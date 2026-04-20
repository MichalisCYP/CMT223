from __future__ import annotations

import importlib
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
        self._rfcomm_device = config.rfcomm_device
        if not self._rfcomm_device.startswith("/dev/rfcomm"):
            print(
                "Configured device '{}' is not RFCOMM. Falling back to /dev/rfcomm0.".format(
                    self._rfcomm_device
                )
            )
            self._rfcomm_device = "/dev/rfcomm0"

    def _ensure_serial(self) -> bool:
        if self._serial is not None:
            return True
        try:
            serial_module = importlib.import_module("serial")

            self._serial = serial_module.Serial(
                self._rfcomm_device,
                self._config.rfcomm_baud,
                timeout=self._config.ingest_poll_seconds,
            )
            print("Connected RFCOMM on {}".format(self._rfcomm_device))
            return True
        except Exception as ex:
            print("RFCOMM unavailable: {}".format(ex))
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
        if "BUTTON" in fields:
            updates["button"] = 1 if int(float(fields["BUTTON"])) > 0 else 0
        if "TEMP" in fields:
            updates["temperature"] = float(fields["TEMP"])
        if "HUM" in fields:
            updates["humidity"] = float(fields["HUM"])

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
                print("RFCOMM read failed: {}".format(ex))
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
            button_event = self._state.consume_button_event()
            if button_event:
                self._manager.handle_button_event(button_event, utc_now_iso())
                self._persist_snapshot()
                continue

            self._manager.tick()
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


class LocalEnvironmentWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, repository: Repository) -> None:
        super().__init__(name="local-env-worker")
        self._config = config
        self._state = state
        self._repository = repository
        self._sensor_port = 4
        self._sensor_type = 0

    def run(self) -> None:
        while not self.stop_event.wait(3.0):
            try:
                grovepi = importlib.import_module("grovepi")

                temp, hum = grovepi.dht(self._sensor_port, self._sensor_type)
                if temp is None or hum is None:
                    continue

                self._state.update_environment(temperature=float(temp), humidity=float(hum))
                self._repository.write_environment(self._state.snapshot()["environment"])
            except Exception:
                # Keep running even when GrovePi is not available in development environments.
                continue


class DisplayWorker(Worker):
    def __init__(self, config: FogConfig, state: SharedState, led_display, oled_display) -> None:
        super().__init__(name="display-worker")
        self._config = config
        self._state = state
        self._led = led_display
        self._oled = oled_display

    def run(self) -> None:
        while not self.stop_event.wait(self._config.display_update_seconds):
            snapshot = self._state.snapshot()
            self._led.render(snapshot["environment"])
            self._oled.render(snapshot["session"], snapshot["focus"])
