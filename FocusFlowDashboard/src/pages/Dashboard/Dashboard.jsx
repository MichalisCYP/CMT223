import React, { useState, useEffect } from 'react';
import Header from '../../components/layout/Header';
import LiveView from './LiveView';
import HistoryView from './HistoryView';
import { T } from '../../constants/theme';
import useSensorData from '../../hooks/useSensorData';
import useTimer from '../../hooks/useTimer';

export default function Dashboard({ initialView = "live", onOpenChat, navigate }) {
  const [view, setView] = useState(initialView);
  const [autoMusic, setAutoMusic] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);

  const timerData = useTimer();
  const sensorData = useSensorData(timerData.active);

  // Auto-start music when session begins
  useEffect(() => {
    if (timerData.active && autoMusic && !timerData.paused) {
      setIsPlaying(true);
    }
    // Stop music when session finishes? Optional, but maybe good.
    // if (!timerData.active) setIsPlaying(false);
  }, [timerData.active, autoMusic, timerData.paused]);

  const handleOpenDashboard = () => {
    setView("live");
    navigate('/');
  };

  const handleOpenHistory = () => {
    setView("history");
    navigate('/history');
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.bg,
        color: T.text,
        fontFamily: T.sans,
      }}
    >
      <Header 
        view={view}
        onViewChange={setView}
        cvOk={sensorData.cvOk}
        envOk={sensorData.envOk}
        onOpenChat={onOpenChat}
        onOpenDashboard={handleOpenDashboard}
        onOpenHistory={handleOpenHistory}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
      />

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "28px 24px" }}>
        {view === "live" && (
          <LiveView 
            {...timerData}
            {...sensorData}
            onOpenChat={onOpenChat}
            autoMusic={autoMusic}
            setAutoMusic={setAutoMusic}
          />
        )}
        {view === "history" && <HistoryView />}
      </main>
    </div>
  );
}
