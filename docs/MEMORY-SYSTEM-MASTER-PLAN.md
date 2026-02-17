# Memory System Master Plan — TMNT Squad

*Created: 2026-02-17 | Owner: Molty 🦎 | Status: ACTIVE*
*Major revision: 2026-02-17 20:55 HKT — Switched from QMD to Option A1 (OpenAI + Architect Pattern)*

---

## Guillermo's 6 Objectives

| # | Objective | Status | How A1 Achieves It |
|---|-----------|--------|-------------------|
| 1 | **Standardise across fleet** | 🔄 Executing | Same OpenAI config on all agents (3 lines) |
| 2 | **One provider** | 🔄 Executing | OpenAI `text-embedding-3-small` everywhere |
| 3 | **Complete indexing → Molty as central architect** | 🔄 Executing | Only Molty indexes the shared vault (under `memory/vault/`). Other agents can write to it but don't search it. |
| 4 | **Consistent embedding index** | 🔄 Executing | Same OpenAI model/dimensions on all agents |
| 5 | **Full re-indexing** | ⏳ Pending | OpenClaw auto-reindexes when config changes. One-step. |
| 6 | **Cleanup** | ⏳ Pending | Remove QMD config, orphaned indexes, unused files |

---

## Architecture Decision

### What we tried and why we moved on

**Local QMD (Feb 17 morning):** Installed QMD with embeddinggemma-300M on all agents. Embedding worked, but `qmd query` (hybrid search) loads a 0.6B reranker + 1.7B query-expansion model — total ~6GB RAM. Railway containers OOM-kill the process every time. After hours of debugging (cmake, timeouts, fallbacks), concluded: **QMD hybrid search is not viable on Railway's current memory limits.**

**QMD + OpenAI fallback (Feb 17 afternoon):** Tried using QMD for indexing with OpenAI as search fallback. Discovered the OpenAI builtin provider only indexes `MEMORY.md` + `memory/**/*.md`. The `extraPaths` config doesn't extend the builtin's indexing scope — it's a QMD-only feature. Dead end.

### Decision: Option A1 — OpenAI + Architect Pattern

**Approved by Guillermo: 2026-02-17 20:53 HKT**

```
┌──────────────────────────────────────────────────┐
│              MOLTY 🦎 (Architect)                 │
│  memory/                                          │
│    ├── YYYY-MM-DD.md     (own daily logs)         │
│    ├── refs/             (own reference docs)     │
│    ├── archive/          (old logs)               │
│    └── vault/            (Syncthing-shared) ◄─────┤── ONLY Molty indexes this
│         ├── decisions/                             │
│         ├── lessons/                               │
│         ├── people/                                │
│         └── ...                                    │
│  Provider: OpenAI text-embedding-3-small           │
│  Indexes: everything under memory/ automatically   │
├──────────────────────────────────────────────────┤
│  RAPHAEL 🔴              LEONARDO 🔵              │
│  memory/                 memory/                   │
│    ├── YYYY-MM-DD.md     ├── YYYY-MM-DD.md        │
│    └── refs/             └── refs/                 │
│                                                    │
│  Provider: OpenAI        Provider: OpenAI          │
│  Indexes: own memory/    Indexes: own memory/      │
│  Can WRITE to vault      Can WRITE to vault        │
│  Cannot SEARCH vault     Cannot SEARCH vault       │
├──────────────────────────────────────────────────┤
│           /data/shared/memory-vault/               │
│  Syncthing syncs to all agents + Guillermo PC      │
│  Agents write P1/P2 items here                     │
│  Only Molty has it under memory/ (as vault/)       │
└──────────────────────────────────────────────────┘
```

**Key principle:** Compartmentalization. Raphael only searches Brinc knowledge. Leonardo only searches Launchpad knowledge. Molty sees everything. Cross-domain queries go through Molty.

