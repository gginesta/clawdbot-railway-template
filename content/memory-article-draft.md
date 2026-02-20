# We Spent 4 Days on AI Memory — Here's What Actually Worked

*By Guillermo Ginesta*

---

I'm going to be honest with you: four days. Four actual, full days of my life went into getting AI agent memory to work. Not "experimenting." Not "exploring options." I mean debugging, configuring, re-indexing, watching containers crash, and Googling the same OOM error message with increasing desperation. 

Here's what I learned — and more importantly, what finally worked.

---

## Why Agent Memory Even Matters

We run three AI agents as a coordinated squad:

- **Molty** — the coordinator. Routes tasks, manages context, keeps the squad aligned.
- **Raphael** — handles sales. Knows our pipeline, our leads, our follow-up cadences.
- **Leonardo** — ventures. Tracks startups we're watching, deals in motion, research threads.

Each of these agents needs to *remember* things across conversations. Not just "what did we talk about last Tuesday" — but deep context. Past decisions. Client history. What we tried, what failed, what we shipped. Without memory, every conversation starts from zero. You end up re-explaining your entire business every single time, which is… not ideal when you're trying to move fast.

So we set out to build a proper memory layer. And we chose the wrong tool first. Obviously.

---

## The Plan: QMD, a Local Vector Database

QMD looked great on paper. Local vector database, hybrid search (semantic + keyword), reranking, query expansion. All the things you'd want for intelligent retrieval. We'd run it as a sidecar on our Railway containers alongside each agent.

We spent Day 1 just getting it installed and configured. That part actually went fine.

[SCREENSHOT: QMD installation and initial config — terminal output showing successful setup]

Then we indexed our files. 400+ documents across meeting notes, decisions, project briefs, lead profiles, research threads. The indexing itself? Beautiful. Watched it chunk and embed everything, metadata intact, ready to query.

Day 2: Time to actually use it.

The query came back empty. No results. We checked the index — everything was there. We checked the query — totally reasonable. Checked logs.

```
FATAL: killed (OOM)
```

Ah.

---

## Four Days of Watching Containers Die

Here's what happens with QMD's hybrid search: it loads a reranker model *and* a query expansion model at query time. Together, they need roughly 6GB of RAM to operate comfortably.

Our Railway containers have 2-4GB.

[SCREENSHOT: Railway container memory metrics — RAM usage spiking to limit right before OOM kill]

So every single search query killed the container. Dead. Restart. The agent would come back up, try to answer a question, pull from memory, *die*, restart, and try again. Infinite loop of optimistic failure.

We tried everything over Days 2, 3, and 4:

**Keyword-only fallback** — disabled the semantic/hybrid search entirely, went pure BM25 keyword matching. This worked! Until it didn't. Keyword search on AI agent memory is rough. "When did we decide to drop the Hong Kong deal?" returns nothing if your notes say "deprioritized HK opportunity." Semantic search exists for a reason.

**Lighter model configs** — tried swapping the reranker for a smaller model. Helped a bit. Still OOM'd under load. And the retrieval quality dropped noticeably.

**Reducing index size** — pruned down to ~200 files. Still crashed. 150 files. Crashed. At some point you're just deleting your memory to save RAM, which defeats the entire purpose.

**Pre-loading vs. lazy loading** — tried forcing the models to load at startup instead of query time, hoping Railway would at least OOM at boot (fast fail) rather than mid-conversation (chaos). Instead it just… crashed at boot. Progress, technically.

[SCREENSHOT: QMD OOM error logs — repeated FATAL killed messages across container restarts]

By the end of Day 4, I had a very clean index of a fraction of our actual knowledge base, a container that restarted every few minutes, and a deep personal relationship with the Railway crash logs dashboard.

---

## The Pivot: Three Lines of Config

A friend mentioned that OpenClaw had built-in memory support with OpenAI embeddings. I'd skimmed past this in the docs before because I assumed it was some basic keyword thing. It's not.

OpenClaw's builtin memory uses `text-embedding-3-small` — OpenAI's embedding model. No local model to load. No RAM spike at query time. The embeddings are computed via API and the vector index lives lightweight on disk. The retrieval happens server-side.

The config:

```yaml
memory:
  provider: builtin
  embedding_model: text-embedding-3-small
  index_path: ./memory/index
```

Three lines. That's it.

[SCREENSHOT: Config comparison — QMD setup (dozens of lines, model paths, RAM limits) vs. OpenClaw builtin (3 lines)]

