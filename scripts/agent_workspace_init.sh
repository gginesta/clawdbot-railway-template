#!/bin/bash

# Define agent workspaces
AGENTS=(
    "raphael:/data/workspace-brinc"
    "leonardo:/data/workspace-cerebro"
)

# Ensure QMD is installed
echo "🔧 Installing QMD globally..."
npm install -g qmd || bun install -g qmd

# Create workspaces and copy necessary configurations
for agent_config in "${AGENTS[@]}"; do
    IFS=':' read -r agent workspace <<< "$agent_config"
    
    echo "🏗️ Initializing workspace for $agent at $workspace"
    
    # Create workspace directory
    mkdir -p "$workspace"
    
    # Copy essential configurations
    cp /data/.openclaw/cron/jobs.json "$workspace/cron_jobs.json"
    cp /data/workspace/scripts/cron_job_validator.py "$workspace/cron_job_validator.py"
    
    # Set permissions
    chmod -R 755 "$workspace"
    
    echo "✅ Workspace for $agent initialized successfully"
done

echo "🎉 Agent Workspace Initialization Complete"