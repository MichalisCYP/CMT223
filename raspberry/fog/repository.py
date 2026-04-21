from __future__ import annotations

import sqlite3
from threading import Lock
from typing import Dict, Any


class Repository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, check_same_thread=False)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS environment_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    light INTEGER,
                    sound INTEGER,
                    move INTEGER,
                    button INTEGER,
                    temperature REAL,
                    humidity REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_event (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    status TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    remaining_seconds INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS focus_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    confidence TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def write_environment(self, payload: Dict[str, Any]) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO environment_log(ts, light, sound, move, button, temperature, humidity)
                VALUES(:updated_at, :light, :sound, :move, :button, :temperature, :humidity)
                """,
                payload,
            )
            conn.commit()

    def write_session_event(self, payload: Dict[str, Any]) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_event(ts, status, phase, remaining_seconds)
                VALUES(:updated_at, :status, :phase, :remaining_seconds)
                """,
                payload,
            )
            conn.commit()

    def write_focus(self, payload: Dict[str, Any]) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO focus_log(ts, score, confidence, reason)
                VALUES(:updated_at, :score, :confidence, :reason)
                """,
                payload,
            )
            conn.commit()

    def latest_environment(self) -> Dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, ts, light, sound, move, button, temperature, humidity
                FROM environment_log
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None

    def latest_session_event(self) -> Dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, ts, status, phase, remaining_seconds
                FROM session_event
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None

    def latest_focus(self) -> Dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, ts, score, confidence, reason
                FROM focus_log
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None
