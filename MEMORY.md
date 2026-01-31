# MEMORY.md - Long-Term Memory

*Created: 2026-01-31 | Last updated: 2026-01-31*

---

## 👤 About Guillermo

- **Location:** Hong Kong (GMT+8)
- **Telegram:** @gginesta (id: 1097408992)
- **Style:** Curious, learns fast, enjoys troubleshooting
- **Technical level:** Not super technical but follows good instructions well
- **Dedication:** Spent 12+ hours getting OpenClaw set up on Day 1!

### Communication Preferences
- Casual + friendly, but efficient and sharp
- No fluff — get to the point
- Appreciates thoroughness when it matters
- Likes tables and structured summaries

---

## 🖥️ System Architecture

### Hosting
- **Platform:** Railway (Docker container)
- **Template:** vignesh07/clawdbot-railway-template (forked to gginesta/)
- **Volume:** `/data` (persistent storage)
- **Public URL:** Via Railway (VPN access from home)

### Key Paths
| Path | Purpose |
|------|---------|
| `/data/workspace` | My workspace (git repo) |
| `/data/.openclaw` | OpenClaw state + config |
| `/data/.openclaw/openclaw.json` | Main config file |
| `/data/.openclaw/credentials/` | Telegram allowlists, pairing |
| `/data/.openclaw/browser/openclaw/` | Chromium profile |
| `/data/.openclaw/memory/main.sqlite` | Memory search index (13MB) |
| `~/.config/git/credentials` | GitHub token |
| `~/.config/last30days/.env` | API keys for last30days skill |

### Browser
- **Binary:** `/usr/bin/chromium` (installed via Dockerfile)
- **Mode:** Headless, no-sandbox (required for Railway containers)
- **Default profile:** `openclaw`
- **User data:** `/data/.openclaw/browser/openclaw/user-data`

---

## 🔑 Credentials & Keys (Configured)

| Service | Location | Status |
|---------|----------|--------|
| Anthropic | OpenClaw auth (token) | ✅ Primary |
| OpenAI | Config env + last30days .env | ✅ |
| OpenAI Codex | OpenClaw auth (OAuth) | ✅ |
| OpenRouter | Config env | ✅ |
| Qwen Portal | OpenClaw auth (OAuth) | ✅ |
| xAI (Grok) | last30days .env | ✅ |
| Brave Search | Config env | ✅ |
| Gemini | Memory search (free tier) | ✅ |
| GitHub | ~/.config/git/credentials | ✅ |
| Telegram Bot | Config (botToken) | ✅ |

---

## 🤖 Model Configuration

### Primary Stack
| Role | Model | Provider |
|------|-------|----------|
| **Primary** | Claude Opus 4.5 | Anthropic |
| **Fallback 1** | Claude Sonnet 4 | Anthropic |
| **Fallback 2** | GPT-5.2 | OpenAI Codex (OAuth) |
| **Fallback 3** | Qwen Coder | Qwen Portal (free) |
| **Images** | Qwen Vision | Qwen Portal (free!) |
| **Subagents** | Qwen Coder | Cheap/fast for background work |

### Available via OpenRouter
- `openrouter/anthropic/claude-sonnet-4`
- `openrouter/google/gemini-2.5-pro-preview` (1M context!)
- `openrouter/openai/gpt-4o`
- `openrouter/meta-llama/llama-3.3-70b-instruct`

### Available via OpenAI Direct
- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `openai/o1` (reasoning)

### Model Aliases
- `qwen` → `qwen-portal/coder-model`

---

## 🛠️ Skills Inventory

### Installed & Ready (11)
| Skill | Source | Notes |
|-------|--------|-------|
| bluebubbles | Bundled | iMessage via BlueBubbles |
| clawhub | Bundled | Skill marketplace CLI |
| skill-creator | Bundled | Create new skills |
| weather | Bundled | Weather lookups |
| email | Clawhub | Email management |
| last30days | Workspace | Reddit/X research tool |
| n8n-workflow-automation | Clawhub | n8n workflow JSON generator |
| notion | Clawhub | Notion API (needs NOTION_API_KEY) |
| task | Clawhub | Task management |
| todo | Clawhub | Todo lists |
| todoist | Clawhub | Todoist integration (needs token) |

