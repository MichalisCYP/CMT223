# Smart IoT Desk Assistant: Unified Requirements and 2-Person Delivery Plan

Deadline: 07/05/2026

This file is the single source of truth for MVP scope, delivery, and ownership.

## 1. Goal

Build a local-first focus assistant that can run a full study session without internet while providing explainable focus feedback and gentle interventions.

## 2. Scope

### 2.1 In Scope (MVP)

- Arduino telemetry: light, sound, PIR motion, temperature/humidity, distance.
- Raspberry Pi hub: ingest data, run session logic, compute focus score, store in SQLite.
- CV signal integration: face presence and looking-away input.
- Dashboard: live status and session history.
- Alerts: buzzer/display prompts with manual acknowledge/override.
- Background sync to AWS IoT Core (non-blocking).

### 2.2 Out Of Scope (MVP)

- Polished mobile app.
- Trained custom ML models.
- Full cloud analytics platform.
- Multi-user profiles.
- Phone detection for enforcement workflows (can be revisited after MVP).

## 3. Functional Requirements

1. Environment Monitoring

- Read light, sound, movement, temperature/humidity, and distance/presence signals.

2. Focus Estimation

- Generate a focus score from available sensor and CV signals.
- Mark confidence when signals are missing.

3. Session Management

- Create, start, pause, resume, and finish sessions.
- Support Pomodoro-style focus and break periods.

4. Interventions

- Trigger buzzer/display prompts from rule thresholds.
- Support manual acknowledge and override.

5. Dashboard

- Show live metrics and active session state.
- Show session history and summary statistics.

6. Cloud Sync

- Persist locally first.
- Retry cloud sync in the background without affecting local flow.

## 4. Non-Functional Requirements

- Works offline for full local session behavior.
- Survives temporary USB serial, CV, or cloud failures.
- Near real-time local dashboard updates (polling every 2 seconds for MVP).
- Maintainable by a 2-person team and demonstrable by 07/05/2026.

## 5. Constraints

- Team size: 2 people.
- Hardware available: 2 Arduinos, 2 Raspberry Pis.
- Raspberry Pi CPU budget is tight when combining CV + messaging + backend.
- AWS IoT Core learning curve is a delivery risk.

## 6. Finalized MVP Decisions

| ID   | Decision                      | Outcome                                                                             | Rationale                                                    |
| ---- | ----------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| D-01 | Temp/humidity sensor location | Arduino edge node                                                                   | Keep core environment telemetry in one constant edge payload |
| D-02 | Display module                | Grove I2C display on Raspberry Pi hub                                               | Easy integration with Raspberry Pi and clear local feedback  |
| D-03 | Button behavior               | Single momentary button on Pi hub: short press acknowledge, long press pause/resume | Direct local interaction with fog session manager            |
| D-04 | CV node scope                 | Face presence + looking-away only                                                   | Useful signal without over-scoping ML                        |
| D-05 | CV transport                  | Local HTTP POST                                                                     | Fast integration and easy debugging                          |
| D-06 | Dashboard updates             | HTTP polling every 2 seconds                                                        | Reliable for MVP without WebSocket complexity                |
| D-07 | AWS scope                     | AWS IoT Core only for MVP                                                           | Reduces delivery risk                                        |

## 7. Technical Baseline (Recommended)

| Layer        | Recommended Technology                                  | Rationale                          |
| ------------ | ------------------------------------------------------- | ---------------------------------- |
| Edge and Hub | Python 3.11, paho-mqtt, OpenCV                          | Mature Raspberry Pi ecosystem      |
| CV Node      | MediaPipe Face Mesh (presence and looking-away signals) | Good speed and reliability for MVP |
| Messaging    | Mosquitto MQTT broker (local telemetry)                 | Lightweight and low-latency        |
| Backend      | FastAPI + SQLite                                        | Fast delivery with zero-config DB  |
| Dashboard    | Web dashboard (React or simple server-rendered UI)      | Mobile app is out of MVP scope     |
| Cloud        | AWS IoT Core                                            | Matches MVP cloud boundary         |

## 8. Working Assumptions

