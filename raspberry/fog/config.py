from dataclasses import dataclass
import os


@dataclass(frozen=True)
class FogConfig:
    serial_device: str = os.getenv("FOG_SERIAL_DEVICE", os.getenv("FOG_RFCOMM_DEVICE", "/dev/ttyACM0"))
    serial_baud: int = int(os.getenv("FOG_SERIAL_BAUD", os.getenv("FOG_RFCOMM_BAUD", "9600")))
    reconnect_seconds: float = float(os.getenv("FOG_RECONNECT_SECONDS", "3.0"))

    ingest_poll_seconds: float = float(os.getenv("FOG_INGEST_POLL_SECONDS", "0.1"))
    focus_update_seconds: float = float(os.getenv("FOG_FOCUS_UPDATE_SECONDS", "2.0"))
    display_update_seconds: float = float(os.getenv("FOG_DISPLAY_UPDATE_SECONDS", "1.0"))
    session_tick_seconds: float = float(os.getenv("FOG_SESSION_TICK_SECONDS", "1.0"))
    button_poll_seconds: float = float(os.getenv("FOG_BUTTON_POLL_SECONDS", "0.05"))
    button_debounce_seconds: float = float(os.getenv("FOG_BUTTON_DEBOUNCE_SECONDS", "0.05"))
    button_long_press_seconds: float = float(os.getenv("FOG_BUTTON_LONG_PRESS_SECONDS", "1.2"))
    button_port: int = int(os.getenv("FOG_BUTTON_PORT", "3"))

    session_minutes: int = int(os.getenv("FOG_SESSION_MINUTES", "25"))
    break_minutes: int = int(os.getenv("FOG_BREAK_MINUTES", "5"))

    sqlite_path: str = os.getenv("FOG_SQLITE_PATH", "focusflow_mvp.db")
