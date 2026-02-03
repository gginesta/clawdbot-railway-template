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

## How to Send Messages

Use `exec` with `curl` to send a webhook message:

### Send to Raphael 🔴

```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR MESSAGE HERE", "name": "Molty", "sessionKey": "agent-link:molty-raphael", "deliver": false}'
```

### Send to Molty 🦎

```bash
curl -s -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR MESSAGE HERE", "name": "Raphael", "sessionKey": "agent-link:raphael-molty", "deliver": false}'
```

## Parameters

- `message` (required): The message content
- `name`: Your agent name (for logging)
- `sessionKey`: Use consistent key for conversation continuity
- `deliver`: `true` to also send to Telegram, `false` for internal only

## Response Codes

- `202`: Message accepted and queued
- `401`: Invalid or missing token
- `400`: Invalid payload

## Example: Full Conversation

**Molty sends:**
```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hey Raphael, status check - how is Brinc prep going?", "name": "Molty", "sessionKey": "agent-link:daily-sync"}'
```

**Raphael receives the message in an isolated session and can respond back via webhook.**

## Security

- Token: `tmnt-agent-link-2026` (shared between trusted agents only)
- All traffic over HTTPS
- Webhooks only accept POST with valid auth