### last30days API Status
- ✅ XAI_API_KEY — X/Twitter research
- ✅ OPENAI_API_KEY — Reddit engagement analysis

---

## 💾 Backup System

### Automated Backups
- **Cron:** Every 6 hours
- **Script:** `/data/workspace/backups/backup.sh`
- **Keeps:** Last 5 tarballs locally

### GitHub Backup
- **Repo:** https://github.com/gginesta/moltybackup (private)
- **Remote:** `backup`
- **Push:** `git push backup master`
- **Note:** Tarballs gitignored (too large), sanitized config pushed

### Recovery Guide
- `/data/workspace/backups/RECOVERY.md`

---

## ⚙️ Key Config Settings

| Setting | Value | Why |
|---------|-------|-----|
| `browser.defaultProfile` | `openclaw` | Use headless Chromium, not Chrome extension |
| `browser.headless` | `true` | Required for Railway containers |
| `browser.noSandbox` | `true` | Required for Railway containers |
| `commands.restart` | `true` | Allow /restart command |
| `heartbeat.every` | `1h` | Periodic check-ins |
| `contextPruning.mode` | `cache-ttl` | Prune old context after 1h |
| `subagents.model` | `qwen-portal/coder-model` | Cheap model for background tasks |
| `subagents.maxConcurrent` | `8` | Parallel subagents allowed |
| `gateway.controlUi.dangerouslyDisableDeviceAuth` | `true` | ⚠️ Needed for web access, mitigated by VPN |

---

## 📝 Preferences & Decisions

### Accepted Risks
- **Port 8080 exposed:** Mitigated by VPN + token auth
- **Device auth disabled:** Needed for web UI access

### Rejected
- **Supermemory plugin:** Reviewed 2026-01-31 — code is safe but sends all conversations to third-party cloud. Privacy trade-off not worth it when local memory works fine.

### Style
- **My emoji:** 🦎 (not 🫠 — doesn't render in webchat)
- **Responses:** Casual but efficient, tables for structured data
- **Platform formatting:** No markdown tables for Discord/WhatsApp (use bullets)

---

## 📚 Lessons Learned

### Day 1 (2026-01-31)

1. **Config changes can crash the gateway** — Always back up before major config changes. The "subagent configuration syntax error" took us offline for 7 hours.

2. **Railway containers need special browser flags** — `headless: true` and `noSandbox: true` are required.

3. **Backup configs have timestamps** — `/data/.openclaw/openclaw.json.bak-*` files saved us when config was corrupted.

4. **Skills need OpenClaw-compatible frontmatter** — Claude Code frontmatter (`allowed-tools`, `context`) doesn't work. Use `metadata.clawdbot` format.

5. **Browser profile matters** — Default is "chrome" (extension relay), but we need "openclaw" (headless). Set `browser.defaultProfile`.

6. **Zombie processes happen** — Chromium crashes leave defunct processes. They're cosmetic and clear on redeploy.

7. **Git remote URLs shouldn't contain tokens** — Store tokens in credential files with proper permissions (600).

---

## 🔧 Quick Reference

### Useful Commands
```bash
# Push to GitHub backup
cd /data/workspace && git push backup master

# Run manual backup
/data/workspace/backups/backup.sh

# Check gateway status
openclaw status

# Restart gateway
openclaw gateway restart
```

### Config Paths
```bash
# Main config
/data/.openclaw/openclaw.json

# Backup configs (timestamped)
/data/.openclaw/openclaw.json.bak-*

# Telegram credentials
/data/.openclaw/credentials/telegram-allowFrom.json
```

---

*This file is my curated long-term memory. Daily logs go in `memory/YYYY-MM-DD.md`.*
