import React from 'react';

export default function ChatBubble({ role, text }) {
  const isUser = role === 'user';
  return (
    <div style={{
      alignSelf: isUser ? 'flex-end' : 'flex-start',
      maxWidth: '80%',
      background: isUser ? 'rgba(52,211,153,0.14)' : 'rgba(59,130,246,0.12)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 18,
      padding: '12px 16px',
      color: '#e2e8f0',
      lineHeight: 1.6,
      fontSize: 14,
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-word',
    }}>
      {text}
    </div>
  );
}
