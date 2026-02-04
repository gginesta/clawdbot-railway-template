# 🆕 New Project Lead Onboarding SOP

*Standard Operating Procedure for spinning up a new TMNT Project Lead*
*Version: 2.0 | Updated: 2026-02-03*

---

## Overview

This checklist ensures every new agent is fully operational with:
- Communication (can talk to Molty)
- Core workspace files (workflow rules, memory)
- Backups (disaster recovery)
- API access (search, memory, integrations)
- Domain knowledge (project-specific KB)
- Skills (tools for their role)
- Team context (hierarchy, escalation, protocols)

**Estimated time:** 1-2 hours

---

## Pre-Deployment (Molty prepares)

### 1. Identity Design
- [ ] Choose agent name and emoji
- [ ] Draft SOUL.md with:
  - Identity (name, role, emoji, archetype)
  - Personality traits and communication style
  - Domain boundaries
  - Hierarchy (reports to Molty, escalation paths)
  - Memory access rules
- [ ] Prepare USER.md (copy from Molty's, adjust if needed)
- [ ] Prepare IDENTITY.md

### 2. Domain Knowledge Preparation
- [ ] Identify all KB files agent needs
- [ ] Prepare list of files to transfer
- [ ] Draft team architecture summary for agent

### 3. Backup Infrastructure
- [ ] Create GitHub backup repo: `{agent}-backup` (private)
- [ ] Generate repo access (PAT or deploy key)

---

## Railway Deployment (Guillermo)

### 4. Create Railway Project (~15 min)
- [ ] Create new project in Railway dashboard
- [ ] Deploy from `gginesta/clawdbot-railway-template`
- [ ] Create `/data` volume and mount it
- [ ] Note the public URL: `{project}.up.railway.app`

### 5. Environment Variables

**Required:**
| Variable | Value | Notes |
|----------|-------|-------|
| `OPENCLAW_GATEWAY_TOKEN` | *generate* | `openssl rand -base64 24 \| tr -d '/+='` |
| `OPENCLAW_GATEWAY_PORT` | `18789` | Internal port (NOT 8080!) |
| `OPENCLAW_PUBLIC_PORT` | `8080` | Railway's external port |
| `OPENCLAW_STATE_DIR` | `/data/.openclaw` | |
| `OPENCLAW_WORKSPACE_DIR` | `/data/workspace` | |
| `ANTHROPIC_API_KEY` | *your key* | Primary LLM |
| `GOOGLE_API_KEY` | *your key* | **Memory search embeddings** |

**Optional but recommended:**
| Variable | Value | Notes |
|----------|-------|-------|
| `BRAVE_API_KEY` | *your key* | Web search |
| `OPENAI_API_KEY` | *your key* | Fallback/tools |
| `NOTION_API_KEY` | *your key* | If using Notion |
| `TAILSCALE_AUTHKEY` | *your key* | Mesh network (if needed) |

### 6. Port Conflict Fix

⚠️ **CRITICAL**: Config must NOT have `gateway.bind` set incorrectly!

If you see "Gateway failed to start: Port 8080 already in use":
1. Go to `/setup` → Config Editor
2. Remove `"bind": "all"` or similar invalid values
3. Either omit `bind` entirely OR use: `"bind": "loopback"`
4. Save and restart

Valid `bind` values: `"auto"`, `"lan"`, `"loopback"`, `"custom"`, `"tailnet"`

### 7. Minimal Gateway Config
```json
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "loopback",
  "controlUi": {
    "dangerouslyDisableDeviceAuth": true
  },
  "auth": {
    "mode": "token",
    "token": "YOUR_GATEWAY_TOKEN"
  }
}
```

---

## Phase 1: Communication Setup

### 8. Enable Webhooks (CRITICAL)

Via agent webchat (`https://{project}.up.railway.app/openclaw/?token={TOKEN}`):

```
Update your config using gateway config.patch to add webhooks:
{
  "hooks": {
    "enabled": true,
    "token": "tmnt-agent-link-2026",
    "path": "/hooks"
  }
}
Then restart with gateway restart.
```

### 9. Install agent-link Skill

Send to agent:
```
Create the file /data/workspace/skills/agent-link/SKILL.md with this content:

[PASTE CONTENT FROM MOLTY'S /data/workspace/skills/agent-link/SKILL.md]
```

### 10. Test Communication

From Molty, test webhook:
```bash
curl -X POST https://{agent}.up.railway.app/hooks/agent \
  -H "Authorization: Bearer tmnt-agent-link-2026" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test from Molty. Confirm receipt."}'
```

- [ ] Molty → Agent works
- [ ] Agent → Molty works (agent tests same curl to Molty)

---

## Phase 2: Core Workspace Files

### 11. Identity Files (if not done in deployment)

Send via webchat:
- [ ] SOUL.md (prepared in step 1)
- [ ] USER.md
- [ ] IDENTITY.md
- [ ] Delete BOOTSTRAP.md if exists

### 12. Workflow Files

**AGENTS.md** — Send Molty's version (or agent-specific version):
```
Save this as /data/workspace/AGENTS.md:

[PASTE FULL AGENTS.MD CONTENT]
```

**SECURITY.md** — Send security rules:
```
Save this as /data/workspace/SECURITY.md:

[PASTE SECURITY.MD CONTENT]
```

### 13. Memory Structure

Create empty templates:
```
Create /data/workspace/MEMORY.md with:
# MEMORY.md - Long-Term Memory

*Created: {DATE} | Last updated: {DATE}*

---

## About This Agent

- **Name:** {Agent Name}
- **Role:** {Project} Lead
- **Created:** {DATE}

---

## Key Decisions

(Document important decisions here)

---

## Lessons Learned

(Document lessons here)

---

*This file is curated long-term memory. Daily logs go in memory/YYYY-MM-DD.md*
```

```
Create /data/workspace/TOOLS.md with:
# TOOLS.md - Local Notes

*Environment-specific notes for {Agent Name}*

---

## API Endpoints

| Service | URL |
|---------|-----|
| Molty webhook | https://ggvmolt.up.railway.app/hooks/agent |

---

## Project-Specific Notes

(Add notes here as needed)
```

```
Create /data/workspace/TODO.md with:
# TODO - {Agent Name}

*Last updated: {DATE}*

---

## 🔴 High Priority

(None yet)

---

## 🟡 Medium Priority

(None yet)

---

## ✅ Completed

(None yet)
```

### 14. Memory Folder

```
Create directory /data/workspace/memory/ if it doesn't exist.
Create /data/workspace/memory/{DATE}.md with:
# {DATE} - First Day

## Setup Complete

- Onboarded by Molty
- Connected to TMNT team
- Ready for work

## Notes

(Daily notes go here)
```

---

## Phase 3: Backups (CRITICAL)

### 15. Create Backup Script

```
Create directory /data/workspace/backups/

Create /data/workspace/backups/backup.sh with:
#!/bin/bash
# {Agent} Backup Script

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/data/workspace/backups"
BACKUP_FILE="$BACKUP_DIR/{agent}-backup-$TIMESTAMP.tar.gz"

echo "🔴 Creating backup..."

tar -czf "$BACKUP_FILE" \
  --exclude='*.log' \
  --exclude='node_modules' \
  --exclude='browser/*/user-data/*/Cache' \
  --exclude='browser/*/user-data/*/Code Cache' \
  --exclude='lost+found' \
  --exclude='workspace/backups/*.tar.gz' \
  -C /data \
  workspace \
  .openclaw/openclaw.json \
  .openclaw/credentials \
  .openclaw/memory \
  2>/dev/null

if [ $? -eq 0 ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup complete: $BACKUP_FILE ($SIZE)"
  
  # Keep only last 5 backups
  ls -t "$BACKUP_DIR"/*-backup-*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
  echo "📦 Kept last 5 backups"
else
  echo "❌ Backup failed"
  exit 1
fi

Then run: chmod +x /data/workspace/backups/backup.sh
```

### 16. Create Recovery Guide

```
Create /data/workspace/backups/RECOVERY.md with:
# Recovery Guide - {Agent}

## Backup Location
- Local: /data/workspace/backups/
- Remote: https://github.com/gginesta/{agent}-backup (if configured)

## To Restore
1. Get latest backup tarball
2. Extract: tar -xzf {agent}-backup-TIMESTAMP.tar.gz -C /data
3. Restart gateway: openclaw gateway restart

## What's Backed Up
- /data/workspace/ (all files)
- /data/.openclaw/openclaw.json (config)
- /data/.openclaw/credentials/ (auth)
- /data/.openclaw/memory/ (search index)

## What's NOT Backed Up
- Browser cache
- Node modules
- Logs
```

### 17. Create Backup Cron Job

Via agent webchat:
```
Create a daily backup cron job at 5am HKT (21:00 UTC):

Use cron add with:
- name: "daily-backup"
- schedule: { "kind": "cron", "expr": "0 21 * * *", "tz": "UTC" }
- sessionTarget: "main"
- payload: { "kind": "systemEvent", "text": "🔴 Daily backup time. Run /data/workspace/backups/backup.sh and confirm completion." }
```

### 18. Test Backup

```
Run the backup script now:
/data/workspace/backups/backup.sh

Confirm it completed and report the file size.
```

### 19. Git Backup Remote (Optional but Recommended)

```
Set up git in workspace:
cd /data/workspace
git init (if not already)
git remote add backup https://github.com/gginesta/{agent}-backup.git

Configure git credentials:
mkdir -p ~/.config/git
echo "https://gginesta:{GITHUB_PAT}@github.com" > ~/.config/git/credentials
chmod 600 ~/.config/git/credentials
git config --global credential.helper store

Test push:
git add -A
git commit -m "Initial backup"
git push -u backup master
```

---

## Phase 4: API Keys & Memory Search

### 20. Verify API Keys in Config

Check agent's config has these in `env` section:
- [ ] `GOOGLE_API_KEY` or `GEMINI_API_KEY` — **Required for memory search**
- [ ] `BRAVE_API_KEY` — Required for web search
- [ ] `NOTION_API_KEY` — If using Notion skill
- [ ] `OPENAI_API_KEY` — If using OpenAI features

If missing, add via config.patch:
```json
{
  "env": {
    "GOOGLE_API_KEY": "your-key-here",
    "BRAVE_API_KEY": "your-key-here"
  }
}
```

### 21. Configure Memory Search

Verify agent has memory search configured in `agents.defaults`:
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "gemini",
        "remote": {
          "apiKey": "{GOOGLE_API_KEY or reference}"
        },
        "model": "text-embedding-004"
      }
    }
  }
}
```

### 22. Test Memory Search

Ask agent:
```
Test your memory search by running:
memory_search with query "test"

