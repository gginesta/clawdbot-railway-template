# We Gave Our AI Agents Pokémon Names. Here's What We Actually Learned About Sub-Agent Design

**PLATFORM:** X/Twitter  
**TYPE:** Thread  
**INSPIRATION LINK: https://x.com/pbteja1998/status/2017662163540971756
**QUOTE/REPOST TARGET: https://x.com/pbteja1998/status/2017662163540971756

---

1/ we name our AI sub-agents after pokémon. yes really. but it's not just vibes, it solves a real problem. #OpenClaw

2/ when you have 6+ agents running simultaneously, you need to tell them apart instantly. "agent-3" vs "agent-4" is useless in logs. squirtle writing specs, charmander building features, pikachu drafting tweets? instantly clear who did what.

3/ started with ad-hoc spawning. total mess. agents stepping on each other, no clear ownership. the fix was giving each one a soul file defining: role, boundaries, which AI model to use, what they can and can't touch.

4/ model matching per role is the real unlock. your strategist agent needs opus. your audit bot is fine on flash. your bulk data processor runs on qwen. treating every task as opus-worthy is just burning money.

5/ one sub-agent built 5 webclaw features (search, pinning, date grouping, smart names, channel badges) in 2 minutes flat. another drafted all our marketing content in 15 min. the constraint is design, not speed.

[SCREENSHOT: webclaw UI showing features built by sub-agent]

6/ saw @pbteja1998's mission control guide (8K+ hearts, wild). his soul/memory system is what inspired our agent structure. we added themed naming and per-role model routing on top. different implementation, same DNA.

how are you organizing your agent squads? genuinely curious what patterns emerge.
