# MEMORY.md - Working Memory

*Last updated: molty | 2026-04-28 22:31 HKT | Codex OAuth active, GitHub consolidated to single branch, fleet Codex migration planned | Target: <15KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **WhatsApp:** +34 677 43 78 34 (Spanish SIM, purchased London 2026-03-22, needs QR pairing)
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
**Version:** v2026.4.25 (all 4 deployed 2026-04-27 22:07 HKT)
| Agent | URL | Model Chain | Status |
|-------|-----|-------------|--------|
| Molty 🦎 | ggvmolt.up.railway.app | Codex GPT-5.5 → glm-5.1 → deepseek-flash → or-sonnet-4.6 → sonnet-4-6 | ✅ v4.25 LIVE |
| Raphael 🔴 | ggv-raphael.up.railway.app | Sonnet 4.6 → glm-5.1 → deepseek-flash → or-sonnet → or-flash | ✅ v4.25 LIVE |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet 4.6 → glm-5.1 → deepseek-flash → or-sonnet → or-flash | ✅ v4.25 LIVE |
| April 🌸 | april-agent-production.up.railway.app | Sonnet 4.6 → glm-5.1 → deepseek-flash → or-sonnet → or-flash | ✅ v4.25 LIVE |

**Molty Primary:** `openai-codex/gpt-5.5` (Codex OAuth via ChatGPT Pro subscription — activated 2026-04-28)
**Molty Fallbacks:** `zai/glm-5.1` → `deepseek/deepseek-v4-flash` → `openrouter/anthropic/claude-sonnet-4.6` → `anthropic/claude-sonnet-4-6`
**Railway env:** `OPENCLAW_PRIMARY_MODEL=openai-codex/gpt-5.5` (fixed from `zai/glm-5.1` on 2026-04-28 18:49 HKT)
**Cron model:** `openai-codex/gpt-5.4` (all 12 crons updated 2026-04-28)
**openai-codex model list:** gpt-5.5, gpt-5.4, gpt-5.3, gpt-5.2 (updated 2026-04-28)
**Heartbeat model:** `xai/grok-3-fast` (fleet standard, all agents)
**⚠️ Anthropic token dead (2026-04-28):** `sk-ant-oat01-...` returns `invalid x-api-key`. Needs new key. Molty switched to Codex; other 3 agents still use Anthropic as primary (will fail → fall back to GLM).
**⚠️ Other agents need Codex auth:** Raphael/Leonardo/April still on Anthropic primary. Each needs `railway shell` + device-code flow to activate Codex OAuth.
**GitHub:** Single remote (`origin`), single branch (`main`). Local `master` tracks `origin/main`. Repo: `gginesta/clawdbot-railway-template`.
**Setup page auth (v4.25):** `/setup` now returns 401. Access via `https://<agent>.up.railway.app/setup?token=<gateway_token>`. `/debug` and `/config` still open.

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
- **GitHub branch consolidation (2026-04-28 22:31 HKT):** Cleaned up from 14 remote branches + 3 remotes to 1 remote (`origin`) + 1 branch (`main`). Local `master` tracks `origin/main`. Deleted stale `local main` (Jan 31 commit), `backup/master`, `backup/chore/bump-openclaw-ref`. Removed `vignesh` remote.
- **Codex native harness: staying on PI (2026-04-28 19:41 HKT):** Reviewed docs. Guillermo decided OpenClaw PI stays in control. Codex is just a model, not the runtime. (Guillermo decision)
- **GitHub force push fix (2026-04-28 20:00 HKT):** Railway builds were failing because `main` pointed to a Jan 31 commit with no Dockerfile. Force-pushed `master:main` to fix. Build succeeded.
- **Railway env var fix + model list update (2026-04-28 18:53 HKT):** `OPENCLAW_PRIMARY_MODEL` was `zai/glm-5.1` (overriding config) → fixed to `openai-codex/gpt-5.5`. Added gpt-5.5/gpt-5.4/gpt-5.3/gpt-5.2 to openai-codex provider model list. Updated aliases. Redeployed Molty.
- **Codex OAuth activated on Molty (2026-04-28):** Guillermo ran device-code flow via Railway shell. `openai-codex/gpt-5.5` now primary. All 12 crons switched to `openai-codex/gpt-5.4`. Legacy `openai-codex` transport override (baseUrl/apiKey) still in config — needs cleanup.
- **Anthropic token dead (2026-04-28):** `sk-ant-oat01-...` returns `invalid x-api-key`. Molty switched to Codex. Other 3 agents still point to Anthropic (falling back to GLM). New key needed or Codex auth per agent.
- **Fleet v4.25 Dockerfile bump (2026-04-27):** `OPENCLAW_VERSION` bumped to `2026.4.25` (commit `8d8f1fa5`). All 4 deployed successfully.
- **Fleet v4.25 feature rollout (2026-04-27 22:07 HKT):** DeepSeek V4 Flash in fallback chain, TTS personas, DeepSeek plugin enabled.
- **Fleet v4.23 upgrade (2026-04-27):** Fixed: pnpm-lock.yaml sync, supervisor in Dockerfile, main branch alignment.
- **Fleet Rehab (2026-04-24):** April + Leonardo redeployed. Configs standardised.
- **Railway API access restored (2026-04-26):** Project-scoped token working.
- **GitHub access restored (2026-04-26):** Token `$GITHUB_API_TOKEN`.

