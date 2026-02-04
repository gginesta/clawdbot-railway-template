# Molty Clone — Zero → One Setup (Railway + OpenClaw)

This guide is written so a **non-technical** person can get a “Molty-like” personal assistant running.

It contains **no private keys, tokens, or identifying info**. Anywhere you see `<LIKE_THIS>`, you will fill in your own values.

---

## What you’re building
- A personal assistant powered by **OpenClaw** (the agent framework).
- Hosted on **Railway** (so you don’t need to manage servers).
- Optional: Telegram/Discord/etc messaging channels.
- Optional: Browser automation (headless) via **Brave**.

---

## Before you start (accounts you’ll need)
1) **Railway account**: https://railway.app/
2) **GitHub account**: https://github.com/
3) At least one AI model provider key:
   - Anthropic (Claude) OR OpenAI OR OpenRouter, etc.

If you only do one: start with **Anthropic** (Claude), then expand later.

---

## Step 1 — Create your Railway project from a template
You need a Railway-ready wrapper repo (a Docker-based template that:
- builds OpenClaw
- exposes port 8080
- mounts a persistent `/data` volume

### Option A (recommended): use a maintained fork of the Railway template
Use a fork that already includes:
- the **webhook JSON middleware fix** (prevents OpenClaw proxied routes from breaking)
- **Brave** installation (for more reliable headless browser automation)

**Best practice (privacy):**
1) Start from the maintained fork URL your friend provides.
2) Click **Fork** to *your own* GitHub account (so the running service isn’t visibly tied to anyone else).
3) In Railway:
   - **New Project → Deploy from GitHub Repo**
   - Select *your* fork

### Option B: use upstream and patch yourself
If you prefer starting from upstream:
- Upstream template: `vignesh07/clawdbot-railway-template`
- You’ll need to apply the webhook middleware fix and (optionally) add Brave to the Dockerfile.


---

## Step 2 — Add a persistent Volume in Railway
In Railway for this service:
1) Add a **Volume**
2) Mount path: `/data`

Why: OpenClaw stores config + memory + credentials under `/data/.openclaw/`.

---

## Step 3 — Set environment variables in Railway
In Railway → Service → Variables, add at least:

### Required
- `ANTHROPIC_API_KEY = <your_key>`  *(or another provider key)*

### Highly recommended
- `OPENCLAW_GATEWAY_TOKEN = <generate_a_long_random_token>`
  - This protects your web control UI.
  - Use a password manager to generate 32+ random characters.

### Optional (add later)
- `OPENAI_API_KEY = <your_key>`
- `OPENROUTER_API_KEY = <your_key>`
- `BRAVE_API_KEY = <your_key>` (only if you want built-in web_search via Brave Search)

Notes:
- Don’t paste keys into chat with anyone.
- Put them only in Railway’s Variables.

---

## Step 4 — First deploy + open the web UI
1) Trigger deploy (Railway will build Docker image; first build can take a while)
2) Open the service URL Railway gives you
3) You should see an OpenClaw web UI

If you see errors:
- Check Railway logs
- Make sure the service listens on `PORT` (most templates do this automatically)

---

## Step 5 — Run OpenClaw onboarding
Use the web UI to:
- Create your agent identity (name, tone)
- Configure default model/provider
- Configure one messaging channel (optional)

**Keep it simple at first:** web UI only is fine.

---

## Step 6 — Enable Telegram (assumed)

1) In Telegram, message **@BotFather**
2) Create a bot (`/newbot`) and copy the **bot token**
3) Put the token into **Railway → Variables** (the exact variable name depends on the template README)
4) Pair/allowlist:
   - Allow your own Telegram user ID
   - (Optional) Allow one group chat ID

If your template supports it, prefer an **allowlist** policy over “respond to everyone.”


---

## Step 7 — (Optional) Enable browser automation (Brave)
Browser automation is the #1 place where Docker hosting differs from laptops.

### The working approach in containers
- Use **Brave headless** with a remote debugging port
- Configure OpenClaw browser to **attach** to that running instance

Typical pattern:
1) Start Brave inside the container:
```bash
nohup brave-browser --headless=new --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 --remote-debugging-address=127.0.0.1 \
  --disable-dev-shm-usage > /dev/null 2>&1 &
```
2) Configure OpenClaw browser:
```json
{
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true,
    "defaultProfile": "openclaw",
    "executablePath": "/usr/bin/brave-browser",
    "attachOnly": true
  }
}
```

If you don’t need browser automation: skip this entirely.

---

## Step 8 — Quick “it works” checklist
- [ ] Web UI loads
- [ ] Agent responds to chat
- [ ] Config persists after redeploy (volume mounted)
- [ ] (Optional) Telegram/Discord can send + receive
- [ ] (Optional) Browser tool can open `https://example.com` and snapshot it

---

## What to paste into ChatGPT for help (copy/paste)
Use this prompt with ChatGPT when you get stuck:

> You are my setup assistant. I’m deploying an OpenClaw agent to Railway using a Docker template repo. I am non-technical.
>
> Goals:
> 1) Deploy successfully on Railway
> 2) Persist data under /data using a volume
> 3) Configure one AI provider key
> 4) (Optional) Add Telegram
> 5) (Optional) Enable Brave headless browser with attachOnly
>
> Please ask me 1 question at a time. When you tell me to change something, specify exactly where (Railway Variables / Railway Volume / GitHub repo file / OpenClaw config).

---

## Safety basics (don’t skip)
- Never paste API keys/tokens into group chats.
- Use a password manager.
- Treat your Railway URL like a production service.

---

If you want, tell me what template repo you chose and which channel (Telegram/Discord) you want first, and I can tailor the exact variables/config keys to that template.
