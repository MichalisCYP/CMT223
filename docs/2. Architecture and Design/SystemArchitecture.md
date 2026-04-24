# System Architecture

## Components

- Edge node (Arduino): reads light/sound/PIR/temp-humidity/distance and sends telemetry.
- Edge CV node (Raspberry Pi CV): captures camera signals and sends focus-related features.
- Fog node (Raspberry Pi hub): system of record, controller, and local inference/orchestration.
- Cloud node: cloud-side processing and integration services.
- AWS IoT Core: essential cloud message ingress, routing, and device connectivity.
- Client apps: web client required for MVP, mobile client optional after MVP.

## Topology

```mermaid
flowchart TB
    subgraph EDGE[Edge Layer]
        subgraph ARD[Arduino Sensor Node]
            ALS[Grove Light Sensor A3]
            ASD[Grove Sound Sensor A0]
            APIR[Grove PIR Sensor D2]
            ADHT[Grove DHT Sensor D5]
            ADIST[Grove Ultrasonic Ranger D6]
            ABT[USB Serial from Arduino]
        end

        subgraph CV[Pi CV Node]
            CAM[Camera CSI or USB]
            CVP[CV Processor]
        end
    end

    subgraph FOG[Fog Layer]
        H[Pi Hub Controller]
        HBTN[Grove Button D3]
        HBUZ[Grove Buzzer D8]
        HDIS[Grove Display I2C]
        DB[(SQLite)]
    end

    subgraph CLOUD[Cloud Layer]
        AWS[AWS IoT Core]
        CN[Cloud Node Services]
        CDB[(Cloud Database)]
    end

    subgraph CLIENT[Client Layer]
        WEB[Web App]
        MOB[Mobile App]
    end

    ALS --> ABT
    ASD --> ABT
    APIR --> ABT
    ADHT --> ABT
    ADIST --> ABT
    CAM --> CVP

    ABT -->|USB Serial Telemetry| H
    CVP -->|HTTP POST Focus Signals| H
    HBTN --> H

    H --> DB
    H --> HBUZ
    H --> HDIS
    H -->|MQTT over TLS| AWS
    AWS --> CN
    CN --> CDB
    CN -->|HTTPS/WebSocket API| WEB
    CN -->|HTTPS/WebSocket API| MOB
    H -->|Fallback local client API| WEB
```

## Fog Node Modules (Pi Hub)

- sensor_ingest: parse Arduino telemetry + local button input.
- focus_engine: compute focus score.
- session_manager: Pomodoro/session state machine.
- alert_manager: buzzer/display/client-app prompts.
- local_api_server: local API endpoints for operations and fallback UX.
- cloud_sync: publish telemetry/events to AWS IoT and retry unsynced records.

## Cloud Node Modules

- iot_ingest: subscribe to AWS IoT topics and normalize payloads.
- cloud_api: serve web client APIs for MVP and optional mobile APIs post-MVP.
- cloud_analytics: aggregate trends, session summaries, and insights.
- cloud_storage_writer: persist data to cloud database/object storage.
- notification_router: send push or alert events to client apps.

## Data Flows

1. Live flow

- Arduino + CV -> fog ingest -> SQLite + focus/session -> local alerts.
- Fog -> AWS IoT -> cloud node -> client apps (web live state for MVP, optional mobile later).

2. Sync flow

- SQLite unsynced rows -> cloud_sync -> AWS IoT -> cloud node persistence -> ack -> mark synced.

3. Client interaction flow

- Client apps -> cloud API -> control/update request -> AWS IoT command topic -> fog node action.

## Protocol Choices

- Edge Arduino -> fog hub: newline-delimited JSON over USB serial.
- Edge CV -> fog hub: local HTTP POST (essential path).
- Fog -> AWS IoT Core: MQTT over TLS (essential path).
- Cloud node -> client apps: HTTPS REST + WebSocket for live updates.
- Client apps -> cloud node: authenticated HTTPS.

## Architecture Decisions

- Local-first storage with SQLite.
- CV node is mandatory for focus-aware features.
- AWS IoT Core is mandatory for cloud connectivity.
- Cloud node is mandatory for remote APIs, persistence, and analytics.
- Web client is mandatory for MVP.
- Mobile client is optional post-MVP.
- Layered design is fixed: Edge (sensing), Fog (local control), Cloud (remote services).

