#!/bin/bash
# Emergency Rollback Script for QMD Migration
set -eu

BACKUP_DIR="${1:-/tmp/qmd_migration_backup}"

# Restore memory stores from backup
tar -xzf "${BACKUP_DIR}/encrypted/openclaw_memory.tar.gz.enc" -C "/data/.openclaw"
tar -xzf "${BACKUP_DIR}/encrypted/shared_memory_vault.tar.gz.enc" -C "/data/shared"

echo "Rollback completed successfully"
