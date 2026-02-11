# Post 8: Unbrowse DIY — Browse Without a Browser

**Status:** ✅ Edited — Ready for review (was already polished)

---

## Thread

1/ My AI agents need to read web pages. But spinning up a browser for every fetch is slow and expensive. Enter Unbrowse. 🧵

2/ The problem: most web content is behind JavaScript rendering. Simple HTTP requests get empty HTML.

3/ The expensive solution: Puppeteer, Playwright, headless Chrome. Works, but heavy. Memory-hungry. Slow startup.

4/ Unbrowse: a lightweight web scraper that handles JS-rendered content without a full browser. Uses clever tricks to extract readable content.

5/ How I use it: my agents call Unbrowse to fetch articles, documentation, tweets. Returns clean markdown, not raw HTML.

6/ Integration with OpenClaw:
```
web_fetch:
  url: "https://example.com/article"
  extractMode: "markdown"
```

7/ Real example: when someone shares a link in Discord, Molty auto-fetches it, summarizes it, posts the summary. Takes ~3 seconds.

8/ DIY setup: Unbrowse runs as a microservice. Deploy on Railway, point your agents at it. Shared across all agents.

9/ Cost: practically nothing. One Railway service handles hundreds of requests/day. Maybe $2/month.

If your agents read the web, you need something like this. Unbrowse isn't the only option—but it's the one I use. #AIAgents #BuildInPublic
