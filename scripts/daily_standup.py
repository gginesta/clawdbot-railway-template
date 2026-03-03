#!/data/workspace/.venv/bin/python3
"""
Daily Standup Script v3 — Redesigned 2026-03-03 per agreed system v2.1

PAGE STRUCTURE:
1. 📋 Summary callout (situation, squad status)
2. 🎯 Tomorrow's Focus — BLANK callout for Guillermo to fill (ONE item)
3. 📬 Email highlights (if any)
4. ❓ Clarifying questions (if any)
5. 📋 Task DB — persistent, pre-triaged
6. 🧱 Blockers

RULES:
- ALL tasks are fully triaged BEFORE the page is sent
- Titles are rewritten to be clear and actionable + 🦎 at end (first intake only)
- Every task has priority, time estimate, owner, notes
- Book Calendar? pre-ticked for P1/P2 owner=Guillermo (bias: tick more not less)
- In MC? pre-ticked for agent-owned multi-step work
- Action column: Keep / Done / Drop / Reschedule ONLY (routing is Owner column)
- NO automatic calendar blocking at generation time — calendar happens post-review
- Tomorrow's Focus: BLANK — Guillermo writes ONE item — it becomes a calendar event
"""
import json, requests, sys, time, os, uuid, urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# === CONFIG ===
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "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")
TODOIST_TOKEN = os.environ.get("TODOIST_API_TOKEN", "9a26743814658c9e82d92aa716b46a9b0a2257c4")
STANDUP_DB_ID = "2fe39dd69afd81f189f7e58925dad602"

NH = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}

HKT = timezone(timedelta(hours=8))
NOTION_SPACE_ID = "375629bd-cc72-4ad8-a3be-84139fa2fb3b"
NOTION_TOKEN_V2_PATH = "/data/workspace/credentials/notion-token-v2.txt"
PERSISTENT_DB_CONFIG = "/data/workspace/credentials/notion-standup-db.json"

# Desired column order for the persistent standup DB
COLUMN_ORDER = ["Task", "Your Notes", "Action", "Owner", "Book Calendar?", "In MC?", "Due Date", "Priority", "Time Est.", "Project", "Section", "Molty's Notes", "Standup Date", "Type"]
COLUMN_WIDTHS = {"Task": 280, "Your Notes": 220, "Action": 130, "Owner": 110, "Book Calendar?": 100, "In MC?": 80, "Due Date": 120, "Priority": 90, "Time Est.": 90, "Project": 120, "Section": 100, "Molty's Notes": 280, "Standup Date": 120, "Type": 130}


