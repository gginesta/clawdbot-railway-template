# Pikachu — Post Ideas v1 (2026-02-07)

*Based on: community trends from the last week + our TMNT accomplishments since inception*

---

## Trending Community Topics (Context)

- @pbteja1998's "Mission Control" guide went mega-viral (8K+ ❤️, 864 RTs) — 10-agent squad with Convex, heartbeats, SOUL files
- OpenClaw security audit drama (ZeroLeaks scored 2/100, then patched within a week)
- levelsio calling OpenClaw "a really special moment in history" 
- Hosted OpenClaw platforms launching ($7K MRR in 3 days)
- Community debating MEMORY.md patterns, heartbeat costs, agent-to-agent comms
- @cass_builds: "The hardest part isn't the AI. It's the nginx config."

---

## 📝 Post Ideas

### 1. "How a Non-Technical Person Runs a Multi-Agent AI Team"
**Angle:** Guillermo's perspective — not a developer, but running 2+ AI agents on Railway with Discord, Syncthing, Todoist, and Notion integration. The "non-coder managing AI" angle is underrepresented.

**Why it works:** Most OpenClaw content is from devs. Guillermo's story (12-hour setup session, learning by doing) is relatable to the wave of non-technical people trying this.

**Inspiration:** @pbteja1998's Mission Control guide (attribute it). Our setup is different — we use Railway (not a VPS), themed sub-agents, and coordinator pattern instead of Convex.

**Screenshottable:** Notion Mission Control page, Todoist integration, Discord squad channels, WebClaw UI

**Privacy check:** ✅ Can show architecture without exposing personal data

---

### 2. "Agent-to-Agent Communication: What Actually Works (and What Doesn't)"
**Angle:** We tried webhooks first. They're fragile. Discord channels are better for multi-agent comms. Here's why, with our actual setup.

**Why it works:** The community is actively debating how agents should talk. @pbteja1998 uses Convex + session messaging. We use Discord channels + Syncthing for file sharing. Different approach, real lessons.

**Key lessons to share:**
- Webhooks = emergencies only (we learned this the hard way)
- Discord threads = per-topic organization that scales
- Syncthing = file sync across agents without cloud APIs
- Channel ownership model (who responds where)

**Screenshottable:** Discord channel structure, Syncthing dashboard showing 4-node mesh, agent-link skill config

**Privacy check:** ✅ Redact tokens/IDs in screenshots

---

### 3. "We Gave Our AI Agents Pokémon Names. Here's What We Actually Learned About Sub-Agent Design."
**Angle:** Fun hook (Pokémon theme) but substance underneath — how we evolved from ad-hoc spawning to formalized sub-agents with SOUL.md, MEMORY.md, and context files. The Peach gold-standard template.

**Why it works:** Everyone's doing multi-agent but few share the actual file structure and design patterns. The Pokémon theme makes it shareable. Lesson: naming/theming agents isn't just fun — it helps you think about role boundaries.

**Inspiration:** @pbteja1998's SOUL system + our iteration on it. Raphael's Super Mario sub-team under Brinc.

**Screenshottable:** Notion Pokémon Squad page, folder structure, SOUL.md template, the role/model assignment table

**Privacy check:** ✅ Brinc-specific content stays out, focus on pattern not project

---

### 4. "The $0 AI Memory Stack: QMD + Syncthing + Markdown Files"
**Angle:** Our memory architecture costs nothing extra — QMD (local hybrid search by Shopify's CEO), Syncthing (P2P file sync), and plain markdown files. No vector DB subscription, no cloud sync service.

**Why it works:** Cost is a huge community concern. @pbteja1998 mentions Convex. Others use Pinecone/Weaviate. We run entirely local-first. The "Shopify CEO built our memory search" hook is interesting.

**Key details:**
- QMD: BM25 + vector + reranking, all local
- Syncthing: 4-node mesh (2 Railway containers + desktop + laptop)
- MEMORY.md as curated long-term memory vs daily logs
- Memory maintenance during heartbeats

**Inspiration:** @pitsch's tweet about MEMORY.md pattern being "from OpenClaw originally"

**Screenshottable:** Syncthing 4-node connected dashboard, memory file structure, QMD config snippet

**Privacy check:** ✅ Redact device IDs and API keys

---

### 5. "7 Days Running AI Agents 24/7: An Honest Cost & Lessons Breakdown"
**Angle:** Raw retrospective. What worked, what broke, what we'd do differently. Include actual lessons learned (we have 35+ documented).

**Why it works:** The community craves honest takes, not hype. @cass_builds' "hardest part is nginx config" resonated because it's real. Our lessons (backup before update, files over system events, test before handoff) are practical.

**Top lessons to highlight:**
- #1: Backup before update (NON-NEGOTIABLE, learned after a crash)
- #6: Mental notes don't survive — WRITE IT DOWN
- #34: Files beat system events for persistence
- #35: Deploy and test before telling the human
- The model escalation strategy (Opus for thinking, Flash for heartbeats, Qwen for bulk)

**Inspiration:** @emillyhumphress: "Past the hype, this is real game-changer territory"

**Screenshottable:** Lessons table from memory files, model strategy table, cron job list

**Privacy check:** ✅ Lessons are generic enough to share safely

---

### 6. "How We Handle the OpenClaw Security Problem (Prompt Injection Defense for Agent Squads)"
**Angle:** The ZeroLeaks audit exposed real risks. Here's what we do: SECURITY.md, channel ownership model, trust boundaries between agents, what agents can/can't access.

**Why it works:** SUPER timely — the security audit drama is this week's biggest OpenClaw story. @gm_holly_ and @NotLucknite's posts got massive engagement. We can share practical mitigations.

**Inspiration:** @theonejvo's hack + fix thread (attribute it). @NotLucknite's ZeroLeaks audit.

**Screenshottable:** SECURITY.md structure (redacted), channel ownership table, agent permission model

**Privacy check:** ⚠️ Careful — don't reveal actual security config details, share the PATTERN not the specifics

---

### 7. "Railway + OpenClaw: Deploy AI Agents Without Touching a Server"
**Angle:** Quick, practical guide. We run 2 agents + WebClaw on Railway. Docker, persistent volumes, auto-deploy. The "@cass_builds is right about nginx being hard, so here's how we skip it" angle.

**Why it works:** @saviomartin7 made $7K MRR in 3 days hosting OpenClaw for non-techies. There's clearly demand. Our Railway setup is simpler than VPS and works.

**Inspiration:** @cass_builds' "hardest part is nginx" tweet + @saviomartin7's hosted platform (attribute both)

**Screenshottable:** Railway dashboard (redacted), Dockerfile snippets, gateway config structure

**Privacy check:** ✅ Redact tokens and URLs

---

## 🎯 Recommended First 3 Posts (Priority Order)

1. **#5 "7 Days Running AI Agents 24/7"** — Honest retrospective, broadest appeal, shows depth
2. **#3 "Pokémon Sub-Agent Design"** — Fun hook, shareable, shows our unique approach
3. **#2 "Agent-to-Agent Communication"** — Practical, fills a gap in community knowledge

## 📌 Rules for All Posts
- **Always attribute inspiration** with links to the original posts
- **Always include screenshots** (redacted of personal data)
- **Show real files/configs** — not theoretical, actual things we use
- **Honest about failures** — what broke, not just what worked
- **End with a question** to invite discussion
- **No corporate tone** — builder sharing with builders
