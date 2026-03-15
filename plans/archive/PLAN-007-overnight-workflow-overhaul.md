# PLAN-007: Overnight Workflow Overhaul
**Created:** 2026-02-28  
**Revised:** 2026-02-28 (v2 — after reading actual docs)  
**Status:** IN PROGRESS  
**Owner:** Molty 🦎  
**MC Task:** jn79k2t1saqtmy88r2vgk3yza58216z2

---

## What We Actually Know (After Reading the Docs)

### How OpenClaw Crons Work

There are **two payload kinds**, and they determine everything:

| `payload.kind` | Compatible `sessionTarget` | Has memory context? | When to use |
|----------------|---------------------------|---------------------|-------------|
| `agentTurn` | **`isolated` ONLY** | ❌ No | Autonomous task execution |
| `systemEvent` | `main` | ✅ Yes (main session) | Scripted/mechanical jobs |

**Source:** CRON_JOB_TEMPLATE.md explicitly states `sessionTarget: isolated` is MANDATORY for `agentTurn`. Using `main` with `agentTurn` is listed as an anti-pattern and breaks cron execution (Leonardo confirmed this at 13:40 HKT).

### What "Isolated" Means

An isolated `agentTurn` session:
- Starts blank — no conversation history, no prior session context
- **CAN** read files on disk (`/data/workspace/memory/*.md`) via exec
- **CAN** call REST APIs (MC, Todoist) via exec/curl
- **CANNOT** reliably use `memory_search` — the semantic index is not loaded in isolated sessions (no existing cron uses it)
- **CAN** use all standard tools (web_search, exec, Read, Write, etc.)

### What This Means for the Problem

The overnight session can't magically get memory context. But it **can** be instructed to read the memory files and MC state explicitly before doing any work. That's the only correct solution within the OpenClaw architecture.

---

## Root Cause (Definitive)

The overnight prompt did not instruct the isolated session to check prior work before executing. The session picked up open Todoist tasks and executed them blindly. The fix is to add a mandatory pre-flight to the prompt — using **file reads and API calls**, not `memory_search`.

---

## Solution: Isolated Sessions with Mandatory Pre-flight

All three overnight crons stay as `sessionTarget: isolated`, `payload.kind: agentTurn`. The fix is entirely in the prompt.

**Pre-flight sequence (embedded in prompt):**
1. Read today's + yesterday's memory log files (`cat /data/workspace/memory/YYYY-MM-DD.md`)
2. Query MC for all agent tasks including completed ones
3. For each open Todoist task — search the memory log content for any mention of it
4. If found → skip, log reason, move on. Do not execute.
5. Write pre-flight summary to log file before proceeding
6. Only then execute remaining tasks

This is deterministic, testable, and works within the actual OpenClaw cron architecture.

---

## Current State of Each Agent

| Agent | sessionTarget | Pre-flight prompt | Issues |
|-------|--------------|-------------------|--------|
| **Molty** | `isolated` ✅ | Added ✅ but has two bugs | (1) Prompt text says "MAIN session" — incorrect and misleading. (2) Uses `memory_search` which doesn't work reliably in isolated sessions |
| **Raphael** | Unknown | Added (per screenshot) | Need to verify it uses cat/curl, not memory_search |
| **Leonardo** | `isolated` ✅ | Added (per screenshot) | Need to verify content |

---

## Execution Steps

### Step 1 — Fix Molty's Overnight Prompt (do this now)
- Remove "You are running on the MAIN session" — false and confusing
- Replace `memory_search` instruction with explicit `cat` file reads
- Verify `sessionTarget: isolated` in jobs.json
- Reload config

### Step 2 — Get Raphael + Leonardo's Actual Prompt Text
- Ask both agents to paste their current overnight cron prompt
- Verify they use `cat` for memory reads, `curl` for MC — not `memory_search`
- Patch if needed

### Step 3 — Dry Run (before tonight)
- Test Molty's prompt manually: paste the prompt text into a conversation and run Phase 0 only
- Confirm pre-flight produces a log file with correct content
- Do this before 22:00 HKT

### Step 4 — Verify all three are ready before each window
- 23:00 HKT — confirm Raphael's config (his window is 00:30)
- 00:45 HKT — confirm Leonardo's config (his window is 01:30)  
- 02:45 HKT — Molty's window runs at 03:00

---

## The Correct Overnight Prompt (Molty)

