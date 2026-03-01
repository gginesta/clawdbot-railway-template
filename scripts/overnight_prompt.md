# Molty Overnight Task Worker — Model B Prompt
# Target: sessionTarget=main
# Schedule: 03:00 HKT daily
# Version: 2 (2026-02-28, PLAN-007)

---

Nightly task worker — 03:00 HKT. You are running on the main session with full memory access. Use it.

## PHASE 0: PRE-FLIGHT (MANDATORY — do not skip any step)

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

**Step 1 — Read today's and yesterday's memory logs:**
```
cat /data/workspace/memory/${TODAY}.md 2>/dev/null || echo "No log for today"
cat /data/workspace/memory/${YESTERDAY}.md 2>/dev/null || echo "No log for yesterday"
```

**Step 2 — Get all open Todoist tasks from Molty's Den:**
```
curl -s "https://api.todoist.com/api/v1/tasks" \
  -H "Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4" | python3 -c "
import json,sys
data=json.load(sys.stdin)
tasks=data.get('results',data) if isinstance(data,dict) else data
for t in tasks:
    print(f'[{t[\"id\"]}] {t.get(\"content\",\"\")}')
"
```

**Step 3 — For EACH task on that list, run memory_search before touching it.**
Search for the task title. If any result shows the task was discussed, completed, or in-progress in a prior session → **SKIP IT**. Log the skip reason. Do not guess — if uncertain, skip and flag for Guillermo.

**Step 4 — Query MC for all tasks to cross-reference:**
```
curl -s "https://resilient-chinchilla-241.convex.site/api/tasks?assignee=molty" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
```
For any MC task that appears done based on memory evidence → mark it done now, before doing any other work:
```
curl -s -X PATCH https://resilient-chinchilla-241.convex.site/api/task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc" \
  -d '{"id":"<mc_id>","status":"done"}'
```

**Step 5 — Write your pre-flight summary to the log before proceeding:**
```
/data/workspace/logs/overnight-tasks-${TODAY}.md
```
Format:
```
# Overnight Tasks — {DATE}
## Pre-flight
- Tasks evaluated: N
- Skipped (already done/discussed): N — [list them with reason]
- Proceeding to execute: N — [list them]
```

Only proceed to Phase 1 after this file is written.

---

## PHASE 0.5: PLAN-009 — Phase 3 MC Features (TONIGHT ONLY — 2026-03-01)

**Run this before normal Todoist task processing. This is the priority work tonight.**
Plan: /data/workspace/plans/PLAN-009-phase3-features.md
Time budget for this phase: 90 min. Stop at 02:45 HKT regardless of where you are.

### Stream A — Cron config (no code deploy needed, do first, ~25 min)

**A1: Enable MC_PASSWORD on Vercel**
```
curl -s -X POST "https://api.vercel.com/v10/projects/tmnt-mission-control/env" \
  -H "Authorization: Bearer vcp_7dd90Ihydd6STMuelqNXRCb7eOTfe4oX2HvTDmyLw4PnNpQ4FF1A1Jcg" \
  -H "Content-Type: application/json" \
  -d '{"key":"MC_PASSWORD","value":"<generate a strong 12-char password>","type":"plain","target":["production"]}'
```
DM the password to Guillermo on Telegram (id: 1097408992) immediately after setting it.
Mark MC task `jn7avzp7axhkc1bazpkmbr5yzs81q95d` done.

**A2: Wire usage report into heartbeat cron (46d1ca32)**
The script `/data/workspace/scripts/mc-usage-report.sh` already exists.
Update the heartbeat cron payload to call it after the heartbeat ping.
Use `openclaw cron edit 46d1ca32` or patch the cron config directly.
Mark MC task `jn7aj2j76f6kpm48swenp6verx81qwg8` done.

**A3: Wire Todoist sync cron (every 30min)**
Script: `/data/workspace/scripts/mc-todoist-sync.sh`
Create new OpenClaw cron: schedule `*/30 * * * *`, isolated session, runs the script.
Mark MC task `jn71fqz0ymrkj056n0gkw0218d81qd4j` done.

**A4: Wire weekly digest cron (Fri 17:00 HKT)**
Script: `/data/workspace/scripts/mc-weekly-digest.sh`
Create new OpenClaw cron: schedule `0 17 * * 5 @ Asia/Hong_Kong`, isolated session.
Mark MC task `jn7efj8tj4zg8sxh29rdf41htn81qwvz` done.

---

### Stream B — MC codebase changes (~55 min)

Clone the repo:
```
cd /tmp && git clone https://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@github.com/gginesta/tmnt-mission-control.git && cd tmnt-mission-control
```

Make ALL code changes below, then do ONE git push at the end. Vercel auto-deploys from main.

**B1: Clean up ESLint warnings** (~10 min)
Fix 4 specific unused imports:
- `Badge` in calendar component
- `ProjectName` in sewer/war-room components
- `router` in login component
- color helpers in activity-item component
Search for these with grep, remove the unused imports.
Mark MC task `jn72t1m0gyp35d4spj2zqhwpjh81qp13` done.

