#!/bin/bash
# mc-todoist-sync-v2.sh — Bidirectional Todoist ↔ Mission Control sync
#
# Block 1: Todoist → MC   (new tasks from synced projects)
# Block 2: MC → Todoist   (Guillermo-assigned MC tasks missing todoistId)
# Block 3: Completion sync (bidirectional)
#
# Usage: bash mc-todoist-sync-v2.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ── Config ─────────────────────────────────────────────────────────────────
export MC_API="https://resilient-chinchilla-241.convex.site"
export MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
export TODOIST_TOKEN="9a26743814658c9e82d92aa716b46a9b0a2257c4"
export DRY_RUN
export SYNC_DATE
SYNC_DATE=$(date +%Y-%m-%d)
export LOG_FILE="/data/workspace/logs/sync-${SYNC_DATE}.log"

# Todoist synced projects → MC project names
export BRINC_PROJECT_ID="6M5rpGgV6q865hrX"
export MANA_PROJECT_ID="6Rr9p6MxWHFwHXGC"

# MC project → Todoist project (for reverse sync)
export TODOIST_BRINC="6M5rpGgV6q865hrX"
export TODOIST_MANA="6Rr9p6MxWHFwHXGC"
export TODOIST_PERSONAL="6M5rpGfw5jR9Qg9R"

WORK_DIR=$(mktemp -d)
export WORK_DIR
trap "rm -rf $WORK_DIR" EXIT

mkdir -p /data/workspace/logs

log() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

export -f log

log "=== mc-todoist-sync-v2 START$([ "$DRY_RUN" = true ] && echo ' [DRY RUN]' || echo '') ==="

# ── Fetch data ─────────────────────────────────────────────────────────────
log "Fetching Todoist active tasks..."
curl -s "https://api.todoist.com/api/v1/tasks" \
    -H "Authorization: Bearer $TODOIST_TOKEN" \
    > "$WORK_DIR/todoist_tasks.json"

