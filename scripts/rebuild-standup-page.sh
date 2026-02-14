#!/bin/bash
# Rebuild today's standup page with correct template
NOTION_API_KEY="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"
PAGE_ID="30639dd6-9afd-81cd-a604-d1c83ae85ce9"
H="Authorization: Bearer $NOTION_API_KEY"
V="Notion-Version: 2022-06-28"
CT="Content-Type: application/json"

# Step 1: Add callout + child_database + divider + headings
echo "=== Adding page blocks ==="
RESP=$(curl -s -X PATCH "https://api.notion.com/v1/blocks/$PAGE_ID/children" \
  -H "$H" -H "$V" -H "$CT" \
  -d '{
  "children": [
    {
      "object": "block",
      "type": "callout",
      "callout": {
        "rich_text": [{"type": "text", "text": {"content": "Daily Standup — Thu Feb 13, 2026. Review the table below: set Action dropdown for each task, leave comments, fill in Tomorrow'\''s Priority. Ping Molty \"standup done\" when finished."}}],
        "icon": {"type": "emoji", "emoji": "📋"},
        "color": "default"
      }
    },
    {
      "object": "block",
      "type": "child_database",
      "child_database": {
        "title": "Task Review"
      }
    },
    {
      "object": "block",
      "type": "divider",
      "divider": {}
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "🎯 Tomorrow'\''s Top Priority"}}]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "(Fill in after reviewing tasks)"}}]
      }
    },
    {
      "object": "block",
      "type": "divider",
      "divider": {}
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [{"type": "text", "text": {"content": "🧱 Blockers"}}]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "None reported"}}]
      }
    }
  ]
}')

echo "$RESP" | jq '[.results[] | {id, type}]'

# Extract the child_database ID
DB_ID=$(echo "$RESP" | jq -r '.results[] | select(.type=="child_database") | .id')
echo "=== New DB ID: $DB_ID ==="

# Step 2: Configure DB schema (add properties to match template)
echo "=== Configuring DB properties ==="
curl -s -X PATCH "https://api.notion.com/v1/databases/$DB_ID" \
  -H "$H" -H "$V" -H "$CT" \
  -d '{
  "properties": {
    "Project": {"select": {"options": [{"name": "Personal 🙂", "color": "blue"}, {"name": "Brinc 🔴", "color": "red"}, {"name": "Mana Capital 🟠", "color": "orange"}, {"name": "Molty'\''s Den 🦎", "color": "green"}, {"name": "Inbox 📥", "color": "gray"}, {"name": "Ideas 💡", "color": "yellow"}]}},
    "Priority": {"select": {"options": [{"name": "🔴 P1", "color": "red"}, {"name": "🟡 P2", "color": "yellow"}, {"name": "🔵 P3", "color": "blue"}, {"name": "⚪ P4", "color": "default"}]}},
    "Due Date": {"date": {}},
    "Action": {"select": {"options": [{"name": "✅ Keep", "color": "green"}, {"name": "📅 Reschedule", "color": "yellow"}, {"name": "🗑️ Drop", "color": "red"}, {"name": "🔀 Delegate", "color": "blue"}, {"name": "✔️ Done", "color": "green"}]}},
    "Owner": {"select": {"options": [{"name": "Guillermo", "color": "default"}, {"name": "Molty", "color": "green"}, {"name": "Raphael", "color": "red"}, {"name": "Leonardo", "color": "blue"}]}},
    "Section": {"select": {"options": [{"name": "Overdue", "color": "red"}, {"name": "Today", "color": "green"}, {"name": "Upcoming", "color": "blue"}, {"name": "Inbox", "color": "gray"}, {"name": "Backlog", "color": "default"}]}},
    "Time Est.": {"select": {"options": [{"name": "15min", "color": "green"}, {"name": "30min", "color": "blue"}, {"name": "1h", "color": "yellow"}, {"name": "2h+", "color": "red"}]}},
    "Molty'\''s Notes": {"rich_text": {}},
    "Your Comments": {"rich_text": {}}
  }
}' | jq '{id, title: .title[0].plain_text}'

echo "=== DB configured. Now adding tasks... ==="
echo "$DB_ID"
