#!/bin/bash

# Source credentials
source /data/workspace/credentials/notion.env

# Create Skill Registry Database
echo "Creating Skill Registry Database..."
DATABASE_RESPONSE=$(curl -s -X POST https://api.notion.com/v1/databases \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  -d '{
    "parent": {
      "type": "page_id",
      "page_id": "2fa39dd69afd80be89dae91e20d30a38"
    },
    "title": [
      {
        "type": "text",
        "text": {
          "content": "Skill Registry"
        }
      }
    ],
    "icon": {
      "type": "emoji",
      "emoji": "🧩"
    },
    "is_inline": true,
    "properties": {
      "Skill Name": {
        "title": {}
      },
      "Tier": {
        "select": {
          "options": [
            {"name": "Core", "color": "red"},
            {"name": "Role", "color": "blue"},
            {"name": "Custom", "color": "green"}
          ]
        }
      },
      "Status": {
        "select": {
          "options": [
            {"name": "Evaluating", "color": "yellow"},
            {"name": "Testing", "color": "orange"},
            {"name": "Installed", "color": "green"},
            {"name": "Deprecated", "color": "gray"},
            {"name": "Rejected", "color": "red"}
          ]
        }
      },
      "Owner": {
        "select": {
          "options": [
            {"name": "Molty 🦎", "color": "green"},
            {"name": "Raphael 🔴", "color": "red"},
            {"name": "Pikachu ⚡", "color": "yellow"},
            {"name": "Leonardo 🔵", "color": "blue"},
            {"name": "April 📰", "color": "gray"},
            {"name": "Donatello 🟣", "color": "purple"},
            {"name": "Michelangelo 🟠", "color": "orange"},
            {"name": "Fleet-wide", "color": "default"}
          ]
        }
      },
      "Installed On": {
        "multi_select": {
          "options": [
            {"name": "Molty", "color": "green"},
            {"name": "Raphael", "color": "red"},
            {"name": "Pikachu", "color": "yellow"},
            {"name": "Leonardo", "color": "blue"},
            {"name": "April", "color": "gray"},
            {"name": "Donatello", "color": "purple"},
            {"name": "Michelangelo", "color": "orange"}
          ]
        }
      },
      "Source": {
        "select": {
          "options": [
            {"name": "ClawhHub", "color": "blue"},
            {"name": "Custom Built", "color": "green"},
            {"name": "Community", "color": "yellow"},
            {"name": "Bundled", "color": "gray"}
          ]
        }
      },
      "Security Score": {
        "select": {
          "options": [
            {"name": "✅ Passed", "color": "green"},
            {"name": "⚠️ Conditional", "color": "yellow"},
            {"name": "❌ Failed", "color": "red"},
            {"name": "🔍 Pending", "color": "gray"}
          ]
        }
      },
      "Last Evaluated": {
        "date": {}
      },
      "Notes": {
        "rich_text": {}
      }
    }
  }')

echo "Database Response: $DATABASE_RESPONSE"
DATABASE_ID=$(echo "$DATABASE_RESPONSE" | jq -r '.id')
echo "Database ID: $DATABASE_ID"
echo "Database URL: https://www.notion.so/$DATABASE_ID"

# Skills data
declare -a SKILLS=(
  "weather|Core|Installed|Fleet-wide|Molty|Bundled|✅ Passed||"
  "email|Core|Installed|Fleet-wide|Molty|ClawhHub|✅ Passed||"
  "notion|Core|Installed|Molty 🦎|Molty,Raphael|ClawhHub|✅ Passed||"
  "todoist|Role|Installed|Molty 🦎|Molty|ClawhHub|✅ Passed||"
  "ai-content-guardian|Core|Installed|Fleet-wide|Molty,Raphael|Custom Built|✅ Passed||"
  "bird|Role|Installed|Pikachu ⚡|Molty|Community|⚠️ Conditional|read-only, posting blocked|"
  "last30days|Role|Installed|Pikachu ⚡|Molty|Custom Built|⚠️ Conditional|OOMs on Railway|"
  "task|Role|Installed|Molty 🦎|Molty|ClawhHub|✅ Passed||"
  "todo|Role|Installed|Molty 🦎|Molty|ClawhHub|✅ Passed||"
  "n8n-workflow-automation|Role|Installed|Molty 🦎|Molty|ClawhHub|✅ Passed||"
  "agent-link|Core|Installed|Fleet-wide|Molty,Raphael|Custom Built|✅ Passed||"
  "skill-creator|Core|Installed|Fleet-wide|Molty|Bundled|✅ Passed||"
)

# Create pages for each skill
echo "Creating skill pages..."
for skill in "${SKILLS[@]}"; do
  IFS='|' read -r name tier status owner installed_on source security notes <<< "$skill"
  
  # Convert installed_on to array for multi_select
  if [[ "$installed_on" == *","* ]]; then
    installed_on_json=$(echo "$installed_on" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')
  else
    installed_on_json="[\"$installed_on\"]"
  fi
  
  echo "Creating page for: $name"
  
  PAGE_RESPONSE=$(curl -s -X POST https://api.notion.com/v1/pages \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Content-Type: application/json" \
    -H "Notion-Version: 2022-06-28" \
    -d "{
      \"parent\": {
        \"type\": \"database_id\",
        \"database_id\": \"$DATABASE_ID\"
      },
      \"properties\": {
        \"Skill Name\": {
          \"title\": [
            {
              \"type\": \"text\",
              \"text\": {
                \"content\": \"$name\"
              }
            }
          ]
        },
        \"Tier\": {
          \"select\": {
            \"name\": \"$tier\"
          }
        },
        \"Status\": {
          \"select\": {
            \"name\": \"$status\"
          }
        },
        \"Owner\": {
          \"select\": {
            \"name\": \"$owner\"
          }
        },
        \"Installed On\": {
          \"multi_select\": $(echo "$installed_on_json" | jq '[.[] | {name: .}]')
        },
        \"Source\": {
          \"select\": {
            \"name\": \"$source\"
          }
        },
        \"Security Score\": {
          \"select\": {
            \"name\": \"$security\"
          }
        },
        \"Last Evaluated\": {
          \"date\": {
            \"start\": \"$(date +%Y-%m-%d)\"
          }
        },
        \"Notes\": {
          \"rich_text\": [
            {
              \"type\": \"text\",
              \"text\": {
                \"content\": \"$notes\"
              }
            }
          ]
        }
      }
    }")
  
  PAGE_ID=$(echo "$PAGE_RESPONSE" | jq -r '.id')
  echo "Created page: $name (ID: $PAGE_ID)"
done

echo "Skill Registry Database creation complete!"