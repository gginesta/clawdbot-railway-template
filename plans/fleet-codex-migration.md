# Fleet Codex OAuth Migration Plan

**Created:** 2026-04-28 22:31 HKT
**Status:** Awaiting Guillermo approval
**Goal:** Migrate Raphael, Leonardo, April from Anthropic primary → Codex OAuth (GPT-5.5/5.4)

---

## Background

- Anthropic token `sk-ant-oat01-...` died silently on 2026-04-28 (`invalid x-api-key`)
- Molty successfully migrated to `openai-codex/gpt-5.5` via device-code OAuth flow
- Other 3 agents are falling back from dead Anthropic → GLM-5.1 (Chinese, degraded)
- Guillermo approved full fleet migration away from Anthropic

## What Each Agent Needs

### Per-Agent Checklist (same for all 3)

| Step | What | Who | Time |
|------|------|-----|------|
| 1 | Update Railway env var `OPENCLAW_PRIMARY_MODEL=openai-codex/gpt-5.5` | Molty (API) | 1 min |
| 2 | Update Railway env var `OPENCLAW_FALLBACK_MODELS` | Molty (API) | 1 min |
| 3 | Update openclaw.json: primary model + openai-codex model list + aliases | Molty (config edit) | 2 min |
| 4 | Update all cron jobs to `openai-codex/gpt-5.4` | Molty (cron tool) | 2 min |
| 5 | Run `openclaw onboard --auth-choice openai-codex-device-code --accept-risk` via Railway shell | Guillermo | 2 min |
| 6 | Open https://auth.openai.com/codex/device in browser, enter code | Guillermo | 1 min |
| 7 | Redeploy via Railway API | Molty | 1 min |
| 8 | Verify: `/status` shows `openai-codex/gpt-5.5` as primary | Molty | 1 min |

**Total per agent: ~10 min (5 min Guillermo, 5 min Molty)**

## Agent Details

### Raphael 🔴
- **Railway project:** `d1b3e2b7-10f9-444f-829d-e77975554175`
- **Service URL:** ggv-raphael.up.railway.app
- **Current primary:** Anthropic Sonnet 4.6 (dead → falls back to GLM)
- **Cron jobs:** Need to enumerate and update

### Leonardo 🔵
- **Railway project:** `56793cec-6283-4af0-ae1f-ac10ec622e58`
- **Service URL:** leonardo-production.up.railway.app
- **Current primary:** Anthropic Sonnet 4.6 (dead → falls back to GLM)
- **Cron jobs:** Need to enumerate and update

### April 🌸
- **Railway project:** `2501cb81-c58d-495c-9e39-642e30826d07`
- **Service URL:** april-agent-production.up.railway.app
- **Current primary:** Anthropic Sonnet 4.6 (dead → falls back to GLM)
- **Cron jobs:** Need to enumerate and update

## Execution Order

**Recommended: Raphael first, then Leonardo, then April** (ascending complexity)

### Session 1: Raphael (quickest win)
1. Molty updates all config/env vars via API
2. Guillermo runs device-code flow for Raphael
3. Redeploy + verify

### Session 2: Leonardo
1. Same steps
2. Leonardo has Cerebro board — verify he still works after migration

### Session 3: April
1. Same steps
2. April has TTS persona — verify voice still works

## Prerequisites
- [x] Molty Codex OAuth working (proven pattern)
- [x] Railway API access working
- [x] GitHub branch consolidated
- [ ] Guillermo available for 3 × device-code flows (~2 min each)
- [ ] Open https://auth.openai.com/codex/device ready in browser

## Post-Migration Cleanup
- [ ] Remove Anthropic token from all Railway env vars
- [ ] Remove Anthropic auth profile from all configs
- [ ] Clean up legacy openai-codex transport override on Molty
- [ ] Update MEMORY.md fleet table
- [ ] Update TOOLS.md

## Rollback
If Codex OAuth fails for an agent:
1. Get a new Anthropic API key from console.anthropic.com
2. Set `OPENCLAW_PRIMARY_MODEL=anthropic/claude-sonnet-4-6` in Railway env
3. Redeploy

---

*Plan by Molty 🦎 — 2026-04-28*
