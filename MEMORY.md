# MEMORY.md - Working Memory

*Last updated: molty | 2026-04-29 09:40 HKT | Codex OAuth fixed on Molty via local-auth-copy flow; fleet migration paused until Raphael verified | Target: <15KB*

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
| Raphael 🔴 | ggv-raphael.up.railway.app | glm-5.1 (primary, env override) → Codex GPT-5.5 → deepseek-flash → or-sonnet-4.6 → sonnet-4-6 | ✅ Recovered 2026-04-29 (env override to glm-5.1 after incident) |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet 4.6 → glm-5.1 → deepseek-flash → or-sonnet → or-flash | ✅ v4.25 LIVE |
| April 🌸 | april-agent-production.up.railway.app | Sonnet 4.6 → glm-5.1 → deepseek-flash → or-sonnet → or-flash | ✅ v4.25 LIVE |

**Molty Primary:** `openai-codex/gpt-5.5` (Codex OAuth via ChatGPT Pro subscription — fresh profile copied into container 2026-04-29; verified active via session_status)
**Molty Fallbacks:** `zai/glm-5.1` → `deepseek/deepseek-v4-flash` → `openrouter/anthropic/claude-sonnet-4.6` → `anthropic/claude-sonnet-4-6`
**Railway env:** `OPENCLAW_PRIMARY_MODEL=openai-codex/gpt-5.5` (fixed from `zai/glm-5.1` on 2026-04-28 18:49 HKT)
**Cron model:** `openai-codex/gpt-5.4` (all 12 crons updated 2026-04-28)
**openai-codex model list:** gpt-5.5, gpt-5.4, gpt-5.3, gpt-5.2 (updated 2026-04-28)
**Heartbeat model:** `xai/grok-3-fast` (fleet standard, all agents)
**⚠️ Anthropic token dead (2026-04-28):** `sk-ant-oat01-...` returns `invalid x-api-key`. Needs new key. Molty + Raphael now on Codex; Leonardo/April still use Anthropic as primary (will fail → fall back to GLM).
**⚠️ Leonardo/April need Codex auth:** Migration requires a fresh per-agent local PowerShell device-code flow, then copying that agent's local `auth-profiles.json` OAuth profile into its Railway container. Remote onboarding alone does NOT store OAuth on the agent. Local OpenClaw CLI points at one remote gateway at a time; repoint before each agent and paste/copy the resulting profile immediately. Never reuse one refresh token across multiple agents. Access tokens last ~10 days but should auto-refresh from the container if correctly copied. SOP: `memory/refs/codex-oauth-migration.md`.
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
- **Codex OAuth fixed on Molty (2026-04-29):** Discovered 2026-04-28 device-code flow only wrote OAuth locally; Railway container still had an expired Feb token. Guillermo pasted local `auth-profiles.json`; fresh `openai-codex:default` profile copied into container and verified via `session_status` as `openai-codex/gpt-5.5 · oauth`. All 12 crons already switched to `openai-codex/gpt-5.4`. Legacy `openai-codex` transport override (baseUrl/apiKey) still in config — needs cleanup.
- **Anthropic token dead (2026-04-28):** `sk-ant-oat01-...` returns `invalid x-api-key`. Molty switched to Codex. Other 3 agents still point to Anthropic (falling back to GLM). New key needed or Codex auth per agent.
- **Supervisor entrypoint fix (2026-04-29):** `entrypoint.sh` patched to start supervisord instead of running OpenClaw directly. Sidecars (Tailscale, Syncthing) now launch. Commit `93ec0e9b`.
- **Raphael recovery from incident (2026-04-29):** Supervisor patch caused agent run failures. Recovered by setting `OPENCLAW_PRIMARY_MODEL=zai/glm-5.1` in Railway env + config patch. Tailscale still unresolved.
- **Memory search restored (2026-04-29):** Switched to OpenAI embeddings (`text-embedding-3-small`). Verified working. Gemini fallback available but quota-limited.
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
| Codex OAuth (GPT-5.5/5.4) | ✅ Molty + Raphael | Local PowerShell device-code + manual auth-profile copy into container. Leonardo/April pending. |
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
- **Railway env vars override config (2026-04-28):** `OPENCLAW_PRIMARY_MODEL` in Railway env overrides config. Always check `env | grep MODEL` when runtime model doesn't match config. Env vars require redeploy.
- **Codex device-code flow (corrected 2026-04-29):** OAuth writes to local Windows auth store, NOT Railway container. Correct flow: generate locally → paste → copy into target container → clear stale cooldown → verify. SOP: `memory/refs/codex-oauth-migration.md`.
- **Supervisor entrypoint must launch supervisord (2026-04-29):** If `entrypoint.sh` runs OpenClaw directly instead of supervisord, sidecars (Tailscale, Syncthing) never start. Fix committed `93ec0e9b`. Check with `supervisorctl status`.
- **Sharp required for image tool (2026-04-29):** OpenClaw's image-ops.js needs `sharp`. If not installed, screenshots fail with 'Failed to optimize image'. Install: `npm install --prefix /usr/local/lib/node_modules/openclaw sharp`.
- **Memory search needs separate embeddings key (2026-04-29):** Codex OAuth only covers chat/completions. `memory_search` needs embeddings provider (OpenAI `text-embedding-3-small` working; Gemini hit quota). Keep embeddings config separate.

## Brinc Updates (Updated 2026-04-03)
- **BRI-44:** 16 Gmail drafts staged since Mar 18 — blocked on Guillermo send confirmation.
- **BRI-53 APAC Lead Research:** v4 (17 prospects across 4 batches). Files: `brinc/outreach/BRI-53-linkedin-outreach-sequences-v*.md`.
- **HARO:** First published comment Apr 2. Pipeline active.

## Infrastructure Issues
- **Anthropic token dead:** `sk-ant-oat01-...` returns invalid x-api-key. Molty verified on Codex OAuth after fresh profile copy. Other 3 agents fall back to GLM until migrated. [verified: 2026-04-29]
- **Legacy Codex transport override:** `models.providers.openai-codex` has stale `baseUrl`/`apiKey`. Needs cleanup (doctor warns). [verified: 2026-04-28]
- **Paperclip API Bug:** Cron sessions fail status updates ("Agent run id required"). Persists. [verified: 2026-04-03]
- **⚠️ FAILED Railway services:** Tunes, cerebro still FAILED. Domains serve 200. [verified: 2026-04-20]
- **Raphael Tailscale:** Supervisor fix committed but Tailscale serve still failing in logs. Needs separate investigation pass with Guillermo approval. [2026-04-29]

---

*Full lesson archive: `memory/refs/lessons-learned.md` | All regressions: `REGRESSIONS.md`*

**Top-of-mind rules:**
- **REG-041:** Verify every pending item against source before reporting. No parroting MEMORY.md.
- **REG-033:** No version bumps without explicit same-session approval.
- **REG-034:** Briefings/heartbeats use scripts only — no fabricated data.
- **REG-036/037:** Never close Todoist personal tasks without 🦎. All closures via `todoist-close.sh`.
- **Alert discipline:** No operational noise to Guillermo. Alerts only when he needs to act.
- **Memory audit:** Weekly cron (Mon 10:00 HKT). Script: `scripts/memory-audit.py`.
