# AWS IoT Core Implementation Plan (FocusFlow)

## 1. Purpose

Implement a cloud node on AWS that receives locally stored data from the Raspberry Pi Fog node, then serves that data to:

- Dashboard (web)

This plan is aligned to the current project architecture and codebase, especially:

- `raspberry/fog/repository.py`
- `raspberry/fog/workers.py`
- `raspberry/fog/config.py`
- `docs/1. Requirements/Requirements-and-Plan.md`
- `docs/2. Architecture and Design/SystemArchitecture.md`

## 2. Current Local State (As-Is)

The Raspberry Pi Fog node already writes data to local SQLite using three tables:

- `environment_log`
- `session_event`
- `focus_log`

Workers already run in background threads for ingest, session state, focus scoring, and display. A cloud sync worker is not yet implemented in the current code.

## 3. Target AWS Architecture (MVP)

### 3.1 Data Flow

1. Fog node writes all data to SQLite first (local-first behavior).
2. New background sync worker reads unsynced rows and publishes to AWS IoT Core over MQTT/TLS.
3. AWS IoT Rules route messages to cloud storage.
4. Cloud API reads cloud storage and serves dashboard queries.

### 3.2 AWS Services

Required for MVP:

- AWS IoT Core (device connectivity, MQTT topics, rules)
- DynamoDB (operational query store for app reads)
- Lambda (rule transform and API handlers)
  -- API Gateway (HTTPS endpoints for dashboard)
- CloudWatch Logs (observability)
- IAM (least-privilege access)

Recommended:

- Amazon Timestream (time-series analytics, optional if DynamoDB-only is sufficient for MVP)
  -- Cognito (user auth for dashboard)

## 4. MQTT Topic and Payload Design

### 4.1 Topic Convention

Use environment-based topic prefix:

- `focusflow/{env}/{site_id}/{device_id}/environment`
- `focusflow/{env}/{site_id}/{device_id}/session`
- `focusflow/{env}/{site_id}/{device_id}/focus`
- `focusflow/{env}/{site_id}/{device_id}/heartbeat`
- `focusflow/{env}/{site_id}/{device_id}/ack` (optional)

Example:

- `focusflow/prod/lab-a/pi-hub-01/environment`

### 4.2 Message Envelope

Every published message should include:

```json
{
  "message_id": "uuid-v4",
  "event_type": "environment|session|focus",
  "occurred_at": "2026-04-21T12:00:00Z",
  "published_at": "2026-04-21T12:00:02Z",
  "device_id": "pi-hub-01",
  "site_id": "lab-a",
  "payload": {
    "...": "table-specific fields"
  }
}
```

Table mapping:

- `environment_log` -> `event_type=environment`
- `session_event` -> `event_type=session`
- `focus_log` -> `event_type=focus`

## 5. Raspberry Pi Changes Required

### 5.1 SQLite Schema Updates

Add sync metadata to support reliable retries:

Option A (recommended): dedicated queue table

```sql
CREATE TABLE IF NOT EXISTS cloud_sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_table TEXT NOT NULL,
  source_row_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  retry_count INTEGER NOT NULL DEFAULT 0,
  next_retry_at TEXT,
  last_error TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(source_table, source_row_id)
);
```

Option B: add `synced_at` column to each existing table (simpler but less flexible).

Use Option A for clearer retry/backoff and operational visibility.

### 5.2 Repository Layer

Extend `Repository` with methods such as:

- `enqueue_for_cloud(source_table, source_row_id, topic, payload_json)`
- `fetch_pending_batch(limit, now_iso)`
- `mark_synced(queue_id)`
- `mark_retry(queue_id, retry_count, next_retry_at, last_error)`

When writing `environment_log`, `session_event`, and `focus_log`, also enqueue a corresponding cloud message.

### 5.3 New Background Worker

Add `CloudSyncWorker` in `raspberry/fog/workers.py`:

Responsibilities:

- Maintain AWS IoT MQTT connection (TLS cert auth)
- Poll pending queue batch every N seconds
- Publish each message with QoS 1
- Mark success/failure in queue
- Apply exponential backoff with jitter
- Keep running even if internet drops

Backoff suggestion:

- `next_retry = min(base * (2 ^ retry_count), max_backoff) + jitter`
- base: 2s
- max_backoff: 300s

### 5.4 Configuration

Add to `FogConfig` in `raspberry/fog/config.py`:

- `aws_iot_endpoint`
- `aws_iot_port` (8883)
- `aws_iot_client_id`
- `aws_iot_topic_prefix`
- `aws_iot_cert_path`
- `aws_iot_key_path`
- `aws_iot_ca_path`
- `cloud_sync_batch_size` (for example 50)
- `cloud_sync_poll_seconds` (for example 2.0)
- `cloud_sync_enabled` (true/false)

### 5.5 Main Startup Wiring

In `raspberry/fog/main.py`, instantiate and start the new `CloudSyncWorker` with other workers.

Critical behavior:

- If cloud worker fails, local workers continue.
- Never block local session flow due to cloud issues.

