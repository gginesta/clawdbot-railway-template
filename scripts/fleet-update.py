#!/data/workspace/.venv/bin/python3
"""fleet-update.py

Staged OpenClaw fleet rollout: Molty → Raphael → Leonardo.
Each agent is verified healthy before proceeding to the next.
On completion, sends Telegram report to Guillermo + posts to #command-center.

Usage:
  fleet-update.py <new-tag>                           # Full staged rollout
  fleet-update.py <new-tag> --agent molty|raphael|leonardo  # Single agent
  fleet-update.py --status                             # Show current fleet versions

State file: /data/workspace/state/openclaw-fleet-version.json
Report file: /data/workspace/state/fleet-update-report.json  (read by morning_briefing.py)
"""
from __future__ import annotations
import json, os, re, subprocess, sys, time, urllib.request, base64
from datetime import datetime
from zoneinfo import ZoneInfo

HKT = ZoneInfo("Asia/Hong_Kong")
STATE_FILE = "/data/workspace/state/openclaw-fleet-version.json"
REPORT_FILE = "/data/workspace/state/fleet-update-report.json"
GITHUB_TOKEN = "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"
RAILWAY_TOKEN = "1d318b62-a713-4fd6-80cf-c54c0934f5d8"
RAILWAY_API = "https://backboard.railway.app/graphql/v2"
MC_KEY = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
MC_API = "https://resilient-chinchilla-241.convex.site"
DISCORD_COMMAND_CENTER = "1468164160398557216"
TELEGRAM_GUILLERMO = "1097408992"
DOCKERFILE_REPO = "gginesta/clawdbot-railway-template"

AGENTS = {
    "molty": {
        "railway_service": "3daf200b-6fdb-4ead-a850-b7d33301f3b0",
        "railway_env": "f55df1f4-35ed-4ae7-9300-ec74ee9035be",
        "health_url": "https://ggvmolt.up.railway.app/health",
        "webhook_url": "https://ggvmolt.up.railway.app/hooks/agent",
        "emoji": "🦎",
    },
    "raphael": {
        "railway_service": "fc8720f0-cd59-48b1-93a2-c8b53e7faa90",
        "railway_env": "88c2c024-7471-4483-81f5-786f5c95c49b",
        "health_url": "https://ggv-raphael.up.railway.app/health",
        "webhook_url": "https://ggv-raphael.up.railway.app/hooks/agent",
        "emoji": "🔴",
    },
    "leonardo": {
        "railway_service": "02713288-b633-4f01-8bfe-e8ef9a739605",
        "railway_env": "ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9",
        "health_url": "https://leonardo-production.up.railway.app/health",
        "webhook_url": "https://leonardo-production.up.railway.app/hooks/agent",
        "emoji": "🔵",
    },
}

WEBHOOK_TOKENS = {
    "molty":    "ab0100a52e5476e61ae531a5d8df789ead150027d4cd07232b150144f5a5c562",
    "raphael":  "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd",
    "leonardo": "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now(HKT).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {a: {"current": "unknown", "last_good": "unknown"} for a in AGENTS}

def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def save_report(report: dict):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)

def _http_json(url, method="GET", data=None, headers=None, timeout=15):
    h = headers or {}
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, (json.loads(r.read()) if r.status != 204 else {})
    except Exception as e:
        return 0, {"error": str(e)}


# ── Health Check ──────────────────────────────────────────────────────────────

def health_check(agent: str, max_wait: int = 300) -> bool:
    """Wait for agent to be healthy AND running the expected version.

    Hits /health for liveness, then asks the agent its version via webhook.
    For webhook-updated agents (Raphael/Leonardo), the old version stays live
    until the agent restarts — so we must confirm the actual running version.
    """
    url = AGENTS[agent]["health_url"]
    log(f"  Health check {agent} ({url}) — waiting up to {max_wait}s...")
    deadline = time.time() + max_wait
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    log(f"  ✅ {agent} HTTP healthy (attempt {attempt})")
                    return True
        except Exception:
            pass
        time.sleep(15)
    log(f"  ❌ {agent} health check timed out after {max_wait}s")
    return False

