import React from 'react';
import { T } from '../../constants/theme';

export default function Card({ children, span, delay = 0, style }) {
  return (
    <div
      style={{
        background: T.surface,
        border: `1px solid ${T.border}`,
        borderRadius: T.radius,
        padding: "22px 26px",
        gridColumn: span ? `span ${span}` : undefined,
        animation: `fadeUp 0.45s ${delay}s ease both`,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
