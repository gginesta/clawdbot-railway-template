#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data/.openclaw}"
BROWSER_DIR="${OPENCLAW_BROWSER_DIR:-$OPENCLAW_STATE_DIR/browser}"

log() {
  echo "[openclaw-browser-profile-guard] $*" >&2
}

pid_is_running() {
  local pid="$1"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null
}

profile_has_live_process() {
  local user_data_dir="$1"
  pgrep -af -- "--user-data-dir=$user_data_dir" >/dev/null 2>&1
}

pid_from_singleton_lock() {
  local lock_target="$1"
  local tail_part
  tail_part="${lock_target##*-}"
  if [[ "$tail_part" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$tail_part"
  fi
}

clean_profile_if_stale() {
  local user_data_dir="$1"
  local lock_path="$user_data_dir/SingletonLock"
  local lock_target=""
  local lock_pid=""

  [ -e "$lock_path" ] || [ -L "$lock_path" ] || return 0

  if profile_has_live_process "$user_data_dir"; then
    log "profile in use, keeping lock: $user_data_dir"
    return 0
  fi

  lock_target="$(readlink "$lock_path" 2>/dev/null || true)"
  lock_pid="$(pid_from_singleton_lock "$lock_target" || true)"

  if [ -n "$lock_pid" ] && pid_is_running "$lock_pid"; then
    log "lock pid $lock_pid still running, keeping lock: $user_data_dir"
    return 0
  fi

  rm -f "$user_data_dir/SingletonLock" \
        "$user_data_dir/SingletonSocket" \
        "$user_data_dir/SingletonCookie"
  log "removed stale Singleton lock files: $user_data_dir"
}

[ -d "$BROWSER_DIR" ] || exit 0

while IFS= read -r -d '' user_data_dir; do
  clean_profile_if_stale "$user_data_dir"
done < <(find "$BROWSER_DIR" -mindepth 2 -maxdepth 2 -type d -name user-data -print0 2>/dev/null)
