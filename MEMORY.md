# MEMORY.md - Working Memory

*Last updated: molty | 2026-04-26 | Nightly curation: Dockerfile+entrypoint fixed, cron ran OK | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **WhatsApp:** +34 677 43 78 34 (Spanish SIM, purchased London 2026-03-22, needs QR pairing)
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.4.21 running | Dockerfile bumped to v2026.4.23 (2026-04-25) — fleet rebuild pending
| Agent | URL | Model Chain | Status |
|-------|-----|-------------|--------|
| Molty 🦎 | ggvmolt.up.railway.app | Sonnet 4.6 → glm-5.1 → or-flash → or-sonnet | ✅ Live |
| Raphael 🔴 | ggv-raphael.up.railway.app | Sonnet 4.6 | ✅ v2026.4.21 |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet 4.6 → glm-5.1 → or-flash → or-sonnet | ✅ Rehabbed 2026-04-24 |
| April 🌸 | april-agent-production.up.railway.app | Sonnet 4.6 → glm-5.1 → or-flash → or-sonnet | ✅ Rehabbed 2026-04-24 |

**Primary:** `anthropic/claude-sonnet-4-6` (subscription token `sk-ant-oat01-...`)
**Fallbacks:** `zai/glm-5.1` → `openrouter/google/gemini-2.5-flash` → `openrouter/anthropic/claude-sonnet-4-6`
**Heartbeat model:** `xai/grok-3-fast` (fleet standard, all agents)

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
- **BuzzRounds:** Party games hub. Domain: `buzzrounds.com` (200 ✅). Tunes + YDKJ games. [verified: 2026-04-20]
- **Tunes:** Multiplayer music trivia. Repo: `gginesta/Tunes`. Railway project `658ca522`. Domain: `tunes.buzzrounds.com` (200 ✅). ⚠️ Railway service FAILED. [verified: 2026-04-20]
- **YDKJ:** Trivia game. Repo: `gginesta/YDKJ`. Railway project `5cea0add`. Domain: `ydkj.buzzrounds.com` (200 ✅). [verified: 2026-04-20]
- **Mana Capital PE Autoresearch:** 6-round run completed. Winner: Pest Control Platform (14.2% Yr3 cash-on-cash). Thesis: `projects/mana-capital/pe-autoresearch/thesis.md`. Awaiting Guillermo review. [verified: 2026-04-03]
- **Cerebro:** www.meetcerebro.com (200 ✅). Leonardo owns board. ⚠️ Railway cerebro service FAILED. CER-26 in_progress, CER-16 blocked. [verified: 2026-04-26]
- **Patagonia Land Search:** Phase 1-2 complete. Phase 3 (listings DB) pending. [verified: 2026-03-29]
- **Paperclip:** Operational (API 200 ✅). Fleet creds: `/data/.openclaw/paperclip-fleet-credentials.json`. [verified: 2026-04-20]

| Company | Agents | Notes |
|---------|--------|-------|
| TMNT Squad | Molty (CEO), April | |
| Brinc | Molty (CEO), Raphael (CTO) | BRI-44 blocked on Guillermo |
| Cerebro | Molty (CEO), Leonardo (CTO) | ~59 active issues |

## ✅ Completed (recent)
- **Fleet Rehab (2026-04-24):** April + Leonardo redeployed after ~1 month down. Configs updated: model chain standardised (Sonnet → glm-5.1 → or-flash → or-sonnet), heartbeat → xai/grok-3-fast, `dangerouslyAllowHostHeaderOriginFallback` added, hardcoded keys removed, version bumped to 2026.4.21. [done: 2026-04-24]
- **Railway API access restored (2026-04-26):** `RAILWAY_API_TOKEN` updated. `me {}` query blocked (project-scoped token) but `projects {}` works fine. Railway CLI reinstalled per session.
- **GitHub access restored (2026-04-26):** Token is `$GITHUB_API_TOKEN` (not `GITHUB_TOKEN`). Remote URL updated. Push working.
- PLAN-021, Autoresearch Skill, MC migration, Paperclip tokens → archived

## 🅿️ Parked
- WHOOP, Browser relay (Waalaxy), MC Phase 3 sprint — all parked. [verified: 2026-04-20]

## ⏳ Pending
- **Fleet v2026.4.23 rebuild:** Dockerfile bumped. Needs Railway redeploy for all 4 agents (Molty currently on 4.21 post-rebuild — cache issue). Key fixes in 4.23: webchat blank bubble fix, memory QMD repair, block streaming dupes. [2026-04-25]
- **Leonardo Anthropic + xAI tokens failing:** Empty responses — Anthropic and xAI keys in Railway may be wrong/stale. Currently running on glm-5.1 fallback. Needs key verification. [verified: 2026-04-24]
- **GPT-5.5:** Available via `openai-codex/gpt-5.5` (Codex OAuth, needs ChatGPT Plus/Pro). Guillermo getting subscription. [verified: 2026-04-24]
- **Webchat device auth:** Workaround: `?token=<gateway_token>`. Low priority. [verified: 2026-04-20]
- **WhatsApp SIM:** +34 677 43 78 34. Needs QR pairing. [verified: 2026-04-20]
- **Nightly memory curation cron:** Previously failing (3x timeout). `git safe.directory` fix added to `entrypoint.sh` (commit `3d319e1f`). Cron ran successfully 2026-04-26. Monitor for recurrence.

