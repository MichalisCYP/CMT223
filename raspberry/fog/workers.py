from __future__ import annotations

import importlib
import json
import time
from threading import Event, Thread

from .config import FogConfig
from .repository import Repository
from .session import SessionManager
from .state import SharedState
from .utils import clamp, parse_arduino_line, utc_now_iso


class Worker(Thread):
    def __init__(self, name: str) -> None:
        super().__init__(name=name, daemon=True)
        self.stop_event = Event()

    def stop(self) -> None:
        self.stop_event.set()


class ArduinoIngestWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, repository: Repository) -> None:
        super().__init__(name="arduino-ingest")
        self._config = config
        self._state = state
        self._repository = repository
        self._serial = None
        self._serial_device = config.serial_device

    def _ensure_serial(self) -> bool:
        if self._serial is not None:
            return True
        try:
            serial_module = importlib.import_module("serial")

            self._serial = serial_module.Serial(
                self._serial_device,
                self._config.serial_baud,
                timeout=self._config.ingest_poll_seconds,
            )
            print("Connected serial device on {}".format(self._serial_device))
            return True
        except Exception as ex:
            print("Serial device unavailable: {}".format(ex))
            self._serial = None
            return False

    def _close_serial(self) -> None:
        if self._serial is None:
            return
        try:
            self._serial.close()
        except Exception:
            pass
        self._serial = None

    def _apply_fields(self, fields: dict[str, str]) -> None:
        if not fields:
            return

        updates = {}
        if "LIGHT" in fields:
            updates["light"] = int(float(fields["LIGHT"]))
        if "SOUND" in fields:
            updates["sound"] = int(float(fields["SOUND"]))
        if "MOVE" in fields:
            updates["move"] = 1 if int(float(fields["MOVE"])) > 0 else 0
        if "TEMP" in fields:
            updates["temperature"] = float(fields["TEMP"])
        if "HUM" in fields:
            updates["humidity"] = float(fields["HUM"])
        if "DISTANCE_CM" in fields:
            updates["distance_cm"] = int(float(fields["DISTANCE_CM"]))
        elif "DISTANCE" in fields:
            updates["distance_cm"] = int(float(fields["DISTANCE"]))
        if "BUTTON" in fields:
            updates["button"] = 1 if int(float(fields["BUTTON"])) > 0 else 0

        if updates:
            self._state.update_environment(**updates)
            snapshot = self._state.snapshot()["environment"]
            self._repository.write_environment(snapshot)

    def run(self) -> None:
        while not self.stop_event.is_set():
            if not self._ensure_serial():
                self.stop_event.wait(self._config.reconnect_seconds)
                continue

            try:
                raw = self._serial.readline().decode("utf-8", errors="ignore").strip()
                if raw:
                    fields = parse_arduino_line(raw)
                    self._apply_fields(fields)
            except Exception as ex:
                print("Serial read failed: {}".format(ex))
                self._close_serial()
                self.stop_event.wait(self._config.reconnect_seconds)

        self._close_serial()


class SessionWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, repository: Repository, manager: SessionManager) -> None:
        super().__init__(name="session-worker")
        self._config = config
        self._state = state
        self._repository = repository
        self._manager = manager
        self._last_button_state = int(self._state.snapshot()["environment"].get("button", 0))
        self._last_logged_remaining = -1

    @staticmethod
    def _format_mmss(total_seconds: int) -> str:
        minutes = max(0, int(total_seconds)) // 60
        seconds = max(0, int(total_seconds)) % 60
        return "{:02d}:{:02d}".format(minutes, seconds)

    def _persist_snapshot(self) -> None:
        snap = self._manager.snapshot()
        self._state.set_session(
            status=snap.status,
            phase=snap.phase,
            remaining_seconds=snap.remaining_seconds,
            started_at=snap.started_at,
        )
        state_session = self._state.snapshot()["session"]
        self._repository.write_session_event(state_session)

    def run(self) -> None:
        self._persist_snapshot()
        while not self.stop_event.wait(self._config.session_tick_seconds):
            environment = self._state.snapshot()["environment"]
            button_state = int(environment.get("button", 0))

            # Toggle only on the rising edge so a held button does not repeatedly toggle.
            if button_state == 1 and self._last_button_state == 0:
                previous = self._manager.snapshot()
                current = self._manager.handle_button_event("CLICK", utc_now_iso())
                if previous.status != "running" and current.status == "running":
                    print(
                        "Session started: started_at={}, timer={}".format(
                            current.started_at,
                            self._format_mmss(current.remaining_seconds),
                        )
                    )
                self._persist_snapshot()
            self._last_button_state = button_state

            tick_snapshot = self._manager.tick()
            if tick_snapshot.status == "running" and tick_snapshot.remaining_seconds != self._last_logged_remaining:
                print(
                    "Session timer: phase={}, remaining={} ({}s)".format(
                        tick_snapshot.phase,
                        self._format_mmss(tick_snapshot.remaining_seconds),
                        tick_snapshot.remaining_seconds,
                    )
                )
                self._last_logged_remaining = tick_snapshot.remaining_seconds
            self._persist_snapshot()


class FocusWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, repository: Repository) -> None:
        super().__init__(name="focus-worker")
        self._config = config
        self._state = state
        self._repository = repository

    def _compute_focus(self) -> tuple[int, str, str]:
        snapshot = self._state.snapshot()
        env = snapshot["environment"]
        session = snapshot["session"]

        if session["status"] != "running":
            return 0, "low", "not_running"

        score = 100.0
        reasons = []

        light = int(env["light"])
        if light < 180:
            score -= 15
            reasons.append("low_light")

        sound = int(env["sound"])
        if sound > 600:
            score -= 20
            reasons.append("high_noise")

        if int(env["move"]) == 0:
            score -= 10
            reasons.append("no_movement")

        distance_cm = int(env["distance_cm"])
        if distance_cm > 0 and (distance_cm < 20 or distance_cm > 120):
            score -= 10
            reasons.append("distance_out_of_range")

        temperature = float(env["temperature"])
        humidity = float(env["humidity"])
        if temperature != 0.0 and (temperature < 18.0 or temperature > 29.0):
            score -= 8
            reasons.append("temp_out_of_range")
        if humidity != 0.0 and (humidity < 30.0 or humidity > 70.0):
            score -= 8
            reasons.append("humidity_out_of_range")

        confidence = "medium" if (light > 0 or sound > 0) else "low"
        if temperature != 0.0 and humidity != 0.0:
            confidence = "high"

        if not reasons:
            reasons.append("stable")

        return int(clamp(score, 0, 100)), confidence, ",".join(reasons)

    def run(self) -> None:
        while not self.stop_event.wait(self._config.focus_update_seconds):
            score, confidence, reason = self._compute_focus()
            self._state.update_focus(score=score, confidence=confidence, reason=reason)
            self._repository.write_focus(self._state.snapshot()["focus"])


class DisplayWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, led_display, oled_display) -> None:
        super().__init__(name="display-worker")
        self._config = config
        self._state = state
        self._led = led_display
        self._oled = oled_display

    def run(self) -> None:
        snapshot = self._state.snapshot()
        self._led.render(snapshot["environment"])
        self._oled.render(snapshot["session"], snapshot["focus"])
        while not self.stop_event.wait(self._config.display_update_seconds):
            snapshot = self._state.snapshot()
            self._led.render(snapshot["environment"])
            self._oled.render(snapshot["session"], snapshot["focus"])