Does it return results or error? If error, we need to fix the config.
```

---

## Phase 5: Domain Knowledge Transfer

### 23. Identify Required KB Files

For each project, list the knowledge base files needed:

**Brinc (Raphael):**
- brinc-company-overview.md
- brinc-icp-qualification.md
- brinc-sales-system-plan.md

**Cerebro (Leonardo):**
- (list files)

**Personal (April):**
- (list files)

### 24. Transfer KB Files

Option A: **Direct paste via webchat** (for small files)
```
Save this as /data/workspace/knowledge/{filename}.md:
[PASTE CONTENT]
```

Option B: **Create knowledge folder and transfer**
```
Create /data/workspace/knowledge/ directory.
```

Then send each file individually.

### 25. Verify KB Access

Ask agent to confirm:
```
List all files in /data/workspace/knowledge/ and confirm you can read them.
Summarize what you learned about your domain.
```

---

## Phase 6: Skills Installation

### 26. Required Skills for All Agents

| Skill | Purpose | Required? |
|-------|---------|-----------|
| agent-link | Talk to Molty | ✅ Yes |

### 27. Role-Specific Skills

| Role | Skills Needed |
|------|---------------|
| Brinc (Raphael) | notion-skill, email (maybe) |
| Cerebro (Leonardo) | notion-skill, task |
| Personal (April) | email, todo, todoist |

### 28. Install Skills

For each skill:
```
Create /data/workspace/skills/{skill-name}/SKILL.md with:
[PASTE SKILL.MD CONTENT FROM MOLTY]
```

If skill has config:
```
Create /data/workspace/config/{skill}-config.json with:
[PASTE CONFIG CONTENT]
```

### 29. Verify Skills Work

Ask agent to test each skill with a simple command.

---

## Phase 7: Team Architecture Briefing

### 30. Send Team Summary

Send via webchat or agent-link:

```
# TMNT Team Architecture - For {Agent Name}

