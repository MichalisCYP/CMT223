import React from 'react';
import Card from '../../components/ui/Card';
import Label from '../../components/ui/Label';
import FocusRing from '../../components/ui/FocusRing';
import Gauge from '../../components/ui/Gauge';
import { T, tooltipStyle } from '../../constants/theme';
import { fmtTime } from '../../utils/helpers';
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import useSpeechDictation from '../../hooks/useSpeechDictation';

export default function LiveView({
  // Timer State
  active, paused, phase, sessionMinutes, timer, poms, isSynced,
  setPaused, adjustSessionMinutes, startSession, stopSession,
  // Sensor State
  sensors, focusScore, cvScore, envScore, focusConf, focusReasons, envOk, focusHistory, sensorHistory,
  // Actions
  onOpenChat
}) {
  const { listening: voiceListening, error: voiceError, startDictation } = useSpeechDictation((transcript) => {
    window.localStorage.setItem("focusflow_chat_draft", transcript.trim());
    onOpenChat();
  });

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        gap: 20,
      }}
    >
      {/* Timer */}
      <Card
        delay={0}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 14,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Label>Session</Label>
          {isSynced && (
            <span style={{ 
              fontSize: 9, 
              fontWeight: 800, 
              color: T.accent, 
              background: "rgba(52,211,153,0.12)", 
              padding: "2px 6px", 
              borderRadius: 6,
              border: "1px solid rgba(52,211,153,0.2)"
            }}>
              FOG SYNCED
            </span>
          )}
        </div>
        {active ? (
          <>
            <div
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: phase === "focus" ? T.accent : T.blue,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
              }}
            >
              {paused ? "Paused" : phase}
            </div>
            <div
              style={{
                fontSize: 50,
                fontWeight: 700,
                fontFamily: T.mono,
                color: paused ? T.dim : T.text,
                letterSpacing: "-0.03em",
                lineHeight: 1,
                transition: "color 0.3s",
              }}
            >
              {fmtTime(timer)}
            </div>
            <div style={{ fontSize: 11, color: T.muted }}>
              Pomodoro {poms + 1} · Focus {sessionMinutes}m
            </div>
            <div
              style={{
                display: "flex",
                gap: 8,
                alignItems: "center",
                marginTop: 2,
              }}
            >
              <button
                onClick={() => adjustSessionMinutes(-1)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: `1px solid ${T.border}`,
                  background: "rgba(255,255,255,0.03)",
                  color: T.muted,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 700,
                  fontFamily: T.mono,
                }}
              >
                -1m
              </button>
              <button
                onClick={() => adjustSessionMinutes(1)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: `1px solid ${T.border}`,
                  background: "rgba(255,255,255,0.03)",
                  color: T.muted,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 700,
                  fontFamily: T.mono,
                }}
              >
                +1m
              </button>
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 2 }}>
              <button
                onClick={() => setPaused((v) => !v)}
                style={{
                  padding: "8px 20px",
                  borderRadius: 10,
                  border: `1px solid ${paused ? "rgba(52,211,153,0.24)" : T.border}`,
                  background: paused
                    ? T.accentDim
                    : "rgba(255,255,255,0.03)",
                  color: paused ? T.accent : T.muted,
                  cursor: "pointer",
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: T.sans,
                }}
              >
                {paused ? "Resume" : "Pause"}
              </button>
              <button
                onClick={stopSession}
                style={{
                  padding: "8px 20px",
                  borderRadius: 10,
                  border: "1px solid rgba(248,113,113,0.24)",
                  background: "rgba(248,113,113,0.08)",
                  color: T.danger,
                  cursor: "pointer",
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: T.sans,
                }}
              >
                Finish Session
              </button>
            </div>
          </>
        ) : (
          <>
            <div
              style={{
                fontSize: 50,
                fontWeight: 700,
                fontFamily: T.mono,
                color: T.dim,
                lineHeight: 1,
              }}
            >
              {fmtTime(sessionMinutes * 60)}
            </div>
            <div style={{ fontSize: 12, color: T.dim, marginBottom: 4 }}>
              Ready to start
            </div>
            <div
              style={{
                display: "flex",
                gap: 8,
                alignItems: "center",
                marginBottom: 4,
              }}
            >
              <button
                onClick={() => adjustSessionMinutes(-1)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: `1px solid ${T.border}`,
                  background: "rgba(255,255,255,0.03)",
                  color: T.muted,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 700,
                  fontFamily: T.mono,
                }}
              >
                -1m
              </button>
              <div
                style={{
                  fontSize: 12,
                  color: T.muted,
                  fontFamily: T.mono,
                }}
              >
                Focus {sessionMinutes}m
              </div>
              <button
                onClick={() => adjustSessionMinutes(1)}
                style={{
                  padding: "6px 10px",
                  borderRadius: 8,
                  border: `1px solid ${T.border}`,
                  background: "rgba(255,255,255,0.03)",
                  color: T.muted,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 700,
                  fontFamily: T.mono,
                }}
              >
                +1m
              </button>
            </div>
            <button
              onClick={startSession}
              style={{
                padding: "12px 42px",
                borderRadius: 12,
                border: "none",
                cursor: "pointer",
                background: `linear-gradient(135deg, ${T.accent}, #059669)`,
                color: "#000",
                fontSize: 15,
                fontWeight: 700,
                fontFamily: T.sans,
                boxShadow: `0 4px 24px rgba(52,211,153,0.25)`,
              }}
            >
              Start Session
            </button>
          </>
        )}
      </Card>

      {/* Focus */}
      <Card
        delay={0.05}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 6,
        }}
      >
        <Label>Focus</Label>
        <FocusRing score={focusScore} confidence={focusConf} />
        
        <div style={{ 
          display: "flex", 
          gap: 15, 
          marginTop: 4, 
          padding: "8px 16px",
          background: "rgba(255,255,255,0.02)",
          borderRadius: 12,
          border: `1px solid ${T.border}`
        }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 9, color: T.muted, textTransform: "uppercase", marginBottom: 2 }}>CV Score</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: T.accent }}>{cvScore}</div>
          </div>
          <div style={{ width: 1, background: T.border }}></div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 9, color: T.muted, textTransform: "uppercase", marginBottom: 2 }}>Env Score</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: T.blue }}>{envScore}</div>
          </div>
        </div>

        {focusReasons.length > 0 && (
          <div
            style={{
              display: "flex",
              gap: 5,
              flexWrap: "wrap",
              justifyContent: "center",
              marginTop: 6,
            }}
          >
            {focusReasons.map((r, i) => (
              <span
                key={i}
                style={{
                  fontSize: 9,
                  padding: "2px 10px",
                  borderRadius: 20,
                  background: "rgba(248,113,113,0.08)",
                  color: T.danger,
                  border: "1px solid rgba(248,113,113,0.12)",
                  fontFamily: T.mono,
                }}
              >
                {r}
              </span>
            ))}
          </div>
        )}
      </Card>

      {/* Tutor Buddy Voice */}
      <Card
        delay={0.1}
        style={{
          minHeight: 320,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <Label>Ask Tutor Buddy A Question</Label>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            alignItems: "center",
            justifyContent: "center",
            flex: 1,
          }}
        >
          <button
            onClick={startDictation}
            disabled={voiceListening}
            title="Use microphone"
            style={{
              width: 150,
              height: 150,
              borderRadius: "50%",
              border: "1px solid rgba(255,255,255,0.12)",
              background: voiceListening
                ? T.accentDim
                : "rgba(255,255,255,0.03)",
              color: voiceListening ? T.accent : T.muted,
              cursor: voiceListening ? "default" : "pointer",
              fontWeight: 800,
              fontSize: 58,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            🎤
          </button>
          {voiceListening && (
            <div style={{ fontSize: 12, color: T.accent }}>
              Listening…
            </div>
          )}
          {voiceError && (
            <div style={{ fontSize: 12, color: T.danger }}>
              {voiceError}
            </div>
          )}
        </div>
      </Card>

      {/* Sensors */}
      <Card delay={0.15}>
        <Label tag={envOk ? "AWS LIVE" : "MOCK"} tagLive={envOk}>
          Environment
        </Label>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 10,
            justifyItems: "center",
          }}
        >
          <Gauge
            value={sensors.temp}
            max={40}
            label="Temperature"
            unit="°C"
            color="#f59e0b"
          />
          <Gauge
            value={sensors.hum}
            max={100}
            label="Humidity"
            unit="%"
            color={T.blue}
          />
          <Gauge
            value={sensors.light}
            max={1023}
            label="Light"
            unit="lux"
            color={T.warn}
          />
          <Gauge
            value={sensors.sound}
            max={1023}
            label="Sound"
            unit="dB"
            color={T.danger}
          />
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 6,
            marginTop: 14,
            fontSize: 11,
            color: T.muted,
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: sensors.motion ? T.accent : T.dim,
            }}
          />
          Motion {sensors.motion ? "detected" : "none"}
        </div>
      </Card>

      {/* Focus Trend */}
      <Card
        span={2}
        delay={0.2}
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <Label>Focus trend</Label>
        <div
          style={{
            height: 220,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {focusHistory.length < 3 ? (
            <div style={{ color: T.dim, fontSize: 13 }}>
              Collecting data…
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={focusHistory}
                margin={{ top: 4, right: 4, bottom: 0, left: -20 }}
              >
                <defs>
                  <linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor={T.accent}
                      stopOpacity={0.25}
                    />
                    <stop
                      offset="95%"
                      stopColor={T.accent}
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(255,255,255,0.03)"
                />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 9, fill: T.dim }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 9, fill: T.dim }}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke={T.accent}
                  fill="url(#fg)"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>

      {/* Env charts */}
      <Card span={3} delay={0.25}>
        <Label>Environment history</Label>
        {sensorHistory.length < 3 ? (
          <div
            style={{
              height: 120,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: T.dim,
              fontSize: 13,
            }}
          >
            Collecting data…
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 28,
            }}
          >
            <div>
              <div
                style={{ fontSize: 10, color: T.muted, marginBottom: 6 }}
              >
                Light & sound
              </div>
              <ResponsiveContainer width="100%" height={115}>
                <LineChart
                  data={sensorHistory}
                  margin={{ top: 4, right: 4, bottom: 0, left: -20 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.03)"
                  />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 8, fill: T.dim }}
                    interval="preserveStartEnd"
                  />
                  <YAxis tick={{ fontSize: 8, fill: T.dim }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line
                    type="monotone"
                    dataKey="light"
                    stroke={T.warn}
                    strokeWidth={1.5}
                    dot={false}
                    name="Light"
                  />
                  <Line
                    type="monotone"
                    dataKey="sound"
                    stroke={T.danger}
                    strokeWidth={1.5}
                    dot={false}
                    name="Sound"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div>
              <div
                style={{ fontSize: 10, color: T.muted, marginBottom: 6 }}
              >
                Temperature & humidity
              </div>
              <ResponsiveContainer width="100%" height={115}>
                <LineChart
                  data={sensorHistory}
                  margin={{ top: 4, right: 4, bottom: 0, left: -20 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.03)"
                  />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 8, fill: T.dim }}
                    interval="preserveStartEnd"
                  />
                  <YAxis tick={{ fontSize: 8, fill: T.dim }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line
                    type="monotone"
                    dataKey="temp"
                    stroke="#f59e0b"
                    strokeWidth={1.5}
                    dot={false}
                    name="Temp °C"
                  />
                  <Line
                    type="monotone"
                    dataKey="hum"
                    stroke={T.blue}
                    strokeWidth={1.5}
                    dot={false}
                    name="Humidity %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
