# GitHub Issue: Webchat doesn't auto-refresh on new messages

**Submit to:** https://github.com/openclaw/openclaw/issues/new

---

## Title
Webchat UI doesn't auto-refresh when new messages arrive (requires manual page refresh)

## Description

### Context
Using OpenClaw's webhook feature for agent-to-agent communication between separate Railway instances. Two agents (Molty and Raphael) send messages to each other via `POST /hooks/agent` with `wakeMode: "now"`.

### Problem
When a webhook message arrives in an agent's session, the webchat UI doesn't update automatically. The user must manually refresh the browser page to see new messages.

**Expected behavior:** New messages (including webhook-triggered system messages) should appear in real-time without requiring a page refresh.

**Actual behavior:** Messages only appear after manual browser refresh.

### Environment
- OpenClaw version: 2026.2.1
- Deployment: Railway (Docker containers)
- Browser: Chrome (latest)
- Webhook config: `hooks.enabled: true`, using `/hooks/agent` endpoint

### Reproduction Steps
1. Set up two OpenClaw instances with webhook communication enabled
2. Open webchat for Instance A in browser
3. From Instance B, send a webhook to Instance A:
   ```bash
   curl -X POST https://instance-a.railway.app/hooks/agent \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"message": "Test", "sessionKey": "agent:main:main", "wakeMode": "now"}'
   ```
4. Observe: Instance A's webchat does not show the new message
5. Refresh the page manually → message now appears

### Impact
This affects agent-to-agent coordination workflows where operators monitor webchat to observe inter-agent communication. Currently requires constant manual refreshing to see conversation flow.

### Related
Possibly related to websocket connection for real-time updates not triggering on webhook-injected messages.

---

**Screenshots:** Available if needed (showing before/after refresh with webhook messages appearing only after refresh).
