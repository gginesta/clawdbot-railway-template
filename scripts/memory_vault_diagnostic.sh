#!/bin/bash

echo "🧠 Memory Vault Diagnostic"
echo "========================="

# Knowledge Graph (PARA)
echo -e "\n📁 Knowledge Graph Structure"
echo "-----------------------------"
for dir in projects areas resources archives; do
    FULL_PATH="/data/shared/memory-vault/knowledge/$dir"
    echo "[$dir]:"
    if [ -d "$FULL_PATH" ]; then
        ls -1 "$FULL_PATH" | head -n 10
        echo "Total items: $(ls -1 "$FULL_PATH" | wc -l)"
    else
        echo "Directory not found"
    fi
    echo ""
done

# Daily Notes
echo -e "\n📅 Daily Notes"
echo "-------------"
DAILY_PATH="/data/shared/memory-vault/daily"
if [ -d "$DAILY_PATH" ]; then
    echo "Daily notes found:"
    find "$DAILY_PATH" -type f -name "*.md" | sort | tail -n 10
    echo "Total daily notes: $(find "$DAILY_PATH" -type f -name "*.md" | wc -l)"
else
    echo "No daily notes directory found"
fi

# AI History
echo -e "\n🤖 AI Conversation History"
echo "-------------------------"
AI_HISTORY_PATH="/data/shared/memory-vault/ai-history"
for platform in chatgpt claude grok; do
    PLATFORM_PATH="$AI_HISTORY_PATH/$platform"
    echo "[$platform]:"
    if [ -d "$PLATFORM_PATH" ]; then
        ls -1 "$PLATFORM_PATH" | head -n 10
        echo "Total archives: $(ls -1 "$PLATFORM_PATH" | wc -l)"
    else
        echo "No archives found"
    fi
    echo ""
done

# Tacit Knowledge
echo -e "\n🤫 Tacit Knowledge"
echo "-----------------"
TACIT_PATH="/data/shared/memory-vault/tacit"
if [ -f "$TACIT_PATH/preferences.md" ]; then
    echo "Preferences file exists. First few lines:"
    head -n 5 "$TACIT_PATH/preferences.md"
else
    echo "No preferences file found"
fi