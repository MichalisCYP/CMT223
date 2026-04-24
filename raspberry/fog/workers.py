from __future__ import annotations

import importlib
import json
from threading import Event, Thread
from time import monotonic

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

        if "BTN_EVENT" in fields:
            self._state.set_button_event(fields["BTN_EVENT"].upper())

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
            self._manager.tick()
            self._persist_snapshot()


class FogButtonWorker(Worker):
    def __init__(
        self,
        config: FogConfig,
        state: SharedState,
        repository: Repository,
        manager: SessionManager,
    ) -> None:
        super().__init__(name="fog-button-worker")
        self._config = config
        self._state = state
        self._repository = repository
        self._manager = manager
        self._pressed_at = 0.0
        self._last_state = 0
        self._last_change = 0.0

    def _persist_session(self, snapshot) -> None:
        self._state.set_session(
            status=snapshot.status,
            phase=snapshot.phase,
            remaining_seconds=snapshot.remaining_seconds,
            started_at=snapshot.started_at,
        )
        self._repository.write_session_event(self._state.snapshot()["session"])

    def run(self) -> None:
        while not self.stop_event.wait(self._config.button_poll_seconds):
            now = monotonic()
            try:
                grovepi = importlib.import_module("grovepi")
                raw_state = int(grovepi.digitalRead(self._config.button_port))
            except Exception:
                continue

            if raw_state != self._last_state:
                if now - self._last_change < self._config.button_debounce_seconds:
                    continue

                self._last_change = now
                self._last_state = raw_state

                if raw_state == 1:
                    self._pressed_at = now
                    self._state.update_environment(button=1)
                    self._repository.write_environment(self._state.snapshot()["environment"])
                    continue

                self._state.update_environment(button=0)
                self._repository.write_environment(self._state.snapshot()["environment"])

                press_seconds = now - self._pressed_at
                if press_seconds >= self._config.button_long_press_seconds:
                    snapshot = self._manager.handle_button_event("LONG", utc_now_iso())
                    self._persist_session(snapshot)
                elif press_seconds > 0:
                    snapshot = self._manager.handle_button_event("SHORT", utc_now_iso())
                    self._persist_session(snapshot)


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
    def __init__(self, config: FogConfig, repository: Repository) -> None:
        super().__init__(name="aws-iot-publisher")
        self._config = config
        self._repository = repository
        self._client = None
        self._last_ids = {
            "environment": 0,
            "session": 0,
            "focus": 0,
        }

    def _is_enabled(self) -> bool:
        return bool(self._config.aws_iot_enabled and self._config.aws_iot_endpoint and self._config.aws_iot_topic_prefix)

    def _ensure_client(self) -> bool:
        if self._client is not None:
            return True
        try:
            boto3 = importlib.import_module("boto3")
            self._client = boto3.client(
                "iot-data",
                region_name=self._config.aws_iot_region,
                endpoint_url="https://{}".format(self._config.aws_iot_endpoint),
            )
            print("AWS IoT publisher connected to {}".format(self._config.aws_iot_endpoint))
            return True
        except Exception as ex:
            print("AWS IoT client unavailable: {}".format(ex))
            self._client = None
            return False

    def _publish_if_new(self, kind: str, row: dict | None) -> None:
        if row is None:
            return

        row_id = int(row.get("id", 0))
        if row_id <= self._last_ids[kind]:
            return

        topic = "{}/{}".format(self._config.aws_iot_topic_prefix.rstrip("/"), kind)
        message = {
            "source": "focusflow-fog",
            "type": kind,
            "payload": row,
        }
        self._client.publish(topic=topic, qos=1, payload=json.dumps(message).encode("utf-8"))
        self._last_ids[kind] = row_id

    def run(self) -> None:
        if not self._is_enabled():
            print("AWS IoT publisher is disabled. Set FOG_AWS_IOT_ENABLED=true and endpoint/topic env vars to enable.")
            return

        while not self.stop_event.wait(self._config.aws_iot_publish_seconds):
            if not self._ensure_client():
                self.stop_event.wait(self._config.reconnect_seconds)
                continue

            try:
                self._publish_if_new("environment", self._repository.latest_environment())
                self._publish_if_new("session", self._repository.latest_session_event())
                self._publish_if_new("focus", self._repository.latest_focus())
            except Exception as ex:
                print("AWS IoT publish failed: {}".format(ex))
                self._client = None
