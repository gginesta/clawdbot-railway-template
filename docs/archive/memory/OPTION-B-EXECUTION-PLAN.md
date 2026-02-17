# Option B Execution Plan: QMD Backend + OpenAI Search

*Created: 2026-02-17 20:30 HKT | Owner: Molty 🦎 | Status: PLANNING*

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 OpenClaw memory_search               │
│                                                      │
│  1. Try QMD query (timeout 1s → always fails fast)   │
│  2. Fall back to OpenAI text-embedding-3-small       │
│     → Indexes: MEMORY.md + memory/*.md + extraPaths  │
│     → extraPaths includes /data/shared/memory-vault  │
│                                                      │
│  QMD still runs in background:                       │
│  • Manages collections (shared-vault, memory, etc.)  │
│  • Indexes session transcripts (30-day retention)    │
│  • Auto-updates every 5min                           │
│  • Embeds with embeddinggemma-300M (for future use)  │
└─────────────────────────────────────────────────────┘
```

**Search flow:** memory_search → QMD times out (1s) → OpenAI handles it (fast, reliable)
**Indexing flow:** QMD still indexes everything in background (sessions, vault, workspace)
**Future:** When QMD gets lighter reranker models, flip timeout back up → full hybrid search

---

## What We Already Have (from today's work)

| Component | Status | Notes |
|-----------|--------|-------|
| QMD binary in Dockerfile | ✅ Done | Commit `3962a31`, all agents |
| QMD backend config (Molty) | ✅ Done | `memory.backend: "qmd"` |
| QMD collections (Molty) | ✅ Done | 5 collections, 543 files, 7406 vectors |
| Shared vault structure | ✅ Done | decisions/, lessons/, people/, projects/ |
| Shared vault QMD collection | ✅ Done | 297 files indexed |
| Contribution protocol | ✅ Done | `/data/shared/memory-vault/CONTRIBUTION_PROTOCOL.md` |
| Agent instructions sent | ✅ Done | Webhooks to Raphael + Leonardo |
| AGENTS.md updated (Molty) | ✅ Done | Shared vault section added |
| OpenAI memorySearch config | ✅ Done | Already configured as fallback |
| extraPaths for shared vault | ✅ Done | `/data/shared/memory-vault` |
| QMD on Leonardo | ✅ Done | 405 files, 2683 vectors |
| QMD config on Raphael | ⚠️ Partial | Config patched, binary persistence unverified |

## What's No Longer Relevant

| Item | Why |
|------|-----|
| Installing cmake | Was trying to fix qmd query — not needed since we're using OpenAI for search |
| Increasing QMD timeout to 30s | Opposite — we want 1s for fast fallback |
| Pre-warming reranker model | Won't fit in Railway memory regardless |
| Debugging qmd query OOM | Root-caused and accepted — Railway can't run reranker |

---

## Execution Steps

### Step 1: Configure Molty for fast OpenAI fallback
**What:** Lower QMD timeout to 1s so `memory_search` falls through to OpenAI instantly instead of hanging.
**Config change:**
```json
{
  "memory": {
    "qmd": {
      "limits": {
        "timeoutMs": 1000
      }
    }
  }
}
```
**Verify:** Run `memory_search("CENTRAL_FEED_CANARY_2026_02_17")` — should return results from OpenAI within seconds, not time out for 30s.
**Rollback:** Set timeoutMs back to 30000.

### Step 2: Verify OpenAI indexes the shared vault via extraPaths
**What:** Confirm that the OpenAI fallback search actually covers `/data/shared/memory-vault/` files, not just workspace memory.
**Test:** 
- `memory_search("central feed canary verification test")` → should find the test file in shared vault
- `memory_search("dockerfile runtime persistence lesson")` → should find the lesson we wrote
**If it doesn't work:** The OpenAI built-in might not index extraPaths on first search. May need a gateway restart or `openclaw memory index` to trigger initial indexing.
**This is the critical gate — if extraPaths doesn't work with OpenAI, we need a different approach.**

### Step 3: Verify Raphael's QMD post-redeployment
**What:** Check if the Dockerfile fix (commit `3962a31`) gave Raphael a working QMD binary.
**Action:** Send webhook to Raphael asking for `which qmd` and `qmd status` output.
**If working:** Confirm collections created, session indexing active.
**If not working:** Debug Dockerfile. But since QMD is background-only (not needed for search), this is lower priority.

### Step 4: Standardise config across fleet
**What:** Ensure all 3 agents have identical memory config.
**Target config for each agent:**
```json
{
  "memory": {
    "backend": "qmd",
    "qmd": {
      "command": "/usr/local/bin/qmd",
      "includeDefaultMemory": true,
      "paths": [
        {
          "path": "/data/shared/memory-vault",
          "name": "shared-vault",
          "pattern": "**/*.md"
        }
      ],
      "sessions": {
        "enabled": true,
        "retentionDays": 30
      },
      "update": {
        "interval": "5m",
        "debounceMs": 15000,
        "onBoot": true
      },
      "limits": {
        "maxResults": 8,
        "timeoutMs": 1000
      }
    }
  },
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "extraPaths": ["/data/shared/memory-vault"]
      }
    }
  }
}
```
**Action:** Send config instructions to Raphael and Leonardo via webhook.
**Verify:** Each agent confirms `memory_search` returns results from shared vault.

### Step 5: Cleanup
**What:** Remove unused artifacts from today's debugging.
- Remove `memory-alt` QMD collection (0 files, never used)
- Remove orphaned manual index at `/root/.cache/qmd/index.sqlite`
- Remove cmake (installed during debugging, not needed)
- Clean up test file: `decisions/2026-02-17-test-central-feed.md`
**Action:** CLI commands on Molty.

### Step 6: Full re-index
**What:** Run `qmd update && qmd embed` on all agents to ensure everything is fresh.
**Action:**
- Molty: run locally with XDG vars
- Leonardo: webhook instruction
- Raphael: webhook instruction (if Step 3 confirmed working)
**Verify:** Each agent reports 0 pending files.

### Step 7: Document final architecture
**What:** Update master plan + MEMORY.md with final architecture decision.
- Update `docs/MEMORY-SYSTEM-MASTER-PLAN.md` — mark Option B as final decision
- Update `MEMORY.md` — record the architecture and config
- Update shared vault copy of master plan
- Commit all changes to git

---

## Success Criteria

All 6 of Guillermo's goals met:

| # | Goal | How Option B Achieves It |
|---|------|--------------------------|
| 1 | Standardise across fleet | Identical config on all 3 agents (Step 4) |
| 2 | One provider | OpenAI text-embedding-3-small for search everywhere (Step 1-2) |
| 3 | Complete indexing → central memory | QMD collections + extraPaths feed shared vault to Molty (Step 2, 4) |
| 4 | Consistent embedding index | Same OpenAI model/dimensions on all agents (Step 4) |
| 5 | Full QMD re-indexing | Clean re-index on all agents (Step 6) |
| 6 | Cleanup + trim | Remove unused collections, set 30-day session retention (Step 5) |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenAI extraPaths doesn't index vault | Medium | High | **Step 2 is the gate.** If fails, investigate `openclaw memory index` or symlink vault into workspace |
| Raphael QMD binary missing post-deploy | Medium | Low | QMD is background-only; OpenAI search works without it |
| OpenAI API cost | Low | Low | ~cents/day across fleet |
| QMD indexing errors | Low | Low | Doesn't affect search; logs warning and continues |

---

## Estimated Time

| Step | Time | Dependencies |
|------|------|-------------|
| 1. Configure timeout | 2 min | None |
| 2. Verify extraPaths | 5 min | Step 1 |
| 3. Verify Raphael | 5 min | None (parallel with 1-2) |
| 4. Fleet config | 10 min | Steps 1-2 confirmed |
| 5. Cleanup | 5 min | Step 2 confirmed |
| 6. Re-index | 10 min | Steps 3-4 |
| 7. Document | 10 min | All steps |
| **Total** | **~45 min** | |

---

*This plan replaces the previous Phase 2/3 approach. Option C (full local QMD) is archived as future possibility.*
