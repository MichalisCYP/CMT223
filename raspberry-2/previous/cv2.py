"""
FocusFlow CV Node — Raspberry Pi Camera
========================================

Detects: face presence, eye focus (looking away), and posture (slouching).
Sends signals to AWS IoT Core via MQTT.

Requirements (install in your venv):
  pip install opencv-python "numpy<2" requests

Setup:
  1. Run start.sh first (downloads root CA + installs AWS SDK)
  2. Then run this script

Usage:
  # With display (sitting at the Pi)
  python3 cv_node.py

  # Headless (over SSH, no monitor)
  python3 cv_node.py --headless

  # Point at teammate's hub Pi too
  python3 cv_node.py --headless --hub-url http://192.168.1.50:8000/api/cv/ingest
"""

import cv2
import os
import sys
import time
import json
import argparse
import logging
import threading
from datetime import datetime, timezone

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("focusflow.cv")


# ══════════════════════════════════════════════════════
#  YOUR AWS CONFIG (from your certs + start.sh)
# ══════════════════════════════════════════════════════

AWS_IOT_ENDPOINT = "a1vd9v79ssqr0b-ats.iot.eu-west-2.amazonaws.com"
AWS_CERT_PATH = "raspberry-1-central_cert.pem"
AWS_KEY_PATH = "raspberry-1-central_private.key"
AWS_ROOT_CA_PATH = "root-CA.crt"
AWS_CLIENT_ID = "basicPubSub"

# Your policy only allows this topic — use it for CV data
AWS_TOPIC = "sdk/test/python"

AWS_ENABLED = True

# ══════════════════════════════════════════════════════
#  HUB CONFIG (teammate's Pi — optional)
# ══════════════════════════════════════════════════════

HUB_URL = ""  # Set to teammate's Pi IP, e.g. "http://192.168.1.50:8000/api/cv/ingest"

# ══════════════════════════════════════════════════════
#  DETECTION SETTINGS
# ══════════════════════════════════════════════════════

POSTURE_THRESHOLD = 40
LOOKING_AWAY_TIMEOUT = 2.0
SEND_INTERVAL = 2.0  # Send data every 2 seconds
CAMERA_INDEX = 0


# ══════════════════════════════════════════════════════
#  HAAR CASCADE SETUP
# ══════════════════════════════════════════════════════

def load_cascades():
    face_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
    eye_path = "/usr/share/opencv4/haarcascades/haarcascade_eye.xml"

    if not os.path.exists(face_path):
        face_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"

    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade = cv2.CascadeClassifier(eye_path)

    if face_cascade.empty():
        logger.error(f"Failed to load face cascade from {face_path}")
        sys.exit(1)

    logger.info(f"Loaded cascades OK")
    return face_cascade, eye_cascade


# ══════════════════════════════════════════════════════
#  AWS IOT CORE CONNECTION
# ══════════════════════════════════════════════════════

class AWSPublisher:
    def _init_(self):
        self.connection = None
        self.client = None
        self.connected = False

    def connect(self):
        try:
            from awsiot import mqtt5_client_builder
            from awscrt import mqtt5

            self.client = mqtt5_client_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                cert_filepath=AWS_CERT_PATH,
                pri_key_filepath=AWS_KEY_PATH,
                ca_filepath=AWS_ROOT_CA_PATH,
                client_id=AWS_CLIENT_ID,
            )
            self.client.start()
            # Give it a moment to connect
            time.sleep(2)
            self.connected = True
            logger.info("[aws] Connected to AWS IoT Core")
            return True

        except ImportError:
            logger.error("[aws] awsiotsdk not installed. Run start.sh first.")
            return False
        except Exception as e:
            logger.warning(f"[aws] MQTT5 failed ({e}), trying v1...")
            return self._connect_v1()

    def _connect_v1(self):
        """Fallback: use the v1 MQTT connection builder."""
        try:
            from awsiot import mqtt_connection_builder

            self.connection = mqtt_connection_builder.mtls_from_path(
                endpoint=AWS_IOT_ENDPOINT,
                cert_filepath=AWS_CERT_PATH,
                pri_key_filepath=AWS_KEY_PATH,
                ca_filepath=AWS_ROOT_CA_PATH,
                client_id=AWS_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30,
            )
            future = self.connection.connect()
            future.result(timeout=10)
            self.connected = True
            logger.info("[aws] Connected via MQTT v1 fallback")
            return True
        except Exception as e:
            logger.error(f"[aws] v1 fallback also failed: {e}")
            return False

    def publish(self, payload: dict):
        if not self.connected:
            return False

        message = json.dumps(payload)

        try:
            if self.client:
                from awscrt import mqtt5
                self.client.publish(mqtt5.PublishPacket(
                    topic=AWS_TOPIC,
                    payload=message.encode("utf-8"),
                    qos=mqtt5.QoS.AT_LEAST_ONCE,
                ))
            elif self.connection:
                from awscrt.mqtt import QoS
                self.connection.publish(
                    topic=AWS_TOPIC,
                    payload=message,
                    qos=QoS.AT_LEAST_ONCE,
                )
            logger.debug(f"[aws] Published to {AWS_TOPIC}")
            return True
        except Exception as e:
            logger.warning(f"[aws] Publish failed: {e}")
            return False


