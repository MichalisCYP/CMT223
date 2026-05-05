"""
FocusFlow API Lambda — serves ALL data to the dashboard.

Endpoints:
  GET /cv/latest              → latest CV reading (your Pi)
  GET /cv/history?limit=60    → CV history
  GET /env/latest             → latest environment reading (teammate's Pi)
  GET /env/history?limit=60   → environment history
  GET /session/latest         → latest session event
  GET /session/history?limit=20 → session history
  GET /focus/latest           → latest focus score
  GET /focus/history?limit=60 → focus history
  GET /health                 → health check
"""

import json
import boto3
import logging
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table_cv = dynamodb.Table("FocusFlow_CV")
table_env = dynamodb.Table("FocusFlow_Environment")
table_session = dynamodb.Table("FocusFlow_Session")
table_focus = dynamodb.Table("FocusFlow_Focus")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def resp(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def query_latest(table, device_id, limit=1):
    result = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("device_id").eq(device_id),
        ScanIndexForward=False,
        Limit=limit,
    )
    return result.get("Items", [])


def lambda_handler(event, context):
    logger.info(f"Request: {json.dumps(event, default=str)}")

    method = event.get("httpMethod", "GET")
    path = event.get("path", "/")
    params = event.get("queryStringParameters") or {}

    if method == "OPTIONS":
        return resp(200, {"status": "ok"})

    try:
        # ── CV endpoints (your Pi) ────────────
        if path == "/cv/latest":
            items = query_latest(table_cv, "cv-node-01", 1)
            return resp(200, items[0] if items else {"message": "No CV data yet"})

        elif path == "/cv/history":
            limit = int(params.get("limit", "60"))
            items = query_latest(table_cv, "cv-node-01", limit)
            return resp(200, items)

        # ── Environment endpoints (teammate's Pi) ──
        elif path == "/env/latest":
            items = query_latest(table_env, "hub-01", 1)
            return resp(200, items[0] if items else {"message": "No environment data yet"})

        elif path == "/env/history":
            limit = int(params.get("limit", "60"))
            items = query_latest(table_env, "hub-01", limit)
            return resp(200, items)

        # ── Session endpoints ─────────────────
        elif path == "/session/latest":
            items = query_latest(table_session, "hub-01", 1)
            return resp(200, items[0] if items else {"message": "No session data yet"})

        elif path == "/session/history":
            limit = int(params.get("limit", "20"))
            items = query_latest(table_session, "hub-01", limit)
            return resp(200, items)

        # ── Focus endpoints ───────────────────
        elif path == "/focus/latest":
            items = query_latest(table_focus, "hub-01", 1)
            return resp(200, items[0] if items else {"message": "No focus data yet"})

        elif path == "/focus/history":
            limit = int(params.get("limit", "60"))
            items = query_latest(table_focus, "hub-01", limit)
            return resp(200, items)

        # ── Health ────────────────────────────
        elif path == "/health" or path == "/":
            return resp(200, {"status": "ok", "service": "FocusFlow API", "tables": ["CV", "Environment", "Session", "Focus"]})

        else:
            return resp(404, {"error": f"Not found: {path}"})

    except Exception as e:
        logger.error(f"Error: {e}")
        return resp(500, {"error": str(e)})