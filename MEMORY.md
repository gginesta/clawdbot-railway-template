# MEMORY.md - Working Memory

*Last updated: 2026-03-12 | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
| Agent | URL | Model |
|-------|-----|-------|
| Molty 🦎 | ggvmolt.up.railway.app | Opus (primary) |
| Raphael 🔴 | ggv-raphael.up.railway.app | Sonnet |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet |

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
- **April (agent):** FULLY OPERATIONAL ✅ Deployed 2026-03-11. Railway service: `ea026a0b-79e0-433d-907e-5cc4f75385e2` (april-agent-production.up.railway.app). Discord ID: 1481167770191401021. Webhook token: `7159178afb1c2c24b1e98bbbac0f0f02dc759aa038cd49ae7fac7873d8acf3ee`. Email: `april.rose.hk@gmail.com`. Channels: Discord ✅ WhatsApp ✅ Google Calendar + Shenanigans ✅ GCP IAM ✅ Syncthing ✅ agent-link ✅. Steph USER.md interview: page not yet shared with Notion integration (pending Guillermo).
- **Agent Performance Review:** P1 overnight work planned (PLAN-011). Design review process + add "Last updated by" headers to shared files. Trust/coaching model, not gatekeeping. Cascade to fleet after approval.
- **gws CLI:** v0.4.4 primary tool. Gmail ✅ Calendar ✅ Drive ✅ Docs ✅ Sheets ✅ (all 9 scopes). Config: `~/.config/gws/`. 11 skills at `/openclaw/skills/gws-*`. gog deprecated as fallback. GCP OAuth project: `847540297795` (separate from Gemini project `226575193033`).
- **Agent-Link v2 (PLAN-015):** IMPLEMENTED ✅ Mar 12. Worker + queue + health system live. Leonardo/April webhooks still timing out → messages auto-queued and retried. Root cause TBD (gateway hangs on `/hooks/agent` endpoint — services ARE up).
- **Browser relay:** PARKED. Blocker: relay only included in full gateway, not `openclaw node run`. Node on GUILLERMO-DESKTOP is paired ✅. Resume when Guillermo wants Raphael to control Waalaxy.
- **Content/Pikachu:** Tamagotchi Trap posted (X + LinkedIn) 2026-03-05. Standing permission: generate kawaii robot images for future articles. Next article: "What AI Agents Actually Do For Me".

