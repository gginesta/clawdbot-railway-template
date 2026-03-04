# OpenClaw Voice & Call Capabilities — Research Brief
**Researcher:** Molty 🦎  
**Date:** 2026-03-05  
**MC Task:** jn797a52wcn176t5kj4bt715d5829fvw

---

## TL;DR

OpenClaw has three distinct voice layers for Telegram. Two are already active on Molty today. One requires a paired node (Guillermo's phone/laptop). No "live phone call" via PSTN exists — this is all Telegram-native async voice or real-time voice via Talk Mode on a paired device.

---

## Layer 1: Inbound STT — Voice → Text (✅ LIVE on Molty)

Guillermo sends a Telegram voice note → Molty transcribes → processes as text command.

**Current Molty config:**
```json
"audio": {
  "enabled": true,
  "maxBytes": 20971520,  // 20MB
  "models": [
    { "provider": "openai", "model": "gpt-4o-mini-transcribe" },  // primary
    { "provider": "gemini", "model": "gemini-2.0-flash" }         // fallback
  ]
}
```

**What works right now:**
- Guillermo sends a voice note on Telegram
- Molty transcribes using OpenAI gpt-4o-mini-transcribe (falls back to Gemini)
- Transcript is processed as if typed — slash commands work too
- 20MB file size limit

**Other STT providers available (not configured):**
- Deepgram nova-3 (low latency, real-time capable)
- Groq Whisper (fast + cheap)
- Local Whisper CLI (free, offline, no API calls)
- Mistral Voxtral

---

## Layer 2: Outbound TTS — Text → Voice (✅ LIVE on Molty)

Molty's replies are converted to audio and sent as round voice-note bubbles on Telegram.

**Current Molty config:**
```json
"tts": {
  "auto": "inbound",           // responds with voice ONLY when user sent voice
  "provider": "elevenlabs",
  "elevenlabs": {
    "voiceId": "onwK4e9ZLuTAKqWW03F9",
    "modelId": "eleven_multilingual_v2"
  },
  "edge": { "enabled": false }
}
```

**What works right now:**
- When Guillermo sends a voice note, Molty replies as a voice note (round bubble in Telegram)
- Uses ElevenLabs eleven_multilingual_v2 (high quality, supports Spanish accent)
- `auto: "inbound"` is the safest mode — no surprise audio on text messages
- Can override per-session with `/tts always` or `/tts off`

**TTS mode options:**
| Mode | Behavior |
|------|----------|
| `off` | Never speaks |
| `inbound` | Speaks only when user sent a voice note (current setting ✅) |
| `always` | Always speaks, regardless of input type |
| `tagged` | Only speaks when reply tagged with `[[tts:...]]` |

---

## Layer 3: Talk Mode — Real-Time Continuous Voice (⚠️ REQUIRES PAIRED NODE)

Continuous voice conversation loop: Listen → Transcribe → Model → Speak. This is "Siri-like" always-on mode.

**Requirements:**
- A paired OpenClaw Node running on Guillermo's device (macOS, iOS, or Android)
- ElevenLabs API key (already have: `sk_a381c3fc...`)
- The node must be paired to Guillermo's OpenClaw instance

**How it works:**
1. Node listens for speech (VAD — voice activity detection)
2. On pause: transcript sent to model
3. Model response generated
4. ElevenLabs speaks reply (streaming, low latency)
5. Interrupt on speech: Guillermo can cut off Molty mid-sentence

**Config needed:**
```json
{
  "talk": {
    "voiceId": "onwK4e9ZLuTAKqWW03F9",
    "modelId": "eleven_v3",
    "apiKey": "sk_a381c3fc850c6f3551be02379bb6ecf6b39430aa8fa6b143",
    "interruptOnSpeech": true
  }
}
```

**Current status:** NOT configured. Would need Guillermo to:
1. Install OpenClaw on his phone or Mac
2. Pair the node
3. Add `talk` config

---

## What DOESN'T Exist in OpenClaw

- ❌ PSTN phone calls (no dial-in/dial-out)
- ❌ WebRTC video calls
- ❌ Real-time phone conversation through Telegram (Telegram's own call API isn't exposed)
- ❌ Proactive voice calls initiated by Molty unprompted

---

## Current State Assessment

| Capability | Status | Notes |
|-----------|--------|-------|
| Receive voice messages from Guillermo | ✅ Active | gpt-4o-mini-transcribe + Gemini fallback |
| Reply as voice note to Guillermo | ✅ Active | ElevenLabs, inbound mode |
| Two-way async voice on Telegram | ✅ Active | Both layers working |
| Real-time voice conversation | ⚠️ Needs setup | Talk Mode, requires paired node |
| Phone call initiation | ❌ Not possible | Not in OpenClaw's feature set |

---

## Recommendations

### Quick Wins (No New Config)
1. **Test today**: Send Molty a voice note on Telegram — both STT and TTS should work out of the box
2. **Voice commands**: "Hey Molty, what's on my calendar today?" via voice will work now

### If Guillermo Wants Real-Time Conversation
1. Install OpenClaw node on his iPhone/Mac
2. Add `talk` block to config
3. Pair the node
4. Invoke Talk Mode → real-time voice assistant on his device

### Optional Optimizations
- Switch TTS to `eleven_turbo_v2_5` for lower latency (vs `eleven_multilingual_v2`)
- Add Deepgram nova-3 as STT primary for ~200ms faster transcription
- Set `auto: "always"` if Guillermo wants voice replies even to text messages

---

## References
- TTS docs: https://docs.openclaw.ai/tts
- Audio/STT docs: https://docs.openclaw.ai/nodes/audio
- Talk Mode docs: https://docs.openclaw.ai/nodes/talk
- Molty config: `/data/.openclaw/openclaw.json`
