# ClawVault Analysis — "Solving Memory for OpenClaw & General Agents"

**Source:** https://x.com/sillydarket/status/2022394007448429004
**Author:** @sillydarket (Pedro, Versatly)
**Date:** Feb 13, 2026
**Engagement:** 733 likes, 48 replies

## Core Claims
1. Plain markdown files outperform specialized memory tools (Mem0, Zep, vector DBs) on LoCoMo benchmark
2. LLMs already know how to work with files — fighting that with specialized APIs is "swimming upstream"
3. Agent memory and human knowledge management are the same problem
4. Obsidian's "notes are just files" philosophy is the key insight

## Architecture
- **Storage:** Markdown files with YAML frontmatter (typed: decision, preference, relationship, commitment, lesson)
- **Linking:** Wiki-links `[[entity-name]]` across notes → knowledge graph (like Obsidian graph view)
- **Retrieval:** Vault index (single file listing all notes with one-liners) + optional embedding search
- **Compression:** LLM-based observation compression with priority tags (P1 critical, P2 important, P3 routine)
- **Context loading:** Budget-aware — P1 first, then P2, then P3 until context window full
- **Zero cloud:** All local filesystem, no network calls except optional LLM for compression

## What TMNT Already Does Well
- MEMORY.md + daily logs + memory/refs/ = markdown-first approach ✅
- QMD = BM25 + vector search (better than just vault index) ✅
- Multi-agent sync via Syncthing (ClawVault doesn't address multi-agent) ✅
- Cron-based compaction + guardrails (file size caps, archival) ✅
- Lessons section in MEMORY.md = informal memory typing ✅

## What We Could Adopt
1. **Memory typing with YAML frontmatter** — Tag memories as decision/preference/relationship/commitment/lesson
2. **Wiki-links** — `[[entity-name]]` cross-referencing across files for navigable context
3. **Vault index** — Single file listing all memory files with one-line descriptions (faster than search for most queries)
4. **Priority-tagged observations** — P1/P2/P3 during daily compaction, load P1 first on wake
5. **Budget-aware context injection** — Most important memories always make it into context window

## Key Quote
"When your agent's memory vault IS an Obsidian vault, something remarkable happens: you can see what your agent knows."

## npm Package
`npm install clawvault` — open source, GitHub repo available
