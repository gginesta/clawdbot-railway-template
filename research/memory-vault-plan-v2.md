# Memory Vault System — Implementation Plan v2

**Based on Nat Eliason's PARA + Atomic Facts Architecture**  
*Created: February 1, 2026*

---

## Executive Summary

This plan implements a three-layer memory system for Molty and future project leads, based on Nat Eliason's architecture:

1. **Knowledge Graph (PARA)** — Entities and facts in structured directories
2. **Daily Notes** — Raw timeline of events
3. **Tacit Knowledge** — User patterns and preferences

Key innovations:
- **Atomic facts with schema** — Structured JSON with access tracking
- **Memory decay** — Hot/Warm/Cold tiers based on recency
- **No-deletion rule** — Facts superseded, never deleted
- **Tiered retrieval** — Summary first, full facts only when needed
- **Automated extraction** — Heartbeat process mines conversations

---

## 1. The Three-Layer Architecture

### Layer 1: Knowledge Graph (PARA)

```
/data/vault/life/
├── projects/                    # Active work with goals/deadlines
│   └── <project-name>/
│       ├── summary.md           # Concise overview (loaded first)
│       └── items.json           # Atomic facts (loaded when needed)
│
├── areas/                       # Ongoing responsibilities (no end date)
│   ├── people/
│   │   └── <person-name>/
│   │       ├── summary.md
│   │       └── items.json
│   ├── companies/
│   │   └── <company-name>/
│   │       ├── summary.md
│   │       └── items.json
│   └── roles/
│       └── <role-name>/
│
├── resources/                   # Topics of interest, reference material
│   └── <topic>/
│       ├── summary.md
│       └── items.json
│
├── archives/                    # Inactive items from above
│   ├── projects/
│   ├── people/
│   └── companies/
│
├── index.md                     # Master index of all entities
└── README.md                    # System documentation
```

### Layer 2: Daily Notes

```
/data/workspace/memory/
├── 2026-01-31.md               # Raw timeline of events
├── 2026-02-01.md
└── ...
```

*We already have this!* Our existing `memory/YYYY-MM-DD.md` files serve this purpose.

### Layer 3: Tacit Knowledge

```
/data/workspace/tacit.md        # User patterns and preferences
```

Content includes:
- Communication preferences (tools, formats, verbosity)
- Working style patterns (brainstorming, decisions, management)
- Tool preferences and workflows
- Rules and boundaries

*Our existing `USER.md` and `SOUL.md` partially serve this purpose.*

---

## 2. The Atomic Fact Schema

Every fact in `items.json` follows this structure:

```json
{
  "id": "person-guillermo-001",
  "fact": "Lives in Hong Kong, timezone GMT+8",
  "category": "context",
  "timestamp": "2026-01-31",
  "source": "2026-01-31",
  "status": "active",
  "supersededBy": null,
  "relatedEntities": ["areas/people/guillermo"],
  "lastAccessed": "2026-02-01",
  "accessCount": 15
}
```

### Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `relationship` | How entities connect | "Reports to Jane", "Investor in Acme" |
| `milestone` | Significant events | "Joined company March 2025" |
| `status` | Current state | "Project on hold", "Active investor" |
| `preference` | How they like things | "Prefers async comms", "No calls before 10am" |
| `context` | Background info | "Based in Hong Kong", "Technical background" |

### Status Values

| Status | Meaning |
|--------|---------|
| `active` | Current, valid fact |
| `superseded` | Outdated, replaced by another fact |

### The No-Deletion Rule

**Critical:** Facts are NEVER deleted. When something changes:

1. Old fact gets `status: "superseded"`
2. Old fact gets `supersededBy: "<new-fact-id>"`
3. New fact is created with `status: "active"`

This preserves complete history — you can trace how relationships evolved.

---

## 3. Memory Decay System

### Recency Tiers

| Tier | Criteria | Treatment |
|------|----------|-----------|
| **Hot** | Accessed in last 7 days | Prominently in summary.md |
| **Warm** | Accessed 8-30 days ago | Included at lower priority |
| **Cold** | Not accessed in 30+ days | Omitted from summary, kept in items.json |

### Access Tracking

Every time a fact is used:
1. `accessCount` increments
2. `lastAccessed` updates to today

### Frequency Resistance

Facts with high `accessCount` resist decay. A frequently-referenced fact stays warm even if skipped for a few weeks.

### Weekly Synthesis

Every week, `summary.md` files are rewritten:

1. Load all active facts from `items.json`
2. Sort by tier: Hot → Warm → Cold
3. Within tier, sort by `accessCount` (descending)
4. Write Hot and Warm facts to `summary.md`
5. Cold facts stay in `items.json` only

---

## 4. Automated Extraction (Heartbeats)

### What the Heartbeat Does

