#!/data/workspace/.venv/bin/python3
"""
overnight_sync.py — Post-overnight auto-sync (runs at 04:00 HKT)

After all agents complete their overnight runs (Raphael 00:30, Leonardo 01:30, Molty 03:00),
this script syncs results back into Todoist and the Notion standup DB.

UPDATED 2026-03-19 (TMN-4): Pulls from Paperclip instead of MC.
- Primary source: Paperclip issues with status=done, completed in last 10h
- Todoist: close matching 🦎 tasks only (REG-036)
- Notion standup DB: mark matching rows done
"""

import difflib, json, os, re, sys, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

HKT   = timezone(timedelta(hours=8))
NOW   = datetime.now(HKT)
TODAY = NOW.strftime("%Y-%m-%d")
YESTERDAY = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")

LOG_FILE = f"/data/workspace/logs/overnight-sync-{TODAY}.log"

# ── Credentials ───────────────────────────────────────────────────────────────
TODOIST_TOKEN = "9a26743814658c9e82d92aa716b46a9b0a2257c4"
NOTION_KEY    = "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"
STANDUP_DB_ID = "31239dd6-9afd-81ad-8ffd-d1db09b1dd36"

# Paperclip
PCP_BASE  = "https://paperclip-production-83f5.up.railway.app"

# Each company requires its own Molty token (different agent registrations per company)
PCP_COMPANIES = {
    "4d845c5e-5c36-4fc5-827d-5a577e683cdb": {
        "name": "TMNT",
        "token": "pcp_5c66968515127b7b30f95a688a8477955f197666c7cfafbe",
        "agent_id": "0e4e3ca3-0cc0-4370-83ea-2e82fbf3ee1d",
    },
    "bd625bc3-1268-4b0f-a591-06bf06ca8d27": {
        "name": "Brinc",
        "token": "pcp_04dac50473349650e58d3d6cf68447e318c2fb4ec21325a4",
        "agent_id": "d46b6609-f79d-4313-802c-0b64c3c1c969",
    },
    "722bc707-271b-43be-a073-059270e031d2": {
        "name": "Cerebro",
        "token": "pcp_afd6a737d85638e3ecf1b01ec5fb672785128e03fccd2ea0",
        "agent_id": "ff8f1f31-f3eb-44c6-9cd8-a892c61d72fc",
    },
}

TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}
NH = {"Authorization": f"Bearer {NOTION_KEY}", "Notion-Version": "2022-06-28",
      "Content-Type": "application/json"}

# Overnight window: last 10 hours
OVERNIGHT_WINDOW_HOURS = 10

# Todoist project IDs (REG-036: personal without 🦎 = Guillermo's)
PERSONAL_PROJECT_ID = "6M5rpGfw5jR9Qg9R"

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
    for c in candidates:
        c_clean = re.sub(r'\s*—\s*\d+\w+\+?\s*🦎\s*$', '', c).strip().lower()
        score = difflib.SequenceMatcher(None, q, c_clean).ratio()
        if score > best_score:
            best_score, best = score, c
    return (best, best_score) if best_score >= threshold else (None, 0)

# ── Paperclip: fetch done issues from overnight window ────────────────────────

