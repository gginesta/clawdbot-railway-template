# TMNT Memory Search Audit

*Date: 2026-02-17 | Author: Molty 🦎 | Status: Audit only — no changes*

---

## Fleet Summary

| Agent | Backend | Binary | Index Status | Session Indexing |
|-------|---------|--------|-------------|-----------------|
| **Molty 🦎** | QMD (local) | `/usr/local/bin/qmd` → `/root/.bun/bin/qmd` | ✅ 246 files, 6589 vectors, 13 pending embed | ✅ 30-day retention |
| **Raphael 🔴** | Built-in memorySearch (OpenAI) | No QMD binary installed | ✅ Working (OpenAI embeddings) | ❌ Not applicable |
| **Leonardo 🔵** | QMD (local) | `/root/.bun/bin/qmd` | ✅ Working (per his report) | ✅ 30-day retention |

---

## Two Different Approaches

### Approach 1: QMD Backend (Molty, Leonardo)

**Config key:** `memory.backend: "qmd"`

Uses QMD as a local sidecar: BM25 full-text + vector embeddings + reranking, all running on-device. No external API calls for search.

**Molty's config:**
```json
"memory": {
  "backend": "qmd",
  "citations": "auto",
  "qmd": {
    "command": "/usr/local/bin/qmd",
    "includeDefaultMemory": true,
    "sessions": { "enabled": true, "retentionDays": 30 },
    "update": { "interval": "5m", "debounceMs": 15000, "onBoot": true },
    "limits": { "maxResults": 8, "timeoutMs": 5000 }
  }
}
```

**Leonardo's config (identical pattern):**
```json
"memory": {
  "backend": "qmd",
  "citations": "auto",
  "qmd": {
    "command": "/root/.bun/bin/qmd",
    "includeDefaultMemory": true,
    "sessions": { "enabled": true, "retentionDays": 30 },
    "update": { "interval": "5m", "debounceMs": 15000, "onBoot": true },
    "limits": { "maxResults": 8, "timeoutMs": 5000 }
  }
}
```

**How it works:**
- OpenClaw manages QMD under `~/.openclaw/agents/<agentId>/qmd/`
- Sets `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` to isolate each agent's index
- Auto-creates 4 collections: `memory-root` (MEMORY.md), `memory-alt` (memory.md), `memory-dir` (memory/**/*.md), `sessions` (transcripts)
- Runs `qmd update` + `qmd embed` on boot and every 5 minutes
- Search via `qmd query --json` (BM25 + vectors + reranking)
- Falls back to built-in SQLite if QMD binary missing/fails

**⚠️ Gotcha:** Running `qmd status` from CLI without XDG vars shows an empty default index. Must set:
```bash
export XDG_CONFIG_HOME="/data/.openclaw/agents/main/qmd/xdg-config"
export XDG_CACHE_HOME="/data/.openclaw/agents/main/qmd/xdg-cache"
```

**Pros:** Fully local, no API costs, hybrid search (BM25+vectors+reranking), session transcript search
**Cons:** CPU-only on Railway (no GPU), embedding is slow, requires QMD binary installed

### Approach 2: Built-in memorySearch (Raphael)

**Config key:** `agents.defaults.memorySearch`

Uses OpenAI's `text-embedding-3-small` API for vector embeddings. No local binary needed.

**Raphael's config:**
```json
"memorySearch": {
  "enabled": true,
  "provider": "openai",
  "remote": {
    "apiKey": "<OPENAI_API_KEY>",
    "batch": { "enabled": false }
  },
  "fallback": "none",
  "model": "text-embedding-3-small"
}
```

**How it works:**
- Indexes `MEMORY.md` + `memory/*.md` using OpenAI embedding API
- Accessed via `memory_search` / `memory_get` tools (same interface as QMD)
- Native to OpenClaw — no external binary
- Requires OpenAI API key

**Pros:** Simple, fast embeddings (API), no binary to install/maintain
**Cons:** API cost per search, no session transcript indexing, no BM25 hybrid search, no reranking

---

## Molty's Detailed Status

**QMD Collections:**
| Collection | Pattern | Files | Purpose |
|-----------|---------|-------|---------|
| `memory-root` | `MEMORY.md` | 1 | Long-term curated memory |
| `memory-alt` | `memory.md` | 0 | Alternative memory file (unused) |
| `memory-dir` | `**/*.md` | 49 | Daily logs + archives |
| `sessions` | `**/*.md` | 196 | Exported session transcripts |

**Index:** 36.3 MB SQLite database
**Vectors:** 6589 embedded, 13 pending
**GPU:** None (CPU-only, 48 math cores) — embedding is slow but functional
**Models (local GGUF):**
- Embedding: `embeddinggemma-300M`
- Reranking: `Qwen3-Reranker-0.6B-Q8_0`
- Query expansion: `qmd-query-expansion-1.7B`

**⚠️ Known issue:** CUDA build fails (no cmake), falls back to CPU. Not blocking — just slower.

---

## Compatibility Note

Both approaches expose the same `memory_search` / `memory_get` tool interface. Agents using either backend can search memories identically from the LLM's perspective. The difference is purely infrastructure.

**Molty also has `agents.defaults.memorySearch` configured** (OpenAI embeddings) alongside QMD. When `memory.backend: "qmd"` is set, QMD takes priority. The `memorySearch` config serves as implicit fallback if QMD fails.

---

## Recommendations (for future — NOT acting now)

1. **No urgency to standardize.** Both approaches work. Raphael's simpler setup is fine for his use case.
2. **If standardizing:** QMD gives session transcript search + hybrid retrieval at no API cost. But requires binary on each container.
3. **QMD binary status:** Installed on Molty + Leonardo containers (via `bun install -g`). NOT on Raphael's container.
4. **13 pending embeddings on Molty:** Will resolve automatically on next QMD update cycle (every 5 min).
