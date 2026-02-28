#!/data/workspace/.venv/bin/python3
"""
process_standup.py — Standup Completion Handler

Run this after Guillermo finishes filling in the daily standup.
It finds today's standup page, reads actions, and executes them:

  🔀 Delegate  → move Todoist task to Molty's Den
  ✅ Keep       → book a calendar slot for Guillermo
  ❌ Drop       → close/delete the Todoist task

Usage:
  python3 process_standup.py             # processes today's standup
  python3 process_standup.py 2026-02-24  # processes a specific date
"""

import json, os, sys, time, urllib.parse, urllib.request, difflib
from datetime import datetime, timedelta, timezone
from typing import Optional

# === CONFIG ===
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "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")
TODOIST_TOKEN  = os.environ.get("TODOIST_API_TOKEN", "9a26743814658c9e82d92aa716b46a9b0a2257c4")
STANDUP_DB_ID  = "2fe39dd69afd81f189f7e58925dad602"
MOLTY_DEN_ID   = "6fwH32grqrCJF23R"
BRINC_ID       = "6M5rpGgV6q865hrX"
CEREBRO_ID     = "6g53F7ccF8HHjgXM"
BRINC_CAL_ID   = "guillermo.ginesta@brinc.io"
PERSONAL_CAL_ID = "guillermo.ginesta@gmail.com"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8292515315:AAETOvDJgl4r13qF3_32qhpn8h7jIOVJQDA")
TELEGRAM_CHAT_ID   = "1097408992"

HKT = timezone(timedelta(hours=8))
NH = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}

PROJECT_MAP = {
    "6M5rpCXmg7x7RC2Q": "Inbox 📥",
    "6M5rpGfw5jR9Qg9R": "Personal 🙂",
    "6M5rpGgV6q865hrX": "Brinc 🔴",
    "6Rr9p6MxWHFwHXGC": "Mana Capital 🟠",
    "6fwH32grqrCJF23R": "Molty's Den 🦎",
    "6g53F7ccF8HHjgXM": "Cerebro 🔵",
    "6fx5GV7Q93Hp4QgM": "Ideas 💡",
}

# Calendar IDs by task type
BRINC_PROJECTS = {"6M5rpGgV6q865hrX"}
PERSONAL_PROJECTS = {"6M5rpGfw5jR9Qg9R", "6Rr9p6MxWHFwHXGC"}

# Task time estimates
TIME_EST_MAP = {
    "30min": 30, "1h": 60, "2h+": 120,
}

# ─────────────────── HTTP helpers ───────────────────

def notion_get(path):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", headers=NH)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def notion_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", data=data, method="POST", headers=NH)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def todoist_get(path):
    req = urllib.request.Request(f"https://api.todoist.com/api/v1{path}", headers=TH)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def todoist_post(path, body=None, method="POST"):
    data = json.dumps(body).encode() if body else None
    h = {**TH, "Content-Type": "application/json"}
    req = urllib.request.Request(f"https://api.todoist.com/api/v1{path}", data=data, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        return json.loads(raw) if raw.strip() else {}

def todoist_delete(path):
    req = urllib.request.Request(f"https://api.todoist.com/api/v1{path}", method="DELETE", headers=TH)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status

def send_telegram(msg):
    body = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=body, method="POST",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Telegram error: {e}")

# ─────────────────── Calendar helpers ───────────────────

def get_sa_token():
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_file(
        "/data/workspace/credentials/google-service-account.json",
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    creds.refresh(Request())
    return creds.token

def cal_get(token, cal_id, start_iso, end_iso):
    encoded = urllib.parse.quote(cal_id, safe="")
    url = (f"https://www.googleapis.com/calendar/v3/calendars/{encoded}/events"
           f"?timeMin={urllib.parse.quote(start_iso)}&timeMax={urllib.parse.quote(end_iso)}"
           f"&singleEvents=true&orderBy=startTime&maxResults=50")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read()).get("items", [])

def cal_create(token, cal_id, summary, start_iso, end_iso, description=""):
    encoded = urllib.parse.quote(cal_id, safe="")
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso, "timeZone": "Asia/Hong_Kong"},
        "end":   {"dateTime": end_iso,   "timeZone": "Asia/Hong_Kong"},
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]}
    }
    data = json.dumps(event).encode()
    req = urllib.request.Request(
        f"https://www.googleapis.com/calendar/v3/calendars/{encoded}/events",
        data=data, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read())
        return resp.get("htmlLink", "")