## 🅿️ Parked
- WHOOP, Browser relay (Waalaxy), MC Phase 3 sprint — all parked. [verified: 2026-04-20]

## ⏳ Pending
- **🚨 Fleet Codex migration (approved 2026-04-28):** Migrate Raphael, Leonardo, April from Anthropic → Codex OAuth. See plan: `plans/fleet-codex-migration.md`
- **Clean up legacy openai-codex transport override:** `models.providers.openai-codex` still has old `baseUrl`/`apiKey` from pre-OAuth. `openclaw doctor` warns about this. Remove the legacy transport fields.
- **DeepSeek API key needed:** Plugin enabled, fallback chain updated, key missing. Get from platform.deepseek.com.
- **April TTS persona:** `april-voice` defined, needs Railway env update.
- **Webchat device auth:** Workaround: `?token=<gateway_token>`. Low priority.
- **WhatsApp SIM:** +34 677 43 78 34. Needs QR pairing.
- **GitHub dangling commit:** Contact GitHub Support to GC `7afb95aa`.

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

## 🚀 Active OpenClaw Features (v4.25 — all deployed)
| Feature | Status | Notes |
|---------|--------|-------|
| Codex OAuth (GPT-5.5/5.4) | ✅ Molty only | Device-code flow via Railway shell. Other 3 agents pending. |
| Forked subagent context | ✅ Available | Pass `context:"fork"` in sessions_spawn |
| Per-call timeoutMs | ✅ Available | For slow gens |
| Memory QMD repair | ✅ Auto-applied | Memory search narrows correctly |
| Block streaming fix | ✅ Auto-applied | No more duplicate replies |
| Browser 60s default timeout | ✅ Live | |
| Browser coordinate clicks | ✅ Live | |
| DeepSeek V4 Flash/Pro | ✅ Live | Key still missing — plugin enabled but unused |
| Google Meet plugin | ✅ Live | |
| Strict-agentic execution contract | 🆕 Available | `executionContract: "strict-agentic"` — stops GPT laziness. Not yet enabled. |

## Recent Lessons Learned
- **GitHub branch must have Dockerfile for Railway (2026-04-28):** Railway watches `main` branch. If `main` points to an old commit without Dockerfile, build fails silently. Always verify `git show origin/main:Dockerfile` before expecting Railway builds to succeed.
- **Local `main` vs `master` divergence (2026-04-28):** Local `main` was stuck at Jan 31 commit while all work happened on `master`. Force push `master:main` to fix. Now consolidated: single remote, single branch.
- **Railway env vars override config (2026-04-28):** `OPENCLAW_PRIMARY_MODEL=zai/glm-5.1` in Railway env overrode the config's `openai-codex/gpt-5.5`. Always check `env | grep MODEL` when the runtime model doesn't match config. Env vars require redeploy to take effect.
- **Config patch blocks protected model fields (2026-04-28):** `gateway config.patch` rejects changes to `models.providers.*.models[]` fields (id, name, contextWindow, etc.). Must edit `openclaw.json` directly for model definitions.
- **Codex device-code flow works headless (2026-04-28):** `openclaw onboard --auth-choice openai-codex-device-code --accept-risk` via Railway shell. User opens auth.openai.com/codex/device in browser, enters code. No SSH needed. Each agent needs its own flow.
- **Anthropic tokens die silently (2026-04-28):** `invalid x-api-key` with no warning. Causes cascading empty-turn failures. Always test with `curl` against api.anthropic.com if model falls back unexpectedly.
- **Railway deploy SOP (2026-04-27):** Railway watches `main` branch. Always push to `main`. Trigger fresh builds via `serviceInstanceRedeploy` API.
- **pnpm-lock.yaml must stay in sync (2026-04-27):** If `package.json` changes, run `pnpm install --no-frozen-lockfile` and commit.
- **Railway API token scope (2026-04-26):** Project-scoped tokens reject `me { }` but `projects { }` works.
- **Railway/GitHub tokens need redeploy to activate (2026-04-26):** Env var changes don't hot-reload.
- **Railway CLI not persistent (2026-04-26):** Must reinstall each session.
- **GitHub token is `GITHUB_API_TOKEN` not `GITHUB_TOKEN` (2026-04-26):** Always use `$GITHUB_API_TOKEN`.
- **Empty webchat bubbles = auth failure (2026-04-23):** Check Anthropic token auth mode.
- **Don't share Anthropic tokens across agents (2026-04-23):** Each needs their own.
- **GLM falls back to Chinese (2026-04-23):** Default behavior when primary fails.
- **Railway Custom Domain Certs (2026-03-31):** Needs BOTH CNAME + TXT record.

## Brinc Updates (Updated 2026-04-03)
- **BRI-44:** 16 Gmail drafts staged since Mar 18 — blocked on Guillermo send confirmation.
- **BRI-53 APAC Lead Research:** v4 (17 prospects across 4 batches). Files: `brinc/outreach/BRI-53-linkedin-outreach-sequences-v*.md`.
- **HARO:** First published comment Apr 2. Pipeline active.

## Infrastructure Issues
- **Anthropic token dead:** `sk-ant-oat01-...` returns invalid x-api-key. Molty on Codex. Other 3 agents fall back to GLM. [verified: 2026-04-28]
- **Legacy Codex transport override:** `models.providers.openai-codex` has stale `baseUrl`/`apiKey`. Needs cleanup (doctor warns). [verified: 2026-04-28]
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
