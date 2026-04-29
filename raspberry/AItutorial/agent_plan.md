LLM Agent plan

I have two raspberry pi 4 with 8gb ram each.

On raspberry-1: There will be an audio-listener worker for a wake word model wakeword.onnx.using https://github.com/dscripka/openWakeWord (get smallest model) to start the recording for a few seconds.

We want to use Tiny-Whisper by OpenaI (smallest model possible) to transcribe audio which is recorded through the usb headset I connected on my raspberry pi which has a microphone.

Upon transcribing the audio, it is sent to the LLM served on raspberry-2 (Ollama - smallest model possible maybe gemma 0.5b). Along with the transcribed audio, a summary of the environment and the current session and environment is also sent to the LLM in the following format:
session_summary = "Session is currently {} with phase {} and {} seconds remaining."
environment_summary = "Current environment: light={}, sound={}, move={}, button={}"

Finally, the LLM processes the request, generates a response, sends it back to raspberry-1 and that response is received and turned into audio using Piper at raspberry-1 and output through the connected usb headset.

Main reference: https://github.com/brenpoly/be-more-agent (main implementation guide: agent_tutorial.py)
