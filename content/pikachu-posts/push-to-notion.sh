#!/bin/bash
# Push polished Pikachu posts to Notion
# Run this from the main agent session which has shell execution capability

set -e
source /data/workspace/credentials/notion.env

PAYLOAD_DIR="/data/workspace/content/pikachu-posts/notion-payloads"
MASTER_PAGE="30039dd69afd81308861fc93bee4dfae"

# Page IDs for existing posts 1-8
declare -A PAGES=(
  ["01"]="30039dd6-9afd-81b1-919e-c558bc646b54"  # 7 Days
  ["02"]="30039dd6-9afd-81b4-87eb-f0ed785cc05c"  # Pokemon
  ["03"]="30039dd6-9afd-810e-b084-dbfc8db32e33"  # Agent Comms
  ["04"]="30039dd6-9afd-81ed-a87b-ea70171c3c5b"  # Memory Stack
  ["05"]="30039dd6-9afd-8143-97df-c48255df13d7"  # Non-Tech
  ["06"]="30039dd6-9afd-8157-b31e-cb143e876ad6"  # Security
  ["07"]="30039dd6-9afd-8148-9b65-dfb6a0d580f5"  # Railway
  ["08"]="30139dd6-9afd-81e3-bcb5-c156209badfb"  # Unbrowse
)

# Function to get all child block IDs for a page
get_child_blocks() {
  local page_id=$1
  curl -s "https://api.notion.com/v1/blocks/${page_id}/children?page_size=100" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" | \
    jq -r '.results[].id'
}

# Function to delete a block
delete_block() {
  local block_id=$1
  curl -s -X DELETE "https://api.notion.com/v1/blocks/${block_id}" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" > /dev/null
  echo "  Deleted block: ${block_id}"
}

# Function to append blocks to a page
append_blocks() {
  local page_id=$1
  local payload_file=$2
  
  curl -s -X PATCH "https://api.notion.com/v1/blocks/${page_id}/children" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d @"${payload_file}" > /dev/null
  echo "  Appended new content from ${payload_file}"
}

# Function to create a new page under the master page
create_page() {
  local title=$1
  
  local response=$(curl -s -X POST "https://api.notion.com/v1/pages" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d "{
      \"parent\": {\"page_id\": \"${MASTER_PAGE}\"},
      \"properties\": {\"title\": [{\"text\": {\"content\": \"${title}\"}}]}
    }")
  
  echo "$response" | jq -r '.id'
}

# Update existing posts 1-8
echo "=== Updating existing posts 1-8 ==="
for num in 01 02 03 04 05 06 07 08; do
  page_id="${PAGES[$num]}"
  payload_file="${PAYLOAD_DIR}/post-${num}-blocks.json"
  
  if [ -f "$payload_file" ]; then
    echo "Processing Post ${num} (${page_id})..."
    
    # Delete existing blocks
    echo "  Deleting existing blocks..."
    for block_id in $(get_child_blocks "$page_id"); do
      delete_block "$block_id"
    done
    
    # Append new content
    append_blocks "$page_id" "$payload_file"
    echo "  Done!"
  else
    echo "Skipping Post ${num} - payload file not found"
  fi
done

# Create new pages for posts 9-12
echo ""
echo "=== Creating new pages for posts 9-12 ==="

echo "Creating Post 9: Audit → Build..."
PAGE_09=$(create_page "Post 9: Audit → Build")
echo "  Created page: ${PAGE_09}"
append_blocks "$PAGE_09" "${PAYLOAD_DIR}/post-09-blocks.json"
echo "  Done!"

echo "Creating Post 10: One-Command Agent Creation..."
PAGE_10=$(create_page "Post 10: One-Command Agent Creation")
echo "  Created page: ${PAGE_10}"
append_blocks "$PAGE_10" "${PAYLOAD_DIR}/post-10-blocks.json"
echo "  Done!"

echo "Creating Post 11: Council Pattern for Decisions..."
PAGE_11=$(create_page "Post 11: Council Pattern for Decisions")
echo "  Created page: ${PAGE_11}"
append_blocks "$PAGE_11" "${PAYLOAD_DIR}/post-11-blocks.json"
echo "  Done!"

echo "Creating Post 12: x-reader..."
PAGE_12=$(create_page "Post 12: x-reader — Read X Threads Without API")
echo "  Created page: ${PAGE_12}"
append_blocks "$PAGE_12" "${PAYLOAD_DIR}/post-12-blocks.json"
echo "  Done!"

echo ""
echo "=== All posts updated/created! ==="
echo "New page IDs:"
echo "  Post 9:  ${PAGE_09}"
echo "  Post 10: ${PAGE_10}"
echo "  Post 11: ${PAGE_11}"
echo "  Post 12: ${PAGE_12}"
