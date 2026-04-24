# MEMORY.md - Working Memory

*Last updated: molty | 2026-04-24 | Nightly curation: GPT-5.5 noted, Leonardo redeploy plan added | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **WhatsApp:** +34 677 43 78 34 (Spanish SIM, purchased London 2026-03-22, needs QR pairing)
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Location:** Back in Hong Kong (arrived Mar 31 from London trip).
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.4.21 (Dockerfile updated 2026-04-22, deployed via Railway)
| Agent | URL | Model |
|-------|-----|-------|
| Molty 🦎 | ggvmolt.up.railway.app | Anthropic Claude Sonnet 4.6 (subscription token) |
| Raphael 🔴 | ggv-raphael.up.railway.app | Anthropic Claude Sonnet 4.6 ✅ (v2026.4.21, confirmed 2026-04-23) |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet |
| April 🌸 | april-agent-production.up.railway.app | Sonnet |

**Primary:** `anthropic/claude-sonnet-4-6` (subscription token `sk-ant-oat01-...`)
**Fallbacks:** `openrouter/google/gemini-2.5-flash` → `openrouter/anthropic/claude-sonnet-4.6`
**Cron model:** xai/grok-3-fast | **Fallback:** grok-3-fast → grok-3

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
- **BuzzRounds:** Party games hub. Domain: `buzzrounds.com` (200 ✅). Tunes + YDKJ games. SSL certs fixed (TXT records added 2026-03-31). [verified: 2026-04-20]
- **Tunes:** Multiplayer music trivia. Repo: `gginesta/Tunes`. Railway project `658ca522`. Domain: `tunes.buzzrounds.com` (200 ✅). ⚠️ Railway service shows FAILED. Built by Guillermo + Claude Code. [verified: 2026-04-20]
- **YDKJ:** Trivia game. Repo: `gginesta/YDKJ`. Railway project `5cea0add`. Domain: `ydkj.buzzrounds.com` (200 ✅). [verified: 2026-04-20]
- **Mana Capital PE Autoresearch:** 6-round run completed. Winner: Pest Control Platform (14.2% Yr3 cash-on-cash). Thesis: `projects/mana-capital/pe-autoresearch/thesis.md`. Awaiting Guillermo review. [verified: 2026-04-03]
- **Cerebro:** www.meetcerebro.com (200 ✅) — active development. Leonardo owns board. ⚠️ Railway cerebro service shows FAILED. [verified: 2026-04-20]
- **Patagonia Land Search:** Phase 1-2 complete. Phase 3 (listings DB) pending. Notion page + `projects/patagonia-land/`. [verified: 2026-03-29]
- **Paperclip:** Operational (API 200 ✅). All agent tokens active. Fleet creds: `/data/.openclaw/paperclip-fleet-credentials.json`. [verified: 2026-04-20]

| Company | Agents | Notes |
|---------|--------|-------|
| TMNT Squad | Molty (CEO), April | |
| Brinc | Molty (CEO), Raphael (CTO) | BRI-44 blocked on Guillermo |
| Cerebro | Molty (CEO), Leonardo (CTO) | ~59 active issues |

## ✅ Completed (recent)
- PLAN-021, Autoresearch Skill, MC migration, Paperclip tokens, Fleet v2026.3.23-2 → archived
- **LLM Quota Resolved (2026-04-08):** Fleet-wide quota block resolved after April's backup ran at 21:01 HKT. Guillermo claimed $200 credit. Cron jobs should resume normally. [verified: 2026-04-08]

## 🅿️ Parked
- WHOOP, Browser relay (Waalaxy), MC Phase 3 sprint — all parked. [verified: 2026-04-20]

