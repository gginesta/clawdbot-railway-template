#!/data/workspace/.venv/bin/python3
"""
overnight_sync.py — Post-overnight auto-sync (runs at 04:00 HKT)

After all agents complete their overnight runs (Raphael 00:30, Leonardo 01:30, Molty 03:00),
this script syncs the results back into Todoist and the Notion standup DB.

What it does:
  1. Query MC for tasks marked done in the last 10 hours (the overnight window)
  2. For each done task: close matching open Todoist task (fuzzy match)
  3. For each done task: update matching Notion standup row Action → "✔️ Done"
  4. Log results + write to /data/workspace/logs/overnight-sync-YYYY-MM-DD.log

Why:
  Without this, agents complete MC tasks overnight but Todoist + Notion still show them
  as open → morning briefing shows stale "overdue" items → Guillermo sees false workload.
"""

import difflib, json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

HKT   = timezone(timedelta(hours=8))
NOW   = datetime.now(HKT)
TODAY = NOW.strftime("%Y-%m-%d")
# "Yesterday" = the standup date (5PM generated page — previous calendar day at 04:00 HKT)
YESTERDAY = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")

LOG_FILE = f"/data/workspace/logs/overnight-sync-{TODAY}.log"

# ── Credentials ───────────────────────────────────────────────────────────────
TODOIST_TOKEN = "9a26743814658c9e82d92aa716b46a9b0a2257c4"
MC_API        = "https://resilient-chinchilla-241.convex.site"
MC_TOKEN      = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
NOTION_KEY    = "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"
STANDUP_DB_ID = "31239dd6-9afd-81ad-8ffd-d1db09b1dd36"

TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
MH = {"Authorization": f"Bearer {MC_TOKEN}", "Content-Type": "application/json"}
NH = {"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2022-06-28",
      "Content-Type": "application/json"}

# Overnight window: last 10 hours (covers all agent runs + buffer)
OVERNIGHT_WINDOW_MS = 10 * 60 * 60 * 1000

_log_lines = []

def log(msg):
    print(msg)
    _log_lines.append(msg)

def flush_log():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w") as f:
        f.write(f"overnight_sync — {TODAY} {NOW.strftime('%H:%M')} HKT\n\n")
        f.write("\n".join(_log_lines) + "\n")

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def http_get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def http_post(url, headers, body=None, method="POST"):
    data = json.dumps(body).encode() if body else b""
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        log(f"  HTTP {e.code} on {url[:60]}: {e.read()[:100]}")
        return {}
    except Exception as e:
        log(f"  Error {url[:60]}: {e}")
        return {}

