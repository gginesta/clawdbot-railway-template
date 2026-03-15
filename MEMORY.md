# MEMORY.md - Working Memory

*Last updated: molty | 2026-03-15 | Nightly curation: removed resolved lesson 126 | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.3.13 (deployed 2026-03-14, all 4 agents ✅)
| Agent | URL | Model |
|-------|-----|-------|
| Molty 🦎 | ggvmolt.up.railway.app | Opus (primary) |
| Raphael 🔴 | ggv-raphael.up.railway.app | Sonnet |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet |
| April 🌸 | april-agent-production.up.railway.app | Sonnet |

**Cron model:** Haiku direct | **Fallback:** Codex/GPT-5.2

## 🐢 Mission Control
- **URL:** https://tmnt-mission-control.vercel.app
- **API:** https://resilient-chinchilla-241.convex.site
- **Key:** Bearer 232e4ddf...c562
- **Endpoints:** GET `/api/tasks` (plural) | POST/PATCH `/api/task` (singular)

## 📅 Calendar
- **SA token:** `google-service-account.json` (no delegation)
- **Brinc busy block:** automatic in cal_create (enforced in code)
- **Full rules:** `memory/refs/standup-process.md`

## 📋 Active Projects
- **Cerebro:** www.meetcerebro.com — 10 customers in 12 weeks
- **WHOOP:** Research done, blocked on CLIENT_ID/SECRET from Guillermo. Notion spec: `31939dd6...`
- **MC Phase 3:** 13 tasks assigned, P2s first
- **ginesta.io:** Brief in Notion → https://www.notion.so/Personal-Website-Brief-www-ginesta-io-31a39dd69afd81cea223fbb9f2b2fe39. Waiting on Guillermo's content checklist.
- **April (agent):** FULLY OPERATIONAL ✅ Deployed 2026-03-11. Discord ✅ WhatsApp ✅ Calendar ✅ agent-link ✅. Steph USER.md interview pending Guillermo. Config: no `tools.allow` restriction (full profile). WhatsApp: `debounceMs: 3000`.
- **Agent Performance Review:** P1 overnight work planned (PLAN-011). Design review process + add "Last updated by" headers to shared files. Trust/coaching model, not gatekeeping. Cascade to fleet after approval.
- **gws CLI:** v0.4.4 primary tool. Gmail ✅ Calendar ✅ Drive ✅ Docs ✅ Sheets ✅ (all 9 scopes). Config: `~/.config/gws/`. 11 skills at `/openclaw/skills/gws-*`. gog deprecated as fallback. GCP OAuth project: `847540297795` (separate from Gemini project `226575193033`).
- **Agent-Link v2 (PLAN-015):** IMPLEMENTED ✅ Mar 12. Worker + queue + health system live. Leonardo/April webhooks still timing out → messages auto-queued and retried. Root cause TBD (gateway hangs on `/hooks/agent` endpoint — services ARE up).
- **Browser relay:** PARKED. Blocker: relay only included in full gateway, not `openclaw node run`. Node on GUILLERMO-DESKTOP is paired ✅. Resume when Guillermo wants Raphael to control Waalaxy.
- **Content/Pikachu:** Tamagotchi Trap posted (X + LinkedIn) 2026-03-05. Standing permission: generate kawaii robot images for future articles. Next article: "What AI Agents Actually Do For Me".

## ⏳ Pending (as of 2026-03-13)
- **Molty webchat device auth:** OpenClaw core bug — `dangerouslyDisableDeviceAuth` recognized but auth still enforced. Issue #41878 open. Workaround: URL token param `?token=<gateway_token>`.
- **Agent-Link webhooks:** ✅ Confirmed working for all agents after v2026.3.13 (Mar 14). HTTP 200 + ok:true.
- **Leonardo:** CRM Pipelines Phase B PR #76 — 724 lines, 3 features. Needs Guillermo review before deploy.
- **Raphael:** G4a test decks — awaiting Guillermo review. G2 exclusion matrix done ✅. C5 shipped ✅.
- **Raphael:** A8 blocked — needs live Brinc proposal deck (Feb 2026 branding) from Guillermo
- **April:** Steph's interview page ready to share — Guillermo sends to Steph when ready
- **MC Phase 3 remaining:** D4 Memory Timeline, D2 Notification Prefs, [D6] Auth, [D1] Templates, [A4] Weekly Digest UI
- **Pikachu article:** "What AI Agents Actually Do For Me" — not started
- **Personal finance tasks:** Life insurance, car estimate, health insurance, joint accounts, last will, credit card — all need Guillermo to drive

