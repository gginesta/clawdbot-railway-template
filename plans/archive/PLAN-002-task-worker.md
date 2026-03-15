# PLAN-002: Autonomous Task Worker
**Created:** 2026-02-24 | **Status:** Approved | **Approved changes:**
- Nightly task worker for Molty (02:00 HKT), results go into morning briefing
- Same pattern for Raphael + Leonardo via their own agents

---

## Architecture

```
Todoist (task added with project = agent's project OR @molty-do / @raphael-do / @leonardo-do label)
    ↓
mc-todoist-sync.sh (every 2h heartbeat) — pushes tasks to MC with correct assignee
    ↓
Mission Control (tasks visible, assignee set: molty / raphael / leonardo)
    ↓
Nightly Task Worker Cron — 02:00 HKT (each agent on their own instance)
    ↓
Agent reads MC tasks assigned to self
    ↓
Evaluate: auto-executable? or needs-input?
    ↓
Execute each auto task → save output to Notion page → close Todoist + MC
    ↓
Write summary to /data/workspace/logs/overnight-tasks-YYYY-MM-DD.md
    ↓
Morning briefing reads log → includes in 06:30 HKT briefing to Guillermo
```

---

## Task Classification (how agent decides)

| Auto-execute | Needs-flag |
|---|---|
| Research (web search + write) | Requires Guillermo decision |
| Write/draft/plan/prepare | Requires external send (email/tweet) |
| Summarise/analyse | Ambiguous scope |
| Compile/gather info | Financial/sensitive actions |

Rule: if in doubt, flag — never attempt partial or wrong. Flag = add to tomorrow's standup with explanation.

---

## Ownership Detection

Task is owned by Molty if:
- Todoist project = Molty's Den (6fwH32grqrCJF23R), OR
- Has label `@molty-do`

Task is owned by Raphael if:
- Todoist project = Brinc (6M5rpGgV6q865hrX) AND content suggests execution (not Guillermo strategic), OR
- Has label `@raphael-do`

Task is owned by Leonardo if:
- Todoist project = Cerebro/Launchpad-related, OR
- Has label `@leonardo-do`

---

## Files

- **Cron:** `46d1ca32` heartbeat updated to push tasks to MC (via mc-todoist-sync.sh)
- **New cron:** Molty Task Worker — `0 18 * * *` UTC (02:00 HKT), isolated, Sonnet, 25min timeout
- **Log output:** `/data/workspace/logs/overnight-tasks-YYYY-MM-DD.md`
- **Morning briefing:** reads log and includes "Overnight completions" section

---

## Molty Cron Prompt (to be set)

```
Nightly task worker (02:00 HKT). Work through Molty-owned tasks silently.

1. Fetch active Todoist tasks where project = Molty's Den OR label = @molty-do:
   curl -s "https://api.todoist.com/api/v1/tasks?project_id=6fwH32grqrCJF23R" \
     -H "Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4"

2. For each task, classify: AUTO (research/write/draft/compile) or FLAG (needs Guillermo input)

3. For AUTO tasks — execute:
   - Research tasks: use web_search + web_fetch, write a Notion page with findings
   - Writing tasks: produce the document, save as Notion page
   - Close in Todoist: POST /tasks/{id}/close
   - Close in MC: PATCH /api/task with status: done

4. For FLAG tasks: note why in the log — do NOT attempt

5. Write summary to /data/workspace/logs/overnight-tasks-{DATE}.md:
   # Overnight Task Summary — {DATE}
   ## ✅ Completed
   - [task name] → [Notion link]
   ## ⏭️ Flagged (needs input)
   - [task name]: [reason]
   ## ❌ Failed
   - [task name]: [error]

6. Commit the log file to git.

Be thorough. Quality over speed. If a task will take >10 minutes, note it as in-progress and continue next cycle.
```

---

## Raphael + Leonardo Pattern

Same architecture. Each agent configures their own task worker cron. Communication:
1. Molty sends webhook to Raphael + Leonardo with the task worker cron config
2. Each agent adds it to their own OpenClaw instance
3. Tasks assigned to them in MC → they pick up nightly
4. Results flow back to MC activity feed → Molty reads it in morning briefing

**Change ticket required** — coordinate with Raphael/Leonardo via webhook after Molty's worker is proven working.

---

## Morning Briefing Integration

Add section to `morning_briefing.py`:
- Check for `/data/workspace/logs/overnight-tasks-{yesterday}.md`
- If exists and has completions: add "🌙 Overnight Work" section to briefing
- If has failures: add ⚠️ flag

---

## Sequence

1. [x] Plan approved
2. [x] Molty task worker cron created: 80105aa4, fires daily 02:00 HKT (18:00 UTC), Sonnet, 25min
3. [x] morning_briefing.py updated: reads /data/workspace/logs/overnight-tasks-{date}.md
4. [x] Todoist task: 6g4pFvQHVvGXhJW2 | MC task: jn767p5mxyp3vkgfg3sd1mm2j181r6e9
5. [x] logs/ directory created
6. [ ] Raphael/Leonardo rollout — separate change ticket after Molty first run validated
7. [ ] Verify first run tomorrow 02:00 HKT (check log file exists + tasks closed)
