#!/usr/bin/env bash
set -euo pipefail

DOMAIN="example.com"
ENV_FILE="/data/workspace/credentials/api-auth/${DOMAIN}.env"

METHOD="POST"
PATH_TEMPLATE="/v1/users"

DATA=""
DRY_RUN=0

usage() {
  cat >&2 <<'USAGE'
Usage:
  users-create.sh --data JSON|@file [--dry-run]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --data) DATA="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  if [[ $DRY_RUN -eq 1 ]]; then
    BASE_URL="${BASE_URL:-https://example.invalid}"
  else
    echo "Missing credentials env: $ENV_FILE" >&2
    exit 2
  fi
fi

BASE_URL="${BASE_URL:-https://example.invalid}"
URL="${BASE_URL}${PATH_TEMPLATE}"

AUTH_HEADERS=()
if [[ -n "${BEARER_TOKEN:-}" ]]; then
  AUTH_HEADERS+=( -H "Authorization: Bearer ${BEARER_TOKEN}" )
fi

DATA_ARGS=()
if [[ -n "$DATA" ]]; then
  if [[ "$DATA" == @* ]]; then
    DATA_ARGS+=( -H "Content-Type: application/json" --data-binary "$DATA" )
  else
    DATA_ARGS+=( -H "Content-Type: application/json" --data "$DATA" )
  fi
fi

TMP_BODY="$(mktemp)"
CURL_CMD=(curl -sS -X "$METHOD" "$URL" -H "Accept: application/json" "${AUTH_HEADERS[@]}" "${DATA_ARGS[@]}" -o "$TMP_BODY" -w "%{http_code}")

if [[ $DRY_RUN -eq 1 ]]; then
  printf '%q ' "${CURL_CMD[@]}"; echo
  rm -f "$TMP_BODY"
  exit 0
fi

HTTP_CODE="$( "${CURL_CMD[@]}" )"
cat "$TMP_BODY"
rm -f "$TMP_BODY"