def verify_agent_version(agent: str, expected_tag: str) -> bool:
    """Confirm an agent is actually running the expected version.

    Sends a version query via webhook and checks the response.
    Returns True if confirmed, False if unconfirmed (treat as not updated).
    Only used for webhook-updated agents (Raphael, Leonardo) where the
    update is async and health check alone is insufficient.
    """
    if agent == "molty":
        # Molty updates in-place synchronously — version is confirmed immediately
        result = subprocess.run(["openclaw", "--version"], capture_output=True, text=True, timeout=10)
        version_str = result.stdout.strip() or result.stderr.strip()
        confirmed = expected_tag.lstrip("v") in version_str
        log(f"  {'✅' if confirmed else '❌'} Molty version: {version_str} (expected {expected_tag})")
        return confirmed

    # For remote agents: we can't synchronously check their version
    # Mark as UNCONFIRMED — caller must verify before sending version-dependent scripts
    log(f"  ⚠️  {agent} version UNCONFIRMED — webhook update is async.")
    log(f"      Do not run version-dependent scripts until agent confirms via Discord.")
    return False  # conservative — caller handles this


# ── Dockerfile Update ─────────────────────────────────────────────────────────

def update_dockerfile_ref(new_tag: str) -> bool:
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    }
    status, data = _http_json(
        f"https://api.github.com/repos/{DOCKERFILE_REPO}/contents/Dockerfile",
        headers=headers
    )
    if status != 200:
        log(f"  ❌ Could not fetch Dockerfile: {status} {data}")
        return False

    content = base64.b64decode(data["content"]).decode()
    sha = data["sha"]

    old_match = re.search(r'ARG OPENCLAW_GIT_REF=(v\S+)', content)
    if not old_match:
        log("  ❌ Could not find OPENCLAW_GIT_REF in Dockerfile")
        return False

    old_ref = old_match.group(1)
    if old_ref == new_tag:
        log(f"  ✅ Dockerfile already at {new_tag}")
        return True

    updated = content.replace(
        f"ARG OPENCLAW_GIT_REF={old_ref}",
        f"ARG OPENCLAW_GIT_REF={new_tag}"
    )
    payload = json.dumps({
        "message": f"chore: bump OPENCLAW_GIT_REF {old_ref} → {new_tag} (fleet update by Molty 🦎)",
        "content": base64.b64encode(updated.encode()).decode(),
        "sha": sha,
    }).encode()

    status, result = _http_json(
        f"https://api.github.com/repos/{DOCKERFILE_REPO}/contents/Dockerfile",
        method="PUT", data=payload, headers=headers
    )
    if status in (200, 201):
        commit_sha = result.get("commit", {}).get("sha", "?")[:8]
        log(f"  ✅ Dockerfile bumped {old_ref} → {new_tag} (commit: {commit_sha})")
        return True
    log(f"  ❌ Dockerfile update failed: {status} {result}")
    return False


# ── Railway Redeploy ──────────────────────────────────────────────────────────

def railway_redeploy(agent: str) -> bool:
    """Try Railway API redeploy. Falls back to webhook update if 403 (token scope limited)."""
    info = AGENTS[agent]
    svc = info["railway_service"]
    env = info["railway_env"]
    # Note: use inline IDs, not GraphQL variables — avoids $-escaping issues in Python strings
    payload = json.dumps({
        "query": f'mutation {{ serviceInstanceRedeploy(serviceId: "{svc}", environmentId: "{env}") }}'
    }).encode()
    status, resp = _http_json(
        RAILWAY_API, method="POST", data=payload,
        headers={"Authorization": f"Bearer {RAILWAY_TOKEN}", "Content-Type": "application/json"}
    )
    if status == 403:
        log(f"  ⚠️  Railway token scope limited for {agent} — falling back to webhook update")
        return webhook_update(agent)
    success = bool(resp.get("data", {}).get("serviceInstanceRedeploy"))
    if success:
        log(f"  ✅ Railway redeploy triggered for {agent}")
    else:
        log(f"  ❌ Railway redeploy failed for {agent}: {resp}")
        log(f"  ↪️  Falling back to webhook update for {agent}")
        return webhook_update(agent)
    return success


# ── Molty Self-Update ─────────────────────────────────────────────────────────

def update_molty_inplace() -> bool:
    log("  Updating Molty in-place via openclaw update...")
    result = subprocess.run(
        ["openclaw", "update"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        log("  ✅ Molty updated in-place")
        return True
    log(f"  ❌ openclaw update failed (rc={result.returncode}): {result.stderr[:300]}")
    return False


# ── Notifications ─────────────────────────────────────────────────────────────

def mc_post(title: str, body: str):
    data = json.dumps({
        "agentId": "molty", "type": "deploy",
        "title": title, "body": body, "project": "fleet"
    }).encode()
    _http_json(
        f"{MC_API}/api/activity", method="POST", data=data,
        headers={"Authorization": f"Bearer {MC_KEY}", "Content-Type": "application/json"}
    )

def discord_send(msg: str):
    """Post to #command-center directly via openclaw CLI."""
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "discord",
         "--target", DISCORD_COMMAND_CENTER, "-m", msg],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        log("  ✅ Discord #command-center post sent")
    else:
        log(f"  ⚠️  Discord post failed (rc={result.returncode}): {result.stderr[:200]}")

def telegram_send(msg: str):
    """Send Telegram message to Guillermo directly via openclaw CLI."""
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "telegram",
         "--target", TELEGRAM_GUILLERMO, "-m", msg],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        log("  ✅ Telegram report sent to Guillermo")
    else:
        log(f"  ⚠️  Telegram send failed (rc={result.returncode}): {result.stderr[:200]}")

