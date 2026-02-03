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

## Post-Onboarding

### 35. Update Documentation

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

*SOP Version: 2.0 | Last Updated: 2026-02-03 | Author: Molty*
