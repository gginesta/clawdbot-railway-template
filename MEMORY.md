# MEMORY.md - Working Memory

*Last updated: molty | 2026-03-29 | Autoresearch skill complete, TMN-12 closed, daily log created | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **WhatsApp:** +34 677 43 78 34 (Spanish SIM, purchased London 2026-03-22, needs QR pairing)
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.3.23-2 (deployed 2026-03-25, all 4 agents ✅)
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
- **Autoresearch Skill:** ✅ COMPLETE 2026-03-29. Self-improving OpenClaw prompt skill infrastructure. Karpathy-style scoring loop (sample → score → improve → iterate). Includes 3-phase SOP, gap patterns (137 lines), scoring rubric (64 lines), Python scorer (81 lines). Compiled to `skills/dist/autoresearch.skill`. [verified: 2026-03-29]
- **Patagonia Land Search:** Family compound project. Notion page: https://www.notion.so/Patagonia-Land-Search-Family-Compound-Project-33239dd69afd81dcbfdee6acbc2fee86. Local files: `projects/patagonia-land/`. Phase 1-2 complete (40+ sources, 9 regions analyzed). Top 3 regions: Coyhaique (practical), Lago General Carrera (best climate), Puerto Natales (best scenery). Guillermo is Chilean national = no DIFROL restrictions. Phase 3 next: populate listings DB. [verified: 2026-03-29]
- **BuzzRounds:** Party games hub. Domain: `buzzrounds.com` (Namecheap, bought 2026-03-28). Vercel project `prj_4lz2Cc50Ilao7XBEP9LA4dgmh6em`. Repo: `gginesta/buzzrounds`. Next.js 15 + TypeScript + Tailwind. DNS: `@` → Vercel, `www` → Vercel, `tunes` → `3s82uf9z.up.railway.app`. Jackbox-inspired concept — collection of multiplayer browser games. [verified: 2026-03-28]
- **Tunes (formerly Hitster):** Renamed 2026-03-28. Multiplayer music trivia game. **Built by Guillermo + Claude Code.** Repo: `gginesta/Tunes`. Railway project `658ca522`, service `2478865e`. Domains: `tunes.up.railway.app` + `tunes.buzzrounds.com` (custom domain SSL **PENDING** — see below). Spotify Web Playback SDK + PKCE OAuth. Auto-deploys from `main`. Tech: React 19/Vite/Zustand + Node/Express/Socket.io + SQLite. Volume `6fa153a6` at `/app/data`. 500+ songs, 4 game modes. CI auto-merge workflow updated to `claude/tunes-*` branch pattern (GitHub Actions). Env vars updated: `VITE_SERVER_URL` + `VITE_SPOTIFY_REDIRECT_URI` → `tunes.buzzrounds.com`. Full codebase rename: 32 files (commit `301ac19`), all `@hitster/*` → `@tunes/*`, type aliases, UI text, localStorage keys. Claude Code PR #18 done directly (timeouts/503s), PR left open — can close without merging. [verified: 2026-03-28]
- **YDKJ:** You Don't Know Jack-inspired trivia game (in development). Railway project `5cea0add` (no services deployed yet). Repo: `gginesta/YDKJ`. Will be at `ydkj.buzzrounds.com` when ready. [verified: 2026-03-28]
- **Cerebro:** www.meetcerebro.com — active development. Deploy pipeline fixed 2026-03-17. [verified: 2026-03-24]
- **Content pipeline:** Article #4 "What AI Agents Actually Do For Me" published 2026-03-24. X: https://x.com/gginesta/status/2036346565154029603 | LinkedIn published. [verified: 2026-03-24]
- **Morning briefing format overhaul:** Guillermo: "just doesn't work" (2026-03-21). Needs full rethink on return from London (~2026-03-25). [verified: 2026-03-24]
- **ginesta.io:** LIVE ✅ https://ginesta.io | Vercel project: ginesta-site | GitHub: gginesta/ginesta-io. Family landing page + /guillermo profile. [verified: 2026-03-24]
- **helmcl.com:** LIVE ✅ https://helmcl.com | Vercel project: helmcl. Helm Consulting placeholder. helmconsulting.io + helmconsultingltd.com redirect here. [verified: 2026-03-24]
- **Paperclip:** FULLY OPERATIONAL ✅ https://paperclip-production-83f5.up.railway.app. All agent tokens regenerated + deployed 2026-03-23. Fleet creds: `/data/.openclaw/paperclip-fleet-credentials.json`. [verified: 2026-03-24]
- **MC sunset:** COMPLETE ✅ Announced 2026-03-23. Paperclip = single source of truth for all task management.

