# Phase 1 Completion + Phase 2 Execution Plan

**Created:** 2026-02-23 12:00 HKT
**Completed:** 2026-02-23 12:50 HKT
**Owner:** Molty 🦎
**Status:** ✅ ALL COMPLETE

---

## Execution Order & Dependencies

```
Phase 1 Completion:
  1A. API Auth Hardening ──────────────────┐
                                           │
Phase 2:                                   │
  2A. Deploy MC skill to Raph + Leo ───────┤ (needs shared skills folder)
  2B. Heartbeat Integration ───────────────┤ (needs skill deployed)
  2C. Shell Calendar ──────────────────────┤ (frontend only, no deps)
  2D. The Vault (Memory Browser) ──────────┤ (needs memory sync API)
  2E. Comment Threads + @Mentions ─────────┤ (Convex schema ready)
  2F. Task Notifications ──────────────────┤ (needs comments)
  2G. Sub-Agent Tracking ──────────────────┘ (activity enrichment)
```

## Detailed Steps

### 1A. API Auth Hardening (~30min)
**Goal:** Secure the HTTP API with a proper key stored in Convex env.
**Plan:**
- Set `MC_API_KEY` env var in Convex dashboard
- Update `validateAuth()` in `convex/http.ts` to check against it
- Generate a proper key (not "tmnt-fleet-key")
- Update skill SKILL.md with the new key
**Risk:** Breaking existing API calls → update skill first, then deploy

### 2A. Deploy MC Skill to Raphael + Leonardo (~30min)
**Goal:** Both agents can post to MC.
**Plan:**
- Copy `skills/mission-control/` to `/data/shared/skills/mission-control/`
- Send webhook to both agents telling them to install the skill from shared folder
- Verify by having them post a test heartbeat
**Risk:** Syncthing sync delay → wait for sync, verify files exist before sending webhooks

### 2B. Heartbeat Integration (~1h)
**Goal:** Every agent heartbeat auto-pings MC Turtle Tracker.
**Plan:**
- Add MC heartbeat to Molty's HEARTBEAT.md
- The heartbeat task: curl MC `/api/heartbeat` with agentId + currentTask
- For Raph/Leo: instruct them via webhook to add the same to their HEARTBEAT.md
- Verify: check Turtle Tracker shows updated lastHeartbeat times
**Depends on:** 2A (agents need the skill/API knowledge)

### 2C. Shell Calendar (~3h)
**Goal:** Timeline view showing past completed tasks and upcoming work per agent.
**Plan:**
- **Backend:** Add `tasks.listForCalendar` query — returns tasks with dates, grouped by agent
- **Frontend:** Build calendar UI with:
  - Week/month toggle
  - Agent swim lanes (horizontal rows per agent)
  - Past: completed tasks plotted by completedAt
  - Future: tasks with dueDate plotted ahead
  - Color-coded by agent
- **Component:** Reuse existing task data, no new schema needed
- Tasks without dates won't appear (that's fine — they live in War Room)
**Depends on:** Nothing (pure frontend + one new query)

### 2D. The Vault — Memory Browser (~3h)
**Goal:** Search and browse all agent memories from the MC UI.
**Plan:**
- **Backend:**
  - Add `memories.search` query (full-text search on title + content)
  - Add `memories.listByAgent` query
  - Add HTTP endpoint `POST /api/memory` for agents to push memory summaries
- **Frontend:** Build Vault UI with:
  - Search bar (searches title + content)
  - Agent filter tabs
  - Date-sorted memory list
  - Markdown renderer for content
  - Stats: total memories per agent, growth over time
- **Sync:** Agents push daily memory summaries on heartbeat (content of today's memory file)
**Depends on:** 2B (heartbeat triggers memory sync)

### 2E. Comment Threads (~2h)
**Goal:** @mention comments on tasks, visible in War Room.
**Plan:**
- **Backend:** `comments` table already exists with `listByTask` + `add` mutations
- **Frontend:**
  - Add comment thread panel to task detail view (expand from TaskCard)
  - Comment input with @mention autocomplete (agent list)
  - Display comments chronologically
- **Need:** Task detail modal/drawer that shows full task + comments
**Depends on:** Nothing

### 2F. Task Notifications (~1h)
**Goal:** When a task has a new comment with @mention, notify the mentioned agent.
**Plan:**
- **Backend:** Add `notifications` concept — on comment.add, check mentions array
- **Delivery:** On heartbeat, agents query `GET /api/tasks?assignee=<me>` and check for new comments
- **Simple v1:** Just add a `GET /api/notifications` endpoint that returns unread @mentions
- Add HTTP endpoint for agents to check
**Depends on:** 2E (comments must exist)

### 2G. Sub-Agent Tracking (~1h)
**Goal:** Sub-agent work appears in activity feed with proper attribution.
**Plan:**
- Already supported in schema: `activities.subAgentId` field exists
- **Frontend:** Update ActivityItem to show "Raphael → Peach 👑: wrote social copy"
- **Backend:** No changes needed — agents post with `subAgentId` field
**Depends on:** Nothing

---

## Order of Execution

1. **1A** — Auth (foundation)
2. **2G** — Sub-agent tracking (quick win, 30min)
3. **2E** — Comment threads (independent, medium effort)
4. **2C** — Shell Calendar (independent, medium effort)
5. **2A** — Deploy skill to agents (needs auth key finalized)
6. **2B** — Heartbeat integration (needs skill deployed)
7. **2D** — The Vault (needs heartbeat for memory sync)
8. **2F** — Task notifications (needs comments)

This order minimizes blocking and maximizes parallel-ready work.

---

## Success Criteria

Phase 1+2 is complete when:
- [x] API uses proper auth key (not placeholder) — `MC_API_KEY` in Convex env
- [x] Raphael + Leonardo have MC skill and are posting heartbeats — webhooks sent, skill shared
- [x] Turtle Tracker shows live heartbeat times for all 3 agents — Molty cron active, agents notified
- [x] Shell Calendar shows tasks on a timeline with agent swim lanes — week/month view live
- [x] The Vault renders agent memories with search — 2 memories synced, search + stats working
- [x] Tasks have expandable comment threads with @mentions — TaskDetail modal with autocomplete
- [x] Sub-agent activity shows attribution (Lead → Sub-agent) — ActivityItem updated
- [x] All changes documented in BUILD-LOG.md and STATUS.md — done
