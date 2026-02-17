#!/bin/bash

# Define agent memory directories
AGENTS=(
    "molty:/data/workspace/memory"
    "raphael:/data/shared/brinc/memory"
    "leonardo:/data/shared/cerebro/memory"
)

echo "🔍 TMNT Squad Memory Management Audit"
echo "======================================"

for agent_config in "${AGENTS[@]}"; do
    IFS=':' read -r agent memory_dir <<< "$agent_config"
    
    echo -e "\n📋 Agent: $agent"
    echo "Memory Directory: $memory_dir"
    
    if [ -d "$memory_dir" ]; then
        echo "Memory Files:"
        ls -l "$memory_dir" | awk '{print $9, $5, "bytes"}'
        
        echo -e "\nRecent Memory Files:"
        find "$memory_dir" -type f -mtime -7 -print0 | xargs -0 ls -l
        
        echo -e "\nMemory File Contents Summary:"
        for file in "$memory_dir"/*.md; do
            [ -f "$file" ] || continue
            echo "File: $file"
            head -n 3 "$file"
            echo "---"
        done
    else
        echo "❌ Memory directory does not exist!"
    fi
done

echo -e "\n🏁 Memory Audit Complete"