#!/bin/bash

# QMD Repair Script for TMNT Squad Memory Architecture
# Version: 0.1
# Maintainer: Molty 🦎

set -euo pipefail

# Logging
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/data/workspace/logs/qmd_repair_${TIMESTAMP}.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

# Diagnostic function
diagnose_qmd_installation() {
    log "Starting QMD installation diagnostic"
    
    # Check OpenClaw configuration
    log "Checking OpenClaw memory configuration"
    openclaw config view | grep -i "qmd" || log "No QMD references found in OpenClaw config"
    
    # Check for potential installation methods
    log "Searching for QMD installation methods"
    if command -v npm &> /dev/null; then
        log "NPM is available - potential installation method"
    fi
    
    if command -v pip &> /dev/null; then
        log "Python pip is available - potential installation method"
    fi
}

# Repair function
repair_qmd_installation() {
    log "Initiating QMD repair process"
    
    # Attempt multiple installation methods
    if command -v npm &> /dev/null; then
        log "Attempting NPM-based QMD installation"
        npm install -g @openclaw/qmd || log "NPM installation failed"
    elif command -v pip &> /dev/null; then
        log "Attempting pip-based QMD installation"
        pip install openclaw-qmd || log "PIP installation failed"
    else
        log "CRITICAL: No package manager found for QMD installation"
        return 1
    fi
    
    # Verify installation
    which qmd && log "QMD successfully installed" || log "QMD installation verification failed"
}

# Main repair process
main() {
    log "Starting QMD Repair Process"
    
    diagnose_qmd_installation
    repair_qmd_installation
    
    log "QMD Repair Process Completed"
}

# Execute main function
main