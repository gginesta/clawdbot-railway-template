#!/bin/bash
set -e

# Logging
LOG_FILE="/data/workspace/logs/memory_search_test.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Test Search Collections
COLLECTIONS=("memory-root" "memory-dir" "sessions")
SEARCH_TERMS=(
    "OpenClaw"
    "TMNT"
    "configuration"
    "deployment"
    "memory framework"
)

log "🔍 Memory Search Integration Test"

for collection in "${COLLECTIONS[@]}"; do
    log "\n📁 Testing Collection: $collection"
    for term in "${SEARCH_TERMS[@]}"; do
        log "Searching for '$term' in $collection:"
        qmd search "$term" -c "$collection" --json || log "❌ Search failed for '$term'"
    done
done

# Advanced Search Modes
log "\n🔬 Advanced Search Modes Test"
log "Vector Search:"
qmd vsearch "OpenClaw memory" || log "❌ Vector search failed"

log "\nCombined Query Search:"
qmd query "TMNT agent configuration" || log "❌ Combined query search failed"

log "🏁 Memory Search Test Complete"