def fix_column_order(db_block_id: str) -> bool:
    """Fix column order in a newly created Notion database using the internal API.
    Reads token_v2 from NOTION_TOKEN_V2_PATH. Silently skips if token missing."""
    if not os.path.exists(NOTION_TOKEN_V2_PATH):
        print(f"   ⚠️ token_v2 not found — skipping column fix")
        return False
    with open(NOTION_TOKEN_V2_PATH) as f:
        token_v2 = f.read().strip()
    if not token_v2:
        return False

    internal_headers = {
        "Content-Type": "application/json",
        "Cookie": f"token_v2={token_v2}",
        "notion-client-version": "23.13.0.36",
        "x-notion-space-id": NOTION_SPACE_ID,
    }

    try:
        # Step 1: Get block → find collection_id and view_id
        req = urllib.request.Request(
            "https://www.notion.so/api/v3/getRecordValues",
            data=json.dumps({"requests": [{"table": "block", "id": db_block_id}]}).encode(),
            method="POST", headers=internal_headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            block_value = json.loads(r.read())["results"][0].get("value", {})
        if not block_value:
            print(f"   ⚠️ Block {db_block_id} not found via internal API"); return False

        collection_id = block_value.get("collection_id")
        view_ids = block_value.get("view_ids", [])
        if not collection_id or not view_ids:
            print(f"   ⚠️ Missing collection_id/view_ids"); return False
        view_id = view_ids[0]

        # Step 2: Get collection schema → name→internal_id map
        req = urllib.request.Request(
            "https://www.notion.so/api/v3/getRecordValues",
            data=json.dumps({"requests": [{"table": "collection", "id": collection_id}]}).encode(),
            method="POST", headers=internal_headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            schema = json.loads(r.read())["results"][0].get("value", {}).get("schema", {})
        if not schema:
            print(f"   ⚠️ Empty schema"); return False

        name_to_id = {v.get("name"): k for k, v in schema.items()}

        # Step 3: Build table_properties in desired order
        table_properties = [
            {"property": name_to_id[col], "visible": True, "width": COLUMN_WIDTHS.get(col, 120)}
            for col in COLUMN_ORDER if col in name_to_id
        ]

        # Step 4: saveTransactions
        payload = {
            "requestId": str(uuid.uuid4()),
            "transactions": [{
                "id": str(uuid.uuid4()),
                "spaceId": NOTION_SPACE_ID,
                "operations": [{
                    "pointer": {"table": "collection_view", "id": view_id, "spaceId": NOTION_SPACE_ID},
                    "command": "update",
                    "path": ["format"],
                    "args": {"table_properties": table_properties}
                }]
            }]
        }
        req = urllib.request.Request(
            "https://www.notion.so/api/v3/saveTransactions",
            data=json.dumps(payload).encode(), method="POST", headers=internal_headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
        print(f"   ✅ Column order fixed ({len(table_properties)} columns)")
        return True

    except Exception as e:
        print(f"   ⚠️ Column order fix failed: {e}")
        return False

PROJECT_MAP = {
    "6M5rpCXmg7x7RC2Q": "Inbox 📥",
    "6M5rpGfw5jR9Qg9R": "Personal 🙂",
    "6M5rpGgV6q865hrX": "Brinc 🔴",
    "6Rr9p6MxWHFwHXGC": "Mana Capital 🟠",
    "6fwH32grqrCJF23R": "Molty's Den 🦎",
    "6g53F7ccF8HHjgXM": "Cerebro 🔵",
    "6fx5GV7Q93Hp4QgM": "Ideas 💡",
}

PRIO_MAP = {4: "🔴 P1", 3: "🟡 P2", 2: "🔵 P3", 1: "⚪ P4"}
MOLTY_PROJECTS = {"6fwH32grqrCJF23R"}


def now_hkt():
    return datetime.now(HKT)

def today_str():
    return now_hkt().strftime("%Y-%m-%d")

def today_display():
    return now_hkt().strftime("%a %b %-d, %Y")


def classify_section(due_str, today):
    if not due_str:
        return "Backlog"
    d = due_str[:10]
    if d < today:
        return "Overdue"
    elif d == today:
        return "Today"
    today_dt = datetime.strptime(today, "%Y-%m-%d")
    due_dt = datetime.strptime(d, "%Y-%m-%d")
    if (due_dt - today_dt).days <= 7:
        return "Upcoming"
    return "Backlog"


def estimate_time(task):
    content = task["content"].lower()
    if any(w in content for w in ["research", "investigate", "explore", "evaluate", "analyze"]):
        return "1h"
    if any(w in content for w in ["build", "create", "implement", "develop", "write", "design"]):
        return "2h+"
    if any(w in content for w in ["setup", "configure", "install", "set up", "connect"]):
        return "1h"
    if any(w in content for w in ["plan", "organise", "organize", "coordinate", "schedule"]):
        return "1h"
    if any(w in content for w in ["order", "buy", "check", "review", "send", "email", "call", "reply"]):
        return "30min"
    return "30min"


def determine_owner(task):
    if task["project_id"] in MOLTY_PROJECTS:
        return "Molty"
    content = task["content"].lower()
    if any(w in content for w in ["molty", "tmnt", "openclaw", "agent", "cron", "memory", "discord"]):
        return "Molty"
    if any(w in content for w in ["raphael", "brinc sales", "hubspot"]):
        return "Raphael"
    if any(w in content for w in ["leonardo", "cerebro", "launchpad"]):
        return "Leonardo"
    return "Guillermo"


def generate_notes(task, section, today):
    """Generate ACTIONABLE notes. Never say 'Needs triage'. Every task gets meaningful context."""
    content = task["content"]
    pid = task["project_id"]
    owner = determine_owner(task)
    notes = []

    # Overdue context — be specific about recommended action
    if section == "Overdue":
        due = task.get("due", {}).get("date", "")[:10]
        if due:
            days = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due, "%Y-%m-%d")).days
            notes.append(f"⚠️ Overdue by {days} day{'s' if days != 1 else ''}")
            if owner == "Molty":
                notes.append("I'll complete this today or reschedule with a realistic date")
            elif owner == "Guillermo":
                if days >= 3:
                    notes.append("Consider: still relevant? Reschedule or drop?")
                else:
                    notes.append("Slipped — needs new date or quick action")
            else:
                notes.append(f"Assigned to {owner} — I'll follow up")

    # Inbox tasks — be specific about where they should go
    elif pid == "6M5rpCXmg7x7RC2Q":  # Inbox
        notes.append("In Inbox — needs project assignment and priority")
        if owner == "Molty":
            notes.append("I'll move to the right project after your input")

    # Today tasks — what's the plan?
    elif section == "Today":
        if owner == "Molty":
            notes.append("On my plate today — will update you when done")
        elif owner == "Guillermo":
            notes.append("Due today — block time or reschedule?")
        else:
            notes.append(f"Due today for {owner}")

    # Upcoming/backlog — brief status
    elif section == "Upcoming":
        if owner == "Molty":
            notes.append("Scheduled — I'll handle on the due date")
        else:
            notes.append("Coming up — on track")
    elif section == "Backlog":
        if owner == "Molty":
            notes.append("Parked — will pick up when prioritized")
        else:
            notes.append("Backlog — review when ready")

    # Add description if present (always useful context)
    if task.get("description"):
        desc = task["description"][:120].strip()
        if desc:
            notes.append(f"Details: {desc}")

    # Add labels as context
    labels = task.get("labels", [])
    if labels:
        notes.append(f"Tags: {', '.join(labels)}")

    # Ensure we never return empty
    if not notes:
        project = PROJECT_MAP.get(pid, "Other")
        notes.append(f"{project} · {owner} · {section}")

    return "; ".join(notes)


def is_decided(task, section):
    """Determine if a task has already been discussed/decided.
    A task is 'decided' if:
    - It has a clear due date in the future (not overdue)
    - It's assigned to Molty (we know what to do)
    - It's in Backlog with a future date (parked intentionally)
    A task 'needs input' if:
    - It's overdue (needs decision: keep/reschedule/drop?)
    - It's new in Inbox (untriaged)
    - It's due today/upcoming but has no clear owner or plan
    """
    pid = task["project_id"]
    owner = determine_owner(task)

    # Overdue always needs input
    if section == "Overdue":
        return False
    # Inbox always needs input
    if pid == "6M5rpCXmg7x7RC2Q":
        return False
    # Molty-owned tasks are decided (I know what to do)
    if owner == "Molty":
        return True
    # Future-dated backlog is decided (parked)
    if section == "Backlog":
        return True
    # Upcoming with clear owner is decided
    if section == "Upcoming" and owner != "Guillermo":
        return True
    # Today tasks for Guillermo need input (what to focus on)
    if section == "Today" and owner == "Guillermo":
        return False
    # Default: needs input
    return False


def deduplicate_tasks(tasks):
    seen = {}
    unique = []
    for t in tasks:
        key = t["content"].strip().lower()
        if key not in seen:
            seen[key] = t
            unique.append(t)
    return unique


def group_tasks(tasks):
    by_id = {t["id"]: t for t in tasks}
    parents = []
    children_map = {}

    for t in tasks:
        pid = t.get("parent_id") or t.get("parent", {}).get("id")
        if pid and pid in by_id:
            children_map.setdefault(pid, []).append(t)
        elif pid:
            children_map.setdefault(pid, []).append(t)
        else:
            parents.append(t)

    for p in parents:
        p["_children"] = children_map.pop(p["id"], [])

    for pid, kids in children_map.items():
        synthetic = dict(kids[0])
        synthetic["_children"] = kids[1:] if len(kids) > 1 else []
        parents.append(synthetic)

    skipped = sum(len(p.get("_children", [])) for p in parents)
    if skipped:
        print(f"   Grouped {skipped} sub-tasks under their parents")
    return parents


def get_completed_tasks():
    """Fetch recently completed tasks from Todoist."""
    try:
        resp = requests.get(
            "https://api.todoist.com/sync/v9/completed/get_all",
            headers=TH,
            params={"since": (now_hkt() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"), "limit": 20},
            timeout=10
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            return [i.get("content", "Unknown") for i in items[:10]]
    except Exception:
        pass
    return []


# === NOTION PAGE CREATION ===

def create_standup_page(today_disp):
    title = f"{today_disp} — 5PM HKT"
    resp = requests.post("https://api.notion.com/v1/pages", headers=NH, json={
        "parent": {"database_id": STANDUP_DB_ID},
        "properties": {"Date": {"title": [{"text": {"content": title}}]}}
    }, timeout=15)
    if resp.status_code != 200:
        print(f"ERROR creating page: {resp.status_code} {resp.text}")
        sys.exit(1)
    page_id = resp.json()["id"]
    print(f"  Page created: {page_id}")
    return page_id


def get_tomorrow_priority(all_tasks, tomorrow):
    """Return the single highest-priority task due tomorrow (or top overdue/P1 if none)."""
    tomorrow_tasks = [
        t for t in all_tasks
        if t.get("due", {}) and t.get("due", {}).get("date", "")[:10] == tomorrow
    ]
    if tomorrow_tasks:
        tomorrow_tasks.sort(key=lambda t: -t.get("priority", 1))
        return tomorrow_tasks[0]
    # Fallback: highest priority overdue P1, then P2
    high_pri = [t for t in all_tasks if t.get("priority", 4) <= 2]
    if high_pri:
        high_pri.sort(key=lambda t: -t.get("priority", 1))
        return high_pri[0]
    return all_tasks[0] if all_tasks else None


def add_top_blocks(page_id, today_disp, tomorrow_disp, completed, needs_input_count, pipeline_count, overdue_tasks, tomorrow_task=None, persistent_db_id=None, squad_status=None, clarifying_questions=None):
    """Add summary callout, blank Tomorrow's Focus, optional email/question blocks, completed section."""
    children = []

    # Summary callout — situation + squad status
    overdue_summary = ""
    if overdue_tasks:
        overdue_lines = [f"• {t['content'][:60]}" for t in overdue_tasks[:3]]
        overdue_summary = "\n\n🔥 Overdue:\n" + "\n".join(overdue_lines)

    squad_text = ""
    if squad_status:
        squad_text = f"\n\n{squad_status}"

    children.append({
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [{"text": {"content":
                f"Daily Standup — {today_disp}\n"
                f"🎯 {needs_input_count} items need your input | 📋 {pipeline_count} in active pipeline"
                f"{overdue_summary}"
                f"{squad_text}"
            }}],
            "icon": {"type": "emoji", "emoji": "📋"},
            "color": "default"
        }
    })

    # Tomorrow's Focus — BLANK. Guillermo fills in ONE item. It becomes a calendar event.
    children.append({
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [
                {"text": {"content": f"🎯 Tomorrow's Focus ({tomorrow_disp})\n"}, "annotations": {"bold": True}},
                {"text": {"content": "Write the ONE thing that makes tomorrow worthwhile.\nThis becomes a calendar event. One item only."}, "annotations": {"color": "gray", "italic": True}},
            ],
            "icon": {"type": "emoji", "emoji": "🎯"},
            "color": "yellow_background"
        }
    })

    # Clarifying questions (if any)
    if clarifying_questions:
        children.append({
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": "❓ Clarifying Questions — answer these before reviewing the table\n"}, "annotations": {"bold": True}},
                    {"text": {"content": clarifying_questions}}
                ],
                "icon": {"type": "emoji", "emoji": "❓"},
                "color": "blue_background"
            }
        })

    # Completed section
    if completed:
        children.append({"object": "block", "type": "heading_3",
                         "heading_3": {"rich_text": [{"text": {"content": "✅ Completed since last standup"}}]}})
        for item in completed[:8]:
            children.append({"object": "block", "type": "bulleted_list_item",
                             "bulleted_list_item": {"rich_text": [{"text": {"content": item[:100]}}]}})
        children.append({"object": "block", "type": "divider", "divider": {}})

    # Link to persistent DB (bookmark block) — filtered view of today's tasks
    if persistent_db_id:
        db_url = f"https://www.notion.so/{persistent_db_id.replace('-', '')}"
        children.append({"object": "block", "type": "paragraph",
                         "paragraph": {"rich_text": [
                             {"type": "text", "text": {"content": "📋 View today's tasks in TMNT Standup Board → "},
                              "annotations": {"bold": True}},
                             {"type": "text", "text": {"content": "Open database", "link": {"url": db_url}},
                              "annotations": {"color": "blue"}},
                         ]}})
        children.append({"object": "block", "type": "bookmark",
                         "bookmark": {"url": db_url, "caption": []}})
    else:
        children.append({"object": "block", "type": "paragraph",
                         "paragraph": {"rich_text": [{"text": {"content":
                             "New, overdue, or needs a decision. Set Action + leave comments."}}]}})

    requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children",
                   headers=NH, json={"children": children}, timeout=15)


