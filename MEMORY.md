# MEMORY.md - Long-Term Memory

*Last updated: 2026-02-26*

---

## 👤 Guillermo

- **Location:** Hong Kong (GMT+8) — **ALWAYS think in HKT!**
- **Telegram:** @gginesta (id: 1097408992)
- **Email:** guillermo.ginesta@gmail.com
- **Mobile:** +852 5405 5953
- **Discord:** 779143499655151646
- **Style:** Casual, efficient, no fluff. Likes tables. Not super technical but learns fast.
- **Travelling:** Cebu Feb 13-18, back HK Feb 19

## 📧 Email & Google Workspace

### gog CLI (primary tool)
| What | Value |
|------|-------|
| CLI | `gog` (v0.11.0) — Google Workspace CLI |
| Account | `ggv.molt@gmail.com` |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Services | gmail, calendar, drive, docs, sheets, contacts, tasks, chat, forms, slides |

### Google Access Strategy
| Service | How | Notes |
|---------|-----|-------|
| **Gmail** | `gog gmail` on ggv.molt | Guillermo CCs Molty on relevant emails |
| **Calendar** | Service account (R/W all calendars) | Full access to Personal, Family, Brinc calendars |
| **Contacts** | Pull from calendar event attendees | Can also invite ggv.molt to events for attendee details |
| **Drive** | Shared folder (TBD) | Will set up when needed |
| **guillermo.ginesta OAuth** | On standby | Same gog auth flow if needed later |

### Email Rules
- **TO** = reply if relevant
- **CC** = don't reply unless necessary  
- **BCC** = NEVER reply

### Legacy (deprecated)
- `gmail.sh` script still exists but superseded by `gog` CLI
- Morning briefing uses `gog gmail messages search` since Feb 19

---

## 🖥️ Infrastructure

### Agents
| Agent | URL | Status |
|-------|-----|--------|
| Molty 🦎 | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | leonardo-production.up.railway.app | ✅ Active |

### Key Config
- **OpenClaw version:** 2026.2.21 (upgraded Feb 22; code live on disk, Railway redeploy pending for all agents)
- **Primary model:** `anthropic/claude-sonnet-4-6` — **DIRECT Anthropic only, NOT OpenRouter** (fleet-wide standing rule, Guillermo directive Feb 22)
- **Fallback:** OpenAI Codex / GPT-5.2 via OpenAI OAuth
- **Cron model:** `anthropic/claude-haiku-4-5` (direct Anthropic via Max plan)
- **Deploy:** Dockerfile `OPENCLAW_GIT_REF` controls version. `gateway restart` reloads config only, not binary—need full Railway redeploy for upgrades.
- **Memory System:** A1.1 with standardized indexing
  - Agents index own `memory/` + `memory/squad/`
  - Molty indexes `memory/vault/`
  - Cross-domain queries route through Molty
- **Deployment:** Railway, with memory limits:
  - Molty: 4.5GB
  - Raphael: 4GB
  - Leonardo: 4GB
- **Fleet monthly cost:** ~$124 (86% RAM cost)
- **Browser:** Brave headless
- **Heartbeat:** 1h | Context pruning: cache-ttl 4h

### Cross-Context Messaging
- **Config path:** `tools.message.crossContext.allowAcrossProviders: true`
- Enables messaging across different platforms

---

## 📝 New Key Lessons

