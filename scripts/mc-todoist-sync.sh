#!/bin/bash
# Todoist → Mission Control sync (read-only)
set -euo pipefail

MC_API="https://resilient-chinchilla-241.convex.site"
MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
TODOIST_TOKEN="9a26743814658c9e82d92aa716b46a9b0a2257c4"

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Fetch from Todoist API v1
echo "[1/3] Fetching tasks from Todoist..."
curl -s "https://api.todoist.com/api/v1/tasks" \
  -H "Authorization: Bearer $TODOIST_TOKEN" > "$TMPDIR/tasks.json"

echo "[2/3] Fetching projects from Todoist..."
curl -s "https://api.todoist.com/api/v1/projects" \
  -H "Authorization: Bearer $TODOIST_TOKEN" > "$TMPDIR/projects.json"

# Transform to MC format
echo "[3/3] Transforming and syncing to Mission Control..."
python3 << PYTHON_EOF
import json
import sys

try:
    with open('$TMPDIR/tasks.json') as f:
        data = json.load(f)
    with open('$TMPDIR/projects.json') as f:
        proj_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Error parsing Todoist API response: {e}", file=sys.stderr)
    sys.exit(1)
except FileNotFoundError as e:
    print(f"Error: Missing temp file: {e}", file=sys.stderr)
    sys.exit(1)

tasks = data.get('results', data) if isinstance(data, dict) else data
projects = proj_data.get('results', proj_data) if isinstance(proj_data, dict) else proj_data

proj_map = {p['id']: p['name'] for p in projects}

mc_tasks = []
for t in tasks[:50]:
    due = None
    if t.get('due') and isinstance(t['due'], dict):
        due = t['due'].get('date')
    elif t.get('deadline') and isinstance(t['deadline'], dict):
        due = t['deadline'].get('date')

    task_obj = {
        'todoistId': str(t['id']),
        'content': t.get('content', ''),
        'description': t.get('description', '') or '',
        'projectName': proj_map.get(t.get('project_id', ''), 'Inbox'),
        'priority': t.get('priority', 1),
        'isCompleted': t.get('is_completed', False) or t.get('checked', False),
        'labels': t.get('labels', []),
    }
    if due:
        task_obj['due'] = due
    mc_tasks.append(task_obj)

with open('$TMPDIR/payload.json', 'w') as f:
    json.dump({'tasks': mc_tasks}, f)

print(f'Prepared {len(mc_tasks)} tasks for sync')
PYTHON_EOF

# Push to MC
RESULT=$(curl -s -X POST "$MC_API/api/todoist-sync" \
  -H "Authorization: Bearer $MC_KEY" \
  -H "Content-Type: application/json" \
  -d @"$TMPDIR/payload.json")

# Parse and display result
echo ""
if echo "$RESULT" | python3 -m json.tool > /dev/null 2>&1; then
  SYNCED=$(echo "$RESULT" | python3 -c "import json, sys; r = json.load(sys.stdin); print(r.get('synced', r.get('count', '?')))")
  echo "✓ Todoist → MC sync complete: $SYNCED tasks synced"
  echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
else
  echo "Sync response: $RESULT"
fi
