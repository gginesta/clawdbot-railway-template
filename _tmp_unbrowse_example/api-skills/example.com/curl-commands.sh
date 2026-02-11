#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "# curl commands for example.com (example)"
echo
for f in "$DIR/scripts/"*.sh; do
  echo "## $(basename "$f")"
  "$f" --dry-run || true
  echo
done