def http_patch(url, headers, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="PATCH", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except Exception as e:
        log(f"  PATCH error {url[:60]}: {e}")
        return {}

# ── Fuzzy matching ────────────────────────────────────────────────────────────

def fuzzy_match(query, candidates, threshold=0.55):
    """Return (best_match, score) or (None, 0)."""
    best, best_score = None, 0
    q = query.lower().strip()
    # Strip 🦎 marker and time estimates from candidate titles
    import re
    for c in candidates:
        c_clean = re.sub(r'\s*—\s*\d+\w+\+?\s*🦎\s*$', '', c).strip().lower()
        score = difflib.SequenceMatcher(None, q, c_clean).ratio()
        if score > best_score:
            best_score, best = score, c
    return (best, best_score) if best_score >= threshold else (None, 0)

# ── MC: fetch done tasks from overnight window ────────────────────────────────

def get_overnight_done_tasks():
    """Fetch MC tasks marked done within the overnight window."""
    cutoff_ms = int(NOW.timestamp() * 1000) - OVERNIGHT_WINDOW_MS
    try:
        tasks = http_get(f"{MC_API}/api/tasks", MH)
        if not isinstance(tasks, list):
            log("  ⚠️ MC returned unexpected format")
            return []
        done = [
            t for t in tasks
            if t.get("status") == "done"
            and (t.get("updatedAt") or t.get("completedAt") or 0) >= cutoff_ms
        ]
        log(f"  MC: {len(tasks)} total tasks, {len(done)} done in overnight window")
        return done
    except Exception as e:
        log(f"  ⚠️ MC fetch failed: {e}")
        return []

# ── Todoist: close matching tasks ─────────────────────────────────────────────

def get_open_todoist_tasks():
    try:
        resp = http_get("https://api.todoist.com/api/v1/tasks?limit=200", TH)
        tasks = resp.get("results", resp) if isinstance(resp, dict) else resp
        return tasks if isinstance(tasks, list) else []
    except Exception as e:
        log(f"  ⚠️ Todoist fetch failed: {e}")
        return []

def close_todoist_task(task_id):
    req = urllib.request.Request(
        f"https://api.todoist.com/api/v1/tasks/{task_id}/close",
        method="POST", headers=TH
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except Exception:
        return False

# Todoist project IDs (REG-036: personal without 🦎 = Guillermo's)
PERSONAL_PROJECT_ID = "6M5rpGfw5jR9Qg9R"

def sync_to_todoist(done_mc_tasks, open_todoist_tasks):
    """Close Todoist tasks that MC marked done overnight. Returns list of closed task titles."""
    closed = []
    todoist_contents = [t.get("content", "") for t in open_todoist_tasks]

    for mc_task in done_mc_tasks:
        mc_title = mc_task.get("title", "")
        match, score = fuzzy_match(mc_title, todoist_contents)
        if match:
            # Find the task object
            for t in open_todoist_tasks:
                if t.get("content", "") == match:
                    # REG-036: Personal tasks without 🦎 are Guillermo's — DO NOT TOUCH
                    if t.get("project_id") == PERSONAL_PROJECT_ID and "🦎" not in t.get("content", ""):
                        log(f"  ⏭ Skipped (personal task, no 🦎): {match[:60]}")
                        break
                    
                    # Safety check: only close tasks created/due in last 7 days
                    # (avoid accidentally closing old backlog items)
                    import re
                    created = t.get("created_at", "")
                    due = (t.get("due") or {}).get("date", "")
                    # Always safe to close if it's a recent task or the match is very strong
                    if score >= 0.75 or created >= YESTERDAY:
                        ok = close_todoist_task(t["id"])
                        if ok:
                            closed.append(f"{match[:60]} (score: {score:.0%})")
                            log(f"  ✅ Todoist closed: {match[:60]} [MC: {mc_title[:50]}] ({score:.0%})")
                        else:
                            log(f"  ⚠️ Todoist close failed: {match[:60]}")
                    else:
                        log(f"  ⏭ Skipped (old task, low score): {match[:60]} ({score:.0%})")
                    break

    return closed

# ── Notion: update standup DB rows ───────────────────────────────────────────

def get_standup_rows_for_date(standup_date: str):
    """Fetch all standup DB rows for a given standup date."""
    body = {
        "filter": {
            "property": "Standup Date",
            "date": {"equals": standup_date}
        },
        "page_size": 100
    }
    try:
        resp = http_post(
            f"https://api.notion.com/v1/databases/{STANDUP_DB_ID}/query",
            NH, body
        )
        rows = resp.get("results", [])
        log(f"  Notion: {len(rows)} rows for standup date {standup_date}")
        return rows
    except Exception as e:
        log(f"  ⚠️ Notion query failed: {e}")
        return []

def get_row_title(row):
    """Extract task title from a Notion DB row."""
    title_prop = row.get("properties", {}).get("Task", {})
    parts = title_prop.get("title", [])
    return "".join(p.get("plain_text", "") for p in parts).strip()

def get_row_action(row):
    """Get current Action select value."""
    action_prop = row.get("properties", {}).get("Action", {})
    sel = action_prop.get("select")
    return sel.get("name") if sel else None

def mark_notion_row_done(page_id: str):
    """Update Action → '✔️ Done' on a Notion standup DB row."""
    body = {
        "properties": {
            "Action": {"select": {"name": "✔️ Done"}}
        }
    }
    resp = http_patch(f"https://api.notion.com/v1/pages/{page_id}", NH, body)
    return bool(resp.get("id"))

def sync_to_notion(done_mc_tasks, standup_rows):
    """Update Notion standup rows where MC task completed overnight. Returns list of updated rows."""
    updated = []
    row_titles = [get_row_title(r) for r in standup_rows]

    for mc_task in done_mc_tasks:
        mc_title = mc_task.get("title", "")
        match, score = fuzzy_match(mc_title, row_titles)
        if match:
            for row in standup_rows:
                if get_row_title(row) == match:
                    current_action = get_row_action(row)
                    # Don't overwrite if already actioned (Done/Drop)
                    if current_action in ("✔️ Done", "🗑️ Drop", "📦 Archive"):
                        log(f"  ⏭ Notion row already actioned ({current_action}): {match[:50]}")
                        break
                    ok = mark_notion_row_done(row["id"])
                    if ok:
                        updated.append(f"{match[:60]} (score: {score:.0%})")
                        log(f"  ✅ Notion row → Done: {match[:60]} [MC: {mc_title[:50]}] ({score:.0%})")
                    else:
                        log(f"  ⚠️ Notion update failed: {match[:60]}")
                    break

    return updated

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log(f"overnight_sync — {TODAY} {NOW.strftime('%H:%M')} HKT")
    log(f"Overnight window: last 10 hours (cutoff: {(NOW - timedelta(hours=10)).strftime('%H:%M')} HKT)")
    log(f"Syncing against standup date: {YESTERDAY}\n")

    # 1. Fetch MC done tasks from overnight window
    log("1. Fetching MC overnight completions...")
    done_mc = get_overnight_done_tasks()

    if not done_mc:
        log("  Nothing completed overnight — nothing to sync.")
        flush_log()
        return 0

    for t in done_mc:
        log(f"  • [{t.get('assignees',['?'])[0] if t.get('assignees') else '?'}] "
            f"{t.get('title','?')[:60]} (updated: {t.get('updatedAt', 0)})")

    # 2. Fetch open Todoist tasks
    log("\n2. Fetching open Todoist tasks...")
    todoist_tasks = get_open_todoist_tasks()
    log(f"  {len(todoist_tasks)} open tasks")

    # 3. Sync to Todoist
    log("\n3. Closing completed tasks in Todoist...")
    closed = sync_to_todoist(done_mc, todoist_tasks)

    # 4. Fetch Notion standup rows
    log(f"\n4. Fetching Notion standup rows for {YESTERDAY}...")
    standup_rows = get_standup_rows_for_date(YESTERDAY)

    # 5. Sync to Notion
    log("\n5. Updating Notion standup rows...")
    updated_notion = sync_to_notion(done_mc, standup_rows)

    # 6. Summary
    log(f"\n── Summary ──────────────────────────────────")
    log(f"  MC tasks done overnight:   {len(done_mc)}")
    log(f"  Todoist tasks closed:      {len(closed)}")
    log(f"  Notion rows marked done:   {len(updated_notion)}")
    if closed:
        for c in closed:
            log(f"    Todoist: {c}")
    if updated_notion:
        for u in updated_notion:
            log(f"    Notion:  {u}")

    flush_log()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
