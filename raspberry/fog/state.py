from __future__ import annotations

from dataclasses import dataclass, asdict
from threading import RLock
from typing import Dict, Any

from .utils import utc_now_iso


@dataclass
class EnvironmentState:
    light: int = 0
    sound: int = 0
    move: int = 0
    button: int = 0
    button2: int = 0
    temperature: float = 0.0
    humidity: float = 0.0
    distance_cm: int = 0
    updated_at: str = ""


@dataclass
class SessionState:
    status: str = "stopped"
    phase: str = "focus"
    remaining_seconds: int = 0
    started_at: str = ""
    updated_at: str = ""


@dataclass
class FocusState:
    score: int = 0
    confidence: str = "low"
    reason: str = "not_running"
    updated_at: str = ""


class SharedState:
    def __init__(self) -> None:
        self._lock = RLock()
        self._environment = EnvironmentState(updated_at=utc_now_iso())
        self._session = SessionState(updated_at=utc_now_iso())
        self._focus = FocusState(updated_at=utc_now_iso())

    def update_environment(self, **kwargs: Any) -> None:
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self._environment, key):
                    setattr(self._environment, key, value)
            self._environment.updated_at = utc_now_iso()

    def set_session(self, status: str, phase: str, remaining_seconds: int, started_at: str) -> None:
        with self._lock:
            self._session.status = status
            self._session.phase = phase
            self._session.remaining_seconds = remaining_seconds
            self._session.started_at = started_at
            self._session.updated_at = utc_now_iso()

    def update_session_remaining(self, remaining_seconds: int, phase: str | None = None) -> None:
        with self._lock:
            self._session.remaining_seconds = max(0, int(remaining_seconds))
            if phase is not None:
                self._session.phase = phase
            self._session.updated_at = utc_now_iso()

    def update_focus(self, score: int, confidence: str, reason: str) -> None:
        with self._lock:
            self._focus.score = int(score)
            self._focus.confidence = confidence
            self._focus.reason = reason
            self._focus.updated_at = utc_now_iso()

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {
                "environment": asdict(self._environment),
                "session": asdict(self._session),
                "focus": asdict(self._focus),
            }