Periodic background task that:

1. **Scans recent conversations** for new information
2. **Extracts durable facts:**
   - Relationships mentioned
   - Status changes
   - Milestones/achievements
   - Decisions made
   - Preferences expressed
3. **Writes facts** to appropriate entity in knowledge graph
4. **Updates daily notes** with timeline entries
5. **Bumps access metadata** on any facts referenced

### What Gets Skipped

- Casual chat
- Transient requests
- Information already captured

### Entity Creation Heuristics

Create a new entity if:
- Mentioned 3+ times, OR
- Has direct relationship to Guillermo, OR
- Is a significant project/company

Otherwise → just capture in daily notes.

---

## 5. Tiered Retrieval

### The Problem
Loading entire knowledge base = blown context window.

### The Solution

```
Query arrives
    ↓
Load relevant summary.md files
    ↓
Usually enough! Most conversations need only summaries.
    ↓
If more detail needed → load specific items.json
    ↓
If searching for something → use QMD search layer
```

### QMD Integration

QMD collections map to our three layers:

```bash
# Knowledge graph
qmd collection add /data/vault/life --name life --mask "**/*.md"

# Daily notes
qmd collection add /data/workspace/memory --name memory --mask "**/*.md"

# Tacit knowledge + workspace
qmd collection add /data/workspace --name workspace --mask "*.md"
```

Search modes:
- `qmd search "query"` — keyword (BM25)
- `qmd vsearch "query"` — semantic
- `qmd query "query"` — combined with reranking

---

## 6. Initial Entity Setup

### For Guillermo

**Path:** `/data/vault/life/areas/people/guillermo/`

**summary.md:**
```markdown
# Guillermo Ginesta

## Quick Context
- Location: Hong Kong (GMT+8)
- Telegram: @gginesta
- Working style: Curious, learns fast, enjoys troubleshooting
- Communication: Casual + friendly, but efficient. No fluff.

## Current Focus
- Setting up multi-agent AI system (TMNT project)
- Projects: Cerebro (venture), Brinc (corporate), Mana Capital (investment)

## Key Relationships
- Molty (AI assistant, coordinator)
- [Other key people to be added]

## Recent Activity
[Updated weekly from Hot facts]
```

**items.json:**
```json
{
  "entity": "areas/people/guillermo",
  "facts": [
    {
      "id": "guillermo-001",
      "fact": "Lives in Hong Kong, timezone GMT+8 (HKT)",
      "category": "context",
      "timestamp": "2026-01-31",
      "source": "2026-01-31",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": [],
      "lastAccessed": "2026-02-01",
      "accessCount": 5
    },
    {
      "id": "guillermo-002",
      "fact": "Telegram username is @gginesta, ID 1097408992",
      "category": "context",
      "timestamp": "2026-01-31",
      "source": "2026-01-31",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": [],
      "lastAccessed": "2026-02-01",
      "accessCount": 3
    },
    {
      "id": "guillermo-003",
      "fact": "Prefers casual + friendly communication but efficient, no fluff",
      "category": "preference",
      "timestamp": "2026-01-31",
      "source": "2026-01-31",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": [],
      "lastAccessed": "2026-02-01",
      "accessCount": 4
    },
    {
      "id": "guillermo-004",
      "fact": "Has Claude Max subscription",
      "category": "context",
      "timestamp": "2026-02-01",
      "source": "2026-02-01",
      "status": "active",
      "supersededBy": null,
      "relatedEntities": [],
      "lastAccessed": "2026-02-01",
      "accessCount": 1
    }
  ]
}
```

### Starter Entities to Create

| Type | Entity | Priority |
|------|--------|----------|
| Person | guillermo | High |
| Person | molty | High |
| Project | cerebro | Medium |
| Project | brinc | Medium |
| Project | openclaw-setup | High |
| Company | [Guillermo's companies] | Medium |
| Resource | ai-models | Medium |
| Resource | memory-systems | Medium |

---

## 7. Integration with Existing OpenClaw Setup

### What We Keep

| Current | Maps To | Notes |
|---------|---------|-------|
| `MEMORY.md` | → `tacit.md` + entity summaries | Restructure content |
| `memory/YYYY-MM-DD.md` | → Layer 2 (Daily Notes) | Already perfect! |
| `USER.md` | → Part of tacit.md | Merge in |
| `SOUL.md` | → Part of tacit.md | Merge in |
| `memory_search` | → Enhanced with vault paths | Add new paths |

### New Components

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `/data/vault/life/` | Knowledge Graph | Create directories |
| `items.json` files | Atomic facts | Per-entity JSON |
| `summary.md` files | Quick context | Per-entity markdown |
| `tacit.md` | Patterns & preferences | New consolidated file |
| Heartbeat extraction | Auto-mine conversations | Enhance existing heartbeat |
| Weekly synthesis | Rewrite summaries | Cron job or manual |
| QMD (optional) | Advanced search | Install if needed |

### Memory Search Enhancement

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "gemini",
        "extraPaths": [
          "/data/vault/life/projects",
          "/data/vault/life/areas",
          "/data/vault/life/resources"
        ]
      }
    }
  }
}
```

---

## 8. Processing Historical Data

### ChatGPT Export

1. Export from Settings → Data Controls → Export Data
2. Parse `conversations.json`
3. For each conversation:
   - Extract entities mentioned (people, companies, projects)
   - Extract facts about those entities
   - Create/update entity folders
   - Add facts to items.json with source = conversation date
4. Create summary.md files

### Claude Export

1. Export conversations
2. Same processing as ChatGPT
3. Pay special attention to Claude Projects — they may map directly to our Projects

### Grok Export

1. Export from Settings
2. Same processing
3. Note: Grok conversations may have more real-time context

### Processing Script Structure

```javascript
// parse-export.js (pseudocode)