def add_pipeline_header(page_id):
    """Add pipeline section header + footer after Table 1."""
    children = [
        {"object": "block", "type": "divider", "divider": {}},
        # No heading_2 here — the database title serves as the section header
        {"object": "block", "type": "paragraph",
         "paragraph": {"rich_text": [{"text": {"content":
             "Already decided — clear owners, dates, plans. Scan occasionally."}}]}},
    ]
    requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children",
                   headers=NH, json={"children": children}, timeout=15)


def add_footer(page_id):
    requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=NH, json={
        "children": [
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2",
             "heading_2": {"rich_text": [{"text": {"content": "🧱 Blockers"}}]}},
            {"object": "block", "type": "paragraph",
             "paragraph": {"rich_text": [{"text": {"content": "None reported"}}]}},
        ]
    }, timeout=15)


# Todoist projects that sync to MC by default
SYNCED_TO_MC_PROJECTS = {"6M5rpGgV6q865hrX", "6Rr9p6MxWHFwHXGC", "6g53F7ccF8HHjgXM"}  # Brinc, Mana, Cerebro
AGENT_PROJECTS = {"6fwH32grqrCJF23R"}  # Molty's Den

def should_be_in_mc(task):
    """Pre-fill the 'In MC?' checkbox.
    YES: agent-owned work in Brinc/Cerebro/Mana/Fleet projects.
    NO: Guillermo-owned, personal tasks, pure admin (call/email/check).
    Bias: when in doubt for agent tasks, tick. Guillermo can untick."""
    pid    = task.get("project_id", "")
    labels = task.get("labels", [])
    owner  = determine_owner(task)
    content = task.get("content", "").lower()

    if "personal" in labels:   # explicit opt-out
        return False
    if "mc" in labels:         # explicit opt-in
        return True
    if owner not in ("Molty", "Raphael", "Leonardo"):
        return False  # Guillermo-owned → no MC task
    if pid not in SYNCED_TO_MC_PROJECTS and pid not in AGENT_PROJECTS:
        return False  # wrong project
    # Skip obvious personal-admin tasks that have leaked into agent projects
    # (e.g. "call dentist", "email accountant", "buy coffee") — these are not agent work
    personal_admin = ["call dentist", "call doctor", "buy ", "order food", "book appointment", "book flight"]
    if any(w in content for w in personal_admin):
        return False
    return True


def should_book_calendar(task, section):
    """Pre-fill the 'Book Calendar?' checkbox.
    Philosophy: bias toward booking. Guillermo can always move a block.
    YES: P1/P2 + owner=Guillermo + not backlog.
    NO: agent-owned, P4, Backlog section."""
    owner    = determine_owner(task)
    priority = task.get("priority", 1)  # Todoist inverted: 4=P1, 3=P2, 2=P3, 1=P4

    if owner != "Guillermo":
        return False  # agent work — no G time needed
    if priority == 1:  # P4 in display — don't book
        return False
    if section == "Backlog":
        return False  # not due soon — don't block calendar for backlog items
    # P1 (priority=4) or P2 (priority=3) owned by Guillermo, not backlog → book
    return priority >= 3


# Column order matters! Notion respects dict insertion order on creation.
# Desired order: Task → Your Notes → In MC? → Action → Due Date → Molty's Notes → Owner → Priority → Section → Time Est. → Project
DB_PROPERTIES = {
    "Task": {"title": {}},
    "Your Notes": {"rich_text": {}},
    "Action": {"select": {"options": [
        {"name": "✅ Keep", "color": "green"},
        {"name": "📅 Reschedule", "color": "yellow"},
        {"name": "🗑️ Drop", "color": "red"},
        {"name": "✔️ Done", "color": "green"},
    ]}},
    "Book Calendar?": {"checkbox": {}},
    "In MC?": {"checkbox": {}},
    "Due Date": {"date": {}},
    "Molty's Notes": {"rich_text": {}},
    "Owner": {"select": {"options": [
        {"name": "Guillermo", "color": "default"},
        {"name": "Molty", "color": "green"},
        {"name": "Raphael", "color": "red"},
        {"name": "Leonardo", "color": "blue"},
    ]}},
    "Priority": {"select": {"options": [
        {"name": "🔴 P1", "color": "red"},
        {"name": "🟡 P2", "color": "yellow"},
        {"name": "🔵 P3", "color": "blue"},
        {"name": "⚪ P4", "color": "default"},
    ]}},
    "Section": {"select": {"options": [
        {"name": "Overdue", "color": "red"},
        {"name": "Today", "color": "green"},
        {"name": "Upcoming", "color": "blue"},
        {"name": "Inbox", "color": "gray"},
        {"name": "Backlog", "color": "default"},
    ]}},
    "Time Est.": {"select": {"options": [
        {"name": "15min", "color": "green"},
        {"name": "30min", "color": "blue"},
        {"name": "1h", "color": "yellow"},
        {"name": "2h+", "color": "red"},
    ]}},
    "Project": {"select": {"options": [
        {"name": "Personal 🙂", "color": "blue"},
        {"name": "Brinc 🔴", "color": "red"},
        {"name": "Mana Capital 🟠", "color": "orange"},
        {"name": "Molty's Den 🦎", "color": "green"},
        {"name": "Cerebro 🔵", "color": "blue"},
        {"name": "Inbox 📥", "color": "gray"},
        {"name": "Ideas 💡", "color": "yellow"},
    ]}},
    "Standup Date": {"date": {}},
    "Type": {"select": {"options": [
        {"name": "Needs Input", "color": "red"},
        {"name": "Active Pipeline", "color": "blue"},
    ]}},
}


