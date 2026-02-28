# Daily Standup Process
*Documented 2026-02-28 — Guillermo's standing instructions. Do not deviate.*

---

## Phase 1 — Molty Preps (before sending to Guillermo)

### 1. Check MC + Todoist alignment
- Fetch all open MC tasks (all statuses)
- Fetch all active Todoist tasks
- Cross-reference: flag anything in MC not in Todoist (and vice versa) that should be synced
- Mark any MC tasks completed if Todoist shows them done

### 2. Catch new tasks
- Any new Todoist task Guillermo has added since last standup → add to standup
- Any new MC task assigned to Guillermo → add to standup

### 3. Rewrite new task titles (ONCE, on first processing only)
- If a Todoist task title is verbatim (unprocessed) → rewrite it
- Verbatim = not processed. Rewritten = Molty has seen and understood it.
- When rewriting: expand the title, infer priority, project, owner, time estimate
- If unclear what Guillermo meant → ASK before processing. Do not guess.
- After first rewrite: never rewrite again. Title is set.

### 4. Check ggv.molt@gmail.com
- Scan for anything relevant to today's standup (forwards, CC'd threads, Notion notifications)
- Add any actionable items to standup

### 5. Build the standup
- Update persistent standup DB (31239dd6-9afd-81ad-8ffd-d1db09b1dd36)
- Create today's cover page
- Send link to Guillermo on Telegram

---

## Phase 2 — Guillermo Processes

Guillermo fills in the Action column for each task:

| Action | Meaning |
|--------|---------|
| **Keep** | Guillermo handles it himself |
| **Molty 🦎** | Route to Molty's Den |
| **Raphael 🔴** | Route to Brinc/Raphael |
| **Leonardo 🔵** | Route to Cerebro/Leonardo |
| **Drop** | Close and remove |
| **Reschedule** | Change due date — Guillermo specifies new date |
| **Done** | Already completed |

Guillermo adds notes, blockers, questions in "Your Notes" column. Sends back when done.

---

## Phase 3 — Molty Processes After Guillermo

### 1. Sync decisions to Todoist + MC
- Delegate → move task to correct Todoist project + assign in MC
- Drop → close in Todoist + mark done in MC
- Reschedule → update due date in BOTH Todoist AND MC (must match)
- Done → close in Todoist + mark done in MC
- Keep → leave as-is, ensure it's in Guillermo's Todoist with correct due date

### 2. Block calendar for next 2-3 days
- Check Guillermo's calendars first (Personal + Brinc + Family — service account has R/W access)
- Use judgment: block tasks based on priority, existing commitments, Guillermo's rhythms
  - Big/complex tasks → mornings (Guillermo prefers big topics early)
  - Admin/comms → afternoons
  - Don't double-book existing calendar events
  - Family time (evenings, weekends) = protected unless P0
- Create calendar blocks with task name as event title

### 3. Update MC
- New tasks → create in MC if not already there
- Assign to correct agent
- Set status, priority, project

---

## Phase 4 — Overnight

- Agents pick up tasks from MC during their overnight windows
- Raphael: 00:30 HKT | Leonardo: 01:30 HKT | Molty: 03:00 HKT
- Pre-flight mandatory (PLAN-007): read memory logs + check MC before executing

---

## Phase 5 — Morning Briefing (06:30 HKT)

- Overnight work summarised in morning briefing (squad section)
- Completed tasks → linked Notion pages
- Under Review → flagged for Guillermo's eyes
- Blocked → specific ask surfaced

---

## Key Rules

1. **Verbatim title = unprocessed.** Always rewrite new tasks on first processing.
2. **Dates must match everywhere.** Todoist due date = MC due date. Always.
3. **Calendar access is available.** Use it. Don't ask Guillermo what he has booked — check.
4. **Ask when uncertain.** Better to clarify a task than process it wrong.
5. **Don't regenerate if already exists.** Check standup-state.json first. If today's page exists, work from it.
6. **process_standup.py runs AFTER Guillermo fills in the Action column.** Not before.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `daily_standup.py` | Generates Notion page + populates DB. Run at 5PM or on demand. |
| `process_standup.py` | Processes Guillermo's decisions. Run AFTER he fills in Action column. |

## Key IDs

| Thing | ID |
|-------|-----|
| Persistent Standup DB | 31239dd6-9afd-81ad-8ffd-d1db09b1dd36 |
| Standup DB (legacy) | 2fe39dd69afd81f189f7e58925dad602 |
| Todoist — Molty's Den | 6fwH32grqrCJF23R |
| Todoist — Brinc | 6M5rpGgV6q865hrX |
| Todoist — Cerebro | 6g53F7ccF8HHjgXM |
| Standup state file | /data/workspace/logs/standup-state.json |

---

*Last updated: 2026-02-28 by Molty. Update this file whenever the process changes.*
