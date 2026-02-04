# Molty Clone — Improve, Configure, and Harden (After Onboarding)

This document assumes you already have a working “Molty-like” OpenClaw agent deployed.

It contains **no private keys**. It does include a checklist of **which keys to get** and **how**.

---

## 1) Security upgrades (do these first)

### A. Lock down the web UI
- Ensure the gateway/control UI is protected by a strong token.
- Prefer:
  - token auth enabled
  - device auth enabled (unless you have a strong reason)

### B. Restrict who can message the bot
For any messaging channel:
- Use allowlists (specific user IDs / chat IDs)
- In group chats: require mention (or restrict to one group)

### C. Secrets hygiene
- Put secrets in Railway Variables (or a secrets manager)
- Never commit secrets to GitHub
- Rotate any key that was ever pasted into chat

### D. Backups
Make sure you can restore:
- `/data/.openclaw/openclaw.json`
- `/data/.openclaw/credentials/`
- `/data/.openclaw/memory/`

Recommended:
- Nightly backup tarball + keep last N
- Optional push to a private GitHub backup repo (sanitized)

---

## 2) Reliability upgrades

### A. Context pruning + compaction
Long chats can get expensive or crashy if you over-stuff context.
- Enable a pruning strategy (TTL or size-based)
- Enable compaction / summarization safeguards

### B. Heartbeats (lightweight, not spammy)
Use heartbeats to:
- Check “anything urgent?” once every 30–60 minutes
- Avoid sending messages unless needed

Suggested:
- Heartbeat every 1h
- Use a cheaper/faster model for heartbeats

### C. Model routing (save money)
If your setup supports it, route:
- Simple admin / quick questions → cheaper model
- Deep planning / coding / architecture → premium model

If routing isn’t supported, you can still:
- Set a cheaper default model
- Manually switch models when needed

---

## 3) Browser automation (Brave) — best practice
In many Docker hosts, auto-launching the browser can be flaky. The reliable pattern is:

1) Install Brave in the image (Dockerfile)
2) Use **attachOnly** in config
3) On boot, run Brave headless with CDP enabled:
```bash
nohup brave-browser --headless=new --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 --remote-debugging-address=127.0.0.1 \
  --disable-dev-shm-usage > /dev/null 2>&1 &
```

Notes:
- `--disable-dev-shm-usage` reduces crashes in small container shared memory.
- DBus warnings in logs are usually harmless in headless containers.

---

## 4) “Keys you should go get” checklist (optional, but nice)

### A. AI model providers
Pick 1–2 to start:
- Anthropic API key (Claude)
- OpenAI API key
- OpenRouter API key (aggregates many models)

### B. Web search
- Brave Search API key (for `web_search` without scraping)

### C. Messaging
- Telegram Bot token (BotFather)
- Discord bot token (Discord Developer Portal)

### D. Optional: Notion integration
- Notion API key
- Create a Notion integration and share the target workspace/pages with it

---

## 5) Quality-of-life improvements

### A. A clear “SOUL.md” / persona
Write a short file that defines:
- tone (direct, no fluff)
- boundaries (don’t do external actions without asking)
- formatting preferences

### B. A “TOOLS.md” local cheat sheet
Store only non-sensitive operational notes:
- which channels you own
- which IDs matter
- common commands

### C. Channel ownership rule (prevents duplicate responses)
Even with a single agent, adopt this mindset:
- Don’t respond everywhere automatically
- Only respond where you’re expected to

---

## 6) Suggested TODOs for the next week
- [ ] Add backups (daily) and test a restore
- [ ] Tighten allowlists + require mention in groups
- [ ] Set heartbeat cadence + rules
- [ ] Add Brave headless boot script (if you use browser tool)
- [ ] Document your config: what’s enabled, why
- [ ] Add a “safe word” rule for group contexts (if you ever join group chats)

---

## 7) Copy/paste prompt for ChatGPT (improvement mode)

> You are my OpenClaw operations assistant. My agent is deployed on Railway and working.
>
> Help me harden and improve it in this order:
> 1) Security: lock down web UI and message allowlists
> 2) Backups + restore test
> 3) Heartbeats: reduce noise, use cheap model
> 4) Browser automation: Brave headless attachOnly pattern
> 5) Cost controls: model routing / model switching guidelines
>
> Ask me one question at a time and don’t assume my config keys—tell me exactly where to click in Railway or which JSON block to edit.

---

If you tell me:
- which template repo you used
- which channels you enabled
- which provider you picked (Anthropic/OpenAI/etc)

…I can produce a customized checklist with exact variable names and config snippets.
