#!/usr/bin/env python3
"""
Standup Calendar Section Generator
Produces structured output for the Notion daily standup.
Shows schedule, free slots, and task scheduling suggestions.

Usage: python3 standup-calendar.py [days_ahead]
"""

import json, sys, os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from collections import defaultdict

DAYS_AHEAD = int(sys.argv[1]) if len(sys.argv) > 1 else 5
HKT = timezone(timedelta(hours=8))
now = datetime.now(HKT)

# Load config & tokens
TOKEN_FILE = "/data/workspace/credentials/calendar-tokens-brinc.json"
CONFIG_FILE = "/data/workspace/credentials/calendar-config.json"
OAUTH_FILE = "/data/workspace/credentials/google-oauth.json"
TODOIST_ENV = "/data/workspace/credentials/todoist.env"

with open(TOKEN_FILE) as f:
    tokens = json.load(f)
with open(CONFIG_FILE) as f:
    config = json.load(f)
with open(OAUTH_FILE) as f:
    oauth = json.load(f)

access_token = tokens['access_token']

# Read todoist token
todoist_token = ""
with open(TODOIST_ENV) as f:
    for line in f:
        if line.startswith('TODOIST_API_TOKEN='):
            todoist_token = line.strip().split('=', 1)[1]

# Refresh calendar token if needed
def refresh_token():
    global access_token
    installed = oauth.get('installed', oauth)
    data = (
        f"client_id={installed['client_id']}"
        f"&client_secret={installed['client_secret']}"
        f"&refresh_token={tokens['refresh_token']}"
        f"&grant_type=refresh_token"
    ).encode()
    req = Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    resp = json.loads(urlopen(req, timeout=10).read())
    if 'access_token' in resp:
        access_token = resp['access_token']
        tokens['access_token'] = access_token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        return True
    return False

def api_get(url, retry=True):
    try:
        req = Request(url, headers={'Authorization': f'Bearer {access_token}'})
        return json.loads(urlopen(req, timeout=10).read())
    except HTTPError as e:
        if e.code == 401 and retry:
            refresh_token()
            return api_get(url, retry=False)
        return {'items': []}

def get_events(cal_id, start, end):
    encoded = quote(cal_id, safe='')
    url = (f'https://www.googleapis.com/calendar/v3/calendars/{encoded}/events'
           f'?timeMin={start}&timeMax={end}&singleEvents=true&orderBy=startTime&maxResults=100')
    data = api_get(url)
    return data.get('items', [])

def get_todoist_tasks():
    try:
        req = Request('https://api.todoist.com/rest/v2/tasks',
                      headers={'Authorization': f'Bearer {todoist_token}'})
        return json.loads(urlopen(req, timeout=10).read())
    except:
        return []

