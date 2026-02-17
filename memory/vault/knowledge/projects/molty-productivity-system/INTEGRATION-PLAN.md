# Molty Productivity System — Integration Plan

**Status:** 🟢 Phases 1-3 Live, Phase 4-5 In Progress
**Created:** 2026-02-04
**Last Updated:** 2026-02-05

---

## Summary

Integrate Todoist and Google Calendar with OpenClaw to enable:
- Task management with Eisenhower Matrix prioritization
- Time-blocking with intelligent scheduling
- Daily and weekly review rituals
- Cross-agent visibility (limited)

---

## Phase 1: Todoist Integration ✅ COMPLETE

**Completed:** 2026-02-05

### What's Live
- [x] Todoist API token configured (`/data/workspace/credentials/todoist.env`)
- [x] Projects restructured:
  | ID | Project | Emoji |
  |----|---------|-------|
  | 2300781375 | Inbox | 📥 |
  | 2300781387 | Personal | 🙂 |
  | 2300781386 | Brinc | 🔴 |
  | 2330246839 | Mana Capital | 🟠 |
  | 2366746501 | Molty's Den | 🦎 |
- [x] Wedding project deleted (Sept 2023, done)
- [x] Eisenhower priority mapping (P1-P4, ⚠️ API inverted: priority=4 is P1!)
- [x] Inbox processing system (hybrid: auto-process hourly, review at standup)
- [x] Processing protocol documented (`/data/workspace/scripts/process-inbox.md`)
- [x] Labels: `@idea` for non-task items

