---
name: agent-link
description: Send messages to other TMNT agents (Raphael, Leonardo, etc.) via secure webhooks. Use when coordinating with team members.
---

# Agent Link 🔗

Direct agent-to-agent messaging via webhooks. Bypasses Telegram bot limitations.

## Team Directory

| Agent | Emoji | Role | Webhook URL |
|-------|-------|------|-------------|
| Molty | 🦎 | Coordinator | https://ggvmolt.up.railway.app/hooks/agent |
| Raphael | 🔴 | Brinc Lead | https://ggv-raphael.up.railway.app/hooks/agent |
| Leonardo | 🔵 | Launchpad Lead | https://leonardo-production.up.railway.app/hooks/agent |

**Shared token (all agents):** `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd`
**⚠️ sessionKey is DISABLED** on these deployments (`allowRequestSessionKey=false`). Omit it — messages still route correctly without it.

## ⚠️ STOP — USE DISCORD FIRST!

**Webhooks are for emergencies ONLY.** Guillermo has said this 5+ times.

**Default:** Send messages to other agents via Discord channels:
- Raphael → `#brinc-private` (1468164139674238976) or `#brinc-general` (1468164121420628081)
- Use the `message` tool with `channel=discord` and `target=<channel_id>`

**Only use webhooks when:** Discord is down, or you need to trigger an immediate isolated agent action.

## Webhook Fallback (EMERGENCY ONLY)

Use `exec` with `curl` to send a webhook message:

### Send to Raphael 🔴

```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Send to Leonardo 🔵

```bash
curl -s -X POST https://leonardo-production.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Your message here", "wakeMode": "now"}'
```

### Send to Molty 🦎

```bash
curl -s -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Your message here", "wakeMode": "now"}'
```

## Parameters

- `message` (required): The message content
- `wakeMode`: `"now"` for immediate processing
- `sessionKey`: **Disabled** — omit entirely

## Response Codes

- `200`: Message accepted (`{"ok": true, "runId": "..."}`)
- `401`: Invalid or missing token
- `400`: Invalid payload

## Example: Status Check

**Molty sends to Raphael:**
```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hey Raphael, status check - how is Brinc prep going?", "wakeMode": "now"}'
```

**Raphael receives and can respond back via webhook to Molty.**

## Critical: sessionKey

**Do NOT include `sessionKey`** — it is disabled on all deployments (`allowRequestSessionKey=false`). Including it returns a 200 but the message won't route correctly. Messages still reach the agent's active session without it.

## Security

- Token: `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd` (shared between trusted agents only)
- All traffic over HTTPS
- Webhooks only accept POST with valid auth
