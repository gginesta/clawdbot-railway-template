# HEARTBEAT.md

# MC heartbeat ping is handled by cron job (46d1ca32-...) every 2h.
# On each heartbeat, also check MC for tasks assigned to Molty and action any pending ones.
# Do not let tasks sit in inbox/assigned — process or escalate immediately.

## Heartbeat Checklist
1. Run usage report: `bash /data/workspace/scripts/mc-usage-report.sh molty 2>/dev/null || true`
2. Check `GET /api/tasks?assignee=molty&status=inbox` and `GET /api/tasks?assignee=molty&status=assigned` — action any inbox/assigned tasks before replying HEARTBEAT_OK
3. If Cerebro tasks pending review: pull PR diff, review, sign off in #launchpad-cerebro + update MC status
4. If blocked tasks: post in #command-center with specific ask
