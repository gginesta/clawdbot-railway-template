# Daily Standup Process v3

*Updated: Feb 23, 2026*

## Flow (strict order — no skipping steps)

### Step 1: Run the script
```bash
/data/workspace/.venv/bin/python3 /data/workspace/scripts/daily_standup.py
```
- Timeout: **120 seconds minimum**
- Fetches Todoist tasks, deduplicates, groups sub-tasks
- Classifies into 🔥 Needs Your Input + 📋 Active Pipeline
- Creates Notion standup page with two inline databases
- Blocks NO calendar yet — wait for Guillermo's input first

### Step 2: Send Telegram summary
- Overdue count + task names (not just numbers)
- Items needing decision + top 3 names
- What Molty is handling
- Notion page link
- **DO NOT block calendar yet**

### Step 3: Guillermo reviews Notion page
- Sets Action column (✅ Keep / 📅 Reschedule / 🗑️ Drop / 🔀 Delegate / ✔️ Done)
- Leaves comments in "Your Comments" column
- Signals done (e.g. "standup done", "done", "reviewed")

### Step 4: Molty processes Guillermo's decisions
**Only after Guillermo says done:**
1. Read the Notion page — process every Action + Comment
2. Update Todoist tasks accordingly (reschedule, complete, delegate)
3. Block calendar for tasks that need focus time
4. Identify what Molty handles vs what goes to Raphael/Leonardo
5. Route tasks to other agents via webhook if needed
6. Send confirmation to Guillermo

## Notion Page Format

### Column order (both tables)
**Task → Your Comments → Action → Due Date → Molty's Notes → Owner → Priority → Section → Time Est. → Project**

"Your Comments" is ALWAYS the 2nd column (next to Task) so Guillermo can quickly scan and respond.

### Page structure (top to bottom)
1. 📋 Callout — date, counts, overdue highlights
2. 🎯 Tomorrow's top priority callout (yellow)
3. ✅ Completed since last standup (bullet list)
4. 🔥 Needs Your Input (Table 1) — Guillermo's focus
5. 📋 Active Pipeline (Table 2) — reference only
6. 🧱 Blockers

### Molty's Notes quality
- **NEVER** generic ("Overdue by 2 days; I'll handle")
- **ALWAYS** actionable: what specifically will happen, or what decision is needed
- Every task gets notes — no empty cells
- Include description/labels as context

## Cron
- **Trigger:** 5PM HKT daily
- **Script:** `/data/workspace/scripts/daily_standup.py`
- **Timeout:** 120s
- **Model:** Haiku (cheap)

## Anti-patterns (never do these)
- ❌ Skip the script and send a manual summary
- ❌ Block calendar before Guillermo reviews
- ❌ Send just numbers without task names
- ❌ Leave empty Molty's Notes
- ❌ Ignore prior session instructions about format