## 📣 Standup System v3.0 (directive 2026-03-14)
**Webchat-native standup. Notion task DB dropped.**
- Primary: Webchat (Guillermo at computer)
- Backup: Telegram (when mobile)
- Notion: Docs hub only — NO task sync, NO standup pages
- Flow: I send formatted review → Guillermo replies inline → I process
- Full spec: `memory/refs/standup-process.md`

## 📋 PLAN-016: Todoist↔MC Sync v2 (approved 2026-03-14)
**Single source of truth in Todoist, mirrored to MC.**
- Guillermo captures fast in Todoist (no extra fields)
- Assignment: prefix (`Raphael: do X`) OR standup triage
- Molty edits task → `[Raphael] do X` + creates MC task
- Fleet tasks STAY in Todoist (Guillermo keeps visibility)
- Completion syncs both ways
- Plan: `/data/workspace/plans/PLAN-016-todoist-mc-sync-v2.md`
- Status: Phase 1-2 tonight, Phase 3-4 Sunday, test Monday

## ⚠️ Core Rules
1. **PPEE:** Pause → Plan → Evaluate → Execute. One fix, not many.
2. **Don't claim done without citing file+line.**
3. **Mistakes → `memory/refs/mistake-tracker.md` immediately.**
4. **Code > docs.** If a rule can be enforced in code, do that.
5. **Before answering "what's the status of X"** — search Notion + plans/ + memory/ first. Never claim "nothing exists" without checking all sources.

