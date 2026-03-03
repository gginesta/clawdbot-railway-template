# MEMORY.md - Long-Term Memory

*Last updated: 2026-03-03*

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

## 🗂 Daily Standup System v2.1 — COMPLETE (2026-03-03)

**Source of truth:** `/data/workspace/plans/standup-build-plan-2026-03-03.md` (19.5KB)
**Design spec:** `/data/workspace/plans/standup-system-redesign.md`
**Quick ref:** `/data/workspace/memory/refs/standup-process.md`
**Git:** master fcea521e → 12e16e95

### Cron Registry
| ID | Name | Time | Model |
|----|------|------|-------|
| 13b4eaa0 | Todoist Inbox Triage | Hourly, HKT | Haiku |
| ad96575e | Pre-Standup Prep | 4:30 PM HKT | Haiku |
| bdb28765 | Daily Standup | 5:00 PM HKT | Sonnet |
| 8991c017 | Overnight Sync (MC→Todoist→Notion) | 04:00 HKT | Haiku |
| 8b748f23 | Morning Briefing | 6:30 AM HKT | (main) |
| 80105aa4 | Molty Nightly | 03:00 HKT | Sonnet |

### Scripts (all compile clean)
todoist_triage.py · standup_prep.py · standup_status_reader.py · daily_standup.py · process_standup.py · overnight_sync.py · morning_briefing.py

### Rules (never forget)
- **Verbal "done"** = close Todoist + Notion + MC in same response. No deferral.
- **Todoist + MC** must never diverge >2h. Heartbeat syncs completions both ways.
- **Task title** (one-time on intake): `Reply to Raeniel — 30min 🦎` — specific + time + 🦎 at end.
- **Tomorrow's Focus** = ONE item, blank callout, Guillermo fills it → calendar event post-review.
- **Calendar** = post-review ONLY, never at generation. Bias: BLOCK (over-book > miss).
- **Clarifying questions** = preferred over silence. Both Telegram + Notion callout.
- **Overnight log format**: ✅ Completed / 👀 Under Review / ❌ Failed (why) / 🚧 Blocked (ask) / ⏭ Skipped
- **Squad status**: agents write to `/data/shared/logs/standup-status-{DATE}-{agent}.txt`
- **Overnight sync** at 04:00 HKT closes Todoist + Notion rows for MC-done tasks

### MC Fleet Tasks (Molty — Mission Control Phase 3)
13 active (assigned), execute overnight P2 first: A2→B1→C1→B3→B4 then P3s
Parked: B2 Dark Mode ("don't care"), C5 File Attachments ("don't need it") — Guillermo 2026-03-03
Large tasks needing breakdown before overnight: D6 User Auth, B4 DnD Kanban, D4 Memory Timeline

### Backup
- Cron d9da8767: 21:00 HKT daily, backup.sh only ✅
- **Never move without explicit Guillermo confirmation in conversation**
- Spurious "21:30" webhook on 2026-03-03 was a confused agent status check — ignored, no change made

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

## 🐢 Mission Control — WHAT IT IS (fleet-wide definition)

**TMNT Mission Control ≠ Notion.** These are two different systems.

| System | What it is | Use for |
|--------|-----------|---------|
| **TMNT Mission Control (MC)** | Custom fleet dashboard (NextJS + Convex) | Fleet-wide tasks, agent status, heartbeats, cross-agent visibility |
| **Notion Brinc HQ Tasks DB** | Raphael's domain task tracker | Brinc-specific work, proposals, sales tasks |

**MC = https://tmnt-mission-control.vercel.app**
**API = https://resilient-chinchilla-241.convex.site**
**API Key = Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc**
**Skill = /data/workspace/skills/mission-control/SKILL.md** (must be installed on all agents)

Create MC task: `POST /api/task` with `title`, `project` (brinc|cerebro|mana|personal|fleet), `createdBy`, optional `assignees`, `priority` (p0-p3), `status`.

---

## 🐢 Mission Control — Build Details (Feb 23, 2026)

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

