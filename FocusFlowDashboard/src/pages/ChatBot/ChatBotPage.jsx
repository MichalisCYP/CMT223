import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { T } from '../../constants/theme';
import Header from '../../components/layout/Header';
import ChatBubble from '../../components/chat/ChatBubble';
import useSpeechDictation from '../../hooks/useSpeechDictation';

export default function ChatBotPage({ onOpenDashboard, onOpenHistory, onOpenChat }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Ask me what to study, how to revise, or how to improve your next focus block.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [cvStatus, setCvStatus] = useState(false);
  const [envStatus, setEnvStatus] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await api('/cv/latest');
        setCvStatus(!!data?.timestamp);
      } catch {
        setCvStatus(false);
      }
    })();

    (async () => {
      try {
        const data = await api('/env/latest');
        setEnvStatus(!!data?.ts);
      } catch {
        setEnvStatus(false);
      }
    })();

    const savedDraft = window.localStorage.getItem('focusflow_chat_draft');
    if (savedDraft) {
      setInput(savedDraft);
      window.localStorage.removeItem('focusflow_chat_draft');
    }
  }, []);

  const { listening, error: micError, startDictation } = useSpeechDictation((transcript) => {
    setInput((prev) => `${prev ? `${prev} ` : ''}${transcript}`.trim());
  });

  const sendMessage = async () => {
    const message = input.trim();
    if (!message || loading) return;

    const nextMessages = [...messages, { role: 'user', text: message }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);

    try {
      const history = nextMessages.slice(-12).map((item) => ({ role: item.role, content: item.text }));
      const latestCv = await api('/cv/latest').catch(() => null);
      const reply = await api('/api/agent/chat', {
        message,
        history,
        localContext: {
          page: 'chat-bot',
          cv: latestCv,
          timestamp: new Date().toISOString(),
        },
      });

      setMessages((prev) => [...prev, { role: 'assistant', text: reply.reply || 'No response returned.' }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', text: `Sorry, chat failed: ${error?.message || 'unknown error'}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: T.bg, color: T.text, fontFamily: T.sans }}>
      <Header 
        view="chat"
        cvOk={cvStatus}
        envOk={envStatus}
        onOpenChat={onOpenChat}
        onOpenDashboard={onOpenDashboard}
        onOpenHistory={onOpenHistory}
      />

      <main style={{ maxWidth: 980, margin: '0 auto', padding: '22px 20px 32px', height: 'calc(100vh - 78px)', boxSizing: 'border-box' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 18, height: '100%' }}>
          <section style={{ background: T.surface, border: `1px solid ${T.border}`, borderRadius: 18, padding: 20, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <div>
                <div style={{ fontSize: 10, color: T.muted, letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 6 }}>Chat bot</div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>Study helper and focus coach</div>
              </div>
              <div style={{ fontSize: 11, color: T.muted, fontFamily: T.mono }}>{messages.length - 1} replies</div>
            </div>

            <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10, paddingRight: 4, marginBottom: 16 }}>
              {messages.map((msg, index) => (
                <ChatBubble key={index} role={msg.role} text={msg.text} />
              ))}
              {loading && (
                <div style={{ color: T.muted, fontSize: 12, fontStyle: 'italic', padding: '4px 2px' }}>Thinking…</div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask for revision tips, quiz ideas, or a study plan…"
                style={{
                  flex: 1,
                  background: 'rgba(15,23,42,0.95)',
                  border: `1px solid ${T.border}`,
                  borderRadius: 12,
                  padding: '13px 16px',
                  color: T.text,
                  outline: 'none',
                  fontSize: 14,
                }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                style={{
                  padding: '13px 22px',
                  borderRadius: 12,
                  border: 'none',
                  background: `linear-gradient(135deg, ${T.accent}, #059669)`,
                  color: '#000',
                  fontWeight: 800,
                  fontSize: 13,
                  cursor: loading || !input.trim() ? 'default' : 'pointer',
                  opacity: loading || !input.trim() ? 0.6 : 1,
                }}
              >
                Send
              </button>
              <button
                onClick={startDictation}
                disabled={listening}
                title="Use microphone"
                style={{
                  padding: '13px 16px',
                  borderRadius: 12,
                  border: `1px solid ${T.border}`,
                  background: listening ? T.accentDim : 'rgba(255,255,255,0.03)',
                  color: listening ? T.accent : '#cbd5e1',
                  fontWeight: 800,
                  fontSize: 13,
                  cursor: listening ? 'default' : 'pointer',
                }}
              >
                {listening ? 'Listening…' : '🎤'}
              </button>
            </div>
            {micError && <div style={{ marginTop: 8, color: T.danger, fontSize: 12 }}>{micError}</div>}
          </section>

          <aside style={{ display: 'flex', flexDirection: 'column', gap: 14, minHeight: 0, height: '100%', alignSelf: 'stretch' }}>
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, background: T.surface, border: `1px solid ${T.border}`, borderRadius: 18, padding: 18, overflow: 'auto' }}>
              <div style={{ fontSize: 10, color: T.muted, letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 10 }}>Quick prompts</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {[
                  'Make me a 30 minute revision plan',
                  'What should I revise next for my IoT lab?',
                  'How can I improve focus this evening?',
                  'Give me a quiz on networking basics',
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    style={{
                      textAlign: 'left',
                      padding: '8px 10px',
                      borderRadius: 10,
                      border: '1px solid rgba(255,255,255,0.06)',
                      background: 'rgba(255,255,255,0.02)',
                      color: '#cbd5e1',
                      cursor: 'pointer',
                      fontSize: 12,
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ flex: '0 0 auto', background: T.surface, border: `1px solid ${T.border}`, borderRadius: 14, padding: 16 }}>
              <div style={{ fontSize: 10, color: T.muted, letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: 8 }}>Live context</div>
              <div style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.5 }}>
                The chat bot can use your latest CV snapshot, study session history, and AI agent context to give tailored study advice.
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}
