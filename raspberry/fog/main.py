from __future__ import annotations

import signal
import sys
import time

from .config import FogConfig
from .display import LedEnvironmentDisplay, OledSessionDisplay
from .repository import Repository
from .session import SessionManager
from .state import SharedState
from .workers import (
    ArduinoIngestWorker,
    AwsIotPublisherWorker,
    DisplayWorker,
    FocusWorker,
    SessionWorker,
    GroveWorker,
)


def main() -> int:
    config = FogConfig()
    print("Using serial transport device: {}".format(config.serial_device))
    state = SharedState()
    repository = Repository(config.sqlite_path)
    session_manager = SessionManager(config.session_minutes, config.break_minutes)

    led_display = LedEnvironmentDisplay()
    oled_display = OledSessionDisplay()

    workers = [
        ArduinoIngestWorker(config, state, repository),
        SessionWorker(config, state, repository, session_manager),
        GroveWorker(config, session_manager),
        FocusWorker(config, state, repository),
        AwsIotPublisherWorker(config, repository),
        DisplayWorker(config, state, led_display, oled_display),
    ]

    for worker in workers:
        worker.start()

    shutting_down = False

    def handle_shutdown(signum, frame):  # type: ignore[unused-argument]
        nonlocal shutting_down
        if shutting_down:
            return
        shutting_down = True
        print("Stopping fog node...")
        for worker in workers:
            worker.stop()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    print("Fog node MVP is running. Press Ctrl+C to stop.")
    try:
        while not shutting_down:
            alive = all(worker.is_alive() for worker in workers)
            if not alive:
                print("A worker stopped unexpectedly. Initiating shutdown.")
                handle_shutdown(signal.SIGTERM, None)
                break
            time.sleep(0.5)
    finally:
        for worker in workers:
            worker.stop()
        for worker in workers:
            worker.join(timeout=2.0)
        repository.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
