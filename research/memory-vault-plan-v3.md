# Memory Vault System — Complete Implementation Plan v3

**Based on Nat Eliason's Architecture + Cathryn Lavery's Implementation**  
*Created: February 1, 2026*  
*Last Updated: February 1, 2026*

---

## Executive Summary

This is the definitive implementation plan for Guillermo's AI memory system, combining:
- **Nat Eliason's** PARA + atomic facts architecture
- **Cathryn Lavery's** practical implementation approach
- **Tobi Lütke's** QMD search layer
- **Our existing OpenClaw infrastructure**

**The Goal:** Give Molty and future project leads access to 3+ years of your AI conversation history, decisions, relationships, and preferences — searchable, structured, and always current.

---

## Part 1: Platform Decision

### The Question: Obsidian vs Plain Markdown?

| Factor | Obsidian | Plain Markdown |
|--------|----------|----------------|
| **Visual graph** | ✅ Beautiful visualization | ❌ No graph UI |
| **Backlinks** | ✅ Automatic | ❌ Manual |
| **Mobile access** | ✅ iOS/Android apps | ⚠️ Requires file sync app |
| **Agent compatibility** | ✅ Just markdown files | ✅ Just markdown files |
| **Runs on Railway** | ❌ No (GUI app) | ✅ Yes |
| **Plugins** | ✅ Huge ecosystem | ❌ None |
| **Sync options** | Obsidian Sync ($) or Git | Git, Syncthing, etc. |
| **Lock-in** | ❌ None (plain files) | ❌ None |

### Recommendation: Hybrid Approach

**Source of truth:** Plain markdown files on Railway (where Molty lives)  
**Human interface:** Obsidian on your devices (laptop, phone)  
**Sync mechanism:** Git (private repo) or Syncthing

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐         ┌─────────────────┐              │
│   │    RAILWAY      │  sync   │  YOUR DEVICES   │              │
│   │   (Molty)       │◄───────►│   (Obsidian)    │              │
│   │                 │   Git   │                 │              │
│   │  /data/vault/   │   or    │  ~/vault/       │              │
│   │  Plain markdown │ Syncthing  Obsidian UI    │              │
│   └─────────────────┘         └─────────────────┘              │
│           │                           │                         │
│           │ read/write                │ browse/edit             │
│           ▼                           ▼                         │
│   ┌─────────────────┐         ┌─────────────────┐              │
│   │  Molty + Leads  │         │   Guillermo     │              │
│   │  (AI agents)    │         │   (human)       │              │
│   └─────────────────┘         └─────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why this works:**
- Molty reads/writes plain markdown files — no special tooling needed
- You browse in Obsidian with graph view, backlinks, search
- Changes sync bidirectionally via Git or Syncthing
- No vendor lock-in — it's all just files

---

## Part 2: Complete Directory Structure

### The Vault Layout

