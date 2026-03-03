#!/data/workspace/.venv/bin/python3
"""
todoist_triage.py — Intra-day Todoist inbox triage (runs hourly)

Fetches raw Todoist inbox tasks → rewrites title, assigns project/owner/priority,
adds 🦎 marker. Silent — no Telegram output. Logs to /data/workspace/logs/triage-YYYY-MM-DD.log

Does NOT: ping squad, scan email, sync MC, write prep state.
Those are standup_prep.py's job at 4:30 PM.
"""

import json, os, re, sys, urllib.request
from datetime import datetime, timedelta, timezone

HKT   = timezone(timedelta(hours=8))
NOW   = datetime.now(HKT)
TODAY = NOW.strftime("%Y-%m-%d")

TODOIST_TOKEN = "9a26743814658c9e82d92aa716b46a9b0a2257c4"
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}

LOG_FILE = f"/data/workspace/logs/triage-{TODAY}.log"

# ── Project IDs ───────────────────────────────────────────────────────────────
INBOX_ID    = "6M5rpCXmg7x7RC2Q"
BRINC_ID    = "6M5rpGgV6q865hrX"
CEREBRO_ID  = "6g53F7ccF8HHjgXM"
MANA_ID     = "6Rr9p6MxWHFwHXGC"
PERSONAL_ID = "6M5rpGfw5jR9Qg9R"
MOLTY_ID    = "6fwH32grqrCJF23R"

PROJECT_NAMES = {
    INBOX_ID: "Inbox", BRINC_ID: "Brinc", CEREBRO_ID: "Cerebro",
    MANA_ID: "Mana", PERSONAL_ID: "Personal", MOLTY_ID: "Molty's Den",
}

KEYWORD_OWNER = {
    "raphael": "Raphael", "brinc sales": "Raphael", "hubspot": "Raphael",
    "proposal": "Raphael", "outreach": "Raphael",
    "leonardo": "Leonardo", "cerebro": "Leonardo", "launchpad": "Leonardo",
    "tmnt": "Molty", "openclaw": "Molty", "molty": "Molty",
    "cron": "Molty", "agent": "Molty",
}

PROJECT_OWNER_DEFAULT = {
    BRINC_ID: "Raphael", CEREBRO_ID: "Leonardo",
    MOLTY_ID: "Molty", MANA_ID: "Guillermo",
    PERSONAL_ID: "Guillermo", INBOX_ID: "Guillermo",
}

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def http_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def http_post(url, headers, body=None):
    data = json.dumps(body).encode() if body else b""
    h = {**headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"  POST error {url[:60]}: {e}")
        return {}

# ── Logging ───────────────────────────────────────────────────────────────────

_log_lines = []

def log(msg):
    print(msg)
    _log_lines.append(msg)

def flush_log(processed):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = NOW.strftime("%H:%M")
    header = f"\n--- {TODAY} {ts} HKT — {processed} task(s) processed ---\n"
    with open(LOG_FILE, "a") as f:
        f.write(header + "\n".join(_log_lines) + "\n")

# ── Triage helpers ────────────────────────────────────────────────────────────

def is_processed(task):
    return "🦎" in task.get("content", "")

def estimate_time(content_lower):
    if any(w in content_lower for w in
           ["research", "build", "implement", "develop", "write", "design", "strategy", "spec", "plan"]):
        return "2h+"
    if any(w in content_lower for w in
           ["review", "analyze", "investigate", "setup", "configure", "prepare"]):
        return "1h"
    return "30min"

def determine_project(task):
    pid = task.get("project_id", "")
    if pid != INBOX_ID:
        return pid
    c = task.get("content", "").lower()
    if any(w in c for w in ["brinc", "hubspot", "proposal", "client", "deal", "sales", "pitch"]):
        return BRINC_ID
    if any(w in c for w in ["cerebro", "leonardo", "launchpad", "stripe", "feature", "beta", "meetcerebro"]):
        return CEREBRO_ID
    if any(w in c for w in ["mana", "portfolio", "investment", "capital"]):
        return MANA_ID
    if any(w in c for w in ["tmnt", "openclaw", "agent", "molty", "cron", "fleet", "railway"]):
        return MOLTY_ID
    return PERSONAL_ID

def determine_priority(task):
    existing = task.get("priority", 1)
    if existing > 1:
        return existing
    c = task.get("content", "").lower()
    if any(w in c for w in ["urgent", "asap", "critical", "blocking", "deadline today", "p0", "p1"]):
        return 4  # P1
    if any(w in c for w in ["proposal", "client", "revenue", "hire", "stripe", "launch", "beta", "deadline"]):
        return 3  # P2
    return 2  # P3 default

def determine_owner(task, assigned_project):
    c = task.get("content", "").lower()
    if assigned_project == MOLTY_ID:
        return "Molty"
    for kw, owner in KEYWORD_OWNER.items():
        if kw in c:
            return owner
    return PROJECT_OWNER_DEFAULT.get(assigned_project, "Guillermo")

def rewrite_title(raw_content, time_est):
    """Make title clean + actionable + append time estimate + 🦎 marker."""
    # Strip leading emoji/symbols that were added manually
    content = re.sub(r'^[\U00010000-\U0010ffff\u2600-\u27ff]+\s*', '', raw_content).strip()
    if not content:
        content = raw_content.strip()
    # Avoid double 🦎
    if "🦎" in content:
        return content
    return f"{content} — {time_est} 🦎"

# ── Todoist API ───────────────────────────────────────────────────────────────

def fetch_tasks():
    resp = http_get("https://api.todoist.com/api/v1/tasks?limit=200", TH)
    return resp.get("results", resp) if isinstance(resp, dict) else resp

def update_task(task_id, body):
    data = json.dumps(body).encode()
    h = {**TH, "Content-Type": "application/json"}
    req = urllib.request.Request(
        f"https://api.todoist.com/api/v1/tasks/{task_id}",
        data=data, method="POST", headers=h
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return True
    except Exception as e:
        log(f"  Update failed for {task_id}: {e}")
        return False

def move_task(task_id, project_id):
    http_post(
        f"https://api.todoist.com/api/v1/tasks/{task_id}/move",
        TH, {"project_id": project_id}
    )

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log(f"todoist_triage — {TODAY} {NOW.strftime('%H:%M')} HKT")

    tasks = fetch_tasks()
    inbox_raw = [t for t in tasks if
                 not is_processed(t) and t.get("project_id") == INBOX_ID]

    log(f"  {len(tasks)} active tasks total")
    log(f"  {len(inbox_raw)} unprocessed inbox tasks to triage")

    if not inbox_raw:
        log("  Nothing to triage — inbox clean.")
        flush_log(0)
        return 0

    processed = 0
    for task in inbox_raw:
        raw = task.get("content", "")
        tid = task["id"]
        c_lower = raw.lower()

        est          = estimate_time(c_lower)
        new_title    = rewrite_title(raw, est)
        new_project  = determine_project(task)
        new_priority = determine_priority(task)
        owner        = determine_owner(task, new_project)

        ok = update_task(tid, {
            "content":  new_title,
            "priority": new_priority,
        })

        if ok and new_project != INBOX_ID:
            move_task(tid, new_project)

        if ok:
            processed += 1
            log(f"  ✅ [{PROJECT_NAMES.get(new_project,'?')}] [{owner}] [P{5 - new_priority}] "
                f"{new_title[:70]}")
        else:
            log(f"  ⚠️  Failed to update: {raw[:60]}")

    log(f"\n  Done — {processed}/{len(inbox_raw)} tasks triaged.")
    flush_log(processed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
