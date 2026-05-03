from __future__ import annotations

import sqlite3
from threading import Lock
from typing import Dict, Any


class Repository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._lock = Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS environment_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    light INTEGER,
                    sound INTEGER,
                    move INTEGER,
                    button INTEGER,
                    temperature REAL,
                    humidity REAL,
                    distance_cm INTEGER
                )
                """
            )
            self._ensure_column(self._conn, "environment_log", "distance_cm", "INTEGER")
            self._conn.execute(
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
            self._conn.execute(
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
            self._conn.commit()

    def _ensure_column(
        self, conn: sqlite3.Connection, table_name: str, column_name: str, column_type: str
    ) -> None:
        row_cursor = conn.execute("PRAGMA table_info({})".format(table_name))
        existing_columns = {row[1] for row in row_cursor.fetchall()}
        if column_name not in existing_columns:
            conn.execute(
                "ALTER TABLE {} ADD COLUMN {} {}".format(table_name, column_name, column_type)
            )

    def write_environment(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO environment_log(ts, light, sound, move, button, temperature, humidity, distance_cm)
                VALUES(:updated_at, :light, :sound, :move, :button, :temperature, :humidity, :distance_cm)
                """,
                payload,
            )
            self._conn.commit()

    def write_session_event(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO session_event(ts, status, phase, remaining_seconds)
                VALUES(:updated_at, :status, :phase, :remaining_seconds)
                """,
                payload,
            )
            self._conn.commit()

    def write_focus(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO focus_log(ts, score, confidence, reason)
                VALUES(:updated_at, :score, :confidence, :reason)
                """,
                payload,
            )
            self._conn.commit()

    def latest_environment(self) -> Dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT id, ts, light, sound, move, button, temperature, humidity, distance_cm
                FROM environment_log
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None

    def latest_session_event(self) -> Dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT id, ts, status, phase, remaining_seconds
                FROM session_event
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None

    def latest_focus(self) -> Dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                """
                SELECT id, ts, score, confidence, reason
                FROM focus_log
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row is not None else None

    def close(self) -> None:
        with self._lock:
            self._conn.close()
