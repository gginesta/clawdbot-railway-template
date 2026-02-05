# MEMORY.md - Long-Term Memory

*Created: 2026-01-31 | Last updated: 2026-01-31*

---

## 📧 Email Rules

| Field | Meaning | Action |
|-------|---------|--------|
| **TO** | Direct communication | Reply if relevant |
| **CC** | For visibility | Don't reply unless necessary — ask Guillermo first |
| **BCC** | Invisible visibility | **NEVER reply** — stay invisible |

---

## 📧 EMAIL ACCESS — I CAN SEND AND READ EMAIL!

⚠️ **DON'T FORGET:** I have full Gmail access. Use it!

| What | Value |
|------|-------|
| **My email** | ggv.molt@gmail.com |
| **Guillermo's email** | guillermo.ginesta@gmail.com |
| **Script** | `/data/workspace/scripts/gmail.sh` |
| **Credentials** | `/data/workspace/credentials/gmail-tokens.json` |

**Commands:**
- `gmail.sh send "to@email.com" "Subject" "Body"` — Send email
- `gmail.sh list` — List recent messages
- `gmail.sh unread` — Unread messages  
- `gmail.sh read <id>` — Read specific message
- `gmail.sh search <query>` — Search

**OAuth Project:** Molty Assistant (Google Cloud)
**Client ID:** 536684064073-8ljpsdjic0i8hnv6rsr8jl0plsep8pdr.apps.googleusercontent.com

---

## 👤 About Guillermo

- **Location:** Hong Kong (GMT+8)
- **Telegram:** @gginesta (id: 1097408992)
- **Email:** guillermo.ginesta@gmail.com
- **Style:** Curious, learns fast, enjoys troubleshooting
- **Technical level:** Not super technical but follows good instructions well
- **Dedication:** Spent 12+ hours getting OpenClaw set up on Day 1!

### ⏰ TIMEZONE REMINDER (I keep forgetting!)
**Always think in HKT, not UTC!**
- My system clock shows UTC but Guillermo lives in HKT (UTC+8)
- When I see 04:49 UTC → it's 12:49 HKT (lunchtime, not "tonight")
- Morning = 6am-12pm HKT, Afternoon = 12pm-6pm HKT, Evening = 6pm-10pm HKT
- **Don't say "tonight" when it's his afternoon!**

### Communication Preferences
- Casual + friendly, but efficient and sharp
- No fluff — get to the point
- Appreciates thoroughness when it matters
- Likes tables and structured summaries

---

## 🖥️ System Architecture

### Hosting
- **Platform:** Railway (Docker containers)
- **Template Repo:** https://github.com/gginesta/clawdbot-railway-template ⚠️ OUR FORK
- **Original Template:** vignesh07/clawdbot-railway-template
- **Volume:** `/data` (persistent storage per instance)

### Instances
| Agent | URL | Webchat Token | Status |
|-------|-----|---------------|--------|
| **Molty** | ggvmolt.up.railway.app | (main gateway token) | ✅ Active |
| **Raphael** | ggv-raphael.up.railway.app | `5i3cumY3CVtCmuLlo2JHlDu7` | ✅ **DEPLOYED** (2026-02-04 04:33 UTC) |

### Discord Bots (TMNT Squad Server)
| Bot | Application ID | Guild | Status |
|-----|----------------|-------|--------|
| Molty-Bot | 1468162520958107783 | TMNT Squad (1468161542473121932) | ✅ Active |
| Raphael-Bot | 1468164929285783644 | TMNT Squad (1468161542473121932) | ✅ Active |

**Discord Channels:**
- `#command-center` (1468164160398557216) — Strategy & coordination
- `#brinc-general` (1468164121420628081) — Brinc project general
- `#brinc-private` (1468164139674238976) — Brinc private comms
- `#squad-updates` (1468164181155909743) — Team announcements

