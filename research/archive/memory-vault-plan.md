# Memory Vault System Plan

**Research & Implementation Proposal**  
*Compiled: February 1, 2026*

---

## 1. Research Summary

### 1.1 qmd (Tobi Lütke's Tool)

**What it is:** A local search engine for markdown documents, knowledge bases, and meeting notes.

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    QMD Hybrid Search                        │
├─────────────────────────────────────────────────────────────┤
│  User Query                                                 │
│      ↓                                                      │
│  Query Expansion (LLM generates variations)                 │
│      ↓                                                      │
│  ┌─────────────┐    ┌─────────────┐                        │
│  │ BM25 (FTS5) │ +  │ Vector Search│  (parallel)           │
│  │ keyword     │    │ semantic    │                        │
│  └─────────────┘    └─────────────┘                        │
│      ↓                                                      │
│  RRF Fusion (Reciprocal Rank Fusion)                       │
│      ↓                                                      │
│  LLM Re-ranking (yes/no with confidence)                   │
│      ↓                                                      │
│  Position-Aware Blending → Final Results                   │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
| Component | Model | Size |
|-----------|-------|------|
| Embeddings | embeddinggemma-300M | ~300MB |
| Re-ranker | qwen3-reranker-0.6b | ~640MB |
| Query expansion | qmd-query-expansion-1.7B | ~1.1GB |

**Total: ~2GB of local models**

**Features:**
- Collections (organize by folder/project)
- Context descriptions (metadata for search)
- MCP server (integrates with Claude)
- SQLite storage (portable)
- Chunking with overlap (800 tokens, 15% overlap)

**Requirements:**
- Bun >= 1.0.0
- macOS: Homebrew SQLite
- ~2GB disk for models

### 1.2 The "Memory Vault" Concept (Twitter Discussion)

**Core Idea:** Export all AI conversations and personal data into a searchable knowledge base that provides context to AI assistants.

**Data Sources to Collect:**
- ChatGPT conversation exports
- Claude conversation exports
- Grok conversation exports
- Meeting transcripts
- Personal notes (Notion, Obsidian, etc.)
- Email summaries
- Project documentation
- Decision logs

**Benefits:**
- AI has "memory" across all platforms
- Searchable personal knowledge graph
- Privacy (all local)
- Portable between AI systems
- Reduces repetition ("I already told Claude this...")

### 1.3 Nat Eliason's AI Life Coach Approach

**Philosophy:** Build personalized AI tools that know YOU.

**Key Insight:** The most valuable AI tools are those customized with your personal data, goals, and context.

---

## 2. Our Current Setup vs. What We Need

### 2.1 What We Have Now

| Feature | Current State | Location |
|---------|---------------|----------|
| Memory search | ✅ Gemini embeddings | `/data/.openclaw/memory/main.sqlite` |
| Daily logs | ✅ `memory/YYYY-MM-DD.md` | `/data/workspace/memory/` |
| Long-term memory | ✅ `MEMORY.md` | `/data/workspace/MEMORY.md` |
| Session transcripts | ✅ JSONL files | `/data/.openclaw/agents/main/sessions/` |

**Limitations:**
- Memory search only indexes `MEMORY.md` + `memory/*.md`
- No access to historical ChatGPT/Claude/Grok conversations
- Session transcripts not semantically searchable
- No structured knowledge base

### 2.2 What We Want

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY VAULT                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ AI Chat History │  │ Personal Notes  │                  │
│  │ - ChatGPT       │  │ - Notion export │                  │
│  │ - Claude        │  │ - Obsidian      │                  │
│  │ - Grok          │  │ - Meeting notes │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                            │
│           └────────┬───────────┘                            │
│                    ↓                                        │
│           ┌────────────────┐                                │
│           │  Unified Index │                                │
│           │  (embeddings)  │                                │
│           └────────┬───────┘                                │
│                    ↓                                        │
│  ┌─────────────────────────────────────┐                   │
│  │     Semantic Search + Retrieval     │                   │
│  └─────────────────────────────────────┘                   │
│                    ↓                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │  Molty  │  │ Project │  │   Sub-  │                     │
│  │ (Opus)  │  │  Leads  │  │ agents  │                     │
│  └─────────┘  └─────────┘  └─────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Options

