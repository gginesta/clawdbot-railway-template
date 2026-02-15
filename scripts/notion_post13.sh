#!/bin/bash
# Script to update Notion Post 13 from thread to article format

NOTION_API_KEY="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"
BLOCK_ID="30839dd6-9afd-812c-91a2-d71aeea0e249"
PAGE_ID="30839dd6-9afd-812c-91a2-d71aeea0e249"
NOTION_VERSION="2022-06-28"

HEADERS=(
  -H "Authorization: Bearer $NOTION_API_KEY"
  -H "Notion-Version: $NOTION_VERSION"
  -H "Content-Type: application/json"
)

# Step 1: Get existing child blocks
echo "=== Step 1: Getting existing child blocks ==="
CHILDREN=$(curl -s "https://api.notion.com/v1/blocks/${BLOCK_ID}/children?page_size=100" "${HEADERS[@]}")
echo "$CHILDREN" | jq '.results | length' 2>/dev/null
echo "$CHILDREN" | jq -r '.results[].id' 2>/dev/null > /tmp/block_ids.txt
cat /tmp/block_ids.txt

# Step 2: Delete all existing child blocks
echo ""
echo "=== Step 2: Deleting existing child blocks ==="
while IFS= read -r block_id; do
  if [ -n "$block_id" ]; then
    echo "Deleting block: $block_id"
    curl -s -X DELETE "https://api.notion.com/v1/blocks/${block_id}" "${HEADERS[@]}" | jq -r '.id' 2>/dev/null
  fi
done < /tmp/block_ids.txt

# Step 3: Update page property Type to "Article"
echo ""
echo "=== Step 3: Updating page Type to Article ==="
curl -s -X PATCH "https://api.notion.com/v1/pages/${PAGE_ID}" "${HEADERS[@]}" \
  -d '{
    "properties": {
      "Type": {
        "select": {
          "name": "Article"
        }
      }
    }
  }' | jq -r '.properties.Type.select.name' 2>/dev/null

