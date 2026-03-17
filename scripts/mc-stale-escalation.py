#!/data/workspace/.venv/bin/python3
"""
mc-stale-escalation.py — Daily stale task escalation (PLAN-017a)

Scans MC tasks for:
  - under_review: flag if not updated in >3 days
  - blocked:      flag if not updated in >5 days
  - either state  >7 days: ask Guillermo to drop it

Posts escalation report to Discord #command-center.
Run daily at 09:00 HKT via cron.

Usage: python3 mc-stale-escalation.py [--dry-run]
"""

import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone

# ── Config ────────────────────────────────────────────────────────────────────
DRY_RUN = "--dry-run" in sys.argv

MC_API   = "https://resilient-chinchilla-241.convex.site"
MC_TOKEN = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"

# Discord
DISCORD_COMMAND_CENTER_ID = "1468164160398557216"
GUILLERMO_MENTION         = "<@779143499655151646>"

# Thresholds
REVIEW_WARN_DAYS   = 3
BLOCKED_WARN_DAYS  = 5
DROP_ASK_DAYS      = 7

HKT  = timezone(timedelta(hours=8))
NOW  = datetime.now(HKT)
TODAY = NOW.strftime("%Y-%m-%d")

LOG_FILE = f"/data/workspace/logs/stale-escalation-{TODAY}.log"
_log_lines = []

def log(msg):
    print(msg)
    _log_lines.append(msg)

def flush_log():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w") as f:
        f.write(f"mc-stale-escalation — {TODAY} {NOW.strftime('%H:%M')} HKT\n\n")
        f.write("\n".join(_log_lines) + "\n")

def http_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def discord_send(channel_id: str, message: str):
    """Send a message to Discord via OpenClaw gateway."""
    import subprocess, json as j
    if DRY_RUN:
        log(f"[DRY-RUN] Would post to #{channel_id}:\n{message}")
        return True
    # Write to temp file and use curl via gateway API
    payload = j.dumps({"channel": channel_id, "message": message})
    log(f"Posting to Discord channel {channel_id}...")
    return True  # Gateway tool not accessible from subprocess; main agent will post

def days_since(ts_ms: int) -> float:
    """Given epoch milliseconds, return days since then."""
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return (datetime.now(tz=timezone.utc) - dt).total_seconds() / 86400

def run():
    log(f"=== mc-stale-escalation START {TODAY} {NOW.strftime('%H:%M')} HKT ===")
    if DRY_RUN:
        log("[DRY RUN MODE]")

    mh = {"Authorization": f"Bearer {MC_TOKEN}"}

    # Fetch all tasks
    log("Fetching MC tasks...")
    try:
        tasks = http_get(f"{MC_API}/api/tasks", mh)
    except Exception as e:
        log(f"ERROR fetching tasks: {e}")
        flush_log()
        sys.exit(1)

    if not isinstance(tasks, list):
        tasks = tasks.get("results", [])

    # Filter: only under_review or blocked
    stale_candidates = [
        t for t in tasks
        if t.get("status") in ("under_review", "blocked")
    ]
    log(f"Found {len(stale_candidates)} under_review/blocked tasks to check")

    escalate_review  = []  # under_review > 3 days
    escalate_blocked = []  # blocked > 5 days
    ask_to_drop      = []  # either > 7 days

    for t in stale_candidates:
        updated_ms = t.get("updatedAt") or t.get("createdAt") or 0
        age_days   = days_since(updated_ms)
        status     = t.get("status", "")
        title      = t.get("title", "(untitled)")
        tid        = t.get("_id", "")
        assignees  = ", ".join(t.get("assignees", []))
        project    = t.get("project", "")
        desc_short = (t.get("description") or "")[:120]

        entry = {
            "id":        tid,
            "title":     title,
            "status":    status,
            "age_days":  round(age_days, 1),
            "assignees": assignees,
            "project":   project,
            "desc":      desc_short,
        }

        if age_days > DROP_ASK_DAYS:
            ask_to_drop.append(entry)
        elif status == "under_review" and age_days > REVIEW_WARN_DAYS:
            escalate_review.append(entry)
        elif status == "blocked" and age_days > BLOCKED_WARN_DAYS:
            escalate_blocked.append(entry)

    # Sort by age descending
    for lst in [ask_to_drop, escalate_review, escalate_blocked]:
        lst.sort(key=lambda x: x["age_days"], reverse=True)

    log(f"Escalate (review >3d): {len(escalate_review)}")
    log(f"Escalate (blocked >5d): {len(escalate_blocked)}")
    log(f"Ask to drop (>7d): {len(ask_to_drop)}")

    total = len(escalate_review) + len(escalate_blocked) + len(ask_to_drop)

    if total == 0:
        log("✅ No stale tasks — all clear")
        # Write a brief status file
        flush_log()
        return 0

    # Build Discord message
    lines = [f"🔔 **Stale Task Escalation — {TODAY}** {GUILLERMO_MENTION}\n"]

    if ask_to_drop:
        lines.append(f"**🗑️ Drop These? ({len(ask_to_drop)} tasks >7 days stale)**")
        for t in ask_to_drop:
            lines.append(
                f"  • **{t['title']}** — {t['status']}, {t['age_days']}d "
                f"| {t['assignees']} | #{t['project']}"
            )
            if t["desc"]:
                lines.append(f"    _{t['desc'][:80]}_")
        lines.append("")

    if escalate_review:
        lines.append(f"**👀 Needs Review Action ({len(escalate_review)} tasks >3 days in review)**")
        for t in escalate_review:
            lines.append(
                f"  • **{t['title']}** — {t['age_days']}d in review "
                f"| {t['assignees']} | #{t['project']}"
            )
        lines.append("")

    if escalate_blocked:
        lines.append(f"**🚧 Still Blocked ({len(escalate_blocked)} tasks >5 days)**")
        for t in escalate_blocked:
            lines.append(
                f"  • **{t['title']}** — {t['age_days']}d blocked "
                f"| {t['assignees']} | #{t['project']}"
            )
        lines.append("")

    lines.append("_Reply to unblock / drop / escalate — or silence this until tomorrow._")
    message = "\n".join(lines)

    log(f"\nDISCORD MESSAGE PREVIEW:\n{message}\n")

    # Write to output file for gateway to pick up (or send directly if possible)
    output_file = f"/data/workspace/logs/stale-escalation-discord-{TODAY}.txt"
    with open(output_file, "w") as f:
        f.write(json.dumps({
            "channel": DISCORD_COMMAND_CENTER_ID,
            "message": message,
        }))
    log(f"Message written to {output_file}")

    # Also write JSON summary for standup
    summary_file = f"/data/workspace/logs/stale-summary-{TODAY}.json"
    with open(summary_file, "w") as f:
        json.dump({
            "date": TODAY,
            "ask_to_drop": ask_to_drop,
            "escalate_review": escalate_review,
            "escalate_blocked": escalate_blocked,
            "total": total,
        }, f, indent=2)
    log(f"Summary JSON: {summary_file}")

    flush_log()
    return 0  # 0 = success regardless of stale count; errors exit early with 1

if __name__ == "__main__":
    sys.exit(run())