## 6. AWS IoT Core Setup Steps (Colleague Checklist)

### 6.1 Device Provisioning

1. Create IoT Thing per Pi hub (for example `pi-hub-01`).
2. Create certificate and keys.
3. Attach IoT policy allowing publish only to project topics.
4. Download cert/key/CA and place securely on Pi.

Policy scope example:

- Allow `iot:Connect` for approved client ID.
- Allow `iot:Publish` to `focusflow/prod/*`.
- Deny wildcard subscribe if not needed.

### 6.2 Topic Rule Routing

Create AWS IoT Rules for each topic family:

- Rule 1: environment topic -> Lambda transform -> DynamoDB table
- Rule 2: session topic -> Lambda transform -> DynamoDB table
- Rule 3: focus topic -> Lambda transform -> DynamoDB table

Alternative: one generic rule with `event_type` branching in Lambda.

### 6.3 Cloud Data Model (DynamoDB)

Create table: `FocusFlowEvents`

- Partition key: `pk` = `SITE#{site_id}#DEVICE#{device_id}`
- Sort key: `sk` = `TS#{occurred_at}#TYPE#{event_type}#ID#{message_id}`
- GSI1 (optional): `event_type` + timestamp for cross-device dashboards

Store original payload and normalized fields for query efficiency.

### 6.4 API Layer for Dashboard

Use API Gateway + Lambda endpoints:

- `GET /api/live/latest?site_id=...&device_id=...`
- `GET /api/sessions/recent?site_id=...&device_id=...`
- `GET /api/focus/trend?site_id=...&device_id=...&from=...&to=...`

Dashboard should call API, not IoT MQTT directly (for MVP simplicity and security).

## 7. Security and Compliance

- Use X.509 cert auth for device-to-IoT Core.
- Rotate certificates per semester or release cycle.
- Restrict IoT policy to exact topic prefix and client ID.
- Keep private keys outside Git; load via filesystem permissions and environment variables.
- Enable CloudWatch alarms for repeated auth failures and publish failures.

## 8. Reliability Requirements

- Local-first guarantee: all writes succeed locally regardless of internet.
- At-least-once cloud delivery from queue (QoS 1 + retry).
- Idempotency via `message_id` in cloud ingestion Lambda.
- Queue growth monitoring to detect prolonged outage.

## 9. Implementation Sequence (Recommended)

### Phase A: Local Queue + Worker Skeleton (Pi only)

- Add `cloud_sync_queue` schema.
- Enqueue rows for all three event types.
- Add worker loop with mocked publish.
- Verify no impact on existing local behavior.

Deliverable: local queue drains to mock publisher.

### Phase B: IoT Core Connectivity

- Provision Thing/cert/policy.
- Connect from Pi and publish heartbeat topic.
- Add real publish path in worker.

Deliverable: messages visible in AWS IoT MQTT test client/CloudWatch logs.

### Phase C: Rule + Storage + API

- Deploy IoT Rule + Lambda + DynamoDB.
- Validate transformed records in DynamoDB.
- Expose API Gateway endpoints.

Deliverable: dashboard can fetch cloud data from API.

### Phase D: Hardening + Monitoring

- Add retries/backoff/jitter tuning.
- Add dead-letter path after max retries.
- Add CloudWatch dashboards/alarms.

Deliverable: stable operation through network outage and recovery test.

## 10. Test Plan

### 10.1 Edge and Queue Tests

- Verify each local table insert creates one queue row.
- Verify queue row marks `synced` on successful publish.
- Verify retry fields update on simulated publish failure.

### 10.2 Offline/Recovery Tests

- Disconnect internet for 15-30 minutes.
- Confirm local session still runs and data accumulates.
- Reconnect internet and confirm queued backlog drains.

### 10.3 Cloud Path Tests

- Publish test events for all event types.
- Confirm DynamoDB records created with correct keys.
- Confirm API returns expected latest and trend results.

## 11. Suggested Ownership Split (2-Person Team)

Person A (Pi/Fog):

- SQLite queue schema and repository methods
- CloudSyncWorker implementation and resilience behavior
- Device cert installation and Pi runtime configuration

Person B (AWS/Cloud API):

- IoT Core Thing/policy/rules
- Lambda ingestion + DynamoDB schema
- API Gateway endpoints for dashboard

Shared:

- Topic contract and payload versioning
- End-to-end tests and demo script

## 12. Definition of Done

Cloud node implementation is complete when:

1. Pi persists locally and publishes in background without blocking local logic.
2. AWS IoT Core receives all three event types.
3. Cloud storage has queryable records by site/device/time.
4. Dashboard API returns latest and historical metrics from cloud data.
5. Offline/recovery scenario passes with no data loss.
6. Security baseline (cert auth + restricted policy) is in place.

## 13. Practical Notes for This Repository

- Existing `raspberry/cloud.py` is a ThingsBoard example and should not be used as-is for AWS IoT Core production path.
- The target implementation should live in the `raspberry/fog` module set so it integrates with current worker orchestration.
- Keep all new AWS configuration values environment-driven to preserve portability between lab devices.
