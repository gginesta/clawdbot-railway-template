#!/usr/bin/env bash

# TMNT Squad Central Memory Indexing Script
# Version: 1.2
# Architect: Molty 🦎

# Exit immediately on any error
set -Eeo pipefail

# Debugging
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
exec 2> >(tee -a "/tmp/qmd_central_indexer_error_${TIMESTAMP}.log" >&2)

# Configuration
BASE_DIR="/data/shared/memory-vault"
CENTRAL_INDEX_DIR="${BASE_DIR}/central_index"
SOURCES_LIST="${BASE_DIR}/index_sources.json"
INDEXING_LOG="/data/workspace/logs/qmd_central_indexing_${TIMESTAMP}.log"
RETENTION_DAYS=365

# Ensure log directory exists
mkdir -p "$(dirname "${INDEXING_LOG}")"

# Logging function
log() {
    local level="$1"
    local message="$2"
    echo "[${level}][$(date +'%Y-%m-%d %H:%M:%S')] ${message}" | tee -a "${INDEXING_LOG}"
}

# Prepare central index directory
prepare_central_index() {
    mkdir -p "${CENTRAL_INDEX_DIR}"
    chmod 700 "${CENTRAL_INDEX_DIR}"
    
    # Create standard subdirectories
    mkdir -p "${CENTRAL_INDEX_DIR}"/{projects,people,daily,ai_history,resources,archives}
}

# Generate sources list from multiple agents
generate_sources_list() {
    local sources=()
    
    # Sources from known agent locations
    sources+=($(find /data/workspace/memory -type f))
    sources+=($(find /data/shared/memory-vault -type f))
    sources+=($(find /data/workspace/docs -type f))
    
    # Remove duplicates and filter
    printf '%s\n' "${sources[@]}" | 
        sort -u | 
        grep -E '\.(md|json|txt)$' | 
        jq -R . | 
        jq -s '.' > "${SOURCES_LIST}"
    
    log "INFO" "Generated sources list with $(jq 'length' "${SOURCES_LIST}") entries"
}

# Clean up old or unnecessary files
cleanup_old_files() {
    log "INFO" "Initiating cleanup of files older than ${RETENTION_DAYS} days"
    
    find "${BASE_DIR}" -type f -mtime +${RETENTION_DAYS} -delete
    find /data/workspace/memory -type f -mtime +${RETENTION_DAYS} -delete
    
    log "SUCCESS" "Cleanup completed"
}

# Centralize and standardize indexing
centralize_index() {
    log "INFO" "Beginning centralization of memory sources"
    
    # Read sources
    local sources
    mapfile -t sources < <(jq -r '.[]' "${SOURCES_LIST}")
    
    for source in "${sources[@]}"; do
        # Determine file type and category
        local filename=$(basename "${source}")
        local category=""
        
        # Categorize files
        case "${source}" in 
            *"/projects/"*)
                category="projects"
                ;;
            *"/daily/"*|*"/memory/"*|*"update-notes"*)
                category="daily"
                ;;
            *"/ai-history/"*)
                category="ai_history"
                ;;
            *"/people/"*|*"/team/"*)
                category="people"
                ;;
            *)
                category="resources"
                ;;
        esac
        
        # Ensure category directory exists
        mkdir -p "${CENTRAL_INDEX_DIR}/${category}"
        
        # Copy to central index with preservation of original path structure
        local dest_path="${CENTRAL_INDEX_DIR}/${category}/${filename}"
        cp "${source}" "${dest_path}"
        
        log "PROCESSED" "Indexed: ${source} → ${dest_path}"
    done
    
    log "SUCCESS" "Central indexing completed"
}

# Source channel validator
source /data/workspace/scripts/discord_channel_validator.sh

# Send notification to validated channel
send_notification() {
    local message="$1"
    local channel
    channel=$(validate_and_log_channel "1468164160398557216")
    
    message_json=$(jq -n \
        --arg msg "$message" \
        '{
            "action": "send", 
            "channel": "discord", 
            "target": env.VALIDATED_CHANNEL, 
            "message": $msg
        }')
    
    # Use message tool to send
    echo "${message_json}" | openclaw message send
}

# Main execution function
main() {
    log "CRITICAL" "Initiating TMNT Squad Central Memory Indexing"
    
    prepare_central_index
    generate_sources_list
    centralize_index
    cleanup_old_files
    
    # Send notification to validated channel
    send_notification "✅ Central Memory Indexing Completed
- Total Sources Processed: $(jq 'length' "${SOURCES_LIST}")
- Retention Period: ${RETENTION_DAYS} days
- Timestamp: ${TIMESTAMP}"
    
    log "CRITICAL" "Central Memory Indexing Process Completed"
}

# Actually execute the main function
main