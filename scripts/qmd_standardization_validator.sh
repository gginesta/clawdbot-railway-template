#!/usr/bin/env bash

# QMD Standardization Validation Script
# Version: 1.2
# Maintainer: Molty 🦎

# Ensure bash features are available
set -Eeo pipefail

# Logging Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="/data/workspace/logs/qmd_validation"
VALIDATION_LOG="${LOG_DIR}/validation_${TIMESTAMP}.log"
CONFIG_PATH="/data/shared/qmd_standard_config.json5"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Logging Function
log() {
    local log_level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    echo "[${log_level}][${timestamp}] ${message}" | tee -a "${VALIDATION_LOG}"
}

# Validate Configuration Syntax
validate_config() {
    log "INFO" "Validating QMD configuration syntax"
    
    if [ ! -f "${CONFIG_PATH}" ]; then
        log "ERROR" "Configuration file not found: ${CONFIG_PATH}"
        return 1
    fi
    
    # Very basic syntax check
    if ! grep -q '"memorySearch"' "${CONFIG_PATH}"; then
        log "ERROR" "Invalid configuration: missing memorySearch section"
        return 1
    fi
    
    log "SUCCESS" "Configuration syntax validated successfully"
    return 0
}

# Check Embedding Provider Compatibility
check_embedding_provider() {
    log "INFO" "Verifying embedding provider compatibility"
    
    # Extract provider and model using grep and cut
    provider=$(grep -o '"provider": *"[^"]*"' "${CONFIG_PATH}" | cut -d'"' -f4)
    model=$(grep -o '"model": *"[^"]*"' "${CONFIG_PATH}" | cut -d'"' -f4)
    
    log "INFO" "Detected Provider: ${provider}"
    log "INFO" "Detected Model: ${model}"
    
    if [ "${provider}" != "openrouter" ] || [ "${model}" != "nomic-ai/nomic-embed-text-v1" ]; then
        log "ERROR" "Embedding provider or model does not match standardization requirements"
        return 1
    fi
    
    log "SUCCESS" "Embedding provider verified successfully"
    return 0
}

# Validate Central Memory Vault
validate_memory_vault() {
    log "INFO" "Checking central memory vault configuration"
    
    # Extract vault path (simplistic approach)
    vault_path=$(grep -o '"primary_vault": *"[^"]*"' "${CONFIG_PATH}" | cut -d'"' -f4)
    
    log "INFO" "Detected Vault Path: ${vault_path}"
    
    if [ -z "${vault_path}" ]; then
        log "ERROR" "No vault path found in configuration"
        return 1
    fi
    
    if [ ! -d "${vault_path}" ]; then
        log "INFO" "Creating central memory vault directory"
        mkdir -p "${vault_path}"
    fi
    
    # Create standard subdirectories
    mkdir -p "${vault_path}"/{projects,people,resources,daily_logs,archives}
    
    log "SUCCESS" "Central memory vault validated and configured"
    return 0
}

# Main Validation Process
main() {
    log "CRITICAL" "Initiating QMD Standardization Validation"
    
    validate_config
    check_embedding_provider
    validate_memory_vault
    
    log "CRITICAL" "QMD Standardization Validation Completed Successfully"
    return 0
}

# Execute main validation with error handling
main || {
    exit_code=$?
    log "CRITICAL" "QMD Standardization Validation Failed with exit code ${exit_code}"
    exit "${exit_code}"
}