I deployed it. Indexed our 400+ files (again — fourth time, but who's counting). Ran a query. Got results. The container didn't crash. Ran another query. Still up. Left it running overnight. Still there in the morning.

Cost for a month of queries across three agents: under $1. `text-embedding-3-small` is genuinely cheap. We're talking fractions of a cent per query.

Was the retrieval quality as good as full hybrid search with reranking? Honestly — close enough. For our use case, the quality difference wasn't worth 4 days of pain and a memory system that couldn't stay alive.

The best memory architecture is the one that actually runs.

---

## Architecture A1.1: How We Actually Set It Up

Once the foundation worked, we had to figure out the right *shape* for memory across three agents. This is where it got interesting — and where the squad had opinions.

Our initial instinct was centralized: one shared memory vault, all agents read from it, Molty manages writes. Clean. Simple. One source of truth.

[SCREENSHOT: Architecture diagram — initial centralized design with single vault]

Raphael and Leonardo pushed back immediately.

Their concern: a centralized vault creates a bottleneck. If Molty's memory index goes down, or gets slow, or needs maintenance, *all* agents lose memory. For a coordinator agent, maybe that's acceptable risk. For a sales agent mid-conversation with a lead? That's a real problem.

They had a point. So we adapted.

**Architecture A1.1 — what we actually shipped:**

[SCREENSHOT: Architecture A1.1 diagram — distributed memory with shared vault sync]

**Each agent indexes its own memory folder.** Molty has `/memory/molty/`, Raphael has `/memory/raphael/`, Leonardo has `/memory/leonardo/`. Each is independent. An agent can read its own memory without touching anyone else's infrastructure.

**Molty additionally indexes a shared vault.** Because the coordinator *should* have global context. Meeting summaries, cross-agent decisions, company-wide context — that all lives in `/memory/vault/` and only Molty indexes it. This keeps the shared knowledge centralized without making it a dependency for Raphael and Leonardo's core function.

**Leads get a read-only squad mirror via Syncthing.** We use Syncthing to replicate a curated subset of the vault to each lead agent — not everything, just what's relevant cross-functionally. Client profiles that Raphael needs to know about but Leonardo surfaced. Market context that both need. Crucially: it's read-only for the lead agents. They can consume it but can't write back to it directly. If they have something worth adding to the shared vault, it goes through a contribution protocol (a simple markdown file with metadata headers). Molty reviews and indexes it.

This gives us:
- **Isolation:** each agent's memory failures don't cascade
- **Shared context:** Molty sees everything; leads see what they need
- **Clean writes:** no race conditions on shared memory, no agents clobbering each other's entries
- **Auditability:** every vault contribution has an author, type, priority, and date in its header

The squad feedback process was actually valuable here. My first instinct (centralize everything) was architecturally tidy but operationally fragile. The leads were right to push back.

---

## What the Actual Daily Experience Looks Like Now

Molty starts a session. It loads context from its own memory — recent decisions, active projects, pending tasks. It also has the shared vault indexed, so it knows what's happened across the whole operation.

Raphael gets a message about a lead we talked to three weeks ago. It pulls from its own memory — the full conversation history, the lead's profile, what we agreed to follow up on. It also has the squad mirror, so it knows if Molty flagged something relevant about that lead from the coordinator's perspective.

Leonardo is researching a startup. It checks its own memory for previous notes on that company. Finds a note from six weeks ago where we decided their market was too early. That context surfaces automatically. No re-explaining, no "wait, didn't we look at these guys before?"

This is what memory is supposed to feel like. It just works, quietly, in the background, for less than a dollar a month.

---

## What I'd Tell Myself at Day 1

Don't start with the most powerful tool. Start with the one that fits your constraints.

QMD is probably great if you're running on metal with 32GB of RAM. We're not. We're running lean containers on Railway, and "lean" is a feature, not a bug — it keeps costs low and deployment simple. The memory solution had to fit that model, not the other way around.

The obsession with local models is real in the AI infra world, and I get it — data privacy, latency, cost control at scale. But for an early-stage operation running three agents with a few hundred files? The API-based approach is just better. Simpler to operate, costs almost nothing, and you're not babysitting RAM limits at 11pm.

Also: when your squad pushes back on your architecture, listen. They're closer to the failure modes than you are.

---

## The Stack, in Case You Want to Copy It

- **Agents:** 3 containers on Railway (Molty, Raphael, Leonardo)
- **Memory provider:** OpenClaw builtin
- **Embedding model:** `text-embedding-3-small` (OpenAI)
- **Sync layer:** Syncthing (shared vault → read-only lead mirrors)
- **Monthly memory cost:** ~$0.50-0.80 across all three agents
- **Days wasted on QMD:** 4
- **Days to set up OpenClaw memory:** 0.5

If you're building agent memory and you're on constrained infrastructure, start here. Not with the local vector database that needs a GPU's worth of RAM to answer a question.

---

*We're documenting everything we build and break. If you found this useful, or if you tried something different that worked better — I want to hear about it.*
