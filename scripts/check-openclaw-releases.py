#!/data/workspace/.venv/bin/python3
"""check-openclaw-releases.py

Daily cron (05:15 HKT): checks for new OpenClaw releases, triages release notes
for TMNT relevance, triggers fleet-update.py if a new version is found.

A separate report file is written for morning_briefing.py to pick up and
send to Guillermo as a separate Telegram message after the 06:30 briefing.

Critical releases (security patches) update immediately.
Standard releases update during the 05:15 maintenance window.

State: /data/workspace/state/openclaw-fleet-version.json
Report: /data/workspace/state/fleet-update-report.json
"""
from __future__ import annotations
import json, os, subprocess, sys, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
STATE_FILE = "/data/workspace/state/openclaw-fleet-version.json"
REPORT_FILE = "/data/workspace/state/fleet-update-report.json"
GITHUB_TOKEN = "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"
FLEET_UPDATE_SCRIPT = "/data/workspace/scripts/fleet-update.py"
PYTHON = "/data/workspace/.venv/bin/python3"

# ── TMNT Relevance Filters ────────────────────────────────────────────────────
# Features/fixes in these areas directly affect our fleet
RELEVANT_KEYWORDS = [
    "subagent", "sub-agent", "cron", "heartbeat", "webhook", "discord",
    "telegram", "memory", "session", "delivery", "routing", "config",
    "gateway", "agent", "tool", "skill", "railway", "redeploy",
    "isolated", "hook", "queue", "drain", "NO_REPLY", "typing",
    "secrets", "auth", "spawn", "thread",
]
SECURITY_KEYWORDS = [
    "security", "Security", "SECURITY", "CVE", "vulnerability",
    "SSRF", "sandbox", "path escape", "injection", "auth bypass",
    "spoofing", "bypass", "hardening", "harden",
]
BREAKING_KEYWORDS = ["breaking", "BREAKING", "Breaking Change"]

# ── How TMNT uses features — maps release keywords to incorporation notes ─────
INCORPORATION_MAP = {
    "secrets": "Migrate TMNT credentials to `openclaw secrets` — stop hardcoding tokens in scripts",
    "cron": "Overnight crons benefit automatically from reliability improvements",
    "NO_REPLY": "NO_REPLY suppression fix applies fleet-wide automatically",
    "isolated": "Isolated cron session routing fix — overnight task workers benefit automatically",
    "subagent": "Sub-agent spawning improvements — check thread=true behaviour in Discord sessions",
    "thread": "Thread-bound agent sessions — review sub-agent Discord routing",
    "delivery": "Delivery queue improvements — better Telegram reliability fleet-wide",
    "webhook": "Webhook routing improvements — test TMNT webhook endpoints post-update",
    "discord": "Discord fixes apply to #command-center and squad channel monitoring",
    "telegram": "Telegram fixes apply to Guillermo's briefing and alert delivery",
    "typing": "Typing indicator cleanup — no action needed, applies automatically",
    "memory": "Memory system improvements — no action needed",
    "auth": "Auth handling improvements — verify all agent tokens post-update",
    "canvas": "Canvas improvements — available for Molty web previews if needed",
}


def _http(url: str, headers: dict | None = None, timeout: int = 15):
    h = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return 0, {"error": str(e)}

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def get_latest_stable_tag() -> str | None:
    status, tags = _http("https://api.github.com/repos/openclaw/openclaw/tags?per_page=10")
    if status != 200:
        print(f"GitHub API error: {status} {tags}")
        return None
    for tag in tags:
        name = tag.get("name", "")
        if name.startswith("v") and "beta" not in name and "alpha" not in name:
            return name
    return None

def get_release_notes(tag: str) -> str:
    status, data = _http(f"https://api.github.com/repos/openclaw/openclaw/releases/tags/{tag}")
    if status == 200:
        return data.get("body", "")
    return ""

def triage_release(tag: str, notes: str) -> dict:
    """
    Parse release notes into:
    - breaking: breaking change items
    - security: security fix items (triggers critical=True)
    - highlights: TMNT-relevant feature/fix items (for the report)
    - incorporation: how we'll use new features in the TMNT squad
    """
    lines = notes.split("\n")
    breaking, security, highlights = [], [], []
    incorporation_seen = set()
    incorporation = []

    in_breaking = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Section header detection
        if stripped.startswith("###"):
            in_breaking = "Breaking" in stripped or "BREAKING" in stripped
            continue

        if not stripped.startswith("-"):
            continue

        item = stripped.lstrip("- ").strip()

        # Classify
        is_security = any(k in item for k in SECURITY_KEYWORDS)
        is_breaking = in_breaking or any(k in item for k in BREAKING_KEYWORDS)
        is_relevant = any(k.lower() in item.lower() for k in RELEVANT_KEYWORDS)

        if is_security:
            security.append(item[:120])

        if is_breaking:
            breaking.append(item[:120])

        if is_relevant and not is_security:
            highlights.append(item[:130])

        # Map to incorporation notes
        for keyword, note in INCORPORATION_MAP.items():
            if keyword.lower() in item.lower() and note not in incorporation_seen:
                incorporation.append(note)
                incorporation_seen.add(note)

    # Security patches always get an incorporation note
    if security and "Verify all agent tokens post-update" not in str(incorporation):
        incorporation.insert(0, f"🔒 {len(security)} security patches — update is mandatory, no config changes required")

    return {
        "tag": tag,
        "breaking": breaking[:5],
        "security": security[:10],
        "highlights": highlights[:8],
        "incorporation": incorporation[:6],
        "is_critical": len(security) > 0,
    }


def main():
    state = load_state()
    current = state.get("molty", {}).get("current", "v0.0.0")

    latest = get_latest_stable_tag()
    if not latest:
        print("Could not fetch latest tag — skipping")
        sys.exit(0)

    print(f"Latest stable: {latest} | Fleet current: {current}")

    if latest == current:
        print("Already up to date — no action needed")
        sys.exit(0)

    # New version found
    print(f"New version available: {latest}")
    notes = get_release_notes(latest)
    triage = triage_release(latest, notes)

    is_critical = triage["is_critical"]
    print(f"Critical: {is_critical} | Security fixes: {len(triage['security'])} | Highlights: {len(triage['highlights'])}")

    # Write context file for fleet-update.py
    context_file = "/data/workspace/state/fleet-update-context.json"
    os.makedirs(os.path.dirname(context_file), exist_ok=True)
    with open(context_file, "w") as f:
        json.dump({
            "highlights": triage["highlights"],
            "incorporation": triage["incorporation"],
            "is_critical": is_critical,
            "breaking": triage["breaking"],
            "security_count": len(triage["security"]),
        }, f, indent=2)

    # Trigger fleet update
    print(f"Triggering fleet update → {latest}...")
    result = subprocess.run(
        [PYTHON, FLEET_UPDATE_SCRIPT, latest, "--context", context_file],
        timeout=900  # 15 min max for full fleet rollout
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
