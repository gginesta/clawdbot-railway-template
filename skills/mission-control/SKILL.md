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

All requests need `Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc` and `Content-Type: application/json`.

## Endpoints

### POST /api/activity
Log an activity to The Sewer feed.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/activity \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
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
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"agentId":"molty","status":"active","currentTask":"Building MC skill"}'
```

**Required:** `agentId`, `status` (active|idle|error|offline)
**Optional:** `currentTask`

### POST /api/heartbeat
Ping to confirm agent is alive. Sets status to active + updates lastHeartbeat.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/heartbeat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"agentId":"molty","currentTask":"Processing morning briefing"}'
```

**Required:** `agentId`
**Optional:** `currentTask`

### PATCH /api/task
Update an existing task's status, priority, assignees, or other fields.

```bash
curl -s -X PATCH https://resilient-chinchilla-241.convex.site/api/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"id":"<task_id>","status":"done"}'
```

**Required:** `id` (task `_id` from GET /api/tasks)
**Optional:** `status` (inbox|assigned|in_progress|review|done|blocked), `title`, `description`, `priority`, `assignees`, `dueDate`, `tags`

To get task IDs: `GET /api/tasks?project=cerebro` — returns `_id` field on each task.

### POST /api/task
Create a task on the War Room board.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"title":"Review proposal","project":"brinc","priority":"p1","assignees":["raphael"],"createdBy":"molty"}'
```

**Required:** `title`, `project`, `createdBy`
**Optional:** `description`, `priority` (p0|p1|p2|p3, default p2), `assignees` (string[]), `dueDate` (ISO), `tags`, `status` (inbox|assigned|in_progress|review|done|blocked)

### PATCH /api/task
Update task status or fields. Use `id` (the Convex document ID from GET /api/tasks).

```bash
curl -s -X PATCH https://resilient-chinchilla-241.convex.site/api/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"id":"<convex-task-id>","status":"done"}'
```

**Required:** `id` (Convex document ID — from GET /api/tasks response as `_id` field)
**Optional:** `status` (inbox|assigned|in_progress|review|done|blocked), `title`, `priority`, `assignees`, `dueDate`, `tags`, `description`

⚠️ Field is `id`, NOT `taskId`.

### GET /api/tasks
Query tasks. Returns JSON array.

```bash
curl -s "https://resilient-chinchilla-241.convex.site/api/tasks?assignee=molty" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
```

**Params:** `assignee`, `status`, `project`

### POST /api/memory
Push a memory summary to The Vault.

```bash
curl -s -X POST https://resilient-chinchilla-241.convex.site/api/memory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"agentId":"molty","date":"2026-02-23","title":"Phase 2 build day","content":"# Summary\n...markdown...","source":"memory/2026-02-23.md"}'
```

**Required:** `agentId`, `date`, `title`, `content`, `source`
**Optional:** `tags` (string[])
**Note:** Upserts — same agent + date + source will update existing entry.

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
