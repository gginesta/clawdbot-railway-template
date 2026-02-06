# Agent Deployment Guide (TMNT Squad)

*Standardized process for deploying new team leads. Learned from Raphael deployment (4h manual → target 30min automated).*

**Created:** 2026-02-05 | **Author:** Molty 🦎

---

## Overview

Every new agent follows the same pattern: Railway container → OpenClaw config → Discord bot → Syncthing → KB transfer → onboarding quiz → go-live.

## Prerequisites (Before Starting)

- [ ] Agent identity defined (name, emoji, theme, project scope)
- [ ] Discord bot application created (Guillermo does this via Discord Developer Portal)
- [ ] Railway project created (fork from `gginesta/clawdbot-railway-template`)

## Phase 1: Infrastructure (15 min)

### 1.1 Railway Deployment
```bash
# Clone template
# Set environment variables:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY (for sub-agents)
# - Gateway token (generate 64-char random)
# Deploy → get URL: https://ggv-{agent}.up.railway.app
```

### 1.2 OpenClaw Config
- Copy base config template (see `/data/workspace/templates/agent-config-template.json`)
- Set: model, fallbacks, channels, heartbeat, subagents
- **Critical settings:** `headless: true`, `noSandbox: true`, `defaultProfile: openclaw`

### 1.3 Discord Bot Setup
- Bot token → config
- Add to TMNT Squad server with correct permissions
- Create/assign channel ownership (update ALL agents' TOOLS.md)
- Set `allowBots: true` for inter-agent visibility
- **Approve Guillermo's Discord pairing:**
  ```bash
  # Guillermo will get a pairing code when he DMs the bot
  # Run this to approve:
  openclaw pairing approve discord <PAIRING_CODE>
  ```
  - Guillermo's Discord user ID: `779143499655151646`
  - This enables DMs and slash commands from Guillermo

## Phase 2: Connectivity (10 min)

### 2.1 Syncthing
- Install Syncthing in container
- Exchange device IDs with existing fleet
- Configure shared folders:
  - `/data/shared/` (sendreceive)
  - Memory vault folders (sendonly from Molty)
  - Shared API skills (sendonly from Molty)

### 2.2 Agent-to-Agent Webhooks
- Configure hooks endpoint with fleet token
- Test webhook both directions:
  ```bash
  curl -X POST https://ggv-{agent}.up.railway.app/hooks/agent \
    -H "Authorization: Bearer $HOOKS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message": "ping", "sessionKey": "agent:main:main", "wakeMode": "now"}'
  ```
- Update agent-link SKILL.md on ALL agents with new endpoint

## Phase 3: Identity & Knowledge (10 min)

### 3.1 Core Files
- `SOUL.md` — personality, role, boundaries
- `AGENTS.md` — operational guidelines
- `USER.md` — about Guillermo
- `TOOLS.md` — channel ownership, credentials, local config
- `IDENTITY.md` — name, creature, vibe, emoji

### 3.2 Knowledge Base Transfer
- Via Syncthing (preferred — auto-syncs)
- Domain-specific KB in `/data/shared/memory-vault/knowledge/projects/{project}/`
- Fleet operational guidelines: `/data/shared/memory-vault/knowledge/squad/OPERATIONAL-GUIDELINES.md`

### 3.3 Sub-Agent Roster (if applicable)
- Define themed sub-agents for the project lead
- Configure sub-agent model (default: `qwen-portal/coder-model`)
- Document roster in agent's TOOLS.md

## Phase 4: Verification (5 min)

### 4.1 Connectivity Tests
- [ ] Webhook ping/pong with Molty
- [ ] Discord channel access (own channels + read others)
- [ ] Syncthing folders synced (`ls /data/shared/`)
- [ ] Can read specific shared file content

### 4.2 Onboarding Quiz (10+ questions)
- Domain knowledge (from KB)
- Operational guidelines (channel ownership, communication protocol)
- Security rules (no secrets in prompts, device auth awareness)
- Coordination protocol (how to relay tasks, update status)

### 4.3 Go-Live Checklist
- [ ] All quiz answers correct
- [ ] First task assigned via Discord
- [ ] Notion project tracker created
- [ ] Todoist coordination flow tested (Molty relays → agent mirrors → completion)
- [ ] Security audit run (healthcheck skill)
- [ ] Backup verified

## Timing

| Phase | Target | Raphael Actual |
|-------|--------|----------------|
| Infrastructure | 15 min | ~90 min |
| Connectivity | 10 min | ~60 min |
| Identity & KB | 10 min | ~45 min |
| Verification | 5 min | ~45 min |
| **Total** | **40 min** | **~4 hours** |

## Agent Roster (Deployed)

| Agent | Project | Theme | URL | Status |
|-------|---------|-------|-----|--------|
| Molty 🦎 | Meta/Coordinator | TMNT | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | Brinc | Super Mario | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | Cerebro (Venture) | TBD | — | Next week |
| Donatello 🟣 | Tinker Labs | TBD | — | Not deployed |
| Michelangelo 🟠 | Mana Capital | TBD | — | Not deployed |
| April 📰 | Personal | TBD | — | Not deployed |

## Lessons Learned

1. **Set up Syncthing BEFORE KB transfer** — files auto-sync once configured
2. **Verify KB access explicitly** — ask agent to `ls` AND `cat` a file
3. **Quiz before "onboarded"** — 10+ questions minimum, require explicit answers
4. **Audit against SOP at the end** — run security healthcheck before declaring complete
5. **Document blockers clearly** — make handoff items explicit (what needs human action)
6. **Bot invites require human action** — generate OAuth URL, human must click it
7. **Channel permissions vs server permissions** — private channels need explicit permission overwrites
8. **`allowBots: true`** — required for agent-to-agent visibility on Discord

---

*This guide should be updated after each deployment to capture new learnings.*