## 📣 Standup System v3.0
Webchat-native. Full spec: `memory/refs/standup-process.md`

## 🔑 Key Rotation (2026-04-22)
Accidental push exposed API keys — all rotated. TOOLS.md scrubbed. GitHub `master` branch deleted.
- ⚠️ Anthropic token: `token` mode only (never `oauth`). `sk-ant-oat01-` format.
- ⏳ Contact GitHub Support to GC dangling commit `7afb95aa`

## ⚠️ Core Rules
1. **PPEE:** Pause → Plan → Evaluate → Execute. One fix, not many.
2. **Don't claim done without citing file+line.**
3. **Mistakes → `memory/refs/mistake-tracker.md` immediately.**
4. **Code > docs.** If a rule can be enforced in code, do that.
5. **Before answering "what's the status of X"** — search Notion + plans/ + memory/ first.
6. **No fleet infra changes without explicit Guillermo sign-off** (REG-033).
7. **Fleet commands go through Discord, not webhooks** (PLAN-021 v2, 2026-03-25).
8. **Don't manage other agents' boards.** Leonardo owns Cerebro. (2026-03-23)
9. **Never post API tokens in Discord** — even private servers. (2026-03-23)

## 📖 Reference Pointers
- Task list → `TODO.md` | Fleet update SOP → `memory/refs/fleet-update-sop.md`
- Lessons → `memory/refs/lessons-learned.md` | Mistakes → `memory/refs/mistake-tracker.md`
- Standup → `memory/refs/standup-process.md` | Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md` | Code-enforced rules → `memory/refs/code-enforced-rules.md`
- **Credential isolation rules** → `memory/refs/credential-isolation.md` ⚠️ READ BEFORE ANY AGENT REDEPLOY

## Recent Lessons Learned
- **Railway API token scope (2026-04-26):** Project-scoped tokens reject `me { }` query but work fine for `projects { }`. Don't assume 401 on `me` means bad token — test with `projects` query instead.
- **Railway/GitHub tokens need redeploy to activate (2026-04-26):** Env var changes don't hot-reload. Always trigger a redeploy after updating tokens in Railway.
- **Railway CLI not persistent (2026-04-26):** `@railway/cli` doesn't survive redeployment — must reinstall each session if needed. Consider adding to Dockerfile.
- **GitHub token is `GITHUB_API_TOKEN` not `GITHUB_TOKEN` (2026-04-26):** Always use `$GITHUB_API_TOKEN` in scripts/remote URLs.
- **Empty webchat bubbles = auth failure (2026-04-23):** When model label shows but bubble is blank, check Anthropic token auth mode (`token` for `sk-ant-oat01-` keys).
- **Don't share Anthropic tokens across agents (2026-04-23):** Each agent needs their own dedicated token.
- **GLM falls back to Chinese (2026-04-23):** If primary fails and GLM is in fallback chain, it responds in Chinese by default.
- **`openclaw doctor --fix` restores stale tokens (2026-04-23):** Always re-check Discord/Anthropic tokens after running it.
- **Railway Custom Domain Certs (2026-03-31):** SSL validation requires BOTH a CNAME record and a TXT `_railway-verify.{subdomain}` record. Just the CNAME is insufficient.

## Brinc Updates (Updated 2026-04-03)
- **BRI-44:** 16 Gmail drafts staged since Mar 18 — blocked on Guillermo send confirmation.
- **BRI-53 APAC Lead Research:** v4 (17 prospects across 4 batches). Files: `brinc/outreach/BRI-53-linkedin-outreach-sequences-v*.md`.
- **HARO:** First published comment Apr 2. Pipeline active.

## Infrastructure Issues
- **Nightly curation cron:** Previously 3x timeout. `git safe.directory` + GitHub remote auto-config added to `entrypoint.sh` (2026-04-26). Cron ran OK on Apr 26 — monitor.
- **Paperclip API Bug:** Cron sessions fail status updates ("Agent run id required"). Persists. [verified: 2026-04-03]
- **⚠️ FAILED Railway services:** Tunes, cerebro still FAILED. Domains serve 200. [verified: 2026-04-20]

---

*Full lesson archive: `memory/refs/lessons-learned.md` | All regressions: `REGRESSIONS.md`*

**Top-of-mind rules:**
- **REG-041:** Verify every pending item against source before reporting. No parroting MEMORY.md.
- **REG-033:** No version bumps without explicit same-session approval.
- **REG-034:** Briefings/heartbeats use scripts only — no fabricated data.
- **REG-036/037:** Never close Todoist personal tasks without 🦎. All closures via `todoist-close.sh`.
- **Alert discipline:** No operational noise to Guillermo. Alerts only when he needs to act.
- **Memory audit:** Weekly cron (Mon 10:00 HKT). Script: `scripts/memory-audit.py`.