## Main Risks

- USB serial disconnects.
- Sensor noise causing unstable score.
- CV latency on Pi hardware.
- Cloud connectivity interruptions impacting remote UX.
- API auth/security complexity for client apps.

## Decisions Baseline

MVP decisions are finalized in `../1. Requirements/Requirements-and-Plan.md`.

- CV transport: local HTTP POST.
- Cloud ingress: AWS IoT Core MQTT over TLS.
- Client app live updates: WebSocket preferred, HTTP polling fallback.
- Architecture layers: Edge + Fog + Cloud + Clients are all essential.

## Hardware Mapping

### Board Allocation

- Arduino: Grove light, sound, PIR, temperature/humidity, distance, USB serial telemetry.
- Pi hub: Grove button, Grove buzzer, Grove display, local control.
- Pi CV node: camera and CV processing.

### Hardware Topology

```mermaid
flowchart TB
    subgraph ARD[Arduino Node]
        ALS[Grove Light Sensor A3]
        ASD[Grove Sound Sensor A0/A1]
        APIR[Grove PIR Sensor D2]
        ADHT[Grove DHT Sensor D5]
        ADIST[Grove Ultrasonic Ranger D6]
        ABT[USB Serial from Arduino]
    end

    subgraph HUB[Raspberry Pi Hub]
        HBTN[Grove Button D3]
        HBUZ[Grove Buzzer D8]
        HDIS[Grove Display I2C]
    end

    subgraph CV[Raspberry Pi CV Node]
        CAM[Camera CSI or USB]
    end

    ARD -->|USB Serial Telemetry| HUB
    CV -->|HTTP POST Focus Signals| HUB
```

### Sensor And Actuator Table

| Device                          | Board                | Suggested Pin               | Voltage / Interface            | Sampling Rate                  | Purpose                                                        |
| ------------------------------- | -------------------- | --------------------------- | ------------------------------ | ------------------------------ | -------------------------------------------------------------- |
| Light sensor                    | Arduino              | A3                          | Grove analog sensor            | 1 Hz                           | Measure ambient lighting quality                               |
| Sound sensor                    | Arduino              | A0 or A1                    | Grove analog sensor            | 2 Hz to 5 Hz                   | Estimate environmental noise and distraction level             |
| PIR movement sensor             | Arduino              | D2                          | Grove digital sensor           | 2 Hz                           | Detect movement near the desk                                  |
| Button or LED button input      | Raspberry Pi hub     | Grove D3                    | Digital input, 3.3V Grove      | event-driven                   | Manual start, pause, acknowledgement, or intervention controls |
| USB serial connection           | Arduino              | USB port                    | Native USB serial              | continuous                     | Send telemetry to the hub                                      |
| Temperature and humidity sensor | Arduino              | D5                          | Grove DHT digital interface    | 0.2 Hz to 0.33 Hz              | Measure room comfort conditions                                |
| Distance sensor                 | Arduino              | D6                          | Grove ultrasonic ranger signal | 1 Hz to 2 Hz                   | Presence estimation and desk distance monitoring               |
| Buzzer                          | Raspberry Pi hub     | D8 on GrovePi               | Digital output                 | event-driven                   | Gentle audio interventions                                     |
| Display screen                  | Raspberry Pi hub     | I2C Grove display port      | I2C / Grove                    | update on state change or 1 Hz | Local feedback and timer display                               |
| Camera                          | Raspberry Pi CV node | CSI camera connector or USB | CSI / USB                      | 5 fps to 15 fps for MVP        | Eye tracking, head pose, face presence                         |

### Suggested Pin Plan (MVP)

#### Arduino

- `A3`: light sensor
- `A0`: sound sensor
- `D2`: PIR motion sensor
- `D5`: Grove DHT sensor
- `D6`: Grove ultrasonic ranger
- USB: Arduino serial connection to the Pi

#### Raspberry Pi Hub

- `D8`: Grove buzzer
- `D3`: Grove button
- display: Grove I2C display port
