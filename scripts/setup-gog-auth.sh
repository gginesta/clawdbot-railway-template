#!/usr/bin/env bash
# setup-gog-auth.sh — Self-healing gog auth restore for Molty (ggv.molt@gmail.com)
#
# Restores gog credentials + keyring tokens from persistent /data/workspace backup
# to ephemeral /root/.config/gogcli/ on every container restart.
# Also syncs the backup with fresh tokens after successful auth (keeps backup current).
#
# Safe to run multiple times — skips if already auth'd.
# Run from: startup.sh, heartbeat cron, or any script needing gog before use.

set -euo pipefail

GOG_BIN="/usr/local/bin/gog"
GOG_DIR="/root/.config/gogcli"
GOG_KEYRING_DIR="$GOG_DIR/keyring"
GOG_CREDS="$GOG_DIR/credentials.json"

BACKUP_DIR="/data/workspace/credentials/gogcli-keyring"
BACKUP_KEYRING="$BACKUP_DIR/keyring"
BACKUP_CREDS="/data/workspace/credentials/google-oauth-client.json"

GOG_ACCOUNT="ggv.molt@gmail.com"
export GOG_KEYRING_PASSWORD="molty2026"

log() { echo "[setup-gog-auth] $*"; }

# --- Step 1: Ensure gog binary exists ---
if [ ! -x "$GOG_BIN" ]; then
  log "gog binary missing — installing v0.11.0..."
  GOG_URL="https://github.com/steipete/gogcli/releases/download/v0.11.0/gogcli_0.11.0_linux_amd64.tar.gz"
  TMP=$(mktemp -d)
  curl -sSL "$GOG_URL" -o "$TMP/gog.tar.gz"
  tar -xzf "$TMP/gog.tar.gz" -C "$TMP" gog
  mv "$TMP/gog" "$GOG_BIN"
  chmod +x "$GOG_BIN"
  rm -rf "$TMP"
  log "gog installed ✓"
fi

# --- Step 2: Quick auth check — skip if already working ---
# Use a lightweight real API call to verify (auth status JSON doesn't include auth state)
_check_auth() {
  "$GOG_BIN" gmail messages search "is:unread" --max 1 -a "$GOG_ACCOUNT" --json 2>/dev/null | grep -q '"messages"' \
    || "$GOG_BIN" gmail messages search "is:unread" --max 1 -a "$GOG_ACCOUNT" --json 2>/dev/null | grep -q '\[\]'
}

if _check_auth; then
  log "Already authenticated as $GOG_ACCOUNT ✓"
  # Still sync backup to keep it fresh
  if [ -d "$GOG_KEYRING_DIR" ] && [ "$(ls -A "$GOG_KEYRING_DIR" 2>/dev/null)" ]; then
    mkdir -p "$BACKUP_KEYRING"
    cp -f "$GOG_KEYRING_DIR"/token:* "$BACKUP_KEYRING/" 2>/dev/null && log "Backup synced ✓"
  fi
  exit 0
fi

log "Auth missing or expired — restoring from backup..."

# --- Step 3: Restore credentials.json ---
mkdir -p "$GOG_DIR"
if [ ! -f "$GOG_CREDS" ] && [ -f "$BACKUP_CREDS" ]; then
  "$GOG_BIN" auth credentials "$BACKUP_CREDS" 2>/dev/null || cp "$BACKUP_CREDS" "$GOG_CREDS"
  log "Credentials restored ✓"
fi

# --- Step 4: Restore keyring tokens ---
if [ -d "$BACKUP_KEYRING" ] && [ "$(ls -A "$BACKUP_KEYRING" 2>/dev/null)" ]; then
  mkdir -p "$GOG_KEYRING_DIR"
  cp -f "$BACKUP_KEYRING"/token:* "$GOG_KEYRING_DIR/" 2>/dev/null
  log "Keyring tokens restored ✓"
else
  log "ERROR: No keyring backup found at $BACKUP_KEYRING — manual re-auth needed"
  exit 1
fi

# --- Step 5: Verify auth works after restore ---
if _check_auth; then
  log "Auth verified after restore ✓"
  # Sync backup with whatever gog just refreshed
  cp -f "$GOG_KEYRING_DIR"/token:* "$BACKUP_KEYRING/" 2>/dev/null && log "Backup updated ✓"
  exit 0
fi

log "ERROR: Auth failed after keyring restore — backup token may be expired"
log "Fix: Run 'GOG_KEYRING_PASSWORD=molty2026 gog auth login -a ggv.molt@gmail.com' manually, then re-run this script to update the backup"
exit 1
