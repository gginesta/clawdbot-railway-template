# PLAN-007: Overnight Workflow Overhaul (Model B)
**Created:** 2026-02-28  
**Status:** IN PROGRESS — approved by Guillermo 2026-02-28  
**Priority:** P0 — affects tonight's overnight window (03:00 HKT)  
**Owner:** Molty 🦎  

---

## Problem Statement

The overnight cron session duplicated already-completed work (Spanish passport research) because it ran in a completely isolated session with no access to MEMORY.md, daily logs, or any prior conversation context. This caused:

1. Wasted compute + time on work already done
2. Confusion and loss of trust in overnight outputs
3. A promised pre-flight check that was never actually implemented

---

## Root Cause Analysis

### Confirmed Root Cause: `sessionTarget: isolated`

The **Molty Nightly Task Worker** cron is configured with:
```
sessionTarget: isolated
```
This means it starts as a completely blank slate — no MEMORY.md, no daily logs, no knowledge of what's been discussed or completed in any prior session. It picks tasks from Todoist by existence alone: if a task is open, it executes it.

Compare to the **Daily Morning Briefing** cron which is `target: main` — that's why briefings work correctly with full context.

### Secondary Root Causes

| Cause | Detail |
|-------|--------|
| No pre-flight state check | Cron prompt doesn't verify if work is already done before executing |
| MC task statuses stale | Completed tasks stay "Backlog" if not marked in-session — overnight picks them up |
| Lessons in MEMORY.md not applied by isolated sessions | They literally cannot read it |
| No "do-not-touch" signal | No mechanism to flag tasks as "discussed/handled, verify before acting" |

---

## Chosen Model: Model B

**Main session does all overnight work directly. No sub-agents for overnight task execution.**

### Why this is right
- Main session has full MEMORY.md access
- Main session has memory_search capability over all prior logs
- Lessons learned are actually applicable
- Prior conversation context is available
- No context handoff complexity

### Trade-offs accepted
- Slightly slower (Sonnet vs Haiku) — acceptable for quality
- If we hit session limits or model rate limits, we revisit Model A

---

## Changes Required

### 1. Molty's Nightly Task Worker — Switch to Main Session

**Current config:**
```json
{
  "sessionTarget": "isolated",
  "agentId": "",
  "payload": { "model": "anthropic/claude-sonnet-4-6" }
}
```

**Target config:**
```json
{
  "sessionTarget": "main",
  "agentId": "main",
  "payload": { "model": "anthropic/claude-sonnet-4-6" }
}
```

### 2. Rewrite the Overnight Cron Prompt

The new prompt must begin with a **mandatory pre-flight checklist** before touching any task. Structure:

```
PHASE 0: PRE-FLIGHT (mandatory — do not skip)
1. Read today's daily memory log: cat /data/workspace/memory/YYYY-MM-DD.md
2. Read yesterday's daily memory log
3. Run memory_search for any task you're about to work on — if there's evidence 
   it was discussed, completed, or in-progress → SKIP IT, log reason, move on
4. Query MC for ALL tasks (all statuses) — cross-reference before executing
5. Mark any tasks you can confirm are done → set status "done" in MC now, 
   before doing any other work

PHASE 1: TASK SELECTION
- Only execute tasks with NO evidence of prior discussion/completion
- Flag anything ambiguous → log "needs verification" and skip

PHASE 2: EXECUTION
- Execute selected tasks fully
- Update MC status to "done" immediately after each completion
- Write Notion output, commit log

PHASE 3: LOG + REPORT
- Write overnight log to /data/workspace/logs/overnight-tasks-YYYY-MM-DD.md
- Post summary to #squad-updates Discord
```

### 3. MC Real-Time Hygiene Rule (Process Change)

**Rule:** Any task resolved in a conversation with Guillermo → marked Done in MC BEFORE sending the next reply. No exceptions.

This must be embedded in MEMORY.md and in the cron prompt itself (not just in the lessons list that isolated sessions can't read).

### 4. Raphael's Overnight Cron

Raphael runs his own overnight cron at 00:30 HKT — **first window in the sequence**. Same isolated-session problem exists even if last night's work happened to be valid. Must be fixed before tonight.

- Audit Raphael's cron config (confirm `sessionTarget`)
- Send directive to switch to `sessionTarget: main`
- Send updated pre-flight prompt pattern
- He confirms before 00:30 tonight

### 5. Leonardo's Overnight Cron

Leonardo runs his own overnight cron at 01:30 HKT. I need to:
- Send him a directive to switch his cron to `sessionTarget: main`
- Send him the updated pre-flight prompt pattern
- He confirms via #squad-updates before tonight's run

### 5. Add Todoist Completion Check to Pre-Flight

Before executing any Todoist task, check if it's been closed/completed in the last 7 days via the completed tasks endpoint. If it appears in completed history → skip.

---

## Tonight's Timeline

| Time (HKT) | Event |
|------------|-------|
| 08:27 | Plan approved by Guillermo |
| After approval | Execution: update Molty's cron config + prompt |
| After approval | Send directives to **Raphael + Leonardo** |
| 17:00 | Daily Standup — confirm all three crons ready |
| 00:30 | **Raphael** — first Model B run |
| 01:30 | **Leonardo** — second Model B run |
| 03:00 | **Molty** — third Model B run |

---

## Success Criteria

- [ ] Molty's 03:00 cron runs on `main` session
- [ ] Pre-flight check executes and produces a "tasks evaluated" log section
- [ ] No task is executed that has prior evidence of completion in memory
- [ ] MC statuses are updated in real-time throughout the session
- [ ] Morning briefing on 2026-03-01 shows clean overnight log with no duplicates
- [ ] Raphael's cron switched to Model B (00:30 window)
- [ ] Leonardo's cron switched to Model B (01:30 window)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Main session rate limit hit during overnight | Fallback to Haiku for research tasks, Sonnet for writing |
| Overnight prompt too long / hits context limit | Split into phases, write intermediate logs |
| Leonardo directive not acknowledged before 01:30 | His cron stays as-is tonight; fix applies to Molty only |

---

## Files to Update

- `/data/.openclaw/cron/jobs.json` — update Molty's nightly cron config
- `/data/workspace/plans/PLAN-007-overnight-workflow-overhaul.md` — this file
- `MEMORY.md` — add Lessons 87+ from this incident
- Directive to **Raphael** via agent-link (audit + switch cron)
- Directive to **Leonardo** via agent-link (switch cron + pre-flight prompt)

---

## Lessons to Add to MEMORY.md

87. **`sessionTarget: isolated` = completely blind.** Isolated cron sessions have zero access to MEMORY.md, daily logs, or prior session context. For any task requiring judgment or context-awareness, always use `sessionTarget: main`. Isolated sessions are only appropriate for pure mechanical tasks (backup, health check pings).
88. **Model B for overnight: main session only.** No sub-agents for overnight task execution. Main session runs the full overnight cron with memory access. If rate limits hit, revisit Model A (main session orchestrator + context-injected sub-agents).
89. **MC task status = must be current.** Any task resolved in conversation → mark Done in MC before next reply. No end-of-day batching. Stale MC status is the direct cause of duplicated work.
90. **Pre-flight before every overnight task.** Read memory logs + run memory_search on task topic BEFORE executing. If any evidence of prior work exists → skip and log reason. Never assume a "Backlog" status means the work hasn't been done.

---

*Awaiting approval. No execution until Guillermo confirms.*
