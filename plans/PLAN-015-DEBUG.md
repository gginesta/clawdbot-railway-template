# PLAN-015 Debug: Fix Agent-Link Webhook Delivery

**Status:** Assigned
**Priority:** P1
**Assignee:** Molty
**Target:** Tonight (03:00 HKT)
**MC Task:** `jn7b0hz75km7g4n4gqarkv98as82vkkg`

---

## Problem

Agent-link webhooks timing out for all agents:
- Raphael ⚠️
- Leonardo ⚠️
- April ⚠️

Messages queue in `/data/shared/queue/` but never deliver. Webhook calls to `/hooks/agent` hang or timeout even though services are running.

## Symptoms

1. `python3 agent-link-worker.py send <agent> task "test"` → queued for retry
2. Direct curl to webhook returns eventually but agent doesn't process
3. Railway shows all services healthy
4. Queue processor runs every 5 min but can't deliver

## Hypotheses

1. **Gateway timeout**: Gateway hangs processing webhook while waiting for agent session response
2. **Envelope format**: tmnt-v1 envelope not being parsed correctly by receiving agent
3. **Auth mismatch**: Webhook tokens rotated or headers wrong
4. **Session routing**: Message arrives but routes to wrong/dead session

## Debug Steps

### Step 1: Check Gateway Logs
```bash
# On each agent, check recent /hooks/agent requests
grep "hooks/agent" /data/.openclaw/logs/*.log | tail -50
```

### Step 2: Test Direct Webhook with Timing
```bash
# Test Raphael
time curl -v -X POST "https://ggv-raphael.up.railway.app/hooks/agent" \
  -H "Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd" \
  -H "Content-Type: application/json" \
  -d '{"message":"ping test"}' \
  --max-time 30
```

### Step 3: Compare Configs
- Check Molty's webhook config (working)
- Compare to Raphael/Leonardo/April configs
- Look for hooks.* or webhook.* differences

### Step 4: Check Agent Session State
- Are agents' main sessions active?
- Is there a session key mismatch?

### Step 5: Test Without Envelope
Try sending raw message without tmnt-v1 envelope wrapper.

## Success Criteria

- [ ] At least one agent receives webhook message successfully
- [ ] Root cause identified and documented
- [ ] Fix deployed or workaround documented

---

*Created: 2026-03-13 16:38 HKT*
