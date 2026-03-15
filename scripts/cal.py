#!/usr/bin/env python3
"""
cal.py — Calendar CLI using service account (REG-005 compliant)

Usage:
  cal.py agenda [--tomorrow|--today|--week|--days N] [--calendar CAL]
  cal.py create --summary "Title" --start "ISO8601" --end "ISO8601" [--calendar personal|brinc|shenanigans] [--description "..."] [--private]
  cal.py freebusy --start "ISO8601" --end "ISO8601"

Automatically applies:
  - REG-005: Uses service account only (no expiring OAuth)
  - REG-006: Creates Brinc busy block for non-Brinc events
  - REG-007: Checks all 3 calendars via freebusy before booking
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build

SA_FILE = "/data/workspace/credentials/google-service-account.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDARS = {
    'personal': 'guillermo.ginesta@gmail.com',
    'brinc': 'guillermo.ginesta@brinc.io',
    'shenanigans': 'vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com',
}

# Noise filters (lesson 143): skip these in briefings
NOISE_PATTERNS = [
    'mayleen', 'maylene', 'mie',  # helpers
    'focus time', 'busy [private]', 'busy block',  # focus/busy blocks
    'school drop', 'school pick',  # school logistics
]

HKT = timezone(timedelta(hours=8))

def is_noise(summary: str) -> bool:
    """Check if event should be filtered from briefings."""
    if not summary:
        return False
    s = summary.lower()
    return any(pattern in s for pattern in NOISE_PATTERNS)

def get_service():
    creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def cal_id(name):
    return CALENDARS.get(name, name)

def agenda(args):
    service = get_service()
    now = datetime.now(HKT)
    
    if args.today:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif args.tomorrow:
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif args.week:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    else:
        days = args.days or 1
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=days)
    
    cals = [args.calendar] if args.calendar else ['personal', 'brinc']
    
    for cal_name in cals:
        cid = cal_id(cal_name)
        print(f"\n📅 {cal_name.upper()} ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})")
        print("-" * 50)
        
        try:
            events = service.events().list(
                calendarId=cid,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            items = events.get('items', [])
            # Filter noise (lesson 143)
            items = [e for e in items if not is_noise(e.get('summary', ''))]
            if not items:
                print("  (no events)")
            for e in items:
                s = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
                time_str = s[11:16] if 'T' in s else 'All day'
                print(f"  {time_str}: {e.get('summary', 'No title')}")
        except Exception as ex:
            print(f"  Error: {ex}")

def freebusy(args):
    service = get_service()
    
    body = {
        "timeMin": args.start,
        "timeMax": args.end,
        "items": [{"id": cal_id(c)} for c in ['personal', 'brinc', 'shenanigans']]
    }
    
    result = service.freebusy().query(body=body).execute()
    
    print(f"\n🔍 Free/Busy ({args.start} to {args.end})")
    print("-" * 50)
    
    has_conflict = False
    for cal_name, cid in CALENDARS.items():
        busy = result.get('calendars', {}).get(cid, {}).get('busy', [])
        if busy:
            has_conflict = True
            print(f"  ⚠️  {cal_name}: {len(busy)} busy slot(s)")
            for b in busy:
                print(f"      {b['start']} - {b['end']}")
        else:
            print(f"  ✅ {cal_name}: free")
    
    return not has_conflict

def create(args):
    service = get_service()
    target_cal = args.calendar or 'personal'
    cid = cal_id(target_cal)
    
    # REG-007: Check conflicts first
    print("Checking for conflicts (REG-007)...")
    if not freebusy_check(service, args.start, args.end):
        print("\n⚠️  Conflict detected! Proceeding anyway (you may want to reschedule)")
    else:
        print("✅ No conflicts found")
    
    # Create event
    event = {
        'summary': args.summary,
        'start': {'dateTime': args.start, 'timeZone': 'Asia/Hong_Kong'},
        'end': {'dateTime': args.end, 'timeZone': 'Asia/Hong_Kong'},
    }
    
    if args.description:
        event['description'] = args.description
    
    if args.private:
        event['visibility'] = 'private'
    
    print(f"\nCreating event on {target_cal}...")
    result = service.events().insert(calendarId=cid, body=event).execute()
    print(f"✅ Created: {result.get('summary')} ({result.get('start', {}).get('dateTime')})")
    print(f"   Link: {result.get('htmlLink')}")
    
    # REG-006: Create Brinc busy block for non-Brinc events
    if target_cal != 'brinc':
        print("\nAdding Brinc busy block (REG-006)...")
        busy_event = {
            'summary': 'Busy [private]',
            'start': {'dateTime': args.start, 'timeZone': 'Asia/Hong_Kong'},
            'end': {'dateTime': args.end, 'timeZone': 'Asia/Hong_Kong'},
            'visibility': 'private',
            'transparency': 'opaque'
        }
        service.events().insert(calendarId=cal_id('brinc'), body=busy_event).execute()
        print("✅ Brinc busy block added")

def freebusy_check(service, start, end):
    body = {
        "timeMin": start,
        "timeMax": end,
        "items": [{"id": cal_id(c)} for c in ['personal', 'brinc', 'shenanigans']]
    }
    result = service.freebusy().query(body=body).execute()
    
    for cid in CALENDARS.values():
        busy = result.get('calendars', {}).get(cid, {}).get('busy', [])
        if busy:
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Calendar CLI (service account)')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # agenda
    agenda_p = subparsers.add_parser('agenda', help='Show upcoming events')
    agenda_p.add_argument('--today', action='store_true')
    agenda_p.add_argument('--tomorrow', action='store_true')
    agenda_p.add_argument('--week', action='store_true')
    agenda_p.add_argument('--days', type=int)
    agenda_p.add_argument('--calendar', choices=['personal', 'brinc', 'shenanigans'])
    
    # freebusy
    fb_p = subparsers.add_parser('freebusy', help='Check free/busy')
    fb_p.add_argument('--start', required=True)
    fb_p.add_argument('--end', required=True)
    
    # create
    create_p = subparsers.add_parser('create', help='Create event')
    create_p.add_argument('--summary', required=True)
    create_p.add_argument('--start', required=True)
    create_p.add_argument('--end', required=True)
    create_p.add_argument('--calendar', choices=['personal', 'brinc', 'shenanigans'])
    create_p.add_argument('--description')
    create_p.add_argument('--private', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'agenda':
        agenda(args)
    elif args.command == 'freebusy':
        freebusy(args)
    elif args.command == 'create':
        create(args)

if __name__ == '__main__':
    main()
