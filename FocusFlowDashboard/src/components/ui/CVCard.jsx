import React from 'react';
import { T } from '../../constants/theme';

export default function CVCard({ data }) {
  if (!data || !data.timestamp) {
    return (
      <div style={{ color: T.dim, fontSize: 13, padding: "16px 0" }}>
        Waiting for camera data…
      </div>
    );
  }
  const ts = new Date(data.timestamp).toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  const items = [
    {
      ok: data.face_present,
      label: `Face ${data.face_present ? "detected" : "not detected"}`,
    },
    {
      ok: data.eyes_detected,
      label: `Eyes ${data.eyes_detected ? "focused" : "not detected"}`,
    },
    {
      ok: !data.slouching,
      label: `Posture ${data.slouching ? "slouching!" : "good"}`,
    },
    {
      ok: !data.looking_away,
      label: data.looking_away ? "Looking away" : "Attentive",
    },
  ];
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((it, i) => (
        <div
          key={i}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "9px 14px",
            background: "rgba(255,255,255,0.015)",
            borderRadius: 10,
          }}
        >
          <span
            style={{
              width: 9,
              height: 9,
              borderRadius: "50%",
              background: it.ok ? T.accent : T.danger,
              boxShadow: `0 0 8px ${it.ok ? "rgba(52,211,153,0.4)" : "rgba(248,113,113,0.4)"}`,
              flexShrink: 0,
            }}
          />
          <span style={{ fontSize: 13, color: "#cbd5e1" }}>{it.label}</span>
        </div>
      ))}
      <div
        style={{
          fontSize: 10,
          color: T.dim,
          textAlign: "right",
          fontFamily: T.mono,
          marginTop: 2,
        }}
      >
        Updated {ts}
      </div>
    </div>
  );
}
