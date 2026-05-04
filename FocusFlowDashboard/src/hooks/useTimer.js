import { useState, useEffect, useRef } from 'react';

const FOG_API = import.meta.env.VITE_FOG_API_URL;

export default function useTimer() {
  const [active, setActive] = useState(false);
  const [paused, setPaused] = useState(false);
  const [phase, setPhase] = useState("focus");
  const [sessionMinutes, setSessionMinutes] = useState(25);
  const [timer, setTimer] = useState(25 * 60);
  const [poms, setPoms] = useState(0);
  const timerRef = useRef(null);
  const [isSynced, setIsSynced] = useState(false);

  // Sync with Fog Node if API is available
  useEffect(() => {
    if (!FOG_API) return;

    const pollFog = async () => {
      try {
        const res = await fetch(`${FOG_API}/api/state`);
        if (!res.ok) throw new Error("Offline");
        const data = await res.json();
        const session = data.session;

        // Update local state based on fog node (source of truth)
        setActive(session.status !== "stopped");
        setPaused(session.status === "paused");
        setPhase(session.phase);
        setTimer(session.remaining_seconds);
        setIsSynced(true);
      } catch (err) {
        setIsSynced(false);
      }
    };

    const interval = setInterval(pollFog, 2000);
    pollFog(); // initial call
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Local timer only runs if not synced or as a fallback
    // If synced, we rely on the polling to update the timer
    if (active && !paused && !isSynced) {
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
  }, [active, paused, phase, sessionMinutes, isSynced]);

  const callFog = async (action) => {
    if (!FOG_API) return false;
    try {
      const res = await fetch(`${FOG_API}/api/session/${action}`, { method: 'POST' });
      return res.ok;
    } catch (err) {
      console.error(`Fog RPC ${action} failed:`, err);
      return false;
    }
  };

  const adjustSessionMinutes = (delta) => {
    setSessionMinutes((m) => {
      const next = Math.max(1, Math.min(120, m + delta));
      if (!active || phase === "focus") {
        setTimer(next * 60);
      }
      return next;
    });
  };

  const startSession = async () => {
    if (FOG_API) {
      const ok = await callFog('start');
      if (ok) return; // Wait for poll to update state
    }
    setActive(true);
    setPaused(false);
    setTimer(sessionMinutes * 60);
    setPhase("focus");
    setPoms(0);
  };

  const stopSession = async () => {
    if (FOG_API) {
      const ok = await callFog('stop');
      if (ok) return;
    }
    setActive(false);
    setPaused(false);
    setTimer(sessionMinutes * 60);
    setPhase("focus");
  };

  const togglePause = async () => {
    if (FOG_API) {
      const action = paused ? 'resume' : 'pause';
      const ok = await callFog(action);
      if (ok) return;
    }
    setPaused(!paused);
  };

  return {
    active,
    paused,
    phase,
    sessionMinutes,
    timer,
    poms,
    isSynced,
    setPaused: togglePause,
    adjustSessionMinutes,
    startSession,
    stopSession
  };
}
