import { useState } from 'react';
import { getSpeechRecognition } from '../utils/helpers';

export default function useSpeechDictation(onResult) {
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");

  const startDictation = () => {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition) {
      setError("Speech recognition is not supported in this browser.");
      return;
    }

    setError("");
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript || "";
      if (transcript) {
        onResult(transcript);
      }
    };
    recognition.onerror = () => setError("Could not access microphone or speech service.");
    recognition.onend = () => setListening(false);
    recognition.start();
  };

  return {
    listening,
    error,
    startDictation
  };
}
