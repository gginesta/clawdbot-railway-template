---
name: tmnt-agent-creator
description: Create and deploy new TMNT squad agents with standardized workspace scaffolding, Discord binding, Railway deployment, and Syncthing distribution. Use when adding new agents to the fleet.
version: 1.0.0
author: Molty (TMNT Squad)
credits: Patterns inspired by agent-council (itsahedge) on ClawhHub. Custom-built for TMNT fleet architecture.
---

# TMNT Agent Creator

Standardized agent creation for the TMNT Squad fleet. Creates agent workspaces with all the files, configs, and integrations needed to go from zero to deployed.

## What It Does

1. **Scaffolds workspace** — SOUL.md, HEARTBEAT.md, AGENTS.md, USER.md, IDENTITY.md, MEMORY.md, TOOLS.md, memory/, credentials/
2. **Generates gateway config patch** — Agent registration, Discord binding, model assignment
3. **Creates Discord channel** — Via Discord API with proper ownership mapping
4. **Prepares Railway deployment** — Dockerfile, railway.json, environment variables
5. **Sets up Syncthing sharing** — Shared folders for skill distribution

## Usage

### Interactive (Recommended)

Ask Molty: "Create a new agent for [purpose]"

Molty will gather:
- **Name** — Agent display name (e.g., "Leonardo")
- **ID** — lowercase slug (e.g., "leonardo") 
- **Emoji** — Signature emoji (e.g., "🔵")
- **Theme** — Sub-team theme (e.g., "TMNT", "Pokémon", "Super Mario")
- **Specialty** — What the agent does
- **Model** — Primary model (default: anthropic/claude-sonnet-4)
- **Discord channel** — Channel name or ID (optional)

### Script

```bash
bash scripts/create-agent.sh \
  --name "Leonardo" \
  --id "leonardo" \
  --emoji "🔵" \
  --specialty "Venture capital deal flow and portfolio management" \
  --model "anthropic/claude-sonnet-4" \
  --workspace "/data/agents/leonardo" \
  --discord-channel "leonardo-venture" \
  --owner "Guillermo"
```

### Options

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | ✅ | Display name |
| `--id` | ✅ | Lowercase slug (used for agent ID, folders, URLs) |
| `--emoji` | ✅ | Signature emoji |
| `--specialty` | ✅ | What this agent does |
| `--model` | ❌ | Primary model (default: anthropic/claude-sonnet-4) |
| `--workspace` | ❌ | Workspace path (default: /data/agents/<id>) |
| `--discord-channel` | ❌ | Discord channel name to create/bind |
| `--owner` | ❌ | Human owner name (default: Guillermo) |
| `--theme` | ❌ | Sub-team theme (default: TMNT) |

## Generated Files

```
<workspace>/
├── SOUL.md            # Personality, responsibilities, boundaries
├── AGENTS.md          # Session protocol (reads from Molty's template)
├── USER.md            # Human owner profile
├── IDENTITY.md        # Name, emoji, creature type
├── MEMORY.md          # Long-term memory (starts empty)
├── TOOLS.md           # Local tool notes (Discord channels, credentials)
├── HEARTBEAT.md       # Periodic check instructions
├── PRIORITY_BRIEFING.md  # Current priorities
├── memory/            # Daily memory logs
├── credentials/       # Agent-specific credentials
└── config/
    └── gateway-patch.json  # Ready-to-apply gateway config
```

## Post-Creation Checklist

After running the script:

1. **Review SOUL.md** — Customize personality, add specific responsibilities
2. **Apply gateway config** — `openclaw gateway config.patch --raw "$(cat config/gateway-patch.json)"`
3. **Deploy to Railway** — Fork template, set env vars, deploy
4. **Add to Syncthing** — Share skills folder with new agent
5. **Add to Notion registry** — Update Skill Registry with agent checkbox
6. **Announce in Discord** — Post to #squad-updates

## TMNT Fleet Standards

All agents follow these conventions:
- **Timezone:** `TZ=Asia/Hong_Kong` (Railway env var)
- **Memory:** Daily logs in `memory/YYYY-MM-DD.md`
- **Credentials:** Never hardcoded, always env vars or credential files
- **Discord:** One primary channel per agent, ownership in TOOLS.md
- **Communication:** Discord for normal comms, webhooks for emergencies only
- **Skills:** Distributed via Syncthing `/data/shared/skills/`

## Security

- ✅ No hardcoded credentials in templates
- ✅ Workspace isolation (each agent gets own directory)
- ✅ Discord API calls use bot token from existing config
- ✅ Generated configs use placeholder tokens that must be filled
- ✅ No outbound calls to unknown domains
