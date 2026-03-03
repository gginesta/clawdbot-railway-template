# Daily Standup & Productivity System — Master Design Document
*Version 2.1 — Updated 2026-03-03 08:48 HKT*
*Status: APPROVED — implement P0 items before tonight's 5PM standup*
*This document is the source of truth. Update it when anything changes. Never let it go stale.*

---

## The Vision

A closed-loop productivity system where Guillermo captures work freely throughout the day, Molty keeps everything in sync in real time, the 5PM standup is a focused 15-minute review (not a data entry session), agents work overnight on a well-scoped queue, and Guillermo wakes up knowing exactly what happened and what to focus on — without ever repeating himself.

---

## Agreed Design Decisions (2026-03-03)

| Question | Decision |
|----------|----------|
| Tomorrow's Focus: how many items? | **ONE item only.** The single thing that makes the day worthwhile. |
| Calendar horizon | **5 working days** |
| Squad pre-standup check timing | **Webhook at 4:30, wait 10 minutes, proceed regardless.** Note in standup if no reply received. |
| Task title edit format | **Silent rewrite** — rewrite to be specific and actionable. The quality of the rewrite IS the signal. No prefix/marker. |
| Clarifying questions delivery | **Both** — short Telegram heads-up + full context in Notion callout. Guillermo prefers more questions over silence + mistakes. |
| MC backlog tasks (15 assigned to Molty) | **Review together with Guillermo** before moving or actioning. |
| Real-time task closure | **Non-negotiable** — verbal "done" = Todoist + Notion + MC updated in same response. |

---

## The Full Day Cycle

```
THROUGHOUT THE DAY (continuous)
  Guillermo → Todoist (capture raw tasks)
  Guillermo → chat (tells Molty tasks are done → Molty acts immediately)
  Guillermo + Squad Leads → MC (task updates)
  Molty → real-time sync: closes tasks, updates Todoist/Notion/MC on the spot

PRE-STANDUP PREP (4:30–4:55 PM)  ← Molty runs silently, no interruption
  1. Todoist: fetch new tasks since last standup → process each one
  2. Check completions: MC + squad lead status check (webhook at 4:30, wait 10 min)
  3. Check ggv.molt inbox for relevant items
  4. Sync Notion DB: mark completed, add new, update statuses
  5. Form clarifying questions (if any)
  6. Confident view confirmed → generate standup page

STANDUP GENERATION (5:00 PM)  ← Cron fires
  Molty sends Telegram: "Standup ready + link + clarifying questions (if any)"
  Notion page: full task DB + blank Tomorrow's Focus + any clarifying questions

GUILLERMO REVIEWS (~5:00–5:30 PM)
  Answers clarifying questions first (if any)
  Fills in Tomorrow's Focus (ONE item — the thing that makes tomorrow worthwhile)
  Reviews task DB: adjusts owners, priorities, calendar flags, MC flags
  Sets Action per task: Keep / Done / Drop / Reschedule
  Adds Your Notes for context
  Says "standup done"

POST-REVIEW PROCESSING  ← Triggered by "standup done"
  1. Book Tomorrow's Focus as calendar event
  2. Process Action column in Todoist (close/reschedule/move)
  3. Create/update MC tasks for In MC? ticked rows
  4. Book calendar blocks for Book Calendar? ticked rows
  5. Dispatch webhooks to Raphael + Leonardo with their tasks
  6. Send Telegram summary to Guillermo

OVERNIGHT (Raphael 00:30 → Leonardo 01:30 → Molty 03:00)
  Pull MC assigned tasks → work → update MC → write log → Molty consolidates

MORNING BRIEFING (06:30)
  Yesterday's ONE declared focus (did it happen?)
  Overnight report: done / failed (why) / blocked / for Guillermo review
  Today's calendar + open P1/P2 tasks + email highlights
```

---

## PHASE 0: Real-Time During the Day

**This is the foundation. The standup is only as good as the data going into it. That data must be maintained continuously — not accumulated at 5PM.**

