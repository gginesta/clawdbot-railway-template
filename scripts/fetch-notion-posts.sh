#!/bin/bash
source /data/workspace/credentials/notion.env

# Post 1: 7 Days
echo "=== POST 1: 7 Days Running AI Agents ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-81b1-919e-c558bc646b54/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 2: Pokémon Sub-Agent Architecture ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-81b4-87eb-f0ed785cc05c/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 3: Agent-to-Agent Communication ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-810e-b084-dbfc8db32e33/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 4: The $0 Memory Stack ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-81ed-a87b-ea70171c3c5b/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 5: Non-Technical Founder ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-8143-97df-c48255df13d7/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 6: Security/Prompt Injection ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-8157-b31e-cb143e876ad6/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 7: Railway + OpenClaw ==="
curl -s "https://api.notion.com/v1/blocks/30039dd6-9afd-8148-9b65-dfb6a0d580f5/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== POST 8: Unbrowse DIY (verify) ==="
curl -s "https://api.notion.com/v1/blocks/30139dd6-9afd-81e3-bcb5-c156209badfb/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== REVISED Feb 9 Content ==="
curl -s "https://api.notion.com/v1/blocks/30239dd6-9afd-810e-8320-c359650f03a5/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"

echo -e "\n\n=== X-Reader Page ==="
curl -s "https://api.notion.com/v1/blocks/30239dd6-9afd-8196-b184-e9815369acd6/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" -H "Notion-Version: 2022-06-28"