**B2: Mobile-Responsive Polish** (~20 min)
Audit all 6 live screens. Apply:
- Sidebar → bottom nav on mobile (< 768px)
- Calendar → vertical scroll on mobile
- War Room Kanban → horizontal scroll with snap on mobile
- Test at 375px, 768px, 1024px breakpoints
Use Tailwind responsive prefixes (`sm:`, `md:`). Don't break desktop layout.
Mark MC task `jn701krgqbwv7mw2tmrtqqczeh81q29d` done.

**B3: Enhanced Dojo — Quick Actions** (~15 min)
Add to the home/dojo page:
- "Create Task" button → opens task creation modal (or links to war room with new task)
- Overdue tasks section with red badge count
- "This Week" mini-calendar widget showing today's calendar events (pull from existing calendar data)
Keep it clean — don't clutter the existing layout.
Mark MC task `jn7dzw9b6nnhxc5t75vwaez4fs81q0rd` done.

**B4: Project Views** (~15 min)
Add routes `/project/brinc`, `/project/cerebro`, `/project/mana`.
Each page shows:
- Tasks filtered to that project (query MC `?project=brinc` etc.)
- Activity feed filtered to that project
- Agents active on that project
Add shortcuts in sidebar. Reuse existing task/activity components with project filter.
Mark MC task `jn737fa7zkc5w7yq48m0rq0g5d81q6j0` done.

**Push all changes:**
```
git add -A && git commit -m "feat: Phase 3 features — mobile polish, dojo quick actions, project views, ESLint cleanup" && git push origin main
```

Wait ~3 min for Vercel deploy, then verify https://tmnt-mission-control.vercel.app loads correctly.

---

### Stream C — If time permits after B4 (check clock — only if before 02:45 HKT)

Skip if short on time. These defer cleanly to next overnight.
- [A2] Pizza Tracker Cost Tracking — new Convex table, needs schema push (risky solo)
- [B4] DnD Kanban — library integration (risky solo)

---

### On completion of PLAN-009
Mark all completed MC tasks done (IDs in plan file).
Add to the overnight log under ✅ Completed with links.
Then continue to normal Todoist task processing (PHASE 1 onwards) for remaining time.

---

## PHASE 1: TASK SELECTION

For each task you're proceeding with, classify:
- **AUTO** — research / write / draft / plan / compile / summarise / find → execute it
- **FLAG** — needs Guillermo decision / external send / financial / public-facing / ambiguous → log reason, skip

Time budget: target 90 minutes total, hard stop at 2 hours. If a task will run long, work to the first completable milestone and leave a clear stopping-point note. Do NOT try to clear the entire list.

---

## PHASE 2: EXECUTION

For each AUTO task:
1. Execute fully and properly — quality over speed
2. Research: web_search + web_fetch → write findings as a Notion page
3. Writing: produce the document as a Notion page
4. **Immediately after completing each task:**
   - Close in Todoist: `POST /api/v1/tasks/{id}/close` with Bearer token
   - Mark done in MC: `PATCH /api/task` with `{"id":"<mc_id>","status":"done"}`
   - Write to log
5. If you cannot complete a task in this session → mark `in_progress` in log, do NOT close in Todoist

---

## PHASE 3: LOG + REPORT

Write final log to `/data/workspace/logs/overnight-tasks-${TODAY}.md` using this format:
```
# Overnight — Molty — {DATE}
## ✅ Completed
- Task name → Notion link (or "no output" if N/A)
  One line summary of what was done

## 👀 Under Review
- Task name → needs: [what Guillermo needs to do/decide]

## 🚩 Flagged / Blocked
- Task name → reason

## ❌ Failed
- Task name → error detail
```

Commit the log:
```
cd /data/workspace && git add logs/ && git commit -m "log: overnight tasks ${TODAY}"
```

## PHASE 4: CONSOLIDATE + POST TO #squad-updates

Read Raphael and Leonardo's overnight summaries:
```
cat /data/shared/logs/overnight-raphael-${TODAY}.md 2>/dev/null || echo "## Raphael: No summary found"
cat /data/shared/logs/overnight-leonardo-${TODAY}.md 2>/dev/null || echo "## Leonardo: No summary found"
```

Combine all three agent summaries (Raphael, Leonardo, Molty) into a single consolidated file:
```
/data/workspace/logs/overnight-consolidated-${TODAY}.md
```

Format:
```
# Overnight Consolidated — {DATE}
## 🔴 Raphael
[paste content from raphael summary, or "No summary — check agent logs"]

## 🔵 Leonardo
[paste content from leonardo summary, or "No summary — check agent logs"]

## 🦎 Molty
[paste content from molty log]
```

Post ONE consolidated summary to #squad-updates (Discord channel 1468164181155909743):
```
🌙 Overnight Report — {DATE}

🔴 Raphael: ✅ N done | 👀 N review | 🚩 N flagged
[one line per completed item]
[one line per under-review item with "needs: X"]

🔵 Leonardo: ✅ N done | 👀 N review | 🚩 N flagged
[one line per completed item]
[one line per under-review item with "needs: X"]

🦎 Molty: ✅ N done | ⏭️ N skipped | 🚩 N flagged
[one line per completed item with Notion link]
[one line per flagged item]
```

If an agent's summary file is missing, note it: "🔴 Raphael: No summary file — check agent logs"

Update MC activity:
```
POST /api/activity — agentId: molty, type: task_update, title: "Overnight consolidated report — {DATE}", body: "[summary counts]", project: fleet
```
