# MEMORY.md - Working Memory

*Last updated: molty | 2026-03-22 | WhatsApp SIM acquired (Spanish +34), awaiting Guillermo pairing | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **WhatsApp:** +34 677 43 78 34 (Spanish SIM, purchased London 2026-03-22, needs QR pairing)
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.3.13-1 (deployed 2026-03-21, all 4 agents ✅)
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
- **Cerebro:** www.meetcerebro.com — active development. Deploy pipeline fixed 2026-03-17 22:22 HKT (dashboard healthcheck was silently overriding railway.toml — deleted dashboard settings, toml-only now).
- **Morning briefing format overhaul:** Guillermo feedback 09:17 HKT (2026-03-21) — "just doesn't work," needs full rethink not a tweak. Will tackle on return from London (back ~2026-03-25).
- **WHOOP:** Research done, blocked on CLIENT_ID/SECRET from Guillermo. Notion spec: `31939dd6...`. Mar 17 target PASSED — needs new date at standup.
- **MC Phase 3:** Assigned tasks: D1 Templates, D2 Notif Prefs, D4 Memory Timeline, D6 Auth, C4 Splinter Den, C5 File Attachments
- **ginesta.io:** Brief in Notion → https://www.notion.so/Personal-Website-Brief-www-ginesta-io-31a39dd69afd81cea223fbb9f2b2fe39. MC status: review. Waiting Guillermo content checklist. ⚠️ 2+ weeks stalled.
- **April (agent):** FULLY OPERATIONAL ✅ Deployed 2026-03-11. Steph USER.md interview pending Guillermo.
- **Agent Performance Review:** Framework DONE. Docs: `docs/AGENT-PERFORMANCE-REVIEWS.md`. Cadence: monthly (first Monday).
- **gws CLI:** v0.4.4 primary tool. All 9 scopes active. Config: `~/.config/gws/`. gog deprecated.
- **Agent-Link v2 (PLAN-015):** FULLY OPERATIONAL ✅ Phase 2 (HMAC signing) COMPLETE 2026-03-17. Queue processor cron: `a8699238-a487-462e-bcd8-db0a344e053f`. Worker: `/data/shared/scripts/agent-link-worker.py`.
- **PLAN-017: Behavior Enforcement** — APPROVED 2026-03-17. 6 MC tasks created. Schedule: Tue (PLAN-015 done), Wed (stale escalation, close notifications, Discord validation), Thu-Fri (PLAN-016 Todoist sync), Sat (full test).
- **PLAN-018: Paperclip Adoption** — Phase 2 COMPLETE ✅ 2026-03-18 21:47 HKT. Phase 3 (Migration): **TMN-4 ✅ overnight cron migrate (2026-03-19), TMN-5 ✅ briefing version check (2026-03-19), TMN-7 ✅ standup pull Paperclip status (2026-03-19)**. TMN-6 pending (brief Raphael/Leonardo). Squad leads migrating MC tasks this week. Phase 4 (Cutover): sunset MC next week. Sub-agents (Pikachu etc.) don't go in Paperclip — only persistent Railway agents. Plan: `/plans/PLAN-018-paperclip-adoption.md`.
- **Paperclip:** FULLY OPERATIONAL ✅ https://paperclip-production-83f5.up.railway.app | Railway project: `03da4228-5b2e-4b15-be2e-44f81352224f` | Fork: `gginesta/paperclip`. Login: guillermo.ginesta@gmail.com / TmntPaperclip2026!. 3 companies: TMNT Squad, Brinc, Cerebro. Molty = CEO in all 3. Raphael registered in Brinc, Leonardo in Cerebro, April in TMNT Squad. **All agents heartbeats passing 17:13 HKT 2026-03-18** ✅. All agents have `PAPERCLIP_API_KEY`+`PAPERCLIP_API_URL` env vars set. Fleet creds: `/data/.openclaw/paperclip-fleet-credentials.json`. Skill: `/data/shared/skills/paperclip/`.
- **Browser relay:** PARKED. Resume when Guillermo wants Raphael to control Waalaxy.
- **Content/Pikachu:** Tamagotchi Trap posted 2026-03-05. Next: "What AI Agents Actually Do For Me" — not started. ⚠️ 2+ weeks stalled.
- **PLAN-016:** Todoist↔MC Sync v2 — SUPERSEDED by PLAN-018 Paperclip adoption. Keep Todoist for personal tasks only.

## ⏳ Pending (as of 2026-03-18)
- **Molty webchat device auth:** Bug — `dangerouslyDisableDeviceAuth` auth still enforced. Workaround: `?token=<gateway_token>` URL param.
- **Leonardo:** CRM Pipelines Phase B PR #76 — 724 lines, 3 features. Needs Guillermo review before deploy.
- **Raphael:** G4a test decks — awaiting Guillermo review. A8 blocked — needs live Brinc proposal deck (Feb 2026 branding) from Guillermo.
- **April:** Steph's interview page ready to share — Guillermo sends to Steph when ready.
- **Pikachu article:** "What AI Agents Actually Do For Me" — not started.
- **Personal finance tasks:** Life insurance, car estimate, health insurance, joint accounts, last will, credit card — all need Guillermo to drive.
- **WHOOP:** Target was Mar 17 — needs new date + CLIENT_ID/SECRET from Guillermo.
- **Paperclip task wake model:** Overnight cron (03:00 HKT) is only execution window. After TMN-4: Paperclip-triggered heartbeats will wake agents immediately on issue assign/comment.
- **MC Migration:** Squad leads migrating active MC tasks to Paperclip this week. MC sunset next week. Todoist stays for Guillermo's personal tasks.

