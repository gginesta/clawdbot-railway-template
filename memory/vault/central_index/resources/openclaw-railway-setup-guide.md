# OpenClaw Railway Setup Guide

*A step-by-step guide to deploying your personal AI assistant on Railway*

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Railway Account Setup](#railway-account-setup)
4. [Template Deployment](#template-deployment)
5. [Environment Variables](#environment-variables)
6. [Volume Setup for Persistence](#volume-setup-for-persistence)
7. [Connecting Telegram](#connecting-telegram)
8. [First Boot & Verification](#first-boot--verification)
9. [Control UI Access](#control-ui-access)
10. [Common Issues & Fixes](#common-issues--fixes)

---

## Overview

OpenClaw (formerly Clawdbot) is a personal AI assistant that runs in a Docker container. Railway provides an easy deployment path with persistent storage, environment variable management, and automatic restarts.

**What you'll have when done:**
- A Claude-powered AI assistant running 24/7
- Telegram integration for mobile access
- Persistent storage that survives redeployments
- Web-based Control UI for configuration

**Time to complete:** ~30 minutes (less if you're familiar with Railway)

---

## Prerequisites

Before starting, you'll need:

| Requirement | Where to Get It | Notes |
|-------------|-----------------|-------|
| **Anthropic API Key** | [console.anthropic.com](https://console.anthropic.com) | Required. Free tier works to start |
| **Railway Account** | [railway.app](https://railway.app) | Free tier: $5/month credit |
| **Telegram Account** | App stores | For mobile access |
| **GitHub Account** | [github.com](https://github.com) | For forking the template |

**Optional but recommended:**
- Additional API keys (OpenAI, OpenRouter) for model fallbacks
- Brave Search API key for web search
- VPN (Tailscale, etc.) for secure Control UI access

---

## Railway Account Setup

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended) or email
3. Verify your account

### 2. Set Up Billing (Recommended)
Railway's free tier includes $5/month credit, but setting up billing ensures uninterrupted service:
1. Go to **Settings** → **Billing**
2. Add a payment method
3. Set usage limits if desired

**Typical cost:** $2-10/month depending on usage (mostly idle time + occasional CPU spikes).

---

## Template Deployment

### Option A: One-Click Deploy (Easiest)
1. Go to the Railway template: [vignesh07/clawdbot-railway-template](https://railway.app/template/clawdbot)
2. Click **Deploy on Railway**
3. Fill in the required environment variables (see next section)
4. Click **Deploy**

### Option B: Fork & Deploy (Recommended for Customization)
This gives you control over the Dockerfile and dependencies:

1. **Fork the template:**
   ```
   https://github.com/vignesh07/clawdbot-railway-template
   ```
   Click **Fork** → Name it something like `my-openclaw`

2. **Add Chromium to Dockerfile** (for browser automation):
   Add this line to your forked Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*
   ```

3. **Deploy from GitHub:**
   - In Railway, click **New Project** → **Deploy from GitHub repo**
   - Select your forked repository
   - Railway will detect the Dockerfile and start building

---

## Environment Variables

In Railway, go to your service → **Variables** tab.

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Claude API key | `sk-ant-api...` |

### Recommended Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI key for fallback/features | `sk-proj-...` |
| `OPENROUTER_API_KEY` | OpenRouter for model variety | `sk-or-v1-...` |
| `BRAVE_SEARCH_API_KEY` | Web search capability | `BSA...` |
| `XAI_API_KEY` | xAI/Grok access | `xai-...` |

### Model Provider Keys (Add as needed)

```
GEMINI_API_KEY=...        # Google AI (free for embeddings!)
MISTRAL_API_KEY=...       # Mistral AI
GROQ_API_KEY=...          # Groq (fast inference)
```

**Pro tip:** Start with just `ANTHROPIC_API_KEY`. Add others later as you explore features.

---

## Volume Setup for Persistence

**Critical:** Without a volume, all data is lost on redeploy!

### 1. Create Volume
1. In Railway, click **+ New** → **Volume**
2. Name it something like `openclaw-data`
3. Set **Mount Path:** `/data`

### 2. Verify Mount
After deployment, check the logs for:
```
Volume mounted at /data
```

### What Gets Stored in /data

| Path | Purpose |
|------|---------|
| `/data/workspace` | Your agent's workspace (SOUL.md, memory, etc.) |
| `/data/.openclaw` | OpenClaw config, credentials, browser profiles |
| `/data/.openclaw/openclaw.json` | Main configuration file |
| `/data/.openclaw/credentials` | Telegram pairing, allowlists |
| `/data/.openclaw/memory` | Conversation memory index |

---

## Connecting Telegram

### 1. Create a Bot with BotFather

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow prompts:
   - **Name:** Something like "Molty" or "My Assistant"
   - **Username:** Must end in `bot`, e.g., `my_assistant_bot`
4. **Copy the bot token** — you'll need this!

Example token format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Configure Bot Settings (Recommended)

Still in BotFather:
```
/setprivacy → Disable (so bot can see group messages)
/setjoingroups → Enable (if you want group chat access)
```

### 3. Add Bot Token to OpenClaw

**Option A: Via Control UI (if accessible)**
1. Open Control UI
2. Go to **Channels** → **Telegram**
3. Paste bot token

**Option B: Via Config File**
SSH/terminal into your container:
```bash
# Edit config
nano /data/.openclaw/openclaw.json

# Add under "channels":
"telegram": {
  "botToken": "YOUR_BOT_TOKEN_HERE",
  "allowFrom": []
}
```

### 4. Pair Your Account

1. **Start chat** with your bot on Telegram
2. Send `/pair`
3. You'll receive a pairing code
4. Complete pairing (usually automatic if you're the first user)

### 5. Set Up Allowlist (Security)

After pairing, restrict who can use your bot:

**File:** `/data/.openclaw/credentials/telegram-allowFrom.json`
```json
[
  {
    "type": "user",
    "id": 1234567890,
    "username": "your_telegram_username"
  }
]
```

Find your Telegram ID by:
- Sending any message to your bot (it logs the sender ID)
- Using @userinfobot on Telegram

---

## First Boot & Verification

### 1. Check Deployment Status
In Railway dashboard:
- Build should complete without errors
- Service should show "Running"

### 2. Check Logs
Click on your service → **Logs** tab

Look for:
```
✓ Gateway started
✓ Telegram channel connected
✓ Listening on port 8080
```

### 3. Test the Bot
Send a message to your bot on Telegram:
```
Hello! Can you hear me?
```

Expected: A response within a few seconds.

### 4. Test Core Functions
```
What's the current time?
Read my SOUL.md file
Create a file called test.txt with "Hello World"
```

### 5. Verify Persistence
1. Create a test file via the bot
2. Redeploy the service in Railway
3. Ask the bot to read the file — it should still exist

---

## Control UI Access

OpenClaw includes a web-based Control UI for configuration.

### 1. Expose Port 8080
In Railway:
1. Go to **Settings** → **Networking**
2. Click **Generate Domain** or expose port 8080

### 2. Get Auth Token
From logs or config:
```bash
cat /data/.openclaw/openclaw.json | grep token
```

### 3. Access UI
Visit: `https://your-railway-url.up.railway.app`
Enter the auth token when prompted.

### Security Considerations
The Control UI gives full access to your assistant. Options:
- **VPN only:** Use Tailscale/Cloudflare Tunnel for secure access
- **Strong token:** Generate with `openssl rand -hex 32`
- **IP allowlist:** Configure in Railway if available

---

## Common Issues & Fixes

### Bot Not Responding

**Check 1: Is the service running?**
```
Railway Dashboard → Your Service → Should show "Running"
```

**Check 2: Bot token correct?**
- Verify token in config matches BotFather
- Tokens don't have spaces or extra characters

**Check 3: Are you on the allowlist?**
- Check `/data/.openclaw/credentials/telegram-allowFrom.json`
- Your user ID must match exactly

### "No API Key" Errors

**Symptom:** Bot responds with API key errors

**Fix:** Verify environment variables in Railway:
1. Go to **Variables** tab
2. Ensure `ANTHROPIC_API_KEY` is set
3. Redeploy after changes

### Volume Not Mounting

**Symptom:** Data lost after redeploy

**Check:**
1. Volume exists in Railway
2. Mount path is exactly `/data`
3. Service is linked to the volume

**Fix:** Delete and recreate volume, then restart service.

### Browser/Chromium Errors

**Symptom:** Web browsing fails, Puppeteer errors

**Cause:** Container missing Chromium or wrong flags

**Fix in Dockerfile:**
```dockerfile
RUN apt-get update && apt-get install -y chromium && rm -rf /var/lib/apt/lists/*
```

**Fix in config** (`/data/.openclaw/openclaw.json`):
```json
"browser": {
  "defaultProfile": "openclaw",
  "headless": true,
  "noSandbox": true
}
```

### Config Corruption

**Symptom:** Gateway won't start, JSON parse errors

**Fix:**
```bash
# OpenClaw creates timestamped backups
ls /data/.openclaw/openclaw.json.bak-*

# Restore most recent
cp /data/.openclaw/openclaw.json.bak-TIMESTAMP /data/.openclaw/openclaw.json

# Restart
openclaw gateway restart
```

### Out of Memory

**Symptom:** Container crashes, OOM errors

**Fix:**
1. Increase Railway service memory limit
2. Reduce concurrent subagents in config
3. Set shorter context pruning TTL

### Slow First Response

**Symptom:** First message takes 30+ seconds

**Cause:** Cold start, model loading

**Normal behavior.** Subsequent messages are faster. Consider:
- Increasing Railway min instances (costs more)
- Using a faster model (Haiku) for quick responses

---

## Next Steps

Once your bot is running:

1. 📖 Read [OpenClaw Best Practices](openclaw-best-practices.md) for configuration tips
2. 🔐 Set up `SECURITY.md` for prompt injection defense
3. 🧠 Configure memory system for context across sessions
4. 🛠️ Install skills for additional capabilities
5. 💾 Set up automated backups

---

## Quick Reference

### Key Paths
```
/data/workspace          # Your workspace
/data/.openclaw          # OpenClaw state
/data/.openclaw/openclaw.json  # Main config
```

### Useful Commands
```bash
openclaw gateway status   # Check status
openclaw gateway restart  # Restart after config changes
openclaw help            # See all commands
```

### Emergency Recovery
```bash
# If config is broken
cp /data/.openclaw/openclaw.json.bak-LATEST /data/.openclaw/openclaw.json
openclaw gateway restart

# If Telegram stops working
# Re-pair: send /pair to your bot
```

---

*Guide version: 2026-02-01 | Based on real deployment experience*
