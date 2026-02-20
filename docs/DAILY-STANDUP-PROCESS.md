# Daily Standup Process

*Locked in: Feb 18, 2026*

## Flow

### Step 1: Pull Todoist
- Fetch all tasks across all projects
- Compare vs previous standup: what's new? what's been completed?

### Step 2: Process Every Task
Every task MUST have:
- **Clear title** — rewrite vague/lazy titles to be actionable
- **Priority** (P1-P4) — based on urgency + importance
- **Time estimate** (15min / 30min / 1h / 2h+)
- **Owner** (Guillermo / Molty / Raphael / Leonardo)
- **Project** — move out of Inbox to correct project
- **Section** — Overdue / Today / Upcoming / Backlog

### Step 3: Handle Sub-Tasks
- **Keep parent/child structure intact** — don't flatten
- Sub-tasks display under their parent in Notion
- Parent task gets the overall priority/estimate; sub-tasks inherit or get their own
- If a parent has sub-tasks, show them as nested items, not separate DB rows

### Step 4: Create Notion Standup Page
- Page in Standup DB (`2fe39dd69afd81f189f7e58925dad602`)
- Callout block with summary (overdue count, today count, changes since last standup)
- Task Review DB — column order: Task → Your Comments → Action → Due Date → Molty's Notes → Owner → Priority → Section → Time Est. → Project
- Footer with blockers + notes
- **All tasks must be fully triaged BEFORE the page is sent** — Guillermo should only need to comment and decide, not triage

### Step 5: Send Guillermo the Telegram Briefing
- **NOT just numbers.** The message must be actionable and specific:
  - 🔥 What's overdue and what's the plan for each
  - 🎯 Top 2-3 items needing Guillermo's decision
  - ✅ What Molty is handling today
  - 🔗 Notion link
- Keep it concise but give real context — task names, not just counts

### Step 6: Guillermo Reviews → Calendar Blocking
- Guillermo reviews the Notion page
- Sends decisions (approve priorities, defer tasks, reassign, etc.)
- Molty takes decisions and:
  - Updates Todoist accordingly
  - Blocks calendar for the next day/week
  - Sends confirmation

## Cron
- **Trigger:** 5PM HKT weekdays
- **Job ID:** `bdb28765-f508-4271-a04d-9408d39f49fd`

## Anti-Patterns
- ❌ Dumping raw Todoist tasks without processing
- ❌ Flattening sub-tasks into separate top-level rows
- ❌ Sending the Notion link before processing is done
- ❌ Missing priorities or time estimates on any task
- ❌ Telegram message with just counts ("18 tasks, 1 overdue") — USELESS
- ❌ Saying "needs triage" in Molty's Notes — triage it YOURSELF before sending
- ❌ Your Comments column buried at the end — must be SECOND column
