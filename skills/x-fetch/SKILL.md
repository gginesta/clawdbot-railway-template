---
name: x-fetch
description: Fetch tweets, threads, and X Articles reliably without auth. Use when you need to read/extract content from any x.com or twitter.com URL.
version: 1.0.0
author: Molty 🦎 (TMNT Squad)
credits: Pipeline discovered by Raphael 🔴 (fxtwitter) and Leonardo 🔵 (Jina reader). Built into skill by Molty.
---

# x-fetch — Reliable X/Twitter Content Extraction

Fetch tweets, threads, and X Articles without authentication or browser automation.

## ⚠️ Safety Rules
- **Read-only** — never post, like, retweet, or reply
- **Attribution** — always credit the original author
- **No cookies needed** — these methods work without auth

## Pipeline (try in order)

### 1. fxtwitter API (BEST — free, no auth, returns JSON)

```bash
curl -s "https://api.fxtwitter.com/{username}/status/{tweet_id}"
```

**Returns:** Full JSON with tweet text, author info, metrics (likes/retweets/views), media URLs, and **full X Article content** (in `tweet.article.content.blocks`).

**Extract tweet text:**
```bash
curl -s "https://api.fxtwitter.com/{user}/status/{id}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tweet = data.get('tweet', {})
print('Author:', tweet.get('author', {}).get('name'))
print('Handle:', '@' + tweet.get('author', {}).get('screen_name', ''))
print('Date:', tweet.get('created_at'))
print('Views:', tweet.get('views'))
print('Likes:', tweet.get('likes'))
print()
print(tweet.get('text', ''))
"
```

**Extract X Article content:**
```bash
curl -s "https://api.fxtwitter.com/{user}/status/{id}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
article = data.get('tweet', {}).get('article')
if article:
    print('# ' + article.get('title', 'Untitled'))
    print()
    for block in article.get('content', {}).get('blocks', []):
        text = block.get('text', '')
        if text:
            print(text)
            print()
else:
    print('No article found — this is a regular tweet.')
    print(data.get('tweet', {}).get('text', ''))
"
```

### 2. Jina Reader (FALLBACK — returns markdown)

```bash
curl -s "https://r.jina.ai/https://x.com/{user}/status/{id}"
```

Returns the page as readable markdown. Works for tweets and some articles. May not get full article content for long X Articles.

### 3. web_fetch with vxtwitter (FALLBACK 2)

Use the `web_fetch` tool with vxtwitter URL:
```
https://vxtwitter.com/{user}/status/{id}
```

### 4. Grok (LAST RESORT)

Grok (xai/grok-3) has native X access. Spawn a sub-agent with model `grok` and ask it to read the tweet. Only use when other methods fail — costs more tokens.

## URL Parsing

Extract username and tweet ID from any X/Twitter URL:
- `https://x.com/{user}/status/{id}`
- `https://twitter.com/{user}/status/{id}`
- `https://x.com/{user}/status/{id}?s=20` (strip query params)

```python
import re
url = "https://x.com/sillydarket/status/2022394007448429004?s=20"
match = re.search(r'(?:x|twitter)\.com/(\w+)/status/(\d+)', url)
if match:
    user, tweet_id = match.groups()
```

## What You Get

| Field | fxtwitter | Jina | vxtwitter |
|-------|-----------|------|-----------|
| Tweet text | ✅ | ✅ | ✅ |
| Author info | ✅ (full) | ⚠️ (partial) | ⚠️ |
| Metrics (likes/views) | ✅ | ❌ | ⚠️ |
| Media URLs | ✅ | ⚠️ | ✅ |
| X Article full text | ✅ | ⚠️ | ❌ |
| Thread (multi-tweet) | ⚠️ (main tweet only) | ⚠️ | ⚠️ |
| JSON format | ✅ | ❌ (markdown) | ❌ |

## Thread Extraction

For threads (multi-tweet), fxtwitter only returns the main tweet. To get the full thread:
1. Fetch the main tweet via fxtwitter
2. Check `tweet.replying_to_status` for parent tweets
3. Use Jina reader as fallback — it often captures visible thread context

## Examples

**Quick tweet fetch:**
```bash
curl -s "https://api.fxtwitter.com/sillydarket/status/2022394007448429004" | python3 -c "import json,sys; d=json.load(sys.stdin)['tweet']; print(f\"{d['author']['name']} (@{d['author']['screen_name']})\n{d.get('text','')}\nViews: {d.get('views')} | Likes: {d.get('likes')}\")"
```

## When to Use This vs x-reader Skill

| Scenario | Use |
|----------|-----|
| Fetch specific tweet/article by URL | **x-fetch** (this skill) |
| Browse timeline, search tweets | **x-reader** (browser-based) |
| Need screenshots of tweets | **x-reader** (browser-based) |
| Quick content extraction | **x-fetch** (this skill) |

## CLI Wrapper

A ready-to-run script is included: `x-fetch.sh`

```bash
# Markdown output (default)
bash x-fetch.sh "https://x.com/user/status/123456"

# JSON output
bash x-fetch.sh "https://x.com/user/status/123456" --json
```

**Output fields (normalized):**
- `author` — name + handle
- `date`, `views`, `likes`, `retweets`, `bookmarks` — metrics
- `text` — tweet content (or article body for X Articles)
- `media` — linked images/videos
- `quote` — quoted tweet if present
- `source` — which method succeeded (fxtwitter|jina)

## Deprecation Note

This skill supersedes the browser-based approach in x-reader for URL-based content extraction. x-reader is still needed for browsing, searching, and screenshot capture.
