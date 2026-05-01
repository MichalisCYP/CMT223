import { useState, useEffect, useCallback, useRef } from "react";
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

// ── API CONFIG ─────────────────────────────────────
// Point this at your Pi's FastAPI backend when ready
const API_BASE = "http://localhost:8000/api";
const USE_MOCK = true; // flip to false when backend is live
const POLL_INTERVAL = 2000;

// ── MOCK DATA GENERATOR ───────────────────────────
// Matches your repo's existing SQLite tables: environment_log, session_event, focus_log
function generateMockSensors() {
  const t = Date.now() / 1000;
  return {
    light_level: Math.round(420 + Math.sin(t / 30) * 80 + Math.random() * 40),
    sound_level: Math.round(180 + Math.sin(t / 15) * 90 + Math.random() * 60),
    movement_detected: Math.random() > 0.3 ? 1 : 0,
    temperature_c: +(21.5 + Math.sin(t / 120) * 1.5 + Math.random() * 0.5).toFixed(1),
    humidity_pct: +(48 + Math.sin(t / 90) * 8 + Math.random() * 2).toFixed(1),
  };
}

function generateMockFocus(sensors) {
  let score = 100;
  const reasons = [];
  if (sensors.light_level < 300) { score -= 15; reasons.push("low_light"); }
  if (sensors.sound_level > 400) { score -= 12; reasons.push("high_noise"); }
  if (!sensors.movement_detected) { score -= 8; reasons.push("no_motion"); }
  if (sensors.temperature_c < 18 || sensors.temperature_c > 26) { score -= 5; reasons.push("comfort"); }
  score = Math.max(0, Math.min(100, score + (Math.random() * 6 - 3)));
  return {
    focus_score: Math.round(score),
    confidence: reasons.length < 2 ? "high" : reasons.length < 3 ? "medium" : "low",
    presence_state: sensors.movement_detected ? "present" : "unknown",
    reason_codes: reasons,
  };
}

const MOCK_HISTORY = [
  { id: "s1", title: "Morning Study", status: "completed", start_time: "2026-04-20T09:00:00Z", end_time: "2026-04-20T09:52:00Z", actual_minutes: 52, average_focus_score: 78, pomodoro_completed: 2 },
  { id: "s2", title: "Algorithms Review", status: "completed", start_time: "2026-04-20T14:00:00Z", end_time: "2026-04-20T15:15:00Z", actual_minutes: 75, average_focus_score: 64, pomodoro_completed: 3 },
  { id: "s3", title: "Report Writing", status: "completed", start_time: "2026-04-19T11:00:00Z", end_time: "2026-04-19T11:48:00Z", actual_minutes: 48, average_focus_score: 82, pomodoro_completed: 2 },
  { id: "s4", title: "IoT Lab Prep", status: "completed", start_time: "2026-04-19T16:00:00Z", end_time: "2026-04-19T16:25:00Z", actual_minutes: 25, average_focus_score: 91, pomodoro_completed: 1 },
  { id: "s5", title: "Literature Review", status: "completed", start_time: "2026-04-18T10:30:00Z", end_time: "2026-04-18T12:00:00Z", actual_minutes: 90, average_focus_score: 57, pomodoro_completed: 3 },
];