def parse_hkt(dt_str):
    """Parse ISO datetime string to HKT datetime"""
    if not dt_str or 'T' not in dt_str:
        return None
    try:
        if dt_str.endswith('Z'):
            dt = datetime.strptime(dt_str[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        elif '+' in dt_str[10:] or dt_str[10:].count('-') > 0:
            # Has timezone offset
            base = dt_str[:19]
            sign = '+' if '+' in dt_str[19:] else '-'
            offset_str = dt_str.split(sign, 1)[-1] if sign == '+' else dt_str[19:].split('-', 1)[-1]
            offset_str = offset_str.replace(':', '')
            hours = int(offset_str[:2])
            mins = int(offset_str[2:4]) if len(offset_str) >= 4 else 0
            offset = timedelta(hours=hours, minutes=mins)
            if sign == '-':
                offset = -offset
            dt = datetime.strptime(base, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone(offset))
        else:
            dt = datetime.strptime(dt_str[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=HKT)
        return dt.astimezone(HKT)
    except:
        return None

# Collect events from all calendars
calendars = {
    'Brinc': 'guillermo.ginesta@brinc.io',
    'Personal': 'guillermo.ginesta@gmail.com',
    'Shenanigans': 'vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com'
}

start_str = now.strftime('%Y-%m-%dT00:00:00%%2B08:00')  # URL-encoded +08:00
end_dt = now + timedelta(days=DAYS_AHEAD)
end_str = end_dt.strftime('%Y-%m-%dT23:59:59%%2B08:00')

all_events = []
for cal_name, cal_id in calendars.items():
    events = get_events(cal_id, start_str, end_str)
    for ev in events:
        s_str = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', ''))
        e_str = ev.get('end', {}).get('dateTime', ev.get('end', {}).get('date', ''))
        s_dt = parse_hkt(s_str)
        e_dt = parse_hkt(e_str)
        is_allday = 'T' not in s_str
        
        all_events.append({
            'calendar': cal_name,
            'summary': ev.get('summary', '(no title)'),
            'start_str': s_str,
            'end_str': e_str,
            'start_dt': s_dt,
            'end_dt': e_dt,
            'start_hour': s_dt.hour + s_dt.minute / 60 if s_dt else None,
            'end_hour': e_dt.hour + e_dt.minute / 60 if e_dt else None,
            'all_day': is_allday,
            'day': s_str[:10]
        })

# Group by day
by_day = defaultdict(list)
for ev in all_events:
    if ev['day']:
        by_day[ev['day']].append(ev)

# Deduplicate events that appear on multiple calendars (same time + similar name)
def dedup_day(events):
    seen = set()
    result = []
    for ev in events:
        key = (ev.get('start_hour'), ev.get('end_hour'), ev['summary'][:20])
        if key not in seen:
            seen.add(key)
            result.append(ev)
    return result

def find_free_slots(day_events, work_start=9, work_end=18):
    busy = []
    for ev in day_events:
        if ev['all_day']:
            continue
        s = ev.get('start_hour')
        e = ev.get('end_hour')
        if s is not None and e is not None:
            busy.append((s, e))
    
    busy.sort()
    merged = []
    for s, e in busy:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    
    free = []
    current = work_start
    for s, e in merged:
        if s > current + 0.25:  # At least 15 min gap
            free.append((current, s))
        current = max(current, e)
    if current < work_end - 0.25:
        free.append((current, work_end))
    
    return free

def energy_label(start_h, end_h):
    mid = (start_h + end_h) / 2
    if 9 <= mid < 12:
        return "⚡ deep work"
    elif 12 <= mid < 14:
        return "💡 light tasks"
    elif 14 <= mid < 17:
        return "🤝 meetings ok"
    elif 17 <= mid < 18:
        return "📋 standup/planning"
    return ""

def fmt_hour(h):
    return f"{int(h):02d}:{int((h % 1) * 60):02d}"

# Get schedulable tasks
tasks = get_todoist_tasks()
schedulable = []
p_map = {4: 'P1', 3: 'P2', 2: 'P3', 1: 'P4'}
for t in tasks:
    due = t.get('due')
    dur = t.get('duration')
    if not due:
        continue
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

# === OUTPUT ===
print("=" * 60)
print(f"📅 CALENDAR REVIEW — {now.strftime('%a %b %d')} to {end_dt.strftime('%a %b %d')}")
print("=" * 60)

total_free_week = 0

for i in range(DAYS_AHEAD + 1):
    day = now + timedelta(days=i)
    day_str = day.strftime('%Y-%m-%d')
    day_name = day.strftime('%a %b %d')
    day_events = dedup_day(by_day.get(day_str, []))
    
    weekday = day.weekday()
    is_weekend = weekday >= 5
    is_today = i == 0
    
    label = " (TODAY)" if is_today else " (Weekend)" if is_weekend else ""
    icon = "📍" if is_today else "🔴" if is_weekend else "📆"
    
    print(f"\n{icon} {day_name}{label}")
    print("-" * 40)
    
    if not day_events:
        if not is_weekend:
            print("  (clear day)")
    else:
        allday = [e for e in day_events if e['all_day']]
        timed = sorted([e for e in day_events if not e['all_day']], 
                       key=lambda x: x.get('start_hour', 0) or 0)
        
        for e in allday:
            print(f"  🔲 all-day   {e['summary']} [{e['calendar']}]")
        
        for e in timed:
            s = e['start_str'][11:16] if 'T' in e['start_str'] else '?'
            end = e['end_str'][11:16] if 'T' in (e['end_str'] or '') else '?'
            cal_tag = f"[{e['calendar']}]"
            print(f"  {s}-{end}  {e['summary']:40s} {cal_tag}")
    
    if not is_weekend:
        free = find_free_slots(day_events)
        if free:
            print(f"  ┄┄┄ Free slots ┄┄┄")
            day_free = 0
            for s, e in free:
                hrs = e - s
                day_free += hrs
                el = energy_label(s, e)
                print(f"  🟢 {fmt_hour(s)}-{fmt_hour(e)} ({hrs:.1f}h) {el}")
            total_free_week += day_free
            print(f"  📊 Day total: {day_free:.1f}h free")

# Task scheduling suggestions
if schedulable:
    print(f"\n{'=' * 60}")
    print("🎯 P1/P2 TASKS NEEDING TIME BLOCKS")
    print("=" * 60)
    for t in sorted(schedulable, key=lambda x: (x['priority'], x['due_date'])):
        if t['duration_mins'] < 60:
            dur_str = f"{t['duration_mins']}m"
        elif t['duration_mins'] % 60:
            dur_str = f"{t['duration_mins']//60}h{t['duration_mins']%60}m"
        else:
            dur_str = f"{t['duration_mins']//60}h"
        print(f"  {t['priority']} | {t['content'][:50]:50s} | {dur_str:>5s} | due {t['due_date']}")
    
    print(f"\n  💡 Suggestion: Schedule P1 tasks in morning deep-work slots (9-12).")
    print(f"     Total free this week: {total_free_week:.1f}h")
    total_task_time = sum(t['duration_mins'] for t in schedulable) / 60
    print(f"     Total task time needed: {total_task_time:.1f}h")
    if total_task_time <= total_free_week:
        print(f"     ✅ Enough free time to fit all P1/P2 tasks")
    else:
        print(f"     ⚠️ Not enough free time — need to prioritize or delegate")

print(f"\n{'=' * 60}")
