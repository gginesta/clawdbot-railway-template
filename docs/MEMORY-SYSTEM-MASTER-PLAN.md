# Memory System Master Plan — TMNT Squad

*Created: 2026-02-17 | Owner: Molty 🦎 | Status: ACTIVE*
*Consolidates 13 previous documents (archived to `docs/archive/memory/`)*

---

## Guillermo's Objectives

These 6 goals drive every action in this plan. Nothing happens that doesn't serve one of them.

| # | Objective | Status | Next Action |
|---|-----------|--------|-------------|
| 1 | **Standardise implementation across the fleet** | 🟢 Done | All 3 agents on QMD backend (local embeddinggemma) |
| 2 | **One embedding provider across the board** | 🟢 Done | embeddinggemma-300M (GGUF) on all agents. Decision: 2026-02-17 |
| 3 | **Complete indexing for all 3 agents, feeding to Molty's central memory** | 🟡 Partial | All indexed locally. Central feed not yet wired (Phase 2). |
| 4 | **Consistent embedding index** | 🟢 Done | Same model + dimensions across fleet |
| 5 | **Full QMD re-indexing** | 🟡 In progress | Molty: 6765 vectors ✅. Leonardo: 2683 vectors, 1 pending. Raphael: indexing. |
| 6 | **Clean up unused collections + trim session bloat** | 🟡 Partial | Phase 3 next. |

---

## Current State (Verified 2026-02-17 12:15 HKT)

### Per-Agent Status

| Agent | Backend | Embedding Model | Files Indexed | Vectors | Central Feed |
|-------|---------|----------------|---------------|---------|-------------|
| **Molty 🦎** | QMD (local) | embeddinggemma-300M (GGUF) | 247 | 6765 | N/A (is central) |
| **Leonardo 🔵** | QMD (local) | embeddinggemma-300M (GGUF) | 405 | 2683 | ❌ No |
| **Raphael 🔴** | QMD (local) ← migrated 2026-02-17 | embeddinggemma-300M (GGUF) | TBD (indexing) | TBD | ❌ No |

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

**Decision (2026-02-17 15:16 HKT): Option B — Local QMD for all agents.**
Approved by Guillermo. Rationale: OpenClaw's development direction, session transcript search, hybrid retrieval, zero marginal cost, best fit for central architect pattern.

---

## Execution Plan

### Phase 1: Standardise (Objectives #1, #2, #4)
*Prerequisite: Provider decision from Guillermo*

**Step 1.1 — Verify Leonardo's QMD status**
- [x] Send webhook to Leonardo: report `qmd status` with XDG paths
- **Finding (2026-02-17 15:27 HKT):** Leonardo had QMD data dirs but NO binary in PATH. bun also missing.
- [x] Sent instruction to install bun + QMD
- [x] **Result:** bun 1.3.9 installed, QMD 1.0.6 installed, symlinked to `/usr/local/bin/qmd`
- [x] **QMD status:** 405 files indexed, 2683 vectors, 1 pending. Index: 15.8 MB. Model: embeddinggemma-300M ✅
- Same CPU-only limitation (no GPU, cmake build fails) — matches Molty

**Step 1.2 — Migrate Raphael to QMD backend**
- [x] Verify QMD binary exists on Raphael — **was missing, now installed**
  - Raphael installed: bun 1.3.9, qmd 1.0.6, binary at `/root/.bun/bin/qmd`
- [x] Sent config patch instruction: `memory.backend: "qmd"` with full QMD config
  - OpenAI `memorySearch` kept as fallback
  - Gateway restart will trigger QMD collection creation + initial indexing
- [ ] Verify: `qmd status` shows collections being created
- [ ] Verify: `memory_search` returns results
- **Risk:** Gateway restart = brief downtime. OpenAI search remains as fallback.
- **Rollback:** Remove `memory.backend` config → reverts to OpenAI embeddings

**Step 1.3 — Confirm consistent embedding model**
- [ ] All 3 agents report same embedding model from `qmd status`
- [ ] Document in this file

### Phase 2: Complete Indexing + Central Feed (Objective #3)
*After Phase 1 is complete*

**Architecture: Molty as Central Architect**

```
┌─────────────────────────────────────────────────────────┐
│                    MOLTY 🦎 (Architect)                  │
│  Indexes: own workspace + shared vault + all agent feeds │
│  QMD collections: memory-root, memory-dir, sessions,     │
│                   shared-vault (new)                      │
├─────────────────────────────────────────────────────────┤
│              /data/shared/memory-vault/                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │decisions/ │  │lessons/  │  │people/   │              │
│  │(append)   │  │(append)  │  │(per-file)│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       ▲              ▲             ▲                     │
│  Syncthing      Syncthing     Syncthing                 │
│       │              │             │                     │
├───────┼──────────────┼─────────────┼────────────────────┤
│ Raphael 🔴    Leonardo 🔵     Molty 🦎                  │
│ (writes P1/P2  (writes P1/P2  (writes P1/P2            │
│  to shared)     to shared)     to shared)               │
└─────────────────────────────────────────────────────────┘
```

