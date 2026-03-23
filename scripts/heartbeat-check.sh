#!/bin/bash
# Heartbeat check script - outputs HEARTBEAT_OK or alerts
# Run: bash /data/workspace/scripts/heartbeat-check.sh

set -e

PCP_URL="https://paperclip-production-83f5.up.railway.app"
PCP_TOKEN="pcp_5c66968515127b7b30f95a688a8477955f197666c7cfafbe"
PCP_AGENT="0e4e3ca3-0cc0-4370-83ea-2e82fbf3ee1d"
TMNT_CID="4d845c5e-5c36-4fc5-827d-5a577e683cdb"
ALERTS=""

# 1. Update agent-link health
python3 /data/shared/scripts/agent-link-worker.py update-health molty up 2>/dev/null || true

# 2. Check April health
APRIL_HEALTH=$(curl -s --max-time 10 https://april-agent-production.up.railway.app/setup/healthz 2>/dev/null || echo '{"ok":false}')
if [[ "$APRIL_HEALTH" != '{"ok":true}' ]]; then
    ALERTS="${ALERTS}⚠️ April health check failed: $APRIL_HEALTH\n"
fi

# 3. Check for blocked Paperclip issues (TMNT)
BLOCKED=$(curl -s -H "Authorization: Bearer $PCP_TOKEN" "$PCP_URL/api/companies/$TMNT_CID/issues?status=blocked&assigneeAgentId=$PCP_AGENT" 2>/dev/null)
BLOCKED_COUNT=$(echo "$BLOCKED" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo "0")

if [[ "$BLOCKED_COUNT" -gt 0 ]]; then
    ALERTS="${ALERTS}🚧 $BLOCKED_COUNT blocked Paperclip issue(s) assigned to Molty\n"
fi

# Output
if [[ -z "$ALERTS" ]]; then
    echo "HEARTBEAT_OK"
else
    echo -e "$ALERTS"
fi