Work is fluid. Guillermo adds tasks to Todoist throughout the day. Squad leads add tasks to MC. Things get completed, reprioritised, handed off. Molty must stay on top of ALL of it — Todoist AND MC — and keep both in sync so that by 5PM, the standup page reflects reality, not a snapshot from this morning.

### Rule 1: Verbal "done" = immediate action. Every time.

The moment Guillermo says a task is complete — in any conversation, on any platform:

1. Acknowledge in the same message
2. Close in Todoist — immediately
3. Update Notion DB row — mark done
4. Update MC — mark done (fuzzy title match)
5. Confirm: "Closed ✅" — not "I'll do that"

**No exceptions. This is the single most important rule in the system.**

### Rule 2: New Todoist tasks get processed on intake

When a new raw task appears in Todoist (via heartbeat check):
- **Rewrite title**: specific + actionable + time signal + 🦎 at the end
  - Raw: `reply raeniel`
  - Processed: `Reply to Raeniel re: FY2025 accounts — 30min 🦎`
- **One-time edit only** — never rewrite the same task again. The 🦎 confirms it's been seen.
- **Assign**: project, owner, priority (Eisenhower), time estimate, due date if obvious
- **Flag**: Book Calendar? and In MC? based on judgment
- Lightweight triage — full context added at standup

### Rule 3: MC is monitored continuously, not just at 5PM

Every heartbeat (every 2h), Molty checks MC for:
- **New tasks** added by squad leads → cross-reference with Todoist. Already there? Sync. Not there? Note for standup.
- **Completed tasks** in MC → close corresponding Todoist task immediately
- **Blocked tasks** → flag immediately, don't wait for standup or morning briefing

If a squad lead completes something in MC and hasn't updated Todoist, Molty closes it in Todoist. If Guillermo closes something in Todoist and MC is still open, Molty closes it in MC. The two systems must never diverge for more than 2 hours.

### Rule 4: Context from chat updates tasks immediately

If Guillermo mentions anything in conversation that changes a task — priority, owner, scope, status, deadline — update it in Todoist and MC on the spot. He should never have to re-explain at standup what he already said during the day.

---

## PHASE 1: Pre-Standup Prep (4:30–4:55 PM)

Runs silently. Guillermo is not interrupted.

### Step 1: Fetch and process new Todoist tasks

Pull everything added since last standup (check against standup-state.json date).

For each unprocessed task (Inbox project = unprocessed):
- Rewrite title (if not already done during day)
- Assign: project, owner, priority, time estimate, due date
- Flag: Book Calendar? (default YES for P1/P2 owner=Guillermo), In MC? (YES for agent-owned work)
- Write Molty's Notes: context, recommendation, what I'll do
- Push to Notion DB

### Step 2: Check completions

**MC check**: `GET /api/tasks` — find tasks marked done today. Cross-reference with Todoist.
- MC done but Todoist open → close in Todoist
- Todoist closed but MC open → close in MC

**Squad lead check** (webhook at 4:30):
Message to Raphael + Leonardo:
> "Pre-standup check — what have you completed or progressed today that may not be in MC yet? Quick status reply please."

Wait 10 minutes. If they reply → incorporate into standup. If not → note "no pre-standup update received from [agent]" in standup.

**Todoist recently completed**: Pull closed tasks (last 24h). Mark corresponding Notion rows done.

### Step 3: Check ggv.molt inbox

Scan for anything since last standup:
- Action-required → surface in standup email section
- Creates a new task → add to Todoist + Notion
- Changes task status → update accordingly

### Step 4: Sync Notion DB