def create_db(page_id, title):
    resp = requests.post("https://api.notion.com/v1/databases", headers=NH, json={
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "is_inline": True,
        "properties": DB_PROPERTIES,
    }, timeout=15)
    if resp.status_code != 200:
        print(f"ERROR creating DB '{title}': {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.json()["id"]


def get_or_create_persistent_db(page_id: str) -> str:
    """Return the persistent TMNT Standup Board DB ID, creating it once if needed.

    Config file: /data/workspace/credentials/notion-standup-db.json
    - If config exists and DB is valid: return stored ID (page_id not used)
    - If not: create new DB titled '📋 TMNT Standup Board' as child of page_id,
      save ID to config, fix column order.
    """
    # --- Try stored config ---
    if os.path.exists(PERSISTENT_DB_CONFIG):
        try:
            with open(PERSISTENT_DB_CONFIG) as f:
                config = json.load(f)
            db_id = config.get("persistent_db_id", "")
            if db_id:
                resp = requests.get(
                    f"https://api.notion.com/v1/databases/{db_id}",
                    headers=NH, timeout=10
                )
                if resp.status_code == 200:
                    print(f"   ♻️  Reusing persistent DB: {db_id}")
                    return db_id
                print(f"   ⚠️ Stored DB not found (HTTP {resp.status_code}), creating new...")
        except Exception as e:
            print(f"   ⚠️ Config read error: {e} — creating new DB...")

    # --- Create new persistent DB ---
    print("   📦 Creating new persistent TMNT Standup Board...")
    resp = requests.post("https://api.notion.com/v1/databases", headers=NH, json={
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [{"type": "text", "text": {"content": "📋 TMNT Standup Board"}}],
        "is_inline": True,
        "properties": DB_PROPERTIES,
    }, timeout=15)
    if resp.status_code != 200:
        print(f"ERROR creating persistent DB: {resp.status_code} {resp.text}")
        sys.exit(1)

    db_id = resp.json()["id"]
    print(f"   ✅ Created persistent DB: {db_id}")

    # --- Save config ---
    os.makedirs(os.path.dirname(PERSISTENT_DB_CONFIG), exist_ok=True)
    with open(PERSISTENT_DB_CONFIG, "w") as f:
        json.dump({
            "persistent_db_id": db_id,
            "created_at": datetime.now(HKT).isoformat(),
        }, f, indent=2)
    print(f"   💾 Config saved: {PERSISTENT_DB_CONFIG}")

    # --- Fix column order (best-effort, requires token_v2) ---
    print("   🔧 Fixing column order...")
    fix_column_order(db_id)

    return db_id


_EXISTING_TASKS_CACHE: set | None = None

def get_existing_task_keys(db_id: str, today: str) -> set:
    """Return set of 'title|type' keys already in the DB for today — used to skip duplicates."""
    global _EXISTING_TASKS_CACHE
    if _EXISTING_TASKS_CACHE is not None:
        return _EXISTING_TASKS_CACHE
    keys = set()
    cursor = None
    while True:
        body = {"page_size": 100, "filter": {"property": "Standup Date", "date": {"equals": today}}}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query",
                          headers=NH, json=body, timeout=15)
        data = r.json()
        for row in data.get("results", []):
            props = row.get("properties", {})
            title = (props.get("Task", {}).get("title") or [{}])[0].get("plain_text", "")
            typ = (props.get("Type", {}).get("select") or {}).get("name", "")
            if title:
                keys.add(f"{title}|{typ}")
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    _EXISTING_TASKS_CACHE = keys
    return keys


def add_task_to_db_with_retry(db_id, task, section, today, task_type="Needs Input", retries=3, sort_order: int = 999) -> bool:
    """Wrapper: retry add_task_to_db on timeout/failure with exponential backoff."""
    # Skip if already written for today (prevents duplicates on re-run)
    existing = get_existing_task_keys(db_id, today)
    key = f"{task.get('content', '')}|{task_type}"
    if key in existing:
        return True  # Already there, treat as success

    for attempt in range(1, retries + 1):
        try:
            result = add_task_to_db(db_id, task, section, today, task_type, sort_order=sort_order)
            if result:
                return True
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            wait = 2 ** attempt
            print(f"   ⚠️  Notion timeout on attempt {attempt}/{retries} — retrying in {wait}s ({e})")
            time.sleep(wait)
        except Exception as e:
            print(f"   ❌ Unexpected error adding task: {e}")
            return False
    print(f"   ❌ Failed after {retries} retries: {task.get('content','?')[:50]}")
    return False


def alert_telegram_failure(error_msg: str):
    """Send immediate Telegram alert when standup fails."""
    try:
        import urllib.request as ur
        payload = json.dumps({
            "chat_id": "1097408992",
            "text": f"⚠️ *Daily Standup Failed*\n\nError: {error_msg[:300]}\n\nI'll retry shortly. Check /data/workspace/logs/standup.log for details.",
            "parse_mode": "Markdown"
        }).encode()
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "8292515315:AAETOvDJgl4r13qF3_32qhpn8h7jIOVJQDA")
        ur.urlopen(ur.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"}
        ), timeout=10)
    except Exception:
        pass  # Best-effort only


# Global cache for existing tasks — loaded once per run
_EXISTING_TASKS_CACHE = {}


def load_existing_tasks(db_id):
    """Load all existing tasks from DB into cache. Call once at start."""
    global _EXISTING_TASKS_CACHE
    _EXISTING_TASKS_CACHE = {}
    
    try:
        # Handle pagination
        has_more = True
        start_cursor = None
        
        while has_more:
            body = {"page_size": 100}
            if start_cursor:
                body["start_cursor"] = start_cursor
            
            resp = requests.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=NH,
                json=body,
                timeout=15
            )
            if resp.status_code != 200:
                break
            
            data = resp.json()
            for page in data.get("results", []):
                if page.get("archived"):
                    continue
                props = page.get("properties", {})
                for k, v in props.items():
                    if v.get("type") == "title":
                        texts = v.get("title", [])
                        if texts:
                            title = texts[0].get("plain_text", "")
                            # Normalize: lowercase, strip, first 50 chars
                            key = title.lower().strip()[:50]
                            _EXISTING_TASKS_CACHE[key] = page.get("id")
                        break
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            time.sleep(0.3)
        
        print(f"   📋 Loaded {len(_EXISTING_TASKS_CACHE)} existing tasks into cache")
    except Exception as e:
        print(f"   ⚠️ Failed to load existing tasks: {e}")


def find_existing_task(title_key):
    """Check cache for existing task. Returns page_id or None."""
    key = title_key.lower().strip()[:50]
    return _EXISTING_TASKS_CACHE.get(key)


def add_task_to_db(db_id, task, section, today, task_type="Needs Input", sort_order: int = 999):
    """Add a task row to the persistent DB, or update if it already exists.

    task_type: "Needs Input" | "Active Pipeline"
    Standup Date is always set to today so rows can be filtered by day.
    """
    due_str = task.get("due", {}).get("date", "") if task.get("due") else ""
    project = PROJECT_MAP.get(task["project_id"], "Other")
    priority = PRIO_MAP.get(task["priority"], "⚪ P4")
    owner = determine_owner(task)
    time_est = estimate_time(task)
    notes = generate_notes(task, section, today)
    in_mc = should_be_in_mc(task)
    book_cal = should_book_calendar(task, section)

    children = task.get("_children", [])
    if children:
        subtask_lines = [f"• {c['content']}" for c in children]
        subtask_text = f"Sub-tasks ({len(children)}):\n" + "\n".join(subtask_lines)
        notes = f"{notes}\n{subtask_text}" if notes else subtask_text

    if len(notes) > 1900:
        notes = notes[:1900] + "..."

    props = {
        "Task": {"title": [{"text": {"content": task["content"]}}]},
        "Book Calendar?": {"checkbox": book_cal},
        "In MC?": {"checkbox": in_mc},
        "Project": {"select": {"name": project}},
        "Priority": {"select": {"name": priority}},
        "Section": {"select": {"name": section}},
        "Owner": {"select": {"name": owner}},
        "Time Est.": {"select": {"name": time_est}},
        "Standup Date": {"date": {"start": today}},
        "Type": {"select": {"name": task_type}},
    }
    if due_str:
        props["Due Date"] = {"date": {"start": due_str[:10]}}
    if notes:
        props["Molty's Notes"] = {"rich_text": [{"text": {"content": notes}}]}
    props["Sort Order"] = {"number": sort_order}

    # Check if task already exists — update instead of creating duplicate
    existing_id = find_existing_task(task["content"])
    
    if existing_id:
        # Update existing task (don't overwrite Action or Your Notes)
        update_props = {k: v for k, v in props.items() if k not in ["Action", "Your Notes"]}
        update_props["Standup Date"] = {"date": {"start": today}}  # Update to today
        resp = requests.patch(
            f"https://api.notion.com/v1/pages/{existing_id}",
            headers=NH,
            json={"properties": update_props},
            timeout=15
        )
        time.sleep(0.35)
        return resp.status_code == 200
    else:
        # Create new task
        resp = requests.post("https://api.notion.com/v1/pages", headers=NH, json={
            "parent": {"database_id": db_id},
            "properties": props
        }, timeout=15)
        time.sleep(0.35)
        return resp.status_code == 200


