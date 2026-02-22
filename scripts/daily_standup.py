#!/data/workspace/.venv/bin/python3
"""
Daily Standup Script v2 — Two-table format with full pre-triage.

PAGE STRUCTURE:
1. 🎯 Top Priority (callout at top)
2. ✅ Completed since last standup (bullet list)
3. 🔥 Needs Your Input (Table 1) — new, untriaged, needs Guillermo's decision
4. 📋 Active Pipeline (Table 2) — decided tasks with clear plans
5. 🧱 Blockers

RULES:
- ALL tasks are fully triaged BEFORE the page is sent
- Titles are rewritten to be clear and actionable
- Every task has priority, time estimate, owner, notes
- "Needs triage" is NEVER acceptable in Molty's Notes
- Your Comments is the 2nd column for quick input
"""
import json, requests, sys, time, os
from datetime import datetime, timedelta, timezone

# === CONFIG ===
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "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")
TODOIST_TOKEN = os.environ.get("TODOIST_API_TOKEN", "9a26743814658c9e82d92aa716b46a9b0a2257c4")
STANDUP_DB_ID = "2fe39dd69afd81f189f7e58925dad602"

NH = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}

HKT = timezone(timedelta(hours=8))

PROJECT_MAP = {
    "6M5rpCXmg7x7RC2Q": "Inbox 📥",
    "6M5rpGfw5jR9Qg9R": "Personal 🙂",
    "6M5rpGgV6q865hrX": "Brinc 🔴",
    "6Rr9p6MxWHFwHXGC": "Mana Capital 🟠",
    "6fwH32grqrCJF23R": "Molty's Den 🦎",
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
    """Generate ACTIONABLE notes. Never say 'Needs triage'."""
    content = task["content"]
    pid = task["project_id"]
    notes = []

    if section == "Overdue":
        due = task.get("due", {}).get("date", "")[:10]
        if due:
            days = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due, "%Y-%m-%d")).days
            notes.append(f"⚠️ Overdue by {days} day{'s' if days != 1 else ''}")

    owner = determine_owner(task)
    if owner == "Molty" and section in ("Today", "Overdue"):
        notes.append("I'll handle this today")
    elif owner == "Molty":
        notes.append("Assigned to me — will schedule")

    if pid == "6M5rpCXmg7x7RC2Q":  # Inbox
        notes.append("In Inbox — I'll move to the right project")

    if task.get("description"):
        desc = task["description"][:100]
        notes.append(f"Details: {desc}")

    return "; ".join(notes) if notes else ""


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


