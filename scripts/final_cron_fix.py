#!/usr/bin/env python3
import json

with open('/data/.openclaw/cron/jobs.json', 'r') as f:
    config = json.load(f)

for job in config['jobs']:
    if job['id'] == 'bdb28765-f508-4271-a04d-9408d39f49fd':
        job['payload']['model'] = 'openrouter/google/gemini-2.5-flash'
        break

with open('/data/.openclaw/cron/jobs.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Daily Standup job model updated successfully.")