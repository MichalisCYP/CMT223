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


