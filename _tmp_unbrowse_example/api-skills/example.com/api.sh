#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat >&2 <<'USAGE'
Usage:
  api.sh <resource> <action> [args...]

Examples:
  api.sh users list --limit 10
  api.sh users get --id 123
USAGE
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

RESOURCE="$1"; ACTION="$2"; shift 2

SCRIPT_GLOB="$DIR/scripts/${RESOURCE}-${ACTION}*.sh"
MATCHES=( $SCRIPT_GLOB )

if [[ ! -e "${MATCHES[0]}" ]]; then
  echo "No matching script for resource='${RESOURCE}' action='${ACTION}'" >&2
  echo "Available scripts:" >&2
  ls -1 "$DIR/scripts" >&2
  exit 2
fi

exec "${MATCHES[0]}" "$@"
