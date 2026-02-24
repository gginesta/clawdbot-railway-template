# PLAN-001: Bidirectional Todoist ↔ Mission Control Sync
**Created:** 2026-02-24  
**Revised:** 2026-02-24 (v2 — bidirectional model)  
**Status:** Awaiting approval to implement  
**Author:** Molty 🦎

---

## Mental Model

Two systems, two purposes — neither is a mirror of the other:

| System | Role |
|--------|------|
| **Todoist** | Guillermo's personal action list — atomic tasks, daily commitments, reminders |
| **Mission Control** | Squad project management — projects, milestones, multi-step work, agent tasks |

**The link:** An MC task can optionally carry a `todoistId`. If it does, the two tasks are linked and completion syncs bidirectionally. If it doesn't, it lives only in MC (sub-tasks, agent work, milestones).

---

## Sync Rules (Option C)

### Todoist → MC (project-based with opt-out)

| Todoist task condition | Action |
|------------------------|--------|
| In Brinc or Cerebro project | Sync to MC by default |
| Has `@personal` label | Stay in Todoist only (opt-out) |
| In Inbox / Personal / Molty's Den | Todoist-only unless `@mc` label present |
| Has `@mc` label (any project) | Force sync to MC |

When a Todoist task is synced to MC:
1. Create MC task (if not already exists)
2. Store Todoist task `id` as `todoistId` on the MC task
3. Map Todoist priority (p4→p3, p3→p2, p2→p1, p1→p0)
4. Map Todoist project to MC project field

### MC → Todoist (reverse — agent-assigned tasks)

When an MC task is assigned to `guillermo` AND has no `todoistId`:
1. Auto-create Todoist task in the matching project
2. Write the Todoist task ID back to MC as `todoistId`
3. This covers: Raphael/Leonardo assigning Guillermo a blocker or action item

### Completion Sync (bidirectional)

- **Todoist done → MC done:** Active Todoist task list diff vs MC open tasks with `todoistId`. Missing from Todoist active = completed → PATCH MC `status: done`
- **MC done → Todoist complete:** When MC task is marked done and has `todoistId` → call Todoist complete API

---

## Notion Standup "In MC?" Column

Add a checkbox column to the daily standup database: **"In MC?"**

**Pre-fill logic (Molty sets on task creation):**
- Brinc or Cerebro project + no `@personal` label → ✅ checked
- `@mc` label → ✅ checked  
- Inbox / Personal / Molty's Den / `@personal` label → ☐ unchecked

Guillermo can override by ticking/unticking in Notion.

**Purpose:** Visibility + control. Not a sync trigger — just confirms which tasks will appear in MC. Standup reads from MC as the project view.

---

## Required Schema Change (MC Convex)

The MC `tasks` table has no `todoistId` field. Need to add:

```typescript
// In convex/schema.ts — tasks table
todoistId: v.optional(v.string()),
```

And a new mutation in `convex/tasks.ts`:
```typescript
export const setTodoistId = mutation({
  args: { id: v.id("tasks"), todoistId: v.string() },
  handler: async (ctx, { id, todoistId }) => {
    await ctx.db.patch(id, { todoistId, updatedAt: Date.now() });
  },
});
```

And expose via HTTP API in `convex/http.ts`:
```
PATCH /api/task  (extend existing handler to accept todoistId field)
```

**This is the foundation — nothing else works without it.**

---

## Todoist Projects → MC Projects Mapping

| Todoist Project ID | Name | MC Project | Sync? |
|--------------------|------|------------|-------|
| `6M5rpGgV6q865hrX` | Brinc 🔴 | `brinc` | ✅ Yes (default) |
| `6Rr9p6MxWHFwHXGC` | Mana Capital 🟠 | `mana` | ✅ Yes (default) |
| `6M5rpCXmg7x7RC2Q` | Inbox | `personal` | ❌ No (unless `@mc`) |
| `6M5rpGfw5jR9Qg9R` | Personal 🙂 | `personal` | ❌ No (unless `@mc`) |
| `6fwH32grqrCJF23R` | Molty's Den 🦎 | `fleet` | ❌ No (Molty's internal) |
| `6fx5GV7Q93Hp4QgM` | Ideas 💡 | — | ❌ No |
| *(none yet)* | Cerebro | `cerebro` | ✅ Once created |

> **Note:** No Cerebro project in Todoist yet. When created, add its ID to the synced set.  
> Molty's Den tasks assigned to Molty → `fleet` project, not synced to Guillermo's standup.

---

## Implementation Plan

