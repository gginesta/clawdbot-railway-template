# New Agent Checklist

*Time estimate: ~1 hour per agent*

---

## Prerequisites (One-Time Setup — Already Done ✅)

- [x] Railway account with payment method
- [x] Tailscale account
- [x] Discord server created
- [x] API keys generated (Anthropic, OpenAI, OpenRouter, Brave)
- [x] Memory Vault structure set up
- [x] Molty (coordinator) instance running

---

## Per-Agent Checklist

### 1. Railway Setup (~10 min)

- [ ] **Duplicate service** in Railway dashboard
  - Go to TMNT project → Molty service → Settings → Duplicate
  - Name: `[agent-name]-service` (e.g., `raphael-service`)
  
- [ ] **Configure environment variables**
  ```
  OPENCLAW_DATA=/data
  NODE_ENV=production
  ```

- [ ] **Attach volume**
  - Create new volume: `[agent-name]-data`
  - Mount path: `/data`

- [ ] **Set domain** (optional)
  - Generate Railway domain or custom subdomain

### 2. API Keys (~5 min)

- [ ] **Create unique API keys** for the agent:
  - Anthropic: https://console.anthropic.com/settings/keys
  - OpenAI: https://platform.openai.com/api-keys
  - OpenRouter: https://openrouter.ai/keys
  - Brave: https://brave.com/search/api/
  
- [ ] **Document keys** in secure location (not in git!)

### 3. Discord Bot (~10 min)

- [ ] **Create bot** at https://discord.com/developers/applications
  - Name: `[Agent-Name]-Bot` (e.g., `Raphael-Bot`)
  - Add bot user
  - Copy token
  
- [ ] **Set permissions**
  - Send Messages, Read Message History, Add Reactions
  - Use Embed Links, Attach Files
  
- [ ] **Invite to server**
  - Generate OAuth2 URL with bot scope
  - Add to TMNT HQ server

- [ ] **Create channels** (if not existing)
  - `#[project]-general`
  - `#[project]-private`
  
- [ ] **Configure channel permissions**
  - Restrict to: Guillermo, Agent bot, Molty bot

### 4. Agent Workspace (~15 min)

- [ ] **Create workspace files** on the new instance:

```
/data/workspace/
├── AGENTS.md        ← Copy from Molty, customize
├── SOUL.md          ← Agent-specific personality
├── USER.md          ← Copy from Molty (same user)
├── IDENTITY.md      ← Agent identity
├── SECURITY.md      ← Copy from Molty
├── TOOLS.md         ← Agent-specific tools
├── HEARTBEAT.md     ← Agent-specific checks
└── memory/          ← Daily notes folder
```

- [ ] **Create SOUL.md** from template:
  - `/data/workspace/research/tmnt-team-architecture/templates/SOUL-[agent].md`

- [ ] **Create IDENTITY.md**:
```markdown
# IDENTITY.md

- **Name:** [Agent Name]
- **Project:** [Project Name]
- **Emoji:** [Emoji]
- **Role:** [Brief role description]
- **Reports to:** Molty 🦎
```

### 5. OpenClaw Config (~10 min)

- [ ] **Create openclaw.json** at `/data/.openclaw/openclaw.json`:

```jsonc
{
  "version": "1.0",
  "agent": {
    "name": "[agent-name]",
    "emoji": "[emoji]"
  },
  "auth": {
    "anthropic": { "apiKey": "[AGENT_ANTHROPIC_KEY]" },
    "openai": { "apiKey": "[AGENT_OPENAI_KEY]" },
    "openrouter": { "apiKey": "[AGENT_OPENROUTER_KEY]" }
  },
  "model": {
    "default": "anthropic/claude-sonnet-4"
  },
  "discord": {
    "botToken": "[AGENT_DISCORD_BOT_TOKEN]",
    "bindings": [
      {
        "channelId": "[GENERAL_CHANNEL_ID]",
        "allowFrom": ["[GUILLERMO_DISCORD_ID]", "[MOLTY_BOT_ID]"]
      },
      {
        "channelId": "[PRIVATE_CHANNEL_ID]",
        "allowFrom": ["[GUILLERMO_DISCORD_ID]", "[MOLTY_BOT_ID]"]
      }
    ]
  },
  "heartbeat": {
    "every": "1h"
  },
  "browser": {
    "headless": true,
    "noSandbox": true,
    "defaultProfile": "openclaw"
  },
  "contextPruning": {
    "mode": "cache-ttl",
    "cacheTtlMinutes": 240
  }
}
```

### 6. Tailscale (~5 min)

- [ ] **Install Tailscale** on the instance
  - Should be in Dockerfile already
  
- [ ] **Join mesh network**
  ```bash
  tailscale up --authkey=[TAILSCALE_AUTH_KEY] --hostname=[agent-name]
  ```

- [ ] **Verify connectivity**
  ```bash
  # From Molty:
  ping [agent-name].tailnet
  ```

### 7. Memory Vault Sync (~5 min)

- [ ] **Configure Syncthing** to sync Memory Vault
  - Add `/data/shared/memory-vault` folder
  - Connect to existing Syncthing cluster
  
- [ ] **Verify sync**
  - Check that project folders appear
  - Verify correct permissions

### 8. SSH Access for Molty (~5 min)

- [ ] **Generate SSH key pair** (if not using existing)
  
- [ ] **Add Molty's public key** to agent's `~/.ssh/authorized_keys`

- [ ] **Test SSH from Molty**
  ```bash
  ssh [agent-name].tailnet
  ```

### 9. Testing (~15 min)

- [ ] **Start OpenClaw**
  ```bash
  openclaw gateway start
  ```

- [ ] **Test Discord**
  - Send message in agent's channel
  - Verify response
  
- [ ] **Test from Molty**
  - SSH into agent instance
  - Check logs: `openclaw status`
  - Send test message via gateway API

- [ ] **Verify Memory Vault access**
  - Agent can read shared resources
  - Agent can write to own project folder
  - Agent CANNOT write to other project folders

### 10. Documentation (~5 min)

- [ ] **Update SPEC.md** with new agent details

- [ ] **Add to Molty's MEMORY.md**
  - Agent name, instance URL, Discord channels, etc.

- [ ] **Create agent's first daily note**
  - `/data/shared/memory-vault/daily/YYYY/MM/YYYY-MM-DD-[agent].md`

---

## Post-Deployment

- [ ] **Introduce agent to Guillermo** in Discord
- [ ] **Brief agent** on current project status
- [ ] **Molty verifies** all access controls working
- [ ] **First task** to test end-to-end workflow

---

## Rollback Plan

If something goes wrong:

1. **Railway**: Delete service, volume persists
2. **Discord**: Remove bot from server
3. **Tailscale**: Remove device from network
4. **Memory Vault**: Agent's writes are isolated, no cleanup needed

---

## Quick Reference: IDs Needed

| Item | Where to Find |
|------|---------------|
| Discord Channel ID | Right-click channel → Copy ID (enable Developer Mode) |
| Discord User ID | Right-click user → Copy ID |
| Discord Bot Token | Discord Developer Portal → Bot → Token |
| Tailscale Auth Key | Tailscale Admin → Settings → Keys |
| API Keys | Each provider's dashboard |

---

*Last updated: 2026-02-03*
