# FocusFlow Docs

Short, practical design docs for the FocusFlow MVP.

## What This Project Is

- Arduino sensor node (light, sound, PIR, button)
- Raspberry Pi hub (session logic, API, SQLite, dashboard, sync)
- Raspberry Pi CV node (face presence and looking-away signals)
- Local-first operation, cloud sync in background

## Read In This Order

1. [1. Requirements/Requirements-and-Plan.md](1.%20Requirements/Requirements-and-Plan.md)
2. [2. Architecture and Design/SystemArchitecture.md](2.%20Architecture%20and%20Design/SystemArchitecture.md)
3. [2. Architecture and Design/SoftwareArchitecture.md](2.%20Architecture%20and%20Design/SoftwareArchitecture.md)
4. [2. Architecture and Design/AWS_IoT_Core_Implementation_Plan.md](2.%20Architecture%20and%20Design/AWS_IoT_Core_Implementation_Plan.md)
5. [2. Architecture and Design/ERD.md](2.%20Architecture%20and%20Design/ERD.md)
6. [2. Architecture and Design/UI-UX Design.md](2.%20Architecture%20and%20Design/UI-UX%20Design.md)
7. [0. Documentation/IoT_Desk_Assistant_Plan.md](0.%20Documentation/IoT_Desk_Assistant_Plan.md)
8. [0. Documentation/Project_Documentation.md](0.%20Documentation/Project_Documentation.md)
9. [2. Architecture and Design/system_design_review.html](2.%20Architecture%20and%20Design/system_design_review.html)

## Requirements Source Of Truth

- Use [1. Requirements/Requirements-and-Plan.md](1.%20Requirements/Requirements-and-Plan.md) as the single authoritative requirements and delivery plan document.
- Treat [1. Requirements/Summary.md](1.%20Requirements/Summary.md) as supporting context only.

## Minimum SDLC Coverage (University)

- Requirements and scope are captured in folder 1.
- Design is captured in folder 2.
- Evaluation and project-planning context are captured in folder 0.

## Ground Rules

- Keep MVP local and stable before adding complexity.
- If code and docs disagree, update docs immediately.
- Use these as implementation specs, not report text.