**Config for each agent (entire memory section):**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small"
      }
    }
  }
}
```

**Additional for Molty only:** vault/ directory under memory/ (via Syncthing or copy).

---

## What Has Been Done (Audit)

### ✅ Keep — Still valuable under A1

| Item | Why it stays |
|------|-------------|
| Shared vault structure (`decisions/`, `lessons/`, `people/`) | Same structure, just accessed differently |
| `CONTRIBUTION_PROTOCOL.md` | Agents still write to vault, protocol unchanged |
| Agent instructions (AGENTS.md updates) | Writing protocol still applies |
| Seed content (2 decisions, 1 lesson in vault) | Useful content |
| Dockerfile QMD addition (commit `3962a31`) | Harmless — QMD binary in image doesn't hurt. Remove in future cleanup if desired. |
| Builtin OpenAI index (`/data/.openclaw/memory/main.sqlite`) | This IS our search engine now — 50 files, 260 chunks, 542 embeddings |

### ❌ Remove — No longer needed

| Item | Why it goes | Action |
|------|-------------|--------|
| `memory.backend: "qmd"` in config | Switching to OpenAI builtin | Remove from config |
| `memory.qmd.*` config block | All QMD config | Remove from config |
| `memorySearch.extraPaths` | Doesn't work with builtin (verified) | Remove from config |
| QMD XDG paths / index files | Won't be used for search | Leave in place (harmless), clean up later |
| cmake (installed during debugging) | Not needed | `apt-get remove cmake` |
| Symlink `memory/shared-vault` | Replace with real directory or Syncthing target | Remove symlink, create proper vault/ |
| `memory-alt` QMD collection | Never used | Cleaned up with QMD removal |
| Orphaned index `/root/.cache/qmd/index.sqlite` | Manual accident | Delete |

### ⚠️ Modify — Needs updating

| Item | Change needed |
|------|---------------|
| Molty's Syncthing config | Point shared vault folder to `/data/workspace/memory/vault/` instead of `/data/shared/memory-vault/` |
| AGENTS.md shared vault section | Update path from `/data/shared/memory-vault/` to `/data/workspace/memory/vault/` |
| Raphael/Leonardo vault write path | They still write to `/data/shared/memory-vault/` — Syncthing syncs it to Molty's `memory/vault/` |
| MEMORY.md | Update architecture description |

---

## Execution Plan

### Step 1: Set up Molty's vault directory
**What:** Create `memory/vault/` and move shared vault content there. Configure Syncthing to sync this path.
**Details:**
- Remove the symlink at `memory/shared-vault`
- Create `memory/vault/` as a real directory
- Copy current shared vault content into it
- Update Syncthing folder config: change Molty's sync target for the shared vault from `/data/shared/memory-vault/` to `/data/workspace/memory/vault/`
**Risk:** Syncthing folder path change could cause a re-sync. Low risk — files are identical.
**Verify:** `ls memory/vault/decisions/` shows the files we created earlier.

### Step 2: Remove QMD config from Molty
**What:** Strip all QMD configuration. Set OpenAI as the provider.
**Config patch:**
```json
{
  "memory": {
    "backend": null,
    "qmd": null
  },
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "extraPaths": null
      }
    }
  }
}
```
**Verify:** After restart, `memory_search("Guillermo Hong Kong timezone")` returns results from MEMORY.md.

### Step 3: Verify vault files are searchable on Molty
**What:** Confirm the builtin indexer picks up `memory/vault/**/*.md`.
**Test:**
- `memory_search("central feed canary verification test")` → finds test file
- `memory_search("dockerfile runtime persistence lesson")` → finds lesson
**Gate:** If this fails, the builtin doesn't recurse into `memory/vault/`. Would need to investigate.
**Fallback:** If subdirectories don't work, flatten key vault files or create a vault summary file.

### Step 4: Standardise Raphael and Leonardo
**What:** Send config instructions to both agents. Remove QMD backend, set OpenAI.
**Config for both (via webhook):**
```json
{
  "memory": {
    "backend": null,
    "qmd": null
  },
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small"
      }
    }
  }
}
```
**Verify:** Each agent confirms `memory_search` returns results from their workspace memory.
**Note:** Neither agent gets vault/ under their memory/ — they only see their own domain.

### Step 5: Verify contribution flow
**What:** Test that an agent can write to the vault and Molty can search it.
**Test:**
1. Ask Raphael to write a test file to `/data/shared/memory-vault/decisions/2026-02-17-test-contribution.md`
2. Syncthing syncs to Molty's `memory/vault/decisions/`
3. Wait for OpenClaw's index refresh
4. `memory_search("test contribution from Raphael")` on Molty → finds it
5. Same search on Raphael → does NOT find it (compartmentalized)
6. Clean up test file

### Step 6: Cleanup
**What:** Remove artifacts from the QMD experiment.
- Remove orphaned index: `rm /root/.cache/qmd/index.sqlite`
- Remove cmake: `apt-get remove -y cmake cmake-data`
- Remove symlink: already done in Step 1
- Archive `docs/OPTION-B-EXECUTION-PLAN.md` → `docs/archive/memory/`
**Note:** Leave QMD binary in Dockerfile for now — it's harmless and avoids another fleet redeployment. Remove in next scheduled Dockerfile update.

### Step 7: Document and commit
**What:** Final documentation pass.
- Update `MEMORY.md` with new architecture
- Update `AGENTS.md` vault path
- Update shared vault `CONTRIBUTION_PROTOCOL.md` with correct paths
- Commit all changes to git
- Post summary to Discord `#command-center`

