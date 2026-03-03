#!/data/workspace/.venv/bin/python3
"""
process_standup.py — Standup Completion Handler v2.1 (redesigned 2026-03-03)

Run after Guillermo says "standup done". Processes the Notion standup page:

  Tomorrow's Focus callout → book as calendar event (first free slot tomorrow)
  Action = Done/Drop       → close in Todoist + MC + Notion
  Action = Reschedule      → update Todoist due date (parse from Your Notes)
  Owner = Raphael/Leonardo → move Todoist task + webhook agent with context
  In MC? = ticked          → create/update MC task (deduplicate first)
  Book Calendar? = ticked  → book focus block (5-day horizon, check both cals)

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

# Mission Control
MC_API_URL = "https://resilient-chinchilla-241.convex.site"
MC_TOKEN   = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
MC_HDR     = {"Authorization": f"Bearer {MC_TOKEN}", "Content-Type": "application/json"}

# Todoist project IDs
MANA_ID    = "6Rr9p6MxWHFwHXGC"
PERSONAL_ID = "6M5rpGfw5jR9Qg9R"

# Webhook endpoints for agents
WEBHOOK_URLS   = {
    "raphael":  "https://ggv-raphael.up.railway.app/hooks/agent",
    "leonardo": "https://leonardo-production.up.railway.app/hooks/agent",
}
WEBHOOK_TOKENS = {
    "raphael":  "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd",
    "leonardo": "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758",
}

# Todoist project → MC project name
PROJECT_TO_MC = {
    "6M5rpGgV6q865hrX": "brinc",
    "6g53F7ccF8HHjgXM": "cerebro",
    "6Rr9p6MxWHFwHXGC": "mana",
    "6fwH32grqrCJF23R": "fleet",
    "6M5rpGfw5jR9Qg9R": "personal",
    "6M5rpCXmg7x7RC2Q": "personal",
}

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

# ─────────────────── Mission Control helpers ───────────────────

def mc_get_tasks():
    """Fetch all open MC tasks."""
    try:
        req = urllib.request.Request(f"{MC_API_URL}/api/tasks", headers=MC_HDR)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"  ⚠️ MC fetch failed: {e}")
        return []

def mc_fuzzy_match(tasks, title, threshold=0.55):
    """Find existing MC task by fuzzy title match. Returns task or None."""
    title_norm = title.lower().strip()
    best_score, best_task = 0, None
    for t in tasks:
        if t.get("status") in ("done",):
            continue
        score = difflib.SequenceMatcher(None, title_norm, t.get("title", "").lower().strip()).ratio()
        if score > best_score:
            best_score, best_task = score, t
    return best_task if best_score >= threshold else None

def mc_create_task(title, project, priority_str, assignee, due_date, description):
    """Create a new MC task. Returns task id or None."""
    # Map Notion priority to MC priority
    prio_map = {"🔴 P1": "p1", "🟡 P2": "p2", "🔵 P3": "p3", "⚪ P4": "p4"}
    mc_prio = prio_map.get(priority_str, "p2")
    # Map owner to MC assignee id
    owner_map = {"Guillermo": "guillermo", "Molty": "molty", "Raphael": "raphael", "Leonardo": "leonardo"}
    mc_assignee = owner_map.get(assignee, "molty")

    payload = {
        "title": title,
        "project": project,
        "priority": mc_prio,
        "assignees": [mc_assignee],
        "createdBy": "molty",
        "status": "assigned",
        "description": description[:2000] if description else "",
    }
    if due_date:
        payload["dueDate"] = due_date

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{MC_API_URL}/api/task", data=data, method="POST", headers=MC_HDR)
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            return resp.get("id") or resp.get("_id")
    except Exception as e:
        print(f"  ⚠️ MC create failed for '{title[:40]}': {e}")
        return None

def mc_update_task(task_id, updates):
    """Update an existing MC task."""
    try:
        payload = {"id": task_id, **updates}
        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{MC_API_URL}/api/task", data=data, method="PATCH", headers=MC_HDR)
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
            return True
    except Exception as e:
        print(f"  ⚠️ MC update failed for {task_id}: {e}")
        return False

def process_in_mc(title, project_id, priority_str, owner, due_date, g_notes, molty_notes, action, mc_tasks):
    """Create or update MC task based on In MC? checkbox. Returns (action_taken, detail)."""
    description = ""
    if g_notes:
        description += f"Guillermo's notes: {g_notes}\n"
    if molty_notes:
        description += f"Molty's notes: {molty_notes}"

    mc_project = PROJECT_TO_MC.get(project_id, "personal")
    existing = mc_fuzzy_match(mc_tasks, title)

    if action in ("✔️ Done", "Done", "🗑️ Drop", "Drop"):
        # Close in MC if exists
        if existing:
            mc_update_task(existing["_id"], {"status": "done"})
            return ("closed", title[:50])
        return ("skipped", f"{title[:50]} (not in MC)")

    if existing:
        # Update existing — don't duplicate
        updates = {"priority": {"🔴 P1": "p1", "🟡 P2": "p2", "🔵 P3": "p3", "⚪ P4": "p4"}.get(priority_str, "p2")}
        if due_date:
            updates["dueDate"] = due_date
        if description:
            updates["description"] = description[:2000]
        mc_update_task(existing["_id"], updates)
        return ("updated", title[:50])
    else:
        # Create new
        task_id = mc_create_task(title, mc_project, priority_str, owner, due_date, description)
        if task_id:
            return ("created", title[:50])
        return ("failed", title[:50])


def dispatch_agent(agent, title, your_notes, molty_notes, due, priority):
    """Webhook an agent with task assignment."""
    note_ctx = f"\nGuillermo's notes: \"{your_notes}\"" if your_notes else ""
    molty_ctx = f"\nMolty's context: \"{molty_notes}\"" if molty_notes else ""
    due_ctx = f"\nDue: {due}" if due else ""
    prio_ctx = f"\nPriority: {priority}" if priority else ""
    msg = (
        f"🦎 Standup dispatch — task assigned to you:\n\n"
        f"**{title}**{prio_ctx}{due_ctx}{note_ctx}{molty_ctx}\n\n"
        f"Pick this up, update MC when started, post results when done."
    )
    data = json.dumps({"message": msg, "wakeMode": "now"}).encode()
    try:
        req = urllib.request.Request(
            WEBHOOK_URLS[agent], data=data, method="POST",
            headers={"Authorization": f"Bearer {WEBHOOK_TOKENS[agent]}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            return resp.get("ok", False)
    except Exception as e:
        print(f"  ⚠️ Webhook to {agent} failed: {e}")
        return False


# ─────────────────── Tomorrow's Focus reader ───────────────────

def read_tomorrows_focus(page_id):
    """Read the Tomorrow's Focus callout block from the standup page.
    Returns the text Guillermo wrote, or None if blank/not found."""
    try:
        req = urllib.request.Request(
            f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=20",
            headers=NH
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            blocks = json.loads(r.read()).get("results", [])

        for block in blocks:
            if block.get("type") != "callout":
                continue
            rich_text = block.get("callout", {}).get("rich_text", [])
            full_text = "".join(t.get("plain_text", "") for t in rich_text)
            # Identify the Tomorrow's Focus callout
            if "Tomorrow's Focus" in full_text or "Tomorrow's Top Priority" in full_text:
                # Strip the header line, get what Guillermo wrote
                lines = full_text.strip().split("\n")
                # Skip header lines (italic hint text + bold header)
                content_lines = [
                    l.strip() for l in lines
                    if l.strip()
                    and "Tomorrow's Focus" not in l
                    and "Tomorrow's Top Priority" not in l
                    and "ONE thing" not in l
                    and "makes tomorrow worthwhile" not in l
                    and "calendar event" not in l
                    and "One item only" not in l
                ]
                if content_lines:
                    return " ".join(content_lines)
        return None
    except Exception as e:
        print(f"  ⚠️ Could not read Tomorrow's Focus: {e}")
        return None


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


def extract_keywords(title: str) -> list[str]:
    """Extract meaningful keywords from a task title for event matching."""
    STOP_WORDS = {
        "the", "a", "an", "to", "for", "of", "in", "on", "at", "by", "with",
        "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "my", "your", "his", "her", "its", "our", "their", "this", "that",
        "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "what", "which", "who", "whom", "whose", "where", "when", "why", "how",
        "all", "each", "every", "both", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
        "very", "just", "also", "now", "then", "once", "here", "there", "up",
        "review", "check", "update", "prepare", "do", "get", "make", "send",
    }
    # Remove emoji prefixes and special chars
    import re
    clean = re.sub(r'^[^\w\s]+', '', title)  # strip leading emoji
    clean = re.sub(r'[^\w\s]', ' ', clean)   # replace special chars with space
    words = clean.lower().split()
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    return keywords[:5]  # Max 5 keywords


def find_related_events(token, cal_ids: list[str], task_title: str, search_days: int = 7) -> list[str]:
    """Search calendar for events with similar keywords in title.
    Returns list of matching event summaries, or empty list."""
    keywords = extract_keywords(task_title)
    if not keywords:
        return []

    now = datetime.now(tz=HKT)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=search_days)).isoformat()

    matches = []
    for cal_id in cal_ids:
        try:
            events = cal_get(token, cal_id, time_min, time_max)
            for e in events:
                summary = (e.get("summary") or "").lower()
                # Check if any keyword matches
                if any(kw in summary for kw in keywords):
                    matches.append(e.get("summary", "(no title)"))
        except Exception as ex:
            print(f"  Warning: find_related_events failed for {cal_id}: {ex}")

    return matches


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
    import re
    now = datetime.now(HKT)
    print(f"\n🚀 Processing standup for {target_date} (v2.1)...\n")

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

    # 2. Get persistent standup DB id from state file
    print("2. Finding standup DB...")
    persistent_db_id = db1_id_hint  # state file has persistent_db_id
    if not persistent_db_id:
        # Fallback: look for child database on the page
        dbs = get_child_databases(page_id)
        persistent_db_id = next(iter(dbs.values()), None) if dbs else None
    if not persistent_db_id:
        send_telegram("❌ Could not find standup DB. Has today's standup been generated?")
        return
    print(f"   DB: {persistent_db_id}")

    # 3. Read Tomorrow's Focus from page
    print("3. Reading Tomorrow's Focus...")
    tomorrows_focus = read_tomorrows_focus(page_id)
    if tomorrows_focus:
        print(f"   Focus: '{tomorrows_focus[:80]}'")
    else:
        print("   No focus written — will warn in summary")

    # 4. Load Todoist tasks + MC tasks for matching/deduplication
    print("4. Loading tasks...")
    all_tasks = get_all_tasks()
    print(f"   Todoist: {len(all_tasks)} active tasks")

    completed_tasks = []
    try:
        since = (datetime.now(HKT) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
        resp = todoist_get(f"/tasks/completed/get_all?limit=50&since={urllib.parse.quote(since)}")
        completed_tasks = resp.get("items", resp) if isinstance(resp, dict) else resp
        print(f"   Todoist completed (7d): {len(completed_tasks)}")
    except Exception as e:
        print(f"   ⚠️ Couldn't fetch completed tasks: {e}")

    mc_tasks = mc_get_tasks()
    print(f"   MC open tasks: {len(mc_tasks)}")

    # 5. Get calendar token (lazy — used for both Tomorrow's Focus and Book Calendar?)
    cal_token = None
    try:
        cal_token = get_sa_token()
        print("5. Calendar token: OK")
    except Exception as e:
        print(f"5. ⚠️ Calendar auth failed: {e}")

    # 6. Book Tomorrow's Focus as calendar event
    focus_booked = None
    if tomorrows_focus and cal_token:
        print(f"6. Booking Tomorrow's Focus...")
        tomorrow_dt = datetime.now(HKT) + timedelta(days=1)
        # Skip weekend — find next weekday
        while tomorrow_dt.weekday() >= 5:
            tomorrow_dt += timedelta(days=1)
        search_from = tomorrow_dt.replace(hour=9, minute=0, second=0, microsecond=0)
        cal_ids = [BRINC_CAL_ID, PERSONAL_CAL_ID]
        # Determine which calendar based on keywords
        focus_lower = tomorrows_focus.lower()
        target_cal = BRINC_CAL_ID if any(w in focus_lower for w in ["brinc", "raphael", "proposal", "helm", "client", "deal"]) else PERSONAL_CAL_ID

        dur = estimate_duration(tomorrows_focus)
        slot_start, slot_end = find_free_slot(cal_token, cal_ids, dur, search_from)
        if slot_start:
            try:
                cal_create(
                    cal_token, target_cal,
                    f"🎯 {tomorrows_focus[:80]}",
                    slot_start.isoformat(), slot_end.isoformat(),
                    description=f"Tomorrow's Focus from standup {target_date}.\nSet by Guillermo."
                )
                day_fmt = slot_start.strftime("%a %b %-d")
                time_fmt = f"{slot_start.strftime('%H:%M')}–{slot_end.strftime('%H:%M')}"
                focus_booked = f"{day_fmt} {time_fmt}: {tomorrows_focus[:60]}"
                print(f"   ✅ Booked: {focus_booked}")
            except Exception as e:
                print(f"   ⚠️ Calendar create failed: {e}")
    elif not tomorrows_focus:
        print("6. Skipping — Tomorrow's Focus not filled in")

    # 7. Process all rows from the standup DB
    print("7. Processing standup rows...")
    rows = query_database(persistent_db_id)
    # Filter to today's rows only
    rows = [r for r in rows if (r.get("properties", {}).get("Standup Date", {}).get("date") or {}).get("start", "") == target_date]
    print(f"   Rows for {target_date}: {len(rows)}")

    closed, rescheduled, routed_raphael, routed_leonardo, routed_molty = [], [], [], [], []
    mc_created, mc_updated, mc_closed = [], [], []
    cal_bookings, unmatched = [], []
    seen_titles = set()

    for row in rows:
        props = row.get("properties", {})
        title       = get_text(props.get("Task"))
        action      = get_text(props.get("Action"))
        owner       = get_text(props.get("Owner"))
        your_notes  = get_text(props.get("Your Notes"))
        molty_notes = get_text(props.get("Molty's Notes"))
        priority    = get_text(props.get("Priority"))
        project_disp = get_text(props.get("Project"))
        time_est    = get_text(props.get("Time Est."))
        in_mc       = props.get("In MC?", {}).get("checkbox", False)
        book_cal    = props.get("Book Calendar?", {}).get("checkbox", False)
        due_date    = (props.get("Due Date", {}).get("date") or {}).get("start", "")

        if not title:
            continue
        title_key = title.lower().strip()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        # Check Your Notes for implicit done signals
        if your_notes:
            notes_lower = your_notes.lower()
            done_phrases = ["mark as done", "already done", "this is done", "completed",
                            "i did this", "already told you", "drop this", "cancel"]
            if any(x in notes_lower for x in done_phrases):
                action = "✔️ Done"

        print(f"  [{action or '—'}] [{owner or '—'}] {title[:55]}")

        matched = find_todoist_task(all_tasks, title)

        # ── 7a. Process Action ──────────────────────────────────
        if action in ("✔️ Done", "Done"):
            if matched:
                close_task(matched["id"])
                print(f"    ✅ Todoist closed")
            closed.append(title[:60])

        elif action in ("🗑️ Drop", "Drop"):
            if matched:
                close_task(matched["id"])
                print(f"    🗑️ Todoist dropped")
            closed.append(f"[dropped] {title[:55]}")

        elif action in ("📅 Reschedule", "Reschedule"):
            new_date = None
            iso_match = re.search(r"(\d{4}-\d{2}-\d{2})", your_notes)
            if iso_match:
                new_date = iso_match.group(1)
            else:
                m = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})", your_notes, re.IGNORECASE)
                if m:
                    try:
                        new_date = datetime.strptime(f"{m.group(1)} {m.group(2)} {now.year}", "%b %d %Y").strftime("%Y-%m-%d")
                    except Exception:
                        pass
            if new_date and matched:
                try:
                    todoist_post(f"/tasks/{matched['id']}", {"due_date": new_date}, method="POST")
                    rescheduled.append(f"{title[:50]} → {new_date}")
                    print(f"    📅 Rescheduled to {new_date}")
                except Exception as e:
                    unmatched.append(f"{title[:50]} (reschedule error: {e})")
            elif not new_date:
                unmatched.append(f"{title[:50]} (reschedule: no date in notes)")

        # ── 7b. Process Owner → routing ──────────────────────────
        owner_route = owner.strip() if owner else ""

        if "Raphael" in owner_route:
            # Move to Brinc project in Todoist
            if matched:
                move_task_to_project(matched["id"], BRINC_ID)
            # Webhook Raphael
            dispatch_agent("raphael", title, your_notes, molty_notes, due_date, priority)
            routed_raphael.append(title[:60])
            print(f"    🔴 Routed to Raphael + dispatched")

        elif "Leonardo" in owner_route:
            # Move to Cerebro project in Todoist
            if matched:
                move_task_to_project(matched["id"], CEREBRO_ID)
            # Webhook Leonardo
            dispatch_agent("leonardo", title, your_notes, molty_notes, due_date, priority)
            routed_leonardo.append(title[:60])
            print(f"    🔵 Routed to Leonardo + dispatched")

        elif "Molty" in owner_route:
            # Move to Molty's Den
            if matched:
                move_task_to_project(matched["id"], MOLTY_DEN_ID)
            routed_molty.append(title[:60])
            print(f"    🦎 Routed to Molty's Den")

        # ── 7c. Process In MC? ────────────────────────────────────
        if in_mc:
            # Get Todoist project_id for MC project mapping
            project_id = matched.get("project_id", "") if matched else ""
            action_taken, detail = process_in_mc(
                title, project_id, priority, owner_route or "Guillermo",
                due_date, your_notes, molty_notes, action, mc_tasks
            )
            if action_taken == "created":
                mc_created.append(detail)
                print(f"    🐢 MC task created")
            elif action_taken == "updated":
                mc_updated.append(detail)
                print(f"    🐢 MC task updated")
            elif action_taken == "closed":
                mc_closed.append(detail)
                print(f"    🐢 MC task closed")

        # ── 7d. Process Book Calendar? ────────────────────────────
        if book_cal and cal_token:
            # Determine duration
            dur_map = {"15min": 15, "30min": 30, "1h": 60, "2h+": 120}
            dur = dur_map.get(time_est, estimate_duration(title))

            # Determine calendar
            brinc_kw = ["brinc", "raphael", "proposal", "helm", "client", "deal", "mana"]
            target_cal = BRINC_CAL_ID if any(w in (project_disp + title).lower() for w in brinc_kw) else PERSONAL_CAL_ID
            cal_ids = [BRINC_CAL_ID, PERSONAL_CAL_ID]

            # Check for existing related event first
            related = find_related_events(cal_token, cal_ids, title, search_days=5)
            if related:
                print(f"    ⏭️ Calendar: related event exists '{related[0][:40]}'")
            else:
                # Find slot within 5 working days
                search_from = datetime(now.year, now.month, now.day, 9, 0, tzinfo=HKT) + timedelta(days=1)
                slot_start, slot_end = find_free_slot(cal_token, cal_ids, dur, search_from)
                if slot_start:
                    try:
                        p_label = priority.split()[-1] if priority else "P2"
                        cal_create(
                            cal_token, target_cal,
                            f"🎯 [{p_label}] {title[:70]}",
                            slot_start.isoformat(), slot_end.isoformat(),
                            description=f"Focus block from standup {target_date}.\nG notes: {your_notes[:200]}"
                        )
                        day_fmt  = slot_start.strftime("%a %b %-d")
                        time_fmt = f"{slot_start.strftime('%H:%M')}–{slot_end.strftime('%H:%M')}"
                        cal_bookings.append(f"{day_fmt} {time_fmt}: {title[:50]}")
                        print(f"    📅 Booked {day_fmt} {time_fmt}")
                    except Exception as e:
                        print(f"    ⚠️ Calendar booking failed: {e}")
                        unmatched.append(f"cal-fail: {title[:45]}")
                else:
                    print(f"    ⚠️ No free slot in 5 days for: {title[:45]}")

    # 8. Send Telegram summary
    print("\n8. Sending summary to Guillermo...")
    lines = [f"✅ *Standup processed — {target_date}*\n[View page]({page_url})\n"]

    if focus_booked:
        lines.append(f"🎯 *Tomorrow's Focus booked:*\n  • {focus_booked}")
    elif tomorrows_focus:
        lines.append(f"⚠️ *Tomorrow's Focus not booked* — calendar auth failed")
    else:
        lines.append(f"⚠️ *Tomorrow's Focus not set* — fill it in for tomorrow's calendar block")

    if cal_bookings:
        lines.append(f"\n📅 *Calendar blocks added ({len(cal_bookings)}):*")
        for b in cal_bookings:
            lines.append(f"  • {b}")

    if mc_created:
        lines.append(f"\n🐢 *MC tasks created ({len(mc_created)}):*")
        for t in mc_created:
            lines.append(f"  • {t}")
    if mc_updated:
        lines.append(f"\n🐢 *MC tasks updated ({len(mc_updated)}):*")
        for t in mc_updated:
            lines.append(f"  • {t}")

    if routed_raphael:
        lines.append(f"\n🔴 *Dispatched to Raphael ({len(routed_raphael)}):*")
        for t in routed_raphael:
            lines.append(f"  • {t}")
    if routed_leonardo:
        lines.append(f"\n🔵 *Dispatched to Leonardo ({len(routed_leonardo)}):*")
        for t in routed_leonardo:
            lines.append(f"  • {t}")
    if routed_molty:
        lines.append(f"\n🦎 *Molty's Den ({len(routed_molty)}):*")
        for t in routed_molty:
            lines.append(f"  • {t}")

    if closed:
        lines.append(f"\n✔️ *Closed in Todoist ({len(closed)}):*")
        for t in closed:
            lines.append(f"  • {t}")
    if rescheduled:
        lines.append(f"\n📅 *Rescheduled ({len(rescheduled)}):*")
        for t in rescheduled:
            lines.append(f"  • {t}")

    if unmatched:
        lines.append(f"\n⚠️ *Issues ({len(unmatched)}):*")
        for t in unmatched:
            lines.append(f"  • {t}")

    total_actions = len(closed) + len(cal_bookings) + len(mc_created) + len(mc_updated) + len(routed_raphael) + len(routed_leonardo)
    if total_actions == 0:
        lines.append("\n_No actions found. Make sure Action and Owner columns are filled in Notion._")

    msg = "\n".join(lines)
    print(msg)
    send_telegram(msg)
    print("\n✅ Done.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = datetime.now(HKT).strftime("%Y-%m-%d")
    process(target)
