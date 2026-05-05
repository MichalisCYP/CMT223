import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { T, tooltipStyle } from '../../constants/theme';
import { timeAgo, scoreColor } from '../../utils/helpers';
import Card from '../../components/ui/Card';
import Label from '../../components/ui/Label';
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function HistoryView() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const [sessionData, focusData] = await Promise.all([
          api("/session/history?limit=40"),
          api("/focus/history?limit=200")
        ]);

        if (sessionData && Array.isArray(sessionData) && sessionData.length > 0) {
          // 1. Group session events into logical sessions
          const groups = [];
          
          sessionData.sort((a, b) => new Date(a.ts) - new Date(b.ts)).forEach(s => {
            const sTime = new Date(s.ts);
            // Try to find a group to join
            let group = groups.find(g => {
              // Primary match: same started_at
              if (s.started_at && g.started_at === s.started_at) return true;
              // Secondary match: within 30 mins of the last event in that group
              if (!s.started_at || !g.started_at) {
                const lastEvent = g.events[g.events.length - 1];
                const diff = Math.abs(sTime - new Date(lastEvent.ts)) / 60000;
                return diff < 30;
              }
              return false;
            });

            if (group) {
              group.events.push(s);
              // Update group's started_at if we found one
              if (s.started_at) group.started_at = s.started_at;
            } else {
              groups.push({ started_at: s.started_at, events: [s] });
            }
          });

          const groupedSessions = groups.map((g) => {
            const events = g.events;
            const sorted = [...events].sort((a, b) => new Date(a.ts) - new Date(b.ts));
            const first = sorted[0];
            const last = sorted[sorted.length - 1];
            
            const isStopped = sorted.some(e => e.status === 'stopped' || e.status === 'break');
            const startTime = new Date(first.started_at || first.ts);
            const endTime = isStopped ? new Date(last.ts) : new Date();
            
            let durationMins = Math.round((endTime - startTime) / 60000);
            if (durationMins <= 0 && last.started_at && last.ts !== last.started_at) {
              durationMins = Math.round((new Date(last.ts) - new Date(last.started_at)) / 60000);
            }

            // 2. Associate focus scores that occurred during this session
            const sessionScores = (focusData || []).filter(f => {
              const fTime = new Date(f.ts);
              return fTime >= startTime && fTime <= endTime;
            });

            const avgScore = sessionScores.length > 0 
              ? Math.round(sessionScores.reduce((a, b) => a + (b.score || 0), 0) / sessionScores.length)
              : (last.score || first.score || 0);

            return {
              title: first.phase ? (first.phase.charAt(0).toUpperCase() + first.phase.slice(1) + " Session") : "Focus Session",
              status: isStopped ? "completed" : last.status,
              mins: Math.max(0, durationMins),
              score: avgScore,
              poms: Math.max(0, Math.floor(durationMins / 25)),
              time: first.started_at || first.ts,
            };
          });

          setSessions(groupedSessions.sort((a, b) => new Date(b.time) - new Date(a.time)));
        }
      } catch (err) {
        console.error("Failed to load history:", err);
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
