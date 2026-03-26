# MEMORY.md - Working Memory

*Last updated: molty | 2026-03-26 | Hitster CI auto-merge workflow, Spotify rate-limit fixes | Target: <15KB*

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
- **Hitster:** Multiplayer music trivia game. **Built by Guillermo + Claude Code.** Molty: deployment + minor improvements. Repo: `gginesta/Hitster`. Railway project `658ca522`, service `2478865e`, domain: `hitster.up.railway.app`. Spotify Web Playback SDK + PKCE OAuth. Auto-deploys from `main`. Tech: React 19/Vite/Zustand + Node/Express/Socket.io + SQLite. Volume `6fa153a6` at `/app/data` for persistence. 500+ songs, 4 game modes, preview mode (no Spotify), leaderboards, player stats, genre/decade/regional packs, fuzzy matching. Recent merges: autoplay unlock (green banner + global tap listener), turn timer top bar (commits `734dc47`, `edf005b`, `4dadad5`). **CI Auto-Merge:** Merged Spotify rate-limit fixes (merges 4-5, commits `72bd2d8`, `c36d32e`). Set up GitHub Actions workflow (`.github/workflows/auto-merge.yml`) to auto-merge any `claude/hitster-spotify-game-*` branch to `main` — eliminates need for manual Claude→main pushes (Claude's GitHub integration token lacks permissions). Commit `13f53d7`. [verified: 2026-03-26]
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
- **PLAN-021 (Agent-Link Security):** COMPLETE ✅ 2026-03-25. Discord-first trust model (webhooks = informational only, commands via Discord). All 3 agents adopted. Phase 1 (gateway HMAC) paused due to path resolution crash — needs Guillermo re-approval. Phase 2 research complete (clawctl evaluated, Discord trust model confirmed). [verified: 2026-03-25]
- **PLAN-018 + MC migration:** COMPLETE ✅ 2026-03-23. Cerebro board cleaned: 132→21 active issues (73 cancelled: duplicates, stale, phantom planning). Lesson: don't bulk-migrate without auditing staleness.
- **Fleet update to v2026.3.23-2:** 2026-03-25. All 4 agents verified SUCCESS via Railway API. SOP created: `memory/refs/fleet-update-sop.md`. [verified: 2026-03-25]
- **Paperclip token fix:** 2026-03-23. Root cause: wrong agent IDs + claim tokens stored during Mar 18 registration. Generated new keys via board session, deployed to Railway. All 6 tokens working.

## 🅿️ Parked
- **WHOOP:** No clear use case. Idea in Todoist. [verified: 2026-03-23]
- **Browser relay:** Parked. Resume when Guillermo wants Raphael on Waalaxy. [verified: 2026-03-23]
- **MC Phase 3 sprint:** D1 Templates, D2 Notif Prefs, D4 Memory Timeline, D6 Auth — may be superseded by Paperclip migration. Needs decision.

## ⏳ Pending [verified: 2026-03-25]
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