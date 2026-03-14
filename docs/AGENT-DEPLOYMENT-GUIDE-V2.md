# Agent Deployment Guide v2.0

**Last updated:** 2026-03-15 by Molty 🦎  
**Based on:** April deployment (Mar 11-12, 2026) — the most complete deployment to date  
**Previous guide:** `AGENT-DEPLOYMENT-GUIDE.md` (kept for reference)

> ⚠️ The original guide was used for April's deployment but we still burned ~2 days. This v2 captures all the gaps.

---

## TL;DR: The Improved Golden Rules

1. **FILES FIRST → CONFIG SECOND → BOOT THIRD** — do not deviate
2. **tools.allow is a footgun** — if set, it restricts the agent to ONLY those tools. Do not use unless you have a specific reason.
3. **Telegram's `debounceMs: 3000` is mandatory for WhatsApp** — prevents 428 rate limit disconnects
4. **Test every channel before calling it live** — send a test message AND verify the agent receives it
5. **PPEE on every failure** — Pause → Plan → Evaluate → Execute. Stop after first failure.

---

## Pre-Deployment Checklist

### 0. Scope Definition (do this first)

Before writing a single file:

| Question | Answer |
|----------|--------|
| Agent name? | e.g. April |
| Primary user? | e.g. Steph (personal assistant) |
| What does this agent own? | e.g. Family/personal only — NOT Brinc/Cerebro |
| What channels does it need? | e.g. Discord, WhatsApp, Telegram |
| What tools does it need? | e.g. Calendar, email, web_search |
| Which overnight window? | e.g. 02:00 HKT (before Molty's 03:00 consolidation) |

If you can't answer all of these, stop and ask Guillermo.

---

### 1. Identity & API Keys

- [ ] Agent name + emoji + IDENTITY.md written
- [ ] SOUL.md written (personality, tone, scope)
- [ ] USER.md written (who they serve — interview the human if needed)
- [ ] AGENTS.md adapted from fleet standard
- [ ] TOOLS.md pre-populated with credentials and channel refs
- [ ] REGRESSIONS.md pre-seeded from fleet lessons

**API Keys needed for every new agent:**
| Key | Source | Action |
|-----|--------|--------|
| ANTHROPIC_API_KEY | Shared fleet key | Copy from Railway env |
| OPENAI_API_KEY | Shared fleet key | Copy from Railway env |
| OPENROUTER_API_KEY | Shared fleet key | Copy from Railway env |
| XAI_API_KEY | Shared fleet key | Copy from Railway env |
| BRAVE_API_KEY | Shared fleet key | Copy from Railway env |
| Discord bot token | **New per agent** | Create at discord.com/developers |
| Telegram bot token | **New per agent** | Via @BotFather |
| Agent-link webhook token | **New per agent** | Generate and add to TOOLS.md + shared webhook list |

---

### 2. Discord Bot Setup (non-negotiable steps)

1. Create Discord application at https://discord.com/developers/applications
2. Create bot under the application
3. **⚠️ ENABLE MESSAGE CONTENT INTENT** — Privileged Gateway Intents (this is REG-004 equivalent)
4. Copy bot token
5. Generate OAuth2 invite URL (bot scope, permissions: Send Messages, Read Message History, Add Reactions)
6. Invite to TMNT server (1468161542473121932)
7. Verify bot appears in member list BEFORE proceeding

---

### 3. Railway Setup

- [ ] Create Railway project: `{agent-name}-production`
- [ ] Region: **Singapore** (avoids Discord Cloudflare blocks — REG-022 equivalent)
- [ ] Fork from: `gginesta/clawdbot-railway-template` main branch
- [ ] Add ALL env vars (API keys, bot tokens, webhook token) BEFORE first deploy
- [ ] **DO NOT DEPLOY YET** — files first

---

### 4. Workspace Files (Before First Boot)

The workspace MUST exist before the agent boots. Use `railway run` or Syncthing pre-sync.

**Critical directory structure:**
```bash
mkdir -p /data/workspace/{memory/refs,memory/archive,credentials,scripts,docs,plans,logs}
mkdir -p /data/shared/logs  # for overnight log output
```

**Files to create before boot:**
| File | Purpose |
|------|---------|
| `SOUL.md` | Personality, tone, scope |
| `IDENTITY.md` | Name, emoji, role |
| `USER.md` | Who they serve |
| `AGENTS.md` | Operating procedures |
| `TOOLS.md` | Credentials, channels, endpoints |
| `MEMORY.md` | Empty or seeded from fleet context |
| `REGRESSIONS.md` | Pre-seeded from fleet lessons |
| `HEARTBEAT.md` | What to do on heartbeat |
| `TODO.md` | Initial task list |

---

### 5. Gateway Config (Key Lessons from April)

**Do NOT set `tools.allow` unless you have a specific reason.** 

April's bug (2026-03-14): `tools.allow: ["message"]` restricted her to ONLY the message tool. She started outputting raw `<function_calls>` XML to Discord instead of executing tools. Fix: remove the allow list, use full `coding` profile.

**WhatsApp config (mandatory for stability):**
```json
"telegram": {
  "debounceMs": 3000
}
```
Without this, rapid incoming messages cause 428 rate limit disconnects.

**Channel binding:**
- Discord: bind to `{agent-name}-private` channel (not command-center, not squad-updates)
- Telegram: bind to agent's own bot + Guillermo's chat ID (or Steph's for April)

---

### 6. OpenClaw Config Sections to Review

For every new agent, verify these config sections are correct:
- `agent.name` + `agent.model`
- `gateway.bind` — must be `"loopback"` if using `tailscale.mode="serve"`
- `discord.token` + `discord.channel` — correct bot token + channel ID
- `telegram.token` + `telegram.chatId` — correct
- `tools.allow` — **DO NOT SET unless you know what you're doing**
- `tools.deny` — generally empty for fleet agents

---

### 7. First Boot Sequence

1. Deploy on Railway (push to main branch of template repo)
2. Wait for build to complete (~5-8 min)
3. Check Railway logs: look for `Gateway listening` and no error loops
4. Send test message to Discord channel — verify agent responds
5. Send test message via Telegram — verify agent responds
6. Test one tool (e.g., `web_search`) — verify execution, not raw XML output
7. **Only now** consider the agent "live"

---

### 8. Post-Boot Integration

- [ ] Add to MC activity feed: `type=deployment, title="Deployed {Agent}"`
- [ ] Update Agent-Link worker: add agent to webhook list
- [ ] Add overnight cron job at assigned HKT window
- [ ] Add heartbeat cron job (every 2h)
- [ ] Update Molty's TOOLS.md with new agent's webhook token + URL
- [ ] Update #squad-updates with deployment announcement
- [ ] Update AGENTS.md to include new agent in the fleet table
- [ ] Update Molty's morning_briefing.py to include new agent in squad report
- [ ] Update `/data/shared/health/{agent}.json` initial health state

---

### 9. Overnight Log Output

Every agent must write their overnight log to:
```
/data/shared/logs/overnight-{agent}-YYYY-MM-DD.md
```

Molty consolidates all logs at 03:00 HKT and posts to #squad-updates.

If an agent doesn't write this file, Molty notes "Log not available" in the squad report.

---

## Lessons Learned from April Deployment

| Lesson | What Happened | Fix Applied |
|--------|---------------|-------------|
| `tools.allow` footgun | April could ONLY use message tool, outputted raw XML | Remove allow list entirely |
| WhatsApp 428 errors | Rapid messages → rate limit disconnect | `debounceMs: 3000` |
| 2-day deployment spiral | Files missing, config wrong at boot, then emergency patches | FILES FIRST rule — enforced |
| tools.deny confusion | Different from tools.allow — deny blocks specific tools | Documented separately |
| Railway filesystem readonly | `openclaw update` / `gateway update.run` fail on Railway | Always update via template repo push |
| Channel binding confusion | Agent responded in wrong channels | Assign dedicated `{agent}-private` channel |

---

## Donatello/Michelangelo Deployment Checklist

Use this guide PLUS the April checklist as templates. Additional considerations:

**Donatello 🟣 (R&D/Research):**
- Scope: Research, idea validation, technical analysis
- Channel: `#donatello-private` (to create)
- Primary user: Guillermo (research consumer)
- Overnight: likely 00:00 HKT (before Raphael's 00:30)

**Michelangelo 🟠 (Mana Capital):**
- Scope: PE/investment research, portfolio tracking
- Channel: `#michelangelo-private` (to create)
- Primary user: Guillermo (Mana Capital work)
- Overnight: TBD (after other agents are settled)

---

## Estimated Time Budget (from April experience)

| Phase | Time (realistic) |
|-------|-----------------|
| Scope definition + API keys | 30 min |
| Workspace files creation | 1 hour |
| Discord bot setup | 30 min |
| Railway project + env vars | 30 min |
| Config refinement + boot | 1 hour |
| Integration (crons, Agent-Link, MC) | 1 hour |
| **Total** | **~4.5 hours** |

Previous estimate was "1 day." Actual April experience: 2 days due to config issues.
With this guide followed strictly: target 4-5 hours.

---

*This is a living document. Update it after every agent deployment.*  
*Molty 🦎 | v2.0 | 2026-03-15*
