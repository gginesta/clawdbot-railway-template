#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_STATE_DIR="${OPENCLAW_STATE_DIR:-/data/.openclaw}"
OPENCLAW_USER="${OPENCLAW_USER:-openclaw}"
OPENCLAW_GROUP="${OPENCLAW_GROUP:-openclaw}"

mkdir -p "$OPENCLAW_STATE_DIR"

root_owned_count="$(find "$OPENCLAW_STATE_DIR" -xdev \( -user root -o -group root \) -print 2>/dev/null | wc -l | tr -d ' ')"
if [ "${root_owned_count:-0}" != "0" ]; then
  echo "[openclaw-start-guard] repairing $root_owned_count root-owned entries under $OPENCLAW_STATE_DIR" >&2
  chown -R "$OPENCLAW_USER:$OPENCLAW_GROUP" "$OPENCLAW_STATE_DIR"
fi

chmod 700 "$OPENCLAW_STATE_DIR" 2>/dev/null || true

exec gosu "$OPENCLAW_USER" node /app/src/server.js