## ⏳ Pending
- **Fleet-wide exec block (2026-04-03):** All 4 agents lost shell exec access mid-day Apr 3. Molty exec now working ✅ (verified 2026-04-20). Other agents' status unknown (April/Leonardo Railway services FAILED). [verified: 2026-04-20]
- **Model Migration (2026-04-22→23):** Molty switched from Z.AI GLM-5.1 → **Anthropic Claude Sonnet 4.6** via subscription token. Z.AI being discontinued end of month. Raphael confirmed on Sonnet 4.6 ✅ (2026-04-23). April 404 (`Application not found`) since Apr 22 — needs redeploy. Leonardo still on old stack — needs update. [verified: 2026-04-24]
- **Leonardo Redeploy Plan (2026-04-24):** Agreed approach with Guillermo: (1) rotate all Apr 22 exposed env vars, (2) update `OPENCLAW_GIT_REF` to `v2026.4.21`, (3) set `OPENCLAW_PRIMARY_MODEL=anthropic/claude-sonnet-4-6` (or gpt-5.5 if Codex OAuth ready), (4) add fallback chain, (5) send startup briefing. Keys to rotate: `ANTHROPIC_TOKEN`, `DISCORD_BOT_TOKEN`, `NOTION_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `TAILSCALE_AUTHKEY`, `TELEGRAM_BOT_TOKEN`, `TODOIST_API_TOKEN`, `XAI_API_KEY`, `BRAVE_API_KEY`. Safe: `PAPERCLIP_API_KEY`, `SETUP_PASSWORD`. Full detail: `memory/2026-04-24.md`. [verified: 2026-04-24]
- **GPT-5.5 (2026-04-24):** OpenAI released GPT-5.5 — available via `openai-codex/gpt-5.5` through Codex OAuth (needs ChatGPT Plus/Pro). Guillermo getting subscription. Test plan: Molty first → Leonardo. Key stats: 82.7% Terminal-Bench. [verified: 2026-04-24]
- **Webchat device auth:** Workaround: `?token=<gateway_token>`. Low priority. Unchanged. [verified: 2026-04-20]
- **April bot visibility (allowBots):** Needs gateway restart + config patch. Unchanged. [verified: 2026-04-20]
- **WhatsApp SIM:** +34 677 43 78 34. Needs QR pairing. Unchanged. [verified: 2026-04-20]
- **Upstream Template Audit (`vignesh07/clawdbot-railway-template`):** Fork behind upstream. 1 important commit to apply (NPM/PNPM persistence, `ec73de5` #139). Full audit: `/data/workspace/plans/dockerfile-rebase-audit.md`. [verified: 2026-04-20]
- **Fix Plan (OpenClaw Update):** ✅ DONE. Dockerfile bumped to v2026.4.21, pushed to `gginesta/clawdbot-railway-template`. Persistence ENV vars added. [resolved: 2026-04-22]

## 📣 Standup System v3.0
Webchat-native. Full spec: `memory/refs/standup-process.md`

## 🔑 Key Rotation (2026-04-22)
Accidental push of workspace repo to GitHub exposed API keys. All keys rotated:
- ✅ Railway, Notion, Vercel, GitHub, OpenRouter, xAI, Z.AI, Google/Gemini, Todoist, Namecheap, Discord bot token, Google SA JSON
- ✅ TOOLS.md scrubbed — all plaintext values replaced with `$ENV_VAR` references
- ✅ GitHub `master` branch (leak) deleted. `main` branch clean (no secrets in history)
- ✅ Dockerfile security fixes: `GOG_KEYRING_PASSWORD` now from env var, gws credential paths use globs (no hardcoded email)
- ⚠️ Anthropic token in `token` mode only (never `oauth`). See `memory/refs/credentials-reference.md`
- ⏳ Contact GitHub Support to GC dangling commit `7afb95aa`

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
- Task list → `TODO.md` | Fleet update SOP → `memory/refs/fleet-update-sop.md`
- Lessons → `memory/refs/lessons-learned.md` | Mistakes → `memory/refs/mistake-tracker.md`
- Standup → `memory/refs/standup-process.md` | Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md` | Code-enforced rules → `memory/refs/code-enforced-rules.md`
- **Credential isolation rules** → `memory/refs/credential-isolation.md` ⚠️ READ BEFORE ANY AGENT REDEPLOY

## Recent Lessons Learned
- **Empty webchat bubbles = auth failure (2026-04-23):** When model label shows but bubble is blank, check Anthropic token auth mode (`token` for `sk-ant-oat01-` keys).
- **Don't share Anthropic tokens across agents (2026-04-23):** Each agent needs their own token. Sharing caused empty responses.
- **GLM falls back to Chinese (2026-04-23):** If primary fails and GLM is in fallback chain, it responds in Chinese by default.
- **`openclaw doctor --fix` restores stale tokens (2026-04-23):** Always re-check Discord/Anthropic tokens after running it.
- **Railway Custom Domain Certs (2026-03-31)**: SSL validation requires BOTH a CNAME record and a TXT `_railway-verify.{subdomain}` record with a Railway-provided token. Just adding the CNAME is insufficient; cert issuance fails without the TXT record. (Source: /data/workspace/memory/2026-03-31.md)

## Brinc Updates (Updated 2026-04-03)
- **BRI-44:** 16 Gmail drafts staged since Mar 18 — blocked on Guillermo send confirmation.
- **BRI-53 APAC Lead Research:** Now at v4 (17 prospects across 4 batches). Latest: Korea batch (4 prospects). Files: `brinc/outreach/BRI-53-linkedin-outreach-sequences-v*.md`.
- **HARO:** First published comment Apr 2 (Website Builder Expert). Pipeline active.

## Infrastructure Issues
- **Fleet-wide exec block (Apr 3):** Molty exec working ✅. April/Leonardo status unknown (Railway FAILED). [verified: 2026-04-20]
- **Paperclip API Bug:** Cron sessions fail status updates ("Agent run id required"). Persists. [verified: 2026-04-03]
- **Apr 2 API degradation:** Anthropic API was slow/hanging, caused fleet-wide cron timeouts. All agents bumped timeouts to 600s as buffer. Resolved by Apr 3. [verified: 2026-04-03]
- **Leonardo MEMORY.md bloat:** Was 21KB, trimmed to 8.7KB. Root cause of his curation timeouts. [verified: 2026-04-03]
- **OpenClaw Update Issue (v2026.4.7):** Railway build cache not picking up `OPENCLAW_GIT_REF`. Pending cache-bust fix. [verified: 2026-04-20]
- **⚠️ FAILED Railway services (2026-04-20):** Tunes, april-agent, leonardo, cerebro all show FAILED. Domains still serve (200) for BuzzRounds and meetcerebro. Needs investigation. [verified: 2026-04-20]

---

*Full lesson archive: `memory/refs/lessons-learned.md` | All regressions: `REGRESSIONS.md`*

**Top-of-mind rules:**
- **REG-041:** Verify every pending item against source before reporting to Guillermo. No parroting MEMORY.md.
- **REG-033:** No version bumps without explicit same-session approval.
- **REG-034:** Briefings/heartbeats use scripts only — no fabricated data.
- **REG-036/037:** Never close Todoist personal tasks without 🦎. All closures via `todoist-close.sh`.
- **Alert discipline:** No operational noise to Guillermo. Alerts only when he needs to act.
- **Memory audit:** Weekly cron (Mon 10:00 HKT). Script: `scripts/memory-audit.py`. All pending items need `[verified: YYYY-MM-DD]`.