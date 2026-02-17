# Shared Memory Vault — Index

*Auto-generated. Last updated: 2026-02-17*

## Purpose
Central shared memory for the TMNT squad. All agents contribute via Syncthing.
Molty 🦎 indexes everything here as the central architect.

## Structure

### `/decisions/` — Cross-agent decisions
Tagged, dated. Append-only per agent.

### `/lessons/` — Shared lessons learned
Hard-won knowledge that applies across the fleet.

### `/people/` — People dossiers
One file per person. Shared across agents.

### `/projects/` — Active project state
Project summaries and status.

### `/knowledge/` — Reference knowledge
- `squad/` — Squad-wide docs, protocols, standards
- `infrastructure/` — Technical docs, delivery config, model compatibility
- `areas/`, `resources/`, `archives/`, `people/`, `projects/`

### `/daily/` — Shared daily logs
Cross-agent daily summaries.

### `/ai-history/` — AI conversation exports
ChatGPT, Claude, Grok conversation extracts.

### `/tacit/` — Preferences and implicit knowledge
User preferences, working styles.

## Contribution Rules
1. Only P1 and P2 items get promoted here
2. Each agent appends, never overwrites another agent's entries
3. File naming: `YYYY-MM-DD-<slug>.md` for decisions/lessons
4. Tag entries: `<!-- agent: molty | type: decision | priority: P1 | date: YYYY-MM-DD -->`