```
/data/vault/
│
├── life/                              # THE KNOWLEDGE GRAPH (PARA)
│   │
│   ├── projects/                      # Active work with goals/deadlines
│   │   ├── _template/                 # Template for new projects
│   │   │   ├── summary.md
│   │   │   └── items.json
│   │   ├── cerebro/
│   │   │   ├── summary.md
│   │   │   └── items.json
│   │   ├── brinc/
│   │   │   ├── summary.md
│   │   │   └── items.json
│   │   ├── openclaw-setup/
│   │   │   ├── summary.md
│   │   │   └── items.json
│   │   └── tinker-labs/
│   │       ├── summary.md
│   │       └── items.json
│   │
│   ├── areas/                         # Ongoing responsibilities (no end date)
│   │   ├── people/
│   │   │   ├── _template/
│   │   │   ├── guillermo/             # YOU
│   │   │   │   ├── summary.md
│   │   │   │   └── items.json
│   │   │   └── [other people]/
│   │   │
│   │   ├── companies/
│   │   │   ├── _template/
│   │   │   └── [companies you work with]/
│   │   │
│   │   └── roles/
│   │       └── [investor, founder, etc.]/
│   │
│   ├── resources/                     # Topics of interest, reference
│   │   ├── ai-models/
│   │   │   ├── summary.md
│   │   │   └── items.json
│   │   ├── productivity-systems/
│   │   ├── investment-thesis/
│   │   └── [other topics]/
│   │
│   ├── archives/                      # Inactive items from above
│   │   ├── projects/
│   │   ├── people/
│   │   └── companies/
│   │
│   ├── index.md                       # Master index of all entities
│   └── README.md                      # System documentation
│
├── imports/                           # RAW AI EXPORTS (for processing)
│   ├── chatgpt/
│   │   └── conversations.json
│   ├── claude/
│   │   └── export/
│   └── grok/
│       └── export/
│
├── daily/                             # DAILY NOTES (Layer 2)
│   ├── 2024/
│   │   └── [YYYY-MM-DD.md files]
│   ├── 2025/
│   │   └── [YYYY-MM-DD.md files]
│   └── 2026/
│       ├── 2026-01-31.md
│       └── 2026-02-01.md
│
├── tacit.md                           # TACIT KNOWLEDGE (Layer 3)
│
├── .obsidian/                         # Obsidian config (if synced)
│   ├── app.json
│   ├── appearance.json
│   └── graph.json
│
└── README.md                          # Vault documentation
```

### Obsidian Configuration

For the best experience in Obsidian, we'll configure:

**Graph View Settings:**
- Color nodes by folder (projects=blue, people=green, companies=orange)
- Show orphan notes
- Highlight current file

**Recommended Plugins:**
- **Dataview** — Query items.json files
- **Calendar** — Navigate daily notes
- **Templater** — Create new entities from templates
- **Git** — Auto-sync with Railway

---

## Part 3: File Formats & Schemas

### 3.1 Entity Summary (summary.md)

```markdown
# [Entity Name]

## Quick Context
<!-- 2-3 sentences max. What you need to know immediately. -->

## Current Status
<!-- What's happening now with this entity? -->

## Key Relationships
<!-- Links to related entities -->
- [[people/jane]] — CTO, primary contact
- [[companies/acme]] — Jane's company
- [[projects/acme-deal]] — Active project

## Hot Facts (Recent)
<!-- Auto-generated weekly from items.json -->
<!-- Facts accessed in last 7 days -->

## Warm Facts
<!-- Auto-generated weekly from items.json -->
<!-- Facts accessed 8-30 days ago -->

---
*Last synthesized: 2026-02-01*
*Facts in items.json: 23 active, 5 superseded*
```

### 3.2 Atomic Facts (items.json)

```json
{
  "entity": "areas/people/jane",
  "entityType": "person",
  "created": "2026-01-15",
  "lastModified": "2026-02-01",
  "facts": [
    {
      "id": "jane-001",
      "fact": "CTO at Acme Corp since March 2024",
      "category": "status",
      "timestamp": "2024-03-15",
      "source": "chatgpt-2024-03-15",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": ["companies/acme"],
      "lastAccessed": "2026-02-01",
      "accessCount": 12,
      "confidence": "high"
    },
    {
      "id": "jane-002", 
      "fact": "Prefers email over Slack for important decisions",
      "category": "preference",
      "timestamp": "2024-06-20",
      "source": "claude-2024-06-20",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": [],
      "lastAccessed": "2025-11-10",
      "accessCount": 3,
      "confidence": "medium"
    },
    {
      "id": "jane-003",
      "fact": "Was VP Engineering at Acme",
      "category": "status",
      "timestamp": "2023-01-01",
      "source": "chatgpt-2023-01-15",
      "status": "superseded",
      "supersededBy": "jane-001",
      "relatedEntities": ["companies/acme"],
      "lastAccessed": "2024-03-15",
      "accessCount": 8,
      "confidence": "high"
    }
  ]
}
```

### 3.3 Categories Reference

