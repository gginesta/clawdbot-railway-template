# Unbrowse DIY Post — v2 (Editor: Pikachu)

## SINGLE TWEET

Saw @getFoundry's Unbrowse.ai and thought — I can build this. So my AI agents did. In one day.

Browse a site once, capture the API calls, never open a browser again. 10-45s → 200ms. Pure bash + curl.

Credit where it's due: https://x.com/getFoundry/status/2018751025520513391

---

## THREAD (4 tweets)

**1/**
My AI agents spend half their time waiting on browsers. Loading pages, clicking buttons, scraping DOM. It's slow, flaky, and expensive.

Then I saw @getFoundry's Unbrowse.ai and had an idea: what if we just... stopped browsing?

So we built our own version. In one day.

https://x.com/getFoundry/status/2018751025520513391

**2/**
The concept is simple: visit a site once with a real browser, record every API call via CDP, then generate a reusable "skill" — just curl commands.

First visit: 10-45 seconds. Every visit after: 200ms.

No browser. No Puppeteer. Just bash, JSON, and curl. The skill syncs across my whole squad automatically.

**3/**
Honest take on what this actually handles:

It nails REST + CRUD — which is ~70% of SaaS. Struggles with OAuth flows, WebSockets, and GraphQL. So it's not magic.

I'd say 80% discovery/scaffolding, 20% human polish. But that 80% used to be 100% manual browser time. I'll take it.

**4/**
The wildest part: 6 sub-agents working in parallel wrote the full spec + MVP in under 2 hours. 2,300-line spec in 9.5 minutes.

Foundry's version is more polished (and has x402 monetization, which is cool). Ours is duct tape and bash — but it's self-contained and it works.

Sometimes the DIY version is exactly what you need.

---

## EDITOR NOTES

- Tightened from 5 → 4 tweets
- Moved the "honest take" to tweet 3 (the authenticity anchor) — it's now the heart of the thread
- Tweet 1 leads with the pain (browser waiting) not the solution — hooks better
- Dropped "game-changer," "multi-agent fleet," bullet-point formatting
- Each tweet works standalone: pain→solution→honesty→build story
- Kept Foundry credit in tweet 1 (prominent, classy) and tweet 4 (comparison)
- "My squad" in tweet 2 feels natural without jargon
- Single tweet version is self-contained for those who don't want to thread
