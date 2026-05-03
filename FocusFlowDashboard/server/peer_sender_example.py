#!/usr/bin/env python3
"""Example sender for your friend's Raspberry Pi.

Pushes environment + audio/mic metadata to your FocusFlow AI API over LAN.
"""

from __future__ import annotations

import json
import time
import urllib.request

TARGET_API = "http://192.168.1.50:8787/api/peer-ingest"  # Change to your Pi LAN IP
PEER_TOKEN = "change_me"  # Must match PEER_SHARED_TOKEN on your Pi if enabled


def post_payload(payload: dict) -> None:
    req = urllib.request.Request(
        TARGET_API,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-peer-token": PEER_TOKEN,
        },
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        print("Status:", res.status)
        print(res.read().decode("utf-8"))


def main() -> None:
    while True:
        payload = {
            "sourcePi": "friend-rpi",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": {
                "temperature": 23.4,
                "humidity": 46.2,
                "light": 420,
                "sound": 210,
                "motion": 1,
            },
            "audio": {
                "micLevel": 0.52,
                "headsetConnected": True,
            },
            "transcript": "Finished chapter 3 and reviewed sorting algorithms.",
        }
        post_payload(payload)
        time.sleep(10)


if __name__ == "__main__":
    main()
