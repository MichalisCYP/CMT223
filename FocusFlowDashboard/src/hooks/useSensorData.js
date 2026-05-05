import { useState, useEffect, useRef } from 'react';
import { api } from '../api/client';
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
  const [cvScore, setCvScore] = useState(0);
  const [tableScore, setTableScore] = useState(0);
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

      // Fetch Focus from Table/Fog
      const tableFocusData = await api("/focus/latest").catch(() => null);
      const tScore = tableFocusData?.score ?? 0;
      setTableScore(tScore);

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
        : {
            light: 0,
            sound: 0,
            motion: 0,
            temp: 0,
            hum: 0,
          };
      setSensors(s);

      // Compute CV Score
      let cScore = 100;
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
          cScore -= 25;
          reasons.push("absent");
        }
        if (cvData.looking_away) {
          cScore -= 20;
          reasons.push("looking_away");
        }
        if (cvData.slouching) {
          cScore -= 15;
          reasons.push("slouching");
        }
        if (!cvData.eyes_detected && facePresentNow) {
          cScore -= 10;
          reasons.push("eyes_unclear");
        }
      } else {
        cScore = 0;
        reasons.push("cv_offline");
      }
      
      cScore = Math.max(0, Math.min(100, Math.round(cScore)));
      setCvScore(cScore);

      // Average them
      const finalScore = Math.round((cScore + tScore) / 2);

      // Merge reasons from Table if available
      if (tableFocusData?.reason && tableFocusData.reason !== "not_running" && tableFocusData.reason !== "stable") {
        const tableReasons = tableFocusData.reason.split(",");
        tableReasons.forEach(r => {
          if (!reasons.includes(r)) reasons.push(r);
        });
      }

      const conf = hasCv
        ? cvData.confidence > 0.7
          ? "high"
          : "medium"
        : "low";
      
      setFocusScore(finalScore);
      setFocusConf(conf);
      setFocusReasons(reasons);

      const now = clockStr();
      setFocusHistory((p) => [...p.slice(-59), { time: now, score: finalScore }]);
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
    cvScore,
    envScore: tableScore,
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
