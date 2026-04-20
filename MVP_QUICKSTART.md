# FocusFlow MVP Quick Start

This guide walks you through setting up and running the basic MVP implementation (no CV yet).

## Architecture Overview

- **Arduino Node**: Sends telemetry (light, sound, motion, button) as JSON over USB serial
- **Fog Node (Raspberry Pi)**: Ingests Arduino data, runs session state machine, computes focus score, drives displays
- **Local Storage**: SQLite for telemetry, session events, and focus samples
- **Displays**:
  - Grove-LCD RGB: Shows temperature, humidity, light, sound (green backlight)
  - Grove-OLED (128x64): Shows session state, countdown timer, focus score

## Hardware Setup

### Arduino Node

1. Connect sensors to the specified pins in [config.h](arduino/arduino_bluetooth/config.h):
   - Light sensor → A3
   - Sound sensor → A0
   - PIR motion → D2
   - Button (momentary) → D3 (active LOW with pull-up)

2. Connect the Arduino to the Raspberry Pi with USB and note the serial device path, typically `/dev/ttyACM0` or `/dev/ttyUSB0`

3. Upload [arduino_bluetooth.ino](arduino/arduino_bluetooth/arduino_bluetooth.ino)

### Raspberry Pi Hub

1. **Connect displays over I2C**:
   - Grove-LCD RGB: I2C address (auto-detect via grove_rgb_lcd library)
   - Grove-OLED: I2C address 0x3C (SSD1306 or SH1106)
   - Both on `/dev/i2c-1`

2. **Install Python dependencies**:
   ```bash
   pip install pyserial
   # Optional (for Grove hardware):
   pip install grove.py grovepi
   # Optional (for OLED):
   pip install luma.oled pillow
   ```

## Running the MVP

### Start Fog Node

```bash
cd /Users/michaelkaramichalis/Developer/CMT223
python3 raspberry/main.py
```

**Expected output:**

```
Using serial transport device: /dev/ttyACM0
Connected serial device on /dev/ttyACM0
Fog node MVP is running. Press Ctrl+C to stop.
[LED] T:22C H:50% | L:412 S:250 | move=1
[OLED] RUNNING FOCUS | 25:00 | Focus: 100%
```

### Button Controls (LED Button on Arduino)

- **Short Press**: Start → Pause → Resume cycle
- **Long Press**: Stop/reset session

### View Live Data

SQLite database is created at `focusflow_mvp.db`:

```bash
sqlite3 focusflow_mvp.db
> SELECT * FROM environment_log ORDER BY rowid DESC LIMIT 5;
> SELECT * FROM session_event ORDER BY rowid DESC LIMIT 5;
> SELECT * FROM focus_log ORDER BY rowid DESC LIMIT 5;
```

## Configuration

Environment variables (optional):

```bash
export FOG_SERIAL_DEVICE=/dev/ttyACM0
export FOG_SERIAL_BAUD=9600
export FOG_SESSION_MINUTES=25
export FOG_BREAK_MINUTES=5
export FOG_SQLITE_PATH=focusflow_mvp.db
python3 raspberry/main.py
```

## Telemetry Format

### Arduino → Fog (JSON over USB serial)

**Environmental telemetry** (every 1 second):

```json
{ "v": 1, "light": 412, "sound": 275, "move": 1, "button": 0 }
```

**Button event** (on short/long press):

```json
{"v":1,"btn_event":"SHORT"}
{"v":1,"btn_event":"LONG"}
```

### Python Parsing

Parser in [fog/utils.py](raspberry/fog/utils.py) handles JSON format with fallback for legacy text formats.

## Worker Threads

The fog coordinator in [fog/main.py](raspberry/fog/main.py) runs these concurrent workers:

1. **ArduinoIngestWorker**: Reads USB serial, parses JSON, updates shared state
2. **LocalEnvironmentWorker**: Optionally reads DHT sensor on GrovePi (D4), falls back gracefully if unavailable
3. **SessionWorker**: Ticks session timer, handles button events, manages state transitions
4. **FocusWorker**: Computes focus score (heuristic based on light/sound/motion/environment)
5. **DisplayWorker**: Updates Grove-LCD and Grove-OLED displays

All workers share thread-safe state via `SharedState` class (RLock-protected).

## Logs and Debugging

To see verbose ingest/focus logs, modify worker print statements in [workers.py](raspberry/fog/workers.py).

For hardware fallbacks:

- If USB serial unavailable: logs to console
- If Grove-LCD missing: renders to console as text
- If Grove-OLED missing: renders to console as text
- If GrovePi DHT unavailable: skips (still works with Arduino-only data)

## Next Steps (Post-MVP)

- Add CV node for face presence + looking-away signals (focus refinement)
- Add local HTTP API for live status and manual controls
- Add AWS IoT Core sync for cloud persistence
- Add web dashboard for session history and analytics
- Integrate buzzer for intervention prompts

## Reference Lab Code

Examples from `iot-lab-book-master/`:

- **LAB 02**: DHT sensor reading patterns → [fog/workers.py LocalEnvironmentWorker](raspberry/fog/workers.py#L196)
- **LAB 04**: MQTT cloud patterns → (ready for Phase 4)
- **LAB 05**: Bluetooth pairing docs → reference for setup
- **LAB 09**: Pi concurrency patterns → [fog/main.py worker orchestration](raspberry/fog/main.py#L22)

## Troubleshooting

| Issue                      | Solution                                                                  |
| -------------------------- | ------------------------------------------------------------------------- |
| Serial unavailable         | Check cable, then set `FOG_SERIAL_DEVICE` to the correct `/dev/tty*` path |
| No serial data             | Verify Arduino is sending JSON, check baud rate (9600)                    |
| Display blank              | Install luma.oled: `pip install luma.oled pillow`                         |
| Focus score always 0       | Ensure session status is "running" (use button to start)                  |
| DHT read fails (test only) | LocalEnvironmentWorker silently continues; not blocking                   |

---

**Delivery Status**: ✅ All success criteria met

- ✅ Sensors transmit over USB serial
- ✅ SQLite stores all telemetry and events
- ✅ Session state machine works (start/pause/resume/stop)
- ✅ Focus estimation runs (light/sound/motion/environment heuristic)
- ✅ Displays render correctly (environmental on LCD RGB, timers on OLED)
- ✅ Works offline without internet
- ✅ Modular, thread-safe, extensible
