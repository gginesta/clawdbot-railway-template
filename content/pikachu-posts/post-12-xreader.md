# Post 12: x-reader — Read X Threads Without API

**Status:** ✅ Edited — Ready for review

---

## Thread

1/ The X/Twitter API is expensive and restrictive. But my agents still need to read threads. Here's how. 🧵

2/ The problem: X's API costs $100/month minimum. For basic read access. That's absurd for a hobbyist or small team.

3/ The workaround: x-reader. A tool that fetches X threads without using the official API.

4/ How it works: uses authenticated session cookies (not API keys). Mimics browser behavior. Returns clean thread data.

5/ My agent workflow:
1. Someone shares an X link in Discord
2. Molty detects the link pattern
3. Calls x-reader to fetch the thread
4. Summarizes and posts back

6/ Setup:
```bash
# Export your X auth cookies
export AUTH_TOKEN="..."
export CT0="..."

# Fetch a thread
xreader thread https://x.com/user/status/123456
```

7/ What you get back: the full thread as structured text. Author, content, timestamps. No rate limit anxiety.

8/ Caveats:
• Depends on session cookies (can expire)
• Against X ToS (use at your own risk)
• Not for high-volume scraping

9/ Why it matters: AI agents that can't read the web are limited. X is where conversations happen. Access matters.

Is this ideal? No. But until X offers reasonable API pricing, builders will find workarounds. #AIAgents #BuildInPublic
