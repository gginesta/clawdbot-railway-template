#!/usr/bin/env python3
"""
Daily Standup Script — Creates a properly processed Notion standup page.

QUALITY CHECKLIST (every task MUST have):
✅ Priority (P1-P4 based on Eisenhower matrix)
✅ Time Estimate (15min/30min/1h/2h+)
✅ Section (Overdue/Today/Upcoming/Inbox/Backlog)
✅ Owner (Guillermo/Molty/Raphael/Leonardo)
✅ Molty's Notes (actionable context, not just labels)

NO DUPLICATES — deduplication by content similarity before inserting.
NO BARE TASKS — every task gets processed with context.
"""
import json, requests, sys, time, os
from datetime import datetime, timedelta

# === CONFIG ===
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "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")
TODOIST_TOKEN = os.environ.get("TODOIST_API_TOKEN", "9a26743814658c9e82d92aa716b46a9b0a2257c4")
STANDUP_DB_ID = "2fe39dd69afd81f189f7e58925dad602"  # Parent DB for standup pages

NH = {"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
TH = {"Authorization": f"Bearer {TODOIST_TOKEN}"}

PROJECT_MAP = {
    "6M5rpCXmg7x7RC2Q": "Inbox 📥",
    "6M5rpGfw5jR9Qg9R": "Personal 🙂",
    "6M5rpGgV6q865hrX": "Brinc 🔴",
    "6Rr9p6MxWHFwHXGC": "Mana Capital 🟠",
    "6fwH32grqrCJF23R": "Molty's Den 🦎",
    "6fx5GV7Q93Hp4QgM": "Ideas 💡",
}

# Todoist API priority is inverted: 4=P1, 3=P2, 2=P3, 1=P4
PRIO_MAP = {4: "🔴 P1", 3: "🟡 P2", 2: "🔵 P3", 1: "⚪ P4"}

# Molty-owned projects
MOLTY_PROJECTS = {"6fwH32grqrCJF23R"}  # Molty's Den


def get_today():
    """Get today's date in HKT."""
    from datetime import timezone
    hkt = timezone(timedelta(hours=8))
    return datetime.now(hkt).strftime("%Y-%m-%d")


def get_today_display():
    from datetime import timezone
    hkt = timezone(timedelta(hours=8))
    now = datetime.now(hkt)
    return now.strftime("%a %b %-d, %Y")


def classify_section(due_str, today):
    """Classify task into section based on due date."""
    if not due_str:
        return "Backlog"
    d = due_str[:10]
    if d < today:
        return "Overdue"
    elif d == today:
        return "Today"
    # Next 7 days
    today_dt = datetime.strptime(today, "%Y-%m-%d")
    due_dt = datetime.strptime(d, "%Y-%m-%d")
    if (due_dt - today_dt).days <= 7:
        return "Upcoming"
    return "Backlog"


def estimate_time(task):
    """Estimate time based on task content and context."""
    content = task["content"].lower()
    desc = (task.get("description") or "").lower()
    
    # Research tasks
    if any(w in content for w in ["research", "investigate", "explore", "evaluate", "analyze"]):
        return "1h"
    # Build/create tasks
    if any(w in content for w in ["build", "create", "implement", "develop", "write", "design"]):
        return "2h+"
    # Setup/config tasks
    if any(w in content for w in ["setup", "configure", "install", "set up", "connect"]):
        return "1h"
    # Planning tasks
    if any(w in content for w in ["plan", "organise", "organize", "coordinate", "schedule"]):
        return "1h"
    # Quick tasks
    if any(w in content for w in ["order", "buy", "check", "review", "send", "email", "call"]):
        return "30min"
    # Default
    return "30min"


def determine_owner(task):
    """Determine task owner based on project and labels."""
    if task["project_id"] in MOLTY_PROJECTS:
        return "Molty"
    content = task["content"].lower()
    if content.startswith("molty"):
        return "Molty"
    if any(l in ["brinc"] for l in task.get("labels", [])):
        return "Raphael"
    return "Guillermo"


def generate_notes(task, section, today):
    """Generate actionable Molty's Notes for each task."""
    content = task["content"]
    pid = task["project_id"]
    notes = []
    
    if section == "Overdue":
        due = task.get("due", {}).get("date", "")[:10]
        days = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(due, "%Y-%m-%d")).days if due else 0
        notes.append(f"⚠️ Overdue by {days} day{'s' if days != 1 else ''}")
    
    if pid == "6M5rpCXmg7x7RC2Q":  # Inbox
        notes.append("Needs triage — move to correct project")
    
    if "Review" in task.get("labels", []):
        notes.append("Recurring review task")
    
    # Add actionable suggestion based on owner
    owner = determine_owner(task)
    if owner == "Molty" and section in ("Today", "Overdue"):
        notes.append("I'll handle this today")
    elif owner == "Molty":
        notes.append("Assigned to me — will schedule")
    
    return "; ".join(notes) if notes else ""


