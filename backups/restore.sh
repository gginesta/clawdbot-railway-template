#!/bin/bash
# ============================================================
# 🦎 Molty One-Click Restore Script
# ============================================================
# Usage: ./restore.sh <backup-tarball>
# Example: ./restore.sh molty-backup-20260205-072057.tar.gz
#
# This script restores a Molty (or Raphael) instance from a
# backup tarball created by backup.sh.
#
# Run this INSIDE a Railway container after fresh deployment.
# ============================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()  { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo ""
echo "============================================"
echo "  🦎 Molty/Raphael Restore Tool"
echo "  One-click disaster recovery"
echo "============================================"
echo ""

# ---- Validate input ----
BACKUP_FILE="${1:-}"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup-tarball>"
  echo ""
  echo "Examples:"
  echo "  $0 /data/workspace/backups/molty-backup-20260205-072057.tar.gz"
  echo "  $0 /tmp/uploaded-backup.tar.gz"
  echo ""
  echo "Available local backups:"
  ls -lh /data/workspace/backups/molty-backup-*.tar.gz 2>/dev/null || echo "  (none found)"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  err "Backup file not found: $BACKUP_FILE"
fi

FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
info "Backup file: $BACKUP_FILE ($FILE_SIZE)"

# ---- Confirm ----
echo ""
warn "This will OVERWRITE the following directories:"
echo "  - /data/workspace/"
echo "  - /data/.openclaw/openclaw.json"
echo "  - /data/.openclaw/credentials/"
echo "  - /data/.openclaw/telegram/"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

# ---- Pre-restore backup ----
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PRE_RESTORE_DIR="/data/pre-restore-$TIMESTAMP"
info "Saving current state to $PRE_RESTORE_DIR (just in case)..."
mkdir -p "$PRE_RESTORE_DIR"

if [ -f /data/.openclaw/openclaw.json ]; then
  cp /data/.openclaw/openclaw.json "$PRE_RESTORE_DIR/" 2>/dev/null || true
fi
if [ -d /data/.openclaw/credentials ]; then
  cp -r /data/.openclaw/credentials "$PRE_RESTORE_DIR/" 2>/dev/null || true
fi
if [ -f /data/workspace/MEMORY.md ]; then
  cp /data/workspace/MEMORY.md "$PRE_RESTORE_DIR/" 2>/dev/null || true
fi
log "Pre-restore backup saved"

# ---- Stop OpenClaw ----
info "Stopping OpenClaw gateway..."
openclaw gateway stop 2>/dev/null || true
sleep 2
log "Gateway stopped"

# ---- Extract backup ----
info "Extracting backup to /data/..."
cd /data
tar -xzf "$BACKUP_FILE" 2>/dev/null

if [ $? -eq 0 ]; then
  log "Backup extracted successfully"
else
  err "Failed to extract backup. File may be corrupted."
fi

# ---- Verify critical files ----
echo ""
info "Verifying restored files..."

CHECKS=(
  "/data/workspace/MEMORY.md:Long-term memory"
  "/data/workspace/SOUL.md:Soul/personality"
  "/data/workspace/USER.md:User profile"
  "/data/workspace/IDENTITY.md:Identity"
  "/data/workspace/AGENTS.md:Agent instructions"
  "/data/.openclaw/openclaw.json:Gateway config"
)

ALL_OK=true
for check in "${CHECKS[@]}"; do
  FILE="${check%%:*}"
  DESC="${check##*:}"
  if [ -f "$FILE" ]; then
    log "$DESC — found"
  else
    warn "$DESC — MISSING ($FILE)"
    ALL_OK=false
  fi
done

# ---- Check env vars ----
echo ""
info "Checking environment variables..."

ENV_CHECKS=(
  "ANTHROPIC_API_KEY:Required - Primary AI model"
  "OPENCLAW_GATEWAY_TOKEN:Required - Web UI auth"
  "TELEGRAM_BOT_TOKEN:Recommended - Telegram messaging"
  "BRAVE_API_KEY:Recommended - Web search"
  "OPENAI_API_KEY:Recommended - Fallback model"
)

for check in "${ENV_CHECKS[@]}"; do
  VAR="${check%%:*}"
  DESC="${check##*:}"
  if [ -n "${!VAR:-}" ]; then
    log "$VAR — set"
  else
    warn "$VAR — NOT SET ($DESC)"
  fi
done

# ---- Fix permissions ----
info "Fixing file permissions..."
chmod -R 755 /data/workspace/scripts/ 2>/dev/null || true
chmod -R 755 /data/workspace/backups/*.sh 2>/dev/null || true
chmod 600 /data/workspace/credentials/* 2>/dev/null || true
log "Permissions fixed"

# ---- Restart gateway ----
echo ""
info "Starting OpenClaw gateway..."
openclaw gateway start 2>/dev/null || openclaw gateway restart 2>/dev/null || true
sleep 3

# ---- Check if gateway is running ----
if openclaw status 2>/dev/null | grep -qi "running\|online\|ok"; then
  log "Gateway is running!"
else
  warn "Gateway may not have started. Check with: openclaw status"
fi

# ---- Summary ----
echo ""
echo "============================================"
echo "  🦎 Restore Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Verify web UI: visit your Railway URL"
echo "  2. Re-pair Telegram: send /pair to your bot"
echo "  3. Check Syncthing: http://localhost:8384"
echo "  4. Test: send a message and verify response"
echo ""
echo "Pre-restore backup saved at: $PRE_RESTORE_DIR"
echo ""

if [ "$ALL_OK" = true ]; then
  log "All critical files present. You should be good to go! 🎉"
else
  warn "Some files were missing. Check the warnings above."
fi
