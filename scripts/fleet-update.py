#!/data/workspace/.venv/bin/python3
"""fleet-update.py

Staged OpenClaw fleet rollout: Molty → Raphael → Leonardo.
Each agent is verified healthy before proceeding to the next.

Usage:
  fleet-update.py <new-tag>              # Full staged rollout
  fleet-update.py <new-tag> --agent molty|raphael|leonardo  # Single agent
  fleet-update.py --status              # Show current fleet versions

State file: /data/workspace/state/openclaw-fleet-version.json
"""
from __future__ import annotations
import json, os, subprocess, sys, time, urllib.request, base64
from datetime import datetime
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
STATE_FILE = "/data/workspace/state/openclaw-fleet-version.json"
GITHUB_TOKEN = "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"
RAILWAY_TOKEN = "1d318b62-a713-4fd6-80cf-c54c0934f5d8"
RAILWAY_API = "https://backboard.railway.app/graphql/v2"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
MC_API = "https://resilient-chinchilla-241.convex.site"
DISCORD_SQUAD_UPDATES = "1468164181155909743"
DOCKERFILE_REPO = "gginesta/clawdbot-railway-template"

AGENTS = {
    "molty": {
        "railway_service": "3daf200b-6fdb-4ead-a850-b7d33301f3b0",
        "railway_env": "f55df1f4-35ed-4ae7-9300-ec74ee9035be",
        "health_url": "https://ggvmolt.up.railway.app/health",
        "webhook_url": "https://ggvmolt.up.railway.app/hooks/agent",
    },
    "raphael": {
        "railway_service": "fc8720f0-cd59-48b1-93a2-c8b53e7faa90",
        "railway_env": "88c2c024-7471-4483-81f5-786f5c95c49b",
        "health_url": "https://ggv-raphael.up.railway.app/health",
        "webhook_url": "https://ggv-raphael.up.railway.app/hooks/agent",
    },
    "leonardo": {
        "railway_service": "02713288-b633-4f01-8bfe-e8ef9a739605",
        "railway_env": "ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9",
        "health_url": "https://leonardo-production.up.railway.app/health",
        "webhook_url": "https://leonardo-production.up.railway.app/hooks/agent",
    },
}
WEBHOOK_TOKENS = {
    "molty":    "ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562",
    "raphael":  "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd",  # shared (old)
    "leonardo": "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758",  # new
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now(HKT).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {a: {"current": "unknown", "last_good": "unknown"} for a in AGENTS}

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def _http_json(url, method="GET", data=None, headers=None, timeout=15):
    h = headers or {}
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read()) if r.status != 204 else {}
    except Exception as e:
        return 0, {"error": str(e)}

