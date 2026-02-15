# ClawVault-Inspired Memory Upgrade Plan for TMNT Squad

*Created: 2026-02-15 | Author: Molty (Systems Architecture Sub-Agent)*
*Status: DRAFT — Pending Guillermo review*

---

## Executive Summary

ClawVault introduces five patterns that would materially improve TMNT memory quality: **memory typing**, **wiki-links**, **vault index**, **priority-based context loading**, and **priority-aware compaction**. However, installing the `clawvault` npm package is **not recommended** — we should adopt their patterns into our existing stack. This plan describes exactly how, in three phases.

---

## Build vs. Install Decision

### Recommendation: **Adopt patterns. Don't install the package.**

| Factor | Install `clawvault` | Adopt Patterns |
|--------|---------------------|----------------|
| Multi-agent (Syncthing) | ❌ Not supported (uses Tailscale) | ✅ Works with existing sync |
| QMD integration | Uses qmd underneath | Already have QMD |
| Migration risk | 🔴 Full restructure (new vault layout) | 🟢 Incremental, backward-compatible |
| Cron compatibility | 🔴 Conflicts with our compaction/guardrails | 🟢 Extends existing crons |
| OpenClaw hook | Available but opinionated | Not needed — we have AGENTS.md boot |
| Task management | Included (but we use Todoist+Notion) | Skip — we don't need this |
| Obsidian dashboards | Nice but we don't use Obsidian daily | Skip — low value for us |
| Maintenance burden | External dependency, breaking changes | Our code, our rules |
| Time to value | ~1 week (migration + debugging) | Phase 1 in 1-2 days |

**Key reasons:**
1. **We already use QMD** — ClawVault's search is just a wrapper around qmd, which we already have.
2. **Multi-agent is non-negotiable** — ClawVault uses Tailscale for multi-vault; we use Syncthing shared folders. Ripping that out would be destructive.
3. **Our crons are more mature** — ClawVault's compaction is LLM-based on-demand; ours is automated and guardrailed. We'd lose reliability.
4. **We already have task management** — Todoist + Notion standup. ClawVault's task system would be a redundant third system.
5. **The value is in the patterns, not the CLI** — Memory typing, wiki-links, priority tagging, and budget-aware loading are all concepts we can implement in pure markdown without another dependency.

---

## Phase 1: Quick Wins (1-2 Days)

### 1.1 — Add YAML Frontmatter to Daily Logs

**What changes:** Daily log entries get inline type tags for important items.

**Current format:**
```markdown
## Sub-Agent Roster Consolidation
**Context:** Guillermo wants unified sub-agent standard...
```

**New format:**
```markdown
## Sub-Agent Roster Consolidation
<!-- type: decision | priority: P1 -->
**Context:** Guillermo wants unified sub-agent standard...
```

We use HTML comments instead of YAML frontmatter blocks because:
- Daily logs have multiple entries per file (YAML frontmatter only works at file top)
- HTML comments are invisible in rendered markdown
- QMD still indexes the content
- No parsing changes needed

**Tag vocabulary (keep it small):**

| Type | Use When | Example |
|------|----------|---------|
| `decision` | A choice was made with reasoning | "Use PostgreSQL for JSONB support" |
| `preference` | User/agent preference noted | "Guillermo prefers tables over bullets" |
| `relationship` | Info about a person/entity | "Pedro from Versatly built ClawVault" |
| `commitment` | Promise or deadline | "Will deploy Leonardo by Friday" |
| `lesson` | Something learned the hard way | "Always backup before Railway update" |
| `update` | Status update (default) | "Pushed config to Railway" |

**Priority vocabulary:**

| Priority | Criteria | Context Loading |
|----------|----------|-----------------|
| `P1` | Decisions, commitments, blockers, errors | Always loaded on wake |
| `P2` | Preferences, insights, relationships, architecture | Loaded if context budget allows |
| `P3` | Routine updates, status reports | Only loaded via search |

