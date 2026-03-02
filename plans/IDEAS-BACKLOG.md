# Ideas Backlog

Ideas worth revisiting later but not priority now.

---

## Android OpenClaw Host

**Added:** 2026-03-02
**Source:** [X Article by @pranay5255](https://x.com/pranay5255/status/2027431212864966725) — 330k views on running PicoClaw on old Android via Termux
**Status:** Parked — not a priority

**Idea:** Run full OpenClaw on an old Android phone (Guillermo has one in good condition)

**What would work:**
- Core gateway, Telegram, Discord, webhooks, basic tools
- ~300-500MB RAM footprint without browser
- 24/7 on home WiFi, $0/month

**What wouldn't:**
- Browser control (no headless Chrome on Termux)
- Some native Node modules

**Potential use cases:**
- April (personal assistant) — lightweight, always-on
- Backup fleet member if Railway goes down
- Home automation / local network agent

**Why parked:**
- Current Railway setup works well
- Not a massive value add for TMNT core ops
- Would need testing time we don't have now

**Revisit when:**
- April deployment is on the roadmap
- We want a truly local/offline agent
- Railway costs become a concern
