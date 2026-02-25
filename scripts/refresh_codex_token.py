#!/usr/bin/env python3
"""
Auto-refresh the OpenAI Codex OAuth token.
Safe to run any time — skips if token still has >2 days remaining.
"""
import json, urllib.request, urllib.parse, time, sys

AUTH_FILE = "/data/.openclaw/agents/main/agent/auth.json"
CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
TOKEN_URL = "https://auth.openai.com/oauth/token"
REFRESH_THRESHOLD_SECS = 2 * 24 * 3600  # refresh if <2 days remaining

def refresh():
    with open(AUTH_FILE) as f:
        auth = json.load(f)

    codex = auth.get("openai-codex", {})
    expires_ms = codex.get("expires", 0)
    refresh_token = codex.get("refresh", "")
    now_ms = time.time() * 1000

    remaining_secs = (expires_ms - now_ms) / 1000
    if remaining_secs > REFRESH_THRESHOLD_SECS:
        print(f"Token still valid for {remaining_secs/3600:.1f}h — skipping refresh.")
        return False

    if not refresh_token:
        print("ERROR: No refresh token found. Manual re-auth required.")
        sys.exit(1)

    print(f"Token expires in {remaining_secs/3600:.1f}h — refreshing...")

    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
    }).encode()

    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read())

    new_access = resp["access_token"]
    new_refresh = resp.get("refresh_token", refresh_token)
    expires_in = resp.get("expires_in", 864000)
    new_expiry_ms = int((time.time() + expires_in) * 1000)

    auth["openai-codex"] = {
        "type": "oauth",
        "access": new_access,
        "refresh": new_refresh,
        "expires": new_expiry_ms
    }

    with open(AUTH_FILE, "w") as f:
        json.dump(auth, f, indent=2)

    print(f"✅ Codex OAuth token refreshed. Valid for {expires_in//3600}h (until {time.strftime('%Y-%m-%d', time.localtime(time.time() + expires_in))})")
    return True

if __name__ == "__main__":
    refresh()
