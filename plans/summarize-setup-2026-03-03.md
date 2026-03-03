# Summarize CLI Setup Plan
**Date:** 2026-03-03
**Author:** Molty 🦎
**Status:** In Progress

## Objective
Install and configure `@steipete/summarize` as a first-class Molty skill.
Unlock YouTube + podcast summarisation for Guillermo's content consumption.

## Current State
- `npx @steipete/summarize` works (v0.11.1) — slow, no global binary
- Skill file: `/openclaw/skills/summarize/SKILL.md` — exists but requires `summarize` binary on PATH
- Missing: `yt-dlp`, `ffmpeg` (YouTube/podcast/audio features)
- Missing: permanent config (API keys, default model)

## Target State
- `summarize` binary on PATH (global npm install)
- `yt-dlp` on PATH (pip install → venv → symlink to /usr/local/bin)
- `ffmpeg` installed (apt)
- `~/.summarize/config.json` configured (Gemini default, Anthropic fallback, ANTHROPIC_API_KEY)
- Skill auto-discovered by OpenClaw (binary present → `requires.bins` satisfied)
- Full YouTube + podcast summarisation working

## Steps

### Step 1 — Install summarize globally
```bash
npm install -g @steipete/summarize
```
Makes `summarize` available as a command on PATH.

### Step 2 — Install yt-dlp
```bash
/data/workspace/.venv/bin/pip install yt-dlp
ln -sf /data/workspace/.venv/bin/yt-dlp /usr/local/bin/yt-dlp
```
Required for: YouTube audio download → Whisper transcription, podcast audio.

### Step 3 — Install ffmpeg
```bash
apt-get install -y ffmpeg
```
Required for: audio extraction, slide screenshots, scene detection.

### Step 4 — Configure ~/.summarize/config.json
```json
{
  "model": "google/gemini-2.5-flash",
  "env": {
    "GEMINI_API_KEY": "<key>",
    "ANTHROPIC_API_KEY": "<key>"
  },
  "models": {
    "fast":   { "id": "google/gemini-2.5-flash" },
    "smart":  { "id": "anthropic/claude-sonnet-4-6" },
    "long":   { "id": "google/gemini-2.5-flash" }
  }
}
```

### Step 5 — Test suite
1. Web article (existing working baseline)
2. YouTube with transcript (known-captioned video)
3. Podcast RSS feed (All-In: feeds.megaphone.fm/allin)
4. Verify skill in available_skills on next session load

### Step 6 — Update MEMORY.md
Add lesson: summarize installed, config location, model defaults.

## Success Criteria
- [x] `summarize --version` works directly (no npx) — v0.11.1 ✅
- [x] yt-dlp installed — v2026.02.21 ✅
- [x] ffmpeg installed — v7.0.2 (static build) ✅
- [x] Config written — ~/.summarize/config.json with Gemini default + Anthropic fallback ✅
- [ ] YouTube video → real summary — ❌ BLOCKED (see findings)
- [ ] Podcast RSS → summary — ❌ BLOCKED (see findings)
- [x] Web articles — ✅ Works well
- [x] Direct audio/video URLs — ✅ Works via OpenAI Whisper
- [ ] Skill appears in available_skills — expected on next session start

## Findings (Post-Install Testing)

### YouTube: Blocked at Railway level
yt-dlp returns: "Sign in to confirm you're not a bot."
Both yt-dlp AND the HTTP transcript API endpoints (youtubei, captionTracks) are blocked.
Railway datacenter IPs are flagged by YouTube anti-bot systems.
**No fix without browser cookies or Apify API key.**

### Podcast RSS: File size issue
Tim Ferriss RSS = 29MB (too large, 10MB limit).
Acquired RSS = empty summary (no embedded transcript in feed).
RSS feeds without inline transcripts don't work — would need audio download (blocked by same issue).

### What Actually Works
| Source | Result |
|--------|--------|
| Web articles | ✅ Excellent — fast, clean, better than web_fetch for some sites |
| Direct audio URLs (MP3/M4A) | ✅ Whisper transcription via OPENAI_API_KEY |
| Direct video URLs (MP4) | ✅ Same pipeline |
| PDFs | ⚠️ Works if under 10MB, Google API needed |
| YouTube | ❌ Bot detection blocks datacenter IPs |
| Podcast RSS | ❌ Too large or no inline transcript |

### Chrome Extension Use Case (Not Our Path)
The extension + local daemon approach would handle YouTube fine
because it runs in Guillermo's browser (not Railway). Not relevant for agent use.
Guillermo could install the Chrome extension for personal YouTube summarisation.

## Status: DONE (partial)
Core installation complete. Web articles + direct audio work.
YouTube and podcasts blocked by Railway IP restrictions — not fixable server-side.
Skill will auto-appear in available_skills on next session (binary now on PATH).