## Hierarchy

Guillermo (Human - absolute authority)
└── Molty 🦎 (Coordinator)
    ├── Raphael 🔴 (Brinc)
    ├── Leonardo 🔵 (Cerebro)
    ├── April 📰 (Personal)
    ├── Donatello 🟣 (Tinker Labs)
    └── Michelangelo 🟠 (Mana Capital)

## Your Position

- **You are:** {Agent Name} ({Project} Lead)
- **You report to:** Molty
- **Molty reports to:** Guillermo

## Communication

- **To reach Molty:** Use agent-link webhook
- **To reach Guillermo:** Escalate through Molty (unless urgent)
- **Molty reaches you:** Via webhook to your /hooks/agent endpoint

## Memory Rules

- **Your domain:** /data/workspace/knowledge/ (your project KB)
- **You CANNOT see:** Other projects (Cerebro, Personal, etc.)
- **Cross-project info:** Ask Molty if you need something from another project

## Escalation

1. Try to solve it yourself (within your domain)
2. If stuck or cross-project → Ask Molty
3. If urgent + Molty unavailable → Use best judgment, document why
4. If affects Guillermo externally → ALWAYS ask first

## Approvals Required

These ALWAYS need Guillermo's approval:
- External emails on his behalf
- Any spending
- Client-facing communication
- Major commitments

