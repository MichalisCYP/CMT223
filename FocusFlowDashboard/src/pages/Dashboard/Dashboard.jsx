import React, { useState } from 'react';
import Header from '../../components/layout/Header';
import LiveView from './LiveView';
import HistoryView from './HistoryView';
import { T } from '../../constants/theme';
import useSensorData from '../../hooks/useSensorData';
import useTimer from '../../hooks/useTimer';

export default function Dashboard({ initialView = "live", onOpenChat, navigate }) {
  const [view, setView] = useState(initialView);

  const timerData = useTimer();
  const sensorData = useSensorData(timerData.active);

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
      />

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "28px 24px" }}>
        {view === "live" && (
          <LiveView 
            {...timerData}
            {...sensorData}
            onOpenChat={onOpenChat}
          />
        )}
        {view === "history" && <HistoryView />}
      </main>
    </div>
  );
}