- Mark completed rows as done (keep history, don't delete)
- Add newly processed tasks
- Update priorities/owners/statuses where context changed
- Deduplicate: never create a row that already exists (title + project check)

### Step 5: Form clarifying questions

Genuine uncertainty only — not second-guessing. If I'm unclear on:
- Who should own a task
- Whether something is still relevant
- Priority of two competing P1s
- Any context that would change my recommendation

→ Add as a numbered list in the standup page + short Telegram mention.

---

## PHASE 2: Standup Generation (5:00 PM)

### Notion Page Structure

```
📋 CALLOUT — Daily Standup: Tue Mar 3, 2026
   [2-3 sentence situation summary: what moved today, what's new, what's overdue]
   [Squad status: Raphael — X | Leonardo — Y | from pre-standup check]

🎯 TOMORROW'S FOCUS  ← Yellow callout, Guillermo fills in
   [BLANK — Guillermo writes the ONE thing that makes tomorrow worthwhile]
   [This becomes a calendar event. One item only.]

📬 EMAIL HIGHLIGHTS  ← Only if relevant items exist
   [Items from ggv.molt needing attention]

❓ CLARIFYING QUESTIONS  ← Only if Molty has genuine uncertainty
   1. [Question]
   2. [Question]
   [Answer these before reviewing the table]

📋 TASK DATABASE
   [Persistent DB — filtered to active + new + recently completed]
   [See column design below]

🧱 BLOCKERS
   [MC blocked tasks from agents — with specific asks]
```

### Telegram message at 5PM

```
📋 Standup ready — Tue Mar 3

Today: 3 new tasks · 5 completed · 2 overdue
🔴 Raphael: [status from pre-standup check, or "no update received"]
🔵 Leonardo: [status from pre-standup check, or "no update received"]

[If clarifying questions:]
❓ 2 questions before you start — see Notion page

Fill in Tomorrow's Focus (ONE item), review the table, say "standup done"
→ [Notion link]
```

---

## PHASE 3: Guillermo Reviews

Guillermo's process:

1. **Answer clarifying questions** first — sets context for everything else
2. **Write Tomorrow's Focus** — ONE item. The thing that makes tomorrow worthwhile. Becomes a calendar event.
3. **Review task rows**:
   - Adjust Owner if I got it wrong
   - Adjust Priority if needed
   - Adjust Book Calendar? — untick what doesn't need time, tick what I missed
   - Adjust In MC? — confirm what goes to agents overnight
   - Set Action: Keep / Done / Drop / Reschedule
   - Add Your Notes for any context I need
4. **Say "standup done"**

**What Guillermo should NOT need to do:**
- Re-enter work already discussed during the day
- Re-explain context already given in earlier conversations
- Look up task status — Molty has already checked

---

## PHASE 4: Post-Review Processing

Triggered immediately when Guillermo says "standup done".

### 4a. Tomorrow's Focus → Calendar

- Parse the text from the callout block
- Book as a calendar event for tomorrow, first available slot 9:00–13:00 HKT
- Check both Brinc and Personal calendars for conflicts
- Brinc-related → Brinc calendar. Everything else → Personal calendar
- Duration: 1 hour default (or estimate from task context)
- If nothing written → warn in Telegram summary

### 4b. Action column → Todoist

- **Done** → close in Todoist + mark MC done (if exists) + update Notion row
- **Drop** → close in Todoist + archive MC (if exists) + update Notion row
- **Reschedule** → update Todoist due date (parse date from Your Notes) + update MC dueDate
- **Keep** → no change (stays in Todoist, reappears in tomorrow's standup)

### 4c. Owner column → Routing

- **Raphael** → move task to Brinc project in Todoist + webhook with context (task, notes, due, priority)
- **Leonardo** → move task to Cerebro project in Todoist + webhook with context
- **Molty** → move task to Molty's Den in Todoist
- **Guillermo** → no move

### 4d. In MC? → Mission Control

For every ticked row:
1. Search MC: `GET /api/tasks` → fuzzy title match (≥55% similarity)
2. **Found + open** → update: priority, assignee, dueDate, description. Do NOT create duplicate.
3. **Not found** → create:
   ```json
   {
     "title": "[task title]",
     "project": "[brinc/cerebro/mana/fleet/personal]",
     "priority": "[p0/p1/p2/p3]",
     "assignees": ["[from Owner column]"],
     "dueDate": "[from Due Date if set]",
     "description": "Guillermo's Notes: ... | Molty's Notes: ...",
     "createdBy": "molty",
     "status": "assigned"
   }
   ```
4. **Found + done** → don't touch (already closed)
5. **Ticked + Action=Done** → mark MC done (don't create if not exists)

### 4e. Book Calendar? → Calendar blocks

**Default stance: block more, not less.**

For every ticked row:
1. Check if similar event exists in next 5 working days (keyword match)
2. If not → find free slot:
   - Duration from Time Est. column
   - Check BOTH calendars for conflicts
   - Work hours: 9:00–18:00 HKT
   - Preferred: morning first (9–13), then afternoon (14–18)
   - Book in correct calendar (Brinc vs Personal)
3. Event: `🎯 [P1] Task name` + 15-min popup reminder
4. If no slot in 5 days → flag in summary (rare, but note it)

### 4f. Telegram Summary

```
✅ Standup processed — Tue Mar 3

🎯 Tomorrow's Focus booked:
  • "Reply to Raeniel re: accounts" → Wed 9:00–9:45 (Brinc cal)

📅 Calendar blocks added (3):
  • Wed 10:00–11:30: Helm Proposal prep [P2]
  • Thu 9:00–10:00: Cerebro beta outreach [P2]
  • Fri 9:00–10:30: Mana Capital portfolio review [P1]

🐢 MC tasks created/updated (3):
  • 🔴 Raphael: A8 proposal template [p1, due Fri] — assigned
  • 🔵 Leonardo: Stripe live keys [p0, due tomorrow] — assigned
  • 🦎 Molty: Standup redesign implementation [p1] — assigned

📤 Dispatched to squad:
  • Raphael → "A8 proposal + brand audit by Friday"
  • Leonardo → "Stripe webhook is P0 — prioritise tonight"

✔️ Closed in Todoist (3): Brinc Q&A, Polymarket context, GetLinks invite
📅 Rescheduled (1): Spanish consulate → Mar 10

❓ Still open (need your reply before I can proceed):
  • Beta list of 20 — draft from you or Leonardo researches from CRM?
```

---

## PHASE 5: Overnight

### Agent schedule

| Time (HKT) | Agent |
|------------|-------|
| 00:30 | Raphael |
| 01:30 | Leonardo |
| 03:00 | Molty (consolidates) |

### Each agent's overnight process

1. **Pre-flight** (mandatory — no skipping):
   - Read today's memory log (cat file)
   - Pull MC assigned tasks (curl API)
   - Scan logs for what's already done — skip duplicates

2. **Select tasks**: 1–3 tasks within 90-min budget. Highest priority first. Never try to clear the backlog.

3. **Execute**: PPEE always. Research before acting. One clean attempt per task.

4. **Update MC per task**:
   - Done → `status: "done"`
   - Needs Guillermo review → `status: "under_review"` + deliverable link (Notion preferred)
   - Blocked → `status: "blocked"` + **specific ask** (never vague)

5. **Write overnight log** to `/data/shared/logs/overnight-<agent>-YYYY-MM-DD.md`:

```markdown
# Overnight Log — [Agent] — YYYY-MM-DD

## ✅ Completed
- [Task name] — [what was done] — [link if applicable]

## 👀 Under Review (needs Guillermo)
- [Task name] — [what to review] — [link]

## ❌ Failed
- [Task name] — Why: [specific reason] — To unblock: [what's needed]

## 🚧 Blocked
- [Task name] — Blocker: [specific reason] — Need from Guillermo: [specific ask]

## ⏭ Skipped (out of budget / not started)
- [Task name]
```

6. **Post to MC activity feed**: one entry per completed/blocked task

### Molty's 03:00 consolidation

1. Read Raphael's + Leonardo's overnight logs from `/data/shared/logs/`
2. Check ggv.molt inbox (overnight emails — action or flag as needed)
3. Update MC for any tasks agents missed updating
4. Write consolidated report to `/data/shared/logs/overnight-consolidated-YYYY-MM-DD.md`
5. Post summary to #squad-updates on Discord
6. Update today's memory log

---

## PHASE 6: Morning Briefing (06:30)

Structure, in order:

```
Good morning, Guillermo — Tue Mar 3

🌤 WEATHER + OUTLOOK

📌 YESTERDAY'S DECLARED FOCUS
   You said: "[exact text from yesterday's Tomorrow's Focus]"
   Status: ✅ Done / ❌ Not done / 🔄 In progress
   (checked via calendar event + MC status)

🌙 OVERNIGHT REPORT
   ✅ Completed: [list with links]
   👀 Needs your review: [list with links — act on these]
   ❌ Failed: [task] — Why: [reason]
   🚧 Blocked: [task] — Need from you: [specific ask]

📅 TODAY'S CALENDAR
   [Full schedule from Google Calendar]
   [Includes blocks booked last night from standup]

🐢 SQUAD STATUS
   Current MC assignments per agent
   Any P0 blockers

✅ OPEN TASKS (P1/P2 only — no noise)
   [Todoist — genuinely open, not verbally confirmed done]

✉️ EMAIL
   [ggv.molt highlights since last check]

🔧 FLEET
   [OpenClaw version check]
```

---

## Notion Standup DB — Column Design

| Column | Type | Who fills | Purpose |
|--------|------|-----------|---------|
| Task | Title | Molty | Rewritten actionable title (edited ONCE on first intake) |
| Your Notes | Text | Guillermo | Freeform — instructions, context, decisions |
| Action | Select | Guillermo | Keep / Done / Drop / Reschedule |
| Owner | Select | Molty pre-fills, G adjusts | Guillermo / Molty / Raphael / Leonardo |
| Book Calendar? | Checkbox | Molty pre-ticks, G overrides | Block focus time? |
| In MC? | Checkbox | Molty pre-ticks, G overrides | Goes to agent overnight queue? |
| Due Date | Date | Molty | When it's due |
| Priority | Select | Molty | P1 / P2 / P3 / P4 |
| Time Est. | Select | Molty | 15min / 30min / 1h / 2h+ |
| Project | Select | Molty | Brinc / Cerebro / Mana / Personal / Fleet |
| Section | Select | Molty | Overdue / Today / Upcoming / Backlog |
| Molty's Notes | Text | Molty | Context, status, recommendation, blocker |
| Standup Date | Date | Molty | When added |

### Pre-ticking logic

**Book Calendar? = YES (default):**
- P1 or P2 AND owner = Guillermo
- Not already in calendar
- **When in doubt: tick it.** Block is better than no block.

**Book Calendar? = NO:**
- Owner = Molty / Raphael / Leonardo (agent handles, no G time needed)
- P3 or P4
- Already blocked in calendar

**In MC? = YES:**
- Owner = Molty / Raphael / Leonardo
- Multi-step work (not a 15-min quick task)
- Project = Brinc / Cerebro / Mana / Fleet
- Not already in MC with open status

**Owner pre-fill:**
- Brinc sales / proposals / marketing / HubSpot → Raphael
- Cerebro product / engineering / features → Leonardo
- Fleet / infrastructure / TMNT / OpenClaw / crons → Molty
- Everything else (personal, finance, meetings, family, admin) → Guillermo

---

## Mission Control Integration

### Task lifecycle

```
Standup: In MC? ticked → MC created, status=assigned
Overnight: agent picks up → status=in_progress
Agent done → status=done OR under_review OR blocked
Morning briefing → Guillermo sees under_review + blocked
Guillermo reviews/unblocks → status=done
Todoist closed, Notion row updated
```

### Deduplication (mandatory before every create)

1. `GET /api/tasks` — load all open tasks
2. Fuzzy match title (≥55% similarity)
3. Found + open → UPDATE, never create
4. Found + done → skip
5. Not found → CREATE

### Required fields on every MC task

```
title, project, priority, assignees[], createdBy="molty"
status="assigned", description (G notes + Molty notes)
dueDate (if known)
```

---

## Calendar Blocking Rules

**Philosophy: Block more, not less. Guillermo can always move a block. He can't recover missed time.**

| Situation | Action |
|-----------|--------|
| Tomorrow's Focus (Guillermo writes it) | Book first available slot tomorrow, always |
| P1 + owner=Guillermo | Book within 24h |
| P2 + owner=Guillermo | Book within 3 days |
| P3 + owner=Guillermo + Book Calendar? ticked | Book within 5 days |
| P4 | Don't book unless Guillermo explicitly ticks |
| Owner = any agent | Don't book (agent work) |
| Similar event already exists | Skip, don't duplicate |

**Settings:**
- Horizon: 5 working days
- Hours: 9:00–18:00 HKT, morning preferred
- Duration: from Time Est. column (30min default)
- Format: `🎯 [P1] Task name` + 15-min popup reminder
- Brinc project → Brinc calendar | Everything else → Personal calendar
- Check BOTH calendars for conflicts before booking

---

## What Changes vs Current System

| Was | Now |
|-----|-----|
| Verbal "done" → acknowledged, not acted on | Verbal "done" → Todoist + Notion + MC updated in same response |
| Calendar auto-blocked at 5PM generation | Calendar only post-review, based on Tomorrow's Focus + approved checkboxes |
| "Tomorrow's Top Priority" auto-generated from Todoist | Left blank — Guillermo writes ONE item, his declaration |
| No pre-standup squad check | Webhook Raphael + Leonardo at 4:30 for status |
| No pre-standup email check | ggv.molt scanned, relevant items surfaced |
| In MC? checkbox exists but does nothing | In MC? → creates/updates real MC tasks |
| Overnight report: done + blocked only | Full: done + failed (why) + blocked (ask) + for G review |
| Morning briefing doesn't remind of yesterday's focus | Yesterday's Focus shown first — accountability loop |
| Design decisions disappear between sessions | This document is permanent. Updated on every change. |
| Calendar bias: conservative | Calendar bias: block more, not less |
| Clarifying questions: rare | Clarifying questions: preferred — ask > assume > mistake |

---

## Build Plan

### P0 — Before tonight's 5PM standup

| # | What | Where |
|---|------|-------|
| 1 | Real-time task closure: G says done → Todoist + Notion + MC | My discipline |
| 2 | Remove block_week_calendar() | daily_standup.py |
| 3 | Add "Book Calendar?" checkbox to Notion DB + pre-tick logic | daily_standup.py |
| 4 | Separate "Owner" column from Action | daily_standup.py |
| 5 | Simplify Action to: Keep / Done / Drop / Reschedule | daily_standup.py |
| 6 | Tomorrow's Focus → blank callout, clearly labelled | daily_standup.py |
| 7 | Wire In MC? → MC task creation in process_standup.py | process_standup.py |
| 8 | Wire Book Calendar? → calendar booking post-review | process_standup.py |
| 9 | Wire Tomorrow's Focus → calendar booking post-review | process_standup.py |

### P1 — This week

| # | What | Where |
|---|------|-------|
| 10 | Pre-standup prep: new Todoist tasks + MC sync + squad check + email scan | standup_prep.py (new) |
| 11 | Morning briefing: overnight report (done/failed/blocked/review) | morning_briefing.py |
| 12 | Morning briefing: yesterday's Tomorrow's Focus with status check | morning_briefing.py |
| 13 | Morning briefing: MC blocked + under_review items | morning_briefing.py |

### P2 — Next week

| # | What | Where |
|---|------|-------|
| 14 | Standardise overnight log format across all agents | overnight prompts |
| 15 | Molty 03:00: read R+L logs, build consolidated report | overnight_prompt.md |
| 16 | Todoist hourly inbox triage during the day | cron/triage.py (new) |

---

## Pending: MC Backlog Review

15 tasks currently in status=assigned (Molty) — all Phase 3 MC features:
C5 (File Attachments), D4 (Memory Timeline), D3 (Activity Analytics), D2 (Notification Prefs),
D6 (User Auth), D1 (Task Templates), C4 (Splinter Den Settings), C2 (Todoist Sync),
A4 (Weekly Digest), B2 (Dark Mode), B4 (Drag-and-Drop Kanban), A2 (Pizza Tracker Cost),
B3 (Enhanced Dojo), C1 (Project Views), B1 (Mobile Responsive)

**Action: Review together with Guillermo — schedule at standup or separately**

---

## Open Items (for next discussion)

- [ ] MC backlog review (15 tasks) — schedule with Guillermo
- [ ] Title rewrite format confirmed: silent rewrite, no prefix marker
- [ ] All P0 build items — implement before tonight 5PM

---

*Every change to this system must be reflected in this document immediately.*
*Memory ref: /data/workspace/memory/refs/standup-process.md*
