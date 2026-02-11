#!/usr/bin/env bash
set -euo pipefail

# capture-and-generate.sh
#
# Convenience wrapper:
#  1) Starts cdp-capture.js in the background
#  2) Waits for browsing (Ctrl+C to stop, or --timeout)
#  3) Stops capture
#  4) Runs skill-gen.py on the capture file(s)
#
# Usage:
#   bash capture-and-generate.sh hubspot.com [--timeout 120] [--port 18800]

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPTURE_DIR="/data/workspace/data/captures"
CREDS_DIR="/data/workspace/credentials/api-auth"
OUT_BASE="/data/shared/api-skills"

usage() {
  cat >&2 <<'USAGE'
Usage:
  capture-and-generate.sh <domain> [--timeout SEC] [--port PORT] [--out-base DIR]

Options:
  --timeout   Stop capture after N seconds (default: 0 = no timeout)
  --port      CDP remote debugging port (default: 18800)
  --out-base  Base directory for generated skills (default: /data/shared/api-skills)

Notes:
  - If this script isn't executable, run it with: bash capture-and-generate.sh ...
  - Brave must be started with remote debugging enabled:
      /usr/bin/brave-browser --remote-debugging-port=18800
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

DOMAIN="$1"; shift 1
TIMEOUT=0
PORT=18800

while [[ $# -gt 0 ]]; do
  case "$1" in
    --timeout) TIMEOUT="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --out-base) OUT_BASE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

mkdir -p "$CAPTURE_DIR" "$CREDS_DIR" "$OUT_BASE"

# Best-effort chmod (in case files were created without +x in this environment)
chmod +x "$DIR/cdp-capture.js" "$DIR/skill-gen.py" "$DIR/capture-and-generate.sh" 2>/dev/null || true

# Ensure CDP endpoint is reachable
if ! curl -fsS "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "Cannot reach CDP at http://127.0.0.1:${PORT}/json/version" >&2
  echo "Is Brave running with --remote-debugging-port=${PORT}?" >&2
  exit 2
fi

START_TS="$(date -u +%Y%m%dT%H%M%SZ)"

echo "[wrapper] Starting capture for domain: $DOMAIN" >&2
node "$DIR/cdp-capture.js" --port "$PORT" --domain "$DOMAIN" --output "$CAPTURE_DIR" &
CAP_PID=$!

cleanup() {
  echo "\n[wrapper] Stopping capture (pid=$CAP_PID)..." >&2
  kill -INT "$CAP_PID" 2>/dev/null || true
  wait "$CAP_PID" 2>/dev/null || true
}
trap cleanup INT TERM

if [[ "$TIMEOUT" -gt 0 ]]; then
  echo "[wrapper] Capture running. Browse now. Will stop automatically in ${TIMEOUT}s (Ctrl+C to stop early)." >&2
  sleep "$TIMEOUT" || true
  cleanup
else
  echo "[wrapper] Capture running. Browse now. Press Ctrl+C when done." >&2
  # wait until Ctrl+C
  wait "$CAP_PID" || true
fi

# Find newest capture file for this domain
CAPTURE_FILE="$(ls -1t "$CAPTURE_DIR"/${DOMAIN}-*.jsonl 2>/dev/null | head -n 1 || true)"
if [[ -z "$CAPTURE_FILE" ]]; then
  echo "[wrapper] No capture file found in $CAPTURE_DIR for domain=$DOMAIN" >&2
  exit 2
fi

echo "[wrapper] Using capture file: $CAPTURE_FILE" >&2

echo "[wrapper] Generating skill..." >&2
python3 "$DIR/skill-gen.py" --input "$CAPTURE_FILE" --domain "$DOMAIN" --out-base "$OUT_BASE"

OUT_DIR="$OUT_BASE/$DOMAIN"
echo "[wrapper] Done." >&2
echo "[wrapper] Skill generated at: $OUT_DIR" >&2
echo "[wrapper] Next:" >&2
echo "  1) Create credentials: /data/workspace/credentials/api-auth/$DOMAIN.env" >&2
echo "  2) Try: bash $OUT_DIR/api.sh <resource> <action> --dry-run" >&2