### Phase 0 — MC Schema Change
**Files:** `tmnt-mission-control/convex/schema.ts`, `tmnt-mission-control/convex/tasks.ts`, `tmnt-mission-control/convex/http.ts`

Add `todoistId` field + `setTodoistId` mutation + extend PATCH endpoint.
Redeploy Convex (`npx convex deploy`).

**Risk:** Low — additive schema change, existing tasks unaffected (field is optional).

---

### Phase 1 — Core Sync Script
**File:** `/data/workspace/scripts/mc-todoist-sync-v2.sh` (replaces old `mc-todoist-sync.sh`)

**Logic block 1 — Todoist → MC (new tasks):**
```
fetch Todoist active tasks from Brinc + Cerebro projects
filter out @personal label
for each task not already in MC (no matching todoistId):
  create MC task via POST /api/task
  write todoistId back to new MC task via PATCH /api/task
```

**Logic block 2 — MC → Todoist (Guillermo-assigned tasks):**
```
fetch MC tasks where assignees contains 'guillermo' AND no todoistId
for each such task:
  create Todoist task in matching project
  PATCH MC task with new todoistId
```

**Logic block 3 — Completion sync:**
```
fetch Todoist active task IDs
fetch MC open tasks that have a todoistId
for each MC task whose todoistId is NOT in Todoist active list:
  PATCH MC task status: done
fetch MC tasks with todoistId that are status: done
for each one whose Todoist counterpart is NOT completed:
  POST Todoist /api/v1/tasks/{id}/close
```

**Safety rules:**
- Only touch MC tasks that have a `todoistId` (never blind-close manual MC tasks)
- Idempotent — safe to run multiple times
- Log all changes to `/data/workspace/logs/sync-YYYY-MM-DD.log`

---

### Phase 2 — Notion "In MC?" Column
**File:** `/data/workspace/scripts/daily_standup.py`

In `create_db()` — add checkbox property:
```python
"In MC?": {"checkbox": {}}
```

In task row creation — pre-fill based on project/label rules:
```python
in_mc = task['project_id'] in SYNCED_PROJECTS and '@personal' not in task['labels']
"In MC?": {"checkbox": in_mc}
```

---

### Phase 3 — Wire Sync into Crons

**5PM Standup (`bdb28765`):** Prepend sync script call before `daily_standup.py`  
**08:00 MC Standup (`62aaf754`):** Prepend sync script call before standup generation  
**MC Heartbeat (`46d1ca32`):** Add sync call (Blocks 2+3 only — no new task creation at heartbeat, only completion + reverse-assign checks)

---

## Dependency Order

```
Phase 0 (schema) → Phase 1 (sync script) → Phase 2 (Notion column) → Phase 3 (crons)
```

**Nothing in Phase 1+ works without Phase 0.**

---

## What This Explicitly Does NOT Do

| Scenario | Behaviour |
|----------|-----------|
| MC sub-tasks (no todoistId) | Never touched by sync |
| Agent tasks assigned to Molty/Raphael/Leonardo | Never synced to Todoist |
| Todoist tasks in Personal/Inbox without @mc | Stay in Todoist only |
| Manual MC task completion (no todoistId) | No Todoist write-back |

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 0: Schema change | Low — additive, optional field | Convex handles backwards compat |
| 1: Sync script | Medium — writes to both systems | Dry-run mode first; log all changes |
| 2: Notion column | Low — additive property | Existing standup not affected |
| 3: Cron wiring | Low — prepend only | If sync fails, standup still runs |

**Blast radius:** Convex schema (additive), 1 new script, 3 cron payload edits, 1 standup script edit.

---

## Files to Touch

1. `tmnt-mission-control/convex/schema.ts` — add `todoistId` field
2. `tmnt-mission-control/convex/tasks.ts` — add `setTodoistId` mutation
3. `tmnt-mission-control/convex/http.ts` — extend PATCH handler
4. `/data/workspace/scripts/mc-todoist-sync-v2.sh` — NEW (replaces old sync script)
5. `/data/workspace/scripts/daily_standup.py` — add "In MC?" column
6. Cron payloads: `bdb28765`, `62aaf754`, `46d1ca32`

---

## Open Questions (need resolution before Phase 1)

1. **Cerebro Todoist project** — doesn't exist yet. Create when ready to track Cerebro tasks in Todoist.
2. **Guillermo's Todoist user ID** — `41529748` (confirmed from API). Used to detect MC→Todoist reverse assignments.
3. **MC PATCH endpoint** — currently accepts `status`, `priority`, `title`. Must confirm it will accept `todoistId` field after Phase 0 schema change (test with dry run first).
4. **Guillermo approval** — required before any code is written.
