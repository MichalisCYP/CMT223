import React from 'react';
import { T } from '../../constants/theme';

export default function StatusDot({ ok, label }) {
  const color = ok === true ? T.accent : ok === "warn" ? T.warn : T.danger;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
      <span
        style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 8px ${color}66`,
          animation: "pulse 2s infinite",
        }}
      />
      <span style={{ fontSize: 10, color: T.muted, fontFamily: T.mono }}>
        {label}
      </span>
    </div>
  );
}
