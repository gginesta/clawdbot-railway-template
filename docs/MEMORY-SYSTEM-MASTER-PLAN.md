# Memory System Master Plan — TMNT Squad

*Created: 2026-02-17 | Owner: Molty 🦎 | Status: ACTIVE*
*Consolidates 13 previous documents (archived to `docs/archive/memory/`)*

---

## Guillermo's Objectives

These 6 goals drive every action in this plan. Nothing happens that doesn't serve one of them.

| # | Objective | Status | Next Action |
|---|-----------|--------|-------------|
| 1 | **Standardise implementation across the fleet** | 🔴 Not done | Migrate Raphael from OpenAI embeddings → QMD backend |
| 2 | **One embedding provider across the board** | 🔴 Not done | Decision needed: OpenAI API vs local embeddinggemma |
| 3 | **Complete indexing for all 3 agents, feeding to Molty's central memory** | 🟡 Partial | Molty indexed (247 files). Leonardo/Raphael not feeding centrally. |
| 4 | **Consistent embedding index** | 🔴 Not done | Blocked by #2 (provider decision) |
| 5 | **Full QMD re-indexing** | 🟢 Molty done | Molty: 6765 vectors, 0 pending. Leonardo/Raphael: TBD |
| 6 | **Clean up unused collections + trim session bloat** | 🟡 Partial | `memory-alt` empty. 196 sessions (36.3MB). No trim policy. |

---

## Current State (Verified 2026-02-17 12:15 HKT)

### Per-Agent Status

| Agent | Backend | Embedding Model | Files Indexed | Vectors | Central Feed |
|-------|---------|----------------|---------------|---------|-------------|
| **Molty 🦎** | QMD (local) | embeddinggemma-300M (GGUF) | 247 | 6765 | N/A (is central) |
| **Leonardo 🔵** | QMD (local) | embeddinggemma-300M (GGUF) | Unknown | Unknown | ❌ No |
| **Raphael 🔴** | OpenAI API | text-embedding-3-small | Unknown | Unknown | ❌ No |

### Molty's QMD (Managed by OpenClaw)
- **Index:** `/data/.openclaw/agents/main/qmd/xdg-cache/qmd/index.sqlite` (36.3 MB)
- **Collections:** `memory-root` (1 file), `memory-dir` (50 files), `sessions` (196 files), `memory-alt` (0 — unused)
- **Auto-update:** Every 5min + on boot
- **XDG paths:** Must set `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` to access from CLI
- **GPU:** None (CPU only, 48 cores). Functional but slow for embedding.

### Shared Infrastructure
- **Syncthing:** All agents + Guillermo-PC connected. Shared folders sync automatically.
- **Memory Vault:** `/data/shared/memory-vault/` — 308 sources catalogued, git-backed
- **Central Index:** `/data/shared/memory-vault/central_index/` — directory structure exists but not wired to QMD

---

## Provider Decision (Objective #2)

Must decide before executing anything else. Two options:

### Option A: OpenAI `text-embedding-3-small` (via API)
- **Pros:** Fast, high quality, OpenClaw's recommended default, works without local binary
- **Cons:** API cost per search (~$0.0001/1K tokens), requires OpenAI key on each agent
- **Config:** `agents.defaults.memorySearch` with `provider: "openai"`

### Option B: Local QMD with `embeddinggemma-300M` (current Molty/Leonardo setup)
- **Pros:** Free, local, includes BM25 + vector + reranking hybrid search, session transcript indexing
- **Cons:** CPU-only on Railway (slow embedding), requires QMD binary installed, more complex
- **Config:** `memory.backend: "qmd"` with local GGUF models

### Option C: QMD backend with OpenAI embeddings (hybrid)
- **Pros:** QMD's hybrid search + session indexing + high-quality OpenAI embeddings
- **Cons:** Need to verify if QMD supports remote embedding providers
- **Config:** Would need investigation

**My recommendation:** Option B (local QMD) for all agents. It's already working on 2/3 agents, gives us session transcript search that OpenAI-only can't do, and costs nothing. The CPU slowness only affects initial embedding — search is fast.

**Awaiting Guillermo's decision.**

---

## Execution Plan

### Phase 1: Standardise (Objectives #1, #2, #4)
*Prerequisite: Provider decision from Guillermo*

**Step 1.1 — Verify Leonardo's QMD status**
- [ ] Send webhook to Leonardo: report `qmd status` with XDG paths
- [ ] Confirm: binary version, collections, vector count, embedding model
- Expected: Same as Molty (embeddinggemma, QMD backend)