| Category | Description | Examples |
|----------|-------------|----------|
| `relationship` | How entities connect | "Investor in Acme", "Reports to Jane" |
| `milestone` | Significant events with dates | "Closed Series A March 2024" |
| `status` | Current state of something | "Project on hold", "Active advisor" |
| `preference` | How they like things done | "Prefers async", "No meetings before 10am" |
| `context` | Background information | "Based in Singapore", "Technical background" |
| `decision` | Important decisions made | "Decided to use Railway for hosting" |
| `insight` | Learnings or realizations | "Realized model routing saves costs" |

### 3.4 Confidence Levels

| Level | Meaning | Source Examples |
|-------|---------|-----------------|
| `high` | Explicitly stated, verified | Direct conversation, official announcement |
| `medium` | Inferred from context | Mentioned in passing, assumed from behavior |
| `low` | Uncertain, needs verification | Heard secondhand, old information |

### 3.5 Tacit Knowledge (tacit.md)

```markdown
# Tacit Knowledge

*How Guillermo operates. Updated when new patterns emerge.*

## Communication Preferences
- **Messaging:** Telegram primary, WhatsApp backup
- **Style:** Casual + friendly, but efficient. No fluff.
- **Response time:** Appreciates quick responses, but quality > speed
- **Timezone:** GMT+8 (Hong Kong) — always use HKT when discussing times

## Working Style
- **Decision making:** Likes structured options, appreciates tables
- **Learning:** Curious by nature, learns fast with good instructions
- **Problem solving:** Enjoys troubleshooting, will spend hours on interesting problems
- **Tools:** Prefers modern tooling, willing to try new things

## AI Interaction Patterns
- **Verbosity:** Prefers concise answers, expand when asked
- **Format:** Tables for comparisons, bullet lists for options
- **Proactivity:** Appreciates suggestions, but ask before major changes
- **Memory:** Expects context retention across sessions

## Rules & Boundaries
- **External actions:** Ask before sending emails/tweets/public posts
- **Spending:** Flag anything that costs money before executing
- **Privacy:** Personal information stays private, especially in group chats

## Tool Preferences
- **Note-taking:** [To be filled]
- **Task management:** [To be filled]
- **Calendar:** [To be filled]

---
*Last updated: 2026-02-01*
```

### 3.6 Daily Notes Format

```markdown
# 2026-02-01 — Daily Log

## Summary
Brief overview of the day's activities.

## Conversations
### Morning Session (09:00-10:30 HKT)
- Discussed model configuration
- Fixed Qwen OAuth authentication
- Updated fallback chain

### Evening Session (20:00-21:00 HKT)
- Reviewed Nat Eliason's memory vault article
- Created implementation plan for vault system

## Entities Mentioned
- [[people/guillermo]] — main user
- [[projects/openclaw-setup]] — ongoing setup work
- [[resources/ai-models]] — model configuration

## Facts Extracted
<!-- For heartbeat processing -->
- guillermo: "Has Claude Max subscription" [context, high confidence]
- openclaw-setup: "Fixed Qwen OAuth Feb 1 2026" [milestone, high confidence]

## Decisions Made
- Will implement PARA-based memory vault
- Obsidian for human interface, plain markdown for agent interface
- QMD for search layer

## Action Items
- [ ] Create vault directory structure
- [ ] Export ChatGPT/Claude/Grok history
- [ ] Process exports into entities

---
*Auto-generated sections will be marked*
```

---

## Part 4: QMD Integration

### 4.1 Why QMD

QMD provides search capabilities beyond basic text search:

| Feature | Basic Search | QMD |
|---------|--------------|-----|
| Keyword search | ✅ grep/ripgrep | ✅ BM25 (better ranking) |
| Semantic search | ❌ No | ✅ Vector embeddings |
| Query expansion | ❌ No | ✅ LLM variations |
| Re-ranking | ❌ No | ✅ LLM confidence scoring |
| Combined search | ❌ No | ✅ Hybrid fusion |

### 4.2 Resource Requirements

