"""
FocusFlow Hub Publisher — runs on your teammate's Raspberry Pi.
Reads from his existing SQLite database and publishes new rows
to AWS IoT Core so they end up in DynamoDB.

Setup:
  1. Run start.sh first (downloads root CA + installs AWS SDK)
  2. Put cert files in the same folder
  3. Update DB_PATH below to match his SQLite database location
  4. Run: python3 hub_publisher.py

His Pi needs its own IoT Thing + certificate in AWS.
Ask him to create a new Thing called "focusflow-hub" and download the certs.
"""

import json
import time
import sqlite3
import logging
import sys
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("focusflow.hub_pub")

# ══════════════════════════════════════════════════════
#  CONFIG — UPDATE THESE
# ══════════════════════════════════════════════════════

# His SQLite database path
DB_PATH = "focusflow.db"  # Update to match his actual db path

# AWS IoT Core — he needs his own certs
AWS_IOT_ENDPOINT = "a1vd9v79ssqr0b-ats.iot.eu-west-2.amazonaws.com"
AWS_CERT_PATH = "raspberry-1-central_cert.pem"     # His cert file
AWS_KEY_PATH = "raspberry-1-central_private.key"    # His key file
AWS_ROOT_CA_PATH = "root-CA.crt"
AWS_CLIENT_ID = "focusflow-hub"  # DIFFERENT from your CV node's client ID

# Topics — must match what the IoT Rules expect
TOPIC_ENV = "focusflow/environment"
TOPIC_SESSION = "focusflow/session"
TOPIC_FOCUS = "focusflow/focus"

# How often to check for new data
SYNC_INTERVAL = 5  # seconds
DEVICE_ID = "hub-01"


# ══════════════════════════════════════════════════════
#  AWS CONNECTION
# ══════════════════════════════════════════════════════

def connect_aws():
    try:
        from awsiot import mqtt_connection_builder
        from awscrt.mqtt import QoS

        connection = mqtt_connection_builder.mtls_from_path(
            endpoint=AWS_IOT_ENDPOINT,
            cert_filepath=AWS_CERT_PATH,
            pri_key_filepath=AWS_KEY_PATH,
            ca_filepath=AWS_ROOT_CA_PATH,
            client_id=AWS_CLIENT_ID,
            clean_session=False,
            keep_alive_secs=30,
        )
        future = connection.connect()
        future.result(timeout=10)
        logger.info("[aws] Connected to AWS IoT Core")
        return connection
    except Exception as e:
        logger.error(f"[aws] Connection failed: {e}")
        return None


def publish(connection, topic, payload):
    try:
        from awscrt.mqtt import QoS
        future, _ = connection.publish(
            topic=topic,
            payload=json.dumps(payload),
            qos=QoS.AT_LEAST_ONCE,
        )
        future.result(timeout=5)
        return True
    except Exception as e:
        logger.warning(f"[aws] Publish failed: {e}")
        return False


# ══════════════════════════════════════════════════════
#  SYNC LOOP
# ══════════════════════════════════════════════════════

def main():
    connection = connect_aws()
    if not connection:
        logger.error("Cannot connect to AWS. Check certs and endpoint.")
        sys.exit(1)

    # Track last synced row IDs
    last_env_id = 0
    last_session_id = 0
    last_focus_id = 0

    logger.info(f"[sync] Reading from {DB_PATH}, syncing every {SYNC_INTERVAL}s")
    print("\n===================================")
    print("  FocusFlow Hub Publisher Running")
    print("  Ctrl+C to stop")
    print("===================================\n")

    try:
        while True:
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row

                # ── Sync environment_log ──────────
                rows = conn.execute(
                    "SELECT * FROM environment_log WHERE id > ? ORDER BY id ASC LIMIT 50",
                    (last_env_id,)
                ).fetchall()

                for row in rows:
                    r = dict(row)
                    payload = {
                        "device_id": DEVICE_ID,
                        "ts": r.get("ts", datetime.now(timezone.utc).isoformat()),
                        "light": r.get("light"),
                        "sound": r.get("sound"),
                        "move": r.get("move"),
                        "button": r.get("button"),
                        "temperature": r.get("temperature"),
                        "humidity": r.get("humidity"),
                        "distance_cm": r.get("distance_cm"),
                    }
                    payload = {k: v for k, v in payload.items() if v is not None}

                    if publish(connection, TOPIC_ENV, payload):
                        last_env_id = r["id"]
                        logger.info(f"[env] Published id={r['id']} light={r.get('light')} sound={r.get('sound')} temp={r.get('temperature')}")

                # ── Sync session_event ────────────
                rows = conn.execute(
                    "SELECT * FROM session_event WHERE id > ? ORDER BY id ASC LIMIT 20",
                    (last_session_id,)
                ).fetchall()

                for row in rows:
                    r = dict(row)
                    payload = {
                        "device_id": DEVICE_ID,
                        "ts": r.get("ts", datetime.now(timezone.utc).isoformat()),
                        "status": r.get("status"),
                        "phase": r.get("phase"),
                        "remaining_seconds": r.get("remaining_seconds"),
                    }
                    payload = {k: v for k, v in payload.items() if v is not None}

                    if publish(connection, TOPIC_SESSION, payload):
                        last_session_id = r["id"]
                        logger.info(f"[session] Published id={r['id']} status={r.get('status')} phase={r.get('phase')}")

                # ── Sync focus_log ────────────────
                rows = conn.execute(
                    "SELECT * FROM focus_log WHERE id > ? ORDER BY id ASC LIMIT 50",
                    (last_focus_id,)
                ).fetchall()

                for row in rows:
                    r = dict(row)
                    payload = {
                        "device_id": DEVICE_ID,
                        "ts": r.get("ts", datetime.now(timezone.utc).isoformat()),
                        "score": r.get("score"),
                        "confidence": r.get("confidence"),
                        "reason": r.get("reason"),
                    }
                    payload = {k: v for k, v in payload.items() if v is not None}

                    if publish(connection, TOPIC_FOCUS, payload):
                        last_focus_id = r["id"]
                        logger.info(f"[focus] Published id={r['id']} score={r.get('score')}")

                conn.close()

            except sqlite3.Error as e:
                logger.error(f"[db] SQLite error: {e}")
            except Exception as e:
                logger.error(f"[sync] Error: {e}")

            time.sleep(SYNC_INTERVAL)

    except KeyboardInterrupt:
        print("\n[sync] Stopping...")
        connection.disconnect()
        logger.info("[sync] Done.")


if __name__ == "__main__":
    main()
