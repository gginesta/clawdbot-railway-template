# PLAN-008: Overnight Consolidation + Post-Standup Audit

**Created:** 2026-03-01  
**Owner:** Molty  
**Status:** In Progress

---

## Problem

Overnight report in morning briefing was pulling MC task statuses without checking *when* tasks were completed. Stale "done" tasks from daytime work were being reported as overnight completions. No reliable way to tell what agents actually did in their overnight windows.

## Solution

### Part 1 — Post-Standup Task Pool Audit
Add a step at the end of `daily_standup.py` (after standup is processed and tasks are routed):
- For each agent (raphael, leonardo, molty): query MC tasks in `assigned`/`in_progress` status
- Cross-check against Todoist: if a Todoist task is already complete but MC still shows open → sync the status
- Remove stale or duplicate tasks flagged during standup
- Log audit results to `/data/workspace/logs/standup-audit-YYYY-MM-DD.md`
- No user involvement needed if standup runs correctly

### Part 2 — Agent Overnight Summary Files
Each agent writes their overnight summary to a shared log file when their cron completes:
- **Raphael:** `/data/shared/logs/overnight-raphael-YYYY-MM-DD.md`
- **Leonardo:** `/data/shared/logs/overnight-leonardo-YYYY-MM-DD.md`
- **Molty:** `/data/workspace/logs/overnight-tasks-YYYY-MM-DD.md` (already exists)

Format (standardised across all agents):
```markdown
# Overnight — <Agent> — YYYY-MM-DD
## ✅ Completed
- Task name → [Notion link if applicable]
  Summary of what was done
## 👀 Under Review
- Task name → needs: [what Guillermo needs to do]
## 🚩 Flagged / Blocked
- Task name → reason
## ❌ Failed
- Task name → error
```

### Part 3 — Molty 03:00 Consolidation
Molty's overnight cron (after completing its own work) reads both Raphael and Leonardo summary files, then:
1. Builds a consolidated overnight report
2. Posts to `#squad-updates` Discord channel
3. Writes consolidated summary to `/data/workspace/logs/overnight-consolidated-YYYY-MM-DD.md`

### Part 4 — Morning Briefing Update
`morning_briefing.py` overnight section replaces MC query with:
1. Read `/data/workspace/logs/overnight-consolidated-YYYY-MM-DD.md`
2. If not found (Molty cron didn't run): fall back to individual agent files
3. Format into the 🌙 Overnight Report section of the Telegram briefing

---

## Implementation Steps

| Stage | Task | Owner | Status |
|-------|------|-------|--------|
| 1 | Add post-standup audit to `daily_standup.py` | Molty | TODO |
| 2 | Update Raphael overnight cron to write summary file | Molty (via directive) | TODO |
| 3 | Update Leonardo overnight cron to write summary file | Molty (via directive) | TODO |
| 4 | Update Molty 03:00 cron to read + consolidate + post to #squad-updates | Molty | TODO |
| 5 | Update `morning_briefing.py` to read from consolidated log | Molty | TODO |

---

## Files Touched
- `/data/workspace/scripts/daily_standup.py` — add audit step
- Raphael's overnight cron script (via fleet directive)
- Leonardo's overnight cron script (via fleet directive)
- Molty's 03:00 cron script
- `/data/workspace/scripts/morning_briefing.py` — overnight section
