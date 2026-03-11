---
name: agent-link
description: Send messages to other TMNT agents (Raphael, Leonardo, etc.) via secure webhooks. Use when coordinating with team members.
---

# Agent Link 🔗

Direct agent-to-agent messaging via webhooks. Each agent has their own inbound token and knows how to reach every other agent.

## Team Directory

| Agent | Emoji | Role | Webhook URL | Inbound Token |
|-------|-------|------|-------------|---------------|
| Molty | 🦎 | Coordinator | https://ggvmolt.up.railway.app/hooks/agent | `ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562` |
| Raphael | 🔴 | Brinc Lead | https://ggv-raphael.up.railway.app/hooks/agent | `ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd` |
| Leonardo | 🔵 | Launchpad Lead | https://leonardo-production.up.railway.app/hooks/agent | `08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758` |
| April | 🌸 | Personal Assistant | https://april-agent-production.up.railway.app/hooks/agent | `7159178afb1c2c24b1e98bbbac0f0f02dc759aa038cd49ae7fac7873d8acf3ee` |

**⚠️ sessionKey is DISABLED** on all deployments (`allowRequestSessionKey=false`). Always omit it.

## ⚠️ STOP — USE DISCORD FIRST!

**Webhooks are for emergencies or triggering immediate isolated agent actions.** Default is Discord channels.

**Default routing:**
- → Raphael: `#brinc-private` (1468164139674238976) or `#brinc-general` (1468164121420628081)
- → Leonardo: `#launchpad-private` (1470919437975814226) or `#launchpad-general` (1470919420791619758)
- → Molty: `#command-center` (1468164160398557216)

**Use webhooks when:** Discord is down, or you need to trigger an immediate isolated agent action that requires a direct wakeMode=now push.

## Webhook Examples

### Molty → Raphael 🔴
```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Molty → Leonardo 🔵
```bash
curl -s -X POST https://leonardo-production.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer 08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Raphael → Molty 🦎
```bash
curl -s -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Raphael → Leonardo 🔵
```bash
curl -s -X POST https://leonardo-production.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer 08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Leonardo → Molty 🦎
```bash
curl -s -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

### Leonardo → Raphael 🔴
```bash
curl -s -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR message here", "wakeMode": "now"}'
```

## Parameters

- `message` (required): The message content
- `wakeMode`: `"now"` for immediate processing
- `sessionKey`: **Disabled** — omit entirely

## Response Codes

- `200`: Message accepted (`{"ok": true, "runId": "..."}`)
- `401`: Invalid or missing token
- `400`: Invalid payload

## Domain Ownership (routing guide)

| Domain | Owner | Don't route to |
|--------|-------|----------------|
| Brinc | Raphael 🔴 | Leonardo, Molty |
| Cerebro / Launchpad | Leonardo 🔵 | Raphael, Molty |
| Fleet / Infrastructure / Coordination | Molty 🦎 | — |

Cross-domain tasks → escalate to Molty first.
