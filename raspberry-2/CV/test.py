"""
FocusFlow AWS IoT Core — Connection Test
==========================================

Run this to check if your Pi can actually publish to AWS IoT Core.
It sends 5 test messages and tells you exactly what's happening.

Usage:
  python3 test_aws.py
"""

import json
import time
import sys
import os
from datetime import datetime, timezone

# Your credentials
ENDPOINT = "a1vd9v79ssqr0b-ats.iot.eu-west-2.amazonaws.com"
CERT = "raspberry-1-central_cert.pem"
KEY = "raspberry-1-central_private.key"
CA = "root-CA.crt"
CLIENT_ID = "basicPubSub"
TOPIC = "sdk/test/python"

# ── Check files exist ─────────────────────────────
print("\n=== FILE CHECK ===")
for label, path in [("Cert", CERT), ("Key", KEY), ("Root CA", CA)]:
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = f"OK ({size} bytes)" if exists else "MISSING!"
    print(f"  {label}: {path} → {status}")

if not os.path.exists(CA):
    print(f"\n  root-CA.crt not found! Downloading...")
    import urllib.request
    urllib.request.urlretrieve(
        "https://www.amazontrust.com/repository/AmazonRootCA1.pem",
        CA
    )
    print(f"  Downloaded root-CA.crt ({os.path.getsize(CA)} bytes)")

# ── Try MQTT5 first, then fall back to v1 ─────────
print("\n=== CONNECTION TEST ===")

connection = None
client = None
use_v5 = False

# Try MQTT v1 (more reliable on Pi)
try:
    from awsiot import mqtt_connection_builder
    from awscrt.mqtt import QoS

    print(f"  Connecting as '{CLIENT_ID}' to {ENDPOINT}...")

    connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT,
        pri_key_filepath=KEY,
        ca_filepath=CA,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=30,
    )

    future = connection.connect()
    future.result(timeout=10)
    print("  CONNECTED (MQTT v1)")

except ImportError:
    print("  ERROR: awsiotsdk not installed!")
    print("  Run: ./start.sh  OR  pip install awsiotsdk")
    sys.exit(1)
except Exception as e:
    print(f"  MQTT v1 FAILED: {e}")
    print()
    print("  Common causes:")
    print("    - Certificate not activated in AWS console")
    print("    - Policy not attached to the certificate")
    print("    - Wrong endpoint URL")
    print("    - Another device using 'basicPubSub' client ID right now")
    print("    - Clock skew on Pi (run: sudo date -s \"$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)\")")
    sys.exit(1)


# ── Publish test messages ─────────────────────────
print(f"\n=== PUBLISHING TO '{TOPIC}' ===")
print(f"  Go to AWS IoT console → MQTT test client → Subscribe to '{TOPIC}'")
print(f"  You should see these messages appear:\n")

for i in range(1, 6):
    payload = {
        "test": True,
        "message_number": i,
        "device_id": "cv-node-test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "face_present": True,
        "looking_away": False,
        "slouching": False,
    }

    message = json.dumps(payload)

    try:
        pub_future, packet_id = connection.publish(
            topic=TOPIC,
            payload=message,
            qos=QoS.AT_LEAST_ONCE,  # Wait for ACK from AWS
        )
        # Wait for the publish to complete
        pub_future.result(timeout=5)
        print(f"  [{i}/5] Published OK (packet_id={packet_id})")
    except Exception as e:
        print(f"  [{i}/5] PUBLISH FAILED: {e}")
        print(f"         This usually means the policy doesn't allow publishing to '{TOPIC}'")

    time.sleep(1)


# ── Disconnect ────────────────────────────────────
print("\n=== DISCONNECTING ===")
try:
    connection.disconnect().result(timeout=5)
    print("  Disconnected cleanly")
except:
    print("  Disconnect timed out (not a problem)")

print("\n=== DONE ===")
print(f"  If you saw 'Published OK' above but nothing in the AWS console:")
print(f"    1. Make sure you subscribed to EXACTLY: {TOPIC}")
print(f"    2. Make sure the MQTT test client region is eu-west-2")
print(f"    3. Try subscribing to '#' (all topics) to catch everything")
print(f"    4. Check the certificate is ACTIVE in AWS IoT → Security → Certificates")
print()