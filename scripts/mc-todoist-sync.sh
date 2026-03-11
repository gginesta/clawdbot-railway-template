#!/bin/bash
# Todoist → Mission Control sync (read-only)
set -euo pipefail

MC_API="https://resilient-chinchilla-241.convex.site"
MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
TODOIST_TOKEN="9a26743814658c9e82d92aa716b46a9b0a2257c4"

echo "[1/2] Fetching Todoist tasks and projects..."

# Fetch, transform, and post to MC in one operation
RESULT=$(python3 << 'PYSCRIPT'
import json
import subprocess
import sys
import os

try:
    # Fetch tasks with curl directly
    task_response = subprocess.run(
        ['curl', '-s', '-w', '\n%{http_code}', 
         'https://api.todoist.com/api/v1/tasks',
         '-H', 'Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4'],
        capture_output=True, text=True, timeout=10
    )
    
    lines = task_response.stdout.strip().split('\n')
    http_code = lines[-1] if lines else '000'
    task_body = '\n'.join(lines[:-1]) if len(lines) > 1 else (lines[0] if lines else '')
    
    if http_code != '200':
        print(f"Todoist tasks API error (HTTP {http_code}): {task_body[:200]}", file=sys.stderr)
        sys.exit(1)
    
    tasks_data = json.loads(task_body)
    
    # Fetch projects
    proj_response = subprocess.run(
        ['curl', '-s', '-w', '\n%{http_code}',
         'https://api.todoist.com/api/v1/projects',
         '-H', 'Authorization: Bearer 9a26743814658c9e82d92aa716b46a9b0a2257c4'],
        capture_output=True, text=True, timeout=10
    )
    
    lines = proj_response.stdout.strip().split('\n')
    http_code = lines[-1] if lines else '000'
    proj_body = '\n'.join(lines[:-1]) if len(lines) > 1 else (lines[0] if lines else '')
    
    if http_code != '200':
        print(f"Todoist projects API error (HTTP {http_code}): {proj_body[:200]}", file=sys.stderr)
        sys.exit(1)
    
    projects_data = json.loads(proj_body)

    tasks = tasks_data.get('results', [])
    projects = projects_data.get('results', [])
    
    print(f"✓ Fetched {len(tasks)} tasks and {len(projects)} projects", file=sys.stderr)
    
    # Build project map
    proj_map = {p['id']: p['name'] for p in projects}

    # Transform to MC format
    mc_tasks = []
    for t in tasks[:50]:
        due = None
        if t.get('due') and isinstance(t['due'], dict):
            due = t['due'].get('date')

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

    # Post to MC
    mc_response = subprocess.run(
        ['curl', '-s', '-X', 'POST', 
         'https://resilient-chinchilla-241.convex.site/api/todoist-sync',
         '-H', 'Authorization: Bearer 232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({'tasks': mc_tasks})],
        capture_output=True, text=True, timeout=10
    )
    
    print(mc_response.stdout)
    sys.exit(0)
    
except Exception as e:
    import traceback
    print(f"Error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
PYSCRIPT
)

echo ""
echo "[2/2] Sync complete."

if echo "$RESULT" | python3 -m json.tool > /dev/null 2>&1; then
  SYNCED=$(echo "$RESULT" | python3 -c "import json, sys; r = json.load(sys.stdin); print(r.get('synced', r.get('count', 'unknown')))" 2>/dev/null || echo "?")
  echo "✓ Todoist → MC: $SYNCED tasks synced"
  echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')"
else
  echo "Response: $RESULT"
fi
