import React, { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard/Dashboard';
import ChatBotPage from './pages/ChatBot/ChatBotPage';

export default function AppRouter() {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = (nextPath) => {
    if (nextPath === window.location.pathname) return;
    window.history.pushState({}, '', nextPath);
    setPath(nextPath);
  };

  if (path === '/chat' || path.startsWith('/chat/')) {
    return (
      <ChatBotPage
        onOpenDashboard={() => navigate('/')}
        onOpenHistory={() => navigate('/history')}
        onOpenChat={() => navigate('/chat')}
      />
    );
  }

  if (path === '/history') {
    return (
      <Dashboard 
        initialView="history" 
        onOpenChat={() => navigate('/chat')} 
        navigate={navigate}
      />
    );
  }

  return (
    <Dashboard 
      initialView="live" 
      onOpenChat={() => navigate('/chat')} 
      navigate={navigate}
    />
  );
}
