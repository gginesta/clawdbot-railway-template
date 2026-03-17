#!/bin/bash
# mc-close-task.sh — THE ONLY WAY to close an MC task (PLAN-017b)
# Notifies #squad-updates BEFORE marking done. No silent closes.
#
# Usage: mc-close-task.sh <task_id> <task_title> [result_summary]
#
# Examples:
#   mc-close-task.sh jn7abc123 "Write TMNT article" "Draft at /data/workspace/docs/tmnt-article.md"
#   mc-close-task.sh jn7abc123 "Fix WhatsApp bug" "PR merged, deployed to Railway"

set -euo pipefail

MC_API="https://resilient-chinchilla-241.convex.site"
MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"

# Discord: #squad-updates
SQUAD_UPDATES_CHANNEL="1468164181155909743"
DISCORD_BOT_CHANNEL_SEND_ENDPOINT="https://discord.com/api/v10/channels/${SQUAD_UPDATES_CHANNEL}/messages"

# Args
TASK_ID="${1:?Usage: mc-close-task.sh <task_id> <task_title> [result_summary]}"
TASK_TITLE="${2:?Usage: mc-close-task.sh <task_id> <task_title> [result_summary]}"
RESULT_SUMMARY="${3:-completed}"

TODAY=$(date +%Y-%m-%d)
LOG_FILE="/data/workspace/logs/task-close-${TODAY}.log"
mkdir -p /data/workspace/logs

log() {
    local msg="[$(date '+%H:%M:%S')] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# ── Step 1: Fetch task to verify it exists and get details ────────────────────
log "Fetching MC task ${TASK_ID}..."
TASK_JSON=$(curl -s "${MC_API}/api/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${MC_KEY}" 2>/dev/null || echo "{}")

ACTUAL_TITLE=$(echo "$TASK_JSON" | python3 -c "import sys,json; t=json.load(sys.stdin); print(t.get('title','(not found)'))" 2>/dev/null || echo "$TASK_TITLE")
ASSIGNEES=$(echo "$TASK_JSON" | python3 -c "import sys,json; t=json.load(sys.stdin); print(', '.join(t.get('assignees',[])) or 'unknown')" 2>/dev/null || echo "unknown")
PROJECT=$(echo "$TASK_JSON" | python3 -c "import sys,json; t=json.load(sys.stdin); print(t.get('project',''))" 2>/dev/null || echo "")
CURRENT_STATUS=$(echo "$TASK_JSON" | python3 -c "import sys,json; t=json.load(sys.stdin); print(t.get('status','unknown'))" 2>/dev/null || echo "unknown")

log "Task: ${ACTUAL_TITLE} | status=${CURRENT_STATUS} | assignees=${ASSIGNEES}"

# Guard: don't double-close
if [ "$CURRENT_STATUS" = "done" ]; then
    log "⚠️ Task is already done — skipping"
    exit 0
fi

# ── Step 2: Write Discord notification message ────────────────────────────────
PROJECT_TAG=""
[ -n "$PROJECT" ] && PROJECT_TAG=" | #${PROJECT}"

DISCORD_MSG="✅ **Task Closed**: ${ACTUAL_TITLE}
→ ${RESULT_SUMMARY}
_Assignee: ${ASSIGNEES}${PROJECT_TAG}_"

log "Discord message prepared: ${DISCORD_MSG:0:100}..."

# Write to file (main agent can read and post, or cron agentTurn reads this)
NOTIFY_FILE="/data/workspace/logs/task-close-notify-${TODAY}.jsonl"
python3 -c "
import json, sys
entry = {
    'task_id': '$TASK_ID',
    'title': '''$ACTUAL_TITLE''',
    'result': '''$RESULT_SUMMARY''',
    'assignees': '$ASSIGNEES',
    'project': '$PROJECT',
    'discord_msg': '''$DISCORD_MSG''',
    'channel': '$SQUAD_UPDATES_CHANNEL',
}
print(json.dumps(entry))
" >> "$NOTIFY_FILE"
log "Notification queued to ${NOTIFY_FILE}"

# ── Step 3: Mark done in MC ───────────────────────────────────────────────────
log "Marking task done in MC..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X PATCH "${MC_API}/api/task" \
  -H "Authorization: Bearer ${MC_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"taskId\": \"${TASK_ID}\", \"status\": \"done\"}")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
    log "✅ MC task closed: ${ACTUAL_TITLE}"
else
    log "⚠️ MC PATCH returned HTTP ${HTTP_CODE} — task may not be closed"
    exit 1
fi

# ── Step 4: Attempt direct Discord post via gateway API ──────────────────────
# OpenClaw gateway exposes a local API for Discord actions
GATEWAY_URL="http://localhost:3000"
GATEWAY_TOKEN=$(cat /data/workspace/credentials/openclaw-gateway-token.txt 2>/dev/null || echo "")

if [ -n "$GATEWAY_TOKEN" ]; then
    log "Posting to Discord via gateway..."
    DISCORD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "${GATEWAY_URL}/api/message/send" \
        -H "Authorization: Bearer ${GATEWAY_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"channel\": \"${SQUAD_UPDATES_CHANNEL}\", \"message\": \"${DISCORD_MSG//\"/\\\"}\"}" 2>/dev/null || echo "000")
    log "Gateway Discord post: HTTP ${DISCORD_RESPONSE}"
else
    log "No gateway token — notification queued for next agent session to deliver"
fi

log "=== mc-close-task COMPLETE: ${ACTUAL_TITLE} ==="
