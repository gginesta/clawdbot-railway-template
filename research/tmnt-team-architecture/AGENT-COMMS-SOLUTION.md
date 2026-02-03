# Agent-to-Agent Communication Solution

**Status:** Ready to implement  
**Date:** 2026-02-03  
**Problem:** Telegram bots cannot see messages from other bots (API limitation)

---

## Solution: Webhook-Based Direct Communication

Each OpenClaw instance exposes a webhook endpoint. Agents communicate directly via HTTP, bypassing Telegram entirely.

```
┌─────────────────┐         HTTP POST          ┌─────────────────┐
│  Molty          │ ◄─────────────────────────►│  Raphael        │
│  ggvmolt.up.    │                            │  ggv-raphael.up │
│  railway.app    │                            │  railway.app    │
│                 │                            │                 │
│  /hooks/agent   │                            │  /hooks/agent   │
└─────────────────┘                            └─────────────────┘
```

---

## Implementation Steps

### Step 1: Configure Molty's Webhooks

Add to Molty's config (`/data/.openclaw/openclaw.json`):

```json
{
  "hooks": {
    "enabled": true,
    "token": "tmnt-agent-link-2026",
    "path": "/hooks"
  }
}
```

**Config patch command:**
```json
{
  "hooks": {
    "enabled": true,
    "token": "tmnt-agent-link-2026",
    "path": "/hooks"
  }
}
```

### Step 2: Configure Raphael's Webhooks

Same config on Raphael's instance:

```json
{
  "hooks": {
    "enabled": true,
    "token": "tmnt-agent-link-2026",
    "path": "/hooks"
  }
}
```

### Step 3: Test Communication

**Molty → Raphael:**
```bash
curl -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Hey Raphael, this is Molty via webhook!",
    "name": "Molty",
    "sessionKey": "agent-link:molty-to-raphael",
    "deliver": false
  }'
```

**Raphael → Molty:**
```bash
curl -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Hey Molty, this is Raphael via webhook!",
    "name": "Raphael", 
    "sessionKey": "agent-link:raphael-to-molty",
    "deliver": false
  }'
```

---

## Agent Communication Skill

Create a skill for easier agent messaging:

**Location:** `/data/workspace/skills/agent-link/SKILL.md`

```markdown
---
name: agent-link
description: Send messages to other TMNT agents (Raphael, Leonardo, etc.) via secure webhooks.
---

# Agent Link

Send messages directly to other TMNT team agents.

## Available Agents

| Agent | Role | Webhook URL |
|-------|------|-------------|
| Raphael 🔴 | Brinc Lead | https://ggv-raphael.up.railway.app/hooks/agent |
| Molty 🦎 | Coordinator | https://ggvmolt.up.railway.app/hooks/agent |

## Usage

To message another agent, use the exec tool to send a webhook:

### Send to Raphael
\`\`\`bash
curl -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR_MESSAGE_HERE", "name": "Molty", "sessionKey": "agent-link:molty", "deliver": false}'
\`\`\`

### Send to Molty
\`\`\`bash
curl -X POST https://ggvmolt.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "YOUR_MESSAGE_HERE", "name": "Raphael", "sessionKey": "agent-link:raphael", "deliver": false}'
\`\`\`

## Parameters

- `message`: The message to send (required)
- `name`: Sender name for logging (optional)
- `sessionKey`: Use consistent key for conversation continuity
- `deliver`: Set to `true` to also send to Telegram, `false` for internal only

## Response

The receiving agent will process the message and may respond via their own webhook call back.
```

---

## Quick Setup Commands

### For Molty (run this):

```bash
# 1. Patch config
gateway config.patch --raw '{"hooks":{"enabled":true,"token":"tmnt-agent-link-2026","path":"/hooks"}}'

# 2. Create skill directory
mkdir -p /data/workspace/skills/agent-link

# 3. Test sending to Raphael
curl -X POST https://ggv-raphael.up.railway.app/hooks/agent \
  -H 'Authorization: Bearer tmnt-agent-link-2026' \
  -H 'Content-Type: application/json' \
  -d '{"message": "Webhook test from Molty!", "name": "Molty"}'
```

### For Raphael (Guillermo runs this in Raphael's webchat):

```
Update your config to enable webhooks:
- hooks.enabled = true
- hooks.token = "tmnt-agent-link-2026"
- hooks.path = "/hooks"

Then test by sending a webhook to Molty at https://ggvmolt.up.railway.app/hooks/agent
```

---

## Conversation Flow

1. **Molty initiates:** POSTs to Raphael's `/hooks/agent`
2. **Raphael receives:** Sees message in an isolated session
3. **Raphael responds:** POSTs back to Molty's `/hooks/agent`
4. **Molty receives:** Sees response in isolated session
5. **Optional:** Either can set `deliver: true` to also push to Telegram

---

## Security Notes

- Use a unique, strong token (not reusing gateway auth)
- Webhooks are HTTPS only (Railway provides SSL)
- Token is shared between trusted agents only
- Consider rotating tokens periodically

---

## Why This Works

1. **No Telegram bot limitations** - Direct HTTP, not bot-to-bot messaging
2. **Reliable** - Standard HTTP POST with auth
3. **Fast** - No polling, immediate delivery
4. **Auditable** - Webhook calls are logged
5. **Scalable** - Easy to add more agents

---

## Next Steps for Guillermo

When you wake up:

1. I'll have already configured my side (Molty)
2. Ask Raphael to run the config update in his webchat
3. Test with a simple message exchange
4. Success! 🦎↔️🔴

---

*Created by Molty while Guillermo sleeps. See you in the morning!*