def get_busy_slots(token, cal_ids, day):
    """Return list of (start_dt, end_dt) tuples for the given day across all calendars."""
    busy = []
    day_start = datetime(day.year, day.month, day.day, 0, 0, tzinfo=HKT).isoformat()
    day_end   = datetime(day.year, day.month, day.day, 23, 59, tzinfo=HKT).isoformat()
    for cal_id in cal_ids:
        try:
            events = cal_get(token, cal_id, day_start, day_end)
            for e in events:
                s = e.get("start", {}).get("dateTime")
                en = e.get("end", {}).get("dateTime")
                if s and en:
                    busy.append((datetime.fromisoformat(s), datetime.fromisoformat(en)))
        except Exception as ex:
            print(f"  Warning: cal_get failed for {cal_id}: {ex}")
    return sorted(busy)

def find_free_slot(token, cal_ids, duration_min, start_from_dt):
    """Find the next free slot of `duration_min` minutes starting from start_from_dt.
    Searches 7 days ahead. Work hours: 09:00-18:00 HKT. Min slot: 30m."""
    dur = timedelta(minutes=duration_min)
    WORK_START = 9   # 09:00
    WORK_END   = 18  # 18:00

    current = start_from_dt
    for _ in range(7):
        day = current.date()
        # Skip weekends
        if day.weekday() >= 5:
            current = datetime(day.year, day.month, day.day, WORK_START, 0, tzinfo=HKT) + timedelta(days=1)
            continue

        day_dt = datetime(day.year, day.month, day.day, tzinfo=HKT)
        slot_start = max(current, day_dt.replace(hour=WORK_START))
        day_end_dt  = day_dt.replace(hour=WORK_END)

        busy = get_busy_slots(token, cal_ids, day_dt)

        # Walk through the day looking for a gap
        while slot_start + dur <= day_end_dt:
            slot_end = slot_start + dur
            conflict = any(s < slot_end and en > slot_start for s, en in busy)
            if not conflict:
                return slot_start, slot_end
            # Jump to end of conflicting event
            for s, en in busy:
                if s < slot_end and en > slot_start:
                    slot_start = en
                    break

        # Move to next day
        current = datetime(day.year, day.month, day.day, WORK_START, 0, tzinfo=HKT) + timedelta(days=1)

    return None, None  # No slot found in 7 days

# ─────────────────── Notion helpers ───────────────────