| Component | Size | RAM Needed |
|-----------|------|------------|
| Embeddings model | ~300MB | ~500MB |
| Re-ranker model | ~640MB | ~800MB |
| Query expansion | ~1.1GB | ~1.5GB |
| **Total** | **~2GB disk** | **~3GB RAM** |

### 4.3 Installation Strategy

**Option A: Install on Railway (Recommended if resources allow)**
```bash
# Check available resources
free -h
df -h

# Install Bun
curl -fsSL https://bun.sh/install | bash

# Install QMD
bun install -g https://github.com/tobi/qmd
```

**Option B: Run QMD locally on your machine**
- Install on your laptop/desktop
- Sync vault via Git
- Use for manual deep searches
- Agent uses OpenClaw's memory_search for basic queries

**Option C: Hybrid (Start simple, add later)**
- Start with OpenClaw's Gemini-based memory_search
- Add QMD when search becomes a bottleneck

### 4.4 QMD Configuration

```bash
# Create collections mapping to our three layers
qmd collection add /data/vault/life --name knowledge --mask "**/*.md"
qmd collection add /data/vault/daily --name daily --mask "**/*.md"
qmd collection add /data/workspace --name workspace --mask "*.md"

# Add context descriptions
qmd context add qmd://knowledge "Knowledge graph: people, companies, projects"
qmd context add qmd://daily "Daily notes and conversation logs"
qmd context add qmd://workspace "Agent workspace, tacit knowledge, config"

# Generate embeddings (takes a while first time)
qmd embed

# Verify setup
qmd status
```

### 4.5 QMD Commands Reference

```bash
# Fast keyword search
qmd search "Jane's role at Acme" -c knowledge

# Semantic search (finds related concepts)
qmd vsearch "how we decided on model architecture" -c knowledge

# Hybrid search with re-ranking (best quality)
qmd query "when did we last discuss investment thesis" 

# Get specific document
qmd get "life/areas/people/jane/summary.md"

# Get by doc ID (from search results)
qmd get "#abc123"

# Output for agent processing
qmd query "project status" --json -n 10

# Update index after changes
qmd update
qmd embed
```

### 4.6 Integration with Molty

**Option 1: Direct exec (current approach)**
```python
# In conversation, when needing to search vault:
result = exec("qmd query 'investment decisions 2024' --json -n 5")
parse_and_use(result)
```

**Option 2: Create a skill**
```markdown
# /data/workspace/skills/vault-search/SKILL.md

## Description
Search the memory vault using QMD.

## Usage
When you need to recall something from the vault:
1. Use `qmd search` for keyword matching
2. Use `qmd vsearch` for semantic similarity
3. Use `qmd query` for best results (combines both)

## Commands
qmd search "<query>" -c knowledge  # Search knowledge graph
qmd search "<query>" -c daily      # Search daily notes
qmd query "<query>" --json -n 10   # Hybrid search, JSON output
```

**Option 3: MCP Server (Advanced)**
QMD exposes an MCP server for tighter integration with Claude-based agents.

---

## Part 5: Automated Processes

### 5.1 Heartbeat Enhancement

**Current:** Check emails, calendar, etc.  
**Enhanced:** Also extract facts from recent conversations.

```markdown
# HEARTBEAT.md additions

## Memory Extraction (every heartbeat)
1. Review conversations since last heartbeat
2. Identify new facts about entities
3. Create/update entity folders if needed
4. Update items.json with new facts
5. Write to daily notes
6. Update QMD index
```

### 5.2 Weekly Synthesis (Cron Job)

Every Sunday at midnight HKT:

```bash
# Pseudocode for weekly synthesis

for each entity in /data/vault/life/**/items.json:
    facts = load_facts(entity)
    active_facts = facts.filter(status == "active")
    
    # Sort by tier
    hot = active_facts.filter(lastAccessed > now - 7 days)
    warm = active_facts.filter(lastAccessed > now - 30 days AND not hot)
    cold = active_facts.filter(lastAccessed <= now - 30 days)
    
    # Within tier, sort by accessCount
    hot.sort_by(accessCount, descending)
    warm.sort_by(accessCount, descending)
    
    # Rewrite summary.md
    summary = generate_summary(entity, hot, warm)
    write(entity/summary.md, summary)
    
    log(f"Synthesized {entity}: {len(hot)} hot, {len(warm)} warm, {len(cold)} cold")
```

