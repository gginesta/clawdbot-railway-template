#!/usr/bin/env bash

# TMNT Squad Embedding Configuration Standardizer
# Version: 1.2
# Architect: Molty 🦎

# Exit immediately on any error
set -Eeo pipefail

# Debugging
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
exec 2> >(tee -a "/tmp/qmd_embedding_standardizer_error_${TIMESTAMP}.log" >&2)

# Configuration
CONFIG_DIR="/data/shared/config"
EMBEDDING_CONFIG="${CONFIG_DIR}/embedding_standard.json"
LOG_FILE="/data/workspace/logs/embedding_standardization_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "$(dirname "${LOG_FILE}")"

# Logging function
log() {
    local level="$1"
    local message="$2"
    echo "[${level}][$(date +'%Y-%m-%d %H:%M:%S')] ${message}" | tee -a "${LOG_FILE}"
}

# Prepare configuration directory
prepare_config_dir() {
    mkdir -p "${CONFIG_DIR}"
    chmod 700 "${CONFIG_DIR}"
}

# Create standardized embedding configuration
create_embedding_config() {
    log "INFO" "Creating standardized embedding configuration"
    
    # Standardized configuration for OpenRouter's nomic-embed-text-v1
    jq -n '{
        "provider": "openrouter",
        "model": "nomic-ai/nomic-embed-text-v1",
        "dimensions": 768,
        "cost_per_1k_tokens": 0.0001,
        "security": {
            "mode": "restricted",
            "allowed_agents": ["molty", "leonardo", "raphael"]
        },
        "indexing": {
            "depth": "6-months",
            "refresh_interval": "daily"
        }
    }' > "${EMBEDDING_CONFIG}"
    
    log "SUCCESS" "Embedding configuration created at ${EMBEDDING_CONFIG}"
}

# Distribute configuration to agents
distribute_config() {
    log "INFO" "Distributing embedding configuration"
    
    # Potential distribution methods
    # 1. Syncthing shared folder
    mkdir -p "/data/shared/memory-vault/config"
    cp "${EMBEDDING_CONFIG}" "/data/shared/memory-vault/config/embedding_config.json"
    
    # 2. Copy to each agent's config directory
    mkdir -p "/data/workspace/config"
    cp "${EMBEDDING_CONFIG}" "/data/workspace/config/embedding_config.json"
    
    log "SUCCESS" "Configuration distributed to shared locations"
}

# Verify agent configurations
verify_agent_configs() {
    log "INFO" "Verifying agent embedding configurations"
    
    # Check Molty's configuration
    if ! jq -e '.provider == "openrouter" and .model == "nomic-ai/nomic-embed-text-v1"' "/data/workspace/config/embedding_config.json" &>/dev/null; then
        log "WARNING" "Molty configuration mismatch"
    fi
    
    log "SUCCESS" "Agent configuration verification completed"
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
    log "CRITICAL" "Initiating TMNT Squad Embedding Configuration Standardization"
    
    prepare_config_dir
    create_embedding_config
    distribute_config
    verify_agent_configs
    
    # Send notification to validated channel
    send_notification "🔧 Embedding Configuration Standardized
- Provider: OpenRouter (nomic-ai/nomic-embed-text-v1)
- Dimensions: 768
- Timestamp: ${TIMESTAMP}"
    
    log "CRITICAL" "Embedding Configuration Standardization Completed"
}

# Actually execute the main function
main