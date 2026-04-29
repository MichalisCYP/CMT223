LLM Agent plan

I have two raspberry pi 4 with 8gb ram each.


On raspberry-1: There will be an audio-listener worker for a wake word using https://github.com/dscripka/openWakeWord (get smallest model) and an additional dedicated button to start the recording for a few seconds. (pressing the button or running the model temporarily disables the wake word worker) (button implemented later - write a scaffold)

We want to use Tiny-Whisper by OpenaI (smallest model possible) using wakeword.onnx. Audio is recorded through the usb headset I connected on my raspberry pi which has a microphone. Then the audio is transcribed and sent to the LLM (Ollama - smallest model possible maybe gemma 0.5b) Along with the transcribed audio, a summary of the environment and the current session and environment is also sent to the LLM in the following form:
        session_summary = "Session is currently {} with phase {} and {} seconds remaining."
        environment_summary = "Current environment: light={}, sound={}, move={}, button={}" 


Finally, the LLM processes the request, generates a response and that response is received and turned into audio using Piper and output through the connected usb headset.

Main reference: https://github.com/brenpoly/be-more-agent (main implementation guide: agent_tutorial.py)

In the future it may be able to call functions and possibly start study sessions or prompt the user to start studying. (RAG can be used)
Later, I will also add a dedicated Agent button to start recording as well.