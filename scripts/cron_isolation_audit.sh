#!/bin/bash

# Cron Job Isolation Audit
# Checks session target, delivery mechanism, and potential risks

AUDIT_LOG="/data/workspace/logs/cron_isolation_audit.log"
mkdir -p "$(dirname "$AUDIT_LOG")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$AUDIT_LOG"
}

log "🕵️ Starting Cron Job Isolation Audit"

# Capture all cron jobs
log "\n📋 Listing Cron Jobs:"
jq -r '.jobs[] | "ID: \(.id)\nName: \(.name)\nSession Target: \(.sessionTarget)\nPayload Kind: \(.payload.kind)\nDelivery Mode: \(.delivery.mode // "NO DELIVERY")\nDelivery Channel: \(.delivery.channel // "NO CHANNEL")\nDelivery Target: \(.delivery.to // "NO TARGET")\n---"' /data/.openclaw/cron/jobs.json

# Analyze Session Targets
log "\n🔍 Session Target Analysis:"
MAIN_SESSION_JOBS=$(jq -r '.jobs[] | select(.sessionTarget == "main") | .id' /data/.openclaw/cron/jobs.json)
ISOLATED_JOBS=$(jq -r '.jobs[] | select(.sessionTarget == "isolated") | .id' /data/.openclaw/cron/jobs.json)

log "Jobs in Main Session (RISK):"
for job in $MAIN_SESSION_JOBS; do
    log "- $job"
done

log "\nJobs in Isolated Session:"
for job in $ISOLATED_JOBS; do
    log "- $job"
done

# Check Delivery Mechanisms
log "\n📤 Delivery Mechanism Check:"
NO_DELIVERY_JOBS=$(jq -r '.jobs[] | select(.delivery.mode | not) | .id' /data/.openclaw/cron/jobs.json)
log "Jobs with No Explicit Delivery:"
for job in $NO_DELIVERY_JOBS; do
    log "- $job"
done

# Payload Risk Assessment
log "\n⚠️ Payload Risk Assessment:"
RISKY_PAYLOADS=$(jq -r '.jobs[] | select(.payload.kind == "systemEvent" and .sessionTarget == "main") | .id' /data/.openclaw/cron/jobs.json)
log "Potentially Risky Payloads (systemEvent in main session):"
for job in $RISKY_PAYLOADS; do
    log "- $job"
done

# Final Summary
log "\n🏁 Audit Summary"
log "Total Jobs: $(jq '.jobs | length' /data/.openclaw/cron/jobs.json)"
log "Jobs in Main Session: $(echo "$MAIN_SESSION_JOBS" | wc -l)"
log "Jobs in Isolated Session: $(echo "$ISOLATED_JOBS" | wc -l)"
log "Jobs with No Delivery: $(echo "$NO_DELIVERY_JOBS" | wc -l)"
log "Jobs with Risky Payloads: $(echo "$RISKY_PAYLOADS" | wc -l)"