```
Nightly task worker — 03:00 HKT. You are running in an isolated session. You have no prior conversation context. Follow Phase 0 before touching anything.

## PHASE 0: PRE-FLIGHT (MANDATORY — do not skip)

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

Step 1 — Read memory logs:
exec: cat /data/workspace/memory/${TODAY}.md 2>/dev/null
exec: cat /data/workspace/memory/${YESTERDAY}.md 2>/dev/null

Step 2 — Get open Todoist tasks:
exec: curl -s "https://api.todoist.com/api/v1/tasks" -H "Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4" | python3 -c "import json,sys; data=json.load(sys.stdin); tasks=data.get('results',data) if isinstance(data,dict) else data; [print(f'[{t[\"id\"]}] {t.get(\"content\",\"\")}') for t in (tasks if isinstance(tasks,list) else [])]"

Step 3 — Query MC for all Molty tasks (all statuses):
exec: curl -s "https://resilient-chinchilla-241.convex.site/api/tasks?assignee=molty" -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"

Step 4 — Cross-reference. For each open Todoist task:
- Search the memory log content (from Step 1) for any mention of the task topic
- Search the MC results for any matching task with status done/in_progress
- If any evidence exists that this task was discussed, completed, or handled → SKIP IT
- When in doubt → SKIP and flag for Guillermo

Step 5 — Write pre-flight log to /data/workspace/logs/overnight-tasks-${TODAY}.md:
# Overnight Tasks — {DATE}
## Pre-flight
- Tasks evaluated: N
- Skipped (prior evidence found): N — [list each with reason from memory log]
- Proceeding with: N — [list each]

Do not proceed to Phase 1 until this file is written.

## PHASE 1: TASK CLASSIFICATION
For each remaining task:
- AUTO: research / write / draft / plan / compile / summarise / find → execute
- FLAG: needs Guillermo decision / external send / financial / public-facing → log + skip
Time budget: 90 min target, 2h hard stop.

## PHASE 2: EXECUTION
For each AUTO task:
1. Execute fully — quality over speed
2. Research → web_search + web_fetch → write Notion page
3. Writing → produce as Notion page
4. After each completion:
   - Close in Todoist: POST https://api.todoist.com/api/v1/tasks/{id}/close -H "Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4"
   - Mark done in MC: PATCH https://resilient-chinchilla-241.convex.site/api/task -d '{"id":"<mc_id>","status":"done"}' -H "Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
5. Can't finish → log in_progress, do NOT close in Todoist

## PHASE 3: REPORT
Append to /data/workspace/logs/overnight-tasks-${TODAY}.md:
## ✅ Completed (N) — [task → Notion link]
## ⏭️ Skipped — prior evidence (N) — [task: reason]
## 🚩 Flagged — needs Guillermo (N) — [task: reason]
## ❌ Failed (N) — [task: error]

Then:
1. git add logs/ && git commit -m "log: overnight tasks ${TODAY}"
2. Post to #squad-updates (Discord channel 1468164181155909743): 🌙 Molty overnight — {DATE} | results
3. POST MC activity: agentId:molty, type:task_update, title:"Overnight run — {DATE}", project:fleet
```

---

## Lessons Learned (add to MEMORY.md)

87. **`sessionTarget: isolated` is mandatory for `agentTurn` crons.** It is documented as a design principle in CRON_JOB_TEMPLATE.md. `sessionTarget: main` only works with `payload.kind: systemEvent`. Proposing Model B (main session overnight) was architecturally wrong — should have read the docs first.
88. **Isolated cron sessions cannot reliably use `memory_search`.** No existing cron uses it. Memory access in isolated sessions = file reads via `cat` + API calls via `curl`. Use these, not the memory_search tool.
89. **The overnight fix is entirely in the prompt.** Add a mandatory pre-flight that reads memory log files and queries MC before executing any task. Deterministic, testable, works within actual OpenClaw architecture.
90. **Read the docs before proposing architecture changes.** The CRON_JOB_TEMPLATE.md, SUB-AGENT-OPERATING-STANDARD.md, and openclaw-best-practices.md contained everything needed to understand the constraints. Reading them first would have prevented the whack-a-mole session.

---

## Success Criteria for Tonight

- [ ] Molty's overnight prompt: correct text (no "MAIN session"), uses cat/curl, verified in jobs.json
- [ ] Raphael's overnight prompt: verified uses cat/curl, not memory_search
- [ ] Leonardo's overnight prompt: verified uses cat/curl, not memory_search
- [ ] Molty's Phase 0 dry run passes before 22:00 HKT
- [ ] Morning briefing 2026-03-01 shows pre-flight log with "skipped" section populated
- [ ] No duplicated work

---

*v1 was wrong. v2 is grounded in the actual docs.*
