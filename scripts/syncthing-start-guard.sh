#!/usr/bin/env bash
set -euo pipefail

SYNCTHING_HOME="${SYNCTHING_HOME:-/data/.syncthing}"
OPENCLAW_USER="${OPENCLAW_USER:-openclaw}"
OPENCLAW_GROUP="${OPENCLAW_GROUP:-openclaw}"
# Small shared paths Syncthing/OpenClaw need writable. Keep this narrow; do not chown all of /data/shared.
SYNCTHING_REPAIR_PATHS="${SYNCTHING_REPAIR_PATHS:-/data/.syncthing /data/shared/logs}"

mkdir -p "$SYNCTHING_HOME"

for repair_path in $SYNCTHING_REPAIR_PATHS; do
  if [ ! -e "$repair_path" ]; then
    mkdir -p "$repair_path" 2>/dev/null || true
  fi

  if [ -e "$repair_path" ]; then
    root_owned_count="$(find "$repair_path" -xdev \( -user root -o -group root \) -print 2>/dev/null | wc -l | tr -d ' ')"
    if [ "${root_owned_count:-0}" != "0" ]; then
      echo "[syncthing-start-guard] repairing $root_owned_count root-owned entries under $repair_path" >&2
      chown -R "$OPENCLAW_USER:$OPENCLAW_GROUP" "$repair_path"
    fi
  fi
done

exec gosu "$OPENCLAW_USER" /usr/bin/syncthing serve --home="$SYNCTHING_HOME" --gui-address=0.0.0.0:8384 --no-browser
