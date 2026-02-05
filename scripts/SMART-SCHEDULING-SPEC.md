# Smart Scheduling Engine — Technical Specification

**Version:** 1.0  
**Author:** Molty 🦎  
**Date:** 2026-02-05  
**Status:** Draft — Pending standup review  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Algorithm](#2-core-algorithm)
3. [Conflict Resolution](#3-conflict-resolution)
4. [Rescheduling Logic](#4-rescheduling-logic)
5. [Data Model](#5-data-model)
6. [API Interactions](#6-api-interactions)
7. [Edge Cases](#7-edge-cases)
8. [Daily Standup Integration](#8-daily-standup-integration)
9. [Implementation Plan](#9-implementation-plan)

---

## 1. Overview

### What This Is

A Reclaim.ai-style intelligent scheduling engine that automatically places Todoist tasks onto Google Calendar as time blocks, respects energy levels, handles conflicts gracefully, and integrates with Molty's daily standup flow.

### Design Constraints

- **No external frameworks or databases.** State lives in JSON files under `/data/workspace/data/scheduler/`.
- **Python + bash scripts** called by Molty via cron or on-demand.
- **REST APIs only:** Google Calendar API v3, Todoist REST API v2.
- **Timezone:** All internal logic in UTC. Display/rules in HKT (UTC+8).
- **Idempotent:** Running the scheduler twice in a row produces the same result.

### Calendars

| Calendar | ID alias | Write Rule | Visibility on Brinc |
|----------|----------|-----------|---------------------|
| **Brinc** (work) | `brinc` | Work tasks, meetings | Native |
| **Personal** | `personal` | Personal tasks | Busy/Private |
| **Shenanigans** (family) | `shenanigans` | Family events | Busy/Private |

### Key Actors

- **Guillermo** — the human. Reviews schedule at daily standup.
- **Molty** — the AI assistant. Runs the scheduling engine.
- **External humans** — book meetings on Brinc calendar.

---

## 2. Core Algorithm

### 2.1 Scheduling Pipeline

The engine runs as a pipeline with discrete steps:

```
[1] FETCH  →  [2] CLASSIFY  →  [3] SCORE  →  [4] PLACE  →  [5] COMMIT
```

#### Step 1: FETCH

Gather all inputs for the scheduling window (today + next 6 days = 7-day rolling window):

```python
def fetch_inputs(window_start, window_end):
    # 1. All events from all 3 calendars
    brinc_events = gcal_list_events("brinc", window_start, window_end)
    personal_events = gcal_list_events("personal", window_start, window_end)
    family_events = gcal_list_events("shenanigans", window_start, window_end)
    
    # 2. All active Todoist tasks with time estimates
    tasks = todoist_get_active_tasks()
    
    # 3. Current scheduler state (previously placed blocks)
    state = load_json("data/scheduler/state.json")
    
    return {
        "events": merge_events(brinc_events, personal_events, family_events),
        "tasks": tasks,
        "state": state
    }
```

#### Step 2: CLASSIFY

Separate inputs into categories:

| Category | Description | Examples |
|----------|-------------|---------|
| **Fixed** | Immovable. Cannot be rescheduled. | External meetings, school drop-off/pick-up |
| **Anchored** | Strongly preferred time, can shift if needed. | Daily standup (5PM HKT), exercise |
| **Flexible** | Engine-placed task blocks. Can be moved freely. | Todoist task time blocks |
| **Recurring-Fixed** | Fixed events that repeat. | School drop-off Mon/Wed/Fri |

Classification rules:
```python
def classify_event(event):
    # If it has attendees (external people) → Fixed
    if event.get("attendees"):
        return "fixed"
    
    # If tagged by scheduler as a task block → Flexible
    if event.get("extendedProperties", {}).get("private", {}).get("molty_task_id"):
        return "flexible"
    
    # If it's a life commitment (matched by title/pattern) → Fixed or Anchored
    if matches_life_commitment(event):
        return commitment_type(event)  # "fixed" or "anchored"
    
    # Everything else created by human → Fixed
    return "fixed"
```

#### Step 3: SCORE — Find Optimal Slots

For each unscheduled task, compute a **placement score** for every available slot.

**Energy Schedule (HKT):**

| Time Block | HKT | UTC | Energy Type | Best For |
|-----------|-----|-----|------------|----------|
| Deep Work | 09:00–12:00 | 01:00–04:00 | 🔴 High Focus | Complex coding, writing, strategy |
| Light Work | 12:00–14:00 | 04:00–06:00 | 🟡 Medium | Email, reviews, light tasks |
| Meetings | 14:00–17:00 | 06:00–09:00 | 🟢 Social | Calls, meetings, collaboration |
| Planning | 17:00–18:00 | 09:00–10:00 | 🔵 Reflective | Standup, next-day planning |

**Scoring Formula:**

```python
def score_slot(task, slot_start, slot_end, day_context):
    score = 0.0
    
    # 1. ENERGY MATCH (0-40 points)
    energy_type = get_energy_type(slot_start)  # deep/light/meetings/planning
    task_energy = classify_task_energy(task)     # from labels/content
    if energy_type == task_energy:
        score += 40
    elif adjacent_energy(energy_type, task_energy):
        score += 20
    else:
        score += 5  # can still schedule, just not ideal
    
    # 2. URGENCY (0-30 points)
    days_until_due = (task.due_date - slot_start.date()).days
    if days_until_due <= 0:
        score += 30  # overdue, max urgency
    elif days_until_due <= 1:
        score += 25
    elif days_until_due <= 3:
        score += 15
    elif days_until_due <= 7:
        score += 5
    
    # 3. PRIORITY (0-20 points)
    # Todoist: priority 4 = P1 (highest), priority 1 = P4 (lowest)
    priority_scores = {4: 20, 3: 15, 2: 10, 1: 5}
    score += priority_scores.get(task.priority, 5)
    
    # 4. CONTINUITY BONUS (0-10 points)
    # Prefer scheduling related tasks adjacently
    if previous_slot_same_project(task, slot_start, day_context):
        score += 10
    
    # 5. EARLINESS PREFERENCE (0-5 points)
    # Prefer earlier days (get things done sooner)
    days_from_now = (slot_start.date() - today()).days
    score += max(0, 5 - days_from_now)
    
    # 6. BUFFER COMPLIANCE (-20 penalty)
    if not has_15min_buffer(slot_start, slot_end, day_context):
        score -= 20
    
    return score
```

**Task Energy Classification:**

```python
def classify_task_energy(task):
    """Classify what energy level a task needs based on labels and content."""
    content_lower = task.content.lower()
    labels = [l.lower() for l in task.labels]
    
    # Deep work indicators
    if any(kw in content_lower for kw in ["write", "design", "architect", "code", "strategy", "plan", "analyze", "research", "spec"]):
        return "deep"
    if "deep" in labels or "focus" in labels:
        return "deep"
    
    # Meeting indicators  
    if any(kw in content_lower for kw in ["call", "meet", "discuss", "sync", "review with", "present"]):
        return "meetings"
    if "meeting" in labels:
        return "meetings"
    
    # Light work indicators
    if any(kw in content_lower for kw in ["email", "reply", "update", "check", "follow up", "review", "read"]):
        return "light"
    if "light" in labels or "admin" in labels:
        return "light"
    
    # Default: match to priority
    # P1/P2 → deep, P3/P4 → light
    if task.priority >= 3:  # Todoist P1/P2
        return "deep"
    return "light"
```

#### Step 4: PLACE — Greedy Scheduling with Backtracking

```python
def place_tasks(tasks, available_slots, day_context):
    """
    Place tasks into calendar slots using priority-ordered greedy algorithm.
    
    Order: P1 first → P2 → P3 → P4
    Within same priority: earliest due date first
    Within same due date: highest time estimate first (big rocks first)
    """
    
    # Sort tasks by scheduling priority
    sorted_tasks = sorted(tasks, key=lambda t: (
        -t.priority,                    # Highest priority first (Todoist: 4=P1)
        t.due_date or date(2099, 12, 31),  # Earliest due date
        -(t.duration or 30),            # Longest tasks first (big rocks)
    ))
    
    placements = []
    
    for task in sorted_tasks:
        duration = task.duration or 60  # default 60 min
        
        # Find all valid slots for this task
        candidates = find_valid_slots(task, available_slots, duration)
        
        if not candidates:
            # No slot found — flag for standup review
            placements.append({"task": task, "slot": None, "status": "unplaceable"})
            continue
        
        # Score each candidate
        scored = [(score_slot(task, s.start, s.end, day_context), s) for s in candidates]
        scored.sort(key=lambda x: -x[0])
        
        # Take best slot
        best_score, best_slot = scored[0]
        placements.append({
            "task": task,
            "slot": best_slot,
            "score": best_score,
            "status": "placed"
        })
        
        # Remove slot from available pool (with 15-min buffers)
        consume_slot(available_slots, best_slot, buffer_minutes=15)
    
    return placements
```

#### Step 5: COMMIT — Write to Calendar

```python
def commit_placements(placements, state):
    """Write placements to Google Calendar and update state."""
    
    for p in placements:
        if p["status"] != "placed":
            continue
        
        task = p["task"]
        slot = p["slot"]
        
        # Determine target calendar
        calendar_id = route_to_calendar(task)
        
        # Check if task already has a calendar event
        existing_event_id = state.get("task_events", {}).get(task.id)
        
        if existing_event_id:
            # Update existing event (move it)
            gcal_update_event(calendar_id, existing_event_id, {
                "start": slot.start,
                "end": slot.end,
                "summary": f"🔲 {task.content}",
                "description": build_description(task),
                "extendedProperties": {
                    "private": {
                        "molty_task_id": task.id,
                        "molty_priority": str(task.priority),
                        "molty_scheduled_at": utc_now_iso(),
                        "molty_engine_version": "1.0"
                    }
                }
            })
        else:
            # Create new event
            event = gcal_create_event(calendar_id, {
                "summary": f"🔲 {task.content}",
                "start": {"dateTime": slot.start.isoformat(), "timeZone": "Asia/Hong_Kong"},
                "end": {"dateTime": slot.end.isoformat(), "timeZone": "Asia/Hong_Kong"},
                "description": build_description(task),
                "colorId": priority_color(task.priority),
                "reminders": {"useDefault": False},
                "extendedProperties": {
                    "private": {
                        "molty_task_id": task.id,
                        "molty_priority": str(task.priority),
                        "molty_scheduled_at": utc_now_iso(),
                        "molty_engine_version": "1.0"
                    }
                }
            })
            state["task_events"][task.id] = event["id"]
        
        # If non-Brinc calendar, create Busy/Private blocker on Brinc
        if calendar_id != "brinc":
            create_or_update_brinc_blocker(task.id, slot, state)
    
    save_json("data/scheduler/state.json", state)
```

### 2.2 Available Slot Detection

```python
def find_available_slots(day, all_events, min_duration=30):
    """
    Find all available time slots on a given day.
    
    Working hours: 09:00-18:00 HKT
    Buffer: 15 minutes between events
    Minimum slot: 30 minutes (after buffers)
    """
    
    work_start = datetime(day.year, day.month, day.day, 9, 0, tz=HKT)
    work_end = datetime(day.year, day.month, day.day, 18, 0, tz=HKT)
    
    # Get all busy periods for this day (from all calendars, merged)
    busy_periods = []
    for event in all_events:
        if overlaps_day(event, day):
            start = max(event.start, work_start)
            end = min(event.end, work_end)
            # Add 15-min buffer on each side
            buffered_start = start - timedelta(minutes=15)
            buffered_end = end + timedelta(minutes=15)
            busy_periods.append((buffered_start, buffered_end))
    
    # Merge overlapping busy periods
    merged = merge_intervals(sorted(busy_periods))
    
    # Invert to get free slots
    free_slots = []
    cursor = work_start
    for busy_start, busy_end in merged:
        if cursor < busy_start:
            slot_duration = (busy_start - cursor).total_seconds() / 60
            if slot_duration >= min_duration:
                free_slots.append(Slot(cursor, busy_start))
        cursor = max(cursor, busy_end)
    
    # Final slot after last busy period
    if cursor < work_end:
        slot_duration = (work_end - cursor).total_seconds() / 60
        if slot_duration >= min_duration:
            free_slots.append(Slot(cursor, work_end))
    
    return free_slots
```

### 2.3 Calendar Routing

```python
def route_to_calendar(task):
    """Determine which calendar a task belongs on."""
    
    project_calendar_map = {
        "2300781386": "brinc",       # Brinc 🔴
        "2330246839": "brinc",       # Mana Capital 🟠 (work-adjacent)
        "2300781387": "personal",    # Personal 🙂
        "2329980736": "shenanigans", # Wedding 💍
        "2366746501": "personal",    # Molty's Den 🦎
        "2300781375": "personal",    # Inbox (default personal)
    }
    
    # Check labels for overrides
    labels = [l.lower() for l in task.labels]
    if "family" in labels or "school" in labels:
        return "shenanigans"
    if "work" in labels or "brinc" in labels:
        return "brinc"
    
    return project_calendar_map.get(task.project_id, "personal")
```

### 2.4 Non-Brinc Privacy Blockers

When a task is scheduled on Personal or Shenanigans, create a corresponding event on Brinc:

```python
def create_or_update_brinc_blocker(task_id, slot, state):
    """Create a Busy/Private event on Brinc to block the time."""
    blocker_id = state.get("brinc_blockers", {}).get(task_id)
    
    event_data = {
        "summary": "Busy",
        "start": {"dateTime": slot.start.isoformat(), "timeZone": "Asia/Hong_Kong"},
        "end": {"dateTime": slot.end.isoformat(), "timeZone": "Asia/Hong_Kong"},
        "visibility": "private",
        "transparency": "opaque",  # Show as Busy
        "extendedProperties": {
            "private": {
                "molty_blocker_for": task_id,
                "molty_engine_version": "1.0"
            }
        }
    }
    
    if blocker_id:
        gcal_update_event("brinc", blocker_id, event_data)
    else:
        event = gcal_create_event("brinc", event_data)
        state.setdefault("brinc_blockers", {})[task_id] = event["id"]
```

---

## 3. Conflict Resolution

### 3.1 Conflict Detection

Conflicts are detected by comparing the current calendar state against our scheduled task blocks.

```python
def detect_conflicts(state):
    """
    Check if any of our task blocks have been overbooked.
    
    Run this on a polling interval (every 15 minutes via cron)
    or triggered by a calendar webhook push notification.
    """
    conflicts = []
    
    for task_id, event_id in state.get("task_events", {}).items():
        try:
            our_event = gcal_get_event(route_to_calendar_by_task_id(task_id), event_id)
        except EventNotFound:
            # Event was deleted — treat as conflict
            conflicts.append({
                "type": "deleted",
                "task_id": task_id,
                "event_id": event_id
            })
            continue
        
        our_start = parse_datetime(our_event["start"])
        our_end = parse_datetime(our_event["end"])
        
        # Check for overlapping events on the same calendar
        overlapping = gcal_list_events(
            our_event["calendar_id"],
            our_start - timedelta(minutes=1),
            our_end + timedelta(minutes=1)
        )
        
        for other in overlapping:
            if other["id"] == event_id:
                continue
            if classify_event(other) == "fixed":
                # A real meeting was booked over our task block
                conflicts.append({
                    "type": "overbooked",
                    "task_id": task_id,
                    "our_event": our_event,
                    "conflicting_event": other
                })
    
    return conflicts
```

### 3.2 Conflict Resolution Strategy

```
CONFLICT DETECTED
       │
       ▼
Is conflicting event Fixed (external meeting)?
       │
   YES ╱╲ NO
      │    │
      ▼    ▼
  Our task  Compare priorities:
  yields.   Higher priority wins.
  Auto-     Lower priority yields.
  reschedule.
       │
       ▼
Find next best slot (same algorithm as initial placement)
       │
       ▼
Can fit today? ──YES──▶ Move to new slot
       │
       NO
       │
       ▼
Can fit this week before due date? ──YES──▶ Move to best available
       │
       NO
       │
       ▼
FLAG for standup review as "at risk"
```

### 3.3 Auto-Reschedule Rules

| Task Priority | Auto-Reschedule? | Notification |
|--------------|-------------------|-------------|
| P1 (Critical) | ✅ Yes, immediately | Telegram: "Moved [task] to [time] due to conflict with [meeting]" |
| P2 (High) | ✅ Yes, immediately | Telegram notification |
| P3 (Medium) | ✅ Yes, immediately | Silent (shown in standup) |
| P4 (Low) | ⚠️ Defer to standup | Added to standup agenda as "Needs Rescheduling" |

### 3.4 Conflict Resolution Code

```python
def resolve_conflicts(conflicts, state):
    """Resolve detected conflicts by rescheduling displaced tasks."""
    
    for conflict in conflicts:
        task = todoist_get_task(conflict["task_id"])
        
        if conflict["type"] == "deleted":
            # Our event was deleted — reschedule from scratch
            log(f"Task block for '{task.content}' was deleted. Rescheduling.")
            del state["task_events"][conflict["task_id"]]
            # Will be picked up in next scheduling run
            continue
        
        if conflict["type"] == "overbooked":
            # Delete our old event
            gcal_delete_event(
                route_to_calendar(task),
                conflict["our_event"]["id"]
            )
            del state["task_events"][conflict["task_id"]]
            
            # Also delete Brinc blocker if exists
            blocker_id = state.get("brinc_blockers", {}).get(conflict["task_id"])
            if blocker_id:
                gcal_delete_event("brinc", blocker_id)
                del state["brinc_blockers"][conflict["task_id"]]
            
            # Find new slot
            new_slot = find_best_replacement_slot(task, state)
            
            if new_slot:
                place_single_task(task, new_slot, state)
                
                # Notify based on priority
                if task.priority >= 3:  # P1 or P2
                    notify_telegram(
                        f"📅 Rescheduled: **{task.content}**\n"
                        f"Moved to {format_time(new_slot.start)} "
                        f"(conflict with {conflict['conflicting_event']['summary']})"
                    )
            else:
                # Cannot fit — flag for standup
                state.setdefault("unplaceable_tasks", []).append({
                    "task_id": task.id,
                    "reason": "no_slot_available",
                    "conflict_with": conflict["conflicting_event"]["summary"],
                    "detected_at": utc_now_iso()
                })
    
    save_json("data/scheduler/state.json", state)
```

---

## 4. Rescheduling Logic

### 4.1 Cascade Prevention

When one task is displaced, it might take the slot of another task. To prevent cascading:

1. **Only displace flexible events.** Fixed and anchored events are never moved by the engine.
2. **Priority hierarchy is absolute.** A P3 task cannot displace a P2 task's slot, even if the P3 is overdue.
3. **Same-priority tiebreaker:** Earlier due date wins.
4. **Cascade limit:** Maximum 3 cascading reschedules per conflict. If more are needed, stop and flag for standup.

```python
MAX_CASCADE_DEPTH = 3

def reschedule_with_cascade(task, state, depth=0):
    if depth >= MAX_CASCADE_DEPTH:
        flag_for_standup(task, "cascade_limit_reached")
        return False
    
    new_slot = find_best_replacement_slot(task, state)
    
    if new_slot and not slot_occupied_by_higher_priority(new_slot, task, state):
        place_single_task(task, new_slot, state)
        return True
    
    if new_slot and slot_occupied_by_lower_priority(new_slot, task, state):
        displaced_task = get_task_in_slot(new_slot, state)
        place_single_task(task, new_slot, state)  # Take the slot
        return reschedule_with_cascade(displaced_task, state, depth + 1)
    
    flag_for_standup(task, "no_slot_available")
    return False
```

### 4.2 Non-Negotiables (Never Move)

These are treated as **immovable walls** in the scheduling algorithm:

| Commitment | Days | Time (HKT) | Calendar | Type |
|-----------|------|------------|----------|------|
| School Drop-off | Mon/Wed/Fri | 08:00–08:30 | Shenanigans | Fixed |
| School Pick-up | Mon/Wed/Fri | 10:30–11:00 | Shenanigans | Anchored* |
| Daily Standup | Daily | 17:00–17:30 | Personal | Anchored |

*Pick-up is "preferred" — if a critical P1 conflict exists, it can shift to 11:00–11:30 max.

```python
NON_NEGOTIABLES = [
    {
        "name": "School Drop-off",
        "days": [0, 2, 4],  # Mon, Wed, Fri
        "start": "08:00",
        "end": "08:30",
        "tz": "Asia/Hong_Kong",
        "calendar": "shenanigans",
        "movable": False
    },
    {
        "name": "School Pick-up",
        "days": [0, 2, 4],
        "start": "10:30",
        "end": "11:00",
        "tz": "Asia/Hong_Kong",
        "calendar": "shenanigans",
        "movable": False,  # Only flexible within 10:30-11:30 window
        "flex_window": {"start": "10:30", "end": "11:30"}
    },
    {
        "name": "Daily Standup",
        "days": [0, 1, 2, 3, 4],  # Mon-Fri
        "start": "17:00",
        "end": "17:30",
        "tz": "Asia/Hong_Kong",
        "calendar": "personal",
        "movable": False
    }
]
```

### 4.3 Exercise Scheduling

Exercise is a special "habit" — flexible but should happen daily:

```python
EXERCISE_HABIT = {
    "name": "Exercise 🏋️",
    "duration": 60,  # minutes
    "frequency": "daily",
    "preferred_times": ["07:00-08:00", "12:00-13:00", "18:00-19:00"],  # HKT
    "calendar": "personal",
    "priority": "anchored",  # Higher than P3/P4 tasks, lower than P1/P2
    "scheduling_rules": {
        "preferred_slot": "07:00-08:00",  # Try morning first
        "fallback_slots": ["12:00-13:00", "18:00-19:00"],
        "min_per_week": 5,  # Alert if fewer than 5 sessions scheduled
        "can_be_displaced_by": ["P1", "P2"]  # Only high-priority can displace
    }
}
```

---

## 5. Data Model

### 5.1 File Structure

```
/data/workspace/data/scheduler/
├── state.json              # Core engine state
├── schedule-cache.json     # Cached calendar data (refreshed hourly)
├── conflict-log.json       # Historical conflict records
├── standup-proposals/
│   └── 2026-02-05.json     # Daily proposed schedule for standup
└── config.json             # Engine configuration
```

### 5.2 state.json — Core State

```json
{
  "version": "1.0",
  "last_run": "2026-02-05T09:00:00Z",
  "last_conflict_check": "2026-02-05T09:15:00Z",
  
  "task_events": {
    "<todoist_task_id>": {
      "gcal_event_id": "<google_calendar_event_id>",
      "calendar": "brinc",
      "scheduled_start": "2026-02-05T01:00:00Z",
      "scheduled_end": "2026-02-05T03:00:00Z",
      "score": 85,
      "placed_at": "2026-02-05T09:00:00Z",
      "reschedule_count": 0,
      "status": "active",
      "approval": "auto"
    }
  },
  
  "brinc_blockers": {
    "<todoist_task_id>": "<brinc_blocker_event_id>"
  },
  
  "habits": {
    "exercise": {
      "last_scheduled": "2026-02-05",
      "week_count": 3,
      "gcal_event_ids": {
        "2026-02-05": "<event_id>",
        "2026-02-06": "<event_id>"
      }
    }
  },
  
  "unplaceable_tasks": [
    {
      "task_id": "12345",
      "reason": "no_slot_available",
      "detected_at": "2026-02-05T09:00:00Z",
      "reviewed": false
    }
  ],
  
  "pending_approval": [
    {
      "task_id": "67890",
      "proposed_slot": {
        "start": "2026-02-06T01:00:00Z",
        "end": "2026-02-06T02:00:00Z"
      },
      "score": 72,
      "proposed_at": "2026-02-05T09:00:00Z"
    }
  ]
}
```

### 5.3 config.json — Engine Configuration

```json
{
  "version": "1.0",
  "timezone": "Asia/Hong_Kong",
  "working_hours": {
    "start": "09:00",
    "end": "18:00"
  },
  "buffer_minutes": 15,
  "min_slot_minutes": 30,
  "max_cascade_depth": 3,
  "scheduling_window_days": 7,
  "conflict_check_interval_minutes": 15,
  
  "energy_blocks": {
    "deep": {"start": "09:00", "end": "12:00"},
    "light": {"start": "12:00", "end": "14:00"},
    "meetings": {"start": "14:00", "end": "17:00"},
    "planning": {"start": "17:00", "end": "18:00"}
  },
  
  "priority_auto_schedule": {
    "4": true,
    "3": false,
    "2": false,
    "1": false
  },
  
  "calendar_ids": {
    "brinc": "<actual-calendar-id>",
    "personal": "<actual-calendar-id>",
    "shenanigans": "<actual-calendar-id>"
  },
  
  "project_calendar_map": {
    "2300781386": "brinc",
    "2330246839": "brinc",
    "2300781387": "personal",
    "2329980736": "shenanigans",
    "2366746501": "personal",
    "2300781375": "personal"
  },
  
  "event_colors": {
    "P1": "11",
    "P2": "6",
    "P3": "2",
    "P4": "8"
  },
  
  "non_negotiables": [
    {
      "name": "School Drop-off",
      "days": [0, 2, 4],
      "start": "08:00",
      "end": "08:30",
      "calendar": "shenanigans"
    },
    {
      "name": "School Pick-up",
      "days": [0, 2, 4],
      "start": "10:30",
      "end": "11:00",
      "calendar": "shenanigans",
      "flex_end": "11:30"
    },
    {
      "name": "Daily Standup",
      "days": [0, 1, 2, 3, 4],
      "start": "17:00",
      "end": "17:30",
      "calendar": "personal"
    }
  ]
}
```

### 5.4 conflict-log.json — Conflict History

```json
{
  "conflicts": [
    {
      "id": "conflict-uuid",
      "detected_at": "2026-02-05T09:15:00Z",
      "type": "overbooked",
      "task_id": "12345",
      "task_name": "Write API spec",
      "conflicting_event": "Team sync with Alice",
      "original_slot": {"start": "...", "end": "..."},
      "resolution": "rescheduled",
      "new_slot": {"start": "...", "end": "..."},
      "cascade_depth": 0
    }
  ]
}
```

### 5.5 standup-proposals/YYYY-MM-DD.json

```json
{
  "date": "2026-02-05",
  "generated_at": "2026-02-05T08:50:00Z",
  "tomorrow_schedule": [
    {
      "time": "09:00-11:00",
      "task": "Write Smart Scheduling Spec",
      "project": "Molty's Den",
      "priority": "P1",
      "energy_match": "deep ✓",
      "status": "auto-scheduled",
      "task_id": "12345"
    },
    {
      "time": "11:15-12:00",
      "task": "Review Brinc proposals",
      "project": "Brinc",
      "priority": "P2",
      "energy_match": "deep ✓",
      "status": "pending_approval",
      "task_id": "67890"
    }
  ],
  "needs_approval": [
    {
      "task_id": "67890",
      "task": "Review Brinc proposals",
      "proposed_slot": "11:15-12:00",
      "reason": "P2 task — needs standup confirmation"
    }
  ],
  "unplaceable": [
    {
      "task_id": "99999",
      "task": "Quarterly planning doc",
      "reason": "4h estimated, no contiguous block available this week",
      "suggestion": "Split into 2x2h blocks?"
    }
  ],
  "conflicts_resolved_today": [
    {
      "task": "Write API spec",
      "was": "10:00-12:00",
      "moved_to": "14:00-16:00",
      "reason": "Alice booked team sync at 10:00"
    }
  ],
  "stats": {
    "tasks_scheduled": 8,
    "tasks_pending_approval": 2,
    "tasks_unplaceable": 1,
    "deep_work_hours": 3.0,
    "meeting_hours": 2.5,
    "utilization": 0.72
  }
}
```

---

## 6. API Interactions

### 6.1 Google Calendar API

**Authentication:** OAuth2 service account or user credentials stored at `/data/workspace/credentials/gcal/`.

**Key Endpoints Used:**

| Operation | Endpoint | Method | When |
|-----------|----------|--------|------|
| List events | `GET /calendars/{id}/events` | GET | Fetch step — get all events in window |
| Create event | `POST /calendars/{id}/events` | POST | Commit step — create task blocks |
| Update event | `PUT /calendars/{id}/events/{eventId}` | PUT | Reschedule — move task blocks |
| Delete event | `DELETE /calendars/{id}/events/{eventId}` | DELETE | Clean up — remove old blocks |
| FreeBusy query | `POST /freeBusy/query` | POST | Quick availability check |

**API Wrapper (bash):**

```bash
#!/bin/bash
# scripts/gcal-api.sh — Google Calendar API wrapper

GCAL_BASE="https://www.googleapis.com/calendar/v3"

gcal_list_events() {
    local calendar_id="$1"
    local time_min="$2"
    local time_max="$3"
    
    curl -s -H "Authorization: Bearer $(get_gcal_token)" \
        "${GCAL_BASE}/calendars/${calendar_id}/events?timeMin=${time_min}&timeMax=${time_max}&singleEvents=true&orderBy=startTime&maxResults=250"
}

gcal_create_event() {
    local calendar_id="$1"
    local event_json="$2"
    
    curl -s -X POST \
        -H "Authorization: Bearer $(get_gcal_token)" \
        -H "Content-Type: application/json" \
        -d "$event_json" \
        "${GCAL_BASE}/calendars/${calendar_id}/events"
}

gcal_update_event() {
    local calendar_id="$1"
    local event_id="$2"
    local event_json="$3"
    
    curl -s -X PUT \
        -H "Authorization: Bearer $(get_gcal_token)" \
        -H "Content-Type: application/json" \
        -d "$event_json" \
        "${GCAL_BASE}/calendars/${calendar_id}/events/${event_id}"
}

gcal_delete_event() {
    local calendar_id="$1"
    local event_id="$2"
    
    curl -s -X DELETE \
        -H "Authorization: Bearer $(get_gcal_token)" \
        "${GCAL_BASE}/calendars/${calendar_id}/events/${event_id}"
}

gcal_freebusy() {
    local request_json="$1"
    
    curl -s -X POST \
        -H "Authorization: Bearer $(get_gcal_token)" \
        -H "Content-Type: application/json" \
        -d "$request_json" \
        "${GCAL_BASE}/freeBusy"
}
```

**Rate Limiting:**
- Google Calendar API: 100 requests per 100 seconds per user.
- Our scheduling runs: ~10-20 API calls per run (3 calendar fetches + event creates/updates).
- Conflict checks: ~5-10 calls per check.
- **Strategy:** Batch operations, cache calendar data in `schedule-cache.json` (TTL: 15 min).

### 6.2 Todoist API

**Authentication:** Bearer token from `/data/workspace/credentials/todoist.env`

**Key Endpoints Used:**

| Operation | Endpoint | When |
|-----------|----------|------|
| List tasks | `GET /rest/v2/tasks` | Fetch — get all active tasks |
| Get task | `GET /rest/v2/tasks/{id}` | Conflict resolution — get task details |
| Update task | `POST /rest/v2/tasks/{id}` | After scheduling — add label "scheduled" |
| Get comments | `GET /rest/v2/comments?task_id={id}` | Get description/notes |
| List projects | `GET /rest/v2/projects` | Map tasks to calendars |

**Task Filtering — Which Tasks to Schedule:**

```python
def get_schedulable_tasks():
    """Get tasks that should be placed on the calendar."""
    all_tasks = todoist_list_tasks()
    
    schedulable = []
    for task in all_tasks:
        # Skip if no due date (backlog tasks)
        if not task.due:
            continue
        
        # Skip if already completed
        if task.is_completed:
            continue
        
        # Skip if due date is beyond scheduling window
        if task.due.date > today() + timedelta(days=7):
            continue
        
        # Skip sub-tasks (we schedule parent tasks)
        if task.parent_id:
            continue
        
        # Skip tasks with @no-schedule label
        if "no-schedule" in task.labels:
            continue
        
        # Extract duration from description or estimate
        task.duration = extract_duration(task)  # returns minutes
        
        schedulable.append(task)
    
    return schedulable
```

**Duration Extraction:**

```python
def extract_duration(task):
    """
    Extract time estimate from task.
    
    Sources (in priority order):
    1. Todoist native duration field (if set)
    2. Description pattern: "~2h" or "~30m" or "est: 1.5h"
    3. Label: "@30min", "@1h", "@2h"
    4. Default by priority: P1=120min, P2=90min, P3=60min, P4=30min
    """
    
    # 1. Native duration
    if task.duration and task.duration.amount:
        if task.duration.unit == "minute":
            return task.duration.amount
        return task.duration.amount * 60  # hours to minutes
    
    # 2. Description pattern
    if task.description:
        match = re.search(r'~?(\d+\.?\d*)\s*h', task.description)
        if match:
            return int(float(match.group(1)) * 60)
        match = re.search(r'~?(\d+)\s*m', task.description)
        if match:
            return int(match.group(1))
    
    # 3. Label
    for label in task.labels:
        match = re.match(r'(\d+)(min|h)', label)
        if match:
            val = int(match.group(1))
            if match.group(2) == "h":
                return val * 60
            return val
    
    # 4. Default by priority
    priority_defaults = {4: 120, 3: 90, 2: 60, 1: 30}
    return priority_defaults.get(task.priority, 60)
```

### 6.3 Task-to-Event Sync

After scheduling, update the Todoist task to reflect its calendar placement:

```python
def sync_task_after_scheduling(task, slot):
    """Update Todoist task with scheduling info."""
    
    # Add "scheduled" label
    new_labels = list(set(task.labels + ["scheduled"]))
    
    # Add comment with calendar link
    todoist_add_comment(
        task.id,
        f"📅 Scheduled: {format_date(slot.start)} {format_time(slot.start)}-{format_time(slot.end)}"
    )
    
    todoist_update_task(task.id, {"labels": new_labels})
```

---

## 7. Edge Cases

### 7.1 All-Day Events

- **Detection:** Google Calendar events with `date` instead of `dateTime` in start/end.
- **Treatment:** Block the entire day for scheduling purposes IF the event is on the task's target calendar.
- **Exception:** All-day events like "Birthday" or informational events → check `transparency` field. If `transparent`, ignore for scheduling.

```python
def handle_all_day_event(event):
    if event.get("transparency") == "transparent":
        return None  # Informational, ignore
    
    # Block entire working hours for that day
    return BusyPeriod(
        start=datetime.combine(event.date, time(9, 0)),
        end=datetime.combine(event.date, time(18, 0)),
        source="all-day-event"
    )
```

### 7.2 Multi-Day Tasks

Tasks estimated at >3 hours should be split into multiple blocks:

```python
def split_large_task(task):
    """Split tasks >3h into manageable blocks."""
    duration = task.duration  # minutes
    
    if duration <= 180:  # 3 hours or less
        return [task]  # Single block
    
    # Split into blocks
    max_block = 120  # 2-hour max blocks
    min_block = 30
    
    blocks = []
    remaining = duration
    part = 1
    
    while remaining > 0:
        block_size = min(max_block, remaining)
        if remaining - block_size < min_block and remaining - block_size > 0:
            # Don't leave a tiny remainder — split more evenly
            block_size = remaining // 2
        
        blocks.append({
            "parent_task_id": task.id,
            "part": part,
            "duration": block_size,
            "content": f"{task.content} (Part {part})",
            "priority": task.priority,
            "due": task.due,
            "project_id": task.project_id,
            "labels": task.labels
        })
        
        remaining -= block_size
        part += 1
    
    return blocks
```

**State tracking for split tasks:**

```json
{
  "split_tasks": {
    "<todoist_task_id>": {
      "total_duration": 300,
      "parts": [
        {"part": 1, "duration": 120, "event_id": "abc", "status": "scheduled"},
        {"part": 2, "duration": 120, "event_id": "def", "status": "scheduled"},
        {"part": 3, "duration": 60, "event_id": "ghi", "status": "pending"}
      ]
    }
  }
}
```

### 7.3 Recurring Tasks

Todoist recurring tasks (e.g., "Review metrics every Monday"):

```python
def handle_recurring_task(task):
    """
    Recurring tasks: only schedule the NEXT occurrence.
    
    Todoist gives us the next due date for recurring tasks.
    We schedule that single occurrence. When completed,
    Todoist generates the next occurrence automatically.
    """
    if not task.due or not task.due.is_recurring:
        return task
    
    # Only schedule if next occurrence is within our window
    next_due = parse_date(task.due.date)
    if next_due > today() + timedelta(days=7):
        return None  # Not in window
    
    # Treat as a regular task with that due date
    return task
```

### 7.4 Timezone Handling

**Critical:** All internal times are stored and compared in UTC. Conversion happens at boundaries.

```python
import pytz

HKT = pytz.timezone("Asia/Hong_Kong")
UTC = pytz.UTC

def hkt_to_utc(hkt_time):
    """Convert HKT-aware datetime to UTC."""
    if hkt_time.tzinfo is None:
        hkt_time = HKT.localize(hkt_time)
    return hkt_time.astimezone(UTC)

def utc_to_hkt(utc_time):
    """Convert UTC datetime to HKT for display."""
    if utc_time.tzinfo is None:
        utc_time = UTC.localize(utc_time)
    return utc_time.astimezone(HKT)

# When creating Google Calendar events: always specify timeZone
event = {
    "start": {"dateTime": "2026-02-05T09:00:00+08:00", "timeZone": "Asia/Hong_Kong"},
    "end": {"dateTime": "2026-02-05T11:00:00+08:00", "timeZone": "Asia/Hong_Kong"}
}
```

**Edge case — DST:** Hong Kong does not observe DST (fixed UTC+8), so this simplifies things. However, if Guillermo travels, the engine should still work because:
- Non-negotiables are anchored to HKT (school times don't change).
- Energy blocks are anchored to HKT.
- Google Calendar handles timezone conversion per-event.

### 7.5 Weekends

- **Default:** No task scheduling on weekends.
- **Override:** If a P1 task is overdue and due Monday, the engine CAN propose a Saturday block.
- **Weekend proposals** always go to `pending_approval` regardless of priority.

```python
def is_schedulable_day(date, task):
    if date.weekday() < 5:  # Mon-Fri
        return True
    if date.weekday() >= 5 and task.priority == 4:  # P1 on weekend
        return True  # But will be flagged for approval
    return False
```

### 7.6 Same-Time Conflicts Across Calendars

When the same time slot has events on different calendars, they might not be visible to each other. The engine must merge all three calendars into a unified busy map:

```python
def build_unified_busy_map(window_start, window_end):
    """Merge all calendars into one busy map."""
    all_busy = []
    
    for cal_id in ["brinc", "personal", "shenanigans"]:
        events = gcal_list_events(cal_id, window_start, window_end)
        for event in events:
            if is_task_block(event):
                # Our own task blocks are "flexible" — can be moved
                all_busy.append(BusyPeriod(
                    start=parse_start(event),
                    end=parse_end(event),
                    calendar=cal_id,
                    priority=get_task_priority(event),
                    movable=True,
                    event_id=event["id"]
                ))
            else:
                # External events are immovable
                all_busy.append(BusyPeriod(
                    start=parse_start(event),
                    end=parse_end(event),
                    calendar=cal_id,
                    priority=999,  # Immovable
                    movable=False,
                    event_id=event["id"]
                ))
    
    return sorted(all_busy, key=lambda b: b.start)
```

### 7.7 Task Completion Mid-Block

If Guillermo completes a Todoist task that's currently scheduled on the calendar:

```python
def handle_task_completion(task_id, state):
    """Clean up calendar when a task is completed in Todoist."""
    
    event_info = state["task_events"].get(task_id)
    if not event_info:
        return
    
    # Delete the calendar event
    gcal_delete_event(event_info["calendar"], event_info["gcal_event_id"])
    
    # Delete Brinc blocker if exists
    blocker_id = state.get("brinc_blockers", {}).get(task_id)
    if blocker_id:
        gcal_delete_event("brinc", blocker_id)
        del state["brinc_blockers"][task_id]
    
    # Clean up state
    del state["task_events"][task_id]
    
    # The freed slot will be picked up in the next scheduling run
    save_json("data/scheduler/state.json", state)
```

### 7.8 Double-Booking Prevention

Before committing any event creation, do a final check:

```python
def pre_commit_check(calendar_id, start, end):
    """Last-second check before creating an event to prevent double-booking."""
    existing = gcal_list_events(calendar_id, start, end)
    
    for event in existing:
        if not is_task_block(event):
            # There's a real event here — abort
            return False
    
    return True
```

---

## 8. Daily Standup Integration

### 8.1 Pre-Standup Generation (Runs at 4:45 PM HKT / 08:45 UTC)

```python
def generate_standup_proposal():
    """
    Generate the proposed schedule for tomorrow,
    to be reviewed at 5PM HKT standup.
    """
    tomorrow = today() + timedelta(days=1)
    
    # Run the full scheduling pipeline for tomorrow
    inputs = fetch_inputs(
        window_start=datetime.combine(tomorrow, time(0, 0)),
        window_end=datetime.combine(tomorrow + timedelta(days=1), time(0, 0))
    )
    
    # Get all tasks that could be scheduled tomorrow
    tasks = get_schedulable_tasks()
    tomorrow_tasks = [t for t in tasks if should_schedule_on(t, tomorrow)]
    
    # Run placement algorithm
    placements = place_tasks(tomorrow_tasks, inputs["events"], tomorrow)
    
    # Build proposal
    proposal = {
        "date": tomorrow.isoformat(),
        "generated_at": utc_now_iso(),
        "tomorrow_schedule": [],
        "needs_approval": [],
        "unplaceable": [],
        "conflicts_resolved_today": get_todays_conflicts(state),
        "stats": {}
    }
    
    for p in placements:
        entry = {
            "time": f"{format_time(p['slot'].start)}-{format_time(p['slot'].end)}",
            "task": p["task"].content,
            "project": get_project_name(p["task"].project_id),
            "priority": priority_label(p["task"].priority),
            "energy_match": energy_match_label(p["slot"].start, p["task"]),
            "task_id": p["task"].id
        }
        
        if p["status"] == "placed":
            if is_auto_approved(p["task"]):
                entry["status"] = "auto-scheduled"
                proposal["tomorrow_schedule"].append(entry)
            else:
                entry["status"] = "pending_approval"
                proposal["tomorrow_schedule"].append(entry)
                proposal["needs_approval"].append({
                    "task_id": p["task"].id,
                    "task": p["task"].content,
                    "proposed_slot": entry["time"],
                    "reason": f"{priority_label(p['task'].priority)} task — needs standup confirmation"
                })
        elif p["status"] == "unplaceable":
            proposal["unplaceable"].append({
                "task_id": p["task"].id,
                "task": p["task"].content,
                "reason": p.get("reason", "no slot available"),
                "suggestion": suggest_resolution(p["task"])
            })
    
    # Save proposal
    save_json(f"data/scheduler/standup-proposals/{tomorrow.isoformat()}.json", proposal)
    
    return proposal
```

### 8.2 Standup Schedule Section Format

The standup generates a formatted section for the Notion standup page:

```
## 📅 Tomorrow's Proposed Schedule (Feb 6, 2026)

### Auto-Scheduled (P1) ✅
| Time (HKT) | Task | Project | Energy |
|------------|------|---------|--------|
| 09:00-11:00 | Write scheduling engine | Molty's Den | 🔴 Deep ✓ |
| 11:15-12:00 | Deploy API endpoint | Brinc | 🔴 Deep ✓ |

### Needs Your Approval 🟡
| Time (HKT) | Task | Project | Priority |
|------------|------|---------|----------|
| 12:15-13:00 | Review vendor proposals | Brinc | P2 |
| 14:00-15:00 | Research wedding venues | Wedding | P3 |

**Reply "approve all" or specify changes:**
- "move vendor review to 14:00"
- "skip wedding research this week"
- "approve all"

### ⚠️ Couldn't Schedule
- **Quarterly planning doc** (4h est.) — No 4h block available. Split into 2x2h?

### 📊 Day Stats
- Deep work: 3h | Light: 1h | Meetings: 2h | Buffer: 1.25h
- Utilization: 72% | Free: 2.5h
```

### 8.3 Approval Flow

```python
def process_standup_decisions(decisions, proposal_date):
    """
    Process Guillermo's decisions from standup.
    
    Input formats:
    - "approve all" → approve everything in pending
    - "approve 67890" → approve specific task
    - "move 67890 to 14:00" → approve with time change
    - "skip 67890" → remove from schedule
    - "split 99999 into 2h blocks" → split and reschedule
    """
    
    proposal = load_json(f"data/scheduler/standup-proposals/{proposal_date}.json")
    state = load_json("data/scheduler/state.json")
    
    for decision in decisions:
        if decision["action"] == "approve_all":
            for item in proposal["needs_approval"]:
                commit_approved_task(item["task_id"], proposal, state)
        
        elif decision["action"] == "approve":
            commit_approved_task(decision["task_id"], proposal, state)
        
        elif decision["action"] == "move":
            # Remove from pending, reschedule to specified time
            new_start = parse_time(decision["new_time"])
            task = todoist_get_task(decision["task_id"])
            duration = extract_duration(task)
            new_end = new_start + timedelta(minutes=duration)
            place_single_task(task, Slot(new_start, new_end), state)
        
        elif decision["action"] == "skip":
            # Mark as skipped, won't be rescheduled until manually re-added
            state.setdefault("skipped_tasks", {})[decision["task_id"]] = {
                "skipped_at": utc_now_iso(),
                "skipped_for": proposal_date
            }
        
        elif decision["action"] == "split":
            task = todoist_get_task(decision["task_id"])
            task.duration = decision.get("block_size", 120)
            blocks = split_large_task(task)
            for block in blocks:
                # Will be placed in next scheduling run
                state.setdefault("split_tasks", {})[task.id] = {
                    "total_duration": extract_duration(task),
                    "block_size": decision.get("block_size", 120),
                    "parts": blocks
                }
    
    save_json("data/scheduler/state.json", state)
    
    # Run scheduler to commit approved tasks
    run_scheduling_pipeline()
```

### 8.4 P1 Auto-Scheduling (No Standup Needed)

P1 tasks bypass standup entirely:

```python
def is_auto_approved(task):
    """
    P1 (Todoist priority=4) tasks auto-schedule without standup approval.
    Everything else waits for standup confirmation.
    """
    return task.priority == 4  # Todoist's "P1" = priority value 4
```

When a P1 task is created or detected in Todoist:
1. Engine runs immediately (not waiting for next scheduled run).
2. Finds the best available slot.
3. Creates the calendar event.
4. Sends Telegram notification: "🔴 Auto-scheduled P1: [task] → [time]"
5. Records in state with `"approval": "auto"`.

---

## 9. Implementation Plan

### Phase 1: Foundation (Est: 2-3 days)

**Goal:** Basic infrastructure — can read calendars and tasks, find free slots.

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Config loader | `scheduler/config.py` | Load `config.json`, validate | 1h |
| GCal wrapper | `scheduler/gcal.py` | Auth + CRUD operations | 3h |
| Todoist wrapper | `scheduler/todoist_api.py` | Auth + read operations | 2h |
| State manager | `scheduler/state.py` | Load/save `state.json` | 1h |
| Free slot finder | `scheduler/slots.py` | Parse events → find available slots | 3h |
| **Total** | | | **~10h** |

**Deliverable:** Script that prints "Available slots for tomorrow: [list]"

### Phase 2: Core Scheduling (Est: 3-4 days)

**Goal:** Can place tasks on calendar with energy matching and priority ordering.

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Task classifier | `scheduler/classify.py` | Energy type, duration extraction | 2h |
| Scoring engine | `scheduler/scoring.py` | Slot scoring formula | 3h |
| Placement algo | `scheduler/placer.py` | Greedy placement with scoring | 4h |
| Calendar writer | `scheduler/commit.py` | Create/update GCal events | 3h |
| Brinc blockers | `scheduler/privacy.py` | Create Busy/Private blockers | 2h |
| Calendar routing | `scheduler/routing.py` | Project → calendar mapping | 1h |
| **Total** | | | **~15h** |

**Deliverable:** Running `python scheduler/main.py schedule` creates task blocks on Google Calendar.

### Phase 3: Conflict Resolution (Est: 2-3 days)

**Goal:** Detect when meetings are booked over task blocks and auto-reschedule.

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Conflict detector | `scheduler/conflicts.py` | Compare state vs calendar reality | 3h |
| Reschedule logic | `scheduler/reschedule.py` | Find replacement slots, cascade | 4h |
| Notification | `scheduler/notify.py` | Telegram notifications for moves | 1h |
| Conflict logger | `scheduler/conflict_log.py` | Log conflicts for history | 1h |
| Cron job setup | `cron/conflict-check.sh` | Run conflict check every 15 min | 1h |
| **Total** | | | **~10h** |

**Deliverable:** When someone books over a task block, it automatically moves to the next best slot and notifies via Telegram.

### Phase 4: Standup Integration (Est: 2-3 days)

**Goal:** Generate proposed schedule for standup, process approvals.

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Proposal generator | `scheduler/standup.py` | Generate tomorrow's schedule | 3h |
| Proposal formatter | `scheduler/format.py` | Format for Notion standup | 2h |
| Approval processor | `scheduler/approve.py` | Parse and execute decisions | 3h |
| Standup cron | `cron/pre-standup.sh` | Run at 4:45 PM HKT | 1h |
| **Total** | | | **~9h** |

**Deliverable:** Standup includes a "📅 Tomorrow's Schedule" section. Guillermo can approve/modify/skip.

### Phase 5: Habits & Edge Cases (Est: 2-3 days)

**Goal:** Handle exercise scheduling, multi-day tasks, recurring tasks, weekends.

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Habit scheduler | `scheduler/habits.py` | Daily exercise placement | 3h |
| Task splitter | `scheduler/splitter.py` | Multi-day task splitting | 2h |
| Recurring handler | `scheduler/recurring.py` | Recurring task logic | 2h |
| Weekend logic | `scheduler/weekdays.py` | Weekend handling + overrides | 1h |
| Task completion sync | `scheduler/completion.py` | Clean up on task complete | 2h |
| **Total** | | | **~10h** |

### Phase 6: Polish & Monitoring (Est: 1-2 days)

| Component | File | Description | Effort |
|-----------|------|-------------|--------|
| Dashboard stats | `scheduler/stats.py` | Utilization, deep work hours | 2h |
| Error handling | All files | Retry logic, graceful failures | 3h |
| Logging | `scheduler/logger.py` | Structured logging to file | 1h |
| Dry-run mode | `scheduler/main.py` | `--dry-run` flag for testing | 1h |
| **Total** | | | **~7h** |

### Total Estimated Effort

| Phase | Effort | Cumulative |
|-------|--------|-----------|
| Phase 1: Foundation | ~10h | 10h |
| Phase 2: Core Scheduling | ~15h | 25h |
| Phase 3: Conflict Resolution | ~10h | 35h |
| Phase 4: Standup Integration | ~9h | 44h |
| Phase 5: Habits & Edge Cases | ~10h | 54h |
| Phase 6: Polish | ~7h | 61h |
| **Total** | | **~61h** |

### Execution Order & Dependencies

```
Phase 1 ──────────────▶ Phase 2 ──────────────▶ Phase 3
(Foundation)             (Core Scheduling)        (Conflict Resolution)
                              │                        │
                              ▼                        ▼
                         Phase 4 ◀─────────────── Phase 5
                         (Standup Integration)    (Edge Cases)
                              │
                              ▼
                         Phase 6
                         (Polish)
```

### Cron Schedule (Final)

```
# Run full scheduling pipeline — every morning at 8:30 AM HKT (00:30 UTC)
30 0 * * 1-5  python /data/workspace/scripts/scheduler/main.py schedule

# Conflict check — every 15 minutes during work hours
*/15 1-10 * * 1-5  python /data/workspace/scripts/scheduler/main.py check-conflicts

# Pre-standup proposal — 4:45 PM HKT (08:45 UTC)
45 8 * * 1-5  python /data/workspace/scripts/scheduler/main.py generate-standup

# Task completion sync — every 30 minutes
*/30 0-12 * * 1-5  python /data/workspace/scripts/scheduler/main.py sync-completions

# P1 task watcher — every 5 minutes (lightweight check for new P1 tasks)
*/5 0-12 * * 1-5  python /data/workspace/scripts/scheduler/main.py watch-p1
```

### CLI Interface

```bash
# Main entry point
python scheduler/main.py <command> [options]

# Commands:
#   schedule              Run full scheduling pipeline
#   check-conflicts       Detect and resolve conflicts
#   generate-standup      Generate standup proposal for tomorrow
#   sync-completions      Clean up completed tasks
#   watch-p1              Check for new P1 tasks to auto-schedule
#   show-schedule [date]  Print schedule for a date
#   dry-run               Run pipeline without committing
#   approve <task_id>     Approve a pending task
#   approve-all           Approve all pending tasks
#   skip <task_id>        Skip a task
#   move <task_id> <time> Move a task to a specific time
#   status                Show engine status and stats
```

---

## Appendix A: Event Naming Convention

| Event Type | Prefix | Example |
|-----------|--------|---------|
| Unstarted task block | 🔲 | 🔲 Write scheduling spec |
| In-progress task block | 🔳 | 🔳 Write scheduling spec |
| Completed task block | ✅ | ✅ Write scheduling spec |
| Exercise habit | 🏋️ | 🏋️ Exercise |
| Blocker (Brinc) | — | Busy |
| Non-negotiable | 🔒 | 🔒 School Drop-off |

## Appendix B: Google Calendar Color IDs

| Color ID | Color | Use For |
|----------|-------|---------|
| 11 | Tomato (Red) | P1 Critical |
| 6 | Tangerine (Orange) | P2 High |
| 2 | Sage (Green) | P3 Medium |
| 8 | Graphite (Gray) | P4 Low |
| 5 | Banana (Yellow) | Habits |
| 9 | Blueberry (Blue) | Blockers |

## Appendix C: Todoist Priority Mapping

⚠️ **CRITICAL:** Todoist API priority values are INVERTED from the UI!

| UI Label | API Value | Eisenhower | Engine Behavior |
|----------|-----------|-----------|-----------------|
| P1 (Red) | `priority: 4` | DO NOW | Auto-schedule immediately |
| P2 (Orange) | `priority: 3` | SCHEDULE | Propose at standup |
| P3 (Blue) | `priority: 2` | DELEGATE | Propose at standup |
| P4 (Gray) | `priority: 1` | DEFER | Propose at standup |

## Appendix D: Error Handling Strategy

| Error | Response | Retry? |
|-------|----------|--------|
| GCal API 401 | Refresh OAuth token | Yes, once |
| GCal API 403 | Log, skip calendar | No |
| GCal API 429 | Exponential backoff | Yes, 3 times |
| GCal API 500 | Wait 60s, retry | Yes, 3 times |
| Todoist API 401 | Log, alert via Telegram | No |
| Todoist API 429 | Wait 60s, retry | Yes, 3 times |
| Event not found | Remove from state, reschedule | N/A |
| No free slots | Flag for standup | N/A |
| State file corrupted | Load backup, rebuild from APIs | N/A |

---

*End of specification. Ready for implementation review at daily standup.*
