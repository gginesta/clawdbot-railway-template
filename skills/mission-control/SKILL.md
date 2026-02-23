---
name: mission-control
description: Post activity, update status, create tasks, and send heartbeats to TMNT Mission Control (Convex backend). Use when agent needs to report work, update fleet status, or manage shared tasks.
---

# Mission Control Skill

Post to the TMNT Mission Control dashboard via its Convex HTTP API.

## API Base

```
https://resilient-chinchilla-241.convex.site
```

All requests need `Authorization: Bearer tmnt-fleet-key` and `Content-Type: application/json`.

## Endpoints

### POST /api/activity
Log an activity to The Sewer feed.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/activity \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tmnt-fleet-key" \
  -d '{"agentId":"molty","type":"task_update","title":"Completed proposal draft","body":"Optional details","project":"brinc"}'
```

**Required:** `agentId`, `type`, `title`
**Optional:** `body`, `project` (brinc|cerebro|mana|personal|fleet), `subAgentId`, `metadata`
**Types:** task_created, task_updated, status_change, heartbeat, memory_write, deploy, message, comment

### POST /api/status
Update agent status and current task.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tmnt-fleet-key" \
  -d '{"agentId":"molty","status":"active","currentTask":"Building MC skill"}'
```

**Required:** `agentId`, `status` (active|idle|error|offline)
**Optional:** `currentTask`

### POST /api/heartbeat
Ping to confirm agent is alive. Sets status to active + updates lastHeartbeat.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/heartbeat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tmnt-fleet-key" \
  -d '{"agentId":"molty","currentTask":"Processing morning briefing"}'
```

**Required:** `agentId`
**Optional:** `currentTask`

### POST /api/task
Create a task on the War Room board.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tmnt-fleet-key" \
  -d '{"title":"Review proposal","project":"brinc","priority":"p1","assignees":["raphael"],"createdBy":"molty"}'
```

**Required:** `title`, `project`, `createdBy`
**Optional:** `description`, `priority` (p0|p1|p2|p3, default p2), `assignees` (string[]), `dueDate` (ISO), `tags`, `status` (inbox|assigned|in_progress|review|done|blocked)

### GET /api/tasks
Query tasks. Returns JSON array.

```bash
curl -s "https://resilient-chinchilla-241.convex.site/api/tasks?assignee=molty" \
  -H "Authorization: Bearer tmnt-fleet-key"
```

**Params:** `assignee`, `status`, `project`

## Agent IDs
- `molty` — Molty 🦎
- `raphael` — Raphael 🔴
- `leonardo` — Leonardo 🔵
- `donatello` — Donatello 🟣
- `michelangelo` — Michelangelo 🟠
- `april` — April 📰
- `guillermo` — Guillermo 👤

## When to Post
- **Activity:** After completing meaningful work (task done, deploy, memory write, message sent)
- **Status:** When starting/finishing a task session, or changing operational state
- **Heartbeat:** On every heartbeat cycle (keeps Turtle Tracker current)
- **Task:** When new work is identified that should be tracked fleet-wide

## Dashboard
https://tmnt-mission-control.vercel.app