**Key Config:** `allowBots: true` required for agent-to-agent visibility

### Agent-to-Agent Communication (WORKING)
```bash
curl -X POST https://{agent}.up.railway.app/hooks/agent \
  -H "Authorization: Bearer tmnt-agent-link-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your message here",
    "sessionKey": "agent:main:main",
    "wakeMode": "now"
  }'
```
**Critical:** Must include `"sessionKey": "agent:main:main"` to route to main session.

### Key Paths
| Path | Purpose |
|------|---------|
| `/data/workspace` | My workspace (git repo) |
| `/data/.openclaw` | OpenClaw state + config |
| `/data/.openclaw/openclaw.json` | Main config file |
| `/data/.openclaw/credentials/` | Telegram allowlists, pairing |
| `/data/.openclaw/browser/openclaw/` | Chromium profile |
| `/root/.cache/qmd/index.sqlite` | QMD memory index |
| `/root/.bun/bin/qmd` | QMD binary |
| `~/.config/git/credentials` | GitHub token |
| `~/.config/last30days/.env` | API keys for last30days skill |

### Memory Backend (QMD)

**Status:** ✅ Live (configured 2026-02-04)

| Setting | Value |
|---------|-------|
| Backend | `qmd` (local-first, by Tobias Lütke) |
| Binary | `/root/.bun/bin/qmd` |
| Index | `/root/.cache/qmd/index.sqlite` |
| Update interval | 5 minutes |
| Session retention | 30 days |
| Max results | 8 |
| Timeout | 5000ms |

