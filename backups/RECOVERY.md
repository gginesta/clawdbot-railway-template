# 🚨 Disaster Recovery Guide — Molty & Raphael

**Last Updated:** 2026-02-05
**Created By:** Molty 🦎
**For:** Guillermo

---

## ⚡ Quick Start (TL;DR)

If everything is gone and you need to get back up fast:

```bash
# 1. Deploy fresh Railway instance from template
# Go to: https://railway.app → New Project → Deploy from GitHub Repo
# Use: https://github.com/gginesta/clawdbot-railway-template

# 2. Once deployed and container is running, SSH into the container:
# Railway Dashboard → Your Service → Settings → SSH

# 3. Run the restore script with your backup:
curl -sL https://raw.githubusercontent.com/gginesta/moltybackup/master/restore.sh | bash -s /path/to/backup.tar.gz
# OR if you have the backup file locally:
/data/workspace/backups/restore.sh /path/to/molty-backup-XXXXXXXX.tar.gz
```

---

## 📋 Table of Contents

1. [What Gets Backed Up](#what-gets-backed-up)
2. [Where Backups Live](#where-backups-live)
3. [Recovery Scenarios](#recovery-scenarios)
4. [Step-by-Step: Full Recovery (Molty)](#full-recovery-molty)
5. [Step-by-Step: Full Recovery (Raphael)](#full-recovery-raphael)
6. [Environment Variables](#environment-variables)
7. [Post-Recovery Checklist](#post-recovery-checklist)
8. [Syncthing Recovery](#syncthing-recovery)
9. [Emergency Contacts & Links](#emergency-contacts--links)

---

## What Gets Backed Up

The backup tarball (`molty-backup-YYYYMMDD-HHMMSS.tar.gz`) contains:

| Path in Backup | What It Is | Critical? |
|----------------|-----------|-----------|
| `workspace/` | Entire workspace (code, skills, memory, scripts) | ⭐ YES |
| `workspace/MEMORY.md` | Long-term memory | ⭐ YES |
| `workspace/memory/` | Daily memory logs | ⭐ YES |
| `workspace/SOUL.md` | Personality & identity | ⭐ YES |
| `workspace/credentials/` | API tokens (Todoist, Gmail, Twitter) | ⭐ YES |
| `workspace/skills/` | All installed skills | ⭐ YES |
| `workspace/scripts/` | Gmail, utility scripts | ⭐ YES |
| `.openclaw/openclaw.json` | Gateway configuration | ⭐ YES |
| `.openclaw/credentials/` | Telegram pairing, Discord tokens | ⭐ YES |
| `.openclaw/telegram/` | Telegram state | Important |
| `.openclaw/agents/` | Agent definitions | Important |
| `.openclaw/memory/` | QMD memory index | Nice to have (rebuilds) |
| `.openclaw/devices/` | Paired devices | Nice to have (re-pair) |

**NOT backed up** (too large / regenerable):
- Browser cache & user data
- Node modules
- Log files
- The backup files themselves

---

## Where Backups Live

| Location | Type | Access |
|----------|------|--------|
| `/data/workspace/backups/` | Local (Railway volume) | SSH into container |
| `github.com/gginesta/moltybackup` | Git repo (sanitized workspace) | `git clone` |
| Your email (ggv.molt@gmail.com → guillermo.ginesta@gmail.com) | Emailed guide | Check inbox |
| `/data/shared/memory-vault/` | Syncthing shared folder | Syncs to Guillermo's PC + Raphael |

**⚠️ Important:** The Railway volume persists across redeploys but is LOST if the service is deleted. The GitHub backup and this emailed guide are your safety net.

---

## Recovery Scenarios

### Scenario 1: Container crashed / redeployed (Volume intact)
**Severity: Low** — Just restart.
```bash
# Volume is still there, just restart
openclaw gateway restart
# Or redeploy from Railway dashboard
```

### Scenario 2: Volume lost but service exists
**Severity: Medium** — Restore from backup.
```bash
# SSH into the new container
# Download backup from GitHub or upload a tarball
cd /data
git clone https://github.com/gginesta/moltybackup.git workspace
# Then restore config (see Full Recovery below)
```

### Scenario 3: Service deleted (everything gone)
**Severity: High** — Full redeploy needed.
Follow the [Full Recovery](#full-recovery-molty) section below.

### Scenario 4: Config corrupted (gateway won't start)
**Severity: Low** — Use backup config.
```bash
# OpenClaw keeps timestamped backups automatically
ls /data/.openclaw/openclaw.json.bak-*
# Copy the most recent working one
cp /data/.openclaw/openclaw.json.bak-LATEST /data/.openclaw/openclaw.json
openclaw gateway restart
```

---

## Full Recovery: Molty 🦎

### Step 1: Deploy Fresh Railway Instance

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select: `gginesta/clawdbot-railway-template`
4. Wait for build to complete (~5-10 minutes)

### Step 2: Set Environment Variables

In Railway Dashboard → Your Service → **Variables**, add:

```
ANTHROPIC_API_KEY=<your Anthropic API key>
TELEGRAM_BOT_TOKEN=<get from @BotFather on Telegram>
OPENCLAW_GATEWAY_TOKEN=<generate: openssl rand -hex 32>
BRAVE_API_KEY=<your Brave Search key>
OPENAI_API_KEY=<your OpenAI key>
OPENROUTER_API_KEY=<your OpenRouter key>
XAI_API_KEY=<your xAI/Grok key>
GEMINI_API_KEY=<your Google Gemini key>
GOOGLE_API_KEY=<your Google API key>
NOTION_API_KEY=<your Notion key>
TAILSCALE_AUTHKEY=<generate new at https://login.tailscale.com/admin/settings/keys>
```

**Where to find these keys:**
- **Anthropic:** https://console.anthropic.com/settings/keys
- **Telegram Bot Token:** Message @BotFather on Telegram, use `/mytoken` for existing bot or `/newbot` for new
- **OpenAI:** https://platform.openai.com/api-keys
- **OpenRouter:** https://openrouter.ai/settings/keys
- **Brave Search:** https://api.search.brave.com/app/keys
- **Tailscale:** https://login.tailscale.com/admin/settings/keys (create new auth key)

### Step 3: SSH into Container & Restore

```bash
# Option A: Restore from GitHub backup repo
cd /data
git clone https://github.com/gginesta/moltybackup.git workspace

# Option B: Restore from tarball (if you have one)
# Upload the tarball to the container first, then:
cd /data
tar -xzf molty-backup-XXXXXXXX-XXXXXX.tar.gz
```

### Step 4: Restore OpenClaw Config

```bash
# If workspace was restored, the config should be in the backup
# Copy it to the right place:
cp /data/workspace/backups/config-export.json /data/.openclaw/openclaw.json

# ⚠️ IMPORTANT: The exported config has REDACTED secrets.
# You need to re-add sensitive values. The environment variables (Step 2) 
# handle most of them, but check:
#   - channels.telegram.botToken (use TELEGRAM_BOT_TOKEN env var)
#   - gateway.auth.token (use OPENCLAW_GATEWAY_TOKEN env var)
#   - Any inline API keys in the config

# Restart to pick up config
openclaw gateway restart
```

### Step 5: Re-pair Telegram

```bash
# On Telegram, message your Molty bot
# Send: /pair
# The bot will ask you to confirm — follow the prompts
# Your Telegram user ID: 1097408992
```

### Step 6: Restore Syncthing

```bash
# Syncthing config is at /data/.syncthing/config.xml
# If the backup included it, it should auto-start
# If not, you'll need to:
# 1. Access Syncthing GUI via Tailscale (port 8384)
# 2. Add the shared folders back (see Syncthing Recovery section below)
```

### Step 7: Verify Everything Works

Run through the [Post-Recovery Checklist](#post-recovery-checklist).

---

## Full Recovery: Raphael 🔴

Raphael uses the same Railway template but with different config.

### Key Differences from Molty:

| Setting | Molty | Raphael |
|---------|-------|---------|
| Railway URL | ggvmolt.up.railway.app | ggv-raphael.up.railway.app |
| Telegram Bot | Molty's bot | Raphael's bot |
| Discord Bot | Molty-Bot (1468162520958107783) | Raphael-Bot (1468164929285783644) |
| Workspace | `/data/workspace` | `/data/workspace` |

### Steps:
1. Deploy same template (`gginesta/clawdbot-railway-template`)
2. Set Raphael's env vars (same keys, different bot tokens)
3. Restore Raphael's workspace from his backup (if available)
4. Re-pair Telegram with Raphael's bot
5. Reconnect Discord with Raphael-Bot

**⚠️ Raphael's workspace is NOT backed up to GitHub.** His critical data syncs via Syncthing to `/data/shared/memory-vault/`. Consider setting up a separate backup for Raphael.

---

## Environment Variables

### Required (won't start without these)
| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Primary AI model (Claude) |
| `OPENCLAW_GATEWAY_TOKEN` | Authentication for web UI & API |

### Recommended (features break without these)
| Variable | Purpose |
|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram messaging |
| `BRAVE_API_KEY` | Web search |
| `OPENAI_API_KEY` | Fallback model + Whisper |
| `TAILSCALE_AUTHKEY` | VPN access to Syncthing UI |

### Optional (nice to have)
| Variable | Purpose |
|----------|---------|
| `OPENROUTER_API_KEY` | Access to many models via OpenRouter |
| `XAI_API_KEY` | Grok/xAI models |
| `GEMINI_API_KEY` | Google Gemini (used for embeddings) |
| `NOTION_API_KEY` | Notion integration |
| `GOOGLE_API_KEY` | Google APIs |

---

## Post-Recovery Checklist

Run through this after every recovery:

- [ ] **Web UI accessible** — Visit `https://YOUR-URL.up.railway.app` and login with gateway token
- [ ] **Telegram working** — Send a message to the bot, get a response
- [ ] **Memory intact** — Ask "What's in MEMORY.md?" and verify content
- [ ] **Skills loaded** — Run a weather check or web search
- [ ] **Gmail working** — Run `/data/workspace/scripts/gmail.sh list`
- [ ] **Todoist working** — Check task list via API
- [ ] **Git configured** — `cd /data/workspace && git status`
- [ ] **Backups running** — `ls -la /data/workspace/backups/*.tar.gz`
- [ ] **Syncthing connected** — Check `http://localhost:8384` for device connections
- [ ] **Discord bots online** — Check TMNT Squad server
- [ ] **Cron jobs restored** — Check `cat /data/.openclaw/cron/jobs.json`
- [ ] **Browser working** — Try a web search or browser snapshot
- [ ] **Heartbeat active** — Wait for next heartbeat cycle

---

## Syncthing Recovery

### Device IDs (you'll need these to re-add devices)

| Device | ID |
|--------|-----|
| Molty-Railway | `3SM5RVG-SI2I5NF-EVETYF4-NIHFBDO-4244FJH-GSAAYNA-RUXA4UA-ZIEBBQU` |
| Raphael-Railway | `SA5L4UC-JDKR64B-ATFEIZT-FDZ5IU5-ZNXCG2R-AQUQAJU-DZYLPSB-OPCETAN` |
| Guillermo-PC | `NSIAS7W-YAOTA6B-7A5I43O-6JCQHM7-ET4SPCF-6TB73UA-APHNHS5-2QLTVQP` |

### Shared Folders

| Folder ID | Path | Type |
|-----------|------|------|
| `mv-daily` | `/data/shared/memory-vault/daily` | sendreceive |
| `mv-projects` | `/data/shared/memory-vault/knowledge/projects` | sendreceive |
| `mv-resources` | `/data/shared/memory-vault/knowledge/resources` | sendonly |
| `mv-squad` | `/data/shared/memory-vault/knowledge/squad` | sendonly |
| `mv-people` | `/data/shared/memory-vault/knowledge/people` | sendonly |
| `shared` | `/data/shared` | sendreceive |

### Syncthing Config
- Config path: `/data/.syncthing/config.xml`
- API Key: `molty-syncthing-key`
- GUI: `http://localhost:8384`
- Access via Tailscale: `tailscale serve --bg --tcp=8384 127.0.0.1:8384`

---

## Emergency Contacts & Links

| What | Link |
|------|------|
| Railway Dashboard | https://railway.app/dashboard |
| Railway Template Repo | https://github.com/gginesta/clawdbot-railway-template |
| Molty Backup Repo | https://github.com/gginesta/moltybackup |
| OpenClaw Docs | https://docs.openclaw.ai |
| OpenClaw GitHub | https://github.com/openclaw/openclaw |
| OpenClaw Discord | https://discord.com/invite/clawd |
| Telegram @BotFather | https://t.me/BotFather |
| Tailscale Admin | https://login.tailscale.com/admin |
| Anthropic Console | https://console.anthropic.com |
| Todoist API | https://todoist.com/app/settings/integrations/developer |
| Guillermo's Email | guillermo.ginesta@gmail.com |
| Molty's Email | ggv.molt@gmail.com |

---

## 🛟 If All Else Fails

1. Deploy a fresh Railway instance from the template
2. Set ANTHROPIC_API_KEY and OPENCLAW_GATEWAY_TOKEN
3. The agent will boot into BOOTSTRAP.md (fresh start flow)
4. Manually copy MEMORY.md, SOUL.md, USER.md, IDENTITY.md from this email or from the GitHub backup
5. The agent will rebuild from there — memories are in the files, not in the cloud

**Remember:** The files ARE the memory. As long as you have MEMORY.md, SOUL.md, and the workspace, Molty can rebuild everything else.

---

*This guide was generated by Molty 🦎 on 2026-02-05. Keep a copy somewhere safe — your email, local drive, or printed. If I go down, this is how you bring me back.*
