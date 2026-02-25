# Post-Mortem: Leonardo Anthropic Auth Failure
**Date:** Feb 23–25, 2026  
**Duration:** ~3 days  
**Resolved:** Feb 25, 2026 ~07:37 HKT  
**Severity:** High — Leonardo completely non-functional for tool use

---

## What Happened

Leonardo's Anthropic authentication broke, causing him to fall back to `xai/grok-3` as primary model. When Grok also became unavailable, he fell to OpenRouter — which returned `404 No endpoints found that support tool use`, making him completely unable to respond to any message.

---

## Root Cause

**auth.json on Leonardo's Railway persistent volume had an empty/wrong Anthropic token.**

The file at `/data/.openclaw/agents/main/agent/auth.json` had:
```json
{"anthropic": {"type": "api_key", "key": ""}}
```

The empty key caused every Anthropic API call to 401. OpenClaw entered cooldown. With no fallback model supporting tool use via OpenRouter, Leonardo became completely non-functional.

**Secondary root cause:** An earlier failed attempt to fix the auth via webhook wrote an empty string (isolated sub-agent processes don't inherit container env vars — see lesson 66).

---

## Contributing Factors

1. **No Railway Connect tab visible** — Guillermo couldn't find the shell access UI (it's under a different navigation path than expected)
2. **Webhook-based fixes are unreliable for auth** — isolated sessions don't inherit `ANTHROPIC_TOKEN` from container env
3. **Multiple conflicting fix attempts** — wrote empty string over partially-correct values, made state worse
4. **No Codex fallback** — when the OpenRouter fallback broke, there was no working model at all

---

## Fix That Worked

**Two-step Railway start command injection:**

1. Set Railway start command to Python patch script:
   ```python
   # Clears browser locks, patches auth.json with ANTHROPIC_TOKEN env var,
   # patches openclaw.json primary model, then os.execv(supervisord)
   ```
2. Trigger redeploy → **FAILED** (health check timeout) but the Python script DID run and patched both files on the persistent volume
3. Revert start command to `None` (Dockerfile CMD = startup.sh)
4. Trigger redeploy → **SUCCESS** — reads the now-correct files from volume, boots cleanly

**Key insight:** Files written to `/data/` during a FAILED Railway deployment **persist on the volume**. The deployment failure doesn't roll back file writes.

---

## What Was Fixed

| File | Before | After |
|------|--------|-------|
| `auth.json` | `{"anthropic": {"type": "api_key", "key": ""}}` | `{"anthropic": {"type": "api_key", "key": "sk-ant-oat01-...108chars"}}` |
| `openclaw.json` → `agents.defaults.model.primary` | Unknown (possibly OpenRouter model) | `anthropic/claude-sonnet-4-6` |
| `openclaw.json` → `agents.defaults.model.fallbacks` | Unknown | `["anthropic/claude-haiku-4-5", "xai/grok-3", "openai-codex/gpt-5.2"]` |

---

## Lessons Learned

### L1: The two-step volume patch pattern
When you need to write to a Railway container's persistent volume without shell access:
1. Set start command = Python script that makes the writes + `os.execv(supervisord)`
2. Deploy → will likely FAIL health check, but writes ARE committed to volume
3. Revert start command to `None`, redeploy → reads patched files, succeeds

### L2: `agents.defaults.model` is the only key
There is no `agents.defaults.subagents.model`. Both main sessions and sub-agents read from `agents.defaults.model`. Patching a nonexistent key silently does nothing.

### L3: OpenClaw cooldown ≠ API rate limit
"Provider X in cooldown" = OpenClaw internally backed off after repeated errors. Self-resolves in 5-15 min. Affects only that process — not other agents even on the same token.

### L4: Always have `openai-codex/gpt-5.2` as final fallback
It uses cached OAuth, supports tool use, doesn't rate limit easily. Without it, any combination of provider failures leaves the agent completely dark.

### L5: Don't spam-test
Rapid webhooks + sub-agent spawns + gateway restarts in quick succession burns per-minute API limits and triggers OpenClaw cooldowns across ALL providers simultaneously.

### L6: auth.json structure for Anthropic Max plan
```json
{
  "anthropic": {
    "type": "api_key",
    "key": "sk-ant-oat01-..."
  }
}
```
`type: api_key` is correct even for OAuth tokens. The gateway reads this and uses it as a bearer token for Anthropic API calls.

### L7: Isolated webhook processes don't inherit env vars
Writing env vars to Railway Railway doesn't help webhook-triggered isolated sub-agent sessions. They start fresh without `ANTHROPIC_TOKEN` etc. Files on the volume are the only reliable cross-process state.

---

## Prevention

1. **Pre-populate `/data/shared/credentials/`** — shared credentials should live there from day 1, readable by all agents at startup without distribution
2. **Fleet health check cron** — daily check of auth.json token length across all agents
3. **Always include Codex fallback** in every agent's model chain
4. **Deployment runbook** — before redeploying an agent, verify auth.json token length > 100 chars

---

## Timeline

| Time (HKT) | Event |
|------------|-------|
| Feb 23 ~09:00 | Leonardo confirmed broken (401 on Anthropic, falling back to Grok) |
| Feb 23-24 | Multiple webhook fix attempts, all failed (empty string writes) |
| Feb 24 ~18:00 | Railway API confirmed working for start command injection |
| Feb 24 ~18:40 | First start command injection ran — auth fixed (108 chars) but deployment FAILED |
| Feb 25 ~07:37 | Clean redeploy SUCCESS — Leonardo back on Anthropic direct |
| Feb 25 ~07:45 | Confirmed working: "Primary: anthropic/claude-sonnet-4-6" |
| Feb 25 ~13:30 | Sub-agent test confirmed: Anthropic Haiku working |
| Feb 25 ~13:30 | **Saga closed.** |

---

*"Leonardo 🔵 — Master of ninjutsu, venture building, and eventually... authentication formats."*