39. **Direct Anthropic Auth:** Prefer direct model authentication over OpenRouter when possible.
40. **Content Writing Workflow:** Guillermo ideas → Molty outlines → Pikachu writes on Sonnet 4.6
41. **Sub-agent Limitations:** Can't use exec tool or directly update Notion
42. **Discord Channel Monitoring:** Set `requireMention: false` for owned channels
43. **Notion Public API can't reorder blocks** — use internal API (`/api/v3/saveTransactions`) with `token_v2` cookie
44. **Notion internal API reorder:** `listRemove` + `listBefore`/`listAfter` on parent `content` array. Include `spaceId` in every pointer.
45. **Notion space ID:** `375629bd-cc72-4ad8-a3be-84139fa2fb3b`
46. **Daily standup must process tasks BEFORE creating Notion page** — rewrite titles, estimate time, set priority, assign owner, handle sub-tasks nested
47. **Todoist CLI:** `todoist-ts-cli` (npm global), needs `TODOIST_API_TOKEN` env var. System Python lacks pip — always use venv.
48. **Cron scripts must use venv Python** — `/data/workspace/.venv/bin/python3`, not bare `python3`.
49. **message tool params:** `message` for text, `target` for recipient, `channel` for platform. NOT `activityState`.
50. **Browser stale lock files:** Brave refuses to start after container redeploy because `SingletonLock`/`SingletonSocket`/`SingletonCookie` persist on the Railway volume from the previous container. **Permanent fix:** Dockerfile now runs `/usr/local/bin/startup.sh` which clears all browser profile lock files before starting supervisord (committed f0f39aa, Feb 22). Manual fix: `rm -f /data/.openclaw/browser/*/user-data/Singleton*`.
51. **Anthropic is a built-in provider:** No `models.providers.anthropic` block needed. Just `auth.profiles.anthropic:default` with `mode: "token"`.
52. **Sonnet 4.6 replaces Opus 4.6 as primary:** 5x cheaper, 1M context, faster, wins on agentic benchmarks. Switched fleet-wide Feb 20.
53. **All cron/heartbeat on direct Anthropic Haiku:** `anthropic/claude-3-5-haiku-latest` — uses Max plan daily allowance, not OpenRouter credits.54. **Calendar ownership rule:** NEVER put Molty tasks on Guillermo's calendar. Only tasks requiring Guillermo's time.
55. **ggv.molt@gmail.com / GCP project reinstated (Feb 22).** Appeal succeeded — project `molty-assistant-486411` reinstated. `gog` binary reinstalled to `/usr/local/bin/gog`. Keyring tokens backed up to `/data/workspace/credentials/gogcli-keyring/`. Morning briefing script now self-heals: auto-installs gog + restores keyring on container restart.
56. **`gateway restart` reloads config only, not binary.** Full Railway redeploy required for OpenClaw version upgrades.
57. **Dockerfile `OPENCLAW_GIT_REF` arg** controls which OpenClaw version gets installed. Always update when upgrading.
58. **Latest OpenClaw tag is v2026.2.21** (upgraded Feb 22). Template Dockerfile updated. Railway redeploy needed to activate on running containers.
59. **Railway API deploy permissions:** Workspace token needs correct mutation scope for `serviceInstanceRedeploy`. Currently returns "Not Authorized"—investigate.
60. **Shared credentials rule:** Credentials for multiple agents go in `/data/shared/credentials/` from day one. Agents read at startup — no distribution step. Webhooks deliver messages, not file writes. (Feb 23 2026.)
61. **Change control protocol:** One change per cycle, declare blast radius, no mixed objectives. STOP means STOP. Distribute plan to affected teams BEFORE execution. Approved changes go to Change Tickets. (Feb 23 incident/change control rollout.)
62. **Change Ticket #001 scheduled for Tuesday 2026-02-24 03:00 HKT** — Per-agent webhook token rotation (cron `2b8f72fa-ec71-4f13-bdb4-52a34ad65977`). Plan: `/data/shared/memory-vault/knowledge/squad/CHANGE-TICKET-001-PER-AGENT-TOKENS.md`. Rollback: revert to shared token if any agent fails. Monitor #command-center.
63. **QMD cleanup freed 300MB:** Removed node-llama-cpp (289MB) + @tobilu/qmd + binary. OOM risk on Railway gone. Switched to OpenAI `text-embedding-3-small` (built-in). (Feb 23, Molty.)
64. **Cron/heartbeat model is `anthropic/claude-haiku-4-5` direct (NOT OpenRouter).** Uses Max plan daily allowance. (Feb 23 clarification.)
65. **OpenClaw auth: auth.json is the TRUE source, auth-profiles.json is derived.** Never write to auth-profiles.json directly. Fix auth via auth.json or `openclaw models auth paste-token` (TTY required). Path: `/data/.openclaw/agents/main/agent/auth.json`.
66. **Isolated sub-agent webhook processes do NOT inherit container env vars.** Scripts get empty strings. Must hardcode values.
67. **Railway CLI `railway shell` = local subshell, NOT container.** Use `railway connect` to SSH into the container.
68. **Leonardo Anthropic auth fixed Feb 25.** Root cause: auth.json on volume had empty/wrong token. Fix applied via Railway start command injection (Python script patched auth.json + openclaw.json before startup). FAILED deployment still writes to persistent volume — use this two-step pattern: step 1 = inject fix script as start command (deployment may fail health check but files ARE written), step 2 = revert to clean start command and redeploy (reads fixed volume, succeeds).
69. **Railway start command injection — two-step pattern.** Patching volume files via custom start command works but often fails health check (supervisord race condition). The files DO persist on the volume even from a FAILED deployment. Pattern: (1) set start command = Python patch script, trigger redeploy → FAILS but patches files, (2) revert start command to `None`/startup.sh, trigger redeploy → SUCCESS reads patched files.
70. **agents.defaults.model is the correct config key for sub-agent defaults.** There is NO `agents.defaults.subagents.model` key. The same `agents.defaults.model` controls both main sessions and spawned sub-agents. Patching a nonexistent key silently does nothing.
71. **OpenClaw cooldown ≠ API rate limit.** "Provider X in cooldown" means OpenClaw internally backed off after repeated errors from that provider (401s or 429s). It's per-process and self-resolving in ~5-15 min. Does NOT affect other agents even on the same token because it's internal state.
72. **Per-IP rate limits isolate agents.** Railway services run on different IPs. Even with the same Anthropic OAuth token, one agent can hit a per-minute rate limit while others are unaffected. Don't assume shared token = shared rate limit.
73. **Don't spam webhooks + sub-agent tests in rapid succession.** Doing so burns through per-minute API limits and triggers OpenClaw cooldowns on all providers simultaneously. Space testing by at least 5 min between attempts.
74. **Always include openai-codex/gpt-5.2 as final fallback.** OAuth-cached, no rate limits, supports tools. Fleet chain: `anthropic/claude-sonnet-4-6` → `anthropic/claude-haiku-4-5` → `xai/grok-3` → `openai-codex/gpt-5.2`.
75. **Leonardo MC Heartbeat cron live (Feb 26).** Schedule `0 */2 * * *`, Haiku direct. Confirmed working.
76. **Content workflow: Twitter-first, LinkedIn is curated mirror.** Pikachu owns Twitter/X pipeline. LinkedIn gets ~2 in 5 pieces, adapted from Twitter. Never pre-populate LinkedIn before Twitter post is live.
77. **Verify current state before reporting a task incomplete.** Daily logs go stale. Check config files, APIs, and MC before claiming something isn't done.
78. **Change Ticket #001 — Per-agent webhook tokens (Feb 26 status).** Leonardo ✅ rotated to `08d506d4...`. Raphael ✅ rotated to `a006d337...`. Molty ✅ rotated to `ab0100a5...`. Old shared token (`ed691e4...`) now inactive.
79. **PLAN-004 — Squad Overnight Workflow COMPLETE (Feb 26).** Crons: Raphael 00:30, Leonardo 01:30, Molty 03:00. Squad report in morning briefing. MC backfills confirmed.
80. **Anthropic token is shared fleet-wide.** Same `sk-ant-*` token used by Molty, Raphael, and Leonardo. secrets.json on shared volume has the correct token for all agents.
81. **PLAN-005 — Fleet Update Manager COMPLETE (Feb 27).** Molty owns all OpenClaw updates. Daily 05:15 HKT check, staged rollout Molty→Raphael→Leonardo via Railway API `OPENCLAW_GIT_REF`. Report after 06:30 briefing. v2026.2.26 fleet-wide.
82. **PLAN-006 — Fleet Directive System (Feb 27).** Queue: `/data/shared/pending-directives/<agent>/`. Scripts: `check_directives.py` + `write_directive.py`. `REQUIRES_VERSION` header gates execution. Molty 15-min cron `bc60c335` live. Raphael + Leonardo bootstrap pending.
83. **process_standup.py fix:** silently skipped rows with no Action — never read Your Notes. Fixed to infer owner from notes text. Commit `fc6d0355`.
84. **Railway API GraphQL: use inline IDs, not `$variable` syntax.** f-string `$` escaping → malformed JSON → 403. Use: `f'mutation {{ serviceInstanceRedeploy(serviceId: "{svc}", environmentId: "{env}") }}'`.
85. **HTTP 200 health check ≠ version confirmed.** Webhook ACK = "received", not "applied". Never send version-dependent scripts without confirmed version gate.
86. **Secrets migration: patch ALL agents' openclaw.json providers block BEFORE writing tokenRef/keyRef.** Missing provider → v2026.2.26 fail-fast crash. Fix: (1) add providers to openclaw.json on every agent, (2) then write refs.

