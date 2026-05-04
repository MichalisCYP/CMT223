import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { MOCK_SESSIONS } from '../../api/client';
import { T, tooltipStyle } from '../../constants/theme';
import { timeAgo, scoreColor } from '../../utils/helpers';
import Card from '../../components/ui/Card';
import Label from '../../components/ui/Label';
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function HistoryView() {
  const [sessions, setSessions] = useState(MOCK_SESSIONS);

  useEffect(() => {
    (async () => {
      try {
        const data = await api("/session/history?limit=20");
        if (data && Array.isArray(data) && data.length > 0) {
          // Group by started_at to collapse events belonging to the same session
          const groups = data.reduce((acc, s) => {
            const sessionId = s.started_at || s.ts;
            if (!acc[sessionId]) acc[sessionId] = [];
            acc[sessionId].push(s);
            return acc;
          }, {});

          const groupedSessions = Object.values(groups).map((events) => {
            // Sort events by timestamp within the group
            const sorted = [...events].sort((a, b) => new Date(a.ts) - new Date(b.ts));
            const first = sorted[0];
            const last = sorted[sorted.length - 1];
            
            const isStopped = sorted.some(e => e.status === 'stopped');
            const startTime = new Date(first.ts);
            const endTime = new Date(last.ts);
            const durationMins = Math.round((endTime - startTime) / 60000);

            return {
              title: first.phase ? (first.phase.charAt(0).toUpperCase() + first.phase.slice(1) + " Session") : "Focus Session",
              status: isStopped ? "completed" : last.status,
              mins: durationMins || Math.round((first.remaining_seconds || 0) / 60) || 25,
              score: last.score || first.score || 75,
              poms: Math.max(1, Math.floor(durationMins / 25)),
              time: first.started_at || first.ts,
            };
          });

          // Sort sessions by time descending
          setSessions(groupedSessions.sort((a, b) => new Date(b.time) - new Date(a.time)));
        }
      } catch (err) {
        // Fallback to mock sessions
      }
    })();
  }, []);

  const total = sessions.length;
  const avgF = Math.round(sessions.reduce((a, s) => a + s.score, 0) / (total || 1));
  const totalM = sessions.reduce((a, s) => a + s.mins, 0);
  const totalP = sessions.reduce((a, s) => a + s.poms, 0);

  const stats = [
    { label: "Total sessions", value: total, color: T.blue },
    { label: "Avg. focus", value: avgF, color: scoreColor(avgF) },
    { label: "Study time", value: `${totalM}m`, color: T.purple },
    { label: "Pomodoros", value: totalP, color: T.amber },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 16,
        }}
      >
        {stats.map((s, i) => (
          <Card key={i} delay={i * 0.05} style={{ textAlign: "center" }}>
            <div
              style={{
                fontSize: 10,
                color: T.muted,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                marginBottom: 10,
              }}
            >
              {s.label}
            </div>
            <div
              style={{
                fontSize: 30,
                fontWeight: 700,
                color: s.color,
                fontFamily: T.mono,
              }}
            >
              {s.value}
            </div>
          </Card>
        ))}
      </div>

      <Card delay={0.2}>
        <Label>Focus by session</Label>
        <ResponsiveContainer width="100%" height={175}>
          <BarChart
            data={[...sessions].reverse()}
            margin={{ top: 8, right: 8, bottom: 0, left: -20 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.03)"
            />
            <XAxis dataKey="title" tick={{ fontSize: 10, fill: T.muted }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: T.dim }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar
              dataKey="score"
              name="Focus"
              radius={[6, 6, 0, 0]}
              maxBarSize={44}
            >
              {[...sessions].reverse().map((e, i) => (
                <Cell key={i} fill={scoreColor(e.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card delay={0.25}>
        <Label>Past sessions</Label>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {sessions.map((s, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: "13px 16px",
                background: "rgba(255,255,255,0.015)",
                borderRadius: 12,
                border: `1px solid ${T.border}`,
              }}
            >
              <div
                style={{
                  width: 42,
                   height: 42,
                  borderRadius: 11,
                  background: `${scoreColor(s.score)}12`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 17,
                  fontWeight: 700,
                  fontFamily: T.mono,
                  color: scoreColor(s.score),
                }}
              >
                {s.score}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{s.title}</div>
                <div style={{ fontSize: 11, color: T.muted, marginTop: 2 }}>
                  {s.mins} min · {s.poms} pom{s.poms !== 1 ? "s" : ""} ·{" "}
                  {timeAgo(s.time)}
                </div>
              </div>
              <span
                style={{
                  fontSize: 10,
                  padding: "4px 12px",
                  borderRadius: 20,
                  background: T.accentDim,
                  color: T.accent,
                  border: "1px solid rgba(52,211,153,0.15)",
                  fontFamily: T.mono,
                }}
              >
                {s.status}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
