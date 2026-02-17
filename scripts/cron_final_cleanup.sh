#!/bin/bash

echo "🔍 OpenClaw Cron Job Final Cleanup Audit"
echo "----------------------------------------"

# List all cron jobs
echo "🕰️ Current Cron Jobs:"
jq -r '.jobs[] | "ID: \(.id)\nName: \(.name)\nSession Target: \(.sessionTarget)\nPayload Kind: \(.payload.kind)\nModel: \(.payload.model)\nDelivery: \(.delivery.mode) to \(.delivery.channel // "N/A")\n---"' /data/.openclaw/cron/jobs.json

# Validation Checks
TOTAL_JOBS=$(jq '.jobs | length' /data/.openclaw/cron/jobs.json)
ISOLATED_JOBS=$(jq '[.jobs[] | select(.sessionTarget == "isolated")] | length' /data/.openclaw/cron/jobs.json)
AGENT_TURN_JOBS=$(jq '[.jobs[] | select(.payload.kind == "agentTurn")] | length' /data/.openclaw/cron/jobs.json)

echo -e "\n📊 Cron Job Statistics:"
echo "Total Jobs: $TOTAL_JOBS"
echo "Jobs in Isolated Session: $ISOLATED_JOBS"
echo "Jobs with AgentTurn Payload: $AGENT_TURN_JOBS"

# Check for any remaining system events
SYSTEM_EVENT_JOBS=$(jq '[.jobs[] | select(.payload.kind == "systemEvent")] | length' /data/.openclaw/cron/jobs.json)
if [ "$SYSTEM_EVENT_JOBS" -gt 0 ]; then
    echo "⚠️ WARNING: $SYSTEM_EVENT_JOBS jobs still use systemEvent payload!"
fi

# Verify model paths
INVALID_MODELS=$(jq '[.jobs[] | select(.payload.model | test("^[^/]+/[^/]+$"))] | length' /data/.openclaw/cron/jobs.json)
if [ "$INVALID_MODELS" -gt 0 ]; then
    echo "⚠️ WARNING: $INVALID_MODELS jobs have incomplete model paths!"
fi