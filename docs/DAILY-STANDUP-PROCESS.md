# Daily Standup Process v2

*Updated: Feb 20, 2026*

## Flow

### Step 1: Pull Todoist
- Fetch all tasks across all projects
- Fetch recently completed tasks (last 24h)

### Step 2: Process Every Task (BEFORE creating Notion page!)
Every task MUST have:
- **Clear title** — rewrite vague/lazy titles. "Divinate" what Guillermo meant. Ask if unclear.
- **Priority** (P1-P4) — based on urgency + importance
- **Time estimate** (15min / 30min / 1h / 2h+)
- **Owner** (Guillermo / Molty / Raphael / Leonardo)
- **Project** — move out of Inbox to correct project
- **Section** — Overdue / Today / Upcoming / Backlog
- **Molty's Notes** — actionable context. NEVER "Needs triage".

### Step 3: Handle Sub-Tasks
- Keep parent/child structure intact — don't flatten
- Sub-tasks display as bullets in parent's Molty's Notes
- Parent task gets the overall priority/estimate

### Step 4: Split into Two Tables
- **🔥 Needs Your Input** — overdue, inbox/untriaged, needs Guillermo's decision, today items for Guillermo
- **📋 Active Pipeline** — decided tasks with clear owners/dates/plans, Molty-owned, future backlog
- Guillermo focuses on Table 1 only. Table 2 is reference.

### Step 5: Create Notion Standup Page
Page structure (top to bottom):
1. 📋 **Callout** — date, counts, overdue highlights
2. ✅ **Completed since last standup** — bullet list (momentum!)
3. 🔥 **Needs Your Input** (Table 1) — Guillermo's focus
4. 📋 **Active Pipeline** (Table 2) — reference only
5. 🧱 **Blockers**

**Column order (both tables):** Task → Your Comments → Action → Due Date → Molty's Notes → Owner → Priority → Section → Time Est. → Project

### Step 6: Send Guillermo the Telegram Briefing
**NOT just numbers.** The message must be actionable:
- 🔥 What's overdue + task names
- 🎯 How many items need decision + top 3 names
- ✅ What Molty is handling today
- 🏆 Completed count
- 🔗 Notion link

### Step 7: Guillermo Reviews → Calendar Blocking
- Guillermo says "standup done" (or similar)
- Molty reads comments/decisions from Notion page
- Updates Todoist accordingly
- Blocks calendar for the next few days
- Sends confirmation

## Cron
- **Trigger:** 5PM HKT weekdays
- **Job ID:** `bdb28765-f508-4271-a04d-9408d39f49fd`
- **Script:** `/data/workspace/scripts/daily_standup.py`

## Anti-Patterns
- ❌ Dumping raw Todoist tasks without processing
- ❌ Flattening sub-tasks into separate top-level rows
- ❌ Sending the Notion link before processing is done
- ❌ Missing priorities or time estimates on any task
- ❌ Telegram message with just counts ("18 tasks, 1 overdue") — USELESS
- ❌ Saying "needs triage" in Molty's Notes — triage it YOURSELF
- ❌ Your Comments column buried at the end — must be SECOND column
- ❌ One mega table mixing decided + undecided tasks — use two tables