# === YESTERDAY'S ACTION PROCESSOR ===

# Map Action column values → behaviour
ACTION_MAP = {
    # done / close
    "done":     "close",
    "✓ done":   "close",
    "✅ done":  "close",
    # keep — no change, will appear in today's standup normally
    "keep":     "keep",
    "✅ keep":  "keep",
    # dispatch agents
    "raphael":      "dispatch_raphael",
    "🔴 raphael":   "dispatch_raphael",
    "🔴":            "dispatch_raphael",
    "leonardo":     "dispatch_leonardo",
    "🔵 leonardo":  "dispatch_leonardo",
    "🔵":            "dispatch_leonardo",
    "molty":        "keep",   # stays in standup for Molty to own
    "🦎 molty":     "keep",
    "🦎":            "keep",
    # park / snooze 60 days
    "park":     "snooze",
    "🅿️ park":  "snooze",
    "snooze":   "snooze",
    "delete":   "close",
}

WEBHOOK_TOKENS = {
    "raphael":  "ed691e4167448ee7be98025a57d40f69553408c0b181890a015265712159c6bd",
    "leonardo": "08d506d4eed31e3117e1c357e30f5606fd342ebcfc912373d18b8eaf3f723758",
}
WEBHOOK_URLS = {
    "raphael":  "https://ggv-raphael.up.railway.app/hooks/agent",
    "leonardo": "https://leonardo-production.up.railway.app/hooks/agent",
}

MC_API_URL = "https://resilient-chinchilla-241.convex.site"
MC_TOKEN   = "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc"
MC_HDR     = {"Authorization": f"Bearer {MC_TOKEN}", "Content-Type": "application/json"}

def _mc_close_by_title(title: str) -> bool:
    """Find MC task by title (fuzzy) and mark it done."""
    try:
        r = requests.get(f"{MC_API_URL}/api/tasks", headers=MC_HDR, timeout=10)
        if r.status_code != 200:
            return False
        tasks = r.json() if isinstance(r.json(), list) else []
        title_lower = title.lower().strip()
        match = None
        for t in tasks:
            if t.get("status") in ("done", "blocked"):
                continue
            t_title = t.get("title", "").lower().strip()
            if t_title == title_lower or title_lower[:40] in t_title or t_title[:40] in title_lower:
                match = t
                break
        if not match:
            return False
        patch = requests.patch(
            f"{MC_API_URL}/api/task",
            headers=MC_HDR,
            json={"id": match["_id"], "status": "done"},
            timeout=10,
        )
        return patch.status_code == 200
    except Exception:
        return False


def _todoist_close(task_id: str) -> bool:
    r = requests.post(f"https://api.todoist.com/api/v1/tasks/{task_id}/close",
                      headers=TH, timeout=10)
    return r.status_code == 204

def _todoist_snooze(task_id: str, days: int = 60) -> bool:
    from datetime import date
    snooze_to = (datetime.now(HKT) + timedelta(days=days)).strftime("%Y-%m-%d")
    r = requests.post(f"https://api.todoist.com/api/v1/tasks/{task_id}",
                      headers={**TH, "Content-Type": "application/json"},
                      json={"due_date": snooze_to}, timeout=10)
    return r.status_code == 200

