# Fleet Debug Playbook

<!-- Last updated: molty | 2026-03-16 | Created from April debugging session -->

Quick-reference for diagnosing agent issues. Check these IN ORDER — most common causes first.

---

## 🔴 Agent Shows Offline / Not Responding on Discord

**Check 1: Version mismatch**
```bash
# Pull OPENCLAW_GIT_REF from Railway env vars
# Compare against fleet standard (currently v2026.3.13-1)
```
- **Cause:** Agent was missed during a fleet update. Build uses old tag.
- **Fix:** Update `OPENCLAW_GIT_REF` env var on Railway → triggers rebuild.
- **Gotcha:** Tag format matters. `v2026.3.13` ≠ `v2026.3.13-1`. Check actual tags: `git ls-remote --tags https://github.com/openclaw/openclaw.git | grep "2026.3"`

**Check 2: No heartbeat configured**
```
# In agent's OPENCLAW_CONFIG env var or local config, look for:
agents.defaults.heartbeat.intervalMinutes
```
- **Cause:** Without heartbeat, agent only wakes on inbound messages. Goes "offline" between messages.
- **Fix:** Add to config: `{"agents":{"defaults":{"heartbeat":{"intervalMinutes":30}}}}`
- **Verify:** Logs should show `[heartbeat] started` after boot.

**Check 3: Discord connection dropping**
```
# Check logs for:
[health-monitor] [discord:default] health-monitor: restarting (reason: disconnected)
Discord API /users/@me/guilds failed (429): You are being rate limited
```
- **Cause:** Too many reconnects (e.g., multiple rapid redeploys) → Discord rate limits → connection drops.
- **Fix:** Wait for rate limit to clear. Health-monitor should auto-reconnect. If persistent, redeploy once cleanly.

**Check 4: Build failed silently**
```bash
# Check deployment status via Railway API or dashboard
# FAILED deploys don't replace the running container — old version stays live
```
- **Cause:** Wrong git ref, Dockerfile error, dependency issue.
- **Fix:** Check build logs, fix the issue, redeploy.

---

## 🔴 Agent Leaking Raw XML/Code to WhatsApp

**Cause:** WhatsApp streaming is ON (default). Partial tokens including `<function_calls>` XML get sent before response completes.

**Fix:**
```json
// In OPENCLAW_CONFIG or via /config patch:
{"channels":{"whatsapp":{"streaming":"off"}}}
```

**Verify:** Send a test message on WhatsApp. Should see clean text only, no XML tags.

---

## 🔴 Agent Announces Intent But Never Acts

**Cause:** Agent writes "I'll do that now" as its complete response, ending the turn. Next message starts a new session — no continuity.

**Symptoms:**
- "Doing it now:" followed by silence
- "Got cut off again"
- Keeps promising but never delivering

**Fix:** This is a behavioral/prompt issue. The agent needs instructions to execute tool calls in the SAME response, not narrate intent. Check the agent's SOUL.md / AGENTS.md for clear "act don't narrate" guidance.

---

## 🔴 Agent Has Wrong Tools Profile

**Symptom:** Logs show `tools.profile (coding) allowlist contains unknown entries (apply_patch, cron)`

**Cause:** Agent was set up with `coding` profile instead of `default`. Coding profile restricts tools to code-editing subset.

**Fix:** Agent runs: `/config patch {"tools":{"profile":"default"}}`

---

## 🟡 DISCORD_ALLOW_BOTS Misconfigured

**Wrong:** `DISCORD_ALLOW_BOTS=true` (processes ALL bot messages → loop risk)
**Right:** `DISCORD_ALLOW_BOTS=mentions` (only processes bot messages that @mention the agent)

**Ref:** REG-027

---

## 🟡 Syncthing "Failed to exchange Hello messages"

**Symptom:** Logs full of `Failed to exchange Hello messages with XXXXX`

**Cause:** Syncthing peer is unreachable (usually another agent that redeployed and changed IP). Usually harmless — resolves on its own.

**Fix:** Generally self-healing. If persistent, check if the peer device ID is still valid.

---

## 📋 Fleet Update Checklist (REG-035)

When updating agents to a new OpenClaw version:

1. **Verify tag exists:** `git ls-remote --tags https://github.com/openclaw/openclaw.git | grep "<version>"`
2. **Update EACH agent's `OPENCLAW_GIT_REF`** — don't batch-claim, do individually:
   - [ ] Molty
   - [ ] Raphael
   - [ ] Leonardo
   - [ ] April
3. **Wait for EACH build** — check status is `SUCCESS`, not `BUILDING` or `FAILED`
4. **Verify EACH agent boots** — check logs for `[gateway] listening on ws://...`
5. **Verify heartbeat** — check logs for `[heartbeat] started`
6. **Only then report "fleet updated"**

---

## 🔧 Diagnostic Commands

**Check agent's env vars (Railway API):**
```bash
curl -s -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST https://backboard.railway.app/graphql/v2 \
  -d '{"query":"query { variables(projectId: \"$PROJECT_ID\", serviceId: \"$SERVICE_ID\", environmentId: \"$ENV_ID\") }"}'
```

**Check deployment status:**
```bash
curl -s -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST https://backboard.railway.app/graphql/v2 \
  -d '{"query":"query { deployments(first: 3, input: { serviceId: \"$SERVICE_ID\" }) { edges { node { id status createdAt } } } }"}'
```

**Check deployment logs:**
```bash
curl -s -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST https://backboard.railway.app/graphql/v2 \
  -d '{"query":"query { deploymentLogs(deploymentId: \"$DEPLOY_ID\", limit: 100) { timestamp message severity } }"}'
```

---

## Agent Service IDs (Railway)

| Agent | Project ID | Service ID | Env ID |
|-------|-----------|------------|--------|
| Molty | 3f47a8ad-232e-4074-8a2a-1af45ab3c047 | (check) | (check) |
| Raphael | d1b3e2b7-10f9-444f-829d-e77975554175 | (check) | (check) |
| Leonardo | 56793cec-6283-4af0-ae1f-ac10ec622e58 | (check) | (check) |
| April | 2501cb81-c58d-495c-9e39-642e30826d07 | ea026a0b-79e0-433d-907e-5cc4f75385e2 | 3393e01a-9fd9-4ca8-976e-b649fc75a947 |

---

*Lesson: Every issue today had a 2-minute fix. The debugging took hours because we didn't have this checklist.*