# ══════════════════════════════════════════════════════
#  MAIN CV LOOP
# ══════════════════════════════════════════════════════

def run_cv(headless=False, hub_url=""):
    face_cascade, eye_cascade = load_cascades()

    # Connect to AWS
    aws = None
    if AWS_ENABLED:
        aws = AWSPublisher()
        if not aws.connect():
            logger.warning("[aws] Running without AWS — data won't be sent to cloud")
            aws = None

    # Open camera
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    if not cap.isOpened():
        logger.error("Cannot open camera. Check connection.")
        sys.exit(1)

    logger.info(f"Camera opened | Headless: {headless} | AWS: {aws is not None}")
    if hub_url:
        logger.info(f"Hub URL: {hub_url}")

    # Posture calibration
    standard_y = None
    last_face_time = time.time()
    last_send_time = 0

    # Stats
    frame_count = 0

    print("\n===================================")
    print("  FocusFlow CV Node Running")
    print("  Press 'q' to quit")
    print("  Press 'r' to recalibrate posture")
    print("===================================\n")

    try:
        while True:
            ret, img = cap.read()
            if not ret:
                logger.warning("Frame grab failed — retrying")
                time.sleep(0.5)
                continue

            frame_count += 1
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # ── Face detection ────────────────
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            face_present = len(faces) > 0
            looking_away = False
            slouching = False
            eyes_detected = False
            head_pose = "unknown"
            confidence = 0.0

            if face_present:
                last_face_time = time.time()
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

                # Posture check
                if standard_y is None:
                    standard_y = y
                    logger.info(f"Posture calibrated — baseline Y: {standard_y}")

                if y > standard_y + POSTURE_THRESHOLD:
                    slouching = True

                # Eye detection
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
                eyes_detected = len(eyes) >= 2

                if eyes_detected:
                    head_pose = "forward"
                    confidence = 0.85
                else:
                    head_pose = "partial"
                    confidence = 0.6

                # Draw on frame
                if not headless:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 0), 2)
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(img, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
                    if slouching:
                        cv2.putText(img, "FIX POSTURE!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            else:
                if time.time() - last_face_time > LOOKING_AWAY_TIMEOUT:
                    looking_away = True
                    head_pose = "away"
                    confidence = 0.7

            # Status text
            if face_present and eyes_detected:
                status, color = "Focused", (0, 255, 0)
            elif face_present:
                status, color = "Face detected (eyes unclear)", (0, 255, 255)
            elif looking_away:
                status, color = "Looking away", (0, 0, 255)
            else:
                status, color = "Searching...", (128, 128, 128)

            if not headless:
                cv2.putText(img, f"Status: {status}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                if slouching:
                    cv2.putText(img, "SLOUCHING", (10, 110),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # ── Send data every SEND_INTERVAL seconds ──
            now = time.time()
            if now - last_send_time >= SEND_INTERVAL:
                last_send_time = now

                payload = {
                    "device_id": "cv-node-01",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "face_present": face_present,
                    "looking_away": looking_away,
                    "head_pose": head_pose,
                    "confidence": confidence,
                    "slouching": slouching,
                    "eyes_detected": eyes_detected,
                }

                # Publish to AWS (non-blocking)
                if aws:
                    threading.Thread(
                        target=aws.publish, args=(payload,), daemon=True
                    ).start()

                # POST to hub (non-blocking)
                if hub_url and HAS_REQUESTS:
                    def post_hub(url, data):
                        try:
                            requests.post(url, json=data, timeout=2)
                        except Exception:
                            pass
                    threading.Thread(
                        target=post_hub, args=(hub_url, payload), daemon=True
                    ).start()

                # Log to console
                logger.info(
                    f"[{status}] face={face_present} eyes={eyes_detected} "
                    f"slouch={slouching} pose={head_pose} conf={confidence}"
                )

            # ── Display ──────────────────────────
            if not headless:
                cv2.imshow("FocusFlow CV Monitor", img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("r"):
                    standard_y = None
                    logger.info("Recalibrating posture...")
            else:
                time.sleep(0.03)

    except KeyboardInterrupt:
        print("\n[cv] Shutting down...")

    finally:
        cap.release()
        if not headless:
            cv2.destroyAllWindows()
        logger.info("[cv] Done.")


# ══════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════

if _name_ == "_main_":
    parser = argparse.ArgumentParser(description="FocusFlow CV Node")
    parser.add_argument("--headless", action="store_true",
                        help="Run without display (over SSH)")
    parser.add_argument("--hub-url", default=HUB_URL,
                        help="Hub API endpoint for HTTP POST")
    parser.add_argument("--camera", type=int, default=CAMERA_INDEX,
                        help="Camera index (default: 0)")
    parser.add_argument("--no-aws", action="store_true",
                        help="Disable AWS publishing")

    args = parser.parse_args()
    CAMERA_INDEX = args.camera
    if args.no_aws:
        AWS_ENABLED = False

    run_cv(headless=args.headless, hub_url=args.hub_url)