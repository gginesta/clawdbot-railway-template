#!/usr/bin/env bash

# QMD Content Validation Script
# Version: 1.2
# Maintainer: Molty 🦎

# Exit on any error
set -e

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="/data/workspace/logs/qmd_validation"
VALIDATION_LOG="${LOG_DIR}/content_validation_${TIMESTAMP}.log"
INDEX_CATALOG="/data/shared/memory-vault/index_catalog.json"
VALIDATION_REPORT="/data/shared/memory-vault/content_validation_report.json"
SUMMARY_REPORT="/data/shared/memory-vault/content_validation_summary.json"

# Ensure directories exist
mkdir -p "${LOG_DIR}"

# Logging function
log() {
    local level="$1"
    local message="$2"
    echo "[${level}][$(date +'%Y-%m-%d %H:%M:%S')] ${message}" | tee -a "${VALIDATION_LOG}"
}

# Detect content type
detect_content_type() {
    local file="$1"
    local mime_type
    mime_type=$(file --mime-type -b "$file")
    
    case "$mime_type" in 
        *markdown*|*text/plain*)
            echo "text"
            ;;
        *json*)
            echo "json"
            ;;
        *csv*)
            echo "csv"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Validate individual file
validate_file() {
    local file="$1"
    local content_type
    
    content_type=$(detect_content_type "$file")
    
    # Validation logic
    case "$content_type" in
        "text")
            lines=$(wc -l < "$file")
            ;;
        "json")
            if ! jq empty "$file" &>/dev/null; then
                log "ERROR" "Invalid JSON: $file"
                content_type="invalid_json"
            fi
            lines=$(wc -l < "$file")
            ;;
        *)
            lines=0
            ;;
    esac
    
    # Output JSON record
    jq -n \
        --arg file "$file" \
        --arg type "$content_type" \
        --arg lines "$lines" \
        '{"file": $file, "type": $type, "lines": $lines}'
}

# Main validation process
main() {
    log "INFO" "Starting QMD Content Validation"
    
    # Read sources from catalog
    sources=$(jq -r '.sources[]' "${INDEX_CATALOG}")
    
    # Process sources and output to report
    for source in $sources; do
        if [ -f "$source" ]; then
            validate_file "$source"
        fi
    done | jq -s '.' > "${VALIDATION_REPORT}"
    
    # Generate summary
    jq -n \
        --arg timestamp "$TIMESTAMP" \
        --argjson total "$(jq 'length' "${VALIDATION_REPORT}")" \
        --argjson text_count "$(jq '[.[] | select(.type == "text")] | length' "${VALIDATION_REPORT}")" \
        --argjson json_count "$(jq '[.[] | select(.type == "json")] | length' "${VALIDATION_REPORT}")" \
        '{
            "timestamp": $timestamp,
            "total_sources": $total,
            "content_types": {
                "text": $text_count,
                "json": $json_count
            }
        }' > "${SUMMARY_REPORT}"
    
    log "SUCCESS" "Validation completed. Reports generated."
}

# Execute main function
main