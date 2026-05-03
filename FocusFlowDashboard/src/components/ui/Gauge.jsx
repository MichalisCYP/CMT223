import React from 'react';
import { T } from '../../constants/theme';

export default function Gauge({ value, max, label, unit, color, size = 108 }) {
  const r = (size - 14) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - Math.min(value / max, 1) * 0.75);
  const rot = `rotate(135 ${size / 2} ${size / 2})`;

  return (
    <div style={{ textAlign: "center" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.04)"
          strokeWidth="5"
          strokeDasharray={`${c * 0.75} ${c * 0.25}`}
          strokeLinecap="round"
          transform={rot}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeDasharray={`${c * 0.75} ${c * 0.25}`}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={rot}
          style={{
            transition: "stroke-dashoffset 0.9s cubic-bezier(0.4,0,0.2,1)",
          }}
        />
        <text
          x={size / 2}
          y={size / 2 - 3}
          textAnchor="middle"
          dominantBaseline="central"
          style={{
            fontSize: 19,
            fontWeight: 600,
            fill: T.text,
            fontFamily: T.sans,
          }}
        >
          {Math.round(value)}
        </text>
        <text
          x={size / 2}
          y={size / 2 + 15}
          textAnchor="middle"
          style={{ fontSize: 9, fill: T.muted, fontFamily: T.mono }}
        >
          {unit}
        </text>
      </svg>
      <div style={{ fontSize: 10, color: T.muted, marginTop: -2 }}>{label}</div>
    </div>
  );
}
