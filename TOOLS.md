# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

---

## Discord Channel Ownership

**Check this before responding in shared channels!**

| Channel | ID | Owner | Non-owners |
|---------|-----|-------|------------|
| `#command-center` | 1468164160398557216 | **Molty** 🦎 | @mention only |
| `#brinc-marketing` | 1469590792900186245 | **Raphael** 🔴 | @mention only |
| `#brinc-sales` | 1470416628272463976 | **Raphael** 🔴 | @mention only |

### Forum Channels (📋 Forums category)
| Forum | ID | Purpose |
|-------|-----|---------|
| `#squad-decisions` | 1470223676845723771 | Key decisions, architecture choices, lessons |
| `#project-updates` | 1470223696349237445 | Project status reports per milestone |
| `#research-findings` | 1470223714112245873 | Research reports, skill evals, market intel |

**Forum rules:** One thread per topic. All agents can create threads and post. Use threads to keep context together instead of flat messages.
| `#squad-updates` | 1468164181155909743 | **Molty** 🦎 | Read-only |
| `#brinc-private` | 1468164139674238976 | **Raphael** 🔴 | @mention only |
| `#brinc-general` | 1468164121420628081 | **Raphael** 🔴 | @mention only |

**Rule:** If you don't own the channel, stay silent unless @mentioned or Guillermo explicitly asks you something.

---

## Guillermo's Discord

**User ID:** `779143499655151646`
**Pairing:** ✅ Approved (2026-02-06)

---

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 📧 Gmail Access (WORKING!)

**I HAVE EMAIL. USE IT.**

| What | Value |
|------|-------|
| My email | `ggv.molt@gmail.com` |
| Guillermo's email | `guillermo.ginesta@gmail.com` |
| Script | `/data/workspace/scripts/gmail.sh` |

**Quick commands:**
```bash
# Send email
gmail.sh send "to@email.com" "Subject" "Body"

# List messages
gmail.sh list

# Read unread
gmail.sh unread

# Search
gmail.sh search "from:someone"
```

---

Add whatever helps you do your job. This is your cheat sheet.

---

## ✅ Railway

**Auth:** OAuth session via `railway login` (logged in as guillermo.ginesta@gmail.com)
**Workspace API Token:** `43d18daf-9d26-4c19-bd0b-74b5cc60306a` (Personal token, name: "Molty")
**⚠️ CLI uses OAuth by default** — don't set RAILWAY_TOKEN env var unless OAuth expires. OAuth is preferred.
**⚠️ If OAuth expires:** Run `railway login --browserless` (needs PTY + 120s timeout), ask Guillermo to approve the pairing code.
**⚠️ API Token note:** Workspace personal tokens may need `RAILWAY_TOKEN` env var set explicitly for API/CLI use.
**Projects:** Molty, raphael, webclaw, positive-consideration, wonderful-harmony (Proposal Studio)
**If CLI breaks:** Run `railway login` to re-authenticate

### Proposal Studio (wonderful-harmony)
| Service | Railway Name | URL |
|---------|-------------|-----|
| Frontend | wonderful-harmony | <https://wonderful-harmony-production.up.railway.app> |
| Backend | considerate-light | <https://considerate-light-production.up.railway.app> |

**Project ID:** `001331eb-af71-4ab5-9c3a-8e6589dbc409`
**Local source:** `/data/workspace/proposal-studio/` (frontend) + `/data/workspace/proposal-studio/backend/`
**Auth:** @brinc.io and @gmail.com domains allowed

---

## ✅ Todoist API

