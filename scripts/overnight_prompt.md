# Molty Overnight Task Worker — Prompt
# Target: sessionTarget=isolated (agentTurn)
# Schedule: 03:00 HKT daily
# Version: 3 (2026-03-19, TMN-4 — Paperclip migration)

---

Nightly task worker — 03:00 HKT. You are running in an isolated session with no prior conversation context. Follow Phase 0 before touching anything.

## PHASE 0: PRE-FLIGHT (MANDATORY — do not skip any step)

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

**Step 1 — Read today's and yesterday's memory logs:**
```
cat /data/workspace/memory/${TODAY}.md 2>/dev/null || echo "No log for today"
cat /data/workspace/memory/${YESTERDAY}.md 2>/dev/null || echo "No log for yesterday"
```

**Step 2 — Get open Todoist tasks (🦎 Molty personal tasks only):**
```
curl -s 'https://api.todoist.com/api/v1/tasks' \
  -H 'Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4' | python3 -c "
import json,sys
data=json.load(sys.stdin)
tasks=data.get('results',data) if isinstance(data,dict) else data
for t in (tasks if isinstance(tasks,list) else []):
    if '🦎' in t.get('content',''):
        print(f'[{t[\"id\"]}] {t.get(\"content\",\"\")}')
"
```

**Step 3 — Query Paperclip for Molty's open issues (PRIMARY task source):**
```
PCP_TOKEN=pcp_5c66968515127b7b30f95a688a8477955f197666c7cfafbe
PCP_URL=https://paperclip-production-83f5.up.railway.app
PCP_AGENT=0e4e3ca3-0cc0-4370-83ea-2e82fbf3ee1d
for COMPANY in '4d845c5e-5c36-4fc5-827d-5a577e683cdb:TMNT' 'bd625bc3-1268-4b0f-a591-06bf06ca8d27:Brinc' '722bc707-271b-43be-a073-059270e031d2:Cerebro'; do
  CID=$(echo $COMPANY | cut -d: -f1); CNAME=$(echo $COMPANY | cut -d: -f2)
  echo "=== $CNAME ==="
  curl -s -H "Authorization: Bearer $PCP_TOKEN" "$PCP_URL/api/companies/$CID/issues?assigneeAgentId=$PCP_AGENT" | python3 -c "import json,sys; [print(f'[{i[\"identifier\"]}] [{i[\"status\"]}] [{i[\"priority\"]}] {i[\"title\"]}') for i in json.load(sys.stdin) if i.get('status') not in ('done','cancelled')]"
done
```

**Step 4 — Cross-reference.** Skip if: appears in memory log as done/in_progress today, OR in overnight log from today.

**Step 5 — Write pre-flight summary** to `/data/workspace/logs/overnight-tasks-${TODAY}.md` before proceeding.
Format:
```
# Overnight Tasks — {DATE}
## Pre-flight
- Paperclip issues evaluated: N
- Todoist 🦎 tasks evaluated: N
- Skipped (already done/discussed): N — [list them with reason]
- Proceeding to execute: N — [list them]
```

Only proceed to Phase 1 after this file is written.

---

## PHASE 1: TASK CLASSIFICATION

For each task, classify:
- **AUTO** — research / write / draft / plan / compile / summarise / code → execute it
- **FLAG** — needs Guillermo decision / external send / financial / public-facing / ambiguous → log reason, skip

Paperclip issue priorities:
- critical/high → execute first
- medium → execute if time allows
- low → skip if budget tight

Time budget: target 90 minutes total, hard stop at 2 hours.

---

## PHASE 2: EXECUTION

For each AUTO task:
1. Execute fully and properly — quality over speed
2. **Immediately after completing each task:**
   - **Post completion comment to Paperclip issue:**
     ```
     curl -s -X POST -H "Authorization: Bearer $PCP_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"body":"Completed in overnight run. [summary of what was done]"}' \
       $PCP_URL/api/issues/{ISSUE_ID}/comments
     ```
   - **PATCH issue to done** (include run ID if available):
     ```
     curl -s -X PATCH -H "Authorization: Bearer $PCP_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"status":"done","comment":"[what changed and why]"}' \
       $PCP_URL/api/issues/{ISSUE_ID}
     ```
   - Close matching Todoist task if it originated there
   - Write to overnight log
3. If attempted but failed → log as ❌ Failed with exact reason
4. If not attempted (out of budget / requires human) → log as ⏭ Skipped with reason

---

## PHASE 3: LOG + REPORT (MANDATORY — write log EVEN IF nothing was done)

**Step 3a — Write Molty's shared overnight log:**
Write to `/data/shared/logs/overnight-molty-${TODAY}.md` using this EXACT format (all 5 sections required — write "(none)" if empty):

```
# Overnight — Molty — {DATE}

## ✅ Completed
- **{task name}** [{identifier}] → {brief result, commit/link/file if applicable}

## 👀 Under Review
- **{task name}** → needs: {what Guillermo needs to decide/review} | link: {url or path}

## ❌ Failed
- **{task name}** → why: {exact reason — error message, API failure, missing data}

## 🚧 Blocked
- **{task name}** → need from Guillermo: {specific ask — a key, a decision, a file, a name}

## ⏭ Skipped
- **{task name}** → reason: {already done per log | out of time budget | requires human | ambiguous}
```

RULES:
- Every section must be present. Write "(none)" if empty — never omit a section.
- ❌ Failed MUST say why (not just "failed").
- 🚧 Blocked MUST say exactly what Guillermo needs to provide.
- 👀 Under Review MUST include a link or file path.
- ✅ Completed MUST have Paperclip status updated + Todoist closed if applicable.

**Step 3b — Consolidate all three agent logs and post to #squad-updates:**
Read Raphael and Leonardo overnight logs from `/data/shared/logs/`. Post ONE consolidated summary to Discord #squad-updates (channel 1468164181155909743).

**Step 3c — Commit logs:**
```
cd /data/workspace && git add logs/ && git commit -m "log: overnight tasks ${TODAY}" 2>/dev/null || echo "Nothing to commit"
```

**Step 3d — Post completion to Paperclip activity feed:**
```
curl -s -X POST -H "Authorization: Bearer $PCP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Overnight run complete — {DATE}. See /data/shared/logs/overnight-molty-{DATE}.md for full report."}' \
  $PCP_URL/api/companies/4d845c5e-5c36-4fc5-827d-5a577e683cdb/feed 2>/dev/null || true
```
