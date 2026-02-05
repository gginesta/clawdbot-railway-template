#!/bin/bash
# Standup Calendar Section Generator
# Produces JSON data for the Notion standup calendar review
# Usage: standup-calendar.sh [days_ahead]
#
# Output: structured text showing schedule + free slots + task scheduling suggestions

DAYS_AHEAD="${1:-5}"
TOKEN_FILE="/data/workspace/credentials/calendar-tokens-brinc.json"
CONFIG_FILE="/data/workspace/credentials/calendar-config.json"
TODOIST_ENV="/data/workspace/credentials/todoist.env"

# Load tokens
ACCESS_TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_FILE'))['access_token'])")
TODOIST_TOKEN=$(grep TODOIST_API_TOKEN "$TODOIST_ENV" | cut -d= -f2)

# Refresh if needed
refresh_cal_token() {
    OAUTH_FILE="/data/workspace/credentials/google-oauth.json"
    REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_FILE'))['refresh_token'])")
    CLIENT_ID=$(grep -o '"client_id": "[^"]*"' "$OAUTH_FILE" | head -1 | cut -d'"' -f4)
    CLIENT_SECRET=$(grep -o '"client_secret": "[^"]*"' "$OAUTH_FILE" | head -1 | cut -d'"' -f4)
    
    RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
        -d "client_id=$CLIENT_ID" \
        -d "client_secret=$CLIENT_SECRET" \
        -d "refresh_token=$REFRESH_TOKEN" \
        -d "grant_type=refresh_token")
    
    NEW_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
    if [ -n "$NEW_TOKEN" ]; then
        python3 -c "
import json
d = json.load(open('$TOKEN_FILE'))
d['access_token'] = '$NEW_TOKEN'
json.dump(d, open('$TOKEN_FILE','w'), indent=2)
"
        ACCESS_TOKEN="$NEW_TOKEN"
    fi
}

python3 << 'PYEOF'
import json, sys, os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError

DAYS_AHEAD = int(os.environ.get('DAYS_AHEAD', '5'))

# Load config
with open(os.environ.get('CONFIG_FILE', '/data/workspace/credentials/calendar-config.json')) as f:
    config = json.load(f)

access_token = os.environ.get('ACCESS_TOKEN', '')
todoist_token = os.environ.get('TODOIST_TOKEN', '')

HKT = timezone(timedelta(hours=8))
now = datetime.now(HKT)

# Energy schedule
energy = {
    'deep_work': (9, 12),
    'light': (12, 14),
    'meetings': (14, 17),
    'standup': (17, 18)
}

# Life commitments
commitments = config.get('life_commitments', {})

def api_get(url):
    try:
        req = Request(url, headers={'Authorization': f'Bearer {access_token}'})
        return json.loads(urlopen(req, timeout=10).read())
    except HTTPError as e:
        if e.code == 401:
            # Would need refresh — skip for now
            return {'items': []}
        return {'items': []}

def get_events(cal_id, start, end):
    encoded = quote(cal_id, safe='')
    url = (f'https://www.googleapis.com/calendar/v3/calendars/{encoded}/events'
           f'?timeMin={start}&timeMax={end}&singleEvents=true&orderBy=startTime&maxResults=50')
    data = api_get(url)
    return data.get('items', [])

def get_todoist_tasks():
    try:
        req = Request('https://api.todoist.com/rest/v2/tasks',
                      headers={'Authorization': f'Bearer {todoist_token}'})
        return json.loads(urlopen(req, timeout=10).read())
    except:
        return []

def parse_dt(ev):
    start = ev.get('start', {})
    end_d = ev.get('end', {})
    s = start.get('dateTime', start.get('date', ''))
    e = end_d.get('dateTime', end_d.get('date', ''))
    return s, e