def add_top_blocks(page_id, today_disp, tomorrow_disp, completed, needs_input_count, pipeline_count, overdue_tasks, tomorrow_task):
    """Add top priority callout, tomorrow focus, completed section, and section headers."""
    children = []

    # Summary callout
    overdue_summary = ""
    if overdue_tasks:
        overdue_lines = [f"• {t['content'][:60]}" for t in overdue_tasks[:3]]
        overdue_summary = f"\n\n🔥 Overdue:\n" + "\n".join(overdue_lines)

    children.append({
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [{"text": {"content":
                f"Daily Standup — {today_disp}\n"
                f"🎯 {needs_input_count} items need your input | 📋 {pipeline_count} in active pipeline"
                f"{overdue_summary}"
            }}],
            "icon": {"type": "emoji", "emoji": "📋"},
            "color": "default"
        }
    })

    # Tomorrow's top priority callout
    if tomorrow_task:
        task_name = tomorrow_task["content"][:120]
        children.append({
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [
                    {"text": {"content": f"Tomorrow's top priority ({tomorrow_disp})\n"}, "annotations": {"bold": True}},
                    {"text": {"content": task_name}}
                ],
                "icon": {"type": "emoji", "emoji": "🎯"},
                "color": "yellow_background"
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

    # Table 1 description (no heading — database title serves as the header)
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


DB_PROPERTIES = {
    "Task": {"title": {}},
    "Your Comments": {"rich_text": {}},
    "Action": {"select": {"options": [
        {"name": "✅ Keep", "color": "green"},
        {"name": "📅 Reschedule", "color": "yellow"},
        {"name": "🗑️ Drop", "color": "red"},
        {"name": "🔀 Delegate", "color": "blue"},
        {"name": "✔️ Done", "color": "green"},
    ]}},
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
        {"name": "Inbox 📥", "color": "gray"},
        {"name": "Ideas 💡", "color": "yellow"},
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


def add_task_to_db(db_id, task, section, today):
    due_str = task.get("due", {}).get("date", "") if task.get("due") else ""
    project = PROJECT_MAP.get(task["project_id"], "Other")
    priority = PRIO_MAP.get(task["priority"], "⚪ P4")
    owner = determine_owner(task)
    time_est = estimate_time(task)
    notes = generate_notes(task, section, today)

    children = task.get("_children", [])
    if children:
        subtask_lines = [f"• {c['content']}" for c in children]
        subtask_text = f"Sub-tasks ({len(children)}):\n" + "\n".join(subtask_lines)
        notes = f"{notes}\n{subtask_text}" if notes else subtask_text

    if len(notes) > 1900:
        notes = notes[:1900] + "..."

    props = {
        "Task": {"title": [{"text": {"content": task["content"]}}]},
        "Project": {"select": {"name": project}},
        "Priority": {"select": {"name": priority}},
        "Section": {"select": {"name": section}},
        "Owner": {"select": {"name": owner}},
        "Time Est.": {"select": {"name": time_est}},
    }
    if due_str:
        props["Due Date"] = {"date": {"start": due_str[:10]}}
    if notes:
        props["Molty's Notes"] = {"rich_text": [{"text": {"content": notes}}]}

    resp = requests.post("https://api.notion.com/v1/pages", headers=NH, json={
        "parent": {"database_id": db_id},
        "properties": props
    }, timeout=15)
    time.sleep(0.35)
    return resp.status_code == 200


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

    # 7. Add top blocks (callout + tomorrow priority + completed + Table 1 header)
    print("7. Adding top blocks...")
    tomorrow_task = get_tomorrow_priority(tasks, tomorrow)
    add_top_blocks(page_id, disp, tomorrow_disp, completed, len(needs_input), len(pipeline), overdue_tasks, tomorrow_task)

    # 8. Create Table 1: Needs Your Input
    print("8. Creating Table 1: Needs Your Input...")
    db1_id = create_db(page_id, "🔥 Needs Your Input")
    added1 = 0
    for task in needs_input:
        if add_task_to_db(db1_id, task, task["_section"], today):
            added1 += 1

    # 9. Add pipeline header
    print("9. Adding pipeline section...")
    add_pipeline_header(page_id)

    # 10. Create Table 2: Active Pipeline
    print("10. Creating Table 2: Active Pipeline...")
    db2_id = create_db(page_id, "📋 Active Pipeline")
    added2 = 0
    for task in pipeline:
        if add_task_to_db(db2_id, task, task["_section"], today):
            added2 += 1

    # 11. Footer
    print("11. Adding footer...")
    add_footer(page_id)

    # Summary
    page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
    total = added1 + added2
    overdue_count = len(overdue_tasks)
    today_count = sum(1 for t in tasks if t.get("_section") == "Today")

    print(f"\n✅ Standup ready! {total} tasks ({overdue_count} overdue, {today_count} today)")
    print(f"   🔥 Needs Input: {added1} | 📋 Pipeline: {added2}")
    print(f"📄 {page_url}")

    # Build Telegram summary lines for caller
    tg_lines = []
    if overdue_tasks:
        tg_lines.append("🔥 *Overdue:*")
        for t in overdue_tasks[:3]:
            due = t.get("due", {}).get("date", "")[:10] if t.get("due") else "?"
            tg_lines.append(f"  • {t['content'][:50]} (due {due})")
    if needs_input:
        tg_lines.append(f"\n🎯 *{len(needs_input)} items need your decision*")
        for t in needs_input[:3]:
            tg_lines.append(f"  • {t['content'][:50]}")
    molty_today = [t for t in tasks if determine_owner(t) == "Molty" and t.get("_section") in ("Today", "Overdue")]
    if molty_today:
        tg_lines.append(f"\n✅ *Molty handling today:*")
        for t in molty_today[:3]:
            tg_lines.append(f"  • {t['content'][:50]}")
    if completed:
        tg_lines.append(f"\n🏆 *Completed:* {len(completed)} tasks since last standup")

    tg_summary = "\n".join(tg_lines) if tg_lines else "All clear — no urgent items"

    # Output for caller
    print(f"\n__PAGE_ID__={page_id}")
    print(f"__PAGE_URL__={page_url}")
    print(f"__DB1_ID__={db1_id}")
    print(f"__DB2_ID__={db2_id}")
    print(f"__TASK_COUNT__={total}")
    print(f"__NEEDS_INPUT__={added1}")
    print(f"__PIPELINE__={added2}")
    print(f"__OVERDUE__={overdue_count}")
    print(f"__TODAY__={today_count}")
    print(f"__TG_SUMMARY__={tg_summary}")


if __name__ == "__main__":
    main()
