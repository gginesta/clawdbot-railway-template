# PLAN-004: Morning Briefing — Squad Status Integration
**Created:** 2026-02-24  
**Status:** ✅ COMPLETE (implemented 2026-02-24)  
**Author:** Molty 🦎

---

## Problem

Two separate morning messages were being sent:
1. **06:30 HKT** — Daily Morning Briefing (personal: calendar, tasks, email)
2. **08:00 HKT** — MC Daily Standup (squad: agent activity, P0s, blockers from MC)

These served different purposes in theory but were redundant in practice — especially after PLAN-001 established Todoist↔MC sync. Guillermo was getting two Telegram messages 90 minutes apart covering overlapping data.

---

## Solution

Merged squad status into the morning briefing as a new Section 5. Retired the 08:00 MC standup cron.

**New briefing structure (06:30 HKT):**
1. 🌤️ Weather
2. 📅 Today's calendar
3. ✅ Tasks due (P1/P2)
4. 🐢 Squad (NEW — from Mission Control)
5. 🔜 Next 5 days
6. ✉️ Email
7. 🌙 Overnight work
8. 🔧 OpenClaw update

---

## What the Squad Section Shows

```
🐢 Squad
🔴 P0 CRITICAL:        (only if any exist)
  • [task] [🦎 molty]
🧱 Blocked:            (only if any exist)
  • [task] (raphael)
🦎 molty: ⚡ [current task]
🔴 raphael: ⚡ [current task]
🔵 leonardo: ⚡ [current task]
Your MC queue:         (only if Guillermo has tasks in MC)
  🟡 [task]
  🔵 [task]
All clear — no P0s or blockers  (when nothing critical)
```

**Status symbols:** ⚡ in_progress | 👀 review | 📋 assigned

---

## Implementation

**File:** `/data/workspace/scripts/morning_briefing.py`

**New function:** `get_squad_status(errors)` → `SquadStatus | None`
- Calls `GET /api/tasks` on MC (10s timeout, graceful fallback)
- Returns: p0_tasks, blocked_tasks, agent_tasks, guillermo_queue
- If MC unavailable → shows "⚠️ MC unavailable" in briefing, doesn't crash

**New dataclass:** `SquadStatus`

**`build_message()`:** Added `squad: SquadStatus | None` parameter; renders section 5

---

## Cron Changes

| Cron | Before | After |
|------|--------|-------|
| `8b748f23` — Daily Morning Briefing | runs morning_briefing.py | unchanged (new section auto-included) |
| `62aaf754` — MC Daily Standup | active (08:00 HKT) | **disabled** |

---

## Files Touched

1. `/data/workspace/scripts/morning_briefing.py` — added Squad section
2. `/data/.openclaw/cron/jobs.json` — `62aaf754` disabled

---

## Commit

`a7c8ef41` — 2026-02-24