def to_hkt_hour(dt_str):
    """Extract hour in HKT from ISO datetime string"""
    if 'T' not in dt_str:
        return None
    try:
        # Parse with timezone
        dt_str_clean = dt_str.replace('+08:00', '+0800').replace('+00:00', '+0000')
        if '+' in dt_str_clean[10:]:
            base = dt_str_clean[:19]
            tz_part = dt_str_clean[19:].replace(':', '')
            dt = datetime.strptime(base + tz_part, '%Y-%m-%dT%H:%M:%S%z')
        elif dt_str_clean.endswith('Z'):
            dt = datetime.strptime(dt_str_clean, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        else:
            dt = datetime.strptime(dt_str_clean[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=HKT)
        hkt = dt.astimezone(HKT)
        return hkt.hour + hkt.minute / 60
    except:
        return None

# Collect all events across calendars
calendars = {
    'Brinc': 'guillermo.ginesta@brinc.io',
    'Personal': 'guillermo.ginesta@gmail.com',
    'Shenanigans': 'vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com'
}

start_str = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
end_dt = now + timedelta(days=DAYS_AHEAD)
end_str = end_dt.strftime('%Y-%m-%dT23:59:59+08:00')

all_events = []
for cal_name, cal_id in calendars.items():
    events = get_events(cal_id, start_str, end_str)
    for ev in events:
        s, e = parse_dt(ev)
        all_events.append({
            'calendar': cal_name,
            'summary': ev.get('summary', '(no title)'),
            'start': s,
            'end': e,
            'start_hour': to_hkt_hour(s),
            'end_hour': to_hkt_hour(e),
            'all_day': 'T' not in s if s else True
        })

# Get tasks with due dates and time estimates
tasks = get_todoist_tasks()
schedulable = []
for t in tasks:
    due = t.get('due')
    dur = t.get('duration')
    if not due:
        continue
    # Priority mapping (Todoist inverted)
    p_map = {4: 'P1', 3: 'P2', 2: 'P3', 1: 'P4'}
    priority = p_map.get(t['priority'], 'P4')
    
    due_date = due.get('date', '')[:10]
    dur_mins = dur.get('amount', 60) if dur else None
    
    if priority in ('P1', 'P2') and dur_mins:
        schedulable.append({
            'content': t['content'],
            'priority': priority,
            'due_date': due_date,
            'duration_mins': dur_mins,
            'project_id': t.get('project_id', ''),
            'task_id': t['id']
        })

# Group events by day
from collections import defaultdict
by_day = defaultdict(list)
for ev in all_events:
    day = ev['start'][:10] if ev['start'] else ''
    if day:
        by_day[day].append(ev)

# Find free slots per day
def find_free_slots(day_events, work_start=9, work_end=18):
    """Find free time slots in work hours"""
    busy = []
    for ev in day_events:
        if ev['all_day']:
            continue
        s = ev.get('start_hour')
        e = ev.get('end_hour')
        if s is not None and e is not None:
            busy.append((s, e))
    
    busy.sort()
    # Merge overlapping
    merged = []
    for s, e in busy:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    
    free = []
    current = work_start
    for s, e in merged:
        if s > current:
            free.append((current, s))
        current = max(current, e)
    if current < work_end:
        free.append((current, work_end))
    
    return free

# Output
print("=" * 60)
print("📅 CALENDAR REVIEW — Rest of Week")
print("=" * 60)

for i in range(DAYS_AHEAD + 1):
    day = now + timedelta(days=i)
    day_str = day.strftime('%Y-%m-%d')
    day_name = day.strftime('%a %b %d')
    day_events = by_day.get(day_str, [])
    
    # Skip if no events and it's a weekend
    weekday = day.weekday()
    is_weekend = weekday >= 5
    
    print(f"\n{'🔴' if is_weekend else '📆'} {day_name} {'(Weekend)' if is_weekend else ''}")
    print("-" * 40)
    
    if not day_events:
        print("  (no events)")
    else:
        # Sort by start time
        timed = [e for e in day_events if not e['all_day']]
        allday = [e for e in day_events if e['all_day']]
        
        for e in allday:
            print(f"  all-day   {e['summary']} [{e['calendar']}]")
        
        timed.sort(key=lambda x: x.get('start_hour', 0) or 0)
        for e in timed:
            s = e['start'][11:16] if 'T' in e['start'] else '?'
            end = e['end'][11:16] if 'T' in (e['end'] or '') else '?'
            print(f"  {s}-{end}  {e['summary']} [{e['calendar']}]")
    
    if not is_weekend:
        free = find_free_slots(day_events)
        if free:
            print(f"  --- Free slots ---")
            total_free = 0
            for s, e in free:
                hrs = e - s
                total_free += hrs
                sh = int(s)
                sm = int((s % 1) * 60)
                eh = int(e)
                em = int((e % 1) * 60)
                # Energy label
                energy_label = ""
                mid = (s + e) / 2
                if 9 <= mid < 12:
                    energy_label = "⚡ deep work"
                elif 12 <= mid < 14:
                    energy_label = "💡 light tasks"
                elif 14 <= mid < 17:
                    energy_label = "🤝 meetings ok"
                print(f"  🟢 {sh:02d}:{sm:02d}-{eh:02d}:{em:02d} ({hrs:.1f}h free) {energy_label}")
            print(f"  Total free: {total_free:.1f}h")

# Task scheduling suggestions
if schedulable:
    print(f"\n{'=' * 60}")
    print("🎯 TASKS NEEDING TIME BLOCKS")
    print("=" * 60)
    for t in sorted(schedulable, key=lambda x: x['priority']):
        dur_str = f"{t['duration_mins']}m" if t['duration_mins'] < 60 else f"{t['duration_mins']//60}h{t['duration_mins']%60:02d}m" if t['duration_mins'] % 60 else f"{t['duration_mins']//60}h"
        print(f"  {t['priority']} | {t['content'][:50]:50s} | {dur_str:>5s} | due {t['due_date']}")

print(f"\n{'=' * 60}")
PYEOF