**Migration path:** No migration needed. Start tagging new entries today. Old entries remain untagged (treated as `update | P3` by default).

**Agent instruction addition** (append to AGENTS.md Memory section):
```markdown
### Entry Tagging
- Tag important entries: `<!-- type: decision | priority: P1 -->`
- Types: decision, preference, relationship, commitment, lesson, update
- Priorities: P1 (critical), P2 (important), P3 (routine)
- When in doubt: don't tag. Untagged = update/P3.
- Only tag ~20-30% of entries. Over-tagging defeats the purpose.
```

**Risk:** Low. HTML comments are inert. Worst case: agents forget to tag sometimes (fine — we tag what matters, not everything).

**Impact:** Enables Phase 2 priority-aware compaction. Immediately makes daily logs more scannable for humans.

---

### 1.2 — Add Wiki-Links for Entity Cross-References

**What changes:** When mentioning people, projects, or agents in daily logs and MEMORY.md, wrap in `[[double brackets]]`.

**Current:**
```markdown
Discussed with Pedro from Versatly about ClawVault integration.
Leonardo's primary model changed to GPT-5.2.
```

**New:**
```markdown
Discussed with [[Pedro]] from [[Versatly]] about [[ClawVault]] integration.
[[Leonardo]]'s primary model changed to GPT-5.2.
```

