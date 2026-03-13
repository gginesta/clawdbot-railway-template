# Research: discrawl — Discord-to-SQLite Archiver

**Date:** 2026-03-14
**Requested by:** Guillermo (Todoist task 6g8VV24G2v9m8cCx)
**Author:** Molty 🦎
**Source:** https://github.com/steipete/discrawl

---

## What It Is

`discrawl` is a CLI (Go) from steipete that mirrors Discord guild data into a local SQLite database with FTS5 search indexes. It uses a **real bot token** (not user token), making it safe and API-compliant.

**504 stars** | Language: Go | Last updated: 2026-03-13 (very active)

---

## Key Capabilities

| Feature | Detail |
|---------|--------|
| **Mirror** | Channels, threads, members, messages → SQLite |
| **FTS5 search** | Fast full-text search over archived messages locally |
| **Live tail** | Gateway event stream for real-time updates |
| **SQL access** | Direct read-only SQL queries against the DB |
| **Embeddings** | Optional OpenAI embeddings for semantic search |
| **Multi-guild** | Handles multiple guilds in one DB |
| **Attachment text** | Indexes text content from small attachments |
| **Mention tracking** | Structured user/role mention records |

---

## What It Solves for Us

### Problem 1: Agents can't search Discord history
Currently, agents can only read recent messages via the message tool. Discrawl would give **all agents SQL-level access to the full Discord history** without burning API calls.

### Problem 2: Cross-session context loss
Discrawl's local SQLite means agents could search "what did Guillermo say about X last month" instantly — not just last 20 messages.

### Problem 3: Bot-to-bot message visibility
If agents use discrawl to sync Discord, they get a **local copy** of all messages including bot messages — bypassing the `allowBots` problem entirely for historical reads. (Note: for real-time, we still need `allowBots: true`.)

---

## Integration Paths

### Path A: Molty-only archive (simplest)
- Install discrawl on Molty's Railway instance
- `discrawl init --from-openclaw ~/.openclaw/openclaw.json`
- Run `discrawl sync --full` once, then `discrawl tail` in background
- DB stored at `/data/workspace/state/discrawl.db`
- Add search wrapper to Molty's toolkit

**Pros:** Zero bot setup needed (reuses OpenClaw bot token), immediate value
**Cons:** Only Molty gets search; no live queries for other agents

### Path B: Shared discrawl DB on /data/shared (best)
- Install discrawl on Molty  
- Point DB to `/data/shared/discrawl/discrawl.db`
- Syncthing syncs it to all agents
- Each agent gets a read-only local copy for SQL queries

**Pros:** All agents get Discord search; works offline
**Cons:** DB size (could be large for full history); sync lag

### Path C: Discrawl as Railway service (most scalable)
- Dedicated Railway service running `discrawl tail`
- Exposes a search API (not in discrawl itself, but could wrap it)
- All agents query via HTTP

**Pros:** Centralized, always up-to-date
**Cons:** More infra overhead; discrawl doesn't have an HTTP server built in

---

## Installation (Path A — Recommended Start)

```bash
# On Molty (Railway)
git clone https://github.com/steipete/discrawl.git /data/workspace/tools/discrawl
cd /data/workspace/tools/discrawl
go build -o bin/discrawl ./cmd/discrawl

# Init from OpenClaw config
./bin/discrawl init --from-openclaw ~/.openclaw/openclaw.json --db /data/workspace/state/discrawl.db

# Run doctor
./bin/discrawl doctor

# Full sync (first time — could be slow)
./bin/discrawl sync --full

# Tail for live updates
./bin/discrawl tail &
```

---

## Recommendation

**Start with Path A** (Molty-only, reusing OpenClaw token). It's a 30-minute install that gives immediate Discord search capability with zero new bot setup. If it proves useful, promote to shared DB (Path B).

**Immediate use case:** Morning briefing could search Discord for "overnight mentions of Brinc deals" or "recent Cerebro updates" from Raphael/Leonardo before generating the brief.

**One concern:** Railway doesn't have Go installed by default. Would need to either:
1. Build binary locally and commit to repo, or
2. Add Go install to Molty's Railway build step

---

## Verdict

High value tool. Addresses our #1 agent limitation (Discord search depth). steipete is the OpenClaw author — this is first-party tooling, well-maintained, and designed to work alongside OpenClaw.

**Recommendation:** Install on Molty's Railway instance in next maintenance window. Flag for Guillermo to decide on scope (Molty-only vs shared).