class AwsIotPublisherWorker(Worker):
    """
    Publishes sensor data to AWS IoT Core using MQTT (v5 with fallback to v1).
    
    Requires certificate files and proper environment configuration:
    - FOG_AWS_IOT_ENABLED=true
    - FOG_AWS_IOT_ENDPOINT=<endpoint>
    - FOG_AWS_IOT_CERT_PATH=<path-to-cert.pem>
    - FOG_AWS_IOT_KEY_PATH=<path-to-private.key>
    - FOG_AWS_IOT_ROOT_CA_PATH=<path-to-root-CA.crt>
    """
    
    def __init__(self, config: FogConfig, repository: Repository) -> None:
        super().__init__(name="aws-iot-publisher")
        self._config = config
        self._repository = repository
        self._connection = None  # MQTT v1 connection
        self._client = None      # MQTT v5 client
        self._device_id = "focusflow-fog-01"  # Identifies this fog node (like "cv-node-01" in basicCV.py)
        self._last_ids = {
            "environment": 0,
            "session": 0,
            "focus": 0,
        }

    def _is_enabled(self) -> bool:
        """Check if AWS IoT publishing is properly configured."""
        required = [
            self._config.aws_iot_enabled,
            self._config.aws_iot_endpoint,
            self._config.aws_iot_topic_prefix,
            self._config.aws_iot_cert_path,
            self._config.aws_iot_key_path,
        ]
        return all(required)

    def _connect_mqtt5(self) -> bool:
        """Try MQTT v5 connection (preferred for modern AWS SDK)."""
        try:
            mqtt5_builder = importlib.import_module("awsiot.mqtt5_client_builder")
            mqtt5 = importlib.import_module("awscrt.mqtt5")

            self._client = mqtt5_builder.mtls_from_path(
                endpoint=self._config.aws_iot_endpoint,
                cert_filepath=self._config.aws_iot_cert_path,
                pri_key_filepath=self._config.aws_iot_key_path,
                ca_filepath=self._config.aws_iot_root_ca_path,
                client_id=self._config.aws_iot_client_id,
            )
            self._client.start()
            time.sleep(1)  # Give it time to connect
            print("[aws] Connected via MQTT v5 to {}".format(self._config.aws_iot_endpoint))
            return True
        except Exception as ex:
            print("[aws] MQTT v5 failed ({}), trying v1...".format(ex))
            self._client = None
            return False

    def _connect_mqtt1(self) -> bool:
        """Fallback to MQTT v1 connection."""
        try:
            mqtt_builder = importlib.import_module("awsiot.mqtt_connection_builder")
            
            self._connection = mqtt_builder.mtls_from_path(
                endpoint=self._config.aws_iot_endpoint,
                cert_filepath=self._config.aws_iot_cert_path,
                pri_key_filepath=self._config.aws_iot_key_path,
                ca_filepath=self._config.aws_iot_root_ca_path,
                client_id=self._config.aws_iot_client_id,
                clean_session=False,
                keep_alive_secs=30,
            )
            future = self._connection.connect()
            future.result(timeout=10)
            print("[aws] Connected via MQTT v1 to {}".format(self._config.aws_iot_endpoint))
            return True
        except Exception as ex:
            print("[aws] MQTT v1 connection failed: {}".format(ex))
            self._connection = None
            return False

    def _ensure_connected(self) -> bool:
        """Establish connection to AWS IoT Core (try v5, fallback to v1)."""
        if self._client is not None or self._connection is not None:
            return True

        if self._connect_mqtt5():
            return True
        
        if self._connect_mqtt1():
            return True
        
        return False

    def _publish(self, topic: str, payload: dict) -> bool:
        """
        Non-blocking publish to a topic.
        Uses threading to avoid blocking the main loop.
        """
        def _do_publish():
            try:
                message_json = json.dumps(payload)
                
                if self._client:
                    # MQTT v5
                    mqtt5 = importlib.import_module("awscrt.mqtt5")
                    self._client.publish(
                        mqtt5.PublishPacket(
                            topic=topic,
                            payload=message_json.encode("utf-8"),
                            qos=mqtt5.QoS.AT_LEAST_ONCE,
                        )
                    )
                elif self._connection:
                    # MQTT v1
                    qos = importlib.import_module("awscrt.mqtt").QoS
                    self._connection.publish(
                        topic=topic,
                        payload=message_json,
                        qos=qos.AT_LEAST_ONCE,
                    )
                else:
                    return False
                
                return True
            except Exception as ex:
                print("[aws] Publish to {} failed: {}".format(topic, ex))
                return False

        # Run publish in background thread to avoid blocking
        thread = Thread(target=_do_publish, daemon=True)
        thread.start()
        return True

    def _publish_if_new(self, kind: str, row: dict | None) -> None:
        """Publish only if we have a new row (higher ID than last sent). 
        Follows basicCV.py pattern with device_id and timestamp."""
        if row is None:
            return

        row_id = int(row.get("id", 0))
        if row_id <= self._last_ids[kind]:
            return

        topic = "{}/{}".format(self._config.aws_iot_topic_prefix.rstrip("/"), kind)
        
        # Build payload similar to basicCV.py: flat structure with device_id and timestamp
        message = {
            "device_id": self._device_id,
            "timestamp": row.get("ts"),  # Already ISO format from database
            "type": kind,
            "id": row_id,
        }
        # Add all other fields from the row (e.g., light, sound, score, confidence, etc.)
        for key, value in row.items():
            if key not in ("id", "ts"):
                message[key] = value
        
        if self._publish(topic, message):
            self._last_ids[kind] = row_id
            print("[aws] Published {} (id={}) to {}".format(kind, row_id, topic))

    def _disconnect(self) -> None:
        """Clean disconnect from AWS IoT Core."""
        try:
            if self._client:
                self._client.stop()
            elif self._connection:
                self._connection.disconnect()
        except Exception as ex:
            print("[aws] Disconnect error: {}".format(ex))
        finally:
            self._client = None
            self._connection = None

    def run(self) -> None:
        """Main loop: connect and publish sensor data periodically."""
        if not self._is_enabled():
            print("[aws] AWS IoT publisher disabled. Set FOG_AWS_IOT_ENABLED=true and cert paths.")
            return

        try:
            while not self.stop_event.wait(self._config.aws_iot_publish_seconds):
                if not self._ensure_connected():
                    self.stop_event.wait(self._config.reconnect_seconds)
                    continue

                try:
                    self._publish_if_new("environment", self._repository.latest_environment())
                    self._publish_if_new("session", self._repository.latest_session_event())
                    self._publish_if_new("focus", self._repository.latest_focus())
                except Exception as ex:
                    print("[aws] Publish cycle failed: {}".format(ex))
                    # Force reconnect on error
                    self._disconnect()

        except KeyboardInterrupt:
            print("[aws] Shutting down...")
        finally:
            self._disconnect()
            print("[aws] Publisher stopped.")
