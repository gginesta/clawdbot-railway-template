#!/usr/bin/env bash
set -euo pipefail

# Save a markdown report to Notion using notion-enhanced (md-to-notion.js)
# Requirements:
#   - NOTION_API_KEY set (e.g., source /data/workspace/credentials/notion.env)
#   - NOTION_PARENT_PAGE_ID set (parent page under which to create the new page)

REPORT_MD="${1:-}"
TITLE="${2:-}"

if [[ -z "$REPORT_MD" || -z "$TITLE" ]]; then
  echo "Usage: notion-save.sh <report.md> <page-title>" >&2
  exit 2
fi
if [[ -z "${NOTION_API_KEY:-}" ]]; then
  echo "NOTION_API_KEY is not set. Try: source /data/workspace/credentials/notion.env" >&2
  exit 2
fi
if [[ -z "${NOTION_PARENT_PAGE_ID:-}" ]]; then
  echo "NOTION_PARENT_PAGE_ID is not set (parent page to create under)." >&2
  exit 2
fi

SCRIPT="/data/workspace/skills/notion-enhanced/scripts/md-to-notion.js"
if [[ ! -f "$SCRIPT" ]]; then
  echo "notion-enhanced not found at $SCRIPT" >&2
  exit 2
fi

node "$SCRIPT" "$REPORT_MD" "$NOTION_PARENT_PAGE_ID" "$TITLE"