---

## 🖥️ Hosting Decision (Feb 23, 2026)

- **Staying on Railway** — persistence, simplicity, fleet managed by Molty. Not worth the migration overhead.
- **DO App Platform explored** — cheaper only if trimming to 2GB RAM per agent. Ephemeral containers need Spaces backup layer. Ruled out for now.
- **Mac Mini floated** — Guillermo interested in getting Molty a Mac Mini. M4 24GB (~$799) would host full TMNT fleet, break-even ~6-7 months vs Railway. Local LLMs possible. **Revisit when timing is right.**

---

## 🐢 Mission Control (Feb 23, 2026)

- **Live:** https://tmnt-mission-control.vercel.app
- **Repo:** github.com/gginesta/tmnt-mission-control (private)
- **Tech:** NextJS 15 (downgrade from 16 due to prerender useContext bug) + Convex + Vercel (all free tier, $0/month)
- **Vercel↔GitHub:** Connected Feb 27 2026 — push to `main` = auto-deploy (no manual redeploy needed)
- **Convex:** dev:resilient-chinchilla-241 | Deployment: rosy-crocodile-290 | Team: guillermo-ginesta
- **HTTP API:** https://resilient-chinchilla-241.convex.site
- **API Key:** In Convex env `MC_API_KEY` + skill SKILL.md
- **COMPLETE.** 8 live screens, 8 API endpoints, auth + all features (Todoist sync, kanban, memory vault, pizza tracker, calendar, cost tracking, stale agent alerts)
- **Heartbeat:** Cron `46d1ca32` every 2h, Haiku, pings `/api/heartbeat` + syncs daily memory to Vault
- **Skill:** `/data/workspace/skills/mission-control/SKILL.md` (deployed to Raphael + Leonardo)
- **Molty owns the build.** Guillermo reviews product/UX.

