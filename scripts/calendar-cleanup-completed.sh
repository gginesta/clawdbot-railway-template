#!/usr/bin/env bash
set -euo pipefail

# Delete calendar task blocks that correspond to Todoist tasks completed in the last N hours.
# Conservative: only deletes events whose summary contains bracket markers like [P1]/[P2] or starts with an emoji,
# and only when a fuzzy match to a completed Todoist task title is found.
#
# Usage:
#   calendar-cleanup-completed.sh [hours]
#
# Requires:
#   - /data/workspace/scripts/calendar.sh
#   - TODOIST_API_TOKEN in env (source /data/workspace/credentials/todoist.env)

HOURS="${1:-48}"

CAL_SH="/data/workspace/scripts/calendar.sh"

need_cmd() { command -v "$1" >/dev/null 2>&1; }

if [[ ! -x "$CAL_SH" ]]; then
  echo "Missing calendar.sh at $CAL_SH" >&2
  exit 1
fi

if [[ -z "${TODOIST_API_TOKEN:-}" ]]; then
  echo "TODOIST_API_TOKEN not set. Run: source /data/workspace/credentials/todoist.env" >&2
  exit 1
fi

NOW_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SINCE_UTC=$(date -u -d "-${HOURS} hours" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || python3 - <<PY
import datetime
print((datetime.datetime.utcnow()-datetime.timedelta(hours=int("$HOURS"))).strftime('%Y-%m-%dT%H:%M:%SZ'))
PY
)

# Pull completed tasks since SINCE_UTC
COMPLETED_JSON=$(curl -s https://api.todoist.com/sync/v9/completed/get_all \
  -H "Authorization: Bearer $TODOIST_API_TOKEN" \
  -d "since=$SINCE_UTC")

export COMPLETED_JSON
export HOURS

python3 - <<'PY'
import json, os, re, subprocess, sys

cal_sh = '/data/workspace/scripts/calendar.sh'
hours = int(os.environ.get('HOURS','48'))

completed = json.loads(os.environ['COMPLETED_JSON']).get('items', [])

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r'\[[^\]]*\]', ' ', s)  # remove [P1] etc
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

completed_norm = [(norm(it.get('content','')), it.get('content','')) for it in completed]
completed_set = {n for n,_ in completed_norm if n}

# calendars to scan
cals = ['guillermo.ginesta@gmail.com','guillermo.ginesta@brinc.io']

# get next 3 days events from each calendar
from datetime import datetime, timedelta

# We use calendar.sh events <cal> 3 and parse the output format:
# start → end | summary | eventId

events = []
for cal in cals:
    out = subprocess.check_output([cal_sh,'events',cal,'3'], text=True, stderr=subprocess.DEVNULL)
    for line in out.splitlines():
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue
        when = parts[0]
        summary = parts[1]
        event_id = parts[2]
        events.append((cal, summary, event_id, when))

# conservative selection: task blocks only
candidate = []
for cal, summary, event_id, when in events:
    s = summary.strip()
    if not s:
        continue
    if '[p' in s.lower() or re.match(r'^[^a-zA-Z0-9\s]', s):
        candidate.append((cal, s, event_id, when))

# match candidates to completed tasks

def match(summary: str) -> bool:
    ns = norm(summary)
    if not ns:
        return False
    # direct contains either way
    for ct in completed_set:
        if ct and (ct in ns or ns in ct):
            return True
    return False


to_delete = [(cal, summary, event_id, when) for (cal, summary, event_id, when) in candidate if match(summary)]

if not to_delete:
    print('No completed-task calendar blocks to delete.')
    sys.exit(0)

print('Deleting calendar blocks for completed tasks:')
for cal, summary, event_id, when in to_delete:
    print(f'- {summary} ({cal})')
    # delete
    subprocess.check_output([cal_sh,'delete',event_id,cal], text=True)

print(f'Deleted {len(to_delete)} event(s).')
PY