TODOIST_COUNT=$(python3 -c "
import json, sys
with open('$WORK_DIR/todoist_tasks.json') as f:
    data = json.load(f)
tasks = data.get('results', data) if isinstance(data, dict) else data
print(len(tasks))
")
log "  → $TODOIST_COUNT active Todoist tasks"

log "Fetching MC tasks..."
curl -s "$MC_API/api/tasks" \
    -H "Authorization: Bearer $MC_KEY" \
    > "$WORK_DIR/mc_tasks.json"

MC_COUNT=$(python3 -c "
import json
with open('$WORK_DIR/mc_tasks.json') as f:
    data = json.load(f)
tasks = data if isinstance(data, list) else data.get('tasks', [])
print(len(tasks))
")
log "  → $MC_COUNT MC tasks"


# ── Block 1: Todoist → MC ─────────────────────────────────────────────────
log ""
log "--- Block 1: Todoist → MC (new tasks from synced projects) ---"

python3 - <<PYEOF
import json, os, urllib.request, urllib.error

WORK_DIR    = os.environ['WORK_DIR']
MC_API      = os.environ['MC_API']
MC_KEY      = os.environ['MC_KEY']
TODOIST_TOKEN = os.environ['TODOIST_TOKEN']
DRY_RUN     = os.environ['DRY_RUN'] == 'true'
LOG_FILE    = os.environ['LOG_FILE']

SYNCED = {
    os.environ['BRINC_PROJECT_ID']: 'brinc',
    os.environ['MANA_PROJECT_ID']:  'mana',
}
PRIORITY_MAP = {4: 'p0', 3: 'p1', 2: 'p2', 1: 'p3'}

def log(msg):
    import datetime
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}]   {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f: f.write(line + '\n')

def mc_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{MC_API}{path}", data=data,
        headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

with open(f'{WORK_DIR}/todoist_tasks.json') as f:
    td_data = json.load(f)
with open(f'{WORK_DIR}/mc_tasks.json') as f:
    mc_data = json.load(f)

todoist_tasks = td_data.get('results', td_data) if isinstance(td_data, dict) else td_data
mc_tasks = mc_data if isinstance(mc_data, list) else mc_data.get('tasks', [])

existing_todoist_ids = {t['todoistId'] for t in mc_tasks if t.get('todoistId')}
log(f"MC tasks already linked to Todoist: {len(existing_todoist_ids)}")

created = 0
for t in todoist_tasks:
    project_id = t.get('project_id', '')
    labels     = t.get('labels', [])
    tid        = t['id']

    in_synced   = project_id in SYNCED
    has_mc      = 'mc' in labels
    has_personal = 'personal' in labels

    if not (in_synced or has_mc): continue
    if has_personal:              continue
    if tid in existing_todoist_ids: continue

    mc_project = SYNCED.get(project_id, 'brinc')
    priority   = PRIORITY_MAP.get(t.get('priority', 1), 'p2')
    due        = t.get('due', {}) or {}
    due_date   = due.get('date') if isinstance(due, dict) else None

    body = {
        "title":     t.get('content', '(untitled)'),
        "project":   mc_project,
        "priority":  priority,
        "assignees": ["guillermo"],
        "createdBy": "molty-sync",
        "status":    "assigned",
        "todoistId": tid,
    }
    if t.get('description'): body["description"] = t['description']
    if due_date:             body["dueDate"]      = due_date
    if labels:               body["tags"]          = labels

    log(f"[CREATE] {t['content'][:70]}")
    log(f"         → {mc_project} / {priority} / due={due_date}")
    if not DRY_RUN:
        try:
            result = mc_post('/api/task', body)
            log(f"         ✓ MC id={result.get('id','?')}")
        except Exception as e:
            log(f"         ✗ Error: {e}")
    created += 1

log(f"Block 1 done: {created} tasks created in MC")
with open(f'{WORK_DIR}/b1.txt', 'w') as f: f.write(str(created))
PYEOF

B1=$(cat "$WORK_DIR/b1.txt" 2>/dev/null || echo 0)


# ── Block 2: MC → Todoist ─────────────────────────────────────────────────
log ""
log "--- Block 2: MC → Todoist (Guillermo tasks missing todoistId) ---"

python3 - <<PYEOF
import json, os, urllib.request, urllib.error

WORK_DIR      = os.environ['WORK_DIR']
MC_API        = os.environ['MC_API']
MC_KEY        = os.environ['MC_KEY']
TODOIST_TOKEN = os.environ['TODOIST_TOKEN']
DRY_RUN       = os.environ['DRY_RUN'] == 'true'
LOG_FILE      = os.environ['LOG_FILE']

MC_TO_TODOIST = {
    'brinc':    os.environ['TODOIST_BRINC'],
    'mana':     os.environ['TODOIST_MANA'],
    'personal': os.environ['TODOIST_PERSONAL'],
}
P_MAP = {'p0': 4, 'p1': 3, 'p2': 2, 'p3': 1}

def log(msg):
    import datetime
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}]   {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f: f.write(line + '\n')

def mc_patch(body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{MC_API}/api/task", data=data,
        headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"},
        method="PATCH")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def todoist_create(title, project_id, priority, description='', due_date=None):
    body = {"content": title, "project_id": project_id, "priority": priority}
    if description: body["description"] = description
    if due_date:    body["due_date"]    = due_date
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        "https://api.todoist.com/api/v1/tasks", data=data,
        headers={"Authorization": f"Bearer {TODOIST_TOKEN}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

with open(f'{WORK_DIR}/mc_tasks.json') as f:
    mc_data = json.load(f)
mc_tasks = mc_data if isinstance(mc_data, list) else mc_data.get('tasks', [])

candidates = [
    t for t in mc_tasks
    if 'guillermo' in t.get('assignees', [])
    and t.get('status') not in ('done', 'blocked')
    and not t.get('todoistId')
    and t.get('project') in MC_TO_TODOIST
]
log(f"MC tasks for Guillermo without Todoist link: {len(candidates)}")

synced = 0
for t in candidates:
    td_project = MC_TO_TODOIST[t['project']]
    td_priority = P_MAP.get(t.get('priority', 'p2'), 2)

    log(f"[REVERSE] {t['title'][:70]}")
    log(f"          → Todoist {t['project']} / priority {td_priority}")
    if not DRY_RUN:
        try:
            td = todoist_create(
                title       = t['title'],
                project_id  = td_project,
                priority    = td_priority,
                description = t.get('description', ''),
                due_date    = t.get('dueDate'),
            )
            mc_patch({"id": t['_id'], "todoistId": td['id']})
            log(f"          ✓ Todoist id={td['id']} linked to MC {t['_id']}")
        except Exception as e:
            log(f"          ✗ Error: {e}")
    synced += 1

log(f"Block 2 done: {synced} tasks pushed to Todoist")
with open(f'{WORK_DIR}/b2.txt', 'w') as f: f.write(str(synced))
PYEOF

B2=$(cat "$WORK_DIR/b2.txt" 2>/dev/null || echo 0)


# ── Block 3: Completion sync ───────────────────────────────────────────────
log ""
log "--- Block 3: Completion sync (bidirectional) ---"

# Re-fetch MC tasks (Block 2 may have added todoistIds)
curl -s "$MC_API/api/tasks" \
    -H "Authorization: Bearer $MC_KEY" \
    > "$WORK_DIR/mc_tasks_fresh.json"

python3 - <<PYEOF
import json, os, urllib.request, urllib.error

WORK_DIR      = os.environ['WORK_DIR']
MC_API        = os.environ['MC_API']
MC_KEY        = os.environ['MC_KEY']
TODOIST_TOKEN = os.environ['TODOIST_TOKEN']
DRY_RUN       = os.environ['DRY_RUN'] == 'true'
LOG_FILE      = os.environ['LOG_FILE']

def log(msg):
    import datetime
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}]   {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f: f.write(line + '\n')

def mc_patch(body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{MC_API}/api/task", data=data,
        headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"},
        method="PATCH")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def todoist_close(task_id):
    req = urllib.request.Request(
        f"https://api.todoist.com/api/v1/tasks/{task_id}/close",
        data=b'',
        headers={"Authorization": f"Bearer {TODOIST_TOKEN}"},
        method="POST")
    urllib.request.urlopen(req)

with open(f'{WORK_DIR}/todoist_tasks.json') as f:
    td_data = json.load(f)
with open(f'{WORK_DIR}/mc_tasks_fresh.json') as f:
    mc_data = json.load(f)

todoist_tasks = td_data.get('results', td_data) if isinstance(td_data, dict) else td_data
mc_tasks      = mc_data if isinstance(mc_data, list) else mc_data.get('tasks', [])

active_td_ids = {t['id'] for t in todoist_tasks}

mc_linked_open = [t for t in mc_tasks if t.get('todoistId') and t.get('status') != 'done']
mc_linked_done = [t for t in mc_tasks if t.get('todoistId') and t.get('status') == 'done']

log(f"Open MC tasks with todoistId: {len(mc_linked_open)}")
log(f"Done MC tasks with todoistId: {len(mc_linked_done)}")

closed_mc = 0
closed_td = 0

# Todoist completed → close in MC
for t in mc_linked_open:
    if t['todoistId'] not in active_td_ids:
        log(f"[CLOSE MC] {t['title'][:65]}")
        log(f"           Todoist {t['todoistId']} not in active list → marking done")
        if not DRY_RUN:
            try:
                mc_patch({"id": t['_id'], "status": "done"})
                log(f"           ✓ MC task closed")
            except Exception as e:
                log(f"           ✗ Error: {e}")
        closed_mc += 1

# MC done → close in Todoist
for t in mc_linked_done:
    if t['todoistId'] in active_td_ids:
        log(f"[CLOSE TD] {t['title'][:65]}")
        log(f"           MC done but Todoist {t['todoistId']} still active → closing")
        if not DRY_RUN:
            try:
                todoist_close(t['todoistId'])
                log(f"           ✓ Todoist task closed")
            except Exception as e:
                log(f"           ✗ Error: {e}")
        closed_td += 1

log(f"Block 3 done: closed {closed_mc} in MC, closed {closed_td} in Todoist")
with open(f'{WORK_DIR}/b3.txt', 'w') as f: f.write(f"{closed_mc},{closed_td}")
PYEOF

B3=$(cat "$WORK_DIR/b3.txt" 2>/dev/null || echo "0,0")
B3_MC=$(echo "$B3" | cut -d',' -f1)
B3_TD=$(echo "$B3" | cut -d',' -f2)


# ── Summary ───────────────────────────────────────────────────────────────
log ""
log "=== SYNC COMPLETE$([ "$DRY_RUN" = true ] && echo ' [DRY RUN]' || echo '') ==="
log "  Block 1 (Todoist→MC):  $B1 tasks created in MC"
log "  Block 2 (MC→Todoist):  $B2 tasks pushed to Todoist"
log "  Block 3 (completion):  $B3_MC closed in MC, $B3_TD closed in Todoist"
log "  Log: $LOG_FILE"
