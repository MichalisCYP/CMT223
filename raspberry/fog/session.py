from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class SessionSnapshot:
    status: str
    phase: str
    remaining_seconds: int
    started_at: str


class SessionManager:
    def __init__(self, focus_minutes: int, break_minutes: int) -> None:
        self._focus_seconds = max(1, int(focus_minutes)) * 60
        self._break_seconds = max(1, int(break_minutes)) * 60
        self._status = "stopped"
        self._phase = "focus"
        self._remaining_seconds = self._focus_seconds
        self._started_at = ""
        self._last_tick = monotonic()

    def start(self, started_at: str) -> SessionSnapshot:
        if self._status in {"stopped", "break"}:
            self._status = "running"
            self._phase = "focus"
            self._remaining_seconds = self._focus_seconds
            self._started_at = started_at
            self._last_tick = monotonic()
        return self.snapshot()

    def pause(self) -> SessionSnapshot:
        if self._status == "running":
            self._status = "paused"
        return self.snapshot()

    def resume(self) -> SessionSnapshot:
        if self._status == "paused":
            self._status = "running"
            self._last_tick = monotonic()
        return self.snapshot()

    def stop(self) -> SessionSnapshot:
        """Transitions to the break state automatically."""
        if self._status in {"running", "paused"}:
            self._status = "break"
            self._phase = "break"
            self._remaining_seconds = self._break_seconds
            self._last_tick = monotonic()
        return self.snapshot()

    def reset(self) -> SessionSnapshot:
        """Returns the session to the default idle state."""
        self._status = "stopped"
        self._phase = "focus"
        self._remaining_seconds = self._focus_seconds
        return self.snapshot()

    def handle_button_event(self, event_name: str, now_iso: str) -> SessionSnapshot:
        event = event_name.strip().upper()

        if event in {"SHORT", "CLICK", "TOGGLE"}:
            if self._status == "stopped":
                return self.start(now_iso)
            if self._status == "break":
                return self.reset()
            return self.stop()
        if event == "LONG":
            if self._status == "break":
                return self.reset()
            return self.stop()
        return self.snapshot()

    def tick(self) -> SessionSnapshot:
        if self._status not in {"running", "break"}:
            return self.snapshot()

        now = monotonic()
        elapsed = int(now - self._last_tick)
        if elapsed <= 0:
            return self.snapshot()

        self._last_tick = now
        self._remaining_seconds = max(0, self._remaining_seconds - elapsed)
        
        if self._remaining_seconds == 0:
            if self._status == "running":
                # Focus finished -> start automatic break
                self.stop()
            elif self._status == "break":
                # Break finished -> reset to idle
                self.reset()

        return self.snapshot()

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            status=self._status,
            phase=self._phase,
            remaining_seconds=self._remaining_seconds,
            started_at=self._started_at,
        )