def _dispatch_agent(agent: str, task_title: str, your_notes: str, molty_notes: str, due: str) -> bool:
    note_ctx = f"\nGuillermo's notes: \"{your_notes}\"" if your_notes else ""
    molty_ctx = f"\nMolty's context: \"{molty_notes}\"" if molty_notes else ""
    due_ctx = f"\nDue: {due}" if due else ""
    msg = (
        f"🦎 Standup dispatch from Molty — task assigned to you:\n\n"
        f"**{task_title}**{due_ctx}{note_ctx}{molty_ctx}\n\n"
        f"Please pick this up, update MC when started, and post results when done."
    )
    data = json.dumps({"message": msg, "wakeMode": "now"}).encode()
    try:
        req = urllib.request.Request(
            WEBHOOK_URLS[agent], data=data, method="POST",
            headers={"Authorization": f"Bearer {WEBHOOK_TOKENS[agent]}",
                     "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            return resp.get("ok", False)
    except Exception as e:
        print(f"   ⚠️  Webhook to {agent} failed: {e}")
        return False

def _find_todoist_id(all_tasks: list, title: str) -> str | None:
    """Fuzzy match task title → Todoist task id."""
    title_lower = title.lower().strip()
    # Exact match first
    for t in all_tasks:
        if t.get("content","").lower().strip() == title_lower:
            return t["id"]
    # Partial match (title starts with or contains)
    for t in all_tasks:
        c = t.get("content","").lower()
        if title_lower[:30] in c or c[:30] in title_lower:
            return t["id"]
    return None

def process_yesterday_actions(all_tasks: list) -> dict:
    """
    Read yesterday's standup DB rows. For each row with an Action set,
    execute the action (close, snooze, dispatch).
    Returns summary dict for logging.
    """
    yesterday = (datetime.now(HKT) - timedelta(days=1)).strftime("%Y-%m-%d")
    DB_ID = "31239dd6-9afd-81ad-8ffd-d1db09b1dd36"

    print(f"\n0. Processing yesterday's standup actions ({yesterday})...")

    # Fetch yesterday's rows
    rows, cursor = [], None
    while True:
        body = {"page_size": 100,
                "filter": {"property": "Standup Date", "date": {"equals": yesterday}}}
        if cursor:
            body["start_cursor"] = cursor
        r = requests.post(f"https://api.notion.com/v1/databases/{DB_ID}/query",
                          headers=NH, json=body, timeout=15)
        data = r.json()
        rows += data.get("results", [])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    if not rows:
        print(f"   No rows found for {yesterday} — skipping")
        return {}

    print(f"   Found {len(rows)} rows from yesterday")

    summary = {"closed": [], "snoozed": [], "dispatched": [], "kept": [], "skipped": []}

    for row in rows:
        props = row.get("properties", {})
        title_parts = props.get("Task", {}).get("title") or []
        title = title_parts[0].get("plain_text", "") if title_parts else ""
        if not title:
            continue

        raw_action = (props.get("Action", {}).get("select") or {}).get("name", "")
        your_notes = ((props.get("Your Notes", {}).get("rich_text") or [{}])[0].get("plain_text", ""))
        molty_notes = ((props.get("Molty's Notes", {}).get("rich_text") or [{}])[0].get("plain_text", ""))
        due = (props.get("Due Date", {}).get("date") or {}).get("start", "")

        # If no Action set, try to infer intent from Your Notes
        if not raw_action:
            notes_lower = your_notes.lower()
            if any(x in notes_lower for x in ["mark as done", "already done", "this is done", "already told you", "completed", "i did this"]):
                raw_action = "done"
            elif any(x in notes_lower for x in ["dont want to see", "don't want to see", "remove this", "delete this", "park this", "not relevant"]):
                raw_action = "snooze"
            else:
                summary["skipped"].append(title[:50])
                continue

        behaviour = ACTION_MAP.get(raw_action.lower().strip(), "keep")

        if behaviour == "close":
            tid = _find_todoist_id(all_tasks, title)
            if tid and _todoist_close(tid):
                print(f"   ✅ Closed: {title[:55]}")
                summary["closed"].append(title[:55])
                # Sync to MC immediately — don't wait for audit
                if _mc_close_by_title(title):
                    print(f"   🔄 MC synced: {title[:55]}")
            else:
                print(f"   ⚠️  Could not close (no Todoist match): {title[:55]}")
                # Still try to close in MC even if Todoist match failed
                if _mc_close_by_title(title):
                    print(f"   🔄 MC synced (no Todoist match): {title[:55]}")
                    summary["closed"].append(title[:55])
                else:
                    summary["skipped"].append(title[:55])

        elif behaviour == "snooze":
            tid = _find_todoist_id(all_tasks, title)
            if tid and _todoist_snooze(tid):
                print(f"   💤 Snoozed 60d: {title[:55]}")
                summary["snoozed"].append(title[:55])
                # MC: leave open (snoozed = still relevant, just deferred)
            else:
                print(f"   ⚠️  Could not snooze: {title[:55]}")
                summary["skipped"].append(title[:55])

        elif behaviour in ("dispatch_raphael", "dispatch_leonardo"):
            agent = "raphael" if "raphael" in behaviour else "leonardo"
            if _dispatch_agent(agent, title, your_notes, molty_notes, due):
                print(f"   📤 Dispatched to {agent}: {title[:50]}")
                summary["dispatched"].append(f"{agent}: {title[:50]}")
            else:
                summary["skipped"].append(f"dispatch-failed: {title[:50]}")

        elif behaviour == "keep":
            summary["kept"].append(title[:50])

    total_acted = len(summary["closed"]) + len(summary["snoozed"]) + len(summary["dispatched"])
    print(f"   Done — {total_acted} actions taken, {len(summary['kept'])} kept, {len(summary['skipped'])} skipped\n")
    return summary


# === POST-STANDUP AUDIT ===

def _post_standup_audit(today: str) -> None:
    """Cross-check MC task statuses vs Todoist after standup completes.

    For each agent, find MC tasks in assigned/in_progress status that have a
    todoistId — if the Todoist task is already complete, sync MC to done.
    Log results to /data/workspace/logs/standup-audit-YYYY-MM-DD.md.
    """
    import requests as _req
    MC_API_URL = "https://resilient-chinchilla-241.convex.site"
    MC_TOKEN   = os.environ.get("MC_API_KEY", "232e4ddf7d69c31e01ad0fa0a61f70c29e4837ed018a153cce1a429842bb7cbc")
    MC_HDR     = {"Authorization": f"Bearer {MC_TOKEN}", "Content-Type": "application/json"}
    TD_TOKEN   = os.environ.get("TODOIST_API_TOKEN", "")
    TD_HDR     = {"Authorization": f"Bearer {TD_TOKEN}"}

    audit_lines = [f"# Post-Standup Audit — {today}\n"]
    synced, skipped, errors = [], [], []

    try:
        # Fetch all MC tasks
        r = _req.get(f"{MC_API_URL}/api/tasks", headers=MC_HDR, timeout=10)
        mc_tasks = r.json() if r.status_code == 200 else []

        # Fetch open Todoist tasks (as a set of IDs)
        td_open_ids: set[str] = set()
        if TD_TOKEN:
            td_r = _req.get("https://api.todoist.com/api/v1/tasks?limit=200", headers=TD_HDR, timeout=10)
            if td_r.status_code == 200:
                for t in td_r.json().get("results", []):
                    td_open_ids.add(str(t["id"]))

        for task in mc_tasks:
            status = task.get("status", "")
            if status in ("done", "blocked"):
                continue
            tid = task.get("todoistId") or task.get("metadata", {}).get("todoistId") if isinstance(task.get("metadata"), dict) else None
            if not tid:
                continue
            # If Todoist task is NOT in the open set → it's been completed
            if str(tid) not in td_open_ids and TD_TOKEN:
                try:
                    patch = _req.patch(
                        f"{MC_API_URL}/api/task",
                        headers=MC_HDR,
                        json={"id": task["_id"], "status": "done"},
                        timeout=10,
                    )
                    if patch.status_code == 200:
                        synced.append(f"- ✅ Synced to done: {task['title'][:70]}")
                    else:
                        errors.append(f"- ⚠️ Patch failed ({patch.status_code}): {task['title'][:60]}")
                except Exception as e:
                    errors.append(f"- ❌ Error patching {task['title'][:50]}: {e}")
            else:
                skipped.append(task["title"][:60])

    except Exception as e:
        audit_lines.append(f"\n❌ Audit crashed: {e}\n")
    else:
        audit_lines.append(f"Synced: {len(synced)} | Skipped (still open): {len(skipped)} | Errors: {len(errors)}\n")
        if synced:
            audit_lines.append("\n## Synced to Done")
            audit_lines.extend(synced)
        if errors:
            audit_lines.append("\n## Errors")
            audit_lines.extend(errors)
        if not synced and not errors:
            audit_lines.append("\n✅ All MC task statuses look correct — nothing to sync.")

    audit_path = f"/data/workspace/logs/standup-audit-{today}.md"
    with open(audit_path, "w") as f:
        f.write("\n".join(audit_lines) + "\n")
    print(f"   Audit complete → {audit_path} | Synced: {len(synced)} | Errors: {len(errors)}")


# === MAIN ===

def main():
    today = today_str()
    disp = today_display()
    tomorrow_dt = datetime.strptime(today, "%Y-%m-%d") + timedelta(days=1)
    tomorrow = tomorrow_dt.strftime("%Y-%m-%d")
    tomorrow_disp = tomorrow_dt.strftime("%a %b %-d")

    print(f"=== Daily Standup: {disp} ===\n")

    # 1. Fetch tasks
    print("1. Fetching Todoist tasks...")
    resp = requests.get("https://api.todoist.com/api/v1/tasks?limit=100", headers=TH, timeout=15)
    tasks = resp.json().get("results", [])
    print(f"   Raw tasks: {len(tasks)}")

    # 0. Process yesterday's standup actions BEFORE building today's view
    yesterday_summary = process_yesterday_actions(tasks)
    # Refresh task list so closed/snoozed tasks don't appear today
    if yesterday_summary.get("closed") or yesterday_summary.get("snoozed"):
        r2 = requests.get("https://api.todoist.com/api/v1/tasks?limit=100", headers=TH, timeout=15)
        tasks = r2.json().get("results", [])
        print(f"   Refreshed task list: {len(tasks)} tasks")

    # 2. Deduplicate
    print("2. Deduplicating...")
    tasks = deduplicate_tasks(tasks)
    print(f"   Unique tasks: {len(tasks)}")

    # 3. Group sub-tasks
    print("3. Grouping sub-tasks...")
    tasks = group_tasks(tasks)

    # 4. Classify and split into two tables
    print("4. Classifying tasks...")
    needs_input = []
    pipeline = []
    overdue_tasks = []

    for task in tasks:
        due_str = task.get("due", {}).get("date", "") if task.get("due") else ""
        section = classify_section(due_str, today)
        task["_section"] = section
        if section == "Overdue":
            overdue_tasks.append(task)
        if is_decided(task, section):
            pipeline.append(task)
        else:
            needs_input.append(task)

    # Sort each list: overdue first, then by priority
    section_order = {"Overdue": 0, "Today": 1, "Upcoming": 2, "Inbox": 3, "Backlog": 4}
    for lst in [needs_input, pipeline]:
        lst.sort(key=lambda t: (section_order.get(t["_section"], 5), -t.get("priority", 1)))

    print(f"   🔥 Needs Input: {len(needs_input)}")
    print(f"   📋 Pipeline: {len(pipeline)}")

    # 5. Get completed tasks
    print("5. Fetching completed tasks...")
    completed = get_completed_tasks()
    print(f"   Completed: {len(completed)}")

    # 6. Create Notion page
    print("6. Creating Notion page...")
    page_id = create_standup_page(disp)

    # 7. Get or create the persistent TMNT Standup Board DB
    print("7. Getting/creating persistent standup DB...")
    persistent_db_id = get_or_create_persistent_db(page_id)

    # 8. Add top blocks (summary callout + blank Tomorrow's Focus + DB link)
    print("8. Adding top blocks...")
    # Read prep state (from standup_prep.py run at 4:30 PM)
    prep_file = f"/data/workspace/logs/standup-prep-{today.strftime('%Y-%m-%d')}.json"
    squad_status = None
    clarifying_questions = None
    if os.path.exists(prep_file):
        try:
            prep = json.load(open(prep_file))
            email_highlights = prep.get("email_highlights", [])
            if email_highlights:
                lines = ["📬 Email items that may affect today's tasks:"]
                for e in email_highlights[:3]:
                    lines.append(f"• {e.get('sender','?')}: {e.get('subject','?')[:70]}")
                clarifying_questions = "\n".join(lines)
            print(f"   Prep state loaded: {prep.get('summary', 'ok')}")
        except Exception as e:
            print(f"   ⚠️ Could not read prep state: {e}")

    # Read agent status files (written by Raphael + Leonardo after 4:30 PM ping)
    # Falls back to "no update received" if files not present
    today_str = today.strftime("%Y-%m-%d")
    squad_lines = []
    for agent, label in [("raphael", "🔴 Raphael"), ("leonardo", "🔵 Leonardo")]:
        path = f"/data/shared/logs/standup-status-{today_str}-{agent}.txt"
        if os.path.exists(path):
            try:
                content = open(path).read().strip()
                if content:
                    short = content[:180] + ("…" if len(content) > 180 else "")
                    squad_lines.append(f"{label}: {short}")
                    print(f"   ✅ {agent} status file found")
                else:
                    squad_lines.append(f"{label}: no update received")
            except Exception:
                squad_lines.append(f"{label}: could not read status file")
        else:
            squad_lines.append(f"{label}: no pre-standup update received")
    squad_status = "\n".join(squad_lines) if squad_lines else None

    # NOTE: tomorrow_task removed — Tomorrow's Focus is BLANK for Guillermo to fill
    add_top_blocks(page_id, disp, tomorrow_disp, completed, len(needs_input), len(pipeline), overdue_tasks,
                   persistent_db_id=persistent_db_id, squad_status=squad_status, clarifying_questions=clarifying_questions)

    # 9. Load existing tasks into cache (one query, prevents duplicates)
    print("9. Loading existing tasks into cache...")
    load_existing_tasks(persistent_db_id)

    # 10. Add Needs Input tasks to persistent DB (sort: 1..N, Overdue P1 first)
    print("10. Adding 'Needs Input' tasks to persistent DB...")
    added1 = 0
    for i, task in enumerate(needs_input, start=1):
        if add_task_to_db_with_retry(persistent_db_id, task, task["_section"], today, "Needs Input", sort_order=i):
            added1 += 1

    # 11. Add Active Pipeline tasks to persistent DB (sort: continues after Needs Input)
    print("11. Adding 'Active Pipeline' tasks to persistent DB...")
    added2 = 0
    pipeline_offset = len(needs_input) + 1
    for i, task in enumerate(pipeline, start=pipeline_offset):
        if add_task_to_db_with_retry(persistent_db_id, task, task["_section"], today, "Active Pipeline", sort_order=i):
            added2 += 1

    # 12. Footer
    print("12. Adding footer...")
    add_footer(page_id)

    # Calendar blocking removed from generation — happens post-review only (process_standup.py)
    cal_blocks = []

    # Summary
    page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
    db_url = f"https://www.notion.so/{persistent_db_id.replace('-', '')}"
    total = added1 + added2
    overdue_count = len(overdue_tasks)
    today_count = sum(1 for t in tasks if t.get("_section") == "Today")

    print(f"\n✅ Standup ready! {total} tasks ({overdue_count} overdue, {today_count} today)")
    print(f"   🔥 Needs Input: {added1} | 📋 Pipeline: {added2}")
    print(f"📄 Page: {page_url}")
    print(f"🗃️  DB:   {db_url}")

    # Build Telegram summary
    tg_lines = []
    if overdue_tasks:
        tg_lines.append("🔥 *Overdue:*")
        for t in overdue_tasks[:3]:
            due = t.get("due", {}).get("date", "")[:10] if t.get("due") else "?"
            tg_lines.append(f"  • {t['content'][:50]} (due {due})")
    if needs_input:
        tg_lines.append(f"\n🎯 *{len(needs_input)} items need your input*")
        for t in needs_input[:3]:
            tg_lines.append(f"  • {t['content'][:50]}")
    if completed:
        tg_lines.append(f"\n✅ *Completed today:* {len(completed)} tasks")

    # Count pre-ticked calendar + MC flags for context
    cal_flagged = sum(1 for t in tasks if should_book_calendar(t, t.get("_section", "Backlog")) and determine_owner(t) == "Guillermo")
    mc_flagged  = sum(1 for t in tasks if should_be_in_mc(t))
    tg_lines.append(f"\n📅 *Calendar blocks queued:* {cal_flagged} (booked after you say 'standup done')")
    tg_lines.append(f"🐢 *MC tasks queued:* {mc_flagged} (created after you say 'standup done')")
    tg_lines.append(f"\n⚠️ *Fill in Tomorrow's Focus first* — ONE item, top of the page")
    tg_lines.append(f"Then review the table and say *standup done*")

    tg_summary = "\n".join(tg_lines) if tg_lines else "All clear — no urgent items"

    # Write state file so process_standup.py can find the page reliably
    state = {
        "date": today,
        "page_id": page_id,
        "page_url": page_url,
        "persistent_db_id": persistent_db_id,
        "db_url": db_url,
        # Legacy keys kept for backward-compat with any readers of this file
        "db1_id": persistent_db_id,
        "db2_id": persistent_db_id,
        "created_at": datetime.now(HKT).isoformat()
    }
    os.makedirs("/data/workspace/logs", exist_ok=True)
    with open("/data/workspace/logs/standup-state.json", "w") as f:
        json.dump(state, f, indent=2)

    # === POST-STANDUP AUDIT ===
    print("\n12. Running post-standup task pool audit...")
    _post_standup_audit(today)

    # Output for caller
    print(f"\n__PAGE_ID__={page_id}")
    print(f"__PAGE_URL__={page_url}")
    print(f"__PERSISTENT_DB_ID__={persistent_db_id}")
    print(f"__DB_URL__={db_url}")
    print(f"__TASK_COUNT__={total}")
    print(f"__NEEDS_INPUT__={added1}")
    print(f"__PIPELINE__={added2}")
    print(f"__OVERDUE__={overdue_count}")
    print(f"__TODAY__={today_count}")
    print(f"__TG_SUMMARY__={tg_summary}")


# === CALENDAR BLOCKING ===

CALENDAR_ID = "guillermo.ginesta@gmail.com"
SA_KEY_FILE = "/data/workspace/credentials/google-service-account.json"

def _get_calendar_token():
    """Get a Google Calendar API access token via service account JWT."""
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        import base64, urllib.parse, urllib.request as ureq
        with open(SA_KEY_FILE) as f:
            sa = json.load(f)
        now = int(time.time())
        header = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b'=')
        payload_data = {"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/calendar",
                        "aud": "https://oauth2.googleapis.com/token", "exp": now+3600, "iat": now}
        payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).rstrip(b'=')
        key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
        sig_input = header + b'.' + payload
        sig = key.sign(sig_input, padding.PKCS1v15(), hashes.SHA256())
        jwt = (sig_input + b'.' + base64.urlsafe_b64encode(sig).rstrip(b'=')).decode()
        data = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}).encode()
        req = ureq.Request("https://oauth2.googleapis.com/token", data=data)
        with ureq.urlopen(req) as r:
            return json.load(r)["access_token"]
    except Exception as e:
        print(f"   ⚠️ Calendar auth failed: {e}")
        return None