87. **`sessionTarget: isolated` mandatory for `agentTurn` crons.** `sessionTarget: main` only for `systemEvent`. Isolated crons can't use memory_search — use `cat` + `curl` for pre-flight.
88. **Overnight cron pre-flight (mandatory):** (1) cat memory logs, (2) curl MC for task statuses, (3) skip if already in logs. No memory_search in isolated sessions.
89. **Fleet directives go to #command-center.** One message, all agents. Don't split across brinc-private / launchpad-private.
90. **OpenClaw update incorporation — PARKED.** Flag to Guillermo when next update drops, discuss before building. Daily check at 05:15 HKT still runs.
91. **Memory index corruption:** `openclaw memory index --force` if status shows 0 files but >0 embeddings. Weekly health check auto-detects + fixes.
92. **Three-agent overnight system:** Raphael 00:30, Leonardo 01:30, Molty 03:00. Logs to /data/shared/logs/. Molty consolidates + posts #squad-updates.
93. **TTS/Voice:** ElevenLabs, Daniel voice (onwK4e9ZLuTAKqWW03F9), inbound only. Credentials: /data/workspace/credentials/elevenlabs.env.
94. **Email:** ggv.molt@gmail.com = Molty's own inbox. 3x daily (6AM/9AM/3PM HKT). Guillermo CCs/forwards for visibility only.
95. **Notion comment monitoring:** Public API returns empty. Use internal API loadPageChunk + token_v2.
96. **process_standup.py:** Don't dump dispatched tasks back at Guillermo. Dedup via in-memory dict O(1) (commit 02b29303). Dedup threshold: 55% fuzzy match.
97. **Cron agentId must not be empty string** — set to "main" or target agent ID. Writes fail silently if empty.
98. **Standup system v2.1 COMPLETE (Mar 3 2026).** See standup section above. Tonight is first live run.
99. **Backup cron d9da8767:** 21:00 HKT, backup.sh only. Never move without explicit Guillermo confirmation. Spurious "21:30" webhook on 2026-03-03 was ignored (confused agent status check).
100. **MC fleet tasks (Molty):** 13 active, execute overnight P2 first. B2 Dark Mode + C5 File Attachments parked (Guillermo, Mar 3).
101. **Unbrowse DIY — audited 2026-03-03. PARKED.** Code is good (cdp-capture.js + skill-gen.py + wrapper). Gaps: requires interactive browsing + manual Brave debug port + no fleet distribution + no skill registration + OAuth not handled. NOT worth deploying — all current integrations (HubSpot/Notion/Todoist/Cerebro) have documented APIs. Pull out only if we ever need to call an undocumented internal portal/tool with no public API. Scripts at: `scripts/api-capture/`. Suggested P3 improvements: auto-browse mode, credential persistence, fleet directive on generation.
102. **summarize CLI — installed 2026-03-03.** `npm install -g @steipete/summarize` (v0.11.1), yt-dlp v2026.02.21, ffmpeg v7.0.2 (static). Config: `~/.summarize/config.json` (Gemini 2.5 Flash default, Anthropic fallback). OPENAI_API_KEY is in env (sk-proj-...). Skill at `/openclaw/skills/summarize/SKILL.md` — auto-discovered on next session (binary on PATH). **What works:** web articles (fast, clean), direct audio/video URLs (Whisper via OPENAI_API_KEY). **What doesn't:** YouTube (Railway IPs blocked by bot detection — both yt-dlp AND transcript APIs), podcast RSS (29MB+ too large or no inline transcript). Chrome extension approach works for YouTube locally but not server-side. Plan: `/data/workspace/plans/summarize-setup-2026-03-03.md`. Code is good (cdp-capture.js + skill-gen.py + wrapper). Gaps: requires interactive browsing + manual Brave debug port + no fleet distribution + no skill registration + OAuth not handled. NOT worth deploying — all current integrations (HubSpot/Notion/Todoist/Cerebro) have documented APIs. Pull out only if we ever need to call an undocumented internal portal/tool with no public API. Scripts at: `scripts/api-capture/`. Suggested P3 improvements: auto-browse mode, credential persistence, fleet directive on generation.

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
