#!/data/workspace/.venv/bin/python3
"""
flush-task-close-notifications.py — PLAN-017b companion

Reads /data/workspace/logs/task-close-notify-YYYY-MM-DD.jsonl
Outputs Discord messages to be posted by calling agent.

Usage: python3 flush-task-close-notifications.py [--date YYYY-MM-DD]

Output: JSON list of {channel, message} dicts to stdout
The calling agent (or cron agentTurn) posts these to Discord.
"""

import json, os, sys
from datetime import datetime, timedelta, timezone

HKT = timezone(timedelta(hours=8))
TODAY = datetime.now(HKT).strftime("%Y-%m-%d")

date_arg = None
for i, arg in enumerate(sys.argv):
    if arg == "--date" and i + 1 < len(sys.argv):
        date_arg = sys.argv[i + 1]

target_date = date_arg or TODAY
notify_file = f"/data/workspace/logs/task-close-notify-{target_date}.jsonl"
archive_file = f"/data/workspace/logs/task-close-notify-{target_date}.jsonl.sent"

if not os.path.exists(notify_file):
    print(json.dumps([]))
    sys.exit(0)

messages = []
with open(notify_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            messages.append({
                "channel": entry.get("channel", "1468164181155909743"),
                "message": entry.get("discord_msg", f"✅ Task closed: {entry.get('title', '?')}"),
            })
        except json.JSONDecodeError:
            pass

# Mark as sent by renaming
if messages:
    os.rename(notify_file, archive_file)

print(json.dumps(messages))
