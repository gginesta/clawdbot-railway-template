# MEMORY.md - Working Memory

*Last updated: 2026-03-05 | Target: <4KB*

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
- **April (agent):** Deployment pending. Notion pages: Setup Qs `31939dd6-9afd-8197` (Guillermo filled ✅), Steph Interview `31939dd6-9afd-81c5` (ready to share, Guillermo will send), Planning notes `31939dd6-9afd-8119`. Channels: WhatsApp (new SIM), Google Calendar + Shenanigans. Voice: yes.
- **Agent Performance Review:** P1 overnight work planned (PLAN-011). Design review process + add "Last updated by" headers to shared files. Trust/coaching model, not gatekeeping. Cascade to fleet after approval.
- **gws CLI:** v0.4.4 primary tool. Gmail ✅ Calendar ✅ Drive ✅ Docs ✅ Sheets ✅ (all 9 scopes). Config: `~/.config/gws/`. 11 skills at `/openclaw/skills/gws-*`. gog deprecated as fallback.
- **Browser relay:** PARKED. Blocker: relay only included in full gateway, not `openclaw node run`. Node on GUILLERMO-DESKTOP is paired ✅. Resume when Guillermo wants Raphael to control Waalaxy.
- **Content/Pikachu:** Tamagotchi Trap posted (X + LinkedIn) 2026-03-05. Standing permission: generate kawaii robot images for future articles. Next article: "What AI Agents Actually Do For Me".

## ⏳ Pending (as of 2026-03-05)
- **Leonardo:** Config fix (`bind=loopback`, dm key) — directive sent, not yet confirmed applied
- **Raphael:** 16 Gmail drafts awaiting Guillermo review
- **Leonardo:** Beta invite list (20 names) pending
- **April:** Steph's interview page — Guillermo will send to Steph when ready

## 📣 Standup Delivery (directive 2026-03-05)
Send daily standup to **both** webchat AND Telegram going forward.
- Webchat: primary (Guillermo at computer)
- Telegram: backup (convenient on phone)

## ⚠️ Core Rules
1. **PPEE:** Pause → Plan → Evaluate → Execute. One fix, not many.
2. **Don't claim done without citing file+line.**
3. **Mistakes → `memory/refs/mistake-tracker.md` immediately.**
4. **Code > docs.** If a rule can be enforced in code, do that.
5. **Before answering "what's the status of X"** — search Notion + plans/ + memory/ first. Never claim "nothing exists" without checking all sources.

## 📖 Reference Pointers
- Technical lessons → `memory/refs/lessons-learned.md`
- Standup/calendar rules → `memory/refs/standup-process.md`
- Code-enforced rules → `memory/refs/code-enforced-rules.md`
- Mistake tracking → `memory/refs/mistake-tracker.md`
- Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md`

---

*Full lesson archive: `memory/refs/lessons-learned.md`*
