#!/bin/bash
# x-fetch.sh — Fetch tweets/articles from X/Twitter URLs
# Pipeline: fxtwitter API → Jina Reader → raw fallback
# Credits: Raphael 🔴 (fxtwitter), Leonardo 🔵 (Jina)
# Usage: bash x-fetch.sh <x_url> [--json|--markdown]

set -euo pipefail

URL="${1:-}"
FORMAT="${2:---markdown}"

if [ -z "$URL" ]; then
  echo "Usage: bash x-fetch.sh <x_url> [--json|--markdown]"
  echo "  x_url: https://x.com/{user}/status/{id} or https://twitter.com/..."
  exit 1
fi

# Extract user and tweet ID from URL
USER=$(echo "$URL" | grep -oP '(?:x|twitter)\.com/\K[^/]+')
TWEET_ID=$(echo "$URL" | grep -oP 'status/\K\d+')

if [ -z "$USER" ] || [ -z "$TWEET_ID" ]; then
  echo "ERROR: Could not parse user/id from URL: $URL"
  exit 1
fi

# --- Method 1: fxtwitter API ---
FXTWITTER_URL="https://api.fxtwitter.com/${USER}/status/${TWEET_ID}"
FX_RESPONSE=$(curl -s --max-time 10 "$FXTWITTER_URL" 2>/dev/null || echo "")

if [ -n "$FX_RESPONSE" ] && echo "$FX_RESPONSE" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
  SOURCE="fxtwitter"
  
  if [ "$FORMAT" = "--json" ]; then
    echo "$FX_RESPONSE"
    exit 0
  fi

  # Extract as markdown
  echo "$FX_RESPONSE" | python3 -c "
import json, sys

data = json.load(sys.stdin)
tweet = data.get('tweet', {})
author = tweet.get('author', {})

print(f\"# @{author.get('screen_name', '?')} ({author.get('name', '?')})\")
print(f\"**Date:** {tweet.get('created_at', '?')}\")
print(f\"**Views:** {tweet.get('views', '?')} | **Likes:** {tweet.get('likes', '?')} | **RTs:** {tweet.get('retweets', '?')} | **Bookmarks:** {tweet.get('bookmarks', '?')}\")
print(f\"**Source:** fxtwitter\")
print(f\"**URL:** {tweet.get('url', '?')}\")
print()

# Check for article
article = tweet.get('article')
if article:
    print(f\"## {article.get('title', 'Untitled Article')}\")
    print()
    blocks = article.get('content', {}).get('blocks', [])
    for block in blocks:
        text = block.get('text', '')
        btype = block.get('type', '')
        if text:
            if btype == 'header-one':
                print(f'# {text}')
            elif btype == 'header-two':
                print(f'## {text}')
            elif btype == 'header-three':
                print(f'### {text}')
            elif btype == 'blockquote':
                print(f'> {text}')
            elif btype == 'code-block':
                print(f'\`\`\`\n{text}\n\`\`\`')
            else:
                print(text)
            print()
else:
    # Regular tweet
    text = tweet.get('text', '')
    if text:
        print('## Tweet')
        print()
        print(text)
        print()

# Media
media = tweet.get('media', {})
if media and media.get('all'):
    print('## Media')
    for m in media['all']:
        url = m.get('url', m.get('thumbnail_url', ''))
        mtype = m.get('type', 'unknown')
        if url:
            print(f'- [{mtype}]({url})')
    print()

# Quote tweet
qt = tweet.get('quote')
if qt:
    print('## Quoted Tweet')
    qt_author = qt.get('author', {})
    print(f'> @{qt_author.get(\"screen_name\", \"?\")}: {qt.get(\"text\", \"\")}')
    print()
"
  exit 0
fi

# --- Method 2: Jina Reader ---
JINA_URL="https://r.jina.ai/https://x.com/${USER}/status/${TWEET_ID}"
JINA_RESPONSE=$(curl -s --max-time 15 "$JINA_URL" 2>/dev/null || echo "")

if [ -n "$JINA_RESPONSE" ] && [ ${#JINA_RESPONSE} -gt 100 ]; then
  SOURCE="jina"
  
  if [ "$FORMAT" = "--json" ]; then
    echo "{\"source\": \"jina\", \"user\": \"${USER}\", \"tweet_id\": \"${TWEET_ID}\", \"content\": $(echo "$JINA_RESPONSE" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")}"
    exit 0
  fi

  echo "# @${USER} (via Jina Reader)"
  echo "**Source:** jina"
  echo "**URL:** https://x.com/${USER}/status/${TWEET_ID}"
  echo
  echo "$JINA_RESPONSE"
  exit 0
fi

# --- All methods failed ---
echo "ERROR: Could not fetch tweet. All methods failed."
echo "  fxtwitter: ${FXTWITTER_URL}"
echo "  jina: ${JINA_URL}"
echo "  Try: spawn a Grok sub-agent with native X access"
exit 1