def get_overnight_done_issues():
    """Fetch Paperclip issues completed within the overnight window across all companies."""
    cutoff = NOW - timedelta(hours=OVERNIGHT_WINDOW_HOURS)
    cutoff_iso = cutoff.isoformat()
    all_done = []

    for company_id, info in PCP_COMPANIES.items():
        company_name = info["name"]
        token = info["token"]
        agent_id = info["agent_id"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            url = f"{PCP_BASE}/api/companies/{company_id}/issues?assigneeAgentId={agent_id}&status=done"
            issues = http_get(url, headers)
            if not isinstance(issues, list):
                log(f"  ⚠️ Paperclip ({company_name}) returned unexpected format: {type(issues)}")
                continue

            # Filter to issues completed in the overnight window
            recent = []
            for issue in issues:
                completed_at = issue.get("completedAt") or issue.get("updatedAt") or ""
                if completed_at and completed_at >= cutoff_iso:
                    issue["_company"] = company_name
                    recent.append(issue)

            log(f"  Paperclip ({company_name}): {len(issues)} done total, {len(recent)} in overnight window")
            all_done.extend(recent)
        except Exception as e:
            log(f"  ⚠️ Paperclip ({company_name}) fetch failed: {e}")

    return all_done

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

def sync_to_todoist(done_issues, open_todoist_tasks):
    """Close Todoist tasks that Paperclip marked done overnight. Returns list of closed task titles."""
    closed = []
    todoist_contents = [t.get("content", "") for t in open_todoist_tasks]

    for issue in done_issues:
        title = issue.get("title", "")
        match, score = fuzzy_match(title, todoist_contents)
        if match:
            for t in open_todoist_tasks:
                if t.get("content", "") == match:
                    # REG-036: Personal tasks without 🦎 are Guillermo's — DO NOT TOUCH
                    if t.get("project_id") == PERSONAL_PROJECT_ID and "🦎" not in t.get("content", ""):
                        log(f"  ⏭ Skipped (personal task, no 🦎): {match[:60]}")
                        break

                    created = t.get("created_at", "")
                    if score >= 0.75 or created >= YESTERDAY:
                        ok = close_todoist_task(t["id"])
                        if ok:
                            closed.append(f"{match[:60]} (score: {score:.0%})")
                            log(f"  ✅ Todoist closed: {match[:60]} [PCP: {title[:50]}] ({score:.0%})")
                        else:
                            log(f"  ⚠️ Todoist close failed: {match[:60]}")
                    else:
                        log(f"  ⏭ Skipped (old task, low score): {match[:60]} ({score:.0%})")
                    break

    return closed

# ── Notion: update standup DB rows ───────────────────────────────────────────

def get_standup_rows_for_date(standup_date: str):
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
    title_prop = row.get("properties", {}).get("Task", {})
    parts = title_prop.get("title", [])
    return "".join(p.get("plain_text", "") for p in parts).strip()

def get_row_action(row):
    action_prop = row.get("properties", {}).get("Action", {})
    sel = action_prop.get("select")
    return sel.get("name") if sel else None

def mark_notion_row_done(page_id: str):
    body = {
        "properties": {
            "Action": {"select": {"name": "✔️ Done"}}
        }
    }
    resp = http_patch(f"https://api.notion.com/v1/pages/{page_id}", NH, body)
    return bool(resp.get("id"))

def sync_to_notion(done_issues, standup_rows):
    updated = []
    row_titles = [get_row_title(r) for r in standup_rows]

    for issue in done_issues:
        title = issue.get("title", "")
        match, score = fuzzy_match(title, row_titles)
        if match:
            for row in standup_rows:
                if get_row_title(row) == match:
                    current_action = get_row_action(row)
                    if current_action in ("✔️ Done", "🗑️ Drop", "📦 Archive"):
                        log(f"  ⏭ Notion row already actioned ({current_action}): {match[:50]}")
                        break
                    ok = mark_notion_row_done(row["id"])
                    if ok:
                        updated.append(f"{match[:60]} (score: {score:.0%})")
                        log(f"  ✅ Notion row → Done: {match[:60]} [PCP: {title[:50]}] ({score:.0%})")
                    else:
                        log(f"  ⚠️ Notion update failed: {match[:60]}")
                    break

    return updated

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log(f"overnight_sync — {TODAY} {NOW.strftime('%H:%M')} HKT")
    log(f"Source: Paperclip (MC deprecated)")
    log(f"Overnight window: last {OVERNIGHT_WINDOW_HOURS} hours (cutoff: {(NOW - timedelta(hours=OVERNIGHT_WINDOW_HOURS)).strftime('%H:%M')} HKT)")
    log(f"Syncing against standup date: {YESTERDAY}\n")

    # 1. Fetch Paperclip done issues from overnight window
    log("1. Fetching Paperclip overnight completions...")
    done_issues = get_overnight_done_issues()

    if not done_issues:
        log("  Nothing completed overnight — nothing to sync.")
        flush_log()
        return 0

    for issue in done_issues:
        log(f"  • [{issue.get('_company','?')}] [{issue.get('identifier','?')}] "
            f"{issue.get('title','?')[:60]} (completed: {issue.get('completedAt', issue.get('updatedAt', '?'))})")

    # 2. Fetch open Todoist tasks
    log("\n2. Fetching open Todoist tasks...")
    todoist_tasks = get_open_todoist_tasks()
    log(f"  {len(todoist_tasks)} open tasks")

    # 3. Sync to Todoist
    log("\n3. Closing completed tasks in Todoist...")
    closed = sync_to_todoist(done_issues, todoist_tasks)

    # 4. Fetch Notion standup rows
    log(f"\n4. Fetching Notion standup rows for {YESTERDAY}...")
    standup_rows = get_standup_rows_for_date(YESTERDAY)

    # 5. Sync to Notion
    log("\n5. Updating Notion standup rows...")
    updated_notion = sync_to_notion(done_issues, standup_rows)

    # 6. Summary
    log(f"\n── Summary ──────────────────────────────────")
    log(f"  Paperclip issues done overnight: {len(done_issues)}")
    log(f"  Todoist tasks closed:            {len(closed)}")
    log(f"  Notion rows marked done:         {len(updated_notion)}")
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
