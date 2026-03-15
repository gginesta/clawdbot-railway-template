# HEARTBEAT.md

# MC heartbeat ping is handled by cron job (46d1ca32-...) every 2h.
# On each heartbeat, also check MC for tasks assigned to Molty and action any pending ones.
# Do not let tasks sit in inbox/assigned — process or escalate immediately.

## Heartbeat Checklist
1. Run usage report: `bash /data/workspace/scripts/mc-usage-report.sh molty 2>/dev/null || true`
2. Update agent-link health: `python3 /data/shared/scripts/agent-link-worker.py update-health molty up`
3. Check `GET /api/tasks?assignee=molty&status=inbox` and `GET /api/tasks?assignee=molty&status=assigned` — action any inbox/assigned tasks before replying HEARTBEAT_OK
4. If Cerebro tasks pending review: pull PR diff, review, sign off in #launchpad-cerebro + update MC status
5. If blocked tasks: post in #command-center with specific ask

## CRITICAL: Response Rules (REG-034)
- If checklist is clean → respond with ONLY: `HEARTBEAT_OK`
- NO status cards, NO briefings, NO calendar, NO embellishments
- Do NOT fabricate data you didn't query
- Adding anything after HEARTBEAT_OK = regression failure
