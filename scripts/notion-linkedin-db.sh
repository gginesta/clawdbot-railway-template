#!/bin/bash
# Create LinkedIn Content Tracker database in Notion

export NOTION_API_KEY="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"

curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "2fa39dd69afd80be89dae91e20d30a38"},
    "title": [{"text": {"content": "Brinc LinkedIn Content Tracker"}}],
    "properties": {
      "Title": {"title": {}},
      "Posting Order": {"number": {"format": "number"}},
      "Posted": {"checkbox": {}},
      "Status": {"select": {"options": [{"name": "Draft", "color": "red"}, {"name": "Ready", "color": "yellow"}, {"name": "Posted", "color": "green"}]}},
      "Platform": {"select": {"options": [{"name": "LinkedIn", "color": "blue"}]}},
      "Hook Theme": {"select": {"options": [
        {"name": "AI Adoption", "color": "purple"},
        {"name": "AI Safety", "color": "red"},
        {"name": "Innovation Strategy", "color": "green"},
        {"name": "Working with Startups", "color": "orange"},
        {"name": "Corporate Transformation", "color": "blue"},
        {"name": "Leadership & Teams", "color": "yellow"}
      ]}},
      "Notes": {"rich_text": {}}
    }
  }'