def webhook_update(agent: str) -> bool:
    """Send openclaw update directive to a remote agent via its inbound webhook."""
    info = AGENTS[agent]
    token = WEBHOOK_TOKENS[agent]
    msg = (
        "FLEET UPDATE DIRECTIVE from Molty 🦎: "
        "Please run `openclaw update` now to update to the latest OpenClaw release. "
        "This is a centrally coordinated update — do not run openclaw update independently."
    )
    data = json.dumps({"message": msg, "wakeMode": "now"}).encode()
    status, resp = _http_json(
        info["webhook_url"], method="POST", data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    if status in (200, 202) and resp.get("ok"):
        log(f"  ✅ Update directive sent to {agent} via webhook")
        return True
    log(f"  ❌ Webhook directive failed for {agent}: {status} {resp}")
    return False


# ── Backup ────────────────────────────────────────────────────────────────────

def backup_state(state: dict, tag: str):
    backup_dir = "/data/workspace/state/backups"
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now(HKT).strftime("%Y%m%d-%H%M%S")
    path = f"{backup_dir}/fleet-version-{ts}-pre-{tag}.json"
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
    log(f"  State backed up → {path}")


# ── Single Agent Update ───────────────────────────────────────────────────────

def update_agent(agent: str, new_tag: str, state: dict) -> bool:
    log(f"\n{'='*55}")
    log(f"  Updating {AGENTS[agent]['emoji']} {agent} → {new_tag}")

    if agent == "molty":
        ok = update_molty_inplace()
        wait = 90
    else:
        # Bump Dockerfile + trigger Railway redeploy (Railway builds take longer)
        ok = railway_redeploy(agent)
        wait = 240  # Railway rebuild takes 2-4 min

    if not ok:
        log(f"  ❌ Update trigger failed for {agent} — skipping")
        return False

    healthy = health_check(agent, max_wait=wait)
    if not healthy:
        log(f"  ❌ {agent} failed health check — rolling back state to last_good")
        state[agent]["current"] = state[agent].get("last_good", "unknown")
        save_state(state)
        return False

    if agent == "molty":
        # In-place update — confirm version immediately
        confirmed = verify_agent_version(agent, new_tag)
        if not confirmed:
            log(f"  ❌ {agent} version mismatch after update — check manually")
            return False
        state[agent]["last_good"] = state[agent].get("current", "unknown")
        state[agent]["current"] = new_tag
        state[agent]["updated_at"] = datetime.now(HKT).isoformat()
        log(f"  ✅ {agent} → {new_tag} confirmed")
    else:
        # Webhook update is async — mark as PENDING, not confirmed
        state[agent]["pending_update"] = new_tag
        state[agent]["pending_since"] = datetime.now(HKT).isoformat()
        log(f"  ⏳ {agent} update directive sent — version UNCONFIRMED until agent self-reports")
        log(f"     Agent must confirm running {new_tag} before version-dependent ops proceed")

    save_state(state)
    return True


# ── Full Rollout ──────────────────────────────────────────────────────────────

def full_rollout(new_tag: str, only_agent: str | None = None,
                 incorporation: list[str] | None = None,
                 highlights: list[str] | None = None,
                 is_critical: bool = False):

    state = load_state()
    backup_state(state, new_tag)
    now = datetime.now(HKT)

    log(f"\n🚀 Fleet update → {new_tag} ({'CRITICAL' if is_critical else 'standard'})")
    log("Current: " + " | ".join(f"{a}={v.get('current','?')}" for a, v in state.items()))

    # Bump Dockerfile for Raphael + Leonardo Railway deploys
    if not only_agent or only_agent != "molty":
        log("\nUpdating shared Dockerfile...")
        if not update_dockerfile_ref(new_tag):
            log("❌ Dockerfile update failed — aborting rollout")
            sys.exit(1)

    sequence = [only_agent] if only_agent else ["molty", "raphael", "leonardo"]
    results: dict[str, str] = {}

    for agent in sequence:
        if state.get(agent, {}).get("current") == new_tag:
            log(f"\n⏭️  {agent} already at {new_tag} — skipping")
            results[agent] = "⏭️ already current"
            continue
        ok = update_agent(agent, new_tag, state)
        results[agent] = "✅" if ok else "❌ failed"
        if not ok and not only_agent:
            log(f"\n⚠️  {agent} failed — continuing to remaining agents (independent deploys)")
            # Don't break — each agent deploys independently via Railway/webhook
        if agent != sequence[-1]:
            log(f"\n  Pausing 30s before next agent...")
            time.sleep(30)

    # Build report
    failed = [a for a, r in results.items() if "❌" in r]
    success = [a for a, r in results.items() if "✅" in r]
    skipped = [a for a, r in results.items() if "⏭️" in r]
    pending = [a for a in AGENTS if state.get(a, {}).get("pending_update") == new_tag]
    all_ok = not failed

    report = {
        "version": new_tag,
        "updated_at": now.isoformat(),
        "results": results,
        "highlights": highlights or [],
        "incorporation": incorporation or [],
        "is_critical": is_critical,
        "all_ok": all_ok,
    }
    save_report(report)

    # Discord #command-center post
    emoji_line = " → ".join(
        f"{AGENTS[a]['emoji']} {results.get(a,'?')}" for a in AGENTS if a in results
    )

    inc_lines = "\n".join(f"• {i}" for i in (incorporation or []))
    hi_lines = "\n".join(f"• {h}" for h in (highlights or [])[:5])

    discord_msg = (
        f"{'🚨' if is_critical else '📦'} **OpenClaw {new_tag}** — "
        f"{'✅ Fleet updated' if all_ok else '⚠️ Partial update'}\n"
        f"{emoji_line}\n"
    )
    if hi_lines:
        discord_msg += f"\n**What's new (TMNT-relevant):**\n{hi_lines}\n"
    if inc_lines:
        discord_msg += f"\n**How we're using it:**\n{inc_lines}\n"
    if failed:
        discord_msg += f"\n⚠️ Failed: {', '.join(failed)} — Molty investigating"

    # Telegram message (plain text, no markdown formatting)
    tg_msg = (
        f"{'🚨' if is_critical else '📦'} OpenClaw {new_tag} — "
        f"{'All agents updated ✅' if all_ok else 'Partial update ⚠️'}\n"
    )
    for a in AGENTS:
        if a in results:
            tg_msg += f"{AGENTS[a]['emoji']} {a}: {results[a]}\n"
    if highlights:
        tg_msg += "\nWhat's new (TMNT-relevant):\n"
        for h in highlights[:5]:
            tg_msg += f"• {h}\n"
    if incorporation:
        tg_msg += "\nHow we're using it:\n"
        for i in incorporation:
            tg_msg += f"• {i}\n"
    if failed:
        tg_msg += f"\n⚠️ Failed: {', '.join(failed)} — Molty investigating"

    # MC activity post (direct API — always works from script context)
    mc_post(
        f"Fleet {'updated' if all_ok else 'partial update'} → {new_tag}",
        f"Results: {results} | Critical: {is_critical}"
    )

    # Discord #command-center + Telegram — send directly now
    log("\nSending notifications...")
    discord_send(discord_msg)
    telegram_send(tg_msg)

    # Mark report as sent
    report["sent_at"] = datetime.now(HKT).isoformat()
    save_report(report)

    log(f"\n{'✅ Done' if all_ok else '⚠️ Partial'}: {results}")
    sys.exit(0 if all_ok else 1)


def show_status():
    state = load_state()
    print("Fleet version status:")
    for agent, info in state.items():
        print(f"  {agent}: current={info.get('current','?')} | last_good={info.get('last_good','?')} | updated={info.get('updated_at','?')}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or "--status" in args:
        show_status()
        sys.exit(0)

    if not args[0].startswith("v"):
        print("Usage: fleet-update.py <vX.Y.Z> [--agent molty|raphael|leonardo]")
        sys.exit(1)

    new_tag = args[0]
    only = None
    if "--agent" in args:
        idx = args.index("--agent")
        only = args[idx + 1]

    # incorporation/highlights can be passed via JSON file for cron use
    incorporation, highlights, is_critical = [], [], False
    if "--context" in args:
        idx = args.index("--context")
        with open(args[idx + 1]) as f:
            ctx = json.load(f)
        incorporation = ctx.get("incorporation", [])
        highlights = ctx.get("highlights", [])
        is_critical = ctx.get("is_critical", False)

    full_rollout(new_tag, only_agent=only,
                 incorporation=incorporation,
                 highlights=highlights,
                 is_critical=is_critical)
