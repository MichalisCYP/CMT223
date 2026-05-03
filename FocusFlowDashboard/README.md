# FocusFlow AI Agent + Tutor Chat

This folder now includes a local AI API server for:

- Receiving your friend's Raspberry Pi data over LAN (`/api/peer-ingest`)
- Generating a study session report with Groq (`/api/agent/report`)
- Running a mini tutoring buddy chat (`/api/agent/chat`)

## 1) Environment setup

```bash
cd raspberry2
cp .env.example .env
```

Edit `.env` and set:

- `GROQ_API_KEY` (required)
- `PEER_SHARED_TOKEN` (optional but recommended)

## 2) Install and run

```bash
npm install
npm run dev:all
```

- Frontend dashboard: `http://localhost:5173`
- Local AI API: `http://localhost:8787`

## 3) Friend Pi sender (LAN)

Use `server/peer_sender_example.py` on your friend's Pi:

1. Set `TARGET_API` to your Pi LAN IP, for example `http://192.168.1.50:8787/api/peer-ingest`
2. Set `PEER_TOKEN` to match your `.env` value
3. Run:

```bash
python3 server/peer_sender_example.py
```

## 4) Dashboard usage

In the Live Session view:

- Click **Generate AI Report** for a summary + recommendations
- Use **Mini Tutoring Buddy** chat for personalized study help

The AI uses combined context from:

- Camera/CV feed from your AWS endpoint
- Your local focus/session telemetry
- Your friend's LAN-ingested environment/audio updates
