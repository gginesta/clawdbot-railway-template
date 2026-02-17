#!/usr/bin/env bash

# QMD Index Discovery Script
# Version: 1.0
# Maintainer: Molty 🦎

set -Eeo pipefail

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="/data/workspace/logs/qmd_indexing"
DISCOVERY_LOG="${LOG_DIR}/discovery_${TIMESTAMP}.log"
INDEX_CATALOG="/data/shared/memory-vault/index_catalog.json"

# Ensure directories exist
mkdir -p "${LOG_DIR}"
mkdir -p "$(dirname "${INDEX_CATALOG}")"

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    echo "[${level}][${timestamp}] ${message}" | tee -a "${DISCOVERY_LOG}"
}

# Discover indexable memory sources
discover_memory_sources() {
    local sources=()

    log "INFO" "Starting memory source discovery"

    # Predefined memory source locations
    local memory_locations=(
        "/data/workspace/MEMORY.md"
        "/data/workspace/memory/"
        "/data/shared/memory-vault/"
        "/data/workspace/memory/refs/"
        "/data/workspace/docs/"
    )

    # Discover markdown and text files
    for location in "${memory_locations[@]}"; do
        if [ -d "${location}" ]; then
            while IFS= read -r -d '' file; do
                # Filter for relevant file types
                if [[ "${file}" =~ \.(md|txt|json)$ ]]; then
                    sources+=("${file}")
                    log "FOUND" "Indexable source: ${file}"
                fi
            done < <(find "${location}" -type f -print0)
        elif [ -f "${location}" ]; then
            sources+=("${location}")
            log "FOUND" "Indexable source: ${location}"
        fi
    done

    # Generate JSON catalog
    printf '%s\n' "${sources[@]}" | jq -R . | jq -s '{
        "timestamp": "'"${TIMESTAMP}"'",
        "total_sources": length,
        "sources": .
    }' > "${INDEX_CATALOG}"

    log "SUCCESS" "Memory source discovery completed"
    log "INFO" "Total sources discovered: ${#sources[@]}"
}

# Main execution
main() {
    log "CRITICAL" "Initiating QMD Memory Source Discovery"
    
    discover_memory_sources
    
    log "CRITICAL" "Memory Source Discovery Completed Successfully"
}

# Execute main function
main