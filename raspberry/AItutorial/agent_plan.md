LLM Agent Pipeline

1) Whisper.cpp to transcribe audio locally which is recorded through the usb headset connected to the raspberry pi.

2) Upon transcribing the audio, it is sent to the LLM via the Groq API. Along with the transcribed audio, a summary of the environment and the current session and environment is also sent to the LLM in the following format:
session_summary = "Session is currently {} with phase {} and {} seconds remaining."
environment_summary = "Current environment: light={}, sound={}, move={}, button={}"

3) Finally, the LLM processes the request, generates a response, sends it back to raspberry and that response is received and turned into audio using Vosk and played through the connected usb headset.

Main reference: https://github.com/brenpoly/be-more-agent (main implementation guide: agent_tutorial.py)

LLama.cpp, OpenWakeWord and Piper were going to be used but they are incompatible with the raspberry's 32-bit and therefore a cloud model was used, a button for waking the LLM and Vosk instead of piper.