def find_todays_standup(target_date: str) -> Optional[str]:
    """Query STANDUP_DB for today's page. Returns page_id or None."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    # Title format: "Tue Feb 24, 2026 — 5PM HKT"
    day_label = dt.strftime("%a %b %-d")  # e.g. "Tue Feb 24"
    year_str  = dt.strftime("%Y")          # e.g. "2026"

    body = {
        "sorts": [{"timestamp": "created_time", "direction": "descending"}],
        "page_size": 30
    }
    try:
        resp = notion_post(f"/databases/{STANDUP_DB_ID}/query", body)
        pages = resp.get("results", [])
        candidates = []
        for page in pages:
            title_parts = page.get("properties", {}).get("Date", {}).get("title", [])
            title = "".join(p.get("plain_text", "") for p in title_parts)
            if day_label in title and year_str in title:
                candidates.append(page)
        if not candidates:
            print(f"  No page found matching '{day_label}, {year_str}'")
            return None
        # Prefer most recently created
        return candidates[0]["id"]
    except Exception as e:
        print(f"  Error finding standup page: {e}")
    return None

def get_child_databases(page_id: str) -> dict:
    """Return dict of {title: db_id} for all child databases on a page."""
    dbs = {}
    try:
        resp = notion_get(f"/blocks/{page_id}/children?page_size=50")
        for block in resp.get("results", []):
            if block.get("type") == "child_database":
                title = block.get("child_database", {}).get("title", "")
                dbs[title] = block["id"]
    except Exception as e:
        print(f"  Error getting child databases: {e}")
    return dbs

def query_database(db_id: str) -> list:
    """Return all rows from a Notion database."""
    try:
        resp = notion_post(f"/databases/{db_id}/query", {})
        return resp.get("results", [])
    except Exception as e:
        print(f"  Error querying database {db_id}: {e}")
        return []

def get_text(prop) -> str:
    if not prop:
        return ""
    if prop.get("type") == "title":
        return "".join(p.get("plain_text", "") for p in prop.get("title", []))
    if prop.get("type") == "rich_text":
        return "".join(p.get("plain_text", "") for p in prop.get("rich_text", []))
    if prop.get("type") == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    return ""

# ─────────────────── Todoist helpers ───────────────────

def get_all_tasks() -> list:
    try:
        resp = todoist_get("/tasks?limit=200")
        return resp.get("results", resp) if isinstance(resp, dict) else resp
    except Exception as e:
        print(f"  Error fetching tasks: {e}")
        return []

def find_todoist_task(tasks: list, title: str) -> Optional[dict]:
    """Fuzzy-match a Notion task title to a Todoist task. Returns best match or None."""
    if not title or not tasks:
        return None
    # Normalize: strip emoji, lowercase
    def norm(s):
        import re
        return re.sub(r'[^\w\s]', '', s.lower()).strip()
    norm_title = norm(title)
    best_score = 0
    best_task = None
    for t in tasks:
        score = difflib.SequenceMatcher(None, norm_title, norm(t.get("content", ""))).ratio()
        if score > best_score:
            best_score = score
            best_task = t
    if best_score >= 0.55:
        return best_task
    return None

def move_task_to_project(task_id: str, project_id: str) -> bool:
    try:
        url = f"https://api.todoist.com/api/v1/tasks/{task_id}/move"
        body = json.dumps({"project_id": project_id}).encode()
        h = {**TH, "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, method="POST", headers=h)
        with urllib.request.urlopen(req, timeout=10) as r:
            _ = r.read()  # may be empty
            return True
    except Exception as e:
        print(f"  Error moving task {task_id}: {e}")
        return False

def close_task(task_id: str) -> bool:
    try:
        req = urllib.request.Request(
            f"https://api.todoist.com/api/v1/tasks/{task_id}/close",
            method="POST", headers=TH
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 204
    except Exception as e:
        print(f"  Error closing task {task_id}: {e}")
        return False

# ─────────────────── Time estimate helper ───────────────────

def estimate_duration(title: str) -> int:
    """Return estimated duration in minutes based on task title keywords."""
    t = title.lower()
    if any(w in t for w in ["research", "investigate", "analyze", "review", "write", "build", "implement"]):
        return 60
    if any(w in t for w in ["call", "email", "send", "reply", "check", "fill", "complete"]):
        return 45
    return 30

def pick_calendar(task_title: str, project_id: str) -> str:
    """Return the right calendar ID based on project."""
    if project_id in BRINC_PROJECTS:
        return BRINC_CAL_ID
    return PERSONAL_CAL_ID

# ─────────────────── MAIN LOGIC ───────────────────

def process(target_date: str):
    now = datetime.now(HKT)
    print(f"\n🚀 Processing standup for {target_date}...\n")

    # 1. Find today's standup page (state file first, then Notion query)
    print("1. Finding standup page...")
    page_id = db1_id_hint = db2_id_hint = None

    state_path = "/data/workspace/logs/standup-state.json"
    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)
        if state.get("date") == target_date:
            page_id     = state.get("page_id")
            db1_id_hint = state.get("db1_id")
            db2_id_hint = state.get("db2_id")
            print(f"   Found via state file: {page_id}")

    if not page_id:
        page_id = find_todays_standup(target_date)

    if not page_id:
        msg = f"❌ Couldn't find standup page for {target_date}. Has it been created yet?"
        print(msg)
        send_telegram(msg)
        return

    page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
    print(f"   Page: {page_url}")

    # 2. Get child databases (use hints from state file if available)
    print("2. Finding child databases...")
    dbs = {}
    if db1_id_hint and db2_id_hint:
        dbs = {"🔥 Needs Your Input": db1_id_hint, "📋 Active Pipeline": db2_id_hint}
        print(f"   Using state file DB IDs")
    else:
        dbs = get_child_databases(page_id)
    print(f"   DBs found: {list(dbs.keys())}")

    needs_input_db = next((v for k, v in dbs.items() if "Input" in k or "input" in k), None)
    pipeline_db    = next((v for k, v in dbs.items() if "Pipeline" in k or "pipeline" in k), None)

    if not needs_input_db:
        send_telegram("❌ Could not find 'Needs Your Input' table on today's standup page.")
        return

    # 3. Load all Todoist tasks (active + recently completed, for matching)
    print("3. Loading Todoist tasks...")
    all_tasks = get_all_tasks()
    print(f"   {len(all_tasks)} active tasks loaded")

    # Also fetch recently completed tasks (last 7 days) to avoid re-creating finished work
    completed_tasks = []
    try:
        since = (datetime.now(HKT) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
        resp = todoist_get(f"/tasks/completed/get_all?limit=50&since={urllib.parse.quote(since)}")
        completed_tasks = resp.get("items", resp) if isinstance(resp, dict) else resp
        print(f"   {len(completed_tasks)} completed tasks loaded (last 7 days)")
    except Exception as e:
        print(f"   Warning: couldn't fetch completed tasks: {e}")

    all_tasks_for_matching = all_tasks + completed_tasks

    # 4. Process "Needs Your Input" table
    print("4. Processing 'Needs Your Input'...")
    rows = query_database(needs_input_db)

    routed_molty, routed_raphael, routed_leonardo = [], [], []
    kept, dropped, unmatched = [], [], []

    cal_token = None  # lazy-load
    cal_bookings = []

    # Deduplication: track seen titles so rows appearing in multiple DB sections
    # (Needs Input + Active Pipeline) don't get processed twice
    seen_titles = set()

    for row in rows:
        props = row.get("properties", {})
        title      = get_text(props.get("Task"))
        action     = get_text(props.get("Action"))
        your_notes = get_text(props.get("Your Notes"))
        owner      = get_text(props.get("Owner"))
        project    = get_text(props.get("Project"))

        if not title:
            continue

        # Deduplication — skip if we've already processed this title
        title_key = title.lower().strip()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        # If no Action set, infer from Your Notes before skipping
        if not action and your_notes:
            notes_lower = your_notes.lower()
            if any(x in notes_lower for x in ["mark as done", "already done", "this is done", "already told you", "completed", "i did this", "we're not using", "not using it", "decided no", "cancel", "drop this"]):
                action = "Drop"
                print(f"   [Drop — inferred from Your Notes] {title[:60]}: \"{your_notes[:80]}\"")
            elif any(x in notes_lower for x in ["molty", "delegate", "for molty"]):
                action = "Molty"
                print(f"   [Molty — inferred from Your Notes] {title[:60]}")
            elif any(x in notes_lower for x in ["raphael", "for raphael"]):
                action = "Raphael"
                print(f"   [Raphael — inferred from Your Notes] {title[:60]}")
            elif any(x in notes_lower for x in ["leonardo", "for leonardo"]):
                action = "Leonardo"
                print(f"   [Leonardo — inferred from Your Notes] {title[:60]}")

        if not action:
            continue

        print(f"   [{action}] {title[:60]}")

        # Match to Todoist task — check active first, then completed
        matched = find_todoist_task(all_tasks, title)
        matched_completed = None if matched else find_todoist_task(completed_tasks, title)

        # Determine routing target
        route_target = None
        route_project_id = None
        route_label = None
        if "Molty" in action or "🦎" in action or "Delegate" in action:
            route_target = routed_molty
            route_project_id = MOLTY_DEN_ID
            route_label = "Molty's Den"
        elif "Raphael" in action or "🔴" in action:
            route_target = routed_raphael
            route_project_id = BRINC_ID
            route_label = "Brinc (Raphael)"
        elif "Leonardo" in action or "🔵" in action:
            route_target = routed_leonardo
            route_project_id = CEREBRO_ID
            route_label = "Cerebro (Leonardo)"

        if route_target is not None:
            # Build a prefixed title so Guillermo can see it was processed
            PREFIX_MAP = {
                "Molty's Den": "🦎",
                "Brinc (Raphael)": "🔴",
                "Cerebro (Leonardo)": "🔵",
            }
            prefix = PREFIX_MAP.get(route_label, "")
            # Strip existing agent prefix if present (avoid double-prefixing)
            clean_title = title
            for p in ["🦎 ", "🔴 ", "🔵 "]:
                if clean_title.startswith(p):
                    clean_title = clean_title[len(p):]
            new_title = f"{prefix} {clean_title}".strip() if prefix else clean_title

            if matched:
                ok = move_task_to_project(matched["id"], route_project_id)
                if ok:
                    try:
                        todoist_post(f"/tasks/{matched['id']}", {"content": new_title}, method="POST")
                        print(f"     ✏️ Title updated: {new_title[:60]}")
                    except Exception as e:
                        print(f"     ⚠️ Title update failed: {e}")
                    route_target.append(new_title)
                    print(f"     ✅ Moved to {route_label}: {matched['id']}")
                else:
                    unmatched.append(f"{title} (move failed)")
            elif matched_completed:
                # Already completed — don't recreate. Just log it.
                print(f"     ⏭️ Already completed in Todoist — skipping creation")
                dropped.append(f"{title} (already completed by {matched_completed.get('responsible_uid', 'agent')})")
            else:
                # Genuinely new task — create in target project
                try:
                    body = {"content": new_title, "project_id": route_project_id}
                    todoist_post("/tasks", body)
                    route_target.append(new_title)
                    print(f"     ✅ Created in {route_label} (new task)")
                except Exception as e:
                    unmatched.append(f"{title} (create failed: {e})")

        elif "Drop" in action:
            if matched:
                ok = close_task(matched["id"])
                dropped.append(title)
                print(f"     🗑️ Closed: {matched['id']}")
            else:
                dropped.append(f"{title} (not found in Todoist)")

        elif "Done" in action:
            if matched:
                # Mark title as confirmed done so Guillermo can see it was processed
                new_title = f"✅ {title}" if not title.startswith("✅") else title
                try:
                    todoist_post(f"/tasks/{matched['id']}", {"content": new_title}, method="POST")
                    close_task(matched["id"])
                    print(f"     ✅ Marked done + title updated: {new_title[:60]}")
                except Exception as e:
                    print(f"     ⚠️ Done update failed: {e}")
                dropped.append(new_title)
            else:
                dropped.append(f"{title} (not found in Todoist — marked done in standup only)")

        elif "Reschedule" in action:
            # Extract new date from Your Notes (look for YYYY-MM-DD or "March 2" style)
            import re
            new_date = None
            # Try ISO date
            iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", your_notes)
            if iso_match:
                new_date = iso_match.group(1)
            else:
                # Try "Month Day" style e.g. "March 2", "Mar 2"
                month_match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})", your_notes, re.IGNORECASE)
                if month_match:
                    try:
                        new_date = datetime.strptime(f"{month_match.group(1)} {month_match.group(2)} {now.year}", "%b %d %Y").strftime("%Y-%m-%d")
                    except Exception:
                        pass
            if new_date and matched:
                try:
                    todoist_post(f"/tasks/{matched['id']}", {"due_date": new_date}, method="POST")
                    new_title = f"📅 {title}" if not title.startswith("📅") else title
                    todoist_post(f"/tasks/{matched['id']}", {"content": new_title}, method="POST")
                    kept.append(f"{title} → rescheduled to {new_date}")
                    print(f"     📅 Rescheduled to {new_date}: {matched['id']}")
                except Exception as e:
                    unmatched.append(f"{title} (reschedule failed: {e})")
            elif new_date:
                kept.append(f"{title} → rescheduled to {new_date} (no Todoist match)")
                print(f"     ⚠️ Reschedule: no Todoist match for '{title[:50]}'")
            else:
                unmatched.append(f"{title} (reschedule: no date found in notes — '{your_notes[:60]}')")
                print(f"     ⚠️ Reschedule: no date found in notes for '{title[:50]}'")

        elif "Keep" in action and ("Guillermo" in owner or not owner):
            # Book calendar slot
            dur = estimate_duration(title)
            # Pick calendar: Brinc vs Personal based on project name
            cal_id = BRINC_CAL_ID if any(w in project for w in ["Brinc", "Mana", "Cerebro"]) else PERSONAL_CAL_ID
            cal_ids = [BRINC_CAL_ID, PERSONAL_CAL_ID]  # check both when finding free slot

            try:
                if cal_token is None:
                    cal_token = get_sa_token()
                    print(f"   Calendar token: OK")

                # Start searching from tomorrow 09:00
                search_from = datetime(now.year, now.month, now.day, 9, 0, tzinfo=HKT) + timedelta(days=1)
                slot_start, slot_end = find_free_slot(cal_token, cal_ids, dur, search_from)

                if slot_start:
                    label = f"🗓️ {title[:60]}"
                    link = cal_create(
                        cal_token, cal_id, label,
                        slot_start.isoformat(), slot_end.isoformat(),
                        description=f"Task from standup {target_date}. Duration: {dur}min."
                    )
                    day_label = slot_start.strftime("%a %b %-d")
                    time_label = f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                    cal_bookings.append(f"{day_label} {time_label} — {title[:50]}")
                    # Update title to show it was scheduled
                    if matched:
                        new_title = f"📅 {title}" if not title.startswith("📅") else title
                        try:
                            todoist_post(f"/tasks/{matched['id']}", {"content": new_title}, method="POST")
                        except Exception:
                            pass
                    kept.append(title)
                    print(f"     📅 Booked: {day_label} {time_label}")
                else:
                    kept.append(f"{title} (no slot found in 7 days)")
                    print(f"     ⚠️ No free slot found in 7 days for: {title[:40]}")
            except Exception as e:
                kept.append(title)
                print(f"     ⚠️ Calendar booking failed: {e}")

        else:
            # Keep with no calendar booking needed (Molty tasks, etc.)
            # Still update title so Guillermo sees it was processed
            if matched:
                new_title = f"👀 {title}" if not any(title.startswith(p) for p in ["👀","🦎","🔴","🔵","✅","📅","🗑️"]) else title
                try:
                    todoist_post(f"/tasks/{matched['id']}", {"content": new_title}, method="POST")
                except Exception:
                    pass
            kept.append(title)

    # 5. Build Telegram summary
    print("\n5. Sending summary...")
    lines = [f"✅ *Standup Processed — {target_date}*", f"[View page]({page_url})\n"]

    if routed_molty:
        lines.append(f"🦎 *→ Molty's Den ({len(routed_molty)}):*")
        for t in routed_molty:
            lines.append(f"  • {t[:70]}")
    if routed_raphael:
        lines.append(f"\n🔴 *→ Raphael / Brinc ({len(routed_raphael)}):*")
        for t in routed_raphael:
            lines.append(f"  • {t[:70]}")
    if routed_leonardo:
        lines.append(f"\n🔵 *→ Leonardo / Cerebro ({len(routed_leonardo)}):*")
        for t in routed_leonardo:
            lines.append(f"  • {t[:70]}")

    if dropped:
        lines.append(f"\n🗑️ *Dropped ({len(dropped)}):*")
        for t in dropped:
            lines.append(f"  • {t[:70]}")

    if cal_bookings:
        lines.append(f"\n📅 *Calendar blocks booked ({len(cal_bookings)}):*")
        for b in cal_bookings:
            lines.append(f"  • {b}")

    if unmatched:
        lines.append(f"\n⚠️ *Couldn't match ({len(unmatched)}):*")
        for t in unmatched:
            lines.append(f"  • {t[:70]}")

    if not routed_molty and not routed_raphael and not routed_leonardo and not dropped and not cal_bookings:
        lines.append("_Nothing to process — no Delegate/Drop/Keep actions found yet._")
        lines.append("_Fill in the Action column in Notion, then run again._")

    msg = "\n".join(lines)
    print(msg)
    send_telegram(msg)
    print("\nDone.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = datetime.now(HKT).strftime("%Y-%m-%d")
    process(target)
