<!-- agent: molty | type: decision | priority: P1 | date: 2026-03-03 -->

# Decision: Daily Standup & Productivity System v2.1

**Date:** 2026-03-03  
**Decided by:** Guillermo + Molty  
**Status:** Approved — implemented same day  
**Full spec:** `/data/workspace/plans/standup-system-redesign.md`

---

## Why This Was Decided

The standup system was causing more grief than value:
- Verbal task completions acknowledged but not acted on → stale tasks reappearing
- Calendar blocked automatically at generation time with no judgment → wrong tasks blocked, right ones missed
- Tomorrow's Focus auto-generated from Todoist → ignored Guillermo's actual priorities
- In MC? checkbox existed but was wired to nothing
- Design decisions not persisted → same conversation repeated 6+ times
- No pre-standup intelligence gathering → Guillermo had to re-enter context at standup

---

## The Agreed System

### Core Rules (never break these)

1. **Verbal "done" = immediate action** — Todoist + Notion + MC closed in the same response. No "I'll note that."
2. **Real-time sync** — Todoist and MC must never diverge more than 2 hours. Every heartbeat: cross-sync completions both ways.
3. **Task title format (one-time on intake):** `Reply to Raeniel re: accounts — 30min 🦎` — specific + actionable + time estimate + 🦎 at end. Never rewrite again.
4. **Tomorrow's Focus = ONE item** — blank callout in Notion. Guillermo writes it. It becomes a calendar event. Do not auto-generate.
5. **Calendar booking = post-review ONLY** — never at generation time.
6. **Calendar bias = BLOCK** — better to over-book than miss. Guillermo can move it. 5 working day horizon.
7. **Clarifying questions = always ask** — preferred over silence + mistakes. Both Telegram + Notion callout.

### The Six Phases

**Phase 0 — Real-time (all day)**
- Verbal done → immediate Todoist + Notion + MC closure
- New Todoist task → rewrite title + assign project/owner/priority/estimate (one-time)
- Every 2h heartbeat: cross-sync MC ↔ Todoist completions

**Phase 1 — Pre-standup prep (4:30 PM, silent)**
1. Fetch + process new Todoist tasks
2. Webhook Raphael + Leonardo: "what did you complete today not in MC?" — wait 10 min
3. MC sync: cross-reference completions with Todoist
4. ggv.molt inbox scan for relevant items
5. Sync Notion DB
6. Form clarifying questions (genuine uncertainty only)

**Phase 2 — Standup generation (5:00 PM)**
- Notion page: summary callout + blank Tomorrow's Focus + email highlights + clarifying questions + task DB + blockers
- Telegram: "Standup ready + link + questions if any"
- NO calendar booking at this stage

**Phase 3 — Guillermo reviews**
- Answers questions → fills ONE Tomorrow's Focus → reviews table → says "standup done"
- Should NOT need to re-enter anything already discussed during the day

**Phase 4 — Post-review processing (on "standup done")**
1. Tomorrow's Focus → calendar event (first free slot tomorrow 9–13 HKT)
2. Action=Done/Drop → close Todoist + MC + Notion
3. Action=Reschedule → update Todoist due date
4. Owner=Raphael/Leonardo → move Todoist + webhook with context
5. In MC? ticked → create/update MC task (deduplicate first)
6. Book Calendar? ticked → book focus block (5-day horizon, check both cals)
7. Telegram summary

**Phase 5 — Overnight (Raphael 00:30 → Leonardo 01:30 → Molty 03:00)**
- Pull MC assigned → work (90-min budget) → update MC → write log
- Log MUST include: ✅ Completed / 👀 Under Review / ❌ Failed (with why) / 🚧 Blocked (specific ask) / ⏭ Skipped
- Molty consolidates R+L logs, checks ggv.molt, posts #squad-updates

**Phase 6 — Morning briefing (06:30)**
Order: Yesterday's Focus status → Overnight report → Calendar → Squad → P1/P2 tasks → Email → Fleet

### Notion DB Columns
Task | Your Notes | Action (Keep/Done/Drop/Reschedule) | Owner (G/Molty/Raphael/Leonardo) | Book Calendar? | In MC? | Due Date | Priority | Time Est. | Project | Section | Molty's Notes | Standup Date

### Calendar Settings
- Brinc project → Brinc calendar | Everything else → Personal calendar
- Horizon: 5 working days | Hours: 9–18 HKT (morning preferred)
- Format: `🎯 [P1] Task name` + 15-min popup | Duration from Time Est.
- Check BOTH calendars for conflicts before booking
- Default: tick Book Calendar? for P1/P2 + owner=Guillermo

### MC Task Creation
- Deduplicate: fuzzy ≥55% match BEFORE creating
- Required: title, project, priority, assignees, createdBy="molty", status="assigned"
- Description = Guillermo's Notes + Molty's Notes
- Update if exists+open. Skip if exists+done. Create only if genuinely new.

---

## What Changed From Previous System

| Was | Now |
|-----|-----|
| Verbal done → acknowledged only | Verbal done → immediate Todoist+Notion+MC action |
| Calendar auto-blocked at 5PM | Calendar only post-review |
| Tomorrow's Focus auto-generated | Blank — Guillermo writes ONE item |
| In MC? checkbox did nothing | In MC? creates/updates real MC tasks |
| No pre-standup squad check | Webhook R+L at 4:30, wait 10 min |
| Overnight: done+blocked only | Full: done+failed(why)+blocked+review |
| Morning briefing: no focus reminder | Yesterday's Focus shown first |
| Design decisions disappeared | This vault entry + plan doc permanent |

---

## Files

- Full spec: `/data/workspace/plans/standup-system-redesign.md`
- Quick ref: `/data/workspace/memory/refs/standup-process.md`
- Scripts: `daily_standup.py`, `process_standup.py`, `morning_briefing.py`
- Cron: `bdb28765` (5PM HKT standup generation)
