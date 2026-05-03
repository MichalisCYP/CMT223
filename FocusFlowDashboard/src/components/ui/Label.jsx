import React from 'react';
import { T } from '../../constants/theme';

export default function Label({ children, tag, tagLive }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        marginBottom: 14,
      }}
    >
      <span
        style={{
          fontSize: 10,
          fontWeight: 600,
          color: T.muted,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
        }}
      >
        {children}
      </span>
      {tag !== undefined && (
        <span
          style={{
            fontSize: 8,
            padding: "2px 8px",
            borderRadius: 6,
            fontFamily: T.mono,
            fontWeight: 500,
            letterSpacing: "0.05em",
            background: tagLive ? T.accentDim : "rgba(251,191,36,0.1)",
            color: tagLive ? T.accent : T.warn,
            border: `1px solid ${tagLive ? "rgba(52,211,153,0.2)" : "rgba(251,191,36,0.2)"}`,
          }}
        >
          {tag}
        </span>
      )}
    </div>
  );
}