def _get_existing_events(token, date_str):
    """Get events for a given date (YYYY-MM-DD) from Guillermo's calendar."""
    import urllib.request as ureq, urllib.parse
    day_start = f"{date_str}T00:00:00+08:00"
    day_end   = f"{date_str}T23:59:59+08:00"
    params = urllib.parse.urlencode({
        "timeMin": day_start, "timeMax": day_end,
        "singleEvents": "true", "orderBy": "startTime"
    })
    url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(CALENDAR_ID)}/events?{params}"
    req = ureq.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with ureq.urlopen(req) as r:
            return json.load(r).get("items", [])
    except Exception:
        return []


def _find_free_slot(events, date_str, duration_hours=1.5):
    """Find a free morning slot on date_str. Returns (start_iso, end_iso) or None."""
    # Candidate slots: 9:00, 9:30, 10:00, 10:30, 11:00, 11:30 HKT
    slots = [(9,0),(9,30),(10,0),(10,30),(11,0),(11,30)]
    # Build list of busy intervals (start, end) in HKT minutes-from-midnight
    busy = []
    for ev in events:
        s = ev.get("start", {}).get("dateTime")
        e = ev.get("end", {}).get("dateTime")
        if not s or not e:
            continue  # all-day
        try:
            s_dt = datetime.fromisoformat(s).astimezone(HKT)
            e_dt = datetime.fromisoformat(e).astimezone(HKT)
            busy.append((s_dt.hour*60+s_dt.minute, e_dt.hour*60+e_dt.minute))
        except Exception:
            continue

    dur_min = int(duration_hours * 60)
    for h, m in slots:
        slot_start = h*60+m
        slot_end   = slot_start + dur_min
        if slot_end > 13*60:  # don't go past 1PM
            continue
        overlap = any(not (slot_end <= bs or slot_start >= be) for bs, be in busy)
        if not overlap:
            s_iso = f"{date_str}T{h:02d}:{m:02d}:00+08:00"
            eh, em = divmod(slot_end, 60)
            e_iso = f"{date_str}T{eh:02d}:{em:02d}:00+08:00"
            return s_iso, e_iso
    return None