### 5.3 Index Maintenance

```bash
# Daily (via heartbeat or cron)
qmd update  # Re-index changed files

# Weekly (after synthesis)
qmd embed   # Regenerate embeddings for changed content
```

---

## Part 6: Processing Historical Exports

### 6.1 Export Procedures

**ChatGPT:**
1. Go to Settings → Data Controls → Export Data
2. Wait for email with download link
3. Download ZIP, extract `conversations.json`
4. Place in `/data/vault/imports/chatgpt/`

**Claude:**
1. Account Settings → Export Conversations
2. Download and extract
3. Place in `/data/vault/imports/claude/`

**Grok:**
1. Settings → Privacy & Data → Download Your Data
2. Download and extract
3. Place in `/data/vault/imports/grok/`

### 6.2 Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPORT PIPELINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Raw Export (JSON)                                              │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────┐                                           │
│  │ Parse & Chunk   │  Split into individual conversations      │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Entity Extract  │  Use LLM to identify people, companies,   │
│  │                 │  projects mentioned                        │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Fact Extract    │  Use LLM to extract atomic facts          │
│  │                 │  with categories and relationships        │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Deduplication   │  Merge similar facts, identify superseded │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Write to Vault  │  Create entities, write items.json,       │
│  │                 │  generate initial summaries               │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Index           │  Update QMD index                         │
│  └─────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Processing Script

I'll create a script that:
1. Reads conversation exports
2. Uses an LLM (Qwen for cost efficiency) to extract entities and facts
3. Creates entity folders and populates them
4. Generates initial summaries
5. Handles deduplication and relationship linking

**Location:** `/data/workspace/scripts/process-ai-exports.js`

---

## Part 7: Sync Strategy

### 7.1 Git-Based Sync (Recommended)

```bash
# On Railway - initialize vault repo
cd /data/vault
git init
git add .
git commit -m "Initial vault structure"
git remote add origin git@github.com:gginesta/memory-vault.git  # private repo
git push -u origin main

# On your laptop - clone vault
git clone git@github.com:gginesta/memory-vault.git ~/vault

# Open in Obsidian
# File > Open vault > ~/vault
```

**Sync workflow:**
- Railway auto-commits after heartbeat updates
- You pull changes when opening Obsidian
- You push changes after manual edits
- Conflict resolution: agent changes take precedence for items.json, human changes for summary.md

### 7.2 Syncthing Alternative

If Git feels too manual:
1. Add vault to Syncthing folders (we already planned this!)
2. Syncs automatically in real-time
3. Conflict handling built-in

### 7.3 Obsidian Git Plugin

Automates Git operations from within Obsidian:
- Auto-pull on open
- Auto-commit/push on close
- Commit interval (e.g., every 10 minutes)

---

## Part 8: Implementation Phases

### Phase 0: Preparation (Now)
**Duration:** 30 minutes

- [x] Study Nate's article ✓
- [x] Create implementation plan ✓
- [ ] Guillermo exports AI conversation history
- [ ] Decide: Install QMD now or later?

### Phase 1: Foundation (Today/Tomorrow)
**Duration:** 2-3 hours

- [ ] Create `/data/vault/` directory structure
- [ ] Create template files (`_template/` folders)
- [ ] Create initial entities:
  - [ ] `areas/people/guillermo/`
  - [ ] `projects/openclaw-setup/`
  - [ ] `projects/cerebro/`
  - [ ] `projects/brinc/`
- [ ] Migrate relevant content from MEMORY.md
- [ ] Create `tacit.md` from USER.md + SOUL.md
- [ ] Initialize Git repo for vault

### Phase 2: Historical Import (This Week)
**Duration:** 4-6 hours (mostly automated)

