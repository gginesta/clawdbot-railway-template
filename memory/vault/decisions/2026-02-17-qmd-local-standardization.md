<!-- agent: molty | type: decision | priority: P1 | date: 2026-02-17 -->
# Standardise on Local QMD for All Agents

## Context
Needed to choose between OpenAI embeddings (API), local QMD with embeddinggemma-300M, or hybrid approach for the TMNT squad's memory system.

## Decision
**Option B: Local QMD with embeddinggemma-300M (GGUF)** for all agents.

Approved by Guillermo 2026-02-17 15:16 HKT.

## Rationale
- OpenClaw's development direction (QMD getting shared model cache in PR #12114)
- Session transcript search only available via QMD
- Hybrid BM25 + vector + reranking search
- Zero marginal cost (no API fees per search)
- Best fit for central architect pattern (Molty indexes shared vault)
- CPU-only on Railway is slow for initial embedding but fast for search

## Impact
- All 3 active agents (Molty, Raphael, Leonardo) must have QMD installed
- Dockerfile updated to include bun + QMD in runtime stage (commit `3962a31`)
- New agents inherit this setup automatically
- Fallback: Option C (QMD + OpenAI embeddings) if local models can't initialize on resource-constrained containers

## Status
- Molty: ✅ 539 files, 6862+ vectors
- Leonardo: ✅ 405 files, 2683 vectors
- Raphael: 🔄 Dockerfile fix deployed, awaiting verification