async function processExport(exportPath, platform) {
  const conversations = await parseExport(exportPath, platform);
  
  for (const convo of conversations) {
    const entities = extractEntities(convo);
    const facts = extractFacts(convo, entities);
    
    for (const entity of entities) {
      await ensureEntityFolder(entity);
      await appendFacts(entity, facts.filter(f => f.entity === entity.id));
    }
    
    await writeDailyNote(convo.date, summarize(convo));
  }
}

function extractEntities(conversation) {
  // Use LLM to identify:
  // - People mentioned (3+ times or significant)
  // - Companies mentioned
  // - Projects discussed
  // Return list with type and name
}

function extractFacts(conversation, entities) {
  // Use LLM to extract:
  // - Relationships between entities
  // - Status changes
  // - Milestones/decisions
  // - Preferences expressed
  // Return list of atomic facts with schema
}
```

---

## 9. Implementation Phases

### Phase 1: Foundation (This Session)
- [x] Understand the architecture (done!)
- [ ] Create directory structure
- [ ] Create initial entities (Guillermo, key projects)
- [ ] Migrate relevant MEMORY.md content

### Phase 2: Historical Import (This Week)
- [ ] Guillermo exports ChatGPT, Claude, Grok data
- [ ] Build/run processing scripts
- [ ] Create entities for frequently mentioned people/companies
- [ ] Populate items.json files

### Phase 3: Integration (Next Week)
- [ ] Enhance memory_search with vault paths
- [ ] Update heartbeat to extract facts from conversations
- [ ] Create tacit.md from USER.md + SOUL.md
- [ ] Test retrieval in real conversations

### Phase 4: Automation (Week 3)
- [ ] Implement access tracking (bump lastAccessed/accessCount)
- [ ] Implement weekly synthesis (rewrite summaries)
- [ ] Consider installing QMD for advanced search
- [ ] Document the system

### Phase 5: Project Leads (When Ready)
- [ ] Each lead gets access to relevant vault sections
- [ ] Cross-referencing between lead contexts
- [ ] Shared entities (Guillermo) vs. project-specific

---

## 10. Example Workflow

### Scenario: Guillermo mentions "Jane from Acme"

**Step 1: During Conversation**
- I note that Jane at Acme was mentioned
- I check if `/data/vault/life/areas/people/jane/` exists

**Step 2: If Entity Exists**
- Load `summary.md` for quick context
- If more detail needed, load `items.json`
- Bump `lastAccessed` and `accessCount` on any facts used

**Step 3: If Entity Doesn't Exist**
- Note in daily log: "Jane from Acme mentioned"
- If mentioned 3+ times or significant, create entity folder

**Step 4: After Conversation (Heartbeat)**
- Scan conversation for durable facts
- Extract: "Jane is CTO at Acme" → add to items.json
- Update daily note with timeline entry

**Step 5: Weekly Synthesis**
- Jane's facts sorted by recency/frequency
- Hot facts written to summary.md
- Cold facts remain in items.json only

---

## 11. Questions Resolved

Based on Nate's article:

| Question | Answer |
|----------|--------|
| Use qmd? | **Yes**, as optional search layer (install later) |
| Delete old facts? | **No** — supersede, never delete |
| How often update summaries? | **Weekly** synthesis |
| What triggers entity creation? | **3+ mentions** OR significant relationship |
| Where do AI exports go? | **Processed into entities**, not stored raw |

---

## 12. Next Steps (Immediate)

1. **Create the vault structure now**
2. **Create Guillermo's entity** as first test
3. **Create a few project entities** (Cerebro, Brinc, OpenClaw-setup)
4. **Migrate MEMORY.md content** into appropriate entities
5. **You export your AI conversation history** — I'll help process

Ready to start building? 🦎
