#!/usr/bin/env bash

# Discord Channel Validator
# Version: 1.0
# Maintainer: Molty 🦎

# Predefined Channel IDs
COMMAND_CENTER="1468164160398557216"
SQUAD_UPDATES="1468164181155909743"
ALLOWED_CHANNELS=("${COMMAND_CENTER}" "${SQUAD_UPDATES}")

# Logging function
log_channel_attempt() {
    local attempted_channel="$1"
    local timestamp
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    echo "[CHANNEL_VALIDATION][${timestamp}] Attempted to send to channel: ${attempted_channel}" >> "/data/workspace/logs/discord_channel_validation.log"
}

# Validate and correct channel
validate_channel() {
    local input_channel="$1"
    
    # Check if input is in allowed channels
    for allowed in "${ALLOWED_CHANNELS[@]}"; do
        if [[ "${input_channel}" == "${allowed}" ]]; then
            echo "${input_channel}"
            return 0
        fi
    done
    
    # Default to command center if invalid
    log_channel_attempt "${input_channel}"
    echo "${COMMAND_CENTER}"
}

# Main function to be sourced by other scripts
validate_and_log_channel() {
    validate_channel "$1"
}