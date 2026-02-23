# MEMORY.md - Long-Term Memory

*Last updated: 2026-02-20*

---

## 👤 Guillermo

- **Location:** Hong Kong (GMT+8) — **ALWAYS think in HKT!**
- **Telegram:** @gginesta (id: 1097408992)
- **Email:** guillermo.ginesta@gmail.com
- **Mobile:** +852 5405 5953
- **Discord:** 779143499655151646
- **Style:** Casual, efficient, no fluff. Likes tables. Not super technical but learns fast.
- **Travelling:** Cebu Feb 13-18, back HK Feb 19

## 📧 Email & Google Workspace

### gog CLI (primary tool)
| What | Value |
|------|-------|
| CLI | `gog` (v0.11.0) — Google Workspace CLI |
| Account | `ggv.molt@gmail.com` |
| Keyring | `GOG_KEYRING_PASSWORD="molty2026"` |
| Services | gmail, calendar, drive, docs, sheets, contacts, tasks, chat, forms, slides |

### Google Access Strategy
| Service | How | Notes |
|---------|-----|-------|
| **Gmail** | `gog gmail` on ggv.molt | Guillermo CCs Molty on relevant emails |
| **Calendar** | Service account (R/W all calendars) | Full access to Personal, Family, Brinc calendars |
| **Contacts** | Pull from calendar event attendees | Can also invite ggv.molt to events for attendee details |
| **Drive** | Shared folder (TBD) | Will set up when needed |
| **guillermo.ginesta OAuth** | On standby | Same gog auth flow if needed later |

### Email Rules
- **TO** = reply if relevant
- **CC** = don't reply unless necessary  
- **BCC** = NEVER reply

### Legacy (deprecated)
- `gmail.sh` script still exists but superseded by `gog` CLI
- Morning briefing uses `gog gmail messages search` since Feb 19

---

## 🖥️ Infrastructure

### Agents
| Agent | URL | Status |
|-------|-----|--------|
| Molty 🦎 | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | leonardo-production.up.railway.app | ✅ Active |

### Key Config
- **OpenClaw version:** 2026.2.21 (upgraded Feb 22; code live on disk, Railway redeploy pending for all agents)
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
50. **Browser stale lock files:** Brave refuses to start after container redeploy because `SingletonLock`/`SingletonSocket`/`SingletonCookie` persist on the Railway volume from the previous container. **Permanent fix:** Dockerfile now runs `/usr/local/bin/startup.sh` which clears all browser profile lock files before starting supervisord (committed f0f39aa, Feb 22). Manual fix: `rm -f /data/.openclaw/browser/*/user-data/Singleton*`.
51. **Anthropic is a built-in provider:** No `models.providers.anthropic` block needed. Just `auth.profiles.anthropic:default` with `mode: "token"`.
52. **Sonnet 4.6 replaces Opus 4.6 as primary:** 5x cheaper, 1M context, faster, wins on agentic benchmarks. Switched fleet-wide Feb 20.
53. **All cron/heartbeat on direct Anthropic Haiku:** `anthropic/claude-3-5-haiku-latest` — uses Max plan daily allowance, not OpenRouter credits.54. **Calendar ownership rule:** NEVER put Molty tasks on Guillermo's calendar. Only tasks requiring Guillermo's time.
55. **ggv.molt@gmail.com / GCP project reinstated (Feb 22).** Appeal succeeded — project `molty-assistant-486411` reinstated. `gog` binary reinstalled to `/usr/local/bin/gog`. Keyring tokens backed up to `/data/workspace/credentials/gogcli-keyring/`. Morning briefing script now self-heals: auto-installs gog + restores keyring on container restart.
56. **`gateway restart` reloads config only, not binary.** Full Railway redeploy required for OpenClaw version upgrades.
57. **Dockerfile `OPENCLAW_GIT_REF` arg** controls which OpenClaw version gets installed. Always update when upgrading.
58. **Latest OpenClaw tag is v2026.2.21** (upgraded Feb 22). Template Dockerfile updated. Railway redeploy needed to activate on running containers.
59. **Railway API deploy permissions:** Workspace token needs correct mutation scope for `serviceInstanceRedeploy`. Currently returns "Not Authorized"—investigate.
60. **Shared credentials rule:** All credentials that need to reach multiple agents go in `/data/shared/credentials/` from day one. Agents read from there at startup — no distribution step needed. Webhooks deliver messages, they don't execute file writes. Never design a "Molty pushes token → agent writes file" flow again. (Lesson from MC token distribution pain, Feb 23 2026.)