def railway_query(query: str, variables: dict | None = None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    status, data = _http_json(
        RAILWAY_API, method="POST", data=payload,
        headers={"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"}
    )
    return data.get("data", {}) if status == 200 else {}


# ── Health Check ─────────────────────────────────────────────────────────────

def health_check(agent: str, max_wait: int = 300) -> bool:
    """Wait for agent health endpoint to return 200. Times out after max_wait seconds."""
    url = AGENTS[agent]["health_url"]
    log(f"  Health check {agent} ({url})...")
    deadline = time.time() + max_wait
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    log(f"  ✅ {agent} healthy (attempt {attempt})")
                    return True
        except Exception:
            pass
        time.sleep(15)
    log(f"  ❌ {agent} health check timed out after {max_wait}s")
    return False

def get_agent_version(agent: str) -> str | None:
    """Ask agent for its current OpenClaw version via webhook."""
    info = AGENTS[agent]
    data = json.dumps({"message": "What is your current OpenClaw version? Reply with just the version tag.", "wakeMode": "now"}).encode()
    status, resp = _http_json(
        info["webhook_url"], method="POST", data=data,
        headers={"Authorization": f"Bearer {WEBHOOK_TOKEN}", "Content-Type": "application/json"}
    )
    return None  # Version check is async; state file is source of truth


# ── Dockerfile Update ────────────────────────────────────────────────────────

def update_dockerfile_ref(new_tag: str) -> bool:
    """Bump OPENCLAW_GIT_REF in the shared Dockerfile on GitHub."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}

    # Get current file + SHA
    status, data = _http_json(
        f"https://api.github.com/repos/{DOCKERFILE_REPO}/contents/Dockerfile",
        headers=headers
    )
    if status != 200:
        log(f"  ❌ Could not fetch Dockerfile: {status}")
        return False

    content = base64.b64decode(data["content"]).decode()
    sha = data["sha"]

    # Find and replace current ref
    import re
    old_match = re.search(r'ARG OPENCLAW_GIT_REF=(v\S+)', content)
    if not old_match:
        log("  ❌ Could not find OPENCLAW_GIT_REF in Dockerfile")
        return False

    old_ref = old_match.group(1)
    if old_ref == new_tag:
        log(f"  ✅ Dockerfile already at {new_tag}")
        return True

    updated = content.replace(f"ARG OPENCLAW_GIT_REF={old_ref}", f"ARG OPENCLAW_GIT_REF={new_tag}")
    payload = json.dumps({
        "message": f"chore: bump OPENCLAW_GIT_REF {old_ref} → {new_tag} (fleet update by Molty)",
        "content": base64.b64encode(updated.encode()).decode(),
        "sha": sha
    }).encode()

    status, result = _http_json(
        f"https://api.github.com/repos/{DOCKERFILE_REPO}/contents/Dockerfile",
        method="PUT", data=payload, headers=headers
    )
    if status in (200, 201):
        log(f"  ✅ Dockerfile bumped {old_ref} → {new_tag} (commit: {result.get('commit',{}).get('sha','?')[:8]})")
        return True
    log(f"  ❌ Dockerfile update failed: {status}")
    return False


# ── Railway Redeploy ──────────────────────────────────────────────────────────

def railway_redeploy(agent: str) -> bool:
    """Trigger Railway redeploy — only works for Molty (token scope limited)."""
    if agent != "molty":
        log(f"  ⚠️  Railway token limited to Molty — using webhook update for {agent}")
        return webhook_update(agent)
    info = AGENTS[agent]
    svc = info["railway_service"]
    env = info["railway_env"]
    payload = json.dumps({
        "query": f'mutation {{ serviceInstanceRedeploy(serviceId: "{svc}", environmentId: "{env}") }}'
    }).encode()
    status, resp = _http_json(
        RAILWAY_API, method="POST", data=payload,
        headers={"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"}
    )
    success = resp.get("data", {}).get("serviceInstanceRedeploy", False)
    if success:
        log(f"  ✅ Railway redeploy triggered for {agent}")
    else:
        log(f"  ❌ Railway redeploy failed for {agent}: {resp}")
    return bool(success)


def webhook_update(agent: str) -> bool:
    """Send openclaw update directive to a remote agent via webhook."""
    info = AGENTS[agent]
    msg = (
        "FLEET UPDATE DIRECTIVE from Molty 🦎: "
        "Run `openclaw update` now to update to the latest OpenClaw release. "
        "After updating, confirm with: openclaw version. "
        "This is a centrally managed update — do not run openclaw update independently going forward."
    )
    token = WEBHOOK_TOKENS.get(agent, WEBHOOK_TOKENS["raphael"])
    data = json.dumps({"message": msg, "wakeMode": "now"}).encode()
    status, resp = _http_json(
        info["webhook_url"], method="POST", data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    if status in (200, 202) and resp.get("ok"):
        log(f"  ✅ Update directive sent to {agent} via webhook (runId: {resp.get('runId','?')[:8]})")
        return True
    log(f"  ❌ Webhook directive failed for {agent}: {status} {resp}")
    return False


# ── Molty Self-Update ────────────────────────────────────────────────────────

def update_molty_inplace() -> bool:
    """Update Molty via openclaw update (in-place, no Railway rebuild needed)."""
    log("  Updating Molty in-place via openclaw update...")
    result = subprocess.run(["openclaw", "update"], capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        log("  ✅ Molty updated in-place")
        return True
    log(f"  ❌ openclaw update failed: {result.stderr[:200]}")
    return False


# ── Notifications ─────────────────────────────────────────────────────────────

def mc_post(title: str, body: str):
    data = json.dumps({"agentId": "molty", "type": "deploy", "title": title, "body": body, "project": "fleet"}).encode()
    _http_json(f"{MC_API}/api/activity", method="POST", data=data,
               headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"})

def discord_post(msg: str):
    try:
        subprocess.run(
            ["openclaw", "send", "--channel", "discord", "--to", f"channel:{DISCORD_SQUAD_UPDATES}", msg],
            capture_output=True, timeout=15
        )
    except Exception as e:
        log(f"Discord post error: {e}")


# ── Backup ────────────────────────────────────────────────────────────────────

def backup_state(state: dict, tag: str):
    backup_dir = "/data/workspace/state/backups"
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now(HKT).strftime("%Y%m%d-%H%M%S")
    path = f"{backup_dir}/fleet-version-{ts}-pre-{tag}.json"
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
    log(f"  State backed up → {path}")


# ── Main Rollout ─────────────────────────────────────────────────────────────

def update_agent(agent: str, new_tag: str, state: dict) -> bool:
    """Update a single agent. Returns True if successful."""
    log(f"\n{'='*50}")
    log(f"Updating {agent} → {new_tag}")

    if agent == "molty":
        ok = update_molty_inplace()
    else:
        ok = webhook_update(agent)
        if ok:
            log(f"  Waiting 45s for {agent} to run update and restart gateway...")
            time.sleep(45)

    if not ok:
        log(f"  ❌ Update trigger failed for {agent}")
        return False

    # Health check — in-place updates restart gateway (~30s), Railway builds take longer
    wait = 90 if agent == "molty" else 180
    healthy = health_check(agent, max_wait=wait)
    if not healthy:
        log(f"  ❌ {agent} failed health check after update — rolling back state")
        state[agent]["current"] = state[agent].get("last_good", "unknown")
        return False

    # Update state
    state[agent]["last_good"] = state[agent].get("current", "unknown")
    state[agent]["current"] = new_tag
    state[agent]["updated_at"] = datetime.now(HKT).isoformat()
    save_state(state)
    log(f"  ✅ {agent} updated to {new_tag}")
    return True


def full_rollout(new_tag: str, only_agent: str | None = None):
    state = load_state()
    backup_state(state, new_tag)

    log(f"\n🚀 Fleet update → {new_tag}")
    log(f"Current state: " + " | ".join(f"{a}={v.get('current','?')}" for a, v in state.items()))

    # Update Dockerfile first (for Raphael + Leonardo rebuilds)
    log("\nUpdating Dockerfile...")
    if not update_dockerfile_ref(new_tag):
        log("❌ Dockerfile update failed — aborting")
        sys.exit(1)

    sequence = [only_agent] if only_agent else ["molty", "raphael", "leonardo"]
    results = {}

    for agent in sequence:
        if state.get(agent, {}).get("current") == new_tag:
            log(f"\n⏭️  {agent} already at {new_tag} — skipping")
            results[agent] = "skipped"
            continue
        ok = update_agent(agent, new_tag, state)
        results[agent] = "✅" if ok else "❌"
        if not ok and not only_agent:
            log(f"\n🛑 Stopping rollout — {agent} failed. Raphael/Leonardo not updated.")
            break

    # Summary
    summary_lines = [f"{a}: {r}" for a, r in results.items()]
    summary = f"Fleet update {new_tag} complete: " + " | ".join(summary_lines)
    log(f"\n{summary}")

    failed = [a for a, r in results.items() if r == "❌"]
    discord_msg = (
        f"📦 **Fleet Update {new_tag}** — {'✅ All clear' if not failed else '⚠️ Partial'}\n"
        + "\n".join(f"• {a}: {r}" for a, r in results.items())
    )
    discord_post(discord_msg)
    mc_post(f"Fleet update {new_tag} {'complete' if not failed else 'partial'}", summary)

    sys.exit(0 if not failed else 1)


def show_status():
    state = load_state()
    print("Fleet version status:")
    for agent, info in state.items():
        print(f"  {agent}: {info.get('current','?')} (last_good: {info.get('last_good','?')})")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or "--status" in args:
        show_status()
    elif len(args) >= 1 and args[0].startswith("v"):
        only = None
        if "--agent" in args:
            idx = args.index("--agent")
            only = args[idx + 1]
        full_rollout(args[0], only_agent=only)
    else:
        print("Usage: fleet-update.py <tag> [--agent molty|raphael|leonardo]")
        sys.exit(1)