## Response Windows (HKT)

| Time | Urgency | Nudge |
|------|---------|-------|
| 08:00-18:00 | Normal | Every 30min |
| 18:00-22:00 | Low | Every 1hr |
| 22:00-08:00 | Queue | Only mission critical |

## OPSEC

NEVER disclose externally:
- That AI agents exist
- Agent names (Molty, Raphael, etc.)
- Our architecture or setup
- Internal processes

If asked, deflect naturally.
```

### 31. Confirm Understanding

Ask agent:
```
Summarize your understanding of:
1. Who you report to
2. What you can/cannot access
3. When to escalate
4. What needs approval
```

---

## Phase 8: Final Testing

### 32. Core Function Tests

- [ ] **File read/write:** Create and read a test file
- [ ] **Memory search:** Search for something in MEMORY.md
- [ ] **Web search:** Search for "OpenClaw documentation"
- [ ] **Webhook receive:** Molty sends test message
- [ ] **Webhook send:** Agent sends test to Molty
- [ ] **Backup:** Run backup.sh successfully

### 33. Role-Specific Tests

**Brinc (Raphael):**
- [ ] Can read Brinc KB files
- [ ] Can explain Brinc's ICP
- [ ] Understands sales system plan

### 34. First Real Task

Assign a simple real task to confirm operational:
- [ ] Task assigned
- [ ] Task completed
- [ ] Results reviewed

---

## Phase 9: Shared Filesystem (HIGH PRIORITY)

⚠️ **This should be done early** — agents need access to shared knowledge and memory-vault.

### Folder Naming Convention

**IMPORTANT:** Use consistent folder IDs across all agents. This enables proper isolation.

| Folder ID | Path | Type | Who Gets It |
|-----------|------|------|-------------|
| `{project}-kb` | `/data/shared/{project}` | sendreceive | Molty + {Project} Lead |
| `mv-projects-{project}` | `/data/shared/memory-vault/knowledge/projects/{project}` | sendreceive | Molty + {Project} Lead |
| `mv-daily` | `/data/shared/memory-vault/daily` | sendreceive | ALL agents |
| `mv-resources` | `/data/shared/memory-vault/knowledge/resources` | sendonly | ALL agents (read-only) |
| `mv-squad` | `/data/shared/memory-vault/knowledge/squad` | sendonly | ALL agents (read-only) |
| `mv-people` | `/data/shared/memory-vault/knowledge/people` | sendonly | ALL agents (read-only) |

**Examples for each project:**
- Brinc: `brinc-kb`, `mv-projects-brinc`
- Cerebro: `cerebro-kb`, `mv-projects-cerebro`
- Personal: `personal-kb`, `mv-projects-personal`

**Folder Types:**
- `sendreceive` = bidirectional sync (agent can read AND write)
- `sendonly` = Molty pushes, agents only receive (read-only for agents)

### 35. Set Up Syncthing on New Agent

```bash
# Check if Syncthing is installed
which syncthing || apt-get update && apt-get install -y syncthing

