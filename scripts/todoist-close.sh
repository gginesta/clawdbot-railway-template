#!/bin/bash
# todoist-close.sh — THE ONLY WAY to close a Todoist task
# REG-036: Personal project tasks without 🦎 are Guillermo's — NEVER close them
#
# Usage: todoist-close.sh <task_id> [reason]
# 
# This script MUST be used for ALL Todoist task closures.
# Direct API calls to /tasks/{id}/close are FORBIDDEN.

set -euo pipefail

TODOIST_TOKEN="9a26743814658c9e82d92aa716b46a9b0a2257c4"
PERSONAL_PROJECT_ID="6M5rpGfw5jR9Qg9R"
TASK_ID="${1:?Usage: todoist-close.sh <task_id> [reason]}"
REASON="${2:-no reason given}"

# Fetch the task
TASK_JSON=$(curl -s "https://api.todoist.com/api/v1/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${TODOIST_TOKEN}")

PROJECT_ID=$(echo "$TASK_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('project_id',''))")
CONTENT=$(echo "$TASK_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('content',''))")

# REG-036 GUARD: Personal project without 🦎 = Guillermo's task
if [ "$PROJECT_ID" = "$PERSONAL_PROJECT_ID" ]; then
  if echo "$CONTENT" | grep -q "🦎"; then
    echo "✅ Personal task WITH 🦎 marker — OK to close: ${CONTENT}"
  else
    echo "🚫 BLOCKED: Personal task WITHOUT 🦎 — this is Guillermo's task!"
    echo "   Task: ${CONTENT}"
    echo "   ID: ${TASK_ID}"
    echo "   DO NOT CLOSE. If you think this is wrong, ask Guillermo."
    exit 1
  fi
fi

# Close the task
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "https://api.todoist.com/api/v1/tasks/${TASK_ID}/close" \
  -H "Authorization: Bearer ${TODOIST_TOKEN}")

if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Closed: ${CONTENT} (reason: ${REASON})"
else
  echo "⚠️ Failed to close (HTTP ${HTTP_CODE}): ${CONTENT}"
  exit 1
fi
