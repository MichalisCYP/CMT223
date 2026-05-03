import { useState, useEffect, useRef } from 'react';

export default function useTimer() {
  const [active, setActive] = useState(false);
  const [paused, setPaused] = useState(false);
  const [phase, setPhase] = useState("focus");
  const [sessionMinutes, setSessionMinutes] = useState(25);
  const [timer, setTimer] = useState(25 * 60);
  const [poms, setPoms] = useState(0);
  const timerRef = useRef(null);

  useEffect(() => {
    if (active && !paused) {
      timerRef.current = setInterval(() => {
        setTimer((t) => {
          if (t <= 1) {
            if (phase === "focus") {
              setPoms((p) => p + 1);
              setPhase("break");
              return 5 * 60;
            }
            setPhase("focus");
            return sessionMinutes * 60;
          }
          return t - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [active, paused, phase, sessionMinutes]);

  const adjustSessionMinutes = (delta) => {
    setSessionMinutes((m) => {
      const next = Math.max(1, Math.min(120, m + delta));
      if (!active || phase === "focus") {
        setTimer(next * 60);
      }
      return next;
    });
  };

  const startSession = () => {
    setActive(true);
    setPaused(false);
    setTimer(sessionMinutes * 60);
    setPhase("focus");
    setPoms(0);
  };

  const stopSession = () => {
    setActive(false);
    setPaused(false);
    setTimer(sessionMinutes * 60);
    setPhase("focus");
  };

  return {
    active,
    paused,
    phase,
    sessionMinutes,
    timer,
    poms,
    setPaused,
    adjustSessionMinutes,
    startSession,
    stopSession
  };
}