**Token:** `/data/workspace/credentials/todoist.env`
**API:** REST v2 (https://api.todoist.com/rest/v2/)
**Status:** ✅ Connected (2026-02-05)

### Projects
| ID | Name | Notes |
|----|------|-------|
| 2300781375 | Inbox | Guillermo dumps raw tasks here → I process them |
| 2300781387 | Personal 🙂 | Personal tasks |
| 2300781386 | Brinc 🔴 | Brinc corporate tasks (coordinate with Raphael) |
| 2329980736 | Wedding 💍 | Shared project |
| 2330246839 | Mana Capital 🟠 | Investment/PE tasks |
| 2366746501 | Molty's Den 🦎 | Meta/infrastructure/agent tasks |

### Raphael's Brinc Tasks (Notion)
- **DB ID:** `2fe39dd69afd810ba2c3e793e8ea8993`
- **URL:** https://www.notion.so/2fe39dd69afd810ba2c3e793e8ea8993
- **Statuses:** Backlog → Next → Doing → Blocked → Review → Done
- **Priorities:** P1/P2/P3/P4 (Eisenhower)
- **Flow:** Todoist → Molty processes → Discord relay → Raphael mirrors in Notion

### Daily Standup (Notion)
- **DB ID:** `2fe39dd69afd81f189f7e58925dad602`
- **URL:** https://www.notion.so/2fe39dd69afd81f189f7e58925dad602
- **Parent:** Molty's Mission Control
- **Format:** Inline table per standup with columns: Task, Section, Project, Owner, Priority, Due Date, Time Est., Action, Molty's Notes, Your Comments
- **Flow:** I create page + inline table at 5PM → Guillermo reviews in Notion → pings "standup done" → I process decisions in Todoist

### Inbox Processing System
- **Flow:** Guillermo dumps → I process hourly → Review at daily standup (5PM HKT)
- **Processing:** Rewrite title, expand description, estimate duration, assign project, set priority
- **Priority mapping:** P1=DO NOW, P2=SCHEDULE, P3=DELEGATE, P4=DEFER (⚠️ Todoist API is inverted: priority=4 is P1!)
- **Ideas:** Tagged with `@idea`, noted for standup discussion
- **Protocol:** See `/data/workspace/scripts/process-inbox.md`

### Daily Standup
- **Time:** 5:00 PM HKT (09:00 UTC) daily
- **Channel:** Webchat first → Telegram fallback after 15min
- **Cron Job:** `bdb28765-f508-4271-a04d-9408d39f49fd`
- **Agenda:** Completed today → Overdue → Inbox triage → Tomorrow planning

### Quick API Examples
```bash
source /data/workspace/credentials/todoist.env

# List projects
curl -s https://api.todoist.com/rest/v2/projects -H "Authorization: Bearer $TODOIST_API_TOKEN"

# List tasks
curl -s https://api.todoist.com/rest/v2/tasks -H "Authorization: Bearer $TODOIST_API_TOKEN"

# Add task
curl -s -X POST https://api.todoist.com/rest/v2/tasks \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Task name", "project_id": "2300781375"}'
```

---

## 🐦 Twitter/X (@Molton_Sanchez)

**Account:** @Molton_Sanchez (Molty Moltensson)
**User ID:** 2017943260631588864
**CLI:** `bird` (installed globally via npm)
**Credentials:** `/data/workspace/credentials/twitter.env`

### Quick Commands
```bash
# Always export creds first
export AUTH_TOKEN="..." CT0="..."

# Check auth
bird whoami

# Search
bird search "query" -n 5

# Read tweet/thread
bird read <url-or-id>
bird thread <url-or-id>

# Post (confirm with user first!)
bird tweet "text"
bird reply <id-or-url> "text"
```

### Rules
- **READ-ONLY MODE** — Account is new, posting blocked by Twitter bot detection
- When Guillermo shares X links → use `bird read` or `bird thread`
- Posting disabled until account warms up (try again in a few days)
- When posting enabled: always confirm with Guillermo first

---

## GitHub API

**Token:** `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`
**Scope:** Repo access for openclaw/openclaw issue submission
**Added:** 2026-02-03 (received via Telegram)

### Submit Issue via API
```bash
curl -X POST https://api.github.com/repos/openclaw/openclaw/issues \
  -H "Authorization: token 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" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{"title": "...", "body": "..."}'
```