def _already_has_focus_block(events, task_name_fragment):
    """Return True if a Molty focus block or task-matching event already exists."""
    frag = task_name_fragment[:25].lower().strip()
    for ev in events:
        summary = ev.get("summary", "").lower()
        desc = ev.get("description", "").lower()
        # Match our own auto-created focus blocks (🎯 prefix)
        if summary.startswith("🎯"):
            return True
        # Match manually-created blocks referencing the same task
        if frag and len(frag) > 5 and frag in summary:
            return True
        # Match if description says "blocked by molty"
        if "molty" in desc and ("focus block" in desc or "standup" in desc):
            return True
    return False


def _create_event(token, summary, description, start_iso, end_iso, color_id="11"):
    import urllib.request as ureq, urllib.parse
    event = {
        "summary": summary, "description": description,
        "start": {"dateTime": start_iso, "timeZone": "Asia/Hong_Kong"},
        "end":   {"dateTime": end_iso,   "timeZone": "Asia/Hong_Kong"},
        "colorId": color_id,
        "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 15}]},
    }
    url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(CALENDAR_ID)}/events"
    req = ureq.Request(url, data=json.dumps(event).encode(), method="POST",
                       headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with ureq.urlopen(req) as r:
        return json.load(r)


def block_week_calendar(all_tasks, today, tomorrow):
    """
    Block Guillermo's calendar for the next 5 working days based on task priority.
    - P1 tasks: 2-hour block, red
    - P2 tasks: 1.5-hour block, yellow
    - One block per day, morning slot (9:00–13:00 HKT)
    - Skips days that already have a focus block for that task
    """
    print("\n12. Blocking calendar for the week...")
    token = _get_calendar_token()
    if not token:
        print("   ⚠️ Skipped — could not authenticate with Google Calendar")
        return []

    # Build working days: tomorrow + next 4 (skip weekends)
    working_days = []
    d = datetime.strptime(tomorrow, "%Y-%m-%d")
    while len(working_days) < 5:
        if d.weekday() < 5:  # Mon–Fri
            working_days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    # Group tasks by their due date, sorted by priority (highest first)
    by_day = defaultdict(list)
    for t in all_tasks:
        due = t.get("due", {}).get("date", "")[:10] if t.get("due") else ""
        if due and due >= tomorrow:
            by_day[due].append(t)
    # Overdue tasks → assign to tomorrow
    for t in all_tasks:
        due = t.get("due", {}).get("date", "")[:10] if t.get("due") else ""
        if due and due < tomorrow and t.get("priority", 4) >= 3:  # P1/P2 overdue
            by_day[tomorrow].append(t)
    for day in by_day:
        by_day[day].sort(key=lambda t: -t.get("priority", 1))

    created = []
    for day in working_days:
        day_tasks = by_day.get(day, [])
        if not day_tasks:
            continue

        # Pick top task for the day
        top = day_tasks[0]
        priority = top.get("priority", 4)
        if priority < 3:  # Only P1 (priority=4) and P2 (priority=3) — Todoist inverts: 4=P1, 3=P2
            continue

        task_name = top["content"]
        events = _get_existing_events(token, day)

        if _already_has_focus_block(events, task_name):
            print(f"   ⏭️  {day}: already has block for '{task_name[:40]}'")
            continue

        duration = 2.0 if priority == 4 else 1.5  # P1=2h, P2=1.5h
        color = "11" if priority == 4 else "5"    # tomato=P1, banana=P2
        slot = _find_free_slot(events, day, duration)

        if not slot:
            print(f"   ⚠️  {day}: no free morning slot for '{task_name[:40]}'")
            continue

        start_iso, end_iso = slot
        p_label = "P1" if priority == 4 else "P2"
        summary = f"🎯 [{p_label}] {task_name[:80]}"
        day_fmt = datetime.strptime(day, "%Y-%m-%d").strftime("%a %b %-d")
        description = (f"Focus block — standup priority for {day_fmt}.\n"
                       f"Blocked automatically by Molty daily standup.")
        try:
            ev = _create_event(token, summary, description, start_iso, end_iso, color)
            print(f"   ✅ {day}: '{task_name[:50]}' → {start_iso[11:16]}–{end_iso[11:16]}")
            created.append({"day": day, "task": task_name, "start": start_iso, "end": end_iso})
        except Exception as e:
            print(f"   ❌ {day}: failed to create event — {e}")

    print(f"   📅 {len(created)} focus block(s) created")
    return created


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        err = f"{type(e).__name__}: {e}"
        print(f"\n❌ Standup crashed: {err}", file=sys.stderr)
        traceback.print_exc()
        alert_telegram_failure(err)
        sys.exit(1)