## 📖 Reference Pointers
- **My task list → `TODO.md`** (check at session start, update after work)
- Technical lessons → `memory/refs/lessons-learned.md`
- Standup/calendar rules → `memory/refs/standup-process.md`
- **Fleet updates → `memory/refs/fleet-updates.md`** (how to update OpenClaw on Railway)
- Code-enforced rules → `memory/refs/code-enforced-rules.md`
- Mistake tracking → `memory/refs/mistake-tracker.md`
- Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md`

---

*Full lesson archive: `memory/refs/lessons-learned.md`*

122. **Policy: no fleet infrastructure changes without explicit Guillermo sign-off** — Guillermo's words after the Rough Monday outage: "Every time you try to update OpenClaw you break the fleet." Do not push version bumps, startCommands, or config patches fleet-wide without approval.
127. **Dockerfile container user mismatch causes fleet outage (REG-025, Mar 10 2026):** arjunkomath upstream uses `root`; ours uses `openclaw`. Upstream merge changed container user → secrets unreadable → total outage. Always check `USER` in Dockerfile before any upstream merge. Our Dockerfile (233 lines) has Tailscale/Brave/Syncthing — must cherry-pick manually, never `git merge`. Audit: `plans/upstream-audit-2026-03-10.md`.
129. **Railway volume duplication causes startup failure (Mar 11 2026):** `railway.toml requiredMountPath` auto-creates a volume. Adding another via API → two volumes at `/data` → no-boot, no logs. Check existing volumes before creating. Delete extras via UI.
130. **Webchat URL token workaround for device auth (Mar 11 2026):** Device auth resets on gateway restart, locking users out. Workaround: append gateway token as URL param — `https://<host>/?token=<gateway_token>`. Avoids repeated setup wizard. Applies to all agents.
131. **gws "Caller does not have required permission" fix (Mar 11 2026):** If `client_secret.json` contains `project_id`, gws triggers GCP serviceUsageConsumer permission check and fails. Fix: remove `project_id` from `~/.config/gws/client_secret.json`. Also delete stale `.enc` credential files from other machines.
132. **Discord bot config — use channel NAME not ID (Mar 11 2026):** Channel IDs sometimes don't resolve in OpenClaw Discord config. Use channel name (e.g. `april-private`) instead. Bot also needs OAuth invite with correct permissions (`/api/oauth2/authorize?client_id=<id>&permissions=68608&scope=bot`) plus explicit View/Send/Read History granted per channel.
133. **MC PATCH API — task ID in body, not URL path (Mar 11 2026):** PATCH `/api/task` requires the task `id` field in the request body. Putting it in the URL path causes silent failure. Confirmed pattern: `PATCH /api/task` with body `{ "id": "<taskId>", ...fields }`.
134. **Morning briefing v3.0 — condensed format (Mar 12 2026):** Briefing was 4 screens → now ~1 screen. Keeps: Focus, Blocked (max 3), Review (max 3), Calendar (one line), Heads up (notable only), Weather (one line), OpenClaw. Removes: overnight report details, plans, tasks, squad, email, Notion comments, weather outlook. See PLAN-013.
135. **OpenClaw agent config — model placement (Mar 12 2026):** `model` must go under `agents.defaults.model` as `{primary: "...", fallbacks: [...]}` — NOT at root config level. Also: `cron.jobs` key does NOT exist in config; add crons via `/cron add` tool only. Learned during April PLAN-014 integration.
136. **Agent-Link v2 IMPLEMENTED (PLAN-015, Mar 12 2026):** Trusted fleet messaging with `tmnt-v1` envelope, retry queue. Worker: `/data/shared/scripts/agent-link-worker.py`. Health: `/data/shared/health/{agent}.json`. Queue cron: `57a4956a` (every 5min). All webhooks ✅ confirmed Mar 14 after v2026.3.13.
137. **Discord @mentions require `<@USER_ID>` format (REG-026, Mar 12 2026):** Plain `@Name` does NOT ping in Discord. Must use `<@779143499655151646>` style with numeric user ID. IDs in TOOLS.md for all agents + Guillermo.
138. **April missing `message` tool config (Mar 12 2026):** April's OpenClaw config lacks `message` tool in `agents.defaults.tools` array. Instruction sent to patch. Needed for Discord/Telegram sends.
139. **TOOLS.md + AGENTS.md over cap (Mar 12 2026):** TOOLS.md +900B, AGENTS.md +500B. Both need trim to meet project caps. Action: consolidate/archive to memory/refs/ where appropriate. Size check: `wc -c /data/workspace/TOOLS.md /data/workspace/AGENTS.md`.

140. **Standup v3.0 — webchat-native, Notion dropped (Mar 14 2026):** Notion task DB was the weakest link — extra sync points, API failures, friction. New flow: I send formatted review to webchat → Guillermo replies inline (1 done, 2 drop, etc.) → I process. Telegram as backup when mobile. Notion stays as docs hub only. Updated cron `bdb28765` and `memory/refs/standup-process.md`.

