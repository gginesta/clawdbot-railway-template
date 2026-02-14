#!/bin/bash
# Tailscale Auth Key Generator via OAuth API
# Usage: tailscale-rotate-key.sh [tag] (default: Molty)
set -euo pipefail

TAG="${1:-Molty}"
CREDS="/data/workspace/credentials/tailscale-oauth.json"
CLIENT_ID=$(python3 -c "import json; print(json.load(open('$CREDS'))['client_id'])")
CLIENT_SECRET=$(python3 -c "import json; print(json.load(open('$CREDS'))['client_secret'])")

# Get access token
ACCESS_TOKEN=$(curl -s -X POST "https://api.tailscale.com/api/v2/oauth/token" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# Generate reusable auth key (90 day expiry)
RESULT=$(curl -s -X POST "https://api.tailscale.com/api/v2/tailnet/-/keys" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"capabilities\": {
      \"devices\": {
        \"create\": {
          \"reusable\": true,
          \"ephemeral\": false,
          \"preauthorized\": true,
          \"tags\": [\"tag:${TAG}\"]
        }
      }
    },
    \"expirySeconds\": 7776000
  }")

KEY=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('key',''))")

if [ -z "$KEY" ]; then
  echo "ERROR: $(echo $RESULT | python3 -c 'import json,sys; print(json.load(sys.stdin))')" >&2
  exit 1
fi

echo "$KEY"