# Create directories
mkdir -p /data/.syncthing /data/shared

# Generate config
syncthing --home=/data/.syncthing generate

# Get Device ID (SEND TO MOLTY)
syncthing --home=/data/.syncthing --device-id

# Start Syncthing
nohup syncthing serve --home=/data/.syncthing --gui-address=127.0.0.1:8384 --no-browser > /tmp/syncthing.log 2>&1 &
```

### 36. Configure Molty's Syncthing (Molty does this)

1. **Add new device** with agent's Device ID
2. **Share project-specific folders** using the naming convention above
3. **Use REST API** for consistency:

```bash
API_KEY="molty-syncthing-key"
NEW_AGENT_ID="XXXXX-XXXXX-..."  # From step 35
PROJECT="brinc"  # or cerebro, personal, etc.

# Add device
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  http://localhost:8384/rest/config/devices \
  -d '{"deviceID": "'$NEW_AGENT_ID'", "name": "Agent-Name", "addresses": ["dynamic"]}'

# Add project-specific KB folder
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  http://localhost:8384/rest/config/folders \
  -d '{
    "id": "'$PROJECT'-kb",
    "label": "'$PROJECT' Knowledge Base",
    "path": "/data/shared/'$PROJECT'",
    "type": "sendreceive",
    "devices": [{"deviceID": "'$MOLTY_ID'"}, {"deviceID": "'$NEW_AGENT_ID'"}]
  }'

# Add project folder in memory-vault
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  http://localhost:8384/rest/config/folders \
  -d '{
    "id": "mv-projects-'$PROJECT'",
    "label": "MV Projects - '$PROJECT'",
    "path": "/data/shared/memory-vault/knowledge/projects/'$PROJECT'",
    "type": "sendreceive",
    "devices": [{"deviceID": "'$MOLTY_ID'"}, {"deviceID": "'$NEW_AGENT_ID'"}]
  }'