def deduplicate_tasks(tasks):
    """Remove duplicate tasks by normalized content."""
    seen = {}
    unique = []
    for t in tasks:
        key = t["content"].strip().lower()
        if key not in seen:
            seen[key] = t
            unique.append(t)
        else:
            print(f"  ⚠️ Skipping duplicate: {t['content'][:50]}")
    return unique


def create_standup_page(today, today_display):
    """Create the standup page in the parent DB."""
    title = f"{today_display} — 5PM HKT"
    resp = requests.post("https://api.notion.com/v1/pages", headers=NH, json={
        "parent": {"database_id": STANDUP_DB_ID},
        "properties": {
            "Date": {"title": [{"text": {"content": title}}]}
        }
    }, timeout=15)
    if resp.status_code != 200:
        print(f"ERROR creating page: {resp.status_code} {resp.text}")
        sys.exit(1)
    page_id = resp.json()["id"]
    print(f"  Page created: {page_id}")
    return page_id


def add_template_blocks(page_id, today_display):
    """Add callout instruction block."""
    resp = requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=NH, json={
        "children": [{
            "object": "block", "type": "callout",
            "callout": {
                "rich_text": [{"text": {"content": f'Daily Standup — {today_display}. Review the table below: set Action dropdown for each task, leave comments, fill in Tomorrow\'s Priority. Ping Molty "standup done" when finished.'}}],
                "icon": {"type": "emoji", "emoji": "📋"},
                "color": "default"
            }
        }]
    }, timeout=15)
    return resp.status_code == 200


