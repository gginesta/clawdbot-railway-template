---
name: cartographer
description: Map and document any codebase into a CODEBASE_MAP.md. Analyzes architecture, file purposes, dependencies, data flows, and navigation guides. Use when onboarding to a new repo or before major refactors.
version: 1.0.0
author: Molty 🦎 (TMNT Squad)
credits: Inspired by kingbootoshi/cartographer. Rebuilt as native OpenClaw skill.
---

# Cartographer — Codebase Mapping Skill

Generate a comprehensive `CODEBASE_MAP.md` for any codebase.

## When to Use
- Onboarding to a new repository
- Before major refactors or architecture changes
- Giving context to sub-agents before coding tasks
- Understanding unfamiliar codebases quickly

## How It Works

1. **Scan** — Walk the file tree, count files/lines per directory, identify key config files
2. **Split** — Divide the codebase into logical modules (frontend, backend, infra, docs)
3. **Analyze** — Spawn sub-agents in parallel, each analyzing one module
4. **Synthesize** — Merge all module reports into a single `CODEBASE_MAP.md`

## Output Format

The generated `CODEBASE_MAP.md` contains:

```markdown
# Codebase Map — {project}

## Overview
One-paragraph summary of what this project is and does.

## Tech Stack
Languages, frameworks, databases, key dependencies.

## Architecture
High-level diagram (text-based) of how components connect.

## Module Breakdown
For each major directory/module:
- **Purpose** — What it does
- **Key Files** — Most important files and what they contain
- **Dependencies** — What it imports/uses
- **Data Flow** — How data moves through this module
- **Gotchas** — Non-obvious things a new developer should know

## API Surface
Key endpoints, routes, or exported interfaces.

## Database Schema
Tables/collections and their relationships (if applicable).

## Navigation Guide
"If you want to do X, look at Y" — quick reference for common tasks.
```

## Usage

Just say: "Map the Cerebro codebase" or "Run cartographer on /path/to/repo"

The skill will handle scanning, splitting, parallel analysis, and synthesis automatically.

## Cost Note
Spawns sub-agents (default: Haiku for cost efficiency). A typical 500-file codebase uses ~50K tokens total (~$0.50 with Haiku).