141. **Discord heartbeat goes in channels.discord.channels, NOT guilds.*.channels (Mar 13 2026):** The `heartbeat: true` flag belongs in `channels.discord.channels.{channelId}` (top-level), not inside `channels.discord.guilds.*.channels.*`. Putting it in guilds causes 'Unrecognized key: heartbeat' error. Structure: top-level channels = name/heartbeat; guilds.channels = allow/requireMention.
141. **Heartbeat target config location CORRECTED (Mar 13 2026):** Heartbeat destination goes in `agents.defaults.heartbeat.target` + `agents.defaults.heartbeat.to`, NOT in Discord channel config. There is NO `heartbeat` key in `channels.discord.guilds.*.channels.*` OR `channels.discord.channels`. Schema: `agents.defaults.heartbeat: {every, model, target: "discord", to: "<channel_id>"}`. Always use gateway config.schema.lookup before guessing config structure.
142. **Email check format locked in (Mar 13 2026):** One line per email, max 5 items, state WHAT is needed (not "replied"). ⚠️ = action today, 📧 = FYI. Silent if nothing important — no "all clear" spam. Skip newsletters/promos/Google alerts. Cron: `25bd223c-78d0-428f-b0d3-f8dd5f959d02`. Full spec: `memory/refs/notification-formats.md`.
143. **Morning briefing v3.3 FINAL approved (Mar 13 2026):** Bold headers, full readable descriptions, no truncation. Calendar max 3 events vertical list. Noise filters: Mayleen, Mie, helpers, school events, focus/busy blocks. Cron now `sessionTarget: isolated` + `wakeMode: now`. Commits: `b713fc0c`, `1bb6336a`. Spec: `memory/refs/notification-formats.md`.
144. **`agents.defaults.tools` NOT a valid schema path (Mar 13 2026):** Gateway rejects this path on config apply. Do not use it. Configure tool access at the provider/agent level directly — not via `agents.defaults.tools`.
145. **Bot-to-bot Discord requires `allowBots: true` (Mar 13 2026):** Default `allowBots: false` silently drops bot messages. Each receiving agent needs `channels.discord.allowBots: true`. Directives to patch all agents: `/data/shared/pending-directives/{agent}/patch-discord-allowbots.sh`.
146. **Startup directives must patch JSON directly (Mar 13 2026):** `openclaw config set` fails silently in startup directives — CLI runs before gateway starts. Patch `config.json` directly via Python/jq instead.
147. **Discord bot-to-bot messaging — `allowBots: true` required (Mar 13 2026):** Each receiving agent needs `channels.discord.allowBots: true`. Directives at `/data/shared/pending-directives/{raphael,leonardo,april}/patch-discord-allowbots.sh` (Python JSON patch, not CLI). Redeployments triggered via API.
148. **April `tools.allow` restriction causes raw XML output (Mar 14 2026):** If `tools.allow: ["message"]` (or any restrictive list) is set in agent config, the agent is blocked from all other tools and outputs raw `<function_calls>` XML to the channel instead of executing. Fix: remove `tools.allow` entirely to grant full profile access. WhatsApp rate limit (428): add `debounceMs: 3000` to WhatsApp channel config.
149. **Standup cron `delivery.mode: "none"` required (Mar 14 2026):** Cron job `bdb28765` was sending a second message to Guillermo with "STANDUP_SENT" diagnostics. Cause: `delivery.mode: "announce"` forwards agent run summary to user. Fix: `delivery.mode: "none"`. Rule: any standup/notification cron that sends via message tool must have `delivery.mode: "none"` to avoid duplicate/internal messages leaking.
150. **Standup task ownership — show ALL, mark correctly (Mar 14 2026):** Don't filter tasks by owner before displaying. Show all overdue/due tasks but mark ownership: 😊 = Guillermo's task, 🦎 = Molty's task, 🔴 = Raphael, 🔵 = Leonardo. Never show Guillermo's personal tasks with 🦎 agent emoji.
151. **Memory retrieval failure — search ALL locations (Mar 14 2026):** When claiming "I don't think I did X", ALWAYS check docs/, plans/, logs/ before returning. Claimed I hadn't done a Todoist productivity audit — but it WAS in docs/ as `PRODUCTIVITY-FRAMEWORK-AUDIT-2026-03-13.md`. Root cause: memory_search only found memory/ files. Fix: Check docs/ folder and citation patterns before giving up. This is why TODO.md exists — to prevent "I forgot I did that" failures.
152. **Fleet update deployment process (Mar 14 2026):** Template repo `gginesta/clawdbot-railway-template` (main branch). Push to main → Railway auto-rebuilds all 4 agents (~5-8 min). Do NOT use `openclaw update` or `gateway update.run` on Railway (read-only filesystem). Full process: `memory/refs/fleet-updates.md`.