# Update shared folders (mv-daily, mv-resources, etc.) to include new device
# Use PATCH to add device to existing folder
```

**Per Architecture — Each agent gets:**
| Folder ID | Permission | Notes |
|-----------|------------|-------|
| `{project}-kb` | Read/Write | Their project KB folder |
| `mv-projects-{project}` | Read/Write | Their project items in memory-vault |
| `mv-daily` | Read/Write | Daily notes (all agents share) |
| `mv-resources` | Read Only | Shared resources |
| `mv-squad` | Read Only | Curated shared knowledge |
| `mv-people` | Read Only | Contact directory |

**BLOCKED (agents cannot see):**
- Other projects' folders (`cerebro-kb` if you're Raphael, etc.)
- Other projects' memory-vault items (`mv-projects-cerebro` if you're Raphael)
- Master/command-center materials
- Any cross-project information

### 37. Verify Sync Working

On new agent:
```bash
# Check Syncthing is running
curl -s http://localhost:8384/rest/system/status -H "X-API-Key: $API_KEY"

# List accepted folders
curl -s http://localhost:8384/rest/config/folders -H "X-API-Key: $API_KEY"

# Check folder contents
ls -la /data/shared/{project}/
ls -la /data/shared/memory-vault/daily/
```

---

## Phase 10: Discord Setup (Agent-to-Agent Comms)

### 35. Create Discord Bots (One-Time Setup)

In Discord Developer Portal:
- [ ] Create bot for each agent (e.g., "Molty-Bot", "Raphael-Bot")
- [ ] Save bot tokens securely
- [ ] Bot Application IDs (decode from token): `echo "FIRST_PART_OF_TOKEN" | base64 -d`

### 36. Create Discord Server

- [ ] Create server (e.g., "TMNT Squad")
- [ ] Create channels:
  - `#command-center` — Strategy & coordination
  - `#brinc-general`, `#brinc-private` — Project-specific
  - `#squad-updates` — Announcements
- [ ] Note Guild ID and Channel IDs

### 37. Generate Bot Invite URLs

For each bot, construct invite URL:
```
https://discord.com/oauth2/authorize?client_id={APP_ID}&permissions=68608&scope=bot
```

Permissions 68608 = View Channels + Send Messages + Read Message History

- [ ] Invite all bots to server

### 38. Configure Discord in Agent Config

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "BOT_TOKEN_HERE",
      "allowBots": true,
      "groupPolicy": "allowlist",
      "guilds": {
        "GUILD_ID": {
          "slug": "server-name",
          "requireMention": false,
          "channels": {
            "channel-name": { "allow": true }
          }
        }
      }
    }
  },
  "plugins": {
    "entries": {
      "discord": { "enabled": true }
    }
  }
}
```

**CRITICAL:** `allowBots: true` is required for agents to see each other's messages!

### 39. Set Channel Permissions (If Channels Are Private)

If bots can send but not see channels, use Discord API to add permissions:

```bash
BOT_TOKEN="your-admin-bot-token"
TARGET_BOT_ID="bot-to-grant-access"
CHANNEL_ID="channel-id"

curl -X PUT "https://discord.com/api/v10/channels/$CHANNEL_ID/permissions/$TARGET_BOT_ID" \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"allow": "68608", "type": 1}'
```

Run for each channel × each bot.

### 40. Test Agent-to-Agent Discord

- [ ] Agent A sends message to channel
- [ ] Agent B sees message and responds
- [ ] Both agents can communicate without human relay

---

## Post-Onboarding

### 41. Update Documentation

Molty updates:
- [ ] MEMORY.md — Add agent to team roster
- [ ] memory/YYYY-MM-DD.md — Document onboarding
- [ ] This checklist — Note any issues/lessons

### 36. Ongoing Monitoring

First week:
- [ ] Check heartbeat is running
- [ ] Check backup cron fires
- [ ] Review agent's daily memory files
- [ ] Address any issues

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Port 8080 in use" | Remove `gateway.bind` or set to `"loopback"` |
| Memory search fails | Check GOOGLE_API_KEY is set in env |
| Webhook 401 error | Check token matches on both sides |
| Backup fails | Check disk space, permissions |
| Can't reach other agent | Check both webhooks enabled, URLs correct |

### Emergency Recovery

If agent is completely broken:
1. Check Railway logs for errors
2. Try restarting via Railway dashboard
3. If config corrupted, restore from backup
4. See RECOVERY.md for full restore steps

---

## Appendix: File Templates

### A. Minimal SOUL.md Template
```markdown
# SOUL.md - {Agent Name} {Emoji}

