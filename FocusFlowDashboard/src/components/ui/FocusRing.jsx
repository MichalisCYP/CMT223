import React from 'react';
import { T } from '../../constants/theme';
import { scoreColor } from '../../utils/helpers';

export default function FocusRing({ score, confidence }) {
  const color = scoreColor(score);
  const sz = 174,
    r = 72,
    c = 2 * Math.PI * r;
  const confLabel =
    typeof confidence === "number"
      ? confidence > 0.7
        ? "high"
        : confidence > 0.4
          ? "medium"
          : "low"
      : confidence || "low";
  const confColor =
    confLabel === "high"
      ? T.accent
      : confLabel === "medium"
        ? T.warn
        : T.danger;

  return (
    <div style={{ textAlign: "center" }}>
      <svg width={sz} height={sz} viewBox={`0 0 ${sz} ${sz}`}>
        <circle
          cx={sz / 2}
          cy={sz / 2}
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.03)"
          strokeWidth="9"
        />
        <circle
          cx={sz / 2}
          cy={sz / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="9"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - score / 100)}
          strokeLinecap="round"
          transform={`rotate(-90 ${sz / 2} ${sz / 2})`}
          style={{
            transition:
              "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1), stroke 0.6s ease",
            filter: `drop-shadow(0 0 10px ${color}33)`,
          }}
        />
        <text
          x={sz / 2}
          y={sz / 2 - 6}
          textAnchor="middle"
          dominantBaseline="central"
          style={{
            fontSize: 40,
            fontWeight: 700,
            fill: color,
            fontFamily: T.sans,
            transition: "fill 0.5s",
          }}
        >
          {score}
        </text>
        <text
          x={sz / 2}
          y={sz / 2 + 20}
          textAnchor="middle"
          style={{
            fontSize: 10,
            fill: T.muted,
            fontFamily: T.mono,
            letterSpacing: "0.12em",
          }}
        >
          FOCUS SCORE
        </text>
      </svg>
      <div
        style={{
          marginTop: 6,
          fontSize: 11,
          color: T.muted,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 6,
        }}
      >
        <span
          style={{
            width: 6,
            height: 6,
            borderRadius: "50%",
            background: confColor,
          }}
        />
        {confLabel} confidence
      </div>
    </div>
  );
}
