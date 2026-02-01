#!/bin/bash
# Molty Backup Script
# Creates a timestamped tarball of critical data

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/data/workspace/backups"
BACKUP_FILE="$BACKUP_DIR/molty-backup-$TIMESTAMP.tar.gz"

echo "🦎 Creating backup..."

# Create tarball (excludes browser cache, logs, node_modules)
tar -czf "$BACKUP_FILE" \
  --exclude='*.log' \
  --exclude='node_modules' \
  --exclude='browser/*/user-data/*/Cache' \
  --exclude='browser/*/user-data/*/Code Cache' \
  --exclude='lost+found' \
  --exclude='workspace/backups/*.tar.gz' \
  -C /data \
  workspace \
  .openclaw/openclaw.json \
  .openclaw/credentials \
  .openclaw/telegram \
  .openclaw/agents \
  .openclaw/memory \
  .openclaw/devices \
  2>/dev/null

if [ $? -eq 0 ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup complete: $BACKUP_FILE ($SIZE)"
  
  # Keep only last 5 backups
  ls -t "$BACKUP_DIR"/molty-backup-*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
  echo "📦 Kept last 5 backups"
else
  echo "❌ Backup failed"
  exit 1
fi
