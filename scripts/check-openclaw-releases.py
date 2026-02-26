#!/data/workspace/.venv/bin/python3
"""check-openclaw-releases.py

Daily cron (09:00 HKT): checks for new OpenClaw releases, triages release notes,
posts TMNT-relevant summary to #squad-updates, triggers fleet-update.py if safe to auto-apply.

State file: /data/workspace/state/openclaw-fleet-version.json
"""
from __future__ import annotations
import json, os, subprocess, sys, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
STATE_FILE = "/data/workspace/state/openclaw-fleet-version.json"
GITHUB_TOKEN = "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"
DISCORD_SQUAD_UPDATES = "1468164181155909743"
MC_API = "https://resilient-chinchilla-241.convex.site"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cba"

# Keywords that flag a release note as TMNT-relevant
RELEVANT_KEYWORDS = [
    "subagent", "sub-agent", "cron", "heartbeat", "webhook", "discord",
    "telegram", "memory", "session", "delivery", "routing", "config",
    "gateway", "agent", "tool", "skill", "railway", "redeploy",
]
BREAKING_KEYWORDS = ["breaking", "BREAKING", "Breaking"]

def _http(url: str, method="GET", data: bytes | None = None, headers: dict | None = None):
    h = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return 0, {"error": str(e)}

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"molty": {}, "raphael": {}, "leonardo": {}}

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_latest_tag() -> str | None:
    status, data = _http("https://api.github.com/repos/openclaw/openclaw/tags?per_page=5")
    if status == 200 and data:
        for tag in data:
            name = tag.get("name", "")
            if name.startswith("v") and "-beta" not in name:
                return name
    return None

def get_release_notes(tag: str) -> str:
    status, data = _http(f"https://api.github.com/repos/openclaw/openclaw/releases/tags/{tag}")
    if status == 200:
        return data.get("body", "")
    # Fallback: compare endpoint
    return ""

def triage_release(tag: str, notes: str) -> dict:
    """Parse release notes into breaking / relevant / summary buckets."""
    lines = notes.split("\n")
    breaking = []
    relevant = []
    in_breaking = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(k in line for k in BREAKING_KEYWORDS):
            in_breaking = True
        if in_breaking and line.startswith("-"):
            breaking.append(line.lstrip("- ").strip())
            continue
        if line.startswith("###") and "Breaking" not in line:
            in_breaking = False
        if line.startswith("-") and any(k.lower() in line.lower() for k in RELEVANT_KEYWORDS):
            relevant.append(line.lstrip("- ").strip()[:120])

    return {"tag": tag, "breaking": breaking, "relevant": relevant}

def post_discord(channel_id: str, message: str):
    """Post to Discord via the message tool (uses openclaw CLI)."""
    try:
        subprocess.run(
            ["openclaw", "send", "--channel", "discord", "--to", f"channel:{channel_id}", message],
            capture_output=True, timeout=15
        )
    except Exception as e:
        print(f"Discord post failed: {e}", file=sys.stderr)

def mc_activity(title: str, body: str):
    data = json.dumps({
        "agentId": "molty", "type": "deploy",
        "title": title, "body": body, "project": "fleet"
    }).encode()
    req = urllib.request.Request(
        f"{MC_API}/api/activity", data=data, method="POST",
        headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            pass
    except Exception:
        pass

def main():
    state = load_state()
    molty_current = state.get("molty", {}).get("current", "v0.0.0")

    latest = get_latest_tag()
    if not latest:
        print("Could not fetch latest tag")
        sys.exit(0)

    print(f"Latest: {latest} | Molty current: {molty_current}")

    if latest == molty_current:
        print("Already up to date — no action needed")
        sys.exit(0)

    # New release found
    notes = get_release_notes(latest)
    triage = triage_release(latest, notes)

    breaking_block = ""
    if triage["breaking"]:
        breaking_block = "\n🚨 **Breaking changes:**\n" + "\n".join(f"• {b[:100]}" for b in triage["breaking"][:5])

    relevant_block = ""
    if triage["relevant"]:
        relevant_block = "\n✅ **TMNT-relevant fixes:**\n" + "\n".join(f"• {r[:100]}" for r in triage["relevant"][:6])

    fleet_versions = (
        f"\n📦 **Fleet versions:** "
        f"Molty `{molty_current}` → `{latest}` | "
        f"Raphael `{state.get('raphael',{}).get('current','?')}` | "
        f"Leonardo `{state.get('leonardo',{}).get('current','?')}`"
    )

    msg = (
        f"🔄 **OpenClaw {latest} available** — running fleet update\n"
        f"{breaking_block}{relevant_block}{fleet_versions}\n\n"
        f"Staged rollout: Molty ✅ → Raphael 🔄 → Leonardo 🔄"
    )

    print(msg)
    post_discord(DISCORD_SQUAD_UPDATES, msg)
    mc_activity(f"OpenClaw {latest} fleet update starting", f"Breaking: {len(triage['breaking'])} | Relevant fixes: {len(triage['relevant'])}")

    # Trigger fleet update
    fleet_script = "/data/workspace/scripts/fleet-update.py"
    if os.path.exists(fleet_script):
        print(f"Triggering fleet-update.py for {latest}...")
        result = subprocess.run(
            ["/data/workspace/.venv/bin/python3", fleet_script, latest],
            capture_output=False, timeout=600
        )
        sys.exit(result.returncode)
    else:
        print("fleet-update.py not found — manual update required")
        sys.exit(1)

if __name__ == "__main__":
    main()