- The system must continue local session behavior during cloud outage.
- Missing CV data should degrade confidence but not stop scoring.
- One active session at a time is sufficient for MVP.
- Any stretch goals are only attempted after all success criteria in Section 12 are met.

## 9. Two-Person Team Split

Person A: Hardware, Firmware, and CV

- Arduino wiring, firmware, and stable telemetry payloads.
- Hub-side device integration for buzzer, display, button behavior.
- CV runtime setup and local signal posting (presence and looking-away).
- Sensor calibration and hardware troubleshooting.

Person B: Hub Backend, Data, Dashboard, and Cloud Sync

- FastAPI endpoints, session state machine, and focus logic integration.
- SQLite schema, data writes, and session/history queries.
- Live dashboard and session controls.
- Background sync queue to AWS IoT Core.

Shared ownership

- Focus score threshold tuning.
- End-to-end integration, testing, demo script, and final report.

## 10. Delivery Plan to 07/05/2026

Delivery order:

1. Local MVP first.
2. Add focus and interventions.
3. Add CV integration.
4. Add cloud sync last.

### Phase 1: Foundation and Local MVP (22/03-04/04)

Outcomes:

- Stable Arduino telemetry into hub.
- SQLite writes and basic API routes running.
- Session create/start/finish and active dashboard view.

Tasks:

- Lock pin map and payload format.
- Implement local DB schema and ingest pipeline.
- Build initial dashboard page for live readings.

### Phase 2: Focus and Interventions (05/04-18/04)

Outcomes:

- Heuristic focus score running end-to-end.
- Buzzer/display prompts with acknowledge and override.

Tasks:

- Implement scoring thresholds and confidence output.
- Wire button short press (ack) and long press (pause/resume).
- Show intervention events in dashboard timeline.

### Phase 3: CV Integration and Hardening (19/04-30/04)

Outcomes:

- CV node sends face presence and looking-away signals to hub.
- Focus engine consumes CV when available and degrades gracefully when missing.

Tasks:

- Set up CV runtime and post compact payloads via local HTTP POST.
- Tune score weights and CPU usage on Raspberry Pi.
- Validate dashboard responsiveness with 2-second polling.

### Phase 4: Cloud Sync, Testing, and Demo Freeze (01/05-07/05)

Outcomes:

- Background sync to AWS IoT Core without blocking local flow.
- Integration tests and demo checklist completed.
- Final report artifacts updated.

Tasks:

- Implement sync queue worker and retry/backoff behavior.
- Run offline, dropout, and recovery test scenarios.
- Freeze demo build and finalize documentation.

## 11. Milestones

| Date Target | Milestone                                               |
| ----------- | ------------------------------------------------------- |
| 28/03/2026  | Sensors publish telemetry and backend stores data       |
| 04/04/2026  | Session state and live dashboard are operational        |
| 12/04/2026  | Focus score and interventions run end-to-end            |
| 24/04/2026  | CV signals integrated and reflected in score/confidence |
| 03/05/2026  | AWS IoT Core background sync validated                  |
| 07/05/2026  | Final demo-ready system and report handoff              |

## 12. Success Criteria

1. One full local session runs end-to-end.
2. Data persists in SQLite.
3. Focus status is visible and explainable.
4. At least one intervention triggers correctly.
5. System still works with internet disabled.

## 13. Risks and Scope Controls

Primary risks:

- Pi performance bottlenecks under combined CV and telemetry load.
- Accuracy degradation under poor lighting or glasses.
- Privacy and ethics concerns for camera-based monitoring.

If schedule pressure increases, reduce scope in this order:

1. Keep only face presence CV signal, defer looking-away.
2. Defer cloud summaries and publish only key session events.
3. Replace any LLM summary logic with rule-based templates.

## 14. Academic and Reporting Requirements

- Cite at least two studies linking indoor environment quality to cognitive performance.
- Reference nudge theory and relevant HCI literature for intervention design.
- Include ethics section: consent, camera usage transparency, retention policy.
- Include system architecture diagram and measurable targets (for example alert latency and score responsiveness).

## 15. Change Control

If decisions or scope change, update this file and related architecture/testing documents in the same commit.