| Company | Agents | Active Issues |
|---------|--------|--------------|
| TMNT Squad | Molty (CEO), April | 2 |
| Brinc | Molty (CEO), Raphael (CTO) | 1 (BRI-44 blocked) |
| Cerebro | Molty (CEO), Leonardo (CTO) | 21 (cleaned from 132) |

## ✅ Completed (archive candidates)
- **TMN-12 (Autoresearch Skill):** COMPLETE ✅ 2026-03-29. Built self-improving skill infrastructure with Karpathy-style scoring loop, gap patterns, and Python scorer. Compiled to dist binary. Foundation for scaling skill quality. [verified: 2026-03-29]
- **PLAN-021 (Agent-Link Security):** COMPLETE ✅ 2026-03-25. Discord-first trust model (webhooks = informational only, commands via Discord). All 3 agents adopted. Phase 1 (gateway HMAC) paused due to path resolution crash — needs Guillermo re-approval. Phase 2 research complete (clawctl evaluated, Discord trust model confirmed). [verified: 2026-03-25]
- **PLAN-018 + MC migration:** COMPLETE ✅ 2026-03-23. Cerebro board cleaned: 132→21 active issues (73 cancelled: duplicates, stale, phantom planning). Lesson: don't bulk-migrate without auditing staleness.
- **Fleet update to v2026.3.23-2:** 2026-03-25. All 4 agents verified SUCCESS via Railway API. SOP created: `memory/refs/fleet-update-sop.md`. [verified: 2026-03-25]
- **Paperclip token fix:** 2026-03-23. Root cause: wrong agent IDs + claim tokens stored during Mar 18 registration. Generated new keys via board session, deployed to Railway. All 6 tokens working.

## 🅿️ Parked
- **WHOOP:** No clear use case. Idea in Todoist. [verified: 2026-03-23]
- **Browser relay:** Parked. Resume when Guillermo wants Raphael on Waalaxy. [verified: 2026-03-23]
- **MC Phase 3 sprint:** D1 Templates, D2 Notif Prefs, D4 Memory Timeline, D6 Auth — may be superseded by Paperclip migration. Needs decision.

## ⏳ Pending [verified: 2026-03-28]
- **Custom domain SSL (tunes.buzzrounds.com):** Railway custom domain stuck on `CERTIFICATE_STATUS_TYPE_VALIDATING_OWNERSHIP`. Root cause: deleted + re-created domain to reset cert, Railway assigned NEW CNAME target `hkhjmdcx.up.railway.app` (was `3s82uf9z.up.railway.app`). Updated DNS. Waiting for propagation + cert issuance. Fallback: `tunes.up.railway.app` works fine. [verified: 2026-03-28]
- **Webchat device auth:** Bug — auth still enforced despite `dangerouslyDisableDeviceAuth`. Workaround: `?token=<gateway_token>`. Low priority. [verified: 2026-03-24]
- **April bot visibility (allowBots):** April cannot see bot-authored messages in Discord (allowBots defaults false). Fix: `config patch --json '{"channels":{"discord":{"allowBots":true}}}'`. Needs gateway restart. [verified: 2026-03-25]
- **WhatsApp SIM:** +34 677 43 78 34 (Spanish, purchased London 2026-03-22). Needs QR pairing when Guillermo is ready. [verified: 2026-03-24]

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
7. **Fleet commands go through Discord, not webhooks** (PLAN-021 v2, 2026-03-25). Discord bot IDs are unforgeable. Webhooks are for health/status only. Config changes still require Guillermo confirmation (REG-040).
8. **Webhook spoofing is solved by not using webhooks for commands** (2026-03-25). Old tmnt-v1 trust model replaced. Discord = trusted, webhooks = informational only.
9. **Don't manage other agents' boards.** Guillermo: "Leonardo owns Cerebro, not Molty." Respect domain ownership. (2026-03-23)
10. **Never post API tokens in Discord** — even private servers. Use direct env var updates or agent-link. (2026-03-23)

## 📖 Reference Pointers
- **My task list → `TODO.md`** (check at session start, update after work)
- **Fleet update SOP → `memory/refs/fleet-update-sop.md`** (mandatory checklist for version updates)
- Technical lessons → `memory/refs/lessons-learned.md`
- Standup/calendar rules → `memory/refs/standup-process.md`
- **Fleet updates → `memory/refs/fleet-updates.md`** (how to update OpenClaw on Railway)
- **Fleet update SOP → `memory/refs/fleet-update-sop.md`** (6-step checklist, mandatory verification)
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