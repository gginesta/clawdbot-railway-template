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
- **OpenClaw version:** Molty v2026.3.1 (updated Mar 2). Raphael + Leonardo v2026.2.26. v2026.3.2 released 2026-03-03 — pending Guillermo go/no-go for fleet update. Update via `OPENCLAW_GIT_REF` Railway env var + auto-redeploy.
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

**Quick ref:** `/data/workspace/memory/refs/standup-process.md` | **Build plan:** `/data/workspace/plans/standup-build-plan-2026-03-03.md`

### Cron Registry
13b4eaa0 Todoist Triage (hourly) · ad96575e Pre-Standup Prep (4:30PM) · bdb28765 Daily Standup (5PM) · 8991c017 Overnight Sync (4AM) · 8b748f23 Morning Briefing (6:30AM) · 80105aa4 Molty Nightly (3AM) · e94b898e Daily Status #command-center (9AM) — all Haiku/Sonnet, isolated

### Scripts (all compile clean)
todoist_triage.py · standup_prep.py · standup_status_reader.py · daily_standup.py · process_standup.py · overnight_sync.py · morning_briefing.py

### Rules (never forget) — full detail in quick-ref
- Verbal "done" = close Todoist + Notion + MC immediately. Calendar = post-review only, bias BLOCK.
- Tomorrow's Focus = ONE blank callout, Guillermo fills → calendar event. Clarify > assume.
- Overnight log: ✅ Completed / 👀 Under Review / ❌ Failed (why) / 🚧 Blocked (ask) / ⏭ Skipped
- Squad status files: `/data/shared/logs/standup-status-{DATE}-{agent}.txt`

### MC Fleet Tasks (Molty — Mission Control Phase 3)
13 active (assigned), execute overnight P2 first: A2→B1→C1→B3→B4 then P3s
Parked: B2 Dark Mode ("don't care"), C5 File Attachments ("don't need it") — Guillermo 2026-03-03
Large tasks needing breakdown before overnight: D6 User Auth, B4 DnD Kanban, D4 Memory Timeline

## 📝 New Key Lessons