---

## 🖥️ Hosting Decision (Feb 23, 2026)

- **Staying on Railway** — persistence, simplicity, fleet managed by Molty. Not worth the migration overhead.
- **DO App Platform explored** — cheaper only if trimming to 2GB RAM per agent. Ephemeral containers need Spaces backup layer. Ruled out for now.
- **Mac Mini floated** — Guillermo interested in getting Molty a Mac Mini. M4 24GB (~$799) would host full TMNT fleet, break-even ~6-7 months vs Railway. Local LLMs possible. **Revisit when timing is right.**

---

## 🐢 Mission Control (Feb 23, 2026)

- **Live:** https://tmnt-mission-control.vercel.app
- **Repo:** github.com/gginesta/tmnt-mission-control (private)
- **Tech:** NextJS 14 + Convex + Vercel (all free tier, $0/month)
- **Convex:** dev:resilient-chinchilla-241 | Team: guillermo-ginesta
- **HTTP API:** https://resilient-chinchilla-241.convex.site
- **API Key:** In Convex env `MC_API_KEY` + skill SKILL.md
- **Phase 1+2+3 complete.** 11 screens, 12 API endpoints, auth + middleware
- **Screens:** Dojo, War Room (kanban + comments), Sewer (activity + sub-agents), Tracker (health bar), Calendar (swim lanes), Vault (memory browser)
- **Placeholders:** Pizza Tracker (metrics), Splinter's Den (settings)
- **Heartbeat:** Cron `46d1ca32` every 2h (Haiku), pings MC `/api/heartbeat` + syncs daily memory to Vault
- **Daily Standup:** Cron `62aaf754` at 08:00 HKT (Haiku), queries MC tasks, compiles standup
- **Skill:** `/data/workspace/skills/mission-control/SKILL.md` + `/data/shared/skills/mission-control/`
- **Docs:** `docs/mission-control/` — SPEC.md, STATUS.md, BUILD-LOG.md, PHASE2-PLAN.md, PHASE3-PLAN.md
- **Molty owns the build.** Guillermo reviews product/UX. Todoist stays as personal tool.

---

## 🧠 Cerebro Project

- **Repo:** `gginesta/cerebro` (private GitHub), v1.0.0, 19 features complete
- **Live:** www.meetcerebro.com — Railway project `efcddaea-6972-...`, service `456f8881-8927-...`, env `cb8a3105-90b5-...`
- **Tech:** React+TS+Tailwind / Node+Express / Railway Postgres / Gemini OCR / xAI Grok / Stripe / Cloudinary / Resend

### Critical Issues (Feb 20)
1. **Live site: white page** — SPA loads but nothing renders. API healthy (200ms). Needs browser console debug.
2. **Missing prod env vars:** STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, GEMINI_API_KEY, Stripe price IDs.
3. **DB ambiguity:** .env references Neon; prod uses Railway Postgres. Schema parity unconfirmed.

### Plans
- **Dev plan:** `/data/shared/cerebro/CEREBRO-DEVELOPMENT-PLAN.md` (3 workstreams: A=Molty/unblock, B=Leonardo+Codex/polish, C=Guillermo+Raphael/sell)
- **Codex plan:** `/data/shared/cerebro/CODEX-INTEGRATION-PLAN.md` (GitHub issues → Codex execution → auto-deploy)
- **Target:** 10 paying customers in 12 weeks

### Files
- **Local:** `/data/shared/cerebro/meetcerebro/` (Syncthing copy, no git history)
