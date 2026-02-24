# PLAN-001: Standup Sync Fix
**Created:** 2026-02-24  
**Status:** Approved — pending execution  
**Author:** Molty 🦎

---

## Problem

Three disconnected systems (Todoist, Mission Control/Convex, Notion) with no completion propagation. When Guillermo marks a task done in Todoist, Mission Control stays stale. The 08:00 standup reads MC directly and shows closed tasks as active (e.g. IRD reply appeared as P0 this morning despite being closed yesterday at 5PM).

---

## Audit Findings

| System | Role | Problem |
|---|---|---|
| Todoist | Source of truth | Completions don't propagate out |
| Mission Control (Convex) | Fleet dashboard | Independent task DB — gets stale |
| Notion standup | Generated view | Read-only, no write-back |
| 5PM standup cron (bdb28765) | Runs daily_standup.py + Telegram summary | No completion sync |
| 08:00 MC standup cron (62aaf754) | Reads MC Convex directly | Never validates against Todoist |

**Root cause:** `mc-todoist-sync.sh` pushes active tasks Todoist → MC but never closes completed ones. MC accumulates stale tasks indefinitely.

**Todoist note:** `/api/v1/tasks/completed/get_all` returns 404 on v1. Approach instead: diff Todoist active task list vs MC open tasks — anything in MC with a `todoistId` missing from Todoist active list = completed.

---

## Change 1 — New Completion Sync Script (foundation)

**File:** `/data/workspace/scripts/mc-completion-sync.sh`

**Logic:**
1. `GET /api/v1/tasks` from Todoist → collect all active todoistIds
2. `GET /api/tasks` from MC → collect all non-`done` tasks that have a `todoistId`
3. For each MC task whose `todoistId` is NOT in the Todoist active set → `PATCH /api/task {id, status: "done"}`

**Safety:** Only touches MC tasks with a `todoistId`. Manual MC tasks (no Todoist link) are never touched. Idempotent.

**Also wire into:** MC Heartbeat cron (46d1ca32) — add one line to payload so sync runs every 2h.

---

## Change 2 — 5PM Standup Pre-Syncs Before Running

**Cron:** `bdb28765` — Daily Standup 5PM HKT  
**Change:** Run `mc-completion-sync.sh` before `daily_standup.py`

**Why:** By 5PM Todoist reflects the full day's completions. Syncing first means Notion page + Telegram summary both reflect reality.

**Why not "standup done" trigger:** Conversational triggers are fragile. Time-based is deterministic.

**Payload edit:** `bash /data/workspace/scripts/mc-completion-sync.sh && python3 /data/workspace/scripts/daily_standup.py`

---

## Change 3 — 08:00 MC Standup Pre-Syncs Before Generating

**Cron:** `62aaf754` — MC Daily Standup  
**Change:** Run `mc-completion-sync.sh` first, then query MC for the report

**Effect:** Overnight Todoist completions flushed to MC before the morning report generates. No more stale P0s.

---

## Dependency Order

```
C1 (build script)  →  C2 (update 5PM cron payload)
                   →  C3 (update 08:00 cron payload)
```

C1 must ship first. C2 and C3 are cron payload edits only.

---

## What This Doesn't Fix (by design)

- Manual MC tasks with no `todoistId` — won't auto-close (agent-created tasks need explicit MC update)
- Same-day lag on heartbeat — if Todoist closes at 10am, MC catches up at next heartbeat (max 2h). 5PM + 08:00 syncs cover high-value moments.

---

## Risk Assessment

| Change | Risk | Mitigation |
|---|---|---|
| C1: New sync script | Low | Only matches on todoistId, never deletes |
| C2: 5PM cron edit | Low | Additive — sync runs before existing script |
| C3: 08:00 cron edit | Low | Additive — sync runs before existing query |

**Blast radius:** 1 new script, 2 cron payload edits. Worst case: wrong task closed → recoverable with PATCH back to `assigned`.

---

## Files to Touch

1. `/data/workspace/scripts/mc-completion-sync.sh` — NEW
2. Cron payload: `46d1ca32` (MC Heartbeat) — add sync call
3. Cron payload: `bdb28765` (5PM Standup) — prepend sync call  
4. Cron payload: `62aaf754` (08:00 MC Standup) — prepend sync call
