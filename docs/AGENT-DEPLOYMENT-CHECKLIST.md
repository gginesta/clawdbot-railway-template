# Agent Deployment Checklist
<!-- Last updated: molty | 2026-03-11 | Created from April launch lessons -->

This checklist ensures consistent, secure agent deployments. Learned from Molty, Raphael, Leonardo, and April launches.

## Pre-Deployment

### 1. Railway Setup
- [ ] Create new Railway service
- [ ] Set service name: `{agent-name}-agent` or `{agent-name}-production`
- [ ] Set Railway region to **Singapore** (avoids Discord Cloudflare blocks - REG-022)
- [ ] Use our custom Dockerfile (not upstream - our image has Tailscale/Syncthing/Brave)

### 2. Discord Bot
- [ ] Create Discord Application at https://discord.com/developers/applications
- [ ] Create bot user, copy bot token
- [ ] Enable intents: Message Content ✓, Server Members ✓, Presence (optional)
- [ ] Generate OAuth2 URL with: `bot`, `applications.commands` scopes
- [ ] Add bot to TMNT Squad server
- [ ] Note bot user ID for agent-link skill

### 3. Config Preparation
- [ ] Copy template config from existing agent (Molty recommended)
- [ ] Update Discord token
- [ ] Set `allowBots: "mentions"` (not `true` - prevents loops, enables bot-to-bot)
- [ ] Configure guild channels with `requireMention: true` for non-owned channels
- [ ] Set `hooks.defaultSessionKey` to a stable value (e.g., `"hook:agent-{name}"`)
- [ ] **Never set** `dangerouslyDisableDeviceAuth: true` in production
- [ ] Only use `dangerouslyAllowHostHeaderOriginFallback: true` if needed for webchat

### 4. Secrets
- [ ] Create `/data/workspace/credentials/` directory with `chmod 700`
- [ ] Store Discord token in env vars (not config file directly)
- [ ] Use `secrets.providers.filemain` for shared secrets
- [ ] Never commit credentials to git

## Deployment

### 5. Railway Deploy
- [ ] Push to Railway
- [ ] Wait for healthcheck to pass
- [ ] Check logs for "Gateway listening" message
- [ ] Verify Discord bot shows online in server

### 6. Syncthing Integration
- [ ] Agent joins Molty's Syncthing cluster (hub-and-spoke via Molty)
- [ ] Share `skills` folder with new agent
- [ ] Share `shared` folder (memory vault access)
- [ ] **Do NOT** add agent directly to Guillermo's desktop (breaks hub-and-spoke)

### 7. Cross-Agent Communication
- [ ] Add agent to `agent-link` skill directory
- [ ] Test webhook connectivity: `curl -X POST {agent-url}/hooks/agent`
- [ ] Exchange Discord user IDs between agents for proper @mentions
- [ ] Test @mention routing works both directions

## Post-Deployment

### 8. Security Audit (run immediately after deploy)
- [ ] Run `openclaw doctor` and fix any issues
- [ ] Verify credentials directory is 700, not 755
- [ ] Check no API keys in plain config (use env/secrets providers)
- [ ] Verify `dangerouslyDisableDeviceAuth: false`
- [ ] Check `allowBots` is `"mentions"` not `true`

### 9. Mission Control
- [ ] Add agent to MC agents list
- [ ] Test heartbeat posting works
- [ ] Create any agent-specific MC tasks

### 10. Discord Channel Config
- [ ] Create agent's private channel (#agent-private)
- [ ] Agent owns their channel: `requireMention: false`
- [ ] Add channel to Molty's config with `requireMention: true` (for @Molty mentions)
- [ ] Test cross-agent @mentions work

## Common Issues & Fixes

### Discord bot shows offline
1. Check Railway logs for errors
2. Verify bot token is correct
3. If Cloudflare 429: change Railway region (REG-022)
4. If "Invalid token": regenerate Discord bot token

### @mentions not routing between agents
1. Verify `allowBots: "mentions"` (not `true` or `false`)
2. Check channel has `allow: true` in both agents' configs
3. Restart gateway (SIGUSR1 may not reload Discord config - use `/restart`)
4. Verify both agents have each other's Discord user IDs saved

### Syncthing not syncing
1. Check device is added to hub (Molty), not directly to desktop
2. Verify folders are shared with new device
3. Check folder paths match between agents

### Gateway won't start
1. Check JSON syntax (use JSON5 parser, not strict JSON)
2. Never `json.load()` OpenClaw configs in Python (REG-017)
3. Verify secrets file exists at path specified in config

## Agent-Specific Notes

### Molty 🦎
- Hub for Syncthing cluster
- Owns: #command-center, #squad-updates
- Primary model: Opus
- Discord ID: 1468162520958107783

### Raphael 🔴
- Owns: #brinc-general, #brinc-private, #brinc-marketing, #brinc-sales
- Discord ID: (check TOOLS.md)

### Leonardo 🔵
- Owns: #launchpad-general, #launchpad-private, #launchpad-cerebro
- Discord ID: (check TOOLS.md)

### April 📰
- Owns: #april-private
- WhatsApp bound (separate SIM)
- Discord ID: 1481167770191401021

### Donatello 🟣 (pending)
- Research/tinkering focus
- TBD

### Michelangelo 🟠 (pending)
- Mana Capital focus
- TBD

---

## Version History
- 2026-03-11: Initial version from April launch lessons (molty)
