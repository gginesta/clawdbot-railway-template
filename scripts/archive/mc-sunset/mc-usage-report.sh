#!/bin/bash
# MC Usage Report — reports token usage + OpenRouter credits to Mission Control
# Called from heartbeat cron or standalone
set -euo pipefail

MC_API="https://resilient-chinchilla-241.convex.site"
MC_KEY="232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
OR_KEY="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"
AGENT_ID="${1:-molty}"
TODAY=$(date -u +%Y-%m-%d)

# 1. OpenRouter credits check
OR_CREDITS=$(curl -s "https://openrouter.ai/api/v1/credits" \
  -H "Authorization: Bearer $OR_KEY" 2>/dev/null || echo '{}')

OR_USED=$(echo "$OR_CREDITS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('total_usage',0))" 2>/dev/null || echo "0")
OR_LIMIT=$(echo "$OR_CREDITS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('total_credits',0))" 2>/dev/null || echo "0")

# Report OpenRouter usage as a cost entry
if [ "$OR_USED" != "0" ]; then
  curl -s -X POST "$MC_API/api/cost" \
    -H "Authorization: Bearer $MC_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"agentId\": \"fleet\",
      \"date\": \"$TODAY\",
      \"model\": \"openrouter/credits\",
      \"inputTokens\": 0,
      \"outputTokens\": 0,
      \"estimatedCost\": $OR_USED,
      \"sessionCount\": 1
    }" > /dev/null 2>&1
fi

# 2. Report Anthropic token volume (from openclaw status if available)
# Parse openclaw status for token counts
OC_STATUS=$(openclaw status 2>/dev/null || echo "")
if [ -n "$OC_STATUS" ]; then
  TOKENS_IN=$(echo "$OC_STATUS" | grep -oP 'Tokens:\s*\K[\d,]+(?=\s*in)' | tr -d ',' || echo "0")
  TOKENS_OUT=$(echo "$OC_STATUS" | grep -oP '[\d,]+(?=\s*out)' | tr -d ',' || echo "0")
  
  if [ "$TOKENS_IN" != "0" ] || [ "$TOKENS_OUT" != "0" ]; then
    curl -s -X POST "$MC_API/api/cost" \
      -H "Authorization: Bearer $MC_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"agentId\": \"$AGENT_ID\",
        \"date\": \"$TODAY\",
        \"model\": \"anthropic/claude-sonnet-4-6\",
        \"inputTokens\": ${TOKENS_IN:-0},
        \"outputTokens\": ${TOKENS_OUT:-0},
        \"estimatedCost\": 0,
        \"sessionCount\": 1
      }" > /dev/null 2>&1
  fi
fi

echo "Usage report sent: OR=$OR_USED, tokens=${TOKENS_IN:-0}/${TOKENS_OUT:-0}"