---

## New Agent Onboarding (Future: Donatello, April, Michelangelo)

1. Set `memorySearch.provider: "openai"`, `model: "text-embedding-3-small"`
2. Connect Syncthing for shared vault (write access to `/data/shared/memory-vault/`)
3. Do NOT put vault under their `memory/` — only Molty has that
4. Add contribution instructions to AGENTS.md
5. Verify `memory_search` works for their own workspace

---

## Syncthing Folder Mapping

| Folder | Molty path | Raphael/Leonardo path | Guillermo PC |
|--------|-----------|----------------------|-------------|
| Shared vault | `/data/workspace/memory/vault/` | `/data/shared/memory-vault/` | Obsidian vault |

**Molty is the only agent where the vault lives under `memory/`.** This is what makes the architect pattern work.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Builtin doesn't index `memory/vault/` subdirs | Low | High | Step 3 tests this before anything else. Fallback: flatten or summarize. |
| Syncthing path change causes conflict | Low | Low | Files are identical; worst case re-syncs |
| OpenAI API cost | Very low | Very low | ~cents/day, text-embedding-3-small is cheapest |
| Agent accidentally searches vault (leak) | Very low | Medium | Config doesn't include vault path on other agents |

---

## What We Learned (Lessons for MEMORY.md)

31. **QMD hybrid search (reranker + query expansion) requires ~6GB RAM.** Not viable on Railway's container limits. Embedding-only works fine.
32. **OpenClaw's builtin memory provider only indexes `MEMORY.md` + `memory/**/*.md`.** The `extraPaths` config is a QMD-only feature — does NOT extend builtin indexing.
33. **Evaluate before brute-forcing.** We spent hours trying to make QMD query work instead of stepping back to assess alternatives. PPEE exists for a reason.
34. **Simpler is almost always better for infrastructure.** Three lines of config beats a complex multi-system architecture that's fragile on the deployment platform.

---

## Phase 4: Quality Improvements (Unchanged — pursue after A1 is stable)

These improvements from the ClawVault analysis apply regardless of backend:

- **Memory typing** (`<!-- type: decision | priority: P1 -->`) — tag important entries
- **Wiki-links** (`[[Guillermo]]`, `[[Cerebro]]`) — cheap knowledge graph
- **Vault index** (`memory/INDEX.md`) — auto-generated one-liner per file
- **Priority-aware compaction** — P1 items survive compaction, P3 gets compressed
- **Tiered boot sequence** — priorities.md → MEMORY.md → daily logs

---

*Previous version of this plan archived to `docs/archive/memory/MASTER-PLAN-QMD-VERSION.md`*