### Option A: Use qmd Directly

**Pros:**
- Best-in-class hybrid search (BM25 + vector + re-ranking)
- MCP server ready
- Actively maintained by Tobi Lütke (Shopify CEO)
- All local, private

**Cons:**
- Requires Bun (not currently installed)
- ~2GB model downloads
- CPU-intensive for embedding/re-ranking
- Separate tool from OpenClaw

**Implementation:**
```bash
# Install
bun install -g https://github.com/tobi/qmd

# Create collections
qmd collection add /data/vault/chatgpt --name chatgpt
qmd collection add /data/vault/claude --name claude
qmd collection add /data/vault/grok --name grok
qmd collection add /data/vault/notes --name notes
qmd collection add /data/workspace/memory --name daily-logs

# Add context
qmd context add qmd://chatgpt "ChatGPT conversation history"
qmd context add qmd://claude "Claude conversation history"
qmd context add qmd://daily-logs "Molty's daily memory logs"

# Generate embeddings
qmd embed

# Search
qmd query "what did Guillermo decide about the project structure?"
```

**Integration with OpenClaw:**
- Run qmd as MCP server
- Or add qmd commands to exec allowlist
- Or create a skill that wraps qmd

### Option B: Enhance OpenClaw's Built-in Memory

**Pros:**
- Already integrated
- Uses free Gemini embeddings
- No additional setup

**Cons:**
- Less sophisticated search (no re-ranking)
- Limited to memory paths
- No hybrid BM25 + vector

**Implementation:**
1. Expand `memorySearch.extraPaths` to include vault
2. Convert chat exports to markdown
3. Let existing Gemini embeddings index everything

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "gemini",
        "extraPaths": [
          "/data/vault/chatgpt",
          "/data/vault/claude",
          "/data/vault/grok"
        ]
      }
    }
  }
}
```

### Option C: Hybrid Approach (Recommended)

**Philosophy:** Use the right tool for each job.

1. **qmd for deep research** — when you need to find something specific
2. **OpenClaw memory for daily context** — automatic recall during conversations
3. **Structured vault** — organized markdown files as the source of truth

**Implementation:**

```
/data/vault/
├── chatgpt/
│   ├── 2024/
│   │   └── conversations.md (parsed exports)
│   └── 2025/
│       └── conversations.md
├── claude/
│   ├── projects/
│   │   └── project-name.md
│   └── conversations/
│       └── YYYY-MM.md
├── grok/
│   └── conversations.md
├── notes/
│   ├── meetings/
│   ├── ideas/
│   └── decisions/
└── index.md (master index)
```

---

## 4. Data Export & Conversion Plan

### 4.1 ChatGPT Export

**Export Method:** Settings → Data Controls → Export Data

**Format:** ZIP containing `conversations.json`

**Conversion Script Needed:**
```javascript
// Parse conversations.json → markdown files
// Group by month or topic
// Extract key decisions, preferences, learnings
```

### 4.2 Claude Export

**Export Method:** Account Settings → Export Conversations (or per-project)

**Format:** JSON or markdown (depending on version)

**Processing:**
- Convert to consistent markdown format
- Tag by project/topic

### 4.3 Grok Export

**Export Method:** Settings → Download Your Data

**Processing:**
- Convert to markdown
- Tag appropriately

### 4.4 Notion Export

**Export Method:** Settings → Export → Markdown & CSV

**Processing:**
- Already markdown, just organize
- May need to flatten nested structure

---

## 5. Recommended Architecture

### 5.1 Directory Structure

```
/data/
├── vault/                      # The Memory Vault
│   ├── ai-history/            # Exported AI conversations
│   │   ├── chatgpt/
│   │   ├── claude/
│   │   └── grok/
│   ├── knowledge/             # Processed knowledge
│   │   ├── preferences.md     # "Guillermo prefers..."
│   │   ├── decisions.md       # "We decided to..."
│   │   └── learnings.md       # Key insights
│   ├── projects/              # Project-specific context
│   │   ├── cerebro/
│   │   ├── brinc/
│   │   └── personal/
│   └── reference/             # Reference materials
│       ├── people.md
│       ├── companies.md
│       └── tools.md
│
├── workspace/                  # Molty's workspace (current)
│   ├── memory/                # Daily logs
│   ├── MEMORY.md              # Long-term memory
│   └── ...
│
└── .openclaw/
    └── memory/main.sqlite     # Embedding index
