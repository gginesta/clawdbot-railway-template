# Daily Standup Process (v2 — Feb 13, 2026)

## Quality Standard (EVERY task must have)
1. **Priority** — P1-P4 via Eisenhower matrix
2. **Time Estimate** — 15min/30min/1h/2h+
3. **Section** — Overdue/Today/Upcoming/Inbox/Backlog
4. **Owner** — Guillermo/Molty/Raphael/Leonardo
5. **Molty's Notes** — Actionable context, not just labels. Include: status, what's blocking, what I suggest, what I'll do.

## Pre-Processing Rules
- **Deduplicate** by normalized task content before inserting
- **Never dump raw tasks** — every task gets processed with context
- **Inbox tasks** → suggest correct project + owner, add triage note
- **Overdue tasks** → flag with days overdue + suggest action (close/reschedule)
- **Molty-assigned research tasks** → I do the research BEFORE standup, include findings in notes
- **Recurring tasks** → note recurrence, suggest close if already done today

## Template (Gold Standard: Feb 7 page)
1. 📋 Callout with date + instructions (mention Action dropdown)
2. Inline "Task Review" child_database (columns: Task, Project, Priority, Section, Due Date, Action, Owner, Time Est., Molty's Notes, Your Comments)
3. Divider
4. 🎯 Tomorrow's Top Priority heading + placeholder
5. Divider  
6. 🧱 Blockers heading + status

## Post-Review (after "standup done")
1. Process Guillermo's Action selections in Todoist (close/reschedule/delegate)
2. Process "Your Comments" as action items
3. Create Google Calendar time blocks for next 1-2 days
4. Send Telegram summary with Notion link

## Script
- `/data/workspace/scripts/daily_standup.py` — main standup generator
- Cron: `bdb28765-f508-4271-a04d-9408d39f49fd` at 5PM HKT

## Sub-Task Handling
- Todoist tasks can have parent_id (nested sub-tasks)
- **Rule:** Show parent task as a row, list sub-tasks as bullet points in Molty's Notes
- Do NOT create separate rows for sub-tasks — they clutter the view
- Example: "Post Transaction Backlog" has 10 sub-tasks (Life insurance, Tax, etc.) — show as one row with sub-tasks listed
- When a parent is deferred/removed, its children follow

## Correct DB ID
- The standup script must track which DB it created (only ONE child_database per page)
- **LESSON #62**: Script created duplicate template blocks → two DBs on page → read wrong one → couldn't see comments
- Fix: Script outputs DB_ID, only create template once, verify block count after creation

## Known Issues Fixed (Feb 13)
- Duplicate tasks from Todoist (same task, different IDs) → deduplicate by content
- Missing time estimates → auto-estimate based on task type
- Missing Molty's Notes → auto-generate actionable context
- Empty pages → script now creates full template end-to-end
- Bare inbox tasks → auto-suggest triage
- Sub-tasks flattened as separate rows → now grouped under parent
- Duplicate template blocks (2 DBs on page) → script now creates exactly once
- Read wrong DB for comments → fixed by tracking correct DB ID
