#!/usr/bin/env bash
set -euo pipefail

DOMAIN="example.com"
ENV_FILE="/data/workspace/credentials/api-auth/${DOMAIN}.env"

METHOD="GET"
PATH_TEMPLATE="/v1/users/{id}"

ID=""
DRY_RUN=0

usage() {
  cat >&2 <<'USAGE'
Usage:
  users-get.sh --id VALUE [--dry-run]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="$2"; shift 2 ;;
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

if [[ "$URL" == *"{id}"* ]]; then
  if [[ -z "$ID" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      :
    else
      echo "This endpoint requires --id" >&2
      exit 2
    fi
  else
    URL="${URL//\{id\}/$ID}"
  fi
fi

AUTH_HEADERS=()
if [[ -n "${BEARER_TOKEN:-}" ]]; then
  AUTH_HEADERS+=( -H "Authorization: Bearer ${BEARER_TOKEN}" )
fi

TMP_BODY="$(mktemp)"
CURL_CMD=(curl -sS -X "$METHOD" "$URL" -H "Accept: application/json" "${AUTH_HEADERS[@]}" -o "$TMP_BODY" -w "%{http_code}")

if [[ $DRY_RUN -eq 1 ]]; then
  printf '%q ' "${CURL_CMD[@]}"; echo
  rm -f "$TMP_BODY"
  exit 0
fi

HTTP_CODE="$( "${CURL_CMD[@]}" )"
cat "$TMP_BODY"
rm -f "$TMP_BODY"
