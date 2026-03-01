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

## 📧 Email & Google Workspace

### gog CLI (primary tool)
| What | Value |
|------|-------|
| CLI | `gog` (v0.11.0) — Google Workspace CLI |
| Account | `ggv.molt@gmail.com` |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Services | gmail, calendar, drive, docs, sheets, contacts, tasks, chat, forms, slides |

### Email Rules
- **TO** = reply if relevant
- **CC** = don't reply unless necessary
- **BCC** = NEVER reply

---

## 🖥️ Infrastructure

### Agents
| Agent | URL | Status |
|-------|-----|--------|
| Molty 🦎 | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | leonardo-production.up.railway.app | ✅ Active |

### Key Config
- **OpenClaw version:** 2026.2.26 (fleet-wide as of Feb 27). Update via `OPENCLAW_GIT_REF` Railway env var + auto-redeploy.
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
50. **Browser stale lock files:** Brave won't start after redeploy due to `Singleton*` lock files persisting on volume. Manual fix: `rm -f /data/.openclaw/browser/*/user-data/Singleton*`. Permanent fix in startup.sh (committed f0f39aa).
51. **Anthropic is a built-in provider:** No `models.providers.anthropic` block needed. Just `auth.profiles.anthropic:default` with `mode: "token"`.
52. **Sonnet 4.6 replaces Opus 4.6 as primary:** 5x cheaper, 1M context, faster, wins on agentic benchmarks. Switched fleet-wide Feb 20.
53. **All cron/heartbeat on direct Anthropic Haiku:** `anthropic/claude-3-5-haiku-latest` — uses Max plan daily allowance, not OpenRouter credits.54. **Calendar ownership rule:** NEVER put Molty tasks on Guillermo's calendar. Only tasks requiring Guillermo's time.
55. **ggv.molt@gmail.com GCP project reinstated (Feb 22).** `gog` binary at `/usr/local/bin/gog`. Keyring at `/data/workspace/credentials/gogcli-keyring/`. Morning briefing self-heals on restart.
56. **`gateway restart` reloads config only, not binary.** Full Railway redeploy required for OpenClaw version upgrades.
57. **`OPENCLAW_GIT_REF` Railway env var** controls which OpenClaw version gets cloned at container start. Update it + auto-redeploy to upgrade fleet.
60. **Shared credentials rule:** Credentials for multiple agents go in `/data/shared/credentials/` from day one. Agents read at startup — no distribution step. Webhooks deliver messages, not file writes. (Feb 23 2026.)
61. **Change control protocol:** One change per cycle, declare blast radius, no mixed objectives. STOP means STOP. Distribute plan to affected teams BEFORE execution. Approved changes go to Change Tickets. (Feb 23 incident/change control rollout.)
62. **Change Ticket #001 — Per-agent webhook token rotation.** Executed Feb 24/26. Tokens in TOOLS.md. Old shared token inactive.
64. **Cron/heartbeat model is `anthropic/claude-haiku-4-5` direct (NOT OpenRouter).** Uses Max plan daily allowance. (Feb 23 clarification.)
65. **OpenClaw auth: auth.json is the TRUE source, auth-profiles.json is derived.** Never write to auth-profiles.json directly. Fix auth via auth.json or `openclaw models auth paste-token` (TTY required). Path: `/data/.openclaw/agents/main/agent/auth.json`.
66. **Isolated sub-agent webhook processes do NOT inherit container env vars.** Scripts get empty strings. Must hardcode values.
67. **Railway CLI `railway shell` = local subshell, NOT container.** Use `railway connect` to SSH into the container.
68. **Leonardo Anthropic auth fixed Feb 25** via Railway start command injection. FAILED deployments still write to persistent volume — two-step pattern: (1) inject fix script as start command → deploy FAILS but files written, (2) revert start command → redeploy SUCCESS reads fixed files.
69. **Raphael Anthropic auth restored Feb 28** via `ANTHROPIC_API_KEY` Railway env var. Simpler than two-step injection when token is available. The `default` secrets provider reads env vars first.
70. **`agents.defaults.model` controls both main + sub-agent sessions.** No separate `agents.defaults.subagents.model` key exists.
71. **OpenClaw cooldown ≠ API rate limit.** Internal backoff after repeated errors. Self-resolving in ~5-15 min, per-process only.
72. **Per-IP rate limits isolate agents.** Different Railway IPs → one agent hitting limits doesn't affect others on the same token.
73. **Don't spam webhooks + sub-agent tests rapidly.** Burns rate limits and triggers cooldowns on all providers. Space by 5+ min.
74. **Always include openai-codex/gpt-5.2 as final fallback.** OAuth-cached, no rate limits, supports tools. Fleet chain: `anthropic/claude-sonnet-4-6` → `anthropic/claude-haiku-4-5` → `xai/grok-3` → `openai-codex/gpt-5.2`.
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

## 📬 Email Clarity (important)
- **guillermo.ginesta@gmail.com** — Guillermo's personal email. Molty has NO access. Only sees what Guillermo forwards, CCs, or BCCs to ggv.molt@gmail.com.
- **ggv.molt@gmail.com** — Molty's OWN inbox. Must check daily (cron re-enabled 2026-02-28, 3x daily 6AM/9AM/3PM HKT). Process everything: Notion notifications, forwards from Guillermo, accountant threads, etc.
- **AgentMail** — reviewed 2026-02-28. Not needed now. Revisit if agents need outbound email at scale (Raphael sales, Cerebro outreach).

## ⚠️ Guillermo's Standing Rule — Promises (2026-02-28)

**"I don't want promises if you can't keep them or forget them in the first place."**

- Do not say something is running/working unless it has been verified end-to-end
- Do not commit to a process unless there is a mechanism (cron, script, enforcement) backing it up
- Verbal commitments with no technical backing are not commitments — they are noise
- If uncertain whether something works: say so, then verify, then confirm
- A broken promise is worse than no promise — it erodes trust and wastes Guillermo's time
- This applies to: email checks, memory logs, overnight crons, fleet updates, anything operational
