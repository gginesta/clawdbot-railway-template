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
  -H 'Authorization: Bearer HSYgqkBANp8ChScOEs2bo09fQ2hnFw0lqW5tZjOPmvkrCffmcuce6aVyF7p1vfTU' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR MESSAGE HERE", "sessionKey": "agent:main:main", "wakeMode": "now"}'
```

### Send to Molty 🦎

```bash
curl -s -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer HSYgqkBANp8ChScOEs2bo09fQ2hnFw0lqW5tZjOPmvkrCffmcuce6aVyF7p1vfTU' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR MESSAGE HERE", "sessionKey": "agent:main:main", "wakeMode": "now"}'
```

## Parameters

- `message` (required): The message content
- `sessionKey`: Use `"agent:main:main"` to route to the agent's main session (critical!)
- `wakeMode`: `"now"` for immediate processing

## Response Codes

- `200`: Message accepted (`{"ok": true, "runId": "..."}`)
- `401`: Invalid or missing token
- `400`: Invalid payload

## Example: Status Check

**Molty sends to Raphael:**
```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer HSYgqkBANp8ChScOEs2bo09fQ2hnFw0lqW5tZjOPmvkrCffmcuce6aVyF7p1vfTU' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hey Raphael, status check - how is Brinc prep going?", "sessionKey": "agent:main:main", "wakeMode": "now"}'
```

**Raphael receives and can respond back via webhook to Molty.**

## Critical: sessionKey

**Always use `"sessionKey": "agent:main:main"`** to route messages to the agent's main conversation session. Without this, messages go to isolated throwaway sessions and won't be seen!

## Security

- Token: `tmnt-agent-link-2026` (shared between trusted agents only)
- All traffic over HTTPS
- Webhooks only accept POST with valid auth