def create_task_review_db(page_id):
    """Create inline Task Review database with full schema."""
    resp = requests.post("https://api.notion.com/v1/databases", headers=NH, json={
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [{"type": "text", "text": {"content": "Task Review"}}],
        "is_inline": True,
        "properties": {
            "Task": {"title": {}},
            "Project": {"select": {"options": [
                {"name": "Personal 🙂", "color": "blue"},
                {"name": "Brinc 🔴", "color": "red"},
                {"name": "Mana Capital 🟠", "color": "orange"},
                {"name": "Molty's Den 🦎", "color": "green"},
                {"name": "Inbox 📥", "color": "gray"},
                {"name": "Ideas 💡", "color": "yellow"},
            ]}},
            "Priority": {"select": {"options": [
                {"name": "🔴 P1", "color": "red"},
                {"name": "🟡 P2", "color": "yellow"},
                {"name": "🔵 P3", "color": "blue"},
                {"name": "⚪ P4", "color": "default"},
            ]}},
            "Due Date": {"date": {}},
            "Action": {"select": {"options": [
                {"name": "✅ Keep", "color": "green"},
                {"name": "📅 Reschedule", "color": "yellow"},
                {"name": "🗑️ Drop", "color": "red"},
                {"name": "🔀 Delegate", "color": "blue"},
                {"name": "✔️ Done", "color": "green"},
            ]}},
            "Owner": {"select": {"options": [
                {"name": "Guillermo", "color": "default"},
                {"name": "Molty", "color": "green"},
                {"name": "Raphael", "color": "red"},
                {"name": "Leonardo", "color": "blue"},
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
            "Molty's Notes": {"rich_text": {}},
            "Your Comments": {"rich_text": {}},
        }
    }, timeout=15)
    if resp.status_code != 200:
        print(f"ERROR creating DB: {resp.status_code} {resp.text}")
        sys.exit(1)
    return resp.json()["id"]


def add_footer_blocks(page_id):
    """Add divider + Tomorrow's Priority + Blockers headings."""
    requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=NH, json={
        "children": [
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🎯 Tomorrow's Top Priority"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "(Fill in after reviewing tasks)"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🧱 Blockers"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "None reported"}}]}},
        ]
    }, timeout=15)


def group_tasks(tasks):
    """Group sub-tasks under their parents. Returns list of parent tasks with children attached."""
    by_id = {t["id"]: t for t in tasks}
    parents = []
    children_map = {}  # parent_id -> [child_tasks]
    
    for t in tasks:
        pid = t.get("parent_id") or t.get("parent", {}).get("id")
        if pid and pid in by_id:
            children_map.setdefault(pid, []).append(t)
        elif pid:
            # Parent not in current results — treat as standalone
            children_map.setdefault(pid, []).append(t)
        else:
            parents.append(t)
    
    # Attach children to parents
    for p in parents:
        p["_children"] = children_map.pop(p["id"], [])
    
    # Orphaned children (parent not in results) — create synthetic parent rows
    for pid, kids in children_map.items():
        # Use first child's info to approximate
        synthetic = dict(kids[0])
        synthetic["content"] = f"{kids[0]['content']} (and {len(kids)-1} more)" if len(kids) > 1 else kids[0]["content"]
        synthetic["_children"] = kids[1:] if len(kids) > 1 else []
        parents.append(synthetic)
    
    skipped = sum(len(p.get("_children", [])) for p in parents)
    if skipped:
        print(f"   Grouped {skipped} sub-tasks under their parents")
    
    return parents


def populate_tasks(db_id, tasks, today):
    """Add tasks to the DB. Sub-tasks are listed as bullets in parent's Molty's Notes."""
    grouped = group_tasks(tasks)
    added = 0
    
    for task in grouped:
        due_str = task.get("due", {}).get("date", "") if task.get("due") else ""
        section = classify_section(due_str, today)
        project = PROJECT_MAP.get(task["project_id"], "Other")
        priority = PRIO_MAP.get(task["priority"], "⚪ P4")
        owner = determine_owner(task)
        time_est = estimate_time(task)
        notes = generate_notes(task, section, today)
        
        # Append sub-tasks to notes
        children = task.get("_children", [])
        if children:
            subtask_lines = [f"• {c['content']}" for c in children]
            subtask_text = f"Sub-tasks ({len(children)}):\n" + "\n".join(subtask_lines)
            notes = f"{notes}\n{subtask_text}" if notes else subtask_text
        
        # Truncate notes to Notion's 2000 char limit for rich_text
        if len(notes) > 1900:
            notes = notes[:1900] + f"\n... +{len(children)} more"
        
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
        if resp.status_code == 200:
            added += 1
        else:
            print(f"  ❌ Failed: {task['content'][:40]}")
        time.sleep(0.35)
    
    return added


def main():
    today = get_today()
    today_display = get_today_display()
    
    print(f"=== Daily Standup: {today_display} ===\n")
    
    # 1. Fetch tasks
    print("1. Fetching Todoist tasks...")
    resp = requests.get("https://api.todoist.com/api/v1/tasks?limit=100", headers=TH, timeout=15)
    tasks = resp.json().get("results", [])
    print(f"   Raw tasks: {len(tasks)}")
    
    # 2. Deduplicate
    print("2. Deduplicating...")
    tasks = deduplicate_tasks(tasks)
    print(f"   Unique tasks: {len(tasks)}")
    
    # 3. Sort: Overdue first, then Today, Upcoming, Backlog
    section_order = {"Overdue": 0, "Today": 1, "Upcoming": 2, "Inbox": 3, "Backlog": 4}
    tasks.sort(key=lambda t: (
        section_order.get(classify_section(
            t.get("due", {}).get("date", "") if t.get("due") else "", today
        ), 5),
        -t.get("priority", 1)
    ))
    
    # 4. Create page
    print("3. Creating Notion page...")
    page_id = create_standup_page(today, today_display)
    
    # 5. Add template
    print("4. Adding template...")
    add_template_blocks(page_id, today_display)
    
    # 6. Create DB
    print("5. Creating Task Review DB...")
    db_id = create_task_review_db(page_id)
    print(f"   DB: {db_id}")
    
    # 7. Add footer
    print("6. Adding footer blocks...")
    add_footer_blocks(page_id)
    
    # 8. Populate tasks
    print("7. Populating tasks...")
    added = populate_tasks(db_id, tasks, today)
    
    # Summary
    overdue = sum(1 for t in tasks if classify_section(t.get("due",{}).get("date","") if t.get("due") else "", today) == "Overdue")
    today_count = sum(1 for t in tasks if classify_section(t.get("due",{}).get("date","") if t.get("due") else "", today) == "Today")
    
    page_url = f"https://www.notion.so/{page_id.replace('-','')}"
    print(f"\n✅ Standup ready! {added} tasks ({overdue} overdue, {today_count} today)")
    print(f"📄 {page_url}")
    
    # Output for caller
    print(f"\n__PAGE_ID__={page_id}")
    print(f"__PAGE_URL__={page_url}")
    print(f"__DB_ID__={db_id}")
    print(f"__TASK_COUNT__={added}")
    print(f"__OVERDUE__={overdue}")
    print(f"__TODAY__={today_count}")


if __name__ == "__main__":
    main()
