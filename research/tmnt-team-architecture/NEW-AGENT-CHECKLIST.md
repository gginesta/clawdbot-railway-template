# 🆕 New Project Lead Checklist

*Standard Operating Procedure for spinning up a new TMNT Project Lead*

---

## Pre-Deployment (Coordinator - Molty)

### 1. Identity Design
- [ ] Choose agent name and emoji
- [ ] Draft SOUL.md with:
  - Identity (name, role, emoji, archetype)
  - Personality traits
  - Communication style
  - Domain boundaries
  - Hierarchy (reports to Molty, escalation paths)
- [ ] Prepare USER.md (copy from template, adjust if needed)
- [ ] Prepare IDENTITY.md

### 2. Discord Setup
- [ ] Create Discord bot at https://discord.com/developers/applications
  - Name: `{AgentName}-Bot`
  - Enable: MESSAGE CONTENT INTENT (required!)
  - Generate token and save securely
- [ ] Invite bot to TMNT Squad server with permissions:
  - Send Messages, Read Message History, Add Reactions, Use External Emojis, Attach Files
- [ ] Create agent-specific channels:
  - `#{project}-general` (team discussions)
  - `#{project}-private` (bot-only, Molty + agent)
- [ ] Configure channel permissions
- [ ] Store token in `/data/.openclaw/credentials/discord-{agent}-bot.json`

---

## Railway Deployment (Human - Guillermo)

### 3. Create Railway Project (~15 min)
- [ ] Create new project in Railway dashboard
- [ ] Deploy from `gginesta/clawdbot-railway-template`
- [ ] Create `/data` volume and mount it

### 4. Configure Environment Variables

**Required:**
| Variable | Value | Notes |
|----------|-------|-------|
| `OPENCLAW_GATEWAY_TOKEN` | *generate new* | `openssl rand -base64 24 \| tr -d '/+='` |
| `OPENCLAW_GATEWAY_PORT` | `18789` | Must match internal port, NOT 8080! |
| `OPENCLAW_PUBLIC_PORT` | `8080` | Railway's external port |
| `OPENCLAW_STATE_DIR` | `/data/.openclaw` | |
| `OPENCLAW_WORKSPACE_DIR` | `/data/workspace` | |
| `ANTHROPIC_API_KEY` | *your key* | Same as Molty |
| `GOOGLE_API_KEY` | *your key* | For memory search |

**Optional (copy from Molty):**
- `TAILSCALE_AUTHKEY` - For mesh network
- `TAILSCALE_HOSTNAME` - e.g., `raphael-railway`

### 5. Handle Port Conflict Issue

⚠️ **CRITICAL**: The config file must NOT have `gateway.bind` set!

If you see "Gateway failed to start: Port 8080 already in use":
1. Go to `/setup` → Config Editor
2. Remove the entire `"bind": "..."` line from gateway section
3. Save and let it restart

The setup proxy uses 8080, gateway uses 18789 internally. They coexist when `bind` is not specified (defaults to loopback).

### 6. Initial Config Fix

After first deployment, the config needs these changes:
- Remove `gateway.bind` if present (causes port conflict)
- Add `gateway.controlUi.dangerouslyDisableDeviceAuth: true` (needed for web UI)

Minimal working gateway section:
```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "auth": {
    "mode": "token",
    "token": "YOUR_GATEWAY_TOKEN"
  },
  "controlUi": {
    "dangerouslyDisableDeviceAuth": true
  }
}
```

---

## Agent Configuration (Human via webchat OR Coordinator via Discord)

### 7. Access Agent Webchat
- URL: `https://{project}.up.railway.app/openclaw/?token={GATEWAY_TOKEN}`

### 8. Install Identity Files

Send to agent webchat:
```
Save this as /data/workspace/SOUL.md:
[paste SOUL.md content]

Save this as /data/workspace/USER.md:
[paste USER.md content]

Save this as /data/workspace/IDENTITY.md:
[paste IDENTITY.md content]

Delete /data/workspace/BOOTSTRAP.md if it exists.
```

### 9. Add Discord Channel

Send to agent:
```
Use gateway config.patch to add Discord:
{
  "channels": {
    "discord": {
      "enabled": true,
      "botToken": "[THEIR_BOT_TOKEN]",
      "dmPolicy": "allowlist",
      "guildPolicy": "allowlist",
      "allowedGuilds": ["1468161542473121932"]
    }
  },
  "plugins": {
    "entries": {
      "discord": {
        "enabled": true
      }
    }
  }
}
```

### 10. Verify Discord Connection
- Check Railway logs for "Discord connected"
- Send test message in `#{project}-private`
- Confirm agent responds

---

## Post-Deployment (Coordinator - Molty)

### 11. Security Audit
- [ ] Run `openclaw doctor` via agent
- [ ] Check for config warnings
- [ ] Verify permissions on `/data/.openclaw` (should be 700)
- [ ] Ensure credentials directory exists

### 12. Full Onboarding Briefing

Message agent in Discord with:
1. **Team Architecture** - TMNT hierarchy, who reports to whom
2. **Memory Vault** - Where their files live, what they can/can't see
3. **Communication Protocols** - How to reach Molty, Guillermo
4. **Domain Boundaries** - What's in scope, what requires escalation
5. **Tools Overview** - What tools they have access to

### 13. Create Agent's Workspace Structure
```
/data/workspace/
├── SOUL.md
├── USER.md
├── IDENTITY.md
├── AGENTS.md
├── TOOLS.md
├── memory/
│   └── YYYY-MM-DD.md
└── [project-specific folders]
```

### 14. Test Core Functions
- [ ] Can read/write files
- [ ] Can respond in Discord
- [ ] Memory search working
- [ ] Can spawn sub-agents (if applicable)

### 15. Update Documentation
- [ ] Add to MEMORY.md team roster
- [ ] Update SPEC.md if architecture changed
- [ ] Record any issues/lessons in memory/YYYY-MM-DD.md

---

## Lessons Learned

### Railway Container Issues
1. **Port 8080 conflict**: Setup server uses 8080, gateway should use different internal port (18789). Never set `OPENCLAW_GATEWAY_PORT=8080`.

2. **Syncthing conflicts**: If you see "Error opening database: resource temporarily unavailable", Syncthing has a lock issue. Usually resolves on redeploy.

3. **Tailscale routing**: Tailscale mesh between Railway containers may not work immediately. Use public URLs or Discord for cross-agent communication.

4. **Config validation**: `gateway.bind: "all"` is INVALID! Omit the bind key entirely or use valid values: `"auto"`, `"lan"`, `"loopback"`, `"custom"`, `"tailnet"`.

### Discord Configuration
1. **MESSAGE CONTENT INTENT required**: Without this, bot won't see message content
2. **Channel IDs vs Names**: Use channel names in `allowedChannels`, guild IDs in `allowedGuilds`
3. **Bot needs to be invited**: Generate OAuth URL with correct permissions

### Time Estimates
| Task | Time |
|------|------|
| Discord bot setup | 10 min |
| Railway project + deploy | 15 min |
| Config fixes | 10 min |
| Identity files | 5 min |
| Testing | 10 min |
| **Total** | **~50 min** |

---

*Version: 2026-02-03 | Updated after Raphael deployment*
