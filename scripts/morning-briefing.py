#!/usr/bin/env python3
"""
Morning briefing script - outputs exact format, no LLM interpretation needed.
Run: python3 /data/workspace/scripts/morning-briefing.py
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta

# Config
MC_API = "https://resilient-chinchilla-241.convex.site"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
SA_FILE = "/data/workspace/credentials/google-service-account.json"
CALENDARS = [
    "guillermo.ginesta@gmail.com",
    "guillermo.ginesta@brinc.io",
    "vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com"
]
# Skip these in calendar
NOISE_WORDS = ["busy", "focus", "mayleen", "mie", "helper", "school drop", "school pick"]


def get_weather():
    """Get weather from wttr.in"""
    try:
        result = subprocess.run(
            ["curl", "-s", "wttr.in/Hong+Kong?format=%c+%t"],
            capture_output=True, text=True, timeout=10
        )
        weather = result.stdout.strip()
        # Convert F to C if needed
        if "°F" in weather:
            parts = weather.split()
            for i, p in enumerate(parts):
                if "°F" in p:
                    try:
                        f = int(p.replace("°F", "").replace("+", ""))
                        c = round((f - 32) * 5 / 9)
                        parts[i] = f"{c}°C"
                    except:
                        pass
            weather = " ".join(parts)
        return weather if weather else "Weather unavailable"
    except Exception as e:
        return f"Weather error: {e}"


def get_calendar():
    """Get today's calendar events using SA token"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        creds = service_account.Credentials.from_service_account_file(
            SA_FILE, 
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        service = build('calendar', 'v3', credentials=creds)
        
        now = datetime.utcnow()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        events = []
        for cal_id in CALENDARS:
            try:
                result = service.events().list(
                    calendarId=cal_id,
                    timeMin=start.isoformat() + 'Z',
                    timeMax=end.isoformat() + 'Z',
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                for e in result.get('items', []):
                    summary = e.get('summary', 'No title')
                    # Skip noise
                    if any(x in summary.lower() for x in NOISE_WORDS):
                        continue
                    
                    start_raw = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
                    if 'T' in start_raw:
                        time_str = start_raw[11:16]
                    else:
                        time_str = "all-day"
                    
                    events.append((start_raw, time_str, summary))
            except Exception as ex:
                pass  # Skip calendars we can't access
        
        # Sort by start time
        events.sort(key=lambda x: x[0])
        
        # Dedupe by summary (keep first occurrence)
        seen = set()
        unique = []
        for start_raw, time_str, summary in events:
            if summary not in seen:
                seen.add(summary)
                unique.append((time_str, summary))
        
        return unique[:6]  # Max 6 events
    except Exception as e:
        return [("error", str(e))]


def get_mc_tasks(status):
    """Get MC tasks by status"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: Bearer {MC_KEY}",
             f"{MC_API}/api/tasks?status={status}"],
            capture_output=True, text=True, timeout=15
        )
        return json.loads(result.stdout) if result.stdout else []
    except Exception as e:
        return []


def format_task(task):
    """Format a single task for display"""
    title = task.get('title', 'No title')
    assignees = task.get('assignees', [])
    priority = task.get('priority', 'p3').upper()
    
    # Agent emoji
    agent_map = {'molty': '🦎', 'raphael': '🔴', 'leonardo': '🔵', 'april': '🌸', 'guillermo': '😊'}
    agent = assignees[0] if assignees else 'unknown'
    emoji = agent_map.get(agent, '👤')
    
    # Truncate title if too long
    if len(title) > 50:
        title = title[:47] + "..."
    
    return f"{emoji} [{priority}] {title}"


def main():
    # Date header
    now = datetime.now()
    date_str = now.strftime("%a %d %b")
    
    # Weather
    weather = get_weather()
    
    print(f"**{date_str}** · {weather}")
    print()
    
    # Calendar
    events = get_calendar()
    if events and events[0][0] != "error":
        print("**📅 Today**")
        for time_str, summary in events:
            print(f"• {time_str} {summary}")
        print()
    
    # Blocked tasks
    blocked = get_mc_tasks("blocked")
    if blocked:
        print("**🚧 Blocked**")
        for task in blocked[:4]:
            print(f"• {format_task(task)}")
        print()
    
    # Review tasks
    review = get_mc_tasks("review")
    if review:
        print("**👀 Review**")
        for task in review[:4]:
            print(f"• {format_task(task)}")
        print()
    
    # Inbox (unprocessed)
    inbox = get_mc_tasks("inbox")
    if inbox:
        print(f"**📥 Inbox** ({len(inbox)} unprocessed)")
        for task in inbox[:3]:
            print(f"• {format_task(task)}")


if __name__ == "__main__":
    main()
