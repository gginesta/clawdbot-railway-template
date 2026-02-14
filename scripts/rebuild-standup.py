#!/usr/bin/env python3
"""Rebuild today's standup page with correct template + all Todoist tasks."""
import json, requests, sys

NOTION_API_KEY = "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"
TODOIST_TOKEN = "9a26743814658c9e82d92aa716b46a9b0a2257c4"
PAGE_ID = "30639dd6-9afd-81cd-a604-d1c83ae85ce9"

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
PRIO_MAP = {4: "🔴 P1", 3: "🟡 P2", 2: "🔵 P3", 1: "⚪ P4"}
TODAY = "2026-02-13"

def get_section(task):
    due = task.get("due")
    if not due or not due.get("date"):
        return "Backlog"
    d = due["date"][:10]
    if d < TODAY: return "Overdue"
    elif d == TODAY: return "Today"
    elif d <= "2026-02-20": return "Upcoming"
    else: return "Backlog"

def get_notes(task):
    section = get_section(task)
    pid = task["project_id"]
    notes = []
    if section == "Overdue": notes.append("⚠️ Overdue")
    if pid == "6M5rpCXmg7x7RC2Q": notes.append("Needs triage from Inbox")
    if "Review" in task.get("labels", []): notes.append("Recurring review task")
    return "; ".join(notes) if notes else ""

# Step 1: Add callout first
print("Adding callout...")
resp = requests.patch(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children", headers=NH, json={
    "children": [{
        "object": "block", "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": "Daily Standup \u2014 Thu Feb 13, 2026. Review the table below: set Action dropdown for each task, leave comments, fill in Tomorrow's Priority. Ping Molty \"standup done\" when finished."}}],
            "icon": {"type": "emoji", "emoji": "\U0001f4cb"},
            "color": "default"
        }
    }]
})
print(f"  Callout: {resp.status_code}")

# Step 2: Create inline database
print("Creating Task Review database...")
schema = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "title": [{"type": "text", "text": {"content": "Task Review"}}],
    "is_inline": True,
    "properties": {
        "Task": {"title": {}},
        "Project": {"select": {"options": [{"name": n, "color": c} for n, c in [("Personal 🙂", "blue"), ("Brinc 🔴", "red"), ("Mana Capital 🟠", "orange"), ("Molty's Den 🦎", "green"), ("Inbox 📥", "gray"), ("Ideas 💡", "yellow")]]}},
        "Priority": {"select": {"options": [{"name": "🔴 P1", "color": "red"}, {"name": "🟡 P2", "color": "yellow"}, {"name": "🔵 P3", "color": "blue"}, {"name": "⚪ P4", "color": "default"}]}},
        "Due Date": {"date": {}},
        "Action": {"select": {"options": [{"name": "✅ Keep", "color": "green"}, {"name": "📅 Reschedule", "color": "yellow"}, {"name": "🗑️ Drop", "color": "red"}, {"name": "🔀 Delegate", "color": "blue"}, {"name": "✔️ Done", "color": "green"}]}},
        "Owner": {"select": {"options": [{"name": "Guillermo", "color": "default"}, {"name": "Molty", "color": "green"}, {"name": "Raphael", "color": "red"}, {"name": "Leonardo", "color": "blue"}]}},
        "Section": {"select": {"options": [{"name": "Overdue", "color": "red"}, {"name": "Today", "color": "green"}, {"name": "Upcoming", "color": "blue"}, {"name": "Inbox", "color": "gray"}, {"name": "Backlog", "color": "default"}]}},
        "Time Est.": {"select": {"options": [{"name": "15min", "color": "green"}, {"name": "30min", "color": "blue"}, {"name": "1h", "color": "yellow"}, {"name": "2h+", "color": "red"}]}},
        "Molty's Notes": {"rich_text": {}},
        "Your Comments": {"rich_text": {}},
    }
}
resp = requests.post("https://api.notion.com/v1/databases", headers=NH, json=schema)
if resp.status_code != 200:
    print(f"ERROR creating DB: {resp.status_code} {resp.text}")
    sys.exit(1)
db_id = resp.json()["id"]
print(f"  DB created: {db_id}")

# Step 3: Add remaining blocks (divider, headings)
print("Adding headings...")
resp = requests.patch(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children", headers=NH, json={
    "children": [
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 Tomorrow's Top Priority"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "(Fill in after reviewing tasks)"}}]}},
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🧱 Blockers"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "None reported"}}]}},
    ]
})
print(f"  Headings: {resp.status_code}")

# Step 4: Fetch Todoist tasks
print("Fetching Todoist tasks...")
resp = requests.get("https://api.todoist.com/api/v1/tasks?limit=50", headers=TH)
tasks = resp.json().get("results", [])
print(f"  Got {len(tasks)} tasks")

# Step 5: Add each task to the DB
added = 0
for task in tasks:
    section = get_section(task)
    project = PROJECT_MAP.get(task["project_id"], "Other")
    priority = PRIO_MAP.get(task["priority"], "⚪ P4")
    due_date = task.get("due", {}).get("date", "")[:10] if task.get("due") else None
    notes = get_notes(task)
    
    owner = "Guillermo"
    if task["project_id"] == "6fwH32grqrCJF23R":
        owner = "Molty"
    elif "brinc" in task.get("labels", []):
        owner = "Raphael"
    
    props = {
        "Task": {"title": [{"text": {"content": task["content"]}}]},
        "Project": {"select": {"name": project}},
        "Priority": {"select": {"name": priority}},
        "Section": {"select": {"name": section}},
        "Owner": {"select": {"name": owner}},
    }
    if due_date:
        props["Due Date"] = {"date": {"start": due_date}}
    if notes:
        props["Molty's Notes"] = {"rich_text": [{"text": {"content": notes}}]}
    
    resp = requests.post("https://api.notion.com/v1/pages", headers=NH, json={
        "parent": {"database_id": db_id},
        "properties": props
    })
    if resp.status_code == 200:
        added += 1
    else:
        print(f"  WARN: '{task['content'][:40]}': {resp.status_code}")

print(f"\n✅ Done! Added {added}/{len(tasks)} tasks to Task Review DB.")
print(f"Page: https://www.notion.so/30639dd69afd81cda604d1c83ae85ce9")
