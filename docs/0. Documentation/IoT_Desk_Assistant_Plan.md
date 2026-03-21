**FocusFlow (Smart IoT Desk Assistant)**

Project Evaluation & 2-Person Implementation Plan

_March 2026_

Supporting planning document. Final MVP scope and delivery decisions are maintained in `../1. Requirements/Requirements-and-Plan.md`.

# 1. Project Evaluation

## 1.1 Concept & Originality

The Smart IoT Desk Assistant is a well-conceived, multi-disciplinary project that merges embedded hardware, computer vision, AI, and full-stack software into a single cohesive product. The combination of local Edge AI processing with tangible physical interaction is a thoughtful design choice that differentiates it from app-only productivity tools.

### Strengths

- Strong scientific grounding — environmental sensors (DHT22, light, loudness) align with established research on ambient intelligence and cognitive performance.
- Privacy-first architecture — on-device CV inference avoids cloud video streaming, a genuinely competitive advantage.
- Multimodal focus estimation (EAR + head pose + presence + phone detection) is more robust than any single-signal approach.
- Tangible HCI (OLED, buttons, potentiometer, LED bar) reduces cognitive load versus screen-only interfaces.
- Clear problem-to-feature mapping already documented in the Summary, demonstrating mature project thinking.

### Risks & Challenges to Address

- Raspberry Pi 4 CPU budget is tight when running YOLOv5 + MediaPipe + MQTT simultaneously — profiling and quantisation will be essential.
- Eye-tracking accuracy degrades with glasses, poor lighting, and off-angle camera placement; mitigation strategy needed.
- Phone detection via camera raises ethical/privacy concerns that the report must address explicitly.
- Scope is large for 2 people — the phased plan below prioritises a working MVP before advanced features.
- The web + mobile platform doubles frontend work; consider starting with web-only and adding mobile in Phase 3.

## 1.2 Technical Feasibility

The project is technically feasible within a 4-phase semester timeline, provided scope is managed carefully. The recommended tech stack below balances capability with development speed.

| Layer             | Recommended Technology                         | Rationale                                               |
| ----------------- | ---------------------------------------------- | ------------------------------------------------------- |
| **Edge (Pi)**     | Python 3.11, OpenCV, MediaPipe, paho-mqtt      | Mature Pi ecosystem; MediaPipe is GPU-optional          |
| **CV / AI**       | MediaPipe Face Mesh (EAR + head pose), YOLOv5n | Optimised for ARM; YOLOv5 nano fits Pi memory           |
| **Messaging**     | Mosquitto MQTT broker (local)                  | Lightweight, low-latency sensor telemetry               |
| **Backend**       | FastAPI (Python) + SQLite                      | Shares codebase knowledge with Pi; SQLite = zero-config |
| **Web Frontend**  | React + Recharts + Tailwind CSS                | Fast dashboards; rich charting library                  |
| **Mobile (opt.)** | React Native (share web logic)                 | Code reuse; defer to Phase 3                            |
| **AI Summaries**  | OpenAI API / local Ollama (Mistral 7B)         | Flexible; Ollama keeps data local                       |

## 1.3 Academic & Report Recommendations

To strengthen the written report and literature review, ensure the following are addressed:

- Cite at least 2 studies linking IEQ (indoor environment quality) to cognitive performance to justify the sensor selection.
- Reference nudge theory (Thaler & Sunstein, 2008) and relevant HCI papers to validate the physical interaction design.
- Include an ethical considerations section covering camera-based monitoring, consent, and data retention.
- A system architecture diagram (block diagram showing Pi sensors → MQTT → backend → frontend) is essential for the System Design chapter.
- Quantify evaluation criteria: target Focus Score accuracy, latency thresholds (<200 ms alert), and user study sample size.

# 2. Team Roles & Responsibilities

## 2.1 Role Split

The project naturally divides into two complementary tracks. Both members share ownership of integration and the final report.

| **Person A — Hardware & Edge AI**               | **Person B — Backend & Platform**          |
| ----------------------------------------------- | ------------------------------------------ |
| Raspberry Pi hardware assembly & wiring         | Project repo, CI/CD pipeline, Git workflow |
| All sensor drivers (DHT22, light, loudness)     | MQTT broker (Mosquitto) & message routing  |
| Computer vision pipeline (EAR, head pose, YOLO) | FastAPI backend + REST endpoints           |
| Focus Score algorithm                           | Database design and queries                |
| OLED display UI & physical controls             | Web dashboard (React + Recharts)           |
| MQTT publishing from Pi                         | Session scheduling & analytics UI          |
| LED ambient feedback & alert system             | AI session summaries & personalised plans  |

# 3. Phased Implementation Plan

## Phase 1 — Foundation (Weeks 1–3)

