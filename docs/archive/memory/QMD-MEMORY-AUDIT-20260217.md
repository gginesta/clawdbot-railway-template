# QMD & Memory System Audit — 2026-02-17

*Audit requested by Guillermo. Evaluating against his actual goals.*

---

## Guillermo's Goals (What Actually Matters)

1. **Brinc** — Corporate venture building (Raphael handles)
2. **Cerebro / Launchpad** — AI venture platform (Leonardo handles)
3. **Mana Capital** — Investment/PE (no agent yet)
4. **Personal productivity** — Calendar, email, tasks, daily standup, briefings
5. **TMNT fleet reliability** — Agents work without constant firefighting

**The memory system exists to serve these goals** — not as a project in itself.

---

## What We Have (Current State)

### QMD Status Per Agent
| Agent | Backend | Status | Files | Vectors |
|-------|---------|--------|-------|---------|
| **Molty** | QMD (local) | ✅ Healthy | 247 | 6717 |
| **Leonardo** | QMD (local) | ✅ Working | — | — |
| **Raphael** | OpenAI embeddings | ✅ Working | — | — |

**All three agents have working memory search.** Different backends, same tool interface. No agent is broken.

### OpenClaw-Managed QMD (Molty)
- Index: `/data/.openclaw/agents/main/qmd/xdg-cache/qmd/index.sqlite` (36.3 MB)
- 4 auto-managed collections: `memory-root`, `memory-alt`, `memory-dir`, `sessions`
- Auto-updates every 5 minutes + on boot
- 7 pending embeddings (will auto-resolve)
- CPU-only (no GPU on Railway) — slow but functional

### What Was Built Yesterday (Feb 16)
- Memory vault structure at `/data/shared/memory-vault/` — 308 sources catalogued
- Central index with categories (people, projects, daily, archives, resources)
- Embedding config standardized (nomic-embed-text-v1, 768 dims)

---

## Plans That Exist (and Their Status)

| Document | Created | Status | Value Assessment |
|----------|---------|--------|-----------------|
| `memory-vault-plan-v3.md` | Feb 1 | Phase 1 done (Syncthing working) | ✅ Foundation done. Phases 2-3 = nice-to-have |
| `qmd-standardization-plan.md` | Feb 16 | Phase 1 done | ⚠️ **Overengineered.** All agents work. Standardizing for standardization's sake. |
| `qmd-migration-strategy-20260216.md` | Feb 16 | Phase 1 done, 2-3 pending | ⚠️ **Same issue.** Cross-agent sync adds complexity with no clear user benefit. |
| `CLAWVAULT-MEMORY-UPGRADE-PLAN.md` | Feb 15 | Draft, not started | 🟡 Phase 1 (YAML frontmatter) is useful. Rest is premature. |
| `qmd_indexing_strategy.md` | — | Unknown | Likely superseded |
| `qmd_standardization_master_log.md` | — | Unknown | Likely superseded |

**There are 6+ documents about memory/QMD strategy.** That's a red flag — we're planning more than executing.

---

## Honest Assessment

### What's Working
- ✅ All agents have memory search — it works
- ✅ Syncthing syncs shared files across agents + Guillermo's PC
- ✅ Memory vault structure exists with 308 sources catalogued
- ✅ Daily logs, MEMORY.md, and workspace files all indexed
- ✅ Session transcripts indexed (196 sessions on Molty)

### What's NOT Worth Pursuing Right Now
1. **Cross-agent QMD synchronization** — Agents don't need to search each other's memories. They communicate via Discord/webhooks. This solves a problem that doesn't exist.
2. **Standardizing Raphael onto QMD** — His OpenAI embeddings work. Migrating costs time for zero user benefit.
3. **Custom embedding provider (nomic-embed)** — OpenClaw's built-in QMD uses embeddinggemma locally. No need for a separate provider.
4. **Memory vault "phases 2-3"** — Parsing rules, webhook propagation, validation suites... this is infrastructure for infrastructure's sake.

### What IS Worth Doing (ranked by Guillermo-impact)

1. **🔴 Fix morning briefing** — Calendar token expired, Gmail broken until Feb 19. This directly affects Guillermo's daily workflow. Priority when he's back in HK.
2. **🔴 Keep cron jobs stable** — All 11 crons now on Haiku. Monitor for failures. Guillermo shouldn't have to think about this.
3. **🟡 ClawVault Phase 1 only** — YAML frontmatter on daily logs. Simple, 1-2 hours, improves memory quality for compaction. Skip phases 2-3.
4. **🟡 Clean up doc sprawl** — Consolidate the 6+ QMD/memory docs into ONE status doc. Archive the rest.
5. **🟢 Memory vault re-extraction** — Better processing of 3 years of AI conversation history (ChatGPT, Claude, Grok). Deferred, do when there's a quiet day.

---

## Recommendation

**Stop building memory infrastructure. Start using what we have.**

The system works. Molty has 247 files and 6717 vectors indexed. Leonardo and Raphael are fine. The memory vault has 308 sources. Syncthing syncs everything.

The next dollar of effort should go to:
1. Getting the morning briefing fully working (Feb 19 when Gmail/Calendar are back)
2. Making the daily standup reliable
3. Actual Brinc/Cerebro/Mana work — the stuff these agents exist for

The QMD migration project should be **closed as complete (Phase 1)** with phases 2-3 marked as "not needed."

---

*Authored by Molty 🦎 — Feb 17, 2026*
