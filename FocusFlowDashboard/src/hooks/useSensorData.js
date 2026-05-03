import { useState, useEffect, useRef } from 'react';
import { api, mockSensors } from '../api/client';
import { clockStr } from '../utils/helpers';

const POLL_MS = 2000;

export default function useSensorData(active) {
  const [cv, setCv] = useState(null);
  const [sensors, setSensors] = useState({
    light: 0,
    sound: 0,
    motion: 0,
    temp: 0,
    hum: 0,
  });
  const [focusScore, setFocusScore] = useState(0);
  const [focusConf, setFocusConf] = useState("low");
  const [focusReasons, setFocusReasons] = useState([]);
  const [cvOk, setCvOk] = useState(false);
  const [envOk, setEnvOk] = useState(false);
  const [focusHistory, setFocusHistory] = useState([]);
  const [sensorHistory, setSensorHistory] = useState([]);

  const facePresentStreak = useRef(0);
  const faceAbsentStreak = useRef(0);
  const smoothedFaceRef = useRef(false);

  useEffect(() => {
    const tick = async () => {
      // Fetch CV
      const cvData = await api("/cv/latest").catch(() => null);
      const hasCv = !!(cvData && cvData.timestamp);
      setCv(hasCv ? cvData : null);
      setCvOk(hasCv);

      // Fetch environment
      const envData = await api("/env/latest").catch(() => null);
      const hasEnv = !!(envData && envData.ts);
      setEnvOk(hasEnv);

      const s = hasEnv
        ? {
            light: envData.light || 0,
            sound: envData.sound || 0,
            motion: envData.move || 0,
            temp: envData.temperature || 0,
            hum: envData.humidity || 0,
          }
        : mockSensors();
      setSensors(s);

      // Compute score
      let score = 100;
      let reasons = [];

      if (hasCv) {
        const rawFace = !!(
          cvData.face_present ||
          cvData.faces_detected ||
          cvData.face
        );
        if (rawFace) {
          facePresentStreak.current += 1;
          faceAbsentStreak.current = 0;
        } else {
          faceAbsentStreak.current += 1;
          facePresentStreak.current = 0;
        }

        if (facePresentStreak.current >= 2) smoothedFaceRef.current = true;
        if (faceAbsentStreak.current >= 3) smoothedFaceRef.current = false;

        const facePresentNow = smoothedFaceRef.current || rawFace;
        if (!facePresentNow) {
          score -= 25;
          reasons.push("absent");
        }
        if (cvData.looking_away) {
          score -= 20;
          reasons.push("looking_away");
        }
        if (cvData.slouching) {
          score -= 15;
          reasons.push("slouching");
        }
        if (!cvData.eyes_detected && facePresentNow) {
          score -= 10;
          reasons.push("eyes_unclear");
        }
      } else {
        score -= 10;
        reasons.push("cv_offline");
      }
      if (s.sound > 400) {
        score -= 10;
        reasons.push("high_noise");
      }
      if (s.light < 300) {
        score -= 10;
        reasons.push("low_light");
      }
      if (s.temp < 18 || s.temp > 26) {
        score -= 5;
        reasons.push("comfort");
      }
      score = Math.max(0, Math.min(100, Math.round(score)));

      const conf = hasCv
        ? cvData.confidence > 0.7
          ? "high"
          : "medium"
        : "low";
      
      setFocusScore(score);
      setFocusConf(conf);
      setFocusReasons(reasons);

      const now = clockStr();
      setFocusHistory((p) => [...p.slice(-59), { time: now, score }]);
      setSensorHistory((p) => [
        ...p.slice(-59),
        { time: now, light: s.light, sound: s.sound, temp: s.temp, hum: s.hum },
      ]);
    };

    tick();
    const id = setInterval(tick, POLL_MS);
    return () => clearInterval(id);
  }, [active]);

  return {
    cv,
    sensors,
    focusScore,
    focusConf,
    focusReasons,
    cvOk,
    envOk,
    focusHistory,
    sensorHistory,
    setFocusHistory,
    setSensorHistory
  };
}
