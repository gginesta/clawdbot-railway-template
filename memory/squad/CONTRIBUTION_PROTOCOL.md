# Shared Memory Vault — Contribution Protocol

*Version: 1.0 | Created: 2026-02-17 | Owner: Molty 🦎*

---

## Purpose

This vault is the **central knowledge base** for the TMNT squad. All agents contribute high-value items here. Molty indexes everything via OpenAI's builtin memory search and serves as the central memory architect.

**Syncthing keeps all copies in sync automatically.** Write a file → it appears on all agents within seconds.

---

## Who Can Write

| Agent | Write Access | Scope |
|-------|-------------|-------|
| Molty 🦎 | Full | All directories |
| Raphael 🔴 | Append-only | decisions/, lessons/, people/, projects/ |
| Leonardo 🔵 | Append-only | decisions/, lessons/, people/, projects/ |
| Donatello 🟣 | Append-only | decisions/, lessons/, people/, projects/ |
| Guillermo | Full | All directories (via Obsidian on PC) |

---

## What Goes Here (and What Doesn't)

### ✅ DO contribute:
- **P1 decisions** — choices that affect multiple agents or the whole fleet
- **P2 decisions** — significant choices within your domain
- **Lessons learned** — hard-won knowledge others should know
- **People dossiers** — contact info, working relationship notes, context
- **Project status** — active project summaries (one file per project)
- **Cross-agent knowledge** — anything another agent might need to search for

### ❌ DON'T contribute:
- P3/routine items — keep in your own workspace
- Raw daily logs — those stay in `memory/YYYY-MM-DD.md` locally
- Temporary task lists — use Todoist
- Duplicate info already in another agent's workspace

---

## Directory Structure

```
/data/shared/memory-vault/
├── decisions/          # Cross-agent decisions (dated)
├── lessons/            # Shared lessons learned
├── people/             # People dossiers (one file per person)
├── projects/           # Active project state
├── knowledge/          # Reference knowledge
│   ├── squad/          # Squad-wide docs, protocols
│   ├── infrastructure/ # Technical docs
│   ├── areas/          # PARA areas
│   ├── people/         # (legacy — use top-level people/ for new)
│   └── projects/       # (legacy — use top-level projects/ for new)
├── daily/              # Cross-agent daily summaries
├── ai-history/         # AI conversation exports (read-only)
└── tacit/              # Preferences, implicit knowledge
```

---

## File Naming Convention

| Directory | Pattern | Example |
|-----------|---------|---------|
| `decisions/` | `YYYY-MM-DD-<slug>.md` | `2026-02-17-openai-memory-switch.md` |
| `lessons/` | `YYYY-MM-DD-<slug>.md` | `2026-02-17-dockerfile-persistence.md` |
| `people/` | `<full-name>.md` | `pedro-versatly.md` |
| `projects/` | `<project-name>.md` | `cerebro.md` |

---

## Entry Format

Every entry must include a metadata header:

```markdown
<!-- agent: raphael | type: decision | priority: P1 | date: 2026-02-17 -->
# Title of the entry

Brief description of what happened and why it matters.

## Context
What led to this decision/lesson.

## Outcome
What was decided/learned.

## Impact
Who/what is affected.
```

### Metadata Fields

| Field | Required | Values |
|-------|----------|--------|
| `agent` | Yes | `molty`, `raphael`, `leonardo`, `donatello` |
| `type` | Yes | `decision`, `lesson`, `person`, `project`, `reference` |
| `priority` | Yes | `P1` (fleet-wide), `P2` (domain-significant) |
| `date` | Yes | `YYYY-MM-DD` |

---

## Rules

1. **Append, never overwrite** another agent's entries
2. **One concept per file** — don't dump multiple decisions in one file
3. **People files are shared** — any agent can add sections (clearly tagged with your agent name)
4. **Keep it concise** — full text is indexed automatically, so searchability is free. Write for humans.
5. **No secrets** — API keys, tokens, passwords go in agent config, NEVER in shared vault
6. **Conflicts** — if Syncthing reports a conflict, Molty arbitrates

---

## How Indexing Works

1. Agent writes file to shared vault (`/data/shared/memory-vault/`)
2. Syncthing syncs to Molty's `memory/vault/` directory
3. OpenClaw's builtin indexer picks it up automatically
4. Molty can search it via `memory_search`
5. Other agents search only their own workspace + `memory/squad/` (shared standards)

---

## Promoting from Daily Logs

When your daily log compaction identifies a P1/P2 item:

1. Tag it in your daily log: `<!-- scope: shared -->`
2. Create the corresponding file in the shared vault
3. Reference it: `See shared vault: decisions/YYYY-MM-DD-<slug>.md`

This can be automated later via compaction cron (Phase 4).
