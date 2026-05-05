import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import cors from "cors";
import dotenv from "dotenv";
import express from "express";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = Number(process.env.PORT || 8787);
const GROQ_API_KEY = process.env.GROQ_API_KEY || "";
const GROQ_MODEL = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";
const PEER_SHARED_TOKEN = process.env.PEER_SHARED_TOKEN || "";
const CV_API = process.env.CV_API || "https://6q2yskmyc7.execute-api.eu-west-2.amazonaws.com/prod";

const peerLogDir = path.join(__dirname, "data");
const peerLogPath = path.join(peerLogDir, "peer-log.jsonl");

// Ensure data directory exists for logging
if (!fs.existsSync(peerLogDir)) {
  fs.mkdirSync(peerLogDir, { recursive: true });
}

let latestPeerPayload = null;

app.use(cors());
app.use(express.json({ limit: "1mb" }));

function buildPromptContext({ cv, peer, local }) {
  // keep cameraCV as-provided by the CV service; phone detection removed
  const cameraCV = Object.assign({}, cv || {});
  return {
    timestamp: new Date().toISOString(),
    cameraCV,
    peerEnvironmentAndAudio: peer,
    localDashboard: local,
  };
}

async function fetchLatestCV() {
  try {
    const res = await fetch(`${CV_API}/cv/latest`);
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch {
    return null;
  }
}

async function callGroq(messages, temperature = 0.4) {
  if (!GROQ_API_KEY) {
    throw new Error("Missing GROQ_API_KEY in environment.");
  }

  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${GROQ_API_KEY}`,
    },
    body: JSON.stringify({
      model: GROQ_MODEL,
      messages,
      temperature,
    }),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Groq request failed (${res.status}): ${detail}`);
  }

  const data = await res.json();
  const content = data?.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error("Groq returned an empty response.");
  }

  return content;
}

function enforcePeerAuth(req, res, next) {
  if (!PEER_SHARED_TOKEN) {
    next();
    return;
  }

  const token = req.header("x-peer-token");
  if (token !== PEER_SHARED_TOKEN) {
    res.status(401).json({ error: "Unauthorized peer sender." });
    return;
  }

  next();
}

app.get("/api/health", (_req, res) => {
  res.json({ ok: true, model: GROQ_MODEL, hasGroqKey: Boolean(GROQ_API_KEY) });
});

app.post("/api/peer-ingest", enforcePeerAuth, (req, res) => {
  const payload = {
    sourcePi: req.body?.sourcePi || "friend-rpi",
    timestamp: req.body?.timestamp || new Date().toISOString(),
    environment: req.body?.environment || {},
    audio: req.body?.audio || {},
    transcript: req.body?.transcript || "",
  };

  latestPeerPayload = payload;
  fs.appendFileSync(peerLogPath, `${JSON.stringify(payload)}\n`, "utf8");

  res.json({ ok: true, receivedAt: new Date().toISOString() });
});

app.get("/api/peer/latest", (_req, res) => {
  res.json({ payload: latestPeerPayload });
});

app.post("/api/agent/report", async (req, res) => {
  try {
    const localData = {
      focusHistory: req.body?.focusHistory || [],
      sensorHistory: req.body?.sensorHistory || [],
      events: req.body?.events || [],
      focusScore: req.body?.focusScore ?? null,
      focusConfidence: req.body?.focusConfidence || null,
      sessionMeta: req.body?.sessionMeta || {},
    };

    const cv = await fetchLatestCV();
    const context = buildPromptContext({ cv, peer: latestPeerPayload, local: localData });

    const system = "You are FocusFlow Analyst. Analyze study sessions and return insights as valid JSON. Avoid hallucinating data. When data is missing, explicitly say it. IMPORTANT: Return ONLY valid JSON object, no markdown code blocks, no extra text, just the JSON.";
    const user = `Return ONLY this JSON shape (no markdown, no extra text, just the object):\n{\n  \"summary\": string (1-2 sentences about the session),\n  \"focusHighlights\": string[] (3-5 positive observations),\n  \"riskFlags\": string[] (3-5 areas of concern, or empty if none),\n  \"recommendations\": string[] (3-5 actionable improvements),\n  \"nextSessionPlan\": string[] (3-5 focus areas for next session)\n}\n\nSession Context:\n${JSON.stringify(context)}`;

    const raw = await callGroq(
      [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
      0.2,
    );

    let parsed;
    
    // Try direct JSON parse first
    try {
      parsed = JSON.parse(raw);
    } catch {
      // Try multiple patterns to extract JSON from markdown or other wrappers
      let jsonStr = null;
      
      // Pattern 1: ```json {...} ```
      let match = raw.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
      if (match) jsonStr = match[1];
      
      // Pattern 2: Just find the largest {...} block
      if (!jsonStr) {
        const braceMatch = raw.match(/\{[\s\S]*\}/);
        if (braceMatch) jsonStr = braceMatch[0];
      }
      
      // Try to parse extracted JSON
      if (jsonStr) {
        try {
          parsed = JSON.parse(jsonStr);
        } catch {
          parsed = null;
        }
      }
      
      // If still no valid JSON, create structured fallback from raw text
      if (!parsed) {
        parsed = {
          summary: raw.slice(0, 300) || "Session analysis generated.",
          focusHighlights: [],
          riskFlags: [],
          recommendations: [],
          nextSessionPlan: [],
        };
      }
    }

    // Ensure all fields are arrays/strings and never empty
    if (!parsed.summary || parsed.summary.includes("fallback")) parsed.summary = "Session analysis generated.";
    if (!Array.isArray(parsed.focusHighlights)) parsed.focusHighlights = [];
    if (!Array.isArray(parsed.riskFlags)) parsed.riskFlags = [];
    if (!Array.isArray(parsed.recommendations)) parsed.recommendations = [];
    if (!Array.isArray(parsed.nextSessionPlan)) parsed.nextSessionPlan = [];

    res.json({ report: parsed, context });
  } catch (error) {
    res.status(500).json({ error: String(error?.message || error) });
  }
});

app.post("/api/agent/chat", async (req, res) => {
  try {
    const message = String(req.body?.message || "").trim();
    if (!message) {
      res.status(400).json({ error: "message is required" });
      return;
    }

    const chatHistory = Array.isArray(req.body?.history) ? req.body.history : [];
    const cv = await fetchLatestCV();
    const context = buildPromptContext({
      cv,
      peer: latestPeerPayload,
      local: req.body?.localContext || {},
    });

    const system = "You are FocusFlow Tutor Buddy. Be friendly, practical, and concise. Use provided IoT and session context for personalized advice. If user asks beyond context, still help with study techniques.";

    const messages = [
      { role: "system", content: system },
      {
        role: "user",
        content: `Session context JSON:\n${JSON.stringify(context)}`,
      },
      ...chatHistory.slice(-8),
      { role: "user", content: message },
    ];

    const reply = await callGroq(messages, 0.5);
    res.json({ reply, context });
  } catch (error) {
    res.status(500).json({ error: String(error?.message || error) });
  }
});

app.listen(port, "0.0.0.0", () => {
  console.log(`\n🚀 FocusFlow AI API listening on http://localhost:${port}`);
  console.log(`📡 Model: ${GROQ_MODEL}`);
  console.log(`🔑 Groq Key: ${GROQ_API_KEY ? "✅ Loaded" : "❌ Missing"}`);
  console.log(`🔗 CV API: ${CV_API}\n`);
});