Goal: Both members have working local environments. Person A has sensors publishing data; Person B has a backend receiving it.

## Phase 2 — Core Features (Weeks 4–7)

Goal: Full focus monitoring pipeline running on the Pi and streaming to a basic web dashboard.

## Phase 3 — Intelligence & Platform (Weeks 8–10)

Goal: AI-powered insights, alerts, scheduling, and a polished frontend.

## Phase 4 — Integration, Testing & Report (Weeks 11–13)

Goal: End-to-end system validated with real users; report complete.

| Phase       | Task                                                      | Person A (Hardware/CV) | Person B (Backend/Platform) |
| ----------- | --------------------------------------------------------- | ---------------------- | --------------------------- |
| **Phase 1** | Hardware Setup: Raspberry Pi, sensor wiring               | ✓                      |                             |
|             | Sensor drivers: DHT22, light, loudness                    | ✓                      |                             |
|             | Camera module setup & test                                | ✓                      |                             |
|             | OLED display driver & basic UI                            | ✓                      |                             |
|             | Buttons & potentiometer input handling                    | ✓                      |                             |
|             | Project repo, CI/CD, folder structure                     |                        | ✓                           |
|             | MQTT broker setup (Mosquitto)                             |                        | ✓                           |
|             | Backend scaffolding (FastAPI/Node)                        |                        | ✓                           |
|             | Database schema (SQLite/PostgreSQL)                       |                        | ✓                           |
| **Phase 2** | Eye tracking & EAR (eye aspect ratio) algorithm           | ✓                      |                             |
|             | Head pose estimation (MediaPipe)                          | ✓                      |                             |
|             | Presence detection (distance/PIR)                         | ✓                      |                             |
|             | Phone detection (YOLOv5 lightweight)                      | ✓                      |                             |
|             | Focus Score computation logic                             | ✓                      | ✓                           |
|             | Pomodoro timer logic (device-side)                        | ✓                      |                             |
|             | REST API endpoints (sessions, env data)                   |                        | ✓                           |
|             | Web dashboard frontend (React/Vue)                        |                        | ✓                           |
|             | Mobile app scaffold (React Native/Flutter, post-MVP only) |                        | ✓                           |
| **Phase 3** | AI session summary generation (LLM prompt)                | ✓                      | ✓                           |
|             | Personalised study plan logic                             |                        | ✓                           |
|             | Break recommendation algorithm                            | ✓                      |                             |
|             | Gentle alert system (LED + OLED nudges)                   | ✓                      |                             |
|             | Analytics dashboard (charts, trends)                      |                        | ✓                           |
|             | Session scheduling (web + mobile)                         |                        | ✓                           |
| **Phase 4** | End-to-end integration testing                            | ✓                      | ✓                           |
|             | Performance benchmarking (Pi CPU/latency)                 | ✓                      |                             |
|             | User study / evaluation                                   | ✓                      | ✓                           |
|             | Documentation & final report write-up                     | ✓                      | ✓                           |

# 4. Key Milestones & Communication

## 4.1 Suggested Milestones

| Week   | Phase       | Milestone                                                                                  |
| ------ | ----------- | ------------------------------------------------------------------------------------------ |
| **3**  | Phase 1 End | Sensors publishing MQTT; backend storing data; basic web page displaying live env readings |
| **5**  | Phase 2 Mid | EAR eye tracking + head pose running in real-time on Pi at >10 fps                         |
| **7**  | Phase 2 End | Full Focus Score computed and displayed live on OLED and web dashboard                     |
| **9**  | Phase 3 Mid | Pomodoro sessions schedulable via web; break alerts firing on device                       |
| **10** | Phase 3 End | AI summaries generated post-session; environmental trend charts live                       |
| **12** | Phase 4 Mid | User study completed (3–5 participants); data collected                                    |
| **13** | Phase 4 End | Final report submitted; demo-ready system                                                  |

## 4.2 Collaboration Tips

- Use a shared Git repo (GitHub/GitLab) with feature branches and pull requests for all code.
- Define a clear MQTT topic schema early (e.g. `desk/sensors/env`, `desk/cv/focus`) so both can work independently.
- Use a shared Notion or Trello board to track tasks per phase and flag blockers early.
- Hold a brief weekly sync (30 min) to demo progress and re-align priorities.
- Person B should provide Person A with a mock backend endpoint in Week 1 so CV work is unblocked.

## 4.3 Scope Management Advice

If time pressure builds, apply these cuts in order:

- Drop phone detection (YOLOv5) — replace with a simple inactivity heuristic.
- Defer mobile app to a stretch goal; focus on a polished web dashboard instead.
- Simplify AI summaries to a rule-based template if LLM integration proves complex.
- Cap user study at 3 participants if recruitment is slow; document limitations in the report.
