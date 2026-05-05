"""
FocusFlow Writer Lambda — handles ALL data from both Pis.

Routes by topic:
  sdk/test/python         → FocusFlow_CV table (your CV Pi)
  focusflow/environment   → FocusFlow_Environment table (teammate's Pi)
  focusflow/session       → FocusFlow_Session table (teammate's Pi)
  focusflow/focus         → FocusFlow_Focus table (teammate's Pi)
"""

import json
import boto3
import logging
from datetime import datetime, timezone
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table_cv = dynamodb.Table("FocusFlow_CV")
table_env = dynamodb.Table("FocusFlow_Environment")
table_session = dynamodb.Table("FocusFlow_Session")
table_focus = dynamodb.Table("FocusFlow_Focus")


def decimal_convert(obj):
    if isinstance(obj, float):
        return Decimal(str(round(obj, 4)))
    if isinstance(obj, dict):
        return {k: decimal_convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_convert(i) for i in obj]
    return obj


def lambda_handler(event, context):
    logger.info(f"Received: {json.dumps(event, default=str)}")

    topic = event.get("t", event.get("topic", "unknown"))
    item = decimal_convert(event)
    item.pop("t", None)
    item.pop("topic", None)

    # Ensure device_id and ts exist
    if "device_id" not in item:
        item["device_id"] = "hub-01" if "light" in item or "sound" in item else "cv-node-01"
    if "ts" not in item:
        item["ts"] = item.get("timestamp", datetime.now(timezone.utc).isoformat())
    if "timestamp" not in item:
        item["timestamp"] = item["ts"]

    # Remove None values
    item = {k: v for k, v in item.items() if v is not None}

    try:
        if "sdk/test/python" in topic:
            # Your CV Pi data
            table_cv.put_item(Item=item)
            logger.info(f"Wrote CV data")

        elif "environment" in topic:
            # Teammate's environment sensor data
            table_env.put_item(Item=item)
            logger.info(f"Wrote environment data")

        elif "session" in topic:
            # Teammate's session events
            table_session.put_item(Item=item)
            logger.info(f"Wrote session data")

        elif "focus" in topic:
            # Teammate's focus scores
            table_focus.put_item(Item=item)
            logger.info(f"Wrote focus data")

        else:
            # Unknown topic — try to figure out from payload
            if "light" in item or "sound" in item or "temperature" in item:
                table_env.put_item(Item=item)
                logger.info(f"Wrote environment data (inferred)")
            elif "score" in item and "confidence" in item:
                table_focus.put_item(Item=item)
                logger.info(f"Wrote focus data (inferred)")
            elif "status" in item and "phase" in item:
                table_session.put_item(Item=item)
                logger.info(f"Wrote session data (inferred)")
            elif "face_present" in item:
                table_cv.put_item(Item=item)
                logger.info(f"Wrote CV data (inferred)")
            else:
                logger.warning(f"Unknown data shape, writing to environment as fallback")
                table_env.put_item(Item=item)

        return {"statusCode": 200, "body": "OK"}

    except Exception as e:
        logger.error(f"Error: {e}")
        raise