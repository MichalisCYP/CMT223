import React, { useEffect, useRef } from 'react';
import { T } from '../../constants/theme';
import StatusDot from '../ui/StatusDot';

export default function Header({
  view,
  onViewChange,
  cvOk,
  envOk,
  onOpenChat,
  onOpenDashboard,
  onOpenHistory,
  isPlaying,
  setIsPlaying
}) {
  const audioRef = useRef(null);

  // Sync audio playback with isPlaying prop
  useEffect(() => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.play().catch(err => {
        console.warn("Autoplay blocked by browser. User interaction needed.", err);
        setIsPlaying(false);
      });
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying, setIsPlaying]);

  const toggleMusic = () => {
    setIsPlaying(!isPlaying);
  };

  const navBtn = (v) => ({
    padding: "8px 22px",
    borderRadius: 10,
    border: "none",
    cursor: "pointer",
    fontFamily: T.sans,
    fontSize: 13,
    fontWeight: 600,
    background: view === v ? T.accentDim : "transparent",
    color: view === v ? T.accent : T.muted,
    transition: "all 0.2s",
  });

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "18px 32px",
        borderBottom: `1px solid ${T.border}`,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: 9,
            background: `linear-gradient(135deg, ${T.accent}, #059669)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: T.mono,
            fontWeight: 700,
            fontSize: 13,
            color: "#000",
          }}
        >
          FF
        </div>
        <div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 700,
              letterSpacing: "-0.02em",
            }}
          >
            FocusFlow
          </div>
          <div style={{ fontSize: 10, color: T.dim, fontFamily: T.mono }}>
            Smart IoT Desk Assistant
          </div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        {/* Lofi Music Player */}
        <div 
          style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 10, 
            padding: "6px 14px", 
            background: "rgba(255,255,255,0.03)", 
            borderRadius: 20,
            border: `1px solid ${T.border}`
          }}
        >
          <span style={{ fontSize: 14 }}>🎵</span>
          <div style={{ fontSize: 11, fontWeight: 600, color: T.muted, textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Lofi Radio
          </div>
          <button
            onClick={toggleMusic}
            style={{
              width: 28,
              height: 28,
              borderRadius: "50%",
              border: "none",
              background: isPlaying ? T.accent : "rgba(255,255,255,0.1)",
              color: isPlaying ? "#000" : T.text,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 10,
              transition: "all 0.2s"
            }}
          >
            {isPlaying ? "⏸" : "▶"}
          </button>
          <audio ref={audioRef} src="/sounds/music.mp3" loop />
        </div>

        <nav style={{ display: "flex", gap: 4 }}>
          <button style={navBtn("live")} onClick={onOpenDashboard}>
            Live Session
          </button>
          <button style={navBtn("history")} onClick={onOpenHistory}>
            History
          </button>
          <button style={navBtn("chat")} onClick={onOpenChat}>
            Tutor Buddy
          </button>
        </nav>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 4,
          alignItems: "flex-end",
        }}
      >
        <StatusDot ok={cvOk} label={cvOk ? "CV live" : "CV offline"} />
        <StatusDot
          ok={envOk}
          label={envOk ? "Sensors live" : "Sensors offline"}
        />
      </div>
    </header>
  );
}