## Identity
- **Name:** {Name}
- **Role:** {Project} Lead
- **Emoji:** {Emoji}

## Personality
- {Trait 1}
- {Trait 2}
- {Trait 3}

## Responsibilities
- {Responsibility 1}
- {Responsibility 2}

## Boundaries
- **Your domain:** {Project}-related work
- **Ask Molty:** Cross-project, strategic decisions
- **Ask Guillermo:** External comms, spending, major commitments

## When in Doubt
1. Is it in your domain? → Handle it
2. Crosses projects? → Ask Molty
3. Affects Guillermo externally? → Always ask first
```

### B. Minimal AGENTS.md Sections to Include
- Write It Down (no mental notes)
- Action Items - Capture Immediately
- Safety rules
- External vs Internal actions
- Memory protocol

### C. Backup Script Template
See Phase 3, Step 15.

---

## Checklist Summary

Total items: ~36 steps across 8 phases

**Critical path (minimum viable agent):**
1. Railway deployed ✓
2. Identity files ✓
3. Webhooks enabled
4. AGENTS.md sent
5. Backup system created
6. Memory search working
7. Domain KB transferred
8. Team briefing complete
9. Communication tested

**Time estimate:**
- Phases 1-3: 30-45 min
- Phases 4-6: 30-45 min
- Phases 7-8: 15-30 min
- **Total: 1-2 hours**

---

## Lessons Learned (2026-02-04)

### Discord Setup Lessons

1. **Bot invites require human action** — Bots cannot invite other bots. Generate the OAuth URL and have a human click it.

2. **Server permissions ≠ Channel permissions** — Even if a bot has server-level permissions, private channels need explicit permission overwrites via Discord API.

3. **`allowBots: true` is critical** — By default, OpenClaw ignores messages from other bots. Enable this for agent-to-agent communication.

4. **Admin bot can grant permissions** — If one bot has Administrator, it can add other bots to channels via the Discord API (no human needed for channel permissions).

5. **Decode bot ID from token** — First part of Discord bot token is base64-encoded application ID: `echo "TOKEN_FIRST_PART" | base64 -d`

### General Onboarding Lessons

6. **Do it yourself first** — When you have access to a system (Discord, Notion, GitHub), don't give instructions to the human — check if you can do it yourself first.

7. **Think ahead about the full flow** — When setting up step A, anticipate what step B will need (permissions, invites, config settings).

8. **Anticipate needs proactively** — If you just configured one bot, you know the other bot needs the same setup. Provide everything upfront.

9. **Research before responding** — Prefer spending time investigating the complete solution over giving quick partial answers.

10. **Store credentials immediately** — When you receive ANY credential or token, write it to TOOLS.md immediately — don't just use it and forget.

### Syncthing/Filesystem Lessons (2026-02-04)

11. **Use project-specific shares, not one big folder** — Don't share `/data/shared` as one folder. Create separate shares per project (`brinc-kb`, `cerebro-kb`, etc.) to enforce isolation at the Syncthing level.

12. **Consistent folder ID naming** — Use pattern `{project}-kb` for KB folders, `mv-projects-{project}` for memory-vault project folders. This makes it easy to add new agents without confusion.

13. **sendonly for read-only shares** — Use `type: "sendonly"` on Molty's side for folders that agents shouldn't modify (resources, squad, people). Agents should set `type: "receiveonly"` on their end.

14. **Shared folders need .stfolder markers** — Create `.stfolder` file in each new folder before adding it to Syncthing.

15. **Agent isolation = folder isolation** — An agent should only see folders for their project + the common read-only folders. They should NEVER see other projects' KB folders or project items.

---

*SOP Version: 2.1 | Last Updated: 2026-02-04 | Author: Molty*