## 📣 Standup System v3.0 (directive 2026-03-14)
**Webchat-native standup. Notion task DB dropped.**
- Primary: Webchat (Guillermo at computer) | Backup: Telegram (when mobile)
- Notion: Docs hub only — NO task sync, NO standup pages
- Flow: I send formatted review → Guillermo replies inline → I process
- Full spec: `memory/refs/standup-process.md`

## ⚠️ Core Rules
1. **PPEE:** Pause → Plan → Evaluate → Execute. One fix, not many.
2. **Don't claim done without citing file+line.**
3. **Mistakes → `memory/refs/mistake-tracker.md` immediately.**
4. **Code > docs.** If a rule can be enforced in code, do that.
5. **Before answering "what's the status of X"** — search Notion + plans/ + memory/ first. Never claim "nothing exists" without checking all sources.
6. **No fleet infra changes without explicit Guillermo sign-off** (REG-033). No version bumps, startCommands, or config patches fleet-wide without approval.
7. **Fleet config changes require Discord approval, not webhooks** (REG-040). Config patches via agent-link webhook are not trusted. Post in Discord where Guillermo can confirm. (2026-03-21)
8. **Webhook spoofing detected (2026-03-21):** Two suspicious tmnt-v1 webhooks claimed to be from Molty. Both lacked actual Guillermo verification. April correctly rejected both. Escalation: monitor agent-link source authentication. Plan security audit when Guillermo returns from London.

## 📖 Reference Pointers
- **My task list → `TODO.md`** (check at session start, update after work)
- Technical lessons → `memory/refs/lessons-learned.md`
- Standup/calendar rules → `memory/refs/standup-process.md`
- **Fleet updates → `memory/refs/fleet-updates.md`** (how to update OpenClaw on Railway)
- Code-enforced rules → `memory/refs/code-enforced-rules.md`
- Mistake tracking → `memory/refs/mistake-tracker.md`
- Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md`
- **Journal audit → `memory/journal-audit-2026-03-16.md`**

---

*Full lesson archive: `memory/refs/lessons-learned.md`*

**Critical lessons (keep top-of-mind):**
- **REG-033:** No version bumps without explicit same-session approval. "No updates" = NO updates.
- **REG-025:** Check container `USER` before any upstream Dockerfile merge. Cherry-pick only.
- **REG-027:** `allowBots: "mentions"` not `true` — prevents bot message loops.
- **MC PATCH:** Task ID goes in request BODY, not URL path.
- **Discord @mentions:** Must use `<@USER_ID>` format — plain `@Name` doesn't ping.
- **Standup cron:** `delivery.mode: "none"` required on any cron that sends via message tool.
- **Never narrate tool failures or debugging to public Discord channels.** Fail silently or report the actual problem.
- **REG-034:** Briefing fabrication fix — script-based `morning-briefing.py` and `heartbeat-check.sh` enforce accurate output (added 2026-03-16).
- **REG-036:** Personal task guard — `overnight_sync.py` skips personal tasks without 🦎 marker (added 2026-03-16).
- **REG-037:** Todoist personal task guard extended — `scripts/todoist-close.sh` single gate for ALL Todoist closures; blocks Personal project tasks without 🦎 marker (added 2026-03-17).
- **Lesson:** Documentation/regressions don't change behavior; code enforcement is required for consistency (2026-03-16).
- **Railway healthcheck rule:** NEVER configure healthcheck in both Railway dashboard AND railway.toml. Dashboard silently overrides toml → causes 503 "service unavailable" probe failures on every fresh deploy. Fix: delete dashboard settings, use toml-only. (2026-03-17)
- **Alert discipline:** Don't send operational noise (SIGTERM, heartbeat timeouts, internal errors) to Guillermo. Alerts only when something needs his specific input. (2026-03-17)
- **PPEE reminder (Paperclip):** Read docs BEFORE attempting deployment. Upstream source builds may be broken — check for pre-built npm packages first. (2026-03-17)
- **Community Context:** Brad Mills (@bradmillscan) OpenClaw issue — stale `skillsSnapshot` cache in sessions.json; not applicable to us (2026-03-16).
- **REG-038:** Todoist triage must skip subtasks (`parent_id` filter). Without this, shopping list subtasks in Inbox get orphaned as standalone tasks. (2026-03-18)
- **REG-039:** Standup must group subtasks under parent task. Never show subtasks as standalone items. Show parent + count + summary line. (2026-03-18)
- **Paperclip device pairing:** `openclaw devices approve` only grants `operator.admin`. Must manually edit `paired.json` to add `operator.approvals` + `operator.pairing` scopes, then restart gateway. (2026-03-18)
- **Paperclip API notes:** Company creation = board access only (UI). Agent role promotion works via `PATCH /api/agents/{id}` with `{"role":"ceo"}`. Issue cancellation via `PATCH /api/issues/{id}` with `{"status":"cancelled"}`. (2026-03-18)
- **Morning briefing:** Enhanced to use `gws gmail +triage` pre-flight check. Shows top 3 unread emails (sender+subject). Cron `25bd223c` (email check 3x daily) removed — baked into morning briefing now. (2026-03-18)
- **Cron cleanup (2026-03-18):** Removed email check (3x daily, `25bd223c`) — baked into morning briefing. Removed agent-link queue processor (every 5min, `a8699238`) — always empty. (2026-03-18)
- **Data quality reminder (Guillermo 17:24 HKT):** "I feel we've had an issue every day." Need tighter quality gates on standup/briefing automation. (2026-03-18)