**Step 1.2 — Migrate Raphael to QMD backend**
- [ ] Verify QMD binary exists on Raphael (`which qmd`, `qmd --version`)
- [ ] If missing: `bun install -g @tobilu/qmd` on Raphael's container
- [ ] Patch Raphael's config: add `memory.backend: "qmd"` section (mirror Molty's)
- [ ] Remove or keep `memorySearch` as fallback
- [ ] Restart Raphael's gateway
- [ ] Verify: `qmd status` shows collections being created, `memory_search` returns results
- **Risk:** Gateway restart = brief downtime. Raphael's existing OpenAI search stops during migration.
- **Rollback:** Remove `memory.backend` config → reverts to OpenAI embeddings

**Step 1.3 — Confirm consistent embedding model**
- [ ] All 3 agents report same embedding model from `qmd status`
- [ ] Document in this file

### Phase 2: Complete Indexing + Central Feed (Objective #3)
*After Phase 1 is complete*

**Step 2.1 — Define what "central memory" means**
Options:
- **A) Shared Syncthing folder** — All agents write summaries to `/data/shared/memory-vault/` which Molty indexes
- **B) Webhook reports** — Agents send weekly memory digests to Molty via webhook
- **C) QMD reads shared folders** — Add `/data/shared/` as a QMD collection on Molty

My recommendation: **Option C** — simplest. Molty adds a QMD collection pointing to the shared vault. Other agents write their key decisions/lessons to shared folders via Syncthing. No webhooks needed.

- [ ] Add QMD collection on Molty: `qmd collection add /data/shared/memory-vault --name shared-vault --mask "*.md"`
- [ ] Define what each agent writes to shared vault (format, frequency)
- [ ] Create agent instructions for writing to shared vault
- [ ] Test: Raphael writes a file → Syncthing syncs → Molty's QMD indexes → `memory_search` finds it

**Step 2.2 — Verify all agent workspaces indexed**
- [ ] Leonardo: confirm collections cover `memory/`, workspace `.md` files
- [ ] Raphael: confirm same (after Phase 1 migration)
- [ ] Molty: already verified ✅

### Phase 3: Full Re-index + Cleanup (Objectives #5, #6)

**Step 3.1 — Full QMD re-index on all agents**
- [ ] Molty: `qmd update && qmd embed` (with XDG vars) — verify 0 pending
- [ ] Leonardo: same via webhook instruction
- [ ] Raphael: same (after Phase 1)

**Step 3.2 — Remove unused collections**
- [ ] Molty: remove `memory-alt` collection (0 files, never used)
- [ ] Remove my manually-created collections at default path (`/root/.cache/qmd/index.sqlite`) — these are orphaned from earlier today

**Step 3.3 — Session trim policy**
- [ ] Decide retention: current = 30 days. Is this right?
- [ ] Check disk usage: 196 sessions in 36.3MB index — manageable but growing
- [ ] Consider: reduce to 14 days? Or keep 30?
- [ ] Implement: update `memory.qmd.sessions.retentionDays` in config if changing

**Step 3.4 — Archive old memory files**
- [ ] Move memory logs older than 3 months to `memory/archive/`
- [ ] Verify QMD still indexes archived files (check collection path patterns)

### Phase 4: Quality Improvements (Nice-to-Have, Post-Core)

These come from the ClawVault analysis. Only pursue after Phases 1-3 are complete.

- [ ] Add `<!-- type: decision | priority: P1 -->` tags to new daily log entries
- [ ] Create `memory/INDEX.md` — auto-generated vault table of contents
- [ ] Start using `[[wiki-links]]` for entity cross-references
- [ ] Priority-aware compaction (P1 items never compressed)

---

## Files Archived

The following docs are superseded by this master plan and moved to `docs/archive/memory/`:

1. `docs/CLAWVAULT-INCORPORATION-PLAN.md` — Sub-agent output, useful patterns extracted above
2. `docs/CLAWVAULT-MEMORY-UPGRADE-PLAN.md` — Sub-agent output, useful patterns extracted above
3. `docs/QMD-MEMORY-AUDIT-20260217.md` — Today's audit, findings incorporated
4. `docs/qmd-standardization-plan.md` — Feb 16, superseded
5. `docs/qmd_indexing_strategy.md` — Feb 16, superseded
6. `docs/qmd_migration_20260216_report.md` — Feb 16, superseded
7. `docs/qmd_migration_report_template.md` — Feb 16, unused template
8. `docs/qmd_standardization_master_log.md` — Feb 16, superseded
9. `research/memory-vault-plan.md` — Feb 1 v1, superseded
10. `research/memory-vault-plan-v2.md` — Feb 1 v2, superseded
11. `research/memory-vault-plan-v3.md` — Feb 1 v3, superseded
12. `memory/refs/qmd-migration-strategy-20260216.md` — Feb 16, superseded
13. `memory/refs/qmd-status-20260217.md` — Today, findings incorporated

---

*This is the single source of truth for the memory system project. All updates go here.*
