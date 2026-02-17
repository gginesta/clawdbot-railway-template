# QMD Status — Molty — 2026-02-17

## Current State: ✅ WORKING
- **Binary:** `/usr/local/bin/qmd` → `/root/.bun/bin/qmd` (v1.0.6)
- **Collections:** 3 (workspace: 15 files, memory: 13 files, vault: 1 file) — 29 docs total
- **Embeddings:** 65 chunks embedded (embeddinggemma, CPU, 19s)
- **Search:** BM25 ✅ | Vector search ✅ | Query (reranker downloading, ~1.3GB one-time)
- **GPU:** None (CPU only — cmake missing, CUDA build fails). Functional but slow for large reranking.
- **Auto-update:** Every 5min + on boot (config: `memory.qmd.update`)

## Collections
| Name | Path | Files |
|------|------|-------|
| workspace | /data/workspace | 15 |
| memory | /data/workspace/memory | 13 |
| vault | /data/shared/memory-vault | 1 |

## What Was Done (Feb 17)
1. Binary was restored by OpenClaw 2026.2.16 update (symlink at 11:48 HKT)
2. Added 3 collections, indexed 29 docs
3. Ran `qmd embed` — 65 chunks in 19s on CPU
4. Verified BM25 search works, vector search works

## Remaining from Migration Plan
- Phase 2 (cross-agent sync) and Phase 3 (validation) from yesterday's plan not started
- Reranker model still downloading (~1.3GB) for `qmd query` command
- Consider adding cmake to Dockerfile for GPU acceleration on future deploys
