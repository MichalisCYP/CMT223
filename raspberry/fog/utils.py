from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def parse_arduino_line(line: str) -> Dict[str, str]:
    """Parse JSON telemetry payload from Arduino.

    Expected format (example):
    {"v":1,"light":412,"sound":275,"move":1,"button":0}
    {"v":1,"btn_event":"SHORT"}
    """
    payload = line.strip()
    if not payload:
        return {}

    try:
        data = json.loads(payload)
        # Normalize keys to uppercase for consistency with field application
        fields: Dict[str, str] = {}
        for key, value in data.items():
            fields[key.upper()] = str(value)
        return fields
    except (json.JSONDecodeError, ValueError):
        # Fall back to legacy formats if JSON parsing fails
        if payload.lower().startswith("light:"):
            return {"LIGHT": payload.split(":", 1)[1].strip()}
        if payload.lower() == "movement":
            return {"MOVE": "1"}
        return {}