// ── HELPERS ────────────────────────────────────────
function scoreColor(score) {
  if (score >= 75) return "#22c55e";
  if (score >= 50) return "#eab308";
  if (score >= 30) return "#f97316";
  return "#ef4444";
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function relativeTime(iso) {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── GAUGE COMPONENT ───────────────────────────────
function CircularGauge({ value, max, label, unit, color, size = 110 }) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const dashoffset = circumference * (1 - pct * 0.75);
  return (
    <div style={{ textAlign: "center", width: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round" transform={`rotate(135 ${size/2} ${size/2})`} />
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={dashoffset} strokeLinecap="round"
          transform={`rotate(135 ${size/2} ${size/2})`}
          style={{ transition: "stroke-dashoffset 0.8s ease" }} />
        <text x={size/2} y={size/2 - 4} textAnchor="middle" dominantBaseline="central"
          style={{ fontSize: "20px", fontWeight: 600, fill: "#e2e8f0", fontFamily: "'DM Sans', sans-serif" }}>
          {Math.round(value)}
        </text>
        <text x={size/2} y={size/2 + 16} textAnchor="middle"
          style={{ fontSize: "10px", fill: "#94a3b8", fontFamily: "'DM Sans', sans-serif" }}>
          {unit}
        </text>
      </svg>
      <div style={{ fontSize: "11px", color: "#94a3b8", marginTop: -4, fontFamily: "'DM Sans', sans-serif" }}>{label}</div>
    </div>
  );
}

// ── FOCUS RING ─────────────────────────────────────
function FocusRing({ score, confidence }) {
  const color = scoreColor(score);
  const size = 180;
  const radius = 76;
  const circumference = 2 * Math.PI * radius;
  const dashoffset = circumference * (1 - score / 100);
  return (
    <div style={{ textAlign: "center", position: "relative" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="10" />
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circumference} strokeDashoffset={dashoffset} strokeLinecap="round"
          transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{ transition: "stroke-dashoffset 1s ease, stroke 0.5s ease", filter: `drop-shadow(0 0 8px ${color}44)` }} />
        <text x={size/2} y={size/2 - 8} textAnchor="middle" dominantBaseline="central"
          style={{ fontSize: "42px", fontWeight: 700, fill: color, fontFamily: "'DM Sans', sans-serif", transition: "fill 0.5s" }}>
          {score}
        </text>
        <text x={size/2} y={size/2 + 22} textAnchor="middle"
          style={{ fontSize: "12px", fill: "#94a3b8", fontFamily: "'DM Sans', sans-serif", letterSpacing: "0.1em", textTransform: "uppercase" }}>
          focus score
        </text>
      </svg>
      <div style={{ marginTop: 4, fontSize: "11px", color: "#64748b", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: confidence === "high" ? "#22c55e" : confidence === "medium" ? "#eab308" : "#ef4444", display: "inline-block" }} />
        {confidence} confidence
      </div>
    </div>
  );
}

// ── EVENT FEED ─────────────────────────────────────
function EventFeed({ events }) {
  if (!events.length) return <div style={{ color: "#475569", fontSize: 13, padding: "12px 0" }}>No recent events</div>;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {events.slice(0, 5).map((e, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 10px", background: "rgba(255,255,255,0.02)", borderRadius: 8, borderLeft: `3px solid ${e.severity === 2 ? "#ef4444" : e.severity === 1 ? "#eab308" : "#3b82f6"}` }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 12, color: "#cbd5e1" }}>{e.message}</div>
            <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>{e.source} · {e.time}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── MAIN DASHBOARD ─────────────────────────────────
export default function FocusFlowDashboard() {
  const [view, setView] = useState("live");
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionPaused, setSessionPaused] = useState(false);
  const [sessionTitle, setSessionTitle] = useState("Study Session");
  const [sessionPhase, setSessionPhase] = useState("focus"); // focus | break
  const [timer, setTimer] = useState(25 * 60);
  const [pomodoroCount, setPomodoroCount] = useState(0);
  const [sensors, setSensors] = useState(generateMockSensors());
  const [focus, setFocus] = useState({ focus_score: 85, confidence: "high", presence_state: "present", reason_codes: [] });
  const [focusHistory, setFocusHistory] = useState([]);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [events, setEvents] = useState([]);
  const [history] = useState(MOCK_HISTORY);
  const timerRef = useRef(null);

  // Poll sensors + focus
  useEffect(() => {
    const poll = setInterval(() => {
      const s = generateMockSensors();
      const f = generateMockFocus(s);
      setSensors(s);
      setFocus(f);
      const now = new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      setFocusHistory(prev => [...prev.slice(-59), { time: now, score: f.focus_score }]);
      setSensorHistory(prev => [...prev.slice(-59), { time: now, light: s.light_level, sound: s.sound_level, temp: s.temperature_c, hum: s.humidity_pct }]);

      // Generate events from focus reasons
      if (f.reason_codes.length > 0 && sessionActive) {
        const msg = f.reason_codes.includes("high_noise") ? "Noise level is elevated" :
                    f.reason_codes.includes("low_light") ? "Consider improving lighting" :
                    f.reason_codes.includes("no_motion") ? "No movement detected" : "Environment suboptimal";
        setEvents(prev => [{ message: msg, severity: f.focus_score < 50 ? 2 : 1, source: "alert_manager", time: now }, ...prev].slice(0, 8));
      }
    }, POLL_INTERVAL);
    return () => clearInterval(poll);
  }, [sessionActive]);

  // Session timer
  useEffect(() => {
    if (sessionActive && !sessionPaused) {
      timerRef.current = setInterval(() => {
        setTimer(prev => {
          if (prev <= 1) {
            if (sessionPhase === "focus") {
              setPomodoroCount(c => c + 1);
              setSessionPhase("break");
              setEvents(prev => [{ message: "Focus block complete! Take a break.", severity: 0, source: "session_manager", time: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }) }, ...prev].slice(0, 8));
              return 5 * 60;
            } else {
              setSessionPhase("focus");
              setEvents(prev => [{ message: "Break over — back to focus!", severity: 0, source: "session_manager", time: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }) }, ...prev].slice(0, 8));
              return 25 * 60;
            }
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [sessionActive, sessionPaused, sessionPhase]);

  const startSession = () => { setSessionActive(true); setSessionPaused(false); setTimer(25 * 60); setSessionPhase("focus"); setPomodoroCount(0); setEvents([]); setFocusHistory([]); setSensorHistory([]); };
  const pauseSession = () => setSessionPaused(true);
  const resumeSession = () => setSessionPaused(false);
  const stopSession = () => { setSessionActive(false); setSessionPaused(false); setTimer(25 * 60); setSessionPhase("focus"); };

  const cardStyle = { background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: "20px 24px" };
  const labelStyle = { fontSize: 10, fontWeight: 600, color: "#64748b", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 12 };

  return (
    <div style={{ minHeight: "100vh", background: "#0c0f17", color: "#e2e8f0", fontFamily: "'DM Sans', sans-serif", padding: "0 0 40px" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* ── Header ──────────────────────────────── */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 32px", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #22c55e 0%, #15803d 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 14, color: "#000" }}>FF</div>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.02em" }}>FocusFlow</div>
            <div style={{ fontSize: 11, color: "#475569", fontFamily: "'JetBrains Mono', monospace" }}>Smart IoT Desk Assistant</div>
          </div>
        </div>
        <nav style={{ display: "flex", gap: 4 }}>
          {["live", "history"].map(v => (
            <button key={v} onClick={() => setView(v)} style={{
              padding: "8px 20px", borderRadius: 10, border: "none", cursor: "pointer",
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, letterSpacing: "0.02em", textTransform: "capitalize",
              background: view === v ? "rgba(34,197,94,0.12)" : "transparent",
              color: view === v ? "#22c55e" : "#64748b",
              transition: "all 0.2s",
            }}>{v === "live" ? "Live Session" : "Session History"}</button>
          ))}
        </nav>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 8px #22c55e66", animation: "pulse 2s infinite" }} />
          <span style={{ fontSize: 11, color: "#64748b", fontFamily: "'JetBrains Mono', monospace" }}>
            {USE_MOCK ? "MOCK" : "LIVE"} · 2s poll
          </span>
        </div>
      </header>

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .ff-card { animation: fadeIn 0.4s ease both; }
      `}</style>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "28px 24px" }}>
        {/* ═══════════ LIVE VIEW ═══════════ */}
        {view === "live" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 20 }}>

            {/* ── Timer + Controls ──────────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "1 / 2", display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
              <div style={labelStyle}>Session</div>
              {sessionActive ? (
                <>
                  <div style={{ fontSize: 13, color: sessionPhase === "focus" ? "#22c55e" : "#3b82f6", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em" }}>
                    {sessionPaused ? "Paused" : sessionPhase === "focus" ? "Focus" : "Break"}
                  </div>
                  <div style={{ fontSize: 52, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace", color: sessionPaused ? "#475569" : "#e2e8f0", letterSpacing: "-0.02em", lineHeight: 1, transition: "color 0.3s" }}>
                    {formatTime(timer)}
                  </div>
                  <div style={{ fontSize: 12, color: "#64748b" }}>Pomodoro {pomodoroCount + 1} · {sessionTitle}</div>
                  <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
                    {sessionPaused ? (
                      <button onClick={resumeSession} style={{ padding: "8px 24px", borderRadius: 10, border: "1px solid rgba(34,197,94,0.3)", background: "rgba(34,197,94,0.1)", color: "#22c55e", cursor: "pointer", fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif" }}>Resume</button>
                    ) : (
                      <button onClick={pauseSession} style={{ padding: "8px 24px", borderRadius: 10, border: "1px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.04)", color: "#94a3b8", cursor: "pointer", fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif" }}>Pause</button>
                    )}
                    <button onClick={stopSession} style={{ padding: "8px 24px", borderRadius: 10, border: "1px solid rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.08)", color: "#ef4444", cursor: "pointer", fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif" }}>Finish</button>
                  </div>
                </>
              ) : (
                <>
                  <div style={{ fontSize: 52, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace", color: "#334155", lineHeight: 1 }}>25:00</div>
                  <div style={{ fontSize: 12, color: "#475569", marginBottom: 4 }}>Ready to start</div>
                  <button onClick={startSession} style={{
                    padding: "12px 40px", borderRadius: 12, border: "none", cursor: "pointer",
                    background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                    color: "#000", fontSize: 15, fontWeight: 700, fontFamily: "'DM Sans', sans-serif",
                    boxShadow: "0 4px 20px rgba(34,197,94,0.3)",
                    transition: "transform 0.15s", 
                  }}>Start Session</button>
                </>
              )}
            </div>

            {/* ── Focus Score ──────────────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "2 / 3", display: "flex", flexDirection: "column", alignItems: "center", gap: 8, animationDelay: "0.05s" }}>
              <div style={labelStyle}>Focus</div>
              <FocusRing score={focus.focus_score} confidence={focus.confidence} />
              {focus.reason_codes.length > 0 && (
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "center", marginTop: 4 }}>
                  {focus.reason_codes.map((r, i) => (
                    <span key={i} style={{ fontSize: 10, padding: "3px 10px", borderRadius: 20, background: "rgba(239,68,68,0.1)", color: "#f87171", border: "1px solid rgba(239,68,68,0.15)", fontFamily: "'JetBrains Mono', monospace" }}>{r}</span>
                  ))}
                </div>
              )}
            </div>

            {/* ── Sensors ──────────────────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "3 / 4", animationDelay: "0.1s" }}>
              <div style={labelStyle}>Environment</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, justifyItems: "center" }}>
                <CircularGauge value={sensors.temperature_c} max={40} label="Temperature" unit="°C" color="#f59e0b" />
                <CircularGauge value={sensors.humidity_pct} max={100} label="Humidity" unit="%" color="#3b82f6" />
                <CircularGauge value={sensors.light_level} max={1023} label="Light" unit="lux" color="#eab308" />
                <CircularGauge value={sensors.sound_level} max={1023} label="Sound" unit="dB" color="#ef4444" />
              </div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, marginTop: 12, fontSize: 11, color: "#64748b" }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: sensors.movement_detected ? "#22c55e" : "#475569" }} />
                Motion {sensors.movement_detected ? "detected" : "none"}
              </div>
            </div>

            {/* ── Focus Trend Chart ────────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "1 / 3", animationDelay: "0.15s" }}>
              <div style={labelStyle}>Focus trend</div>
              {focusHistory.length < 2 ? (
                <div style={{ height: 160, display: "flex", alignItems: "center", justifyContent: "center", color: "#334155", fontSize: 13 }}>
                  Collecting data...
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={160}>
                  <AreaChart data={focusHistory} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                    <defs>
                      <linearGradient id="focusGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#475569" }} interval="preserveStartEnd" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#475569" }} />
                    <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }} />
                    <Area type="monotone" dataKey="score" stroke="#22c55e" fill="url(#focusGrad)" strokeWidth={2} dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* ── Events Feed ──────────────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "3 / 4", animationDelay: "0.2s" }}>
              <div style={labelStyle}>Alerts & Events</div>
              <EventFeed events={events} />
            </div>

            {/* ── Environment Charts ─────── */}
            <div className="ff-card" style={{ ...cardStyle, gridColumn: "1 / 4", animationDelay: "0.25s" }}>
              <div style={labelStyle}>Environment history</div>
              {sensorHistory.length < 2 ? (
                <div style={{ height: 140, display: "flex", alignItems: "center", justifyContent: "center", color: "#334155", fontSize: 13 }}>
                  Collecting data...
                </div>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                  <div>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>Light & Sound</div>
                    <ResponsiveContainer width="100%" height={120}>
                      <LineChart data={sensorHistory} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                        <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#475569" }} interval="preserveStartEnd" />
                        <YAxis tick={{ fontSize: 9, fill: "#475569" }} />
                        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }} />
                        <Line type="monotone" dataKey="light" stroke="#eab308" strokeWidth={1.5} dot={false} name="Light" />
                        <Line type="monotone" dataKey="sound" stroke="#ef4444" strokeWidth={1.5} dot={false} name="Sound" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>Temperature & Humidity</div>
                    <ResponsiveContainer width="100%" height={120}>
                      <LineChart data={sensorHistory} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                        <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#475569" }} interval="preserveStartEnd" />
                        <YAxis tick={{ fontSize: 9, fill: "#475569" }} />
                        <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }} />
                        <Line type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="Temp °C" />
                        <Line type="monotone" dataKey="hum" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="Humidity %" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══════════ HISTORY VIEW ═══════════ */}
        {view === "history" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {/* Summary stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
              {[
                { label: "Total sessions", value: history.length, color: "#3b82f6" },
                { label: "Avg. focus", value: Math.round(history.reduce((a, s) => a + s.average_focus_score, 0) / history.length), color: scoreColor(Math.round(history.reduce((a, s) => a + s.average_focus_score, 0) / history.length)) },
                { label: "Total study time", value: `${Math.round(history.reduce((a, s) => a + s.actual_minutes, 0))}m`, color: "#a78bfa" },
                { label: "Pomodoros done", value: history.reduce((a, s) => a + s.pomodoro_completed, 0), color: "#f59e0b" },
              ].map((stat, i) => (
                <div key={i} className="ff-card" style={{ ...cardStyle, textAlign: "center", animationDelay: `${i * 0.05}s` }}>
                  <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>{stat.label}</div>
                  <div style={{ fontSize: 32, fontWeight: 700, color: stat.color, fontFamily: "'JetBrains Mono', monospace" }}>{stat.value}</div>
                </div>
              ))}
            </div>

            {/* Focus by session chart */}
            <div className="ff-card" style={{ ...cardStyle, animationDelay: "0.2s" }}>
              <div style={labelStyle}>Focus score by session</div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={[...history].reverse()} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="title" tick={{ fontSize: 10, fill: "#64748b" }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#475569" }} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }} />
                  <Bar dataKey="average_focus_score" name="Focus" radius={[6, 6, 0, 0]} maxBarSize={48}>
                    {[...history].reverse().map((entry, index) => (
                      <rect key={index} fill={scoreColor(entry.average_focus_score)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Session list */}
            <div className="ff-card" style={{ ...cardStyle, animationDelay: "0.25s" }}>
              <div style={labelStyle}>Past sessions</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {history.map((s, i) => (
                  <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 16px", background: "rgba(255,255,255,0.02)", borderRadius: 12, border: "1px solid rgba(255,255,255,0.04)", transition: "background 0.2s" }}>
                    <div style={{ width: 44, height: 44, borderRadius: 12, background: `${scoreColor(s.average_focus_score)}15`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace", color: scoreColor(s.average_focus_score) }}>
                      {s.average_focus_score}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, fontWeight: 600 }}>{s.title}</div>
                      <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>
                        {s.actual_minutes} min · {s.pomodoro_completed} pomodoro{s.pomodoro_completed !== 1 ? "s" : ""} · {relativeTime(s.start_time)}
                      </div>
                    </div>
                    <div style={{ fontSize: 11, padding: "4px 12px", borderRadius: 20, background: s.status === "completed" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)", color: s.status === "completed" ? "#22c55e" : "#ef4444", border: `1px solid ${s.status === "completed" ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"}`, fontFamily: "'JetBrains Mono', monospace" }}>
                      {s.status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}