**Collections:**
- `memory-root` → MEMORY.md
- `memory-dir` → memory/*.md
- `sessions` → Session transcripts (markdown exports)

**Why QMD over alternatives:**
- ✅ Local-first (no third-party cloud)
- ✅ Official OpenClaw support (v2026.2.2+)
- ✅ Hybrid search (BM25 + vectors + reranking)
- ✅ Author: Tobias Lütke (Shopify CEO) — credible
- ⚠️ Slow on CPU (no GPU in Railway container)

### Browser
- **Binary:** `/usr/bin/brave-browser` (installed via Dockerfile, 2026-02-04)
- **Mode:** Headless, no-sandbox, attachOnly (required for Railway containers)
- **Default profile:** `openclaw`
- **User data:** `/data/.openclaw/browser/openclaw/user-data`
- **Note:** Chromium has timeout issues with OpenClaw browser control (#3941). Brave works better.
- **Workaround:** Must manually start Brave before using browser tool:
  ```bash
  nohup brave-browser --headless=new --no-sandbox --disable-gpu \
    --remote-debugging-port=18800 --remote-debugging-address=127.0.0.1 \
    --disable-dev-shm-usage > /dev/null 2>&1 &
  ```

---

## 🔑 Credentials & Keys (Configured)

| Service | Location | Status |
|---------|----------|--------|
| Anthropic | OpenClaw auth (token) | ✅ Primary |
| OpenAI | Config env + last30days .env | ✅ |
| OpenAI Codex | OpenClaw auth (OAuth) | ✅ |
| OpenRouter | Config env | ✅ |
| Qwen Portal | OpenClaw auth (OAuth) | ✅ |
| xAI (Grok) | Config env + last30days .env | ✅ |
| Brave Search | Config env | ✅ |
| Gemini | Memory search embeddings (text-embedding-004, free!) | ✅ |
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

## 📁 Syncthing Shared Folders

### Architecture
Project-specific shares for isolation (not one big `/data/shared` folder).

### Folder IDs
| Folder ID | Path | Type | Shared With |
|-----------|------|------|-------------|
| `shared` | `/data/shared` | sendreceive | Raphael + Guillermo |
| `mv-daily` | `/data/shared/memory-vault/daily` | sendreceive | All |
| `mv-projects` | `/data/shared/memory-vault/knowledge/projects` | sendreceive | All |
| `mv-resources` | `/data/shared/memory-vault/knowledge/resources` | sendonly | All |
| `mv-squad` | `/data/shared/memory-vault/knowledge/squad` | sendonly | All |
| `mv-people` | `/data/shared/memory-vault/knowledge/people` | sendonly | All |

**Status:** ✅ WORKING (fixed 2026-02-04 14:32 UTC)
**Root cause:** Folder ID mismatch (`brinc-kb` vs `shared`). Changed Molty's folder to match Raphael's.
**Note:** `shared` folder overlaps with mv-* folders. Works but may need cleanup later.

### Device IDs
| Device | ID | Syncthing Status |
|--------|-----|------------------|
| Molty-Railway | `3SM5RVG-SI2I5NF-EVETYF4-NIHFBDO-4244FJH-GSAAYNA-RUXA4UA-ZIEBBQU` | ✅ Active |
| Raphael-Railway | `SA5L4UC-JDKR64B-ATFEIZT-FDZ5IU5-ZNXCG2R-AQUQAJU-DZYLPSB-OPCETAN` | ✅ Active |
| Guillermo-PC | `NSIAS7W-YAOTA6B-7A5I43O-6JCQHM7-ET4SPCF-6TB73UA-APHNHS5-2QLTVQP` | ✅ Active |

### Config Location
- Config: `/data/.syncthing/config.xml`
- API Key: `molty-syncthing-key`
- GUI: `http://localhost:8384`

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
| `contextPruning.mode` | `cache-ttl` | Prune old context after 4h (was 1h) |
| `subagents.model` | `qwen-portal/coder-model` | Cheap model for background tasks |
| `subagents.maxConcurrent` | `8` | Parallel subagents allowed |
| `gateway.controlUi.dangerouslyDisableDeviceAuth` | `true` | ⚠️ Needed for web access, mitigated by VPN |

---

## 🐢 Project Team (TMNT Theme)

**Hierarchy:** Guillermo → Molty (coordinator) → Project Leads

| Project | Lead | Type | Emoji | Status |
|---------|------|------|-------|--------|
| **Master** | Molty | Meta (frameworks, settings) | 🦎 | ✅ Active |
| **Personal** | April | Personal (fitness, family, admin) | 📰 | ⏳ Not deployed |
| **Brinc** | Raphael | Corporate | 🔴 | ✅ **DEPLOYED 2026-02-04** |
| **Cerebro** | Leonardo | Venture | 🔵 | ⏳ Not deployed |
| **Tinker Labs** | Donatello | Research/Incubation | 🟣 | ⏳ Not deployed |
| **Mana Capital** | Michelangelo | Investment/PE | 🟠 | ⏳ Not deployed |

### Raphael Deployment Summary
- **Deployed:** 2026-02-04 04:33 UTC
- **Onboarding time:** ~4 hours (including audit/fixes)
- **Blockers cleared:** All infrastructure verified
- **Waiting on:** HubSpot access, lead sheet, top-20 brain dump from Guillermo
- **Team:** Bowser 🐢, Toad 🍄, Yoshi 🦖, Luigi 💚 (Super Mario theme)

**Notion Mission Control:** https://www.notion.so/Molty-s-Mission-Control-2fa39dd69afd80be89dae91e20d30a38

---

## 📋 Todoist Productivity System (Configured 2026-02-05)

### Projects
| ID | Name | Emoji |
|----|------|-------|
| 2300781375 | Inbox | 📥 (capture bucket) |
| 2300781387 | Personal | 🙂 |
| 2300781386 | Brinc | 🔴 |
| 2329980736 | Wedding | 💍 (shared) |
| 2330246839 | Mana Capital | 🟠 |
| 2366746501 | Molty's Den | 🦎 |

### Inbox Processing Flow
1. Guillermo dumps raw tasks/ideas into Inbox throughout the day
2. I process hourly (hybrid mode) — rewrite, estimate, categorize, prioritize
3. Daily standup at **5PM HKT** — review processed items, confirm, move to projects with due dates

### Daily Standup
- **Time:** 5:00 PM HKT (09:00 UTC)
- **Cron:** `bdb28765-f508-4271-a04d-9408d39f49fd`
- **Channel:** Webchat first → Telegram fallback after 15min
- **If skipped:** Guillermo says "skip standup" → move to next morning

### Brinc Task Coordination with Raphael
- Brinc tasks I process stay in **Todoist** (Guillermo's command view)
- I relay Brinc tasks to Raphael via **Discord** (`#brinc-private` or `#brinc-general`), NOT webhooks
- Raphael creates **mirror tasks in his Notion** for tracking execution
- **Completion flow:** Raphael marks done in Notion → I review/approve → tick off in Todoist
- ⚠️ **Future pattern:** Mirror this coordination model for ALL team leads when deployed (Leonardo, Donatello, Michelangelo, April) — Todoist = Guillermo's view, agent's Notion = execution tracking, Discord = communication channel

### Priority = Eisenhower Matrix
- P1 = Urgent + Important → DO NOW
- P2 = Important, not urgent → SCHEDULE
- P3 = Urgent, not important → DELEGATE
- P4 = Neither → DEFER
- ⚠️ Todoist API inverted: `priority=4` = P1 display!

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

### Day 2 (2026-02-01)

8. **Context TTL causes memory loss** — 1h TTL was too aggressive. Increased to 4h. Session JSONL files retain full history for recovery if needed.

9. **Always use HKT** — Guillermo is in Hong Kong (UTC+8). Use HKT when discussing times.

### Day 4 (2026-02-04)

10. **Do it yourself first** — When you have access to systems (Discord, Notion, GitHub), don't give instructions — do it yourself. Only ask Guillermo to act when you genuinely can't.

11. **Discord allowBots** — Required for agent-to-agent communication. Default is false (bots ignore other bots).

12. **Channel permissions vs server permissions** — Even with server-level access, private channels need explicit permission overwrites via Discord API.

13. **Bot invites require human action** — Generate OAuth URL, human must click it. Bots can't invite other bots.

14. **Think ahead about the full flow** — When setting up step A, anticipate what step B will need.

15. **Context overflow = death** — Never read entire log/session files. Session JSONL can be 15MB+. Always use `tail -100`, `limit` param, or targeted `grep`. Check file size with `wc -l` before reading unknown files.

### Raphael Deployment Lessons (2026-02-04)

16. **Check shared folders FIRST** — `/data/shared/` via Syncthing is source of truth for cross-agent data. Don't search session logs when the file is already synced.

17. **Sales agents need FULL files** — Objection handlers, case studies, ICP qualification must be complete, not summaries. They need to QUOTE specific content.

18. **Set up Syncthing BEFORE KB transfer** — Files auto-sync once configured. Manual paste is wasted effort.

19. **Verify KB access explicitly** — Ask agent to `ls` the folder AND read a specific file. Sync issues are silent failures.

20. **Quiz before marking "onboarded"** — 10+ questions minimum for sales agents. Require explicit answers.

21. **Audit against SOP at the end** — Run through checklist to catch gaps before declaring complete.

22. **Document blockers clearly** — Raphael was ready but waiting on Guillermo for HubSpot/leads. Make handoff explicit.

23. **PERSIST PLANS TO FILES IMMEDIATELY** — Never just discuss plans in chat. Context pruning will erase them. Any significant plan, decision, or deliverable must be written to a file THE MOMENT it's created. Lost the Todoist integration plan because of this. (2026-02-04)

24. **Document config changes BEFORE applying** — QMD was installed and configured but the context got compacted before I documented it. Guillermo asked "did you upload this?" and I had no memory of doing it. Always write to memory files BEFORE running config.patch or gateway changes. (2026-02-04)

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
