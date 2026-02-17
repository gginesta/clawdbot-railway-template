#!/bin/bash

echo "🕵️ OpenClaw Morning Postmortem Diagnostic"
echo "----------------------------------------"

# Cron Job Isolation Check
echo -e "\n📅 Cron Job Isolation Verification:"
for job in $(cron list | jq -r '.jobs[].id'); do
    echo "Checking job: $job"
    cron list | jq -r ".jobs[] | select(.id == \"$job\") | {id, name, sessionTarget, payload}"
done

# Memory Search Comprehensive Test
echo -e "\n🔍 Memory Search Diagnostics:"
qmd status
echo -e "\nCollection Details:"
qmd collection list

echo -e "\nSearch Test Across Collections:"
COLLECTIONS=("memory-root" "memory-dir" "sessions")
QUERIES=("OpenClaw" "TMNT" "configuration" "deployment")

for collection in "${COLLECTIONS[@]}"; do
    echo -e "\nCollection: $collection"
    for query in "${QUERIES[@]}"; do
        echo "Query: $query"
        qmd search "$query" -c "$collection" --json | head -n 10
    done
done

# Embedding Quality Check
echo -e "\n📊 Embedding Statistics:"
qmd status | grep -E "Total|Vectors|Updated"

# Configuration Verification
echo -e "\n⚙️ Memory Configuration:"
cat /data/.openclaw/openclaw.json | jq '.memory, .agents.defaults.memorySearch'

# Cron Configuration Sanity Check
echo -e "\n⏰ Cron Configuration Sanity Check:"
cron list | jq '.jobs[] | select(.payload.kind != "agentTurn" and .payload.kind != "systemEvent")'

# Fallback Chain Verification
echo -e "\n🔄 Model Fallback Chains:"
cat /data/.openclaw/openclaw.json | jq '.agents.defaults.model.fallbacks, .agents.defaults.subagents.model.fallbacks'