### Brinc Task Coordination with Raphael
- Brinc tasks stay in **Todoist** (Guillermo's command view)
- Relay to Raphael via **Discord** (#brinc-private / #brinc-general)
- Raphael creates **mirror tasks in Notion** for execution tracking
- **Completion flow:** Raphael marks done in Notion → Molty reviews → tick off in Todoist
- ⚠️ **Future pattern:** Same model for ALL team leads when deployed

---

## Phase 2: Google Calendar Integration ✅ COMPLETE

**Completed:** 2026-02-05

### What's Live
- [x] Calendar API enabled on Molty Assistant (Google Cloud)
- [x] OAuth tokens via Brinc account (covers all calendars)
- [x] Token file: `/data/workspace/credentials/calendar-tokens-brinc.json`
- [x] Script: `/data/workspace/scripts/calendar.sh` (list, events, today, week, add, busy, move, delete, freebusy)
- [x] Config: `/data/workspace/credentials/calendar-config.json`

### Calendars

| Calendar | ID | Read | Write | Use |
|----------|-----|------|-------|-----|
| **Brinc** ⭐ | `guillermo.ginesta@brinc.io` | ✅ | ✅ | Work events + consolidated busy view |
| **Personal** | `guillermo.ginesta@gmail.com` | ✅ | ✅ | Exercise, focus time, personal tasks |
| **Shenanigans** | `vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com` | ✅ | ✅ | Family (school runs, family meetings) |
| HK Leave | `brinc.io_m1sncj13438k4k3aq3enaglpu4@group.calendar.google.com` | ✅ | ❌ | Reference only |
| HK Holidays | `en.hong_kong#holiday@group.v.calendar.google.com` | ✅ | ❌ | Reference only |

### Write Rules

| Event Type | Write To | Brinc Shows As |
|------------|----------|----------------|
| Family/kids | Shenanigans | Busy/Private |
| Brinc work | Brinc | Actual name |
| Personal/exercise | Personal | Busy/Private |
| Mana Capital | Personal | Busy/Private |
| Molty infra | Personal | Busy/Private |

**Key rule:** Brinc = consolidated availability view. Brinc stuff shows real names; everything else shows as "Busy" so colleagues see full availability without personal details.

### Life Commitments (Recurring)

| Commitment | Calendar | Days | Time (HKT) | Flexibility |
|------------|----------|------|------------|-------------|
| 🏫 School Drop-off | Shenanigans | Mon/Wed/Fri | 08:00–08:30 | 🔒 Non-negotiable |
| 🎯 Focus Time | Personal | Mon/Wed/Fri | 08:30–10:30 | Protected (no calls). Mon exception: staff meeting |
| 🏫 School Pick-up | Shenanigans | Mon/Wed/Fri | 10:30–11:00 | 🟡 Preferred, can yield for P1 |
| 🏋️ Exercise | Flexible | Daily | Flexible | 🟡 Must exist somewhere in the day |

### Cross-Calendar Busy Blocks on Brinc

| Days | Time | Block |
|------|------|-------|
| Wed/Fri | 08:00–11:00 | Full block (drop-off + focus + pick-up) |
| Monday | 08:00–08:30 | Drop-off only (staff meeting in middle) |
| Monday | 10:30–11:00 | Pick-up only |

### Energy Schedule

| Time (HKT) | Best For |
|-------------|----------|
| 09:00–12:00 | Deep work / P1 tasks |
| 12:00–14:00 | Light tasks / lunch |
| 14:00–17:00 | Meetings / collaborative |
| 17:00–18:00 | Standup + planning |

---

## Phase 3: Daily Standup ✅ COMPLETE

**Completed:** 2026-02-05

### What's Live
- [x] Cron job: daily 5PM HKT (09:00 UTC) — ID: `bdb28765-f508-4271-a04d-9408d39f49fd`
- [x] Notion template: inline database table under Molty's Mission Control
- [x] DB ID: `2fe39dd69afd81f189f7e58925dad602`
- [x] Columns: Task, Section, Project, Owner, Priority, Due Date, Time Est., Action, Molty's Notes, Your Comments
- [x] Flow: Molty creates page → Guillermo reviews in Notion → pings "standup done" → Molty processes decisions in Todoist

### Standup Agenda
1. ✅ Completed Today
2. 🚨 Overdue — Action Required
3. 📥 Inbox Triage
4. 📅 Coming Up (Next 7 Days)
5. 🗂️ Floating Tasks (No Due Date)
6. 📅 **Calendar Review (rest of week)** ← TO BUILD
7. 🎯 Tomorrow's Top Priority
8. 🧱 Blockers

### Standup Calendar Section — TO BUILD
When generating the standup, include:
- Tomorrow's schedule at a glance
- Rest-of-week calendar overview
- Identify free slots for P1/P2 tasks with time estimates
- Auto-create time blocks for confirmed tasks
- Flag scheduling conflicts

---

## Phase 4: Weekly Review 🟡 NOT STARTED

### Plan
- **When:** Sunday 3PM HKT (07:00 UTC)
- **Channel:** Webchat
- **Model:** Sonnet or Opus (needs deeper analysis)
- **Trigger:** Cron job (agentTurn, isolated session)

### Agenda
1. Week Retrospective — What worked, what didn't
2. Overdue Triage — Clear the backlog
3. Week Ahead Calendar — Preview and prep
4. Weekly Goals — Set 3-5 key outcomes
5. Task Queue — Prioritize the week's work

### To Do
- [ ] Create cron job for Sunday 3PM HKT
- [ ] Build Notion template for weekly review (similar to daily but broader)
- [ ] Include time-tracking insights if available

---

## Phase 5: Smart Scheduling Engine 🟡 NOT STARTED

### Vision (Reclaim.ai Style)
Build intelligent auto-scheduling that:
- Finds optimal time slots for tasks based on priority + energy schedule
- Auto-creates calendar blocks for P1 tasks (no approval needed)
- Reschedules displaced tasks when conflicts arise (e.g., Guillermo moves something)
- Respects life commitments (school runs = non-negotiable)
- Maintains buffer time between events (15 min default)
- Ensures exercise slot exists every day

### Architecture
```
Todoist Task (with priority + time estimate + due date)
    ↓
Scheduling Engine
    ↓ reads
All Calendars (free/busy across Brinc, Personal, Shenanigans)
    ↓ applies
Energy Schedule + Life Commitments + Priority Rules
    ↓ outputs
Calendar Event (on correct calendar) + Busy Block (on Brinc if non-Brinc)
```

### Rules
- P1 tasks: auto-schedule in next available deep-work slot
- P2 tasks: suggest slot at standup, create after approval
- P3/P4: no auto-scheduling, review at standup
- If a slot is lost (meeting booked over it): find next available, re-block
- If Guillermo moves a task block: respect the move, don't fight it

### To Do
- [ ] Build `find_free_slots()` — scan calendars, return available windows
- [ ] Build `schedule_task()` — place task in optimal slot per energy rules
- [ ] Build `reschedule_displaced()` — detect conflicts, auto-relocate tasks
- [ ] Build `daily_schedule_sync()` — run at standup, reconcile Todoist ↔ Calendar
- [ ] Integrate with standup: show proposed schedule, let Guillermo adjust
- [ ] Handle recurring task scheduling (e.g., exercise finds a slot daily)

### Research
- Reclaim.ai: https://reclaim.ai/ — study their approach for inspiration
- May complement or replace custom logic later

---

## Estimated Progress

| Phase | Status | Effort | Done |
|-------|--------|--------|------|
| Phase 1: Todoist | ✅ Complete | ~2 hours | 2026-02-05 |
| Phase 2: Calendar | ✅ Complete | ~2 hours | 2026-02-05 |
| Phase 3: Daily Standup | ✅ Complete (calendar section pending) | ~1 hour | 2026-02-05 |
| Phase 4: Weekly Review | 🟡 Not started | ~1 hour | — |
| Phase 5: Smart Scheduling | 🟡 Not started | ~4-6 hours | — |

---

## Key Files

| File | Purpose |
|------|---------|
| `/data/workspace/credentials/todoist.env` | Todoist API token |
| `/data/workspace/credentials/calendar-tokens-brinc.json` | Google Calendar OAuth tokens |
| `/data/workspace/credentials/calendar-config.json` | Calendar config (IDs, rules, commitments) |
| `/data/workspace/credentials/google-oauth.json` | Google OAuth client credentials |
| `/data/workspace/scripts/calendar.sh` | Calendar CLI |
| `/data/workspace/scripts/gmail.sh` | Gmail CLI |
| `/data/workspace/scripts/process-inbox.md` | Inbox processing protocol |

---

*This plan persisted to file to survive context pruning. Updated 2026-02-05 after completing Phases 1-3.*