---

## 🧠 Cerebro Project

- **Repo:** `gginesta/cerebro` (private GitHub), v1.0.0, 19 features complete
- **Live:** www.meetcerebro.com — Railway project `efcddaea-6972-...`, service `456f8881-8927-...`, env `cb8a3105-90b5-...`
- **Tech:** React+TS+Tailwind / Node+Express / Railway Postgres / Gemini OCR / xAI Grok / Stripe / Cloudinary / Resend

### Critical Issues (Feb 20)
1. **Live site: white page** — SPA loads but nothing renders. API healthy (200ms). Needs browser console debug.
2. **Missing prod env vars:** STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, GEMINI_API_KEY, Stripe price IDs.
3. **DB ambiguity:** .env references Neon; prod uses Railway Postgres. Schema parity unconfirmed.

### Plans
- **Dev plan:** `/data/shared/cerebro/CEREBRO-DEVELOPMENT-PLAN.md` (3 workstreams: A=Molty/unblock, B=Leonardo+Codex/polish, C=Guillermo+Raphael/sell)
- **Codex plan:** `/data/shared/cerebro/CODEX-INTEGRATION-PLAN.md` (GitHub issues → Codex execution → auto-deploy)
- **Target:** 10 paying customers in 12 weeks

### Files
- **Local:** `/data/shared/cerebro/meetcerebro/` (Syncthing copy, no git history)

87. **`sessionTarget: isolated` is mandatory for `agentTurn` crons.** Documented explicitly in CRON_JOB_TEMPLATE.md. `sessionTarget: main` only works with `payload.kind: systemEvent`. Proposing "Model B" (main session overnight) was architecturally wrong — should have read the docs first.
88. **Isolated cron sessions cannot reliably use `memory_search`.** No existing cron uses it. Memory access in isolated sessions = file reads via `cat` + API calls via `curl`. Never instruct an isolated agentTurn session to use memory_search for pre-flight.
89. **The overnight context fix is entirely in the prompt.** Mandatory pre-flight: (1) cat memory log files, (2) curl MC for task statuses, (3) scan log text for each task before executing. If mentioned → skip.
90. **Read the docs before proposing architecture changes.** CRON_JOB_TEMPLATE.md, SUB-AGENT-OPERATING-STANDARD.md, and openclaw-best-practices.md contained all necessary constraints. Reading them first would have prevented a full day of whack-a-mole.
91. **Fleet directives go to #command-center, not split channels.** One message, all agents see it. Don't open parallel threads across brinc-private and launchpad-private for the same topic.

## 🏥 Insurance & Benefits

### Bupa Health Insurance
- **Policy:** Bupa group membership (Brinc corporate)
- **Email:** Renewal docs forwarded to ggv.molt@gmail.com Feb 20 2026
- **Action:** Review renewal documents, confirm coverage details when asked

### Accountant
- **Name:** Raeniel CAAGBAY
- **Email:** raeniel@imsg.com.hk
- **Role:** Guillermo's accountant — ggv.molt added for visibility on relevant threads
- **Action:** Monitor for items needing Guillermo's attention, flag FY threads
