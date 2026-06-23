#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="${WEBCHAT_WATCHDOG_LOCK_FILE:-/data/workspace/.webchat-turn-watchdog.lock}"
LOG_FILE="${WEBCHAT_WATCHDOG_LOG_FILE:-/data/workspace/logs/webchat-turn-watchdog.log}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
WATCHDOG_SCRIPT="${WEBCHAT_WATCHDOG_SCRIPT:-/data/workspace/scripts/webchat-turn-watchdog.py}"

mkdir -p "$(dirname "$LOCK_FILE")" "$(dirname "$LOG_FILE")"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "webchat-turn-watchdog already active" >> "$LOG_FILE"
  exit 0
fi

exec "$PYTHON_BIN" "$WATCHDOG_SCRIPT" --loop