# Step 4: Add new article content as blocks
echo ""
echo "=== Step 4: Adding new article content ==="
curl -s -X PATCH "https://api.notion.com/v1/blocks/${BLOCK_ID}/children" "${HEADERS[@]}" \
  -d '{
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "I\u2019ve been running AI agents for two weeks now. The promise was simple: set up some smart assistants, automate the busywork, and ship 10x faster. Instead, I\u2019ve discovered something nobody warns you about\u200a\u2014\u200athe moment your AI tools stop working for you and start making you work for them." }
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
            "text": { "content": "I\u2019m calling it " }
          },
          {
            "type": "text",
            "text": { "content": "The Tamagotchi Trap" },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": ": spending all your time feeding and optimizing your digital pets instead of doing actual work. And I fell into it hard." }
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
            "text": { "content": "The Update Spiral" }
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
            "text": { "content": "It started innocently enough. OpenClaw released a new version. Then another. Then another. I went from 2026.2.10 to 2026.2.13 to the latest main branch\u200a\u2014\u200a169+ commits of \u201Cimprovements.\u201D Each update broke something. I spent an entire evening resurrecting dead cron jobs, debugging config changes, and patching things back together. In the time it took me to \u201Cupgrade,\u201D I could have written three blog posts. But hey, at least my agent was running the freshest build, right?" }
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
            "text": { "content": "The Cron Obsession" }
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
            "text": { "content": "I started with three simple cron jobs. Reasonable. Responsible, even. Somehow, over the course of a few days, I ended up with eighteen. Then I spent hours auditing and consolidating them back down to ten, carefully adjusting schedules and eliminating redundancies. At one point I was genuinely debugging why a cron job didn\u2019t fire at 2:17 AM. Let me repeat that: I was losing sleep over whether my automation ran at the exact right minute while I was supposed to be sleeping. The irony was not lost on me\u200a\u2014\u200aeventually." }
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
            "text": { "content": "The Memory Palace Nobody Asked For" }
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
            "text": { "content": "Then came the memory system. I built QMD search, set up Syncthing sync, implemented daily log compaction, added memory guardrails, configured file size caps. A whole architecture for agent memory management. What did my agent actually need to remember? Mostly just what happened yesterday. I built a cathedral when a sticky note would have done the job. Over-engineered doesn\u2019t even begin to cover it." }
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
            "text": { "content": "The Multi-Agent Money Pit" }
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
            "text": { "content": "I spent a full day getting my agents to talk to each other. Discord webhooks, session keys, config patches\u200a\u2014\u200athe works. A beautiful inter-agent communication system. The task I was trying to automate? Something I could have done manually in two hours. Sometimes the \u201Csmart\u201D solution is the dumb one. When your automation takes 4x longer than doing it by hand, you haven\u2019t saved time. You\u2019ve invested it in an imaginary future that may never arrive." }
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
            "text": { "content": "The Perfect Database with Nothing In It" }
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
            "text": { "content": "Instead of writing my second Content Hub post, I redesigned the entire Notion database. Perfect schema. Clean migration. Beautiful structure. Posts published after all that work? Still one. The database was pristine and empty. My priorities were clearly not aligned\u200a\u2014\u200aI was polishing the container instead of filling it." }
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
            "text": { "content": "The Standup System That Stood Still" }
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
            "text": { "content": "My personal favorite: I rewrote my standup system three times. Quality gates, deduplication, sub-task grouping\u200a\u2014\u200athe process became a work of art. The tasks inside it? The same overdue items from a week ago, staring back at me like disappointed parents. I had optimized the view of my failures into a beautifully formatted dashboard of procrastination." }
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
            "text": { "content": "The Pattern" }
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
            "text": { "content": "Looking at all of this, the pattern is painfully clear. There\u2019s a real tension between building the machine and using the machine. And I kept choosing \u201Cmake it perfect\u201D over \u201Cmake it work.\u201D Every hour I spent optimizing infrastructure was an hour I didn\u2019t spend shipping. Every config tweak was a blog post unwritten. Every architectural improvement was a customer conversation I didn\u2019t have." }
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
            "text": { "content": "The best AI setup is the one that\u2019s good enough\u200a\u2014\u200anot perfect. Perfection is a trap, and with AI tools, it\u2019s an especially seductive one because the optimization always " }
          },
          {
            "type": "text",
            "text": { "content": "feels" },
            "annotations": { "italic": true }
          },
          {
            "type": "text",
            "text": { "content": " productive. You\u2019re typing commands, reading logs, solving problems. It looks like work. It feels like work. But it\u2019s not " }
          },
          {
            "type": "text",
            "text": { "content": "your" },
            "annotations": { "italic": true }
          },
          {
            "type": "text",
            "text": { "content": " work." }
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
            "text": { "content": "Escaping the Trap: A Simple Framework" }
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
            "text": { "content": "I\u2019ve since adopted a few rules to keep myself honest:" }
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
            "text": { "content": "The 2-Hour Rule." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " If I\u2019ve spent two hours on infrastructure without shipping anything, I stop. Full stop. I close the terminal, open a doc, and do actual work. The infrastructure will still be there tomorrow." }
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
            "text": { "content": "The Hiring Test." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Would I hire someone to do this task? Would I pay a contractor $100/hour to optimize my cron schedule? If the answer is no, why am I spending my own time on it?" }
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
            "text": { "content": "The Tamagotchi Check." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Before any AI infrastructure work, I ask myself one question: Am I feeding the pet, or am I doing my actual job? Your AI agents should make you more productive, not become your productivity problem." }
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
            "text": { "content": "Ship First, Optimize Later." },
            "annotations": { "bold": true }
          },
          {
            "type": "text",
            "text": { "content": " Get the 80% solution out the door. Your future self can iterate. But your future self can\u2019t publish the blog post you never wrote because you were tweaking configs at midnight." }
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
            "text": { "content": "The Takeaway" }
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
            "text": { "content": "AI agents are incredible tools. But they come with a hidden cost that nobody talks about: the maintenance tax. Every agent you spin up, every automation you build, every integration you configure\u200a\u2014\u200ait all needs feeding. And if you\u2019re not careful, you\u2019ll spend more time maintaining the system than benefiting from it." }
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
            "text": { "content": "Sometimes the best optimization is hitting \u201Cgood enough\u201D and moving on. Sometimes the smartest thing you can do with your AI setup is stop touching it." }
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
            "text": { "content": "Now if you\u2019ll excuse me, I have actual work to do. My Tamagotchi can wait." }
          }
        ]
      }
    }
  ]
}' | jq -r '.results | length' 2>/dev/null

echo ""
echo "=== Done ==="