39. **Direct Anthropic Auth:** Prefer direct auth over OpenRouter. Sub-agents can't use exec tool or directly update Notion. Discord owned channels: `requireMention: false`.
43. **Notion block reorder:** Use internal API (`/api/v3/saveTransactions`) with `token_v2` cookie. `listRemove` + `listBefore`/`listAfter` on parent `content` array. Space ID: `375629bd-cc72-4ad8-a3be-84139fa2fb3b`.
44. **Daily standup must process tasks BEFORE creating Notion page** — rewrite titles, estimate time, set priority, assign owner, handle sub-tasks nested
47. **Todoist CLI:** `todoist-ts-cli` (npm global), needs `TODOIST_API_TOKEN` env var. System Python lacks pip — always use venv.
48. **Cron scripts must use venv Python** — `/data/workspace/.venv/bin/python3`, not bare `python3`.
49. **message tool params:** `message` for text, `target` for recipient, `channel` for platform. NOT `activityState`.
50. **Browser stale lock files:** Brave won't start after redeploy due to `Singleton*` lock files persisting on volume. Manual fix: `rm -f /data/.openclaw/browser/*/user-data/Singleton*`. Permanent fix in startup.sh (committed f0f39aa).
51. **Anthropic is a built-in provider:** No `models.providers.anthropic` block needed. Just `auth.profiles.anthropic:default` with `mode: "token"`.
52. **Sonnet 4.6 replaces Opus 4.6 as primary:** 5x cheaper, 1M context, faster, wins on agentic benchmarks. Switched fleet-wide Feb 20.
53. **All cron/heartbeat on direct Anthropic Haiku:** `anthropic/claude-haiku-4-5` direct — Max plan daily allowance.
54. **Calendar ownership rule:** NEVER put Molty tasks on Guillermo's calendar. Only tasks requiring Guillermo's time.
56. **OpenClaw upgrades:** `gateway restart` reloads config only. Full Railway redeploy required. `OPENCLAW_GIT_REF` env var controls version — update it + auto-redeploy.
60. **Shared credentials rule:** Go in `/data/shared/credentials/`. Agents read at startup. Webhooks deliver messages, not file writes.
61. **Change control:** One change per cycle, declare blast radius, no mixed objectives. Distribute plan before execution. Tokens in TOOLS.md (Change Ticket #001 Feb 24/26).
64. **Cron/heartbeat model is `anthropic/claude-haiku-4-5` direct (NOT OpenRouter).** Uses Max plan daily allowance. (Feb 23 clarification.)
65. **OpenClaw auth: auth.json is the TRUE source, auth-profiles.json is derived.** Never write to auth-profiles.json directly. Fix auth via auth.json or `openclaw models auth paste-token` (TTY required). Path: `/data/.openclaw/agents/main/agent/auth.json`.
66. **Isolated sub-agent webhook processes do NOT inherit container env vars.** Scripts get empty strings. Must hardcode values.
74. **Always include openai-codex/gpt-5.2 as final fallback.** OAuth-cached, no rate limits, supports tools. Fleet chain: `anthropic/claude-sonnet-4-6` → `anthropic/claude-haiku-4-5` → `xai/grok-3` → `openai-codex/gpt-5.2`.
77. **Verify current state before reporting a task incomplete.** Daily logs go stale. Check config files, APIs, and MC before claiming something isn't done.
80. **Anthropic token is shared fleet-wide.** Same `sk-ant-*` token used by Molty, Raphael, and Leonardo. secrets.json on shared volume has the correct token for all agents.
82. **Fleet Directive System (Feb 27).** Queue: `/data/shared/pending-directives/<agent>/`. Scripts: `check_directives.py` + `write_directive.py`. `REQUIRES_VERSION` header gates execution. Molty cron `bc60c335` live.
84. **Railway API GraphQL:** Use inline IDs, not `$variable` syntax — f-string `$` escaping breaks JSON. Webhook ACK = "received", not "applied".

---

## 🖥️ Hosting
- **Railway** — staying. Mac Mini floated (M4 24GB ~$799, break-even ~6-7mo), revisit when timing right.

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

---

## 🧠 Cerebro Project

- **Repo:** `gginesta/cerebro` (private GitHub), v1.0.0, 19 features complete
- **Live:** www.meetcerebro.com — Railway project `efcddaea-6972-...`, service `456f8881-8927-...`, env `cb8a3105-90b5-...`
- **Tech:** React+TS+Tailwind / Node+Express / Railway Postgres / Gemini OCR / xAI Grok / Stripe / Cloudinary / Resend

- **Plans:** dev plan + codex plan in `/data/shared/cerebro/`. Target: 10 paying customers in 12 weeks.

87. **Isolated crons:** `sessionTarget: isolated` for `agentTurn` crons. Can't use memory_search — use `cat` + `curl`. Pre-flight: cat memory logs, curl MC statuses, skip if already done.
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
101. **Unbrowse DIY — audited 2026-03-03. PARKED.** CDP-based API skill capture (cdp-capture.js + skill-gen.py). NOT worth deploying — all current integrations have documented APIs. Only useful for undocumented internal portals. Scripts: `scripts/api-capture/`. Pull out on-demand.
102. **summarize CLI installed (2026-03-03).** v0.11.1 global + yt-dlp + ffmpeg. Config: `~/.summarize/config.json` (Gemini Flash default). Skill: `/openclaw/skills/summarize/SKILL.md`. Works: web articles, direct audio URLs (Whisper). Broken: YouTube (Railway IPs blocked), podcast RSS. YouTube: Guillermo's Chrome extension works locally. See TOOLS.md for full setup.
103. **Calendar booking rules — LOCKED (Guillermo, 2026-03-03).** Check ALL 3 cals before booking (Brinc/Personal/Shenanigans). Family→Shenanigans, work→Brinc (visible), personal→Personal. All non-Brinc bookings = auto Brinc "Busy [private]" block. Protected: school dropoff 08:00-08:30 MoWeFr (LOCKED), pickup 10:30-11:00 MoWeFr, focus 08:30-10:30 WeFr. Full config: `/data/workspace/credentials/calendar-config.json`. Enforced in process_standup.py (commit 50336348).
104. **Standup script key lesson — never run debug/test runs after showing Guillermo the URL.** Each run creates new page + updates state file. State file must be locked after presenting to user. Fixed: always check state file points to the user-facing page before running process_standup.py.
105. **Notion property name matching is strict.** If script writes to a property that doesn't exist in the DB schema, Notion returns 400 and fails silently. Always verify DB property names match script exactly. Fix: log response body on non-200 writes.

## 📬 Contacts & Email
- **Raeniel CAAGBAY** (raeniel@imsg.com.hk) — Guillermo's accountant. Flag FY threads needing his attention.
- **Bupa** — Group health insurance (Brinc corp). Renewal docs in ggv.molt@gmail.com (Feb 20 2026).
- **guillermo.ginesta@gmail.com** — Guillermo's personal email. Molty has NO access.
- **ggv.molt@gmail.com** — Molty's OWN inbox. 3x daily (6AM/9AM/3PM HKT). Process everything.

113. **OpenClaw config: tailscale.mode=serve requires bind=loopback (Mar 4 2026).** When `gateway.tailscale.mode="serve"`, `gateway.bind` must be `"loopback"`. Do not use `"auto"` with serve mode. This was the fix that brought Raphael back online after a 2hr outage.
114. **OpenClaw config: channels.discord.dm is old format (Mar 4 2026).** The `channels.discord.dm.policy` key is deprecated. Remove it entirely. The new format uses `channels.discord.dmPolicy` at the top level. Having the old `dm` key crashes the gateway.
115. **PPEE lesson (Mar 4 2026): diagnose before acting on infra issues.** I triggered 8+ redeployments without a clear fix plan. Wasted 2hrs. Rule: read the logs fully, identify root cause, form ONE fix, execute once. Never whack-a-mole Railway deployments. Check if the same issue has been solved before (it had — Raphael fixed the same bind issue on Molty).

## ⚠️ Promises Rule (Guillermo, Feb 28)
**"Don't promise what you can't keep."** Only commit to things with a technical mechanism backing them. Verify before confirming. A broken promise is worse than no promise.

106. **Fleet update cron = check + notify only. NEVER auto-update.** `openclaw update` doesn't exist. Correct update path: change `OPENCLAW_GIT_REF` Railway env var + trigger redeploy via Railway API. Updates are PARKED — always ask Guillermo first. Cron: `c0705ffd` at 21:15 HKT, state file: `/data/workspace/state/openclaw-fleet-version.json`. (2026-03-03)
107. **Cerebro DB migration 003 (2026-03-03).** Added `is_vip BOOLEAN DEFAULT FALSE` to contacts table; created `contact_reminders` table (id, contact_id, user_id, trigger_type, reminder_date, message, sent, created_at) + 2 indexes. Trigger already existed. Leonardo's PR #33 (Smart Follow-up Reminders) now live on prod Railway Postgres.
108. **Daily status cron — all agents post to #command-center at 09:00 HKT.** Molty cron: `e94b898e`, Haiku, isolated. Raphael + Leonardo instructed via fleet directive. Format: matches Leonardo's established pattern.
109. **Fleet backup separation rule (2026-03-03).** Updates = Molty only (fleet update cron at 05:15 HKT). Backup = each agent's own dedicated cron, no mixed objectives. Raphael + Leonardo notified via webhook to audit and split if mixed.
110. **Whoop Health Integration — MC task assigned to Molty.** Scope: research Whoop API (auth flow, data endpoints: recovery score, sleep, HRV, strain), multi-user access (Guillermo + wife), integration plan. Guillermo directive 2026-03-03.
112. **Python variable shadowing bug (2026-03-03).** Assigning to a name anywhere in a function makes Python treat it as local for the ENTIRE scope. If a local var shares a name with a module-level function that's also called in the same function → UnboundLocalError. Fix: rename local var. Never reuse function names as variable names.
111. **April + Donatello planning interview — booked Wed Mar 4, 15:45–16:15 HKT.** April (personal assistant) + Donatello (R&D/tinkerer) are pending deployment. Molty to interview Guillermo on plans for both roles. Personal cal + Brinc busy/private block added.
