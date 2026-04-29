create a .md file with the following: refine this plan accordingly to match the implementation in #file:raspberry and #file:arduino :
#codebase evaluate my plan for this project:
This plan integrates the "agentic" workflow from the BMO video into your existing **FocusFlow** architecture. Since you have no cooling, this plan uses **asynchronous event-driven triggers** to ensure the CPU only works when necessary.

---

## Phase 1: The "Brain" Setup (Ollama & Tools)
Instead of a simple chatbot, you will treat the AI as a **Worker** that can call functions in your `repository.py` and `state.py`.

* **Model Selection:** Install **Qwen 2.5 0.5B**. It is the smallest and most "thermal-friendly" model for a Pi 4.
* **Tool Definition:** Create a new file `agent_tools.py` that maps your SQLite data to the LLM.

```python
# agent_tools.py
def get_focus_summary():
    """Returns the average focus score from the last 10 minutes of SQLite data."""
    # Logic to query your repository.py
    return f"Current score is {latest_score}% with {session_type} active."

def get_environment_status():
    """Returns current temperature and light levels from state.py."""
    return f"Temp: {state.temp}C, Light: {state.light_level}."
```

---

## Phase 2: The Fog Layer Integration
You will add an **AgentWorker** to your `workers.py`. This thread will remain idle (consuming 0% CPU) until triggered by a wake word or a button press on your Arduino.

### New Workflow in `workers.py`:
1.  **Trigger:** `Button(D3)` on Arduino or **openWakeWord** sends a signal.
2.  **Listen:** **Whisper.cpp (Tiny)** records for 5 seconds.
3.  **Process:** The text is sent to Ollama with a "System Prompt" that includes your tool definitions.
4.  **Action:** If the user asks "How am I doing?", the LLM calls `get_focus_summary()` and reads the result.



---

## Phase 3: The "Voice" and Feedback
To prevent the Pi from overheating, we use **Piper** for TTS because it is extremely fast and low-impact.

* **Visual Feedback:** Update `display.py` to show icons on the **Grove-OLED** during states:
    * `👂` (Listening)
    * `🤔` (Thinking/Processing)
    * `🗣️` (Speaking)
* **Audio Output:** Connect your speaker to the 3.5mm jack. In your code, use a "queue" system so audio doesn't block your Focus CV processing.

---

## Phase 4: Implementation Roadmap

| Task | File to Modify | Description |
| :--- | :--- | :--- |
| **1. Tool Bridge** | `repository.py` | Add a method to fetch a "Focus Summary" string from SQLite. |
| **2. AI Core** | `agent_logic.py` | **(NEW)** Initialize Ollama client and define the system personality. |
| **3. Audio Worker** | `workers.py` | Create `VoiceWorker` to handle Whisper (STT) and Piper (TTS). |
| **4. Trigger Logic** | `fog5-worker.py` | Map the Arduino `Button(D3)` to trigger the `VoiceWorker`. |

---

## Phase 5: Thermal & Resource Management
Since you have **no cooling**, we must implement "Burst Inference":
* **Pre-load Models:** Set `OLLAMA_KEEP_ALIVE=-1` to keep the model in the 8GB RAM, preventing the CPU spike caused by loading from the SD card.
* **Frequency Capping:** Limit AI interactions to once every 60 seconds via a simple boolean flag in `state.py` to allow the CPU to cool down between responses.
* **Priority:** Set the `AgentWorker` to a lower process priority (`nice` value) than your **Computer Vision Node** to ensure focus tracking never stutters.