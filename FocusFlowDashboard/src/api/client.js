export const API = "https://6q2yskmyc7.execute-api.eu-west-2.amazonaws.com/prod";

export async function api(path, body) {
  try {
    const res = await fetch(path.startsWith('/api') ? path : `${API}${path}`, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });

    const contentType = res.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await res.json();
    } else {
      const text = await res.text();
      if (!res.ok) {
        throw new Error(`Server error (${res.status}): ${text.slice(0, 100)}${text.length > 100 ? '...' : ''}`);
      }
      return text;
    }

    if (!res.ok) {
      throw new Error(data?.error || `Request failed with status ${res.status}`);
    }
    return data;
  } catch (err) {
    if (err.name === 'SyntaxError') {
      throw new Error('Failed to parse server response as JSON. The server might be down or returning an error page.');
    }
    throw err;
  }
}

export const mockSensors = () => {
  const t = Date.now() / 1000;
  return {
    light: Math.round(420 + Math.sin(t / 30) * 80 + Math.random() * 40),
    sound: Math.round(180 + Math.sin(t / 15) * 90 + Math.random() * 60),
    motion: Math.random() > 0.3 ? 1 : 0,
    temp: +(21.5 + Math.sin(t / 120) * 1.5 + Math.random() * 0.5).toFixed(1),
    hum: +(48 + Math.sin(t / 90) * 8 + Math.random() * 2).toFixed(1),
  };
};

export const MOCK_SESSIONS = [
  {
    title: "Morning Study",
    status: "completed",
    mins: 52,
    score: 78,
    poms: 2,
    time: "2026-04-20T09:00:00Z",
  },
  {
    title: "Algorithms Review",
    status: "completed",
    mins: 75,
    score: 64,
    poms: 3,
    time: "2026-04-20T14:00:00Z",
  },
  {
    title: "Report Writing",
    status: "completed",
    mins: 48,
    score: 82,
    poms: 2,
    time: "2026-04-19T11:00:00Z",
  },
  {
    title: "IoT Lab Prep",
    status: "completed",
    mins: 25,
    score: 91,
    poms: 1,
    time: "2026-04-19T16:00:00Z",
  },
  {
    title: "Literature Review",
    status: "completed",
    mins: 90,
    score: 57,
    poms: 3,
    time: "2026-04-18T10:30:00Z",
  },
];