```

### 5.2 Integration Points

1. **memory_search** — Enhanced to include vault paths
2. **New skill: vault-search** — Wrapper for qmd if installed
3. **MEMORY.md** — Curated summary, points to vault for details
4. **Subagent context** — Can query vault for project-specific info

### 5.3 Workflow

**When Guillermo asks something:**
```
User: "What did we decide about the investor presentation?"

Molty:
1. memory_search("investor presentation decision")
2. Check MEMORY.md
3. If needed, deeper search via vault
4. Synthesize answer with source references
```

---

## 6. Implementation Phases

### Phase 1: Foundation (This Week)
- [ ] Create `/data/vault/` directory structure
- [ ] Set up conversion scripts for exports
- [ ] Guillermo exports ChatGPT, Claude, Grok data
- [ ] Convert to markdown format

### Phase 2: Basic Integration (Next Week)
- [ ] Add vault paths to `memorySearch.extraPaths`
- [ ] Create `preferences.md`, `decisions.md` from exports
- [ ] Test memory_search with vault data
- [ ] Update MEMORY.md to reference vault

### Phase 3: Advanced Search (Week 3)
- [ ] Install qmd (requires decision on Bun)
- [ ] Create qmd collections
- [ ] Generate embeddings
- [ ] Create vault-search skill

### Phase 4: Project Lead Integration (When Ready)
- [ ] Define per-project vault sections
- [ ] Configure project leads to access their sections
- [ ] Set up cross-referencing

---

## 7. Questions for Guillermo

1. **qmd vs Native:** Do you want to install Bun and use qmd's advanced search, or start with OpenClaw's native memory search?

2. **Scope:** What data do you want to include first?
   - [ ] ChatGPT history
   - [ ] Claude history
   - [ ] Grok history
   - [ ] Notion notes
   - [ ] Meeting transcripts
   - [ ] Other:

3. **Privacy:** Any conversations/data that should be EXCLUDED from the vault?

4. **Processing:** Should I create automated scripts to convert exports, or do you prefer to curate manually?

5. **Project Separation:** Should each project lead have access to the full vault, or only their project section?

---

## 8. Appendix: qmd Commands Reference

```bash
# Collection management
qmd collection add <path> --name <name>
qmd collection list
qmd collection remove <name>

# Context (descriptions)
qmd context add qmd://<collection> "description"
qmd context list

# Indexing
qmd embed              # Generate embeddings
qmd embed -f           # Force re-embed
qmd update             # Re-index all

# Search modes
qmd search "query"     # BM25 keyword search (fast)
qmd vsearch "query"    # Vector semantic search
qmd query "query"      # Hybrid + re-ranking (best)

# Retrieval
qmd get <file>         # Get full document
qmd get "#docid"       # Get by short hash
qmd multi-get "*.md"   # Get multiple files

# Output formats
--json                 # For agent processing
--files                # Path list
--md                   # Markdown
```

---

*This plan will be refined based on your feedback and the specific tweets' content.*