**Rules:**
- Use for: people, companies, projects, agents, tools, significant concepts
- Don't use for: common words, generic terms, one-off mentions
- Prefer canonical names: `[[Leonardo]]` not `[[Leo]]`, `[[Guillermo]]` not `[[G]]`
- No need to create target files — links are for searchability, not navigation (we're not Obsidian)

**Why this works without Obsidian:** QMD indexes `[[entity]]` as a searchable term. Searching `[[Leonardo]]` returns every file that mentions Leonardo in a cross-reference context, filtering out noise. It's a cheap knowledge graph via search.

**Migration path:** No migration of old files. Start using in new entries. Optionally backfill MEMORY.md during a quiet heartbeat (it's small enough to do manually).

**Agent instruction addition:**
```markdown
### Cross-References
- Wrap notable entities in wiki-links: `[[Person]]`, `[[Project]]`, `[[Tool]]`
- Use canonical names (full, consistent spelling)
- Enables entity-based search: `memory_search("[[Leonardo]]")`
```

**Risk:** Very low. Wiki-links in plain markdown are just text with brackets. No tooling changes.

**Impact:** Enables entity-based queries ("what do I know about [[Pedro]]?"). Creates implicit knowledge graph. Makes memory search more precise.

---

### 1.3 — Create VAULT_INDEX.md

**What changes:** New file at `/data/workspace/VAULT_INDEX.md` listing all memory-related files with one-line descriptions.

**Format:**
```markdown
# VAULT_INDEX.md — Memory File Registry

*Auto-updated by compaction cron. Manual edits welcome.*
*Last updated: 2026-02-15*

## Core Files
| File | Description |
|------|-------------|
| `MEMORY.md` | Long-term curated memory (people, infra, lessons) |
| `SOUL.md` | Agent identity and personality |
| `USER.md` | User profile and preferences |
| `AGENTS.md` | Session boot instructions and workspace rules |
| `PRIORITY_BRIEFING.md` | Current priorities surfaced on first user message |
| `TOOLS.md` | Tool notes, Discord channels, credentials |

## Daily Logs
| File | Description |
|------|-------------|
| `memory/2026-02-15.md` | Sub-agent roster consolidation, Leonardo model config, CODEX framework, ClawVault analysis |
| `memory/2026-02-14.md` | ... |

## Reference Docs
| File | Description |
|------|-------------|
| `memory/refs/clawvault-analysis.md` | ClawVault article analysis and adoption notes |
| `memory/refs/...` | ... |

## Shared Memory Vault
| Folder | Description |
|--------|-------------|
| `shared/memory-vault/knowledge/` | Cross-agent knowledge base |
| `shared/memory-vault/projects/` | Project-specific memory |
| `shared/memory-vault/people/` | People dossiers |
```

**Why this complements QMD (not replaces it):**
- Vault index answers "what files exist?" (orientation) — fast, no search needed
- QMD answers "what do I know about X?" (retrieval) — deep, content-aware
- Reading the index on wake gives instant orientation without burning context on full file reads

**Auto-update mechanism:** The existing 11PM compaction cron appends a step: after compaction, regenerate the daily logs section of VAULT_INDEX.md by listing files in `memory/` with their first H2 headings as descriptions.

**Migration path:** Create the file now (manually). Add auto-update to compaction cron in Phase 2.

**Risk:** Low. It's just a new file. Risk of going stale — mitigated by cron auto-update in Phase 2.

**Impact:** Faster orientation on wake. Reduces unnecessary file reads. Useful for sub-agents that need to know what's available.

---

### 1.4 — Add Priority Section to MEMORY.md

**What changes:** Add a "P1 Active Context" section at the top of MEMORY.md, before the Guillermo section.

**Format:**
```markdown
# MEMORY.md - Long-Term Memory

*Last updated: 2026-02-15*

---

## 🔴 P1 — Active Context (Always Load)

- **Email broken** until Feb 19 (OAuth client disabled, Guillermo has 2FA phone)
- **Guillermo traveling** — Cebu Feb 13-18, back HK Feb 19
- **Sub-Agent Standard v1.0** published — all squad leads should follow it
- **Calendar blocked** — no time-blocking until Google auth restored
- **gogcli** installed, auth pending (could unblock Calendar+Gmail early)

---

## 👤 Guillermo
...
```

**Rules for P1 section:**
- Maximum 10 items (ruthlessly curated)
- Only: active blockers, in-flight decisions, current-week commitments, recent critical changes
- Review and prune weekly (or during heartbeat)
- Items graduate to appropriate MEMORY.md sections or get removed when resolved

**Migration path:** Add the section now. Populate from current context. Takes 5 minutes.

**Risk:** None. It's a new section in an existing file.

**Impact:** Most critical context is always at the top of the most-read file. Agents see blockers and active commitments immediately on wake.

---

## Phase 2: Structural Improvements (1 Week)

### 2.1 — Priority-Aware Daily Compaction

**What changes:** The 11PM compaction cron becomes priority-aware instead of purely size-based.

**Current behavior:** If daily log > 10KB, archive the raw file to `memory/archive/` and create a summary.

**New behavior:**

```
COMPACTION LOGIC (pseudocode):

1. Parse daily log for tagged entries
2. Extract all P1 and P2 entries (preserve full text)
3. Summarize P3/untagged entries (compress to bullets)
4. Build compacted file:
   - H1: Date
   - H2: Key Decisions & Commitments (P1 entries, full text)
   - H2: Insights & Preferences (P2 entries, full text)
   - H2: Activity Summary (P3/untagged, compressed bullets)
5. If compacted file > 10KB, further compress P3 section
6. Archive raw log to memory/archive/ (always keep original)
7. Replace daily log with compacted version
```

**Implementation:** Modify the existing compaction cron script. The tag parsing is simple regex:

```bash
# Extract priority from HTML comments
grep -oP '<!-- type: \K[^|]+(?=\s*\|)' memory/2026-02-15.md    # types
grep -oP 'priority: \K\w+' memory/2026-02-15.md                  # priorities
```

For the actual summarization of P3 content, use a sub-agent (Qwen Coder or Flash — cheap models):
```
Prompt: "Compress the following daily log entries into bullet points. 
Preserve all names, numbers, and specific details. Remove conversational filler.
Target: 30% of original length."
```

**Migration path:** 
1. Update compaction script with new logic
2. Old untagged logs compact same as before (all treated as P3 → full compression)
3. New tagged logs get priority-aware treatment

**Integration with QMD:** Compacted files retain all P1/P2 text verbatim, so QMD search quality stays the same or improves (less noise from verbose P3 entries).

**Integration with Syncthing:** No change — compacted files sync like any other markdown file.

**Risk:** Medium. LLM-based compression could lose details. **Mitigation:** Always archive raw logs. The raw file is the source of truth; compacted version is the working copy.

**Impact:** High. P1/P2 entries survive compaction intact. Weekly review of archived decisions becomes possible. "Show me all decisions from this week" works by grepping P1 tags.

---

### 2.2 — VAULT_INDEX.md Auto-Generation

**What changes:** Add auto-update step to the 11PM compaction cron.

**Script pseudocode:**
```bash
#!/bin/bash
# vault-index-update.sh — Run after daily compaction

INDEX="/data/workspace/VAULT_INDEX.md"

cat > "$INDEX" << 'HEADER'
# VAULT_INDEX.md — Memory File Registry

*Auto-generated by compaction cron. Manual edits to Core/Refs sections preserved.*
*Last updated: $(date +%Y-%m-%d)*

## Core Files
| File | Description |
|------|-------------|
| `MEMORY.md` | Long-term curated memory (people, infra, lessons) |
| `SOUL.md` | Agent identity and personality |
| `USER.md` | User profile and preferences |
| `AGENTS.md` | Session boot instructions and workspace rules |
| `PRIORITY_BRIEFING.md` | Current priorities for first user message |
| `TOOLS.md` | Tool notes, Discord channels, credentials |
| `VAULT_INDEX.md` | This file — memory file registry |

## Daily Logs (Last 7 Days)
| File | Key Topics |
|------|------------|
HEADER

# Generate daily log entries (last 7 days)
for f in $(ls -r memory/202*.md 2>/dev/null | head -7); do
    date=$(basename "$f" .md)
    # Extract H2 headings as topic summary
    topics=$(grep '^## ' "$f" | sed 's/^## //' | head -4 | paste -sd ', ')
    echo "| \`$f\` | $topics |" >> "$INDEX"
done

echo "" >> "$INDEX"
echo "## Reference Docs" >> "$INDEX"
echo "| File | Description |" >> "$INDEX"
echo "|------|-------------|" >> "$INDEX"

for f in memory/refs/*.md; do
    [ -f "$f" ] || continue
    # Use first line or H1 as description
    desc=$(head -1 "$f" | sed 's/^#* //')
    echo "| \`$f\` | $desc |" >> "$INDEX"
done

echo "" >> "$INDEX"
echo "## Archive ($(ls memory/archive/ 2>/dev/null | wc -l) files)" >> "$INDEX"
echo "*Raw daily logs older than 7 days. Search with QMD.*" >> "$INDEX"
```

**Cron schedule:** Run at 11:05 PM HKT (5 minutes after compaction finishes).

**Risk:** Low. Purely generative — doesn't modify any source files.

**Impact:** Vault index stays current without manual effort. Agents can read it on wake for instant orientation.

---

### 2.3 — Priority-Based Wake Context Loading

**What changes:** Modify the AGENTS.md boot sequence to incorporate priority-based loading.

**Current boot (from AGENTS.md):**
```
1. Read SOUL.md
2. Read USER.md
3. Read memory/YYYY-MM-DD.md (today + yesterday)
4. Main session: Read MEMORY.md
5. Read PRIORITY_BRIEFING.md
```

**New boot:**
```
1. Read SOUL.md
2. Read USER.md
3. Read MEMORY.md (P1 section is at the top — most critical context loads first)
4. Read PRIORITY_BRIEFING.md
5. Read VAULT_INDEX.md (orientation — what files exist, what happened recently)
6. Read memory/YYYY-MM-DD.md (today only — yesterday only if today is sparse)
7. If context budget allows: Read yesterday's log
```

**Key changes:**
- MEMORY.md moves before daily logs (P1 section = most important context)
- VAULT_INDEX.md added (cheap — small file, high orientation value)
- Yesterday's log becomes conditional (saves context budget on busy days)
- PRIORITY_BRIEFING.md stays early (Guillermo's priorities > everything)

**Migration path:** Update AGENTS.md. All agents pick this up via Syncthing.

**Risk:** Low. Reading order change, not content change. If VAULT_INDEX.md doesn't exist yet, skip it.

**Impact:** Most important context always loads. Less risk of P1 items getting pushed out of context by verbose daily logs.

---

### 2.4 — Entity Reference Files in memory/refs/

**What changes:** For high-value entities (people, projects, companies mentioned repeatedly), create dedicated reference files.

**Trigger:** When an entity appears in `[[wiki-links]]` across 3+ daily logs, it deserves a reference file.

**Format example — `memory/refs/people/pedro-versatly.md`:**
```markdown
---
type: relationship
entity: Pedro
org: Versatly
first_seen: 2026-02-13
last_updated: 2026-02-15
priority: P2
---

# Pedro (Versatly)

- Twitter: @sillydarket
- Built [[ClawVault]] — open-source memory system for AI agents
- His article on solving agent memory got 733 likes (Feb 13, 2026)
- Key claim: plain markdown > specialized memory tools on LoCoMo benchmark
- Connection context: Found via Twitter, relevant to our memory architecture work

## Interactions
- 2026-02-15: Analyzed his ClawVault article, decided to adopt patterns not package
```

**Format example — `memory/refs/projects/clawvault-upgrade.md`:**
```markdown
---
type: project
status: active
started: 2026-02-15
priority: P1
---

# ClawVault Memory Upgrade

Adopting [[ClawVault]]-inspired patterns into TMNT memory stack.
Plan: `/data/workspace/docs/CLAWVAULT-MEMORY-UPGRADE-PLAN.md`

## Decisions
- Don't install npm package — adopt patterns only
- Use HTML comment tags (not YAML frontmatter) for daily log entries
- Wiki-links for entity cross-referencing

## Status
- Phase 1: In progress
- Phase 2: Not started
- Phase 3: Not started
```

**YAML frontmatter here (not HTML comments)** because these are standalone files (one entity per file), so YAML works naturally.

**Migration path:** Create people files for high-frequency entities first (Guillermo already has a section in MEMORY.md — that's effectively his entity file). Create project files for active projects. Don't mass-create — grow organically.

**Integration with QMD:** These files are searchable by default. The YAML frontmatter fields (`type: relationship`, `entity: Pedro`) become searchable metadata.

**Integration with Syncthing:** Files in `memory/refs/` sync across all agents. Consider moving high-value entities to `shared/memory-vault/people/` for cross-agent access.

**Risk:** Medium. File proliferation — too many small files becomes noise. **Mitigation:** Only create when entity appears 3+ times. Review quarterly and archive stale ones.

**Impact:** "What do I know about Pedro?" has a single, definitive answer file. Relationships and project state persist across sessions without cluttering MEMORY.md.

---

## Phase 3: Advanced Features (2-4 Weeks)

### 3.1 — Cross-Agent Memory Typing in Shared Vault

**What changes:** Extend memory typing to the shared memory vault (`/data/shared/memory-vault/`), enabling structured cross-agent queries.

**Current shared structure:**
```
shared/memory-vault/
├── knowledge/
│   └── projects/brinc/...
├── projects/
└── people/
```

**New shared structure:**
```
shared/memory-vault/
├── decisions/          # Cross-agent decisions (tagged, searchable)
├── lessons/            # Shared lessons learned
├── people/             # Shared people dossiers
├── projects/           # Active project state
├── knowledge/          # Reference knowledge (existing)
└── SHARED_INDEX.md     # Index of shared files
```

**Rules for shared memory:**
- Only P1 and P2 items get promoted to shared vault
- Each agent maintains their own local memory — shared vault is for cross-cutting concerns
- File naming: `YYYY-MM-DD-<slug>.md` for decisions, `<entity-name>.md` for people/projects
- SHARED_INDEX.md auto-updated by cron (same pattern as VAULT_INDEX.md)

**Coordination protocol:**
- Agent creates a decision/lesson locally → tags it `<!-- scope: shared -->`
- Compaction cron copies shared-scope items to shared vault
- Other agents see it via Syncthing on next sync cycle

**Migration path:** Restructure shared vault folders. Move existing people/project files into new structure. Update Syncthing shared folder config if needed.

**Risk:** Medium-high. Syncthing conflict resolution with multiple agents writing to shared files. **Mitigation:** Append-only pattern for shared files. Each agent appends, never overwrites. Use agent-prefixed entries:
```markdown
## 🦎 Molty — 2026-02-15
Decided to adopt ClawVault patterns instead of installing the package.

## 🔴 Raphael — 2026-02-16
Applied memory typing to Brinc client notes.
```

**Impact:** "What did the squad decide about X?" becomes answerable from a single shared source of truth.

---

### 3.2 — Automated Entity Extraction & Wiki-Link Suggestion

**What changes:** A cron job (or heartbeat task) scans recent daily logs for un-linked entity mentions and suggests wiki-links.

**Implementation:**
```
ENTITY EXTRACTION (run during heartbeat, not cron — needs LLM):

1. Read today's daily log
2. Read list of known entities from memory/refs/ filenames + MEMORY.md headings
3. Find mentions of known entities that aren't wiki-linked
4. Suggest additions (or auto-apply if confidence > 0.9)
5. Identify NEW entities mentioned 2+ times that don't have reference files
6. Create stub reference files for new entities
```

**This is a heartbeat task, not a cron**, because:
- It needs LLM reasoning (entity extraction is fuzzy)
- It's not time-critical (can run during any quiet heartbeat)
- It's iterative (gets better as the entity list grows)

**Frequency:** 1x daily during afternoon heartbeat (2-4 PM HKT, after morning work is logged).

**Risk:** Low — only creates new files and suggests edits, never deletes.

**Impact:** Knowledge graph grows organically without requiring the agent to remember to wiki-link every entity.

---

### 3.3 — Weekly Memory Reflection

**What changes:** A new weekly cron (Sunday 10 PM HKT) that generates a reflection document.

**Reflection template:**
```markdown
# Week of 2026-02-10 to 2026-02-16

## Decisions Made This Week
<!-- Auto-extracted from P1 entries tagged 'decision' -->
- ...

## Commitments (Open)
<!-- Auto-extracted from P1 entries tagged 'commitment' + still open -->
- ...

## Lessons Learned
<!-- Auto-extracted from entries tagged 'lesson' -->
- ...

## Key Relationships Updated
<!-- Auto-extracted from entries tagged 'relationship' -->
- ...

## Unresolved Questions
<!-- Items that appeared multiple times without resolution -->
- ...

## MEMORY.md Update Suggestions
<!-- Items from this week that should be promoted to long-term memory -->
- Consider adding: ...
- Consider updating: ...
- Consider removing (stale): ...
```

**Output:** `memory/reflections/week-YYYY-MM-DD.md`

**The reflection is generated by a sub-agent** (Flash model, cheap) that:
1. Reads all 7 daily logs for the week
2. Reads current MEMORY.md
3. Extracts tagged items by type
4. Identifies patterns and gaps
5. Suggests MEMORY.md updates

**The agent reviews suggestions during Monday morning heartbeat** and applies them. This closes the loop: daily logs → weekly reflection → long-term memory curation.

**Risk:** Low. Generative, doesn't modify source files. Worst case: bad suggestions get ignored.

**Impact:** High. Prevents MEMORY.md from going stale. Ensures lessons and decisions migrate to long-term memory. Creates a searchable weekly archive.

---

### 3.4 — Budget-Aware Context Injection (Advanced)

**What changes:** Instead of reading full files on wake, implement a context budget system.

**Concept:**
```
CONTEXT BUDGET (pseudocode):

TOTAL_BUDGET = 8000 tokens  # ~20% of usable context for memory
P1_BUDGET = 3000 tokens     # Always loaded
P2_BUDGET = 3000 tokens     # Loaded if space
P3_BUDGET = 2000 tokens     # Loaded if space

on_wake():
    context = []
    
    # Always load (not counted against budget)
    context += read("SOUL.md")       # ~500 tokens
    context += read("USER.md")       # ~300 tokens
    context += read("AGENTS.md")     # ~600 tokens
    
    # P1: Critical context (always)
    context += read_section("MEMORY.md", "P1 — Active Context")  # ~200 tokens
    context += read("PRIORITY_BRIEFING.md")                       # ~300 tokens
    remaining_p1 = P1_BUDGET - tokens_used
    context += search_and_load(type="commitment", status="open", limit=remaining_p1)
    
    # P2: Important context (if budget allows)
    context += read("VAULT_INDEX.md")                    # ~400 tokens
    context += read("memory/today.md", limit=P2_BUDGET)  # Today's log
    
    # P3: Supplementary (if budget allows)
    context += read("memory/yesterday.md", limit=P3_BUDGET)  # Yesterday
```

**Reality check:** This level of programmatic control over context loading would require either:
- An OpenClaw hook (which we'd need to write/configure)
- Or restructuring AGENTS.md instructions so the agent self-manages its reads

**Practical approach for now:** Don't try to automate token counting. Instead, restructure AGENTS.md boot instructions with clear priority tiers and trust the agent to skip lower-priority reads when context feels heavy:

```markdown
## Every Session (Boot Sequence)

### Tier 1 — Always (identity + critical state)
1. Read `SOUL.md`
2. Read `USER.md`  
3. Read `MEMORY.md` (start from P1 section at top)
4. Read `PRIORITY_BRIEFING.md`

### Tier 2 — Usually (orientation + today)
5. Read `VAULT_INDEX.md` (scan, don't memorize)
6. Read `memory/YYYY-MM-DD.md` (today)

### Tier 3 — If Relevant (supplementary)
7. Read yesterday's log (skip if today's is comprehensive)
8. Search memory for entities relevant to first user message
```

**Risk:** Low — it's just boot order instructions. Agent compliance varies but it's better than no priority.

**Impact:** Reduces the chance of context overflow killing important memory. Most critical state always loads first.

---

## Implementation Timeline

```
Week 1 (Feb 15-16):
  ✅ Phase 1.1: Start tagging daily log entries with type/priority
  ✅ Phase 1.2: Start using wiki-links in entries
  ✅ Phase 1.3: Create VAULT_INDEX.md (manual first version)
  ✅ Phase 1.4: Add P1 section to top of MEMORY.md

Week 2 (Feb 17-21):
  📋 Phase 2.1: Update compaction cron for priority-aware logic
  📋 Phase 2.2: Add vault index auto-generation to cron
  📋 Phase 2.3: Update AGENTS.md boot sequence across all agents
  📋 Phase 2.4: Create first entity reference files (Guillermo, active projects)

Week 3-4 (Feb 22 - Mar 7):
  📋 Phase 3.1: Restructure shared vault with memory typing
  📋 Phase 3.2: Implement entity extraction heartbeat task
  📋 Phase 3.3: Create weekly reflection cron
  📋 Phase 3.4: Implement tiered boot sequence in AGENTS.md
```

---

## Success Metrics

| Metric | Current | Target (4 weeks) | How to Measure |
|--------|---------|-------------------|----------------|
| Can query "all decisions this week" | ❌ No | ✅ Yes | `grep 'type: decision' memory/*.md` |
| Can query "what do I know about X" | Partial (QMD) | ✅ Definitive (ref file + QMD) | Reference file exists for top 10 entities |
| P1 items survive compaction | ❌ No (size-based) | ✅ Yes (priority-aware) | P1 entries in compacted logs match raw logs |
| Time to orient on wake | ~30s (read 3-4 files) | ~15s (P1 section + index) | Subjective agent assessment |
| MEMORY.md freshness | Updated manually (sporadic) | Weekly reflection suggests updates | Reflection cron runs, suggestions applied |
| Cross-agent decision visibility | ❌ No shared decisions | ✅ Shared decisions/ folder | Count of shared decision files |

---

## Risks Summary

| Risk | Severity | Phase | Mitigation |
|------|----------|-------|------------|
| Agents forget to tag entries | Low | 1 | Untagged = P3/update (graceful default). Add to AGENTS.md as habit. |
| Over-tagging (everything is P1) | Medium | 1 | Rule: max 20-30% of entries tagged. P1 max 2-3 per day. |
| Compaction LLM loses detail | Medium | 2 | Always keep raw archive. Compacted = working copy, raw = source of truth. |
| Vault index goes stale | Low | 2 | Auto-generated by cron. Manual edits preserved in Core section. |
| Syncthing conflicts in shared vault | Medium | 3 | Append-only pattern. Agent-prefixed entries. |
| Entity file proliferation | Low | 3 | Threshold: 3+ mentions before creating. Quarterly review. |
| Boot sequence too long | Low | 3 | Tiered loading. Tier 3 is optional. VAULT_INDEX.md is tiny. |

---

## Files Changed Summary

| File | Change | Phase |
|------|--------|-------|
| `memory/YYYY-MM-DD.md` | Add type/priority HTML comment tags | 1 |
| `MEMORY.md` | Add P1 Active Context section at top | 1 |
| `VAULT_INDEX.md` | New file — memory file registry | 1 |
| `AGENTS.md` | Add tagging rules, wiki-link rules, update boot sequence | 1-2 |
| Compaction cron script | Priority-aware compaction logic | 2 |
| `memory/refs/people/*.md` | New entity reference files (YAML frontmatter) | 2 |
| `memory/refs/projects/*.md` | New project reference files (YAML frontmatter) | 2 |
| `shared/memory-vault/` | Restructure with decisions/, lessons/ folders | 3 |
| `SHARED_INDEX.md` | New file — shared vault index | 3 |
| `memory/reflections/` | New folder — weekly reflections | 3 |
| Heartbeat config | Add entity extraction task | 3 |
| Weekly cron | New — Sunday 10PM reflection generation | 3 |

---

## Appendix: Full Tag Reference

### HTML Comment Tag (for daily log entries)
```
<!-- type: decision | priority: P1 -->
<!-- type: lesson | priority: P2 -->
<!-- type: preference | priority: P2 -->
<!-- type: commitment | priority: P1 -->
<!-- type: relationship | priority: P2 -->
<!-- type: update | priority: P3 -->
```

### YAML Frontmatter (for standalone reference files)
```yaml
---
type: relationship          # decision | lesson | preference | commitment | relationship | project
entity: Pedro               # canonical name
org: Versatly               # optional: organization
priority: P2                # P1 | P2 | P3
status: active              # active | resolved | archived
first_seen: 2026-02-13      # when first encountered
last_updated: 2026-02-15    # when last modified
related:                    # wiki-link references
  - "[[ClawVault]]"
  - "[[Versatly]]"
---
```

### Wiki-Link Convention
```
[[Guillermo]]       — people (first name, capitalized)
[[Leonardo]]        — agents (agent name)
[[ClawVault]]       — tools/products (proper case)
[[Brinc]]           — companies (proper case)
[[memory-upgrade]]  — projects (kebab-case)
```
