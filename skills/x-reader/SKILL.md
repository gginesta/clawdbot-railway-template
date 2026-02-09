---
name: x-reader
description: Read-only Twitter/X viewing and thread extraction using headless Brave + cookie injection. Use when user asks to view, read, summarize, or extract a tweet/thread, or when Pikachu/Peach/Raphael need to reference X posts reliably without posting.
---

# x-reader (Read-only)

Goal: reliably **view tweets + threads** and extract clean text for summarization, without posting.

## Safety rules (non-negotiable)
- **Read-only**: do NOT like/retweet/reply/post.
- **Never paste cookies** (`auth_token`, `ct0`) into chat or Notion.
- Only use cookies from `/data/workspace/credentials/twitter.env`.
- Only navigate to `https://x.com/*`.

## Quick workflow

### A) Read a tweet or thread by URL
1) Ensure the browser tool is available.
2) Open the tweet URL.
3) If you hit a login wall/blank page, do cookie injection (below), then reload.
4) Expand the thread:
   - click **“Show more”**, **“Show replies”**, **“Read more”** where relevant
   - scroll until no new tweets load
5) Extract:
   - author, timestamp
   - main tweet text
   - thread tweets in order (if thread)
   - any quoted tweet text (if present)
6) Output:
   - **Thread transcript** (plain text)
   - **Summary** (5–10 bullets)
   - **Takeaways** (what matters + why)

### B) Summarize into Notion Content Hub (optional)
If the user wants it saved:
- Create a markdown file with:
  - URL
  - transcript
  - summary
  - attribution line
- Push to Notion Content Hub parent page using `notion-enhanced/scripts/md-to-notion.js`.

## Cookie injection (login workaround)

Read cookie values from:
- `/data/workspace/credentials/twitter.env`

Then in the browser context (JS evaluate), set cookies for `x.com`:
- `auth_token=<value>; domain=.x.com; path=/; secure; samesite=lax`
- `ct0=<value>; domain=.x.com; path=/; secure; samesite=lax`

Reference: `references/cookie-injection.js`.

## Notes
- X may rate-limit or show partial content without scrolling.
- If a thread is long, prioritize: top tweet + author’s follow-up tweets + any tweets with images/links.
