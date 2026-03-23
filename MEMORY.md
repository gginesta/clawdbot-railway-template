# MEMORY.md - Working Memory

*Last updated: molty | 2026-03-23 | Full memory audit — purged stale items, added verification dates, REG-041 | Target: <15KB*

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
- **Cerebro:** www.meetcerebro.com — active development. Deploy pipeline fixed 2026-03-17. [verified: 2026-03-23]
- **Morning briefing format overhaul:** Guillermo: "just doesn't work" (2026-03-21). Needs full rethink on return from London (~2026-03-25). [verified: 2026-03-23]
- **ginesta.io:** Notion brief → https://www.notion.so/Personal-Website-Brief-www-ginesta-io-31a39dd69afd81cea223fbb9f2b2fe39. Guillermo wants to tackle today (2026-03-23). [verified: 2026-03-23]
- **PLAN-018: Paperclip Adoption** — Phases 0-2 DONE ✅. Phase 3 partially done (TMN-4,5,7 ✅). **Paperclip shows: "Migrate active MC tasks" still BLOCKED, "Fleet config management" IN_REVIEW.** TMN-6 (brief R/L) not done. Guillermo wants migration finished today. [verified: 2026-03-23]
- **Paperclip:** Running at https://paperclip-production-83f5.up.railway.app. 3 companies, all agents registered. Fleet creds: `/data/.openclaw/paperclip-fleet-credentials.json`. [verified: 2026-03-23]
- **Leonardo PR #76:** CLOSED (not merged) since 2026-03-14. Status unknown — may have been superseded. [verified: 2026-03-23]

## ✅ Completed (archive candidates)
- **April (agent):** FULLY OPERATIONAL ✅ Deployed 2026-03-11.
- **Agent-Link v2 (PLAN-015):** FULLY OPERATIONAL ✅ HMAC signing complete 2026-03-17. Queue processor cron removed (always empty).
- **Content/Pikachu:** "What AI Agents Actually Do For Me" — DONE ✅ https://www.notion.so/30b39dd69afd81c49baaf35c4ef1e269
- **Agent Performance Review:** Framework DONE. Docs: `docs/AGENT-PERFORMANCE-REVIEWS.md`.
- **gws CLI:** v0.4.4, 9 scopes active. gog deprecated.
- **PLAN-016:** SUPERSEDED by PLAN-018. Todoist for personal tasks only.
- **PLAN-017:** APPROVED but schedule (week of Mar 17) passed. Status unclear — needs audit. [verified: 2026-03-23]

## 🅿️ Parked
- **WHOOP:** No clear use case. Idea in Todoist. [verified: 2026-03-23]
- **Browser relay:** Parked. Resume when Guillermo wants Raphael on Waalaxy. [verified: 2026-03-23]
- **MC Phase 3 sprint:** D1 Templates, D2 Notif Prefs, D4 Memory Timeline, D6 Auth — may be superseded by Paperclip migration. Needs decision.

## ⏳ Pending [verified: 2026-03-23]
- **Webchat device auth:** Bug — auth still enforced despite `dangerouslyDisableDeviceAuth`. Workaround: `?token=<gateway_token>`. Low priority. [verified: 2026-03-23]
- **Webhook spoofing:** Two suspicious tmnt-v1 messages (2026-03-21). Security audit planned for Guillermo's return. [verified: 2026-03-23]
- **WhatsApp SIM:** +34 677 43 78 34 (Spanish, purchased London 2026-03-22). Needs QR pairing when Guillermo is ready. [verified: 2026-03-23]

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

*Full lesson archive: `memory/refs/lessons-learned.md` | All regressions: `REGRESSIONS.md`*

**Top-of-mind rules:**
- **REG-041:** Verify every pending item against source before reporting to Guillermo. No parroting MEMORY.md.
- **REG-033:** No version bumps without explicit same-session approval.
- **REG-034:** Briefings/heartbeats use scripts only — no fabricated data.
- **REG-036/037:** Never close Todoist personal tasks without 🦎. All closures via `todoist-close.sh`.
- **Alert discipline:** No operational noise to Guillermo. Alerts only when he needs to act.
- **Memory audit:** Weekly cron (Mon 10:00 HKT). Script: `scripts/memory-audit.py`. All pending items need `[verified: YYYY-MM-DD]`.