- [ ] Receive exports from Guillermo
- [ ] Create processing script
- [ ] Run extraction pipeline
- [ ] Review and refine extracted entities
- [ ] Generate initial summaries
- [ ] Create relationship links between entities

### Phase 3: Search Layer (This Week)
**Duration:** 1-2 hours

- [ ] Evaluate Railway resources for QMD
- [ ] Install QMD (or plan local installation)
- [ ] Configure collections
- [ ] Generate embeddings
- [ ] Test search functionality
- [ ] Create vault-search skill

### Phase 4: Automation (Next Week)
**Duration:** 2-3 hours

- [ ] Enhance heartbeat for fact extraction
- [ ] Implement access tracking (bump counts on use)
- [ ] Create weekly synthesis cron job
- [ ] Test decay mechanics
- [ ] Create index maintenance cron

### Phase 5: Human Interface (Next Week)
**Duration:** 1-2 hours

- [ ] Set up Git sync to your devices
- [ ] Configure Obsidian on your laptop
- [ ] Install recommended plugins
- [ ] Configure graph view
- [ ] Test round-trip editing

### Phase 6: Project Lead Integration (When Ready)
**Duration:** 2-3 hours per lead

- [ ] Define access patterns for each lead
- [ ] Create project-specific views
- [ ] Set up cross-referencing
- [ ] Test context isolation

---

## Part 9: Success Metrics

### Short-term (1 week)
- [ ] Vault structure created
- [ ] 50+ entities populated from exports
- [ ] Search returns relevant results
- [ ] Daily notes integrated

### Medium-term (1 month)
- [ ] 200+ facts in knowledge graph
- [ ] Decay mechanics working (hot/warm/cold visible)
- [ ] Heartbeat extracting facts automatically
- [ ] You can browse vault in Obsidian

### Long-term (3 months)
- [ ] All project leads have vault access
- [ ] Cross-referencing working across leads
- [ ] Memory feels "real" — agents recall context naturally
- [ ] Search finds anything in seconds
- [ ] Facts evolve (supersession working)

---

## Part 10: Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **QMD too heavy for Railway** | Medium | Medium | Fall back to memory_search; run QMD locally |
| **Export processing misses facts** | Medium | Low | Manual review; iterative refinement |
| **Sync conflicts** | Low | Medium | Clear merge rules; backup before sync |
| **Vault grows too large** | Low | Medium | Archive aggressively; prune cold facts |
| **Schema needs changes** | Medium | Medium | Version the schema; migration scripts |

---

## Part 11: Commands Quick Reference

### Vault Management
```bash
# Create new entity
mkdir -p /data/vault/life/areas/people/[name]
cp /data/vault/life/areas/people/_template/* /data/vault/life/areas/people/[name]/

# Move to archives
mv /data/vault/life/projects/[name] /data/vault/life/archives/projects/

# Sync vault
cd /data/vault && git add . && git commit -m "Update" && git push
```

### QMD Operations
```bash
# Search
qmd search "query" -c knowledge
qmd vsearch "semantic query" -c knowledge  
qmd query "complex query" --json -n 10

# Maintenance
qmd update                    # Re-index files
qmd embed                     # Regenerate embeddings
qmd status                    # Check health

# Retrieval
qmd get "path/to/file.md"     # Get document
qmd get "#docid"              # Get by ID
```

### Weekly Tasks
```bash
# Run synthesis
/data/workspace/scripts/weekly-synthesis.sh

# Backup
cd /data/vault && git add . && git commit -m "Weekly sync" && git push
```

---

## Part 12: Next Action

**Guillermo, your move:**

1. **Export your data now:**
   - ChatGPT: Settings → Data Controls → Export
   - Claude: Account Settings → Export
   - Grok: Settings → Download Data

2. **Tell me:** Install QMD on Railway now, or start with native memory_search?

3. **Confirm:** Private GitHub repo for vault sync? (`gginesta/memory-vault`)

Once I have your go-ahead, I'll start building the foundation immediately.

---

*This plan is the blueprint. Let's build something great.* 🦎
