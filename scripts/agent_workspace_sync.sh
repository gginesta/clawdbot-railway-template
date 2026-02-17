#!/bin/bash

# Define agent workspaces in shared folder
AGENTS=(
    "raphael:/data/shared/brinc"
    "leonardo:/data/shared/cerebro"
)

# Ensure essential directories exist
for agent_config in "${AGENTS[@]}"; do
    IFS=':' read -r agent workspace <<< "$agent_config"
    
    echo "🏗️ Initializing workspace for $agent at $workspace"
    
    # Create workspace directory
    mkdir -p "$workspace"
    
    # Copy essential configurations
    cp /data/.openclaw/cron/jobs.json "$workspace/cron_jobs.json"
    cp /data/workspace/scripts/cron_job_validator.py "$workspace/cron_job_validator.py"
    
    # Ensure QMD is available
    npm install -g qmd || bun install -g qmd
    
    # Set permissions
    chmod -R 755 "$workspace"
    
    echo "✅ Workspace for $agent initialized in shared folder"
done

echo "🎉 Agent Workspace Synchronization Complete"