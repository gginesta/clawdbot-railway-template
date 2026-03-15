#!/bin/bash
# Heartbeat check script - outputs HEARTBEAT_OK or alerts
# Run: bash /data/workspace/scripts/heartbeat-check.sh

set -e

MC_API="https://resilient-chinchilla-241.convex.site"
MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
ALERTS=""

# 1. Usage report (silent, just run it)
bash /data/workspace/scripts/mc-usage-report.sh molty 2>/dev/null || true

# 2. Update agent-link health
python3 /data/shared/scripts/agent-link-worker.py update-health molty up 2>/dev/null || true

# 3. Check April health
APRIL_HEALTH=$(curl -s --max-time 10 https://april-agent-production.up.railway.app/setup/healthz 2>/dev/null || echo '{"ok":false}')
if [[ "$APRIL_HEALTH" != '{"ok":true}' ]]; then
    ALERTS="${ALERTS}⚠️ April health check failed: $APRIL_HEALTH\n"
fi

# 4. Check for inbox tasks (should be processed)
INBOX=$(curl -s -H "Authorization: Bearer $MC_KEY" "$MC_API/api/tasks?assignee=molty&status=inbox" 2>/dev/null)
INBOX_COUNT=$(echo "$INBOX" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo "0")

if [[ "$INBOX_COUNT" -gt 0 ]]; then
    ALERTS="${ALERTS}📥 $INBOX_COUNT inbox task(s) need triage\n"
fi

# 5. Check for urgent assigned tasks (P0/P1 due today)
# Skip for now - could add date filtering

# Output
if [[ -z "$ALERTS" ]]; then
    echo "HEARTBEAT_OK"
else
    echo -e "$ALERTS"
fi
