#!/bin/bash
# Update Post 5 on Notion - Rewrite from Thread to Article format
# Page ID: 30739dd6-9afd-8169-a211-d06d6436a140

NOTION_API_KEY="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"
PAGE_ID="30739dd69afd8169a211d06d6436a140"
NOTION_VERSION="2022-06-28"

HEADERS=(
  -H "Authorization: Bearer $NOTION_API_KEY"
  -H "Notion-Version: $NOTION_VERSION"
  -H "Content-Type: application/json"
)

echo "=== Step 1: Get existing page ==="
curl -s "https://api.notion.com/v1/pages/$PAGE_ID" "${HEADERS[@]}" | python3 -m json.tool 2>/dev/null || curl -s "https://api.notion.com/v1/pages/$PAGE_ID" "${HEADERS[@]}"

echo ""
echo "=== Step 2: Get existing child blocks ==="
CHILDREN=$(curl -s "https://api.notion.com/v1/blocks/$PAGE_ID/children?page_size=100" "${HEADERS[@]}")
echo "$CHILDREN" | python3 -m json.tool 2>/dev/null || echo "$CHILDREN"

# Extract block IDs to delete
BLOCK_IDS=$(echo "$CHILDREN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for block in data.get('results', []):
    print(block['id'])
" 2>/dev/null)

echo ""
echo "=== Step 3: Delete existing child blocks ==="
if [ -n "$BLOCK_IDS" ]; then
  for BLOCK_ID in $BLOCK_IDS; do
    echo "Deleting block: $BLOCK_ID"
    curl -s -X DELETE "https://api.notion.com/v1/blocks/$BLOCK_ID" "${HEADERS[@]}" | python3 -c "import json,sys; d=json.load(sys.stdin); print('  Deleted:', d.get('id','unknown'))" 2>/dev/null
  done
else
  echo "No blocks to delete (or couldn't parse)"
fi

echo ""
echo "=== Step 4: Update page Type property to Article ==="
# Try both select and multi_select formats
UPDATE_RESULT=$(curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" "${HEADERS[@]}" \
  -d '{
    "properties": {
      "Type": {
        "select": {
          "name": "Article"
        }
      }
    }
  }')
echo "$UPDATE_RESULT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if 'object' in d and d['object'] == 'error':
    print('Select format failed:', d.get('message',''))
else:
    print('Type updated to Article successfully')
" 2>/dev/null || echo "$UPDATE_RESULT"

echo ""
echo "=== Step 5: Add new article content as blocks ==="
curl -s -X PATCH "https://api.notion.com/v1/blocks/$PAGE_ID/children" "${HEADERS[@]}" \
  -d '{
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "My first AI agent crashed seven hours after launch. The culprit? A missing comma in a config file. I spent another twelve hours on January 31st just getting it back online — Googling error messages, pasting logs into Claude, and feeling like I had no business touching any of this." },
            "annotations": { "italic": true }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Today, I run three AI agents around the clock. They coordinate my schedule, handle deal flow, run research, and send me a daily standup every evening at 5PM. I still can'\''t code. Here'\''s how I got here." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Why I Needed AI Agents in the First Place" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "I work in venture capital. On any given day, I'\''m juggling deal memos, reviewing pitch decks, chasing portfolio updates, and doing market research. The workload is relentless, and every shortcut matters." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "So when AI agents started trending, I was excited. Finally — automation that could actually think. But every tutorial I found assumed I could code. \"Just clone this repo.\" \"Modify the Python script.\" \"Set up a Docker container.\" I know enough about technology to break things, but not nearly enough to fix them. Every guide felt like it was written for someone else." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The Breakthrough: Writing Instructions, Not Code" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Everything changed when I discovered the OpenClaw framework. The concept was simple: write your agent'\''s instructions in plain markdown — like you'\''re writing a document, not programming — and deploy it to Railway with a single command. No Docker. No API wrangling. No \"just modify the Python.\" For the first time, I'\''d found a tool that felt like it was actually built for people like me." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The First Month: From Clueless to Operational" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Week one was pure education. I read every piece of documentation I could find, watched YouTube tutorials, and leaned heavily on Claude to explain error messages I didn'\''t understand. It was slow, sometimes frustrating, but I was learning." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "By week two, I had my first agent — Molty 🦎 — actually running. And then crashing. And running again. And crashing again. But each crash taught me something, and each fix made me a little more confident." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Week three was the turning point. I set up daily standups — automated check-ins at 5PM sharp — and when they actually started working, something clicked. This wasn'\''t a toy anymore. This was a system. By the end of week four, I had three agents deployed and running 24/7." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Meet the Squad" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "My current team consists of three AI agents, each with a distinct role:" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Molty 🦎 — The Coordinator." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Manages schedules, sets priorities, and runs the daily standup. Think of Molty as the team lead who keeps everything on track." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Raphael 🔴 — The Brinc Operator." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Handles deal flow, portfolio updates, and day-to-day VC operations. The workhorse of the team." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Leonardo 🔵 — The Researcher." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Runs market research, explores new ventures, and digs into emerging trends. The brains behind the strategy." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "They communicate with each other through Discord, track their work in Notion, and manage tasks in Todoist. It'\''s a real workflow — not a demo." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The Honest Framework That Actually Works" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "If you'\''re thinking about doing something similar, here'\''s the framework I'\''d recommend — stripped of all the hype:" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "numbered_list_item",
      "numbered_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Pick ONE task you hate doing." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Don'\''t try to automate everything at once. Find the one repetitive thing that eats your time and start there." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "numbered_list_item",
      "numbered_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Write instructions like you'\''re training an intern." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Be specific. Be clear. If a smart 22-year-old couldn'\''t follow your instructions, neither can an AI agent." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "numbered_list_item",
      "numbered_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Test on OpenClaw + Railway (free tier)." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " You don'\''t need to spend money to see if this works for you. Start free. Prove the concept." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "numbered_list_item",
      "numbered_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Fix what breaks." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " It will break. That'\''s not failure — that'\''s iteration. Every crash is a lesson." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "numbered_list_item",
      "numbered_list_item": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Scale once it works." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Only add more agents or more tasks once your first one is running reliably. Resist the urge to build too fast." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "What My Day Actually Looks Like Now" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Here'\''s what I do: write plain English instructions, review my agents'\'' output, and make decisions. That'\''s it." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "Here'\''s what I don'\''t do: touch code, manage servers, or debug APIs. I'\''m not a technical founder playing engineer. I'\''m a VC who found a way to get leverage without learning to program." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The total cost? $59 per week for all three agents running 24/7. That'\''s less than a single freelancer for a few hours, and my agents don'\''t take weekends off." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "A Reality Check" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "I want to be honest: this isn'\''t magic, and it isn'\''t perfect. I still ping Claude when something breaks. My agents make mistakes. They sometimes miss context or need a nudge in the right direction." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "But they handle about 60% of my routine work — and they do it while I sleep. When Molty sends the daily standup at 5PM, I actually know what happened that day without having to chase updates from a dozen different places. That alone has been transformative." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The Real Takeaway" }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "The magic isn'\''t the AI itself. It'\''s having systems that work without you. Systems that run in the background, handle the boring stuff, and free you up to focus on what actually matters — the thinking, the relationships, the decisions that move the needle." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "If there'\''s a repetitive task you hate, you can probably agent-ify it. Even if you don'\''t code. Start with one. Make it work. Then scale." }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "divider",
      "divider": {}
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "What'\''s the one task you'\''d want an AI agent to handle for you? I'\''m always curious what others are thinking about automating — feel free to reach out." },
            "annotations": { "italic": true }
          }
        ]
      }
    }
  ]
}'

echo ""
echo "=== Done ==="