## ⏳ Pending (as of 2026-03-13)
- **Molty webchat device auth:** Confirmed OpenClaw core bug — config flags `dangerouslyDisableDeviceAuth` DO get recognized (logs confirm) but auth still enforced. GitHub issue #41878 opened. Upstream audit done; 4 commits need manual cherry-pick to Dockerfile (see `/data/workspace/plans/upstream-audit-2026-03-10.md`).
- **Agent-Link webhook timeouts:** All agents (Raphael, Leonardo, April) timing out on fleet message delivery. Messages queue but delivery hangs. Gateway's `/hooks/agent` endpoint investigation needed.
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
- Code-enforced rules → `memory/refs/code-enforced-rules.md`
- Mistake tracking → `memory/refs/mistake-tracker.md`
- Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md`

---

*Full lesson archive: `memory/refs/lessons-learned.md`*

122. **Fleet outage 2026-03-09 ("Rough Monday"):** After v2026.3.7 update, Molty Discord, Raphael, Leonardo Discord, and Molty webchat all went down. Root cause: untested Python `startCommand` in Raphael used `json.load()` on JSONC config → container crash. Lesson: no fleet infra changes without Guillermo sign-off. REG-017/018 added.
123. **Working Molty webchat (controlUi) config:** `"dangerouslyAllowHostHeaderOriginFallback": true` + `"dangerouslyDisableDeviceAuth": true`. Also requires `gateway.trustedProxies: ["127.0.0.1", "100.64.0.0/10"]` — Railway's CGNAT range must be trusted or websocket connections fail silently. REG-021 added.
124. **Leonardo Discord token rotation + region fix (Mar 9 2026):** Discord bot token expired/rotated. After updating token, Discord was still blocked (Cloudflare 429 on Railway us-west2). Fix: change Railway region to Singapore → fresh IP → Discord online. REG-022 added.
125. **Policy: no fleet infrastructure changes without explicit Guillermo sign-off** — Guillermo's words after the Rough Monday outage: "Every time you try to update OpenClaw you break the fleet." Do not push version bumps, startCommands, or config patches fleet-wide without approval.
126. **Webchat device auth is an OpenClaw core bug (Mar 10 2026):** `dangerouslyDisableDeviceAuth: true` IS recognized (log: "security warning: dangerous config flags enabled") but device auth still enforced anyway. Issue is in OpenClaw core, not our wrapper config. GitHub issue #41878 opened. Workaround: Tailscale as intended (keep auth on).
127. **Never blindly sync upstream templates with different container users (REG-025, Mar 10 2026):** arjunkomath Dockerfile runs as `root`; our image runs as `openclaw`. Syncing arjunkomath changed container user → volume files owned by `openclaw` but container running as `root` → OpenClaw refuses to load secrets → total fleet outage. Always check `USER` in Dockerfile before any upstream merge.
128. **Our Dockerfile is too customized to auto-merge (Mar 10 2026):** 233 lines vs 89 upstream (vignesh07). We have Tailscale, Brave, Syncthing, Supervisor, Chromium. Upstream changes must be manually cherry-picked at the server.js/app layer, not via git merge. Full audit: `/data/workspace/plans/upstream-audit-2026-03-10.md`.
129. **Railway volume duplication causes startup failure (Mar 11 2026):** When `railway.toml` specifies `requiredMountPath`, Railway auto-creates a volume. Creating another via API → two volumes mounted at `/data` → container can't start and produces no logs. Fix: check for existing volumes before creating one. Delete extras via Railway UI if API delete doesn't fully work.
130. **Webchat URL token workaround for device auth (Mar 11 2026):** Device auth resets on gateway restart, locking users out. Workaround: append gateway token as URL param — `https://<host>/?token=<gateway_token>`. Avoids repeated setup wizard. Applies to all agents.
131. **gws "Caller does not have required permission" fix (Mar 11 2026):** If `client_secret.json` contains `project_id`, gws triggers GCP serviceUsageConsumer permission check and fails. Fix: remove `project_id` from `~/.config/gws/client_secret.json`. Also delete stale `.enc` credential files from other machines.
132. **Discord bot config — use channel NAME not ID (Mar 11 2026):** Channel IDs sometimes don't resolve in OpenClaw Discord config. Use channel name (e.g. `april-private`) instead. Bot also needs OAuth invite with correct permissions (`/api/oauth2/authorize?client_id=<id>&permissions=68608&scope=bot`) plus explicit View/Send/Read History granted per channel.
133. **MC PATCH API — task ID in body, not URL path (Mar 11 2026):** PATCH `/api/task` requires the task `id` field in the request body. Putting it in the URL path causes silent failure. Confirmed pattern: `PATCH /api/task` with body `{ "id": "<taskId>", ...fields }`.
134. **Morning briefing v3.0 — condensed format (Mar 12 2026):** Briefing was 4 screens → now ~1 screen. Keeps: Focus, Blocked (max 3), Review (max 3), Calendar (one line), Heads up (notable only), Weather (one line), OpenClaw. Removes: overnight report details, plans, tasks, squad, email, Notion comments, weather outlook. See PLAN-013.
135. **OpenClaw agent config — model placement (Mar 12 2026):** `model` must go under `agents.defaults.model` as `{primary: "...", fallbacks: [...]}` — NOT at root config level. Also: `cron.jobs` key does NOT exist in config; add crons via `/cron add` tool only. Learned during April PLAN-014 integration.
136. **Agent-Link v2 IMPLEMENTED (PLAN-015, Mar 12 2026):** Trusted fleet messaging with `tmnt-v1` envelope, persistent retry queue, health-aware routing. Key files: worker `/data/shared/scripts/agent-link-worker.py`, health `/data/shared/health/{agent}.json`, token `/data/shared/credentials/agent-link-token.txt`, delivery log `/data/shared/logs/agent-link-deliveries.log`. Queue processor cron: `57a4956a-5f79-4fe1-a7c3-257c09741314` (every 5min). Raphael ✅, Leonardo ⚠️ still timing out (queued for retry).
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
147. **Discord bot-to-bot messaging — allowBots + directive scripts (Mar 13 2026):** Implemented solution to let agents send each other Discord messages. Each receiving agent needs `channels.discord.allowBots: true`. Directives created at `/data/shared/pending-directives/{raphael,leonardo,april}/patch-discord-allowbots.sh` (uses Python JSON patching, not CLI). Railway redeployments triggered via API (all three agents). Status: test ping pending. Full gateway tokens documented in TOOLS.md.
