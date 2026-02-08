#!/bin/bash

echo "🧩 Creating Molty's Skill Management System in Notion..."
echo "=================================================="

# Check if credentials exist
if [[ ! -f "/data/workspace/credentials/notion.env" ]]; then
    echo "❌ Error: /data/workspace/credentials/notion.env not found!"
    echo "Please create it with: NOTION_API_KEY=your_actual_key"
    exit 1
fi

# Source credentials
source /data/workspace/credentials/notion.env

if [[ -z "$NOTION_API_KEY" || "$NOTION_API_KEY" == "your_notion_api_key_here" ]]; then
    echo "❌ Error: NOTION_API_KEY not set or still placeholder!"
    echo "Please edit /data/workspace/credentials/notion.env with your actual API key"
    exit 1
fi

echo "✅ Credentials loaded"

# Execute both tasks
echo ""
echo "🗄️  TASK 1: Creating Skill Registry Database..."
bash /data/workspace/notion-skill-registry-api.sh

echo ""
echo "📋 TASK 2: Creating Skill Evaluation Checklist..."  
bash /data/workspace/notion-checklist-api.sh

echo ""
echo "🎉 Molty's Skill Management System created successfully!"
echo ""
echo "📍 Both items should now appear under Molty's Mission Control:"
echo "   https://www.notion.so/2fa39dd69afd80be89dae91e20d30a38"