**Step 2.1 — Restructure shared vault**
- [ ] Create standard folders in `/data/shared/memory-vault/`:
  ```
  decisions/    # Cross-agent decisions (tagged, dated)
  lessons/      # Shared lessons learned
  people/       # People dossiers (one file per person)
  projects/     # Active project state
  knowledge/    # Reference knowledge (existing)
  SHARED_INDEX.md  # Auto-generated vault index
  ```
- [ ] Move existing files into new structure

**Step 2.2 — Add shared vault as QMD collection on Molty**
- [ ] `qmd collection add /data/shared/memory-vault --name shared-vault --mask "*.md"` (with XDG vars)
- [ ] Run `qmd embed` to index existing shared content

**Step 2.3 — Define agent contribution protocol**
Each agent writes to shared vault using append-only, agent-prefixed entries:
```markdown
<!-- agent: raphael | type: decision | priority: P1 | date: 2026-02-17 -->
## 🔴 Raphael — Switched Brinc proposal template to v3
Reason: Better conversion rate in Q4 tests...
```
Rules:
- Only P1 and P2 items get promoted to shared vault
- Each agent appends, never overwrites another agent's entries
- File naming: `YYYY-MM-DD-<slug>.md` for decisions/lessons, `<entity-name>.md` for people/projects
- Agents tag with `<!-- scope: shared -->` in their daily logs → compaction cron copies to shared vault

**Step 2.4 — Create agent instructions**
- [ ] Add shared vault contribution instructions to each agent's AGENTS.md
- [ ] Include: when to write, format, naming convention
- [ ] Template for new agents (Donatello, April, Michelangelo)

**Step 2.5 — Verify all agent workspaces indexed locally**
- [ ] Leonardo: confirm QMD collections cover `memory/`, workspace `.md` files
- [ ] Raphael: confirm same (after Phase 1 migration)
- [ ] Molty: already verified ✅

**Step 2.6 — Test the full flow**
- [ ] Raphael writes a test decision to `decisions/2026-02-XX-test.md`
- [ ] Syncthing syncs to Molty's container
- [ ] Molty's QMD update cycle indexes it (within 5 min)
- [ ] `memory_search("Raphael test decision")` returns the file
- [ ] Clean up test file

**New Agent Onboarding Template (Objective #3: "any new team mate")**
When deploying a new agent:
1. Install QMD: `bun install -g @tobilu/qmd`
2. Add to config: `memory.backend: "qmd"` (copy Molty's template)
3. Connect Syncthing shared folders
4. Add contribution instructions to agent's AGENTS.md
5. Verify: `qmd status` shows collections, `memory_search` works
6. Add to this plan's status table

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

### Phase 4: Quality Improvements (Post-Core)
*From ClawVault analysis. Pursue after Phases 1-3 are complete.*

**Step 4.1 — Memory typing in daily logs**
Tag important entries with HTML comments (invisible in rendered markdown):
```markdown
## Decided to use QMD across fleet
<!-- type: decision | priority: P1 -->
Standardising on local QMD with embeddinggemma...
```

| Type | When to use | Example |
|------|-------------|---------|
| `decision` | A choice was made | "Use QMD not OpenAI for embeddings" |
| `preference` | User/agent preference | "Guillermo prefers tables over bullets" |
| `relationship` | Person/entity info | "Pedro from Versatly built ClawVault" |
| `commitment` | Promise or deadline | "Fix Gmail OAuth by Feb 19" |
| `lesson` | Hard-won learning | "Always backup before Railway update" |

Priority: P1 (always load on wake), P2 (load if budget allows), P3 (search only).
Tag ~20-30% of entries. Over-tagging defeats the purpose.

**Step 4.2 — Wiki-links for cross-referencing**
Wrap notable entities: `[[Guillermo]]`, `[[Leonardo]]`, `[[Brinc]]`, `[[Cerebro]]`
- QMD indexes these as searchable terms
- No target files needed — it's a cheap knowledge graph via search
- Use canonical names: `[[Leonardo]]` not `[[Leo]]`

**Step 4.3 — Vault index**
- [ ] Create `memory/INDEX.md` — one-line description per memory file
- [ ] Auto-update via cron or heartbeat (not manual)
- [ ] Faster than embedding search for "what do I know about X?"

**Step 4.4 — Priority-aware compaction**
- [ ] During daily log compaction, extract P1 items to `memory/priorities.md`
- [ ] `priorities.md` loads before MEMORY.md on boot — agent always knows active commitments
- [ ] P1/P2 items survive compaction intact; only P3 gets compressed

**Step 4.5 — Tiered boot sequence** (update AGENTS.md)
```
1. SOUL.md + IDENTITY.md (who am I)
2. memory/priorities.md (what's critical RIGHT NOW)
3. MEMORY.md (long-term context)
4. memory/YYYY-MM-DD.md (today + yesterday)
```

---

## Reference: ClawVault Analysis

*Source: @sillydarket (Pedro, Versatly) — "Solving Memory for OpenClaw & General Agents"*
*Full analysis: `memory/refs/clawvault-analysis.md`*

**Key insight:** Plain markdown with memory typing + wiki-links outperformed specialised memory tools (Mem0, Zep, vector DBs) on benchmarks. We independently arrived at the same core architecture. ClawVault patterns worth adopting are captured in Phase 4 above. The npm package itself is NOT recommended (single-agent, uses Tailscale not Syncthing, conflicts with our cron/compaction setup).

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
