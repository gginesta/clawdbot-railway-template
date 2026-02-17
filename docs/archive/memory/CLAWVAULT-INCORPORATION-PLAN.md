# ClawVault-Inspired Memory Improvements — Implementation Plan

*Created: 2026-02-15 | Author: Molty (Systems Architecture Sub-Agent)*
*Status: DRAFT — Awaiting Guillermo's review*

---

## Executive Summary

ClawVault's core insight is sound: **typed, linked, priority-tagged markdown files beat both monolithic docs and specialized memory APIs.** But our existing stack already handles several things ClawVault solves (QMD search, multi-agent sync, automated compaction). The move is to **adopt their patterns, not their package** — cherry-picking memory typing, wiki-links, priority tagging, and a vault index while keeping our QMD, Syncthing, and cron infrastructure intact.

**Expected outcome:** Agents can answer "show me all decisions about X" or "what do I know about person Y" without full-text search. Session wake is smarter (P1 memories load first). Compaction preserves important context instead of blindly truncating by size.

---

## Build vs. Install Decision

### Recommendation: **Adopt patterns, don't install the package.**

| Factor | Install `clawvault` | Adopt patterns |
|--------|---------------------|----------------|
| **Search** | Uses QMD (same as us) | Keep our QMD directly |
| **Multi-agent** | Tailscale networking (we use Syncthing) | Keep Syncthing |
| **Task management** | Built-in (we use Todoist + Notion) | Skip — duplication |
| **Vault structure** | Opinionated dirs (`decisions/`, `lessons/`, etc.) | Conflicts with our `memory/` layout |
| **Compaction** | `observe --compress` (LLM-based) | Our 11PM cron already does this |
| **Wake/Sleep** | `clawvault wake` / `clawvault sleep` | Adopt the *concept* in AGENTS.md boot |
| **Dependencies** | Another global npm package × 3 agents | Zero dependencies |
| **Obsidian canvases** | Nice but we don't use Obsidian actively | Skip |
| **Config files** | `.clawvault.json`, `.clawvault/graph-index.json` | Adds hidden state to sync |

**Justification:** ClawVault is designed for single-agent setups or Tailscale-networked vaults. We have 3 agents syncing via Syncthing with existing cron jobs, QMD, Todoist, and Notion integrations. Installing it would mean:
- Maintaining `.clawvault.json` + graph index across 3 agents (sync conflicts likely)
- Duplicating task management (ClawVault tasks vs Todoist)
- Replacing working search with their wrapper around the same QMD
- Learning a new CLI when we can just write markdown directly

**The value is in the *patterns*, not the *package*.** We adopt: memory typing, wiki-links, vault index, priority tagging, budget-aware wake. We skip: their CLI, task system, canvas generation, Tailscale networking.

---

## Phase 1 — Quick Wins (1-2 Days)

### 1.1 Add YAML Frontmatter to MEMORY.md Sections

**What:** Restructure MEMORY.md's "Key Lessons" section to use typed entries. Don't change the file structure — just add semantic markers that QMD can index.

**Current:**
```markdown
## 📝 Key Lessons (Curated)

1. **Backup before update — ALWAYS.** Non-negotiable.
2. **Think in HKT.** System clock is UTC but Guillermo is HKT.
```

**New:**
```markdown
## 📝 Key Lessons (Curated)

1. **Backup before update — ALWAYS.** Non-negotiable. `[lesson]` `[P1]`
2. **Think in HKT.** System clock is UTC but Guillermo is HKT. `[lesson]` `[P1]`
3. **Todoist priority is INVERTED:** `priority=4` = P1 display. `[lesson]` `[P2]`
```

**Why inline tags instead of YAML frontmatter on MEMORY.md?** MEMORY.md is a single curated file, not a collection of individual notes. YAML frontmatter per-section isn't valid markdown. Inline tags (`[lesson]`, `[P1]`) are grep-friendly, QMD-searchable, and don't break the file format.

**Migration:** Agent manually tags existing lessons in next MEMORY.md review. Takes 5 minutes.

**Risk:** Minimal. Additive only, nothing breaks.

**Impact:** `memory_search "lesson P1"` now returns prioritized results. Agent can quickly find "all P1 decisions" vs "P3 routine info."

---

### 1.2 Create Vault Index (`memory/INDEX.md`)

**What:** A single file listing every memory file with a one-line description. Updated by the agent whenever it creates/modifies memory files, and verified by the 8AM guardrail cron.

**Format:**
```markdown
# Memory Vault Index

*Auto-maintained. Last updated: 2026-02-15T21:00+08:00*

## Core Files
| File | Type | Description |
|------|------|-------------|
| MEMORY.md | curated | Long-term memory: people, infra, lessons, squad |
| SOUL.md | identity | Personality, values, operating principles |
| USER.md | identity | Guillermo's profile, preferences, context |
| AGENTS.md | config | Boot sequence, rules, tool notes |
| TOOLS.md | config | Channel IDs, credentials, tool-specific notes |

## Daily Logs
| File | Description |
|------|-------------|
| memory/2026-02-15.md | Sub-agent roster, CODEX, ClawVault analysis, gogcli |
| memory/2026-02-14.md | Daily standup (late), overdue items, Brinc focus |
| memory/2026-02-13.md | ... |

## Reference Docs (`memory/refs/`)
| File | Type | Description |
|------|------|-------------|
| clawvault-analysis.md | research | ClawVault article analysis + adoption notes |
| ... | ... | ... |

## Shared Vault (`/data/shared/memory-vault/`)
| Path | Type | Description |
|------|------|-------------|
| knowledge/projects/brinc/ | project | Brinc corporate knowledge base |
| knowledge/projects/launchpad/ | project | Launchpad venture knowledge base |
| squad/ | squad | Cross-agent coordination docs |
```

**Migration:** Agent builds initial index by scanning existing files. 15-minute task.

**Maintenance rule (add to AGENTS.md):**
> When creating or significantly updating any memory file, add/update its entry in `memory/INDEX.md`.

**Integration with QMD:** INDEX.md itself becomes searchable. `memory_search "what files do we have about Brinc"` → hits INDEX.md and returns the listing.

**Integration with Syncthing:** Each agent maintains their own INDEX.md. No conflicts since each workspace is separate.

**Risk:** Index can drift out of date if agent forgets to update it. Mitigation: 8AM guardrail cron can auto-regenerate from file listing (see Phase 2).

**Impact:** Fastest way to orient in the vault without searching. "What do we know?" is answered by reading one file instead of running multiple searches.

---

### 1.3 Add Wiki-Links to Daily Logs

**What:** When writing daily logs, use `[[entity-name]]` syntax to reference people, projects, and other files. This is pure convention — no tooling needed initially. QMD already indexes the text, so `memory_search "[[Guillermo]]"` works immediately.

**Examples:**
```markdown
## Sub-Agent Roster Consolidation

Worked with [[Leonardo]] on Star Wars theme for his sub-agents.
[[Raphael]] has existing Brinc roster (Scout, Scribe, Analyst, Builder).
Pushed to [[Notion]] standup DB and shared with [[Guillermo]].
Related: [[SUB-AGENT-OPERATING-STANDARD]]
```

**Convention rules:**
- `[[Person Name]]` — People (Guillermo, Leonardo, Raphael)
- `[[Project-Name]]` — Projects (Brinc, Launchpad, Pikachu)
- `[[FILENAME]]` — Cross-reference to another memory file
- `[[tool:ToolName]]` — Tools/services (Todoist, Notion, Syncthing)

**Migration:** Start using in new daily logs. Don't retroactively edit old logs (not worth it).

**Risk:** None. Pure additive convention. If we later want to build a graph index, these links are the raw data.

**Impact:** Human-readable cross-references. Makes daily logs navigable. Enables future graph queries ("show me everything connected to [[Brinc]]").

---

### 1.4 Priority Tags in Daily Logs

**What:** When logging events in daily memory files, prefix significant entries with priority markers.

**Format:**
```markdown
## 2026-02-15 Key Events

- **[P1/decision]** Chose Star Wars theme for [[Leonardo]]'s sub-agents
- **[P1/commitment]** Will fix Gmail OAuth on Feb 19 when [[Guillermo]] returns
- **[P2/lesson]** gogcli can bypass the OAuth client issue — revisit today
- **[P3/update]** Posted CODEX framework to #command-center
```

**Tag vocabulary:**

| Priority | When to use | Survives compaction? |
|----------|-------------|---------------------|
| P1 | Decisions, commitments, critical config changes | Always |
| P2 | Insights, preferences, lessons, relationship notes | Usually |
| P3 | Routine updates, status changes, minor tasks | Only if space |

| Type | Examples |
|------|----------|
| `decision` | "Chose PostgreSQL", "Switched to Opus 4.6" |
| `commitment` | "Will deliver by Friday", "Promised Guillermo X" |
| `lesson` | "Never brute-force config", "Grok unreliable as sub-agent" |
| `preference` | "Guillermo likes tables", "Use Sonnet for execution" |
| `relationship` | "Leonardo owns Launchpad", "Pedro = @sillydarket" |
| `update` | "Pushed to Notion", "Cron updated" |

**Migration:** Start using in today's log entry. Zero disruption.

**Risk:** Agent might over-tag or inconsistently tag. Mitigation: Keep it simple — when in doubt, skip the tag. P1 is the only one that *must* be tagged.

**Impact:** Compaction cron (Phase 2) can now make intelligent decisions about what to keep vs. archive. Priority-based wake loading (Phase 2) becomes possible.

---

## Phase 2 — Structural Improvements (1 Week)

### 2.1 Priority-Aware Compaction

**What:** Upgrade the 11PM compaction cron to be priority-aware instead of purely size-based.

**Current behavior:** If daily log > 10KB, compress it into a summary and archive the raw file.

**New behavior:**
1. Scan the daily log for `[P1/...]` and `[P2/...]` entries
2. Extract all P1 entries verbatim → append to a new file: `memory/priorities.md`
3. Extract P2 entries verbatim → include in the compacted summary
4. P3 entries → summarize in one line each (or drop if space-constrained)
5. Archive the raw log as before
6. If `memory/priorities.md` > 5KB, agent reviews and promotes the most important items to MEMORY.md

**New file: `memory/priorities.md`**
```markdown
# Priority Items (Auto-Collected)

*P1 items extracted from daily logs during compaction. Review weekly.*

## Active Commitments
- [2026-02-15] Will fix Gmail OAuth on Feb 19 — [[Guillermo]] returns to HK
- [2026-02-13] Deploy Pikachu content pipeline by end of Feb

## Recent Decisions
- [2026-02-15] Star Wars theme for [[Leonardo]]'s sub-agents (10 roles mapped)
- [2026-02-15] Sub-Agent Operating Standard v1.0 finalized

## Lessons (Pending Curation)
- [2026-02-15] gogcli can bypass OAuth client issue — potential Gmail/Calendar unlock
```

**Compaction script pseudocode:**
```bash
#!/bin/bash
# Enhanced compaction — runs at 11PM HKT

TODAY=$(date +%Y-%m-%d)
LOG="memory/${TODAY}.md"
PRIORITIES="memory/priorities.md"

if [ ! -f "$LOG" ]; then exit 0; fi

FILE_SIZE=$(wc -c < "$LOG")
if [ "$FILE_SIZE" -lt 10240 ]; then exit 0; fi  # Skip if under 10KB

# Extract priority items (grep-based, fast)
grep -n '\[P1/' "$LOG" > /tmp/p1_items.txt
grep -n '\[P2/' "$LOG" > /tmp/p2_items.txt

# Append P1 items to priorities.md with date prefix
if [ -s /tmp/p1_items.txt ]; then
    echo "" >> "$PRIORITIES"
    echo "## From ${TODAY}" >> "$PRIORITIES"
    while IFS= read -r line; do
        echo "- [${TODAY}] ${line#*]}" >> "$PRIORITIES"
    done < /tmp/p1_items.txt
fi

# Cap priorities.md at 5KB
PRIO_SIZE=$(wc -c < "$PRIORITIES" 2>/dev/null || echo 0)
if [ "$PRIO_SIZE" -gt 5120 ]; then
    # Flag for agent review
    echo "⚠️ priorities.md exceeds 5KB — needs curation" >> "$PRIORITIES"
fi

# Archive raw log
mv "$LOG" "memory/archive/${TODAY}.md"

# Create compacted summary (agent does this via LLM in the cron session)
# The cron triggers a sub-agent that reads the archived log and writes a compact version
```

**Integration with existing cron:** Wrap this logic around the existing 11PM compaction. The existing cron likely triggers an agent session — add instructions to that session's prompt to use priority-aware extraction.

**Integration with QMD:** `memory/priorities.md` is automatically indexed by QMD. `memory_search "commitment"` now returns priority items first.

**Syncthing:** Each agent has their own `memory/priorities.md`. No cross-agent conflicts.

**Risk:** Grep-based P1/P2 extraction is brittle if tagging format varies. Mitigation: Strict format in Phase 1.4. Also, the LLM-based compaction step can catch untagged-but-important items.

**Impact:** Critical decisions and commitments *never get lost* during compaction. The #1 failure mode of the current system — important context buried in a size-truncated summary — is eliminated.

---

### 2.2 Budget-Aware Session Wake

**What:** Modify the AGENTS.md boot sequence to load memories in priority order until context budget is consumed.

**Current boot sequence (from AGENTS.md):**
1. Read SOUL.md
2. Read USER.md
3. Read today's + yesterday's daily log
4. Read MEMORY.md (main session only)
5. Read PRIORITY_BRIEFING.md

**New boot sequence:**
1. Read SOUL.md *(~2KB)*
2. Read USER.md *(~1KB)*
3. Read PRIORITY_BRIEFING.md *(~1KB — surface priorities first)*
4. **Read `memory/priorities.md`** *(≤5KB — all P1 items, recent decisions/commitments)*
5. Read MEMORY.md *(≤15KB — but now with inline tags for skimmability)*
6. Read today's daily log *(variable)*
7. Read yesterday's daily log *(only if context budget allows)*
8. Read `memory/INDEX.md` *(~2KB — quick orientation on what exists)*

**Key change:** `memory/priorities.md` loads *before* MEMORY.md. This ensures that even if context is tight, the agent always knows:
- Active commitments (what was promised)
- Recent decisions (what was decided)
- Critical lessons (what not to repeat)

**Update to AGENTS.md:**
```markdown
## Every Session
1. Read `SOUL.md` — who you are
2. Read `USER.md` — who you're helping  
3. Read `PRIORITY_BRIEFING.md` — surface priorities FIRST
4. Read `memory/priorities.md` — active commitments, recent decisions
5. **Main session only:** Read `MEMORY.md`
6. Read `memory/YYYY-MM-DD.md` (today, then yesterday if context allows)
7. Skim `memory/INDEX.md` — know what files exist
```

**Migration:** Update AGENTS.md. Create initial `memory/priorities.md` by extracting current commitments/decisions from MEMORY.md + recent daily logs. One-time 15-minute task.

**Risk:** Adding more files to boot increases context consumption. Mitigation: `priorities.md` is capped at 5KB and replaces some of what would be searched for later anyway. Net context usage may actually *decrease* because the agent doesn't need to search for recent decisions — they're already loaded.

**Impact:** No more "I forgot we decided X yesterday" failures. The agent wakes up with its most critical knowledge pre-loaded, every time.

---

### 2.3 Typed Memory Files in `memory/refs/`

**What:** Add YAML frontmatter to reference docs in `memory/refs/` for typed retrieval.

**Current:** Files in `memory/refs/` are untyped markdown. You have to read them to know what they contain.

**New format:**
```markdown
---
type: research
priority: P2
entities: [ClawVault, Pedro, Versatly, memory-architecture]
created: 2026-02-15
summary: "Analysis of ClawVault memory system — key patterns to adopt for TMNT"
---

# ClawVault Analysis — "Solving Memory for OpenClaw & General Agents"

(rest of content unchanged)
```

**Frontmatter schema:**
```yaml
---
type: research | process | credential | project | person | decision-log
priority: P1 | P2 | P3
entities: [list, of, wiki-link, targets]  # What this doc is about
created: YYYY-MM-DD
updated: YYYY-MM-DD  # Optional
summary: "One-line description for INDEX.md"
---
```

**How QMD uses this:** QMD indexes full file content including YAML frontmatter. Searching `memory_search "type: research"` returns all research docs. Searching `memory_search "entities: Brinc"` returns everything about Brinc.

**Migration path:**
1. Agent adds frontmatter to existing `memory/refs/` files during a maintenance session
2. New files always include frontmatter (add to agent instructions)
3. INDEX.md auto-populated from frontmatter `summary` fields

**Syncthing:** Each agent's `memory/refs/` is independent. Shared docs go in `/data/shared/memory-vault/`.

**Risk:** Agents might write inconsistent frontmatter (e.g., `type: report` instead of `type: research`). Mitigation: Strict enum in instructions. The guardrail cron (Phase 3) can validate.

**Impact:** Structured retrieval. "Show me all research docs about Brinc" becomes a single search query instead of a manual hunt.

---

### 2.4 Auto-Maintain INDEX.md via Guardrail Cron

**What:** Extend the existing 8AM guardrail cron to auto-regenerate `memory/INDEX.md` from actual file listings + YAML frontmatter.

**Script pseudocode:**
```bash
#!/bin/bash
# INDEX.md auto-generator — runs at 8AM HKT alongside existing guardrails

INDEX="memory/INDEX.md"
echo "# Memory Vault Index" > "$INDEX"
echo "" >> "$INDEX"
echo "*Auto-generated: $(date -Iseconds)*" >> "$INDEX"
echo "" >> "$INDEX"

# Core files
echo "## Core Files" >> "$INDEX"
echo "| File | Description |" >> "$INDEX"
echo "|------|-------------|" >> "$INDEX"
for f in MEMORY.md SOUL.md USER.md AGENTS.md TOOLS.md PRIORITY_BRIEFING.md; do
    if [ -f "$f" ]; then
        # Extract first heading or first line as description
        DESC=$(head -5 "$f" | grep -m1 '^#' | sed 's/^#* //')
        echo "| $f | $DESC |" >> "$INDEX"
    fi
done

# Daily logs (last 7 days)
echo "" >> "$INDEX"
echo "## Daily Logs (Last 7 Days)" >> "$INDEX"
echo "| File | First Heading |" >> "$INDEX"
echo "|------|---------------|" >> "$INDEX"
for f in $(ls -r memory/202*.md 2>/dev/null | head -7); do
    HEADING=$(head -5 "$f" | grep -m1 '^## ' | sed 's/^## //')
    echo "| $f | ${HEADING:-no heading} |" >> "$INDEX"
done

# Reference docs (with frontmatter parsing)
echo "" >> "$INDEX"
echo "## Reference Docs" >> "$INDEX"
echo "| File | Type | Summary |" >> "$INDEX"
echo "|------|------|---------|" >> "$INDEX"
for f in memory/refs/*.md; do
    if [ -f "$f" ]; then
        # Extract type and summary from YAML frontmatter
        TYPE=$(sed -n '/^---$/,/^---$/p' "$f" | grep '^type:' | sed 's/type: *//')
        SUMMARY=$(sed -n '/^---$/,/^---$/p' "$f" | grep '^summary:' | sed 's/summary: *//' | tr -d '"')
        [ -z "$TYPE" ] && TYPE="untyped"
        [ -z "$SUMMARY" ] && SUMMARY=$(head -5 "$f" | grep -m1 '^#' | sed 's/^#* //')
        echo "| $(basename $f) | $TYPE | $SUMMARY |" >> "$INDEX"
    fi
done

# Size check
INDEX_SIZE=$(wc -c < "$INDEX")
if [ "$INDEX_SIZE" -gt 8192 ]; then
    echo "" >> "$INDEX"
    echo "⚠️ Index exceeds 8KB — consider archiving old refs" >> "$INDEX"
fi
```

**Integration with existing 8AM cron:** Append this to the existing guardrail script. Runs after file size checks.

**Risk:** Low. INDEX.md is regenerated fresh each morning, so drift is self-correcting.

**Impact:** INDEX.md is always accurate. Agents don't have to remember to update it manually (though they still should for intra-day accuracy).

---

## Phase 3 — Advanced Features (2-4 Weeks)

### 3.1 Entity Files (`memory/entities/`)

**What:** Dedicated files for frequently-referenced entities (people, projects, tools). Each file aggregates everything the agent knows about that entity.

**Structure:**
```
memory/entities/
├── people/
│   ├── guillermo.md
│   ├── pedro-sillydarket.md
│   └── ...
├── projects/
│   ├── brinc.md
│   ├── launchpad.md
│   ├── pikachu-content.md
│   └── ...
└── tools/
    ├── todoist.md
    ├── notion.md
    ├── syncthing.md
    └── ...
```

**Entity file format:**
```markdown
---
type: person
name: Guillermo Ginesta
aliases: [Guillermo, G, gginesta]
priority: P1
related: [[Brinc]], [[Launchpad]], [[Mana Capital]]
---

# Guillermo Ginesta

## Quick Facts
- **Location:** Hong Kong (GMT+8)
- **Telegram:** @gginesta (id: 1097408992)
- **Style:** Casual, efficient, no fluff. Likes tables.

## Preferences
- Prefers tables over bullet lists
- Wants to see conclusions, not process
- Not super technical but learns fast

## Key Decisions (reverse chronological)
- [2026-02-15] Approved Star Wars theme for Leonardo's sub-agents
- [2026-02-13] Chose to try gogcli for Gmail/Calendar bypass

## Commitments
- Returns to HK Feb 19 — will fix OAuth 2FA
```

**Why this matters:** Currently, "what do I know about Guillermo?" requires reading MEMORY.md + searching daily logs. An entity file puts everything in one place, and wiki-links like `[[Guillermo]]` in daily logs point back to it.

**Migration:**
1. Agent creates initial entity files by extracting from MEMORY.md and recent daily logs
2. Ongoing: When logging something about a person/project, update their entity file
3. INDEX.md auto-includes entity listings

**Maintenance rule:** Entity files are capped at 3KB each. When they grow beyond that, old/routine items move to the entity's "history" section (collapsible) or get pruned.

**Integration with QMD:** Entity files are automatically indexed. `memory_search "Guillermo preferences"` → hits the entity file directly.

**Syncthing considerations:** Entity files in each agent's local `memory/entities/`. Shared entities (like `guillermo.md`) could also live in `/data/shared/memory-vault/people/` — but this risks merge conflicts. **Recommendation:** Each agent maintains their own entity files. Cross-agent queries go through Discord or webhooks.

**Risk:** Entity files become stale or redundant with MEMORY.md. Mitigation: MEMORY.md keeps the *summary*; entity files hold the *detail*. Think of MEMORY.md as the index card and entity files as the dossier.

**Impact:** "What do we know about X?" is answered by reading one file. Relationship mapping becomes trivial.

---

### 3.2 Wiki-Link Graph Index

**What:** A script that scans all memory files for `[[wiki-links]]` and builds a graph index showing connections between entities.

**Output: `memory/GRAPH.md`**
```markdown
# Knowledge Graph

*Auto-generated: 2026-02-15T21:00+08:00*

## Entities (by mention count)
| Entity | Mentions | Files |
|--------|----------|-------|
| [[Guillermo]] | 47 | MEMORY.md, 12 daily logs, 3 refs |
| [[Brinc]] | 23 | MEMORY.md, 8 daily logs, 2 refs |
| [[Leonardo]] | 19 | MEMORY.md, 6 daily logs |
| [[Todoist]] | 14 | MEMORY.md, TOOLS.md, 5 daily logs |

## Connections
| From | To | Context |
|------|----|---------|
| [[Guillermo]] | [[Brinc]] | CEO/Founder |
| [[Guillermo]] | [[Launchpad]] | Venture lead |
| [[Leonardo]] | [[Launchpad]] | Agent owner |
| [[Raphael]] | [[Brinc]] | Agent owner |
| [[Pikachu]] | [[Brinc]] | Content/Marketing sub-project |
```

**Script approach:** Bash + grep, run weekly by cron (not daily — too expensive for marginal benefit).

```bash
#!/bin/bash
# Wiki-link graph builder — runs weekly (Sunday 8AM HKT)

GRAPH="memory/GRAPH.md"
echo "# Knowledge Graph" > "$GRAPH"
echo "*Auto-generated: $(date -Iseconds)*" >> "$GRAPH"
echo "" >> "$GRAPH"

# Find all wiki-links across memory files
grep -roh '\[\[[^]]*\]\]' memory/ MEMORY.md TOOLS.md 2>/dev/null \
    | sort | uniq -c | sort -rn \
    | while read count link; do
        echo "| $link | $count |"
    done > /tmp/graph_counts.txt

echo "## Entities (by mention count)" >> "$GRAPH"
echo "| Entity | Mentions |" >> "$GRAPH"
echo "|--------|----------|" >> "$GRAPH"
cat /tmp/graph_counts.txt >> "$GRAPH"
```

**Why not a JSON graph like ClawVault?** Their `.clawvault/graph-index.json` is designed for programmatic traversal by their CLI. We don't have their CLI. A markdown table is readable by both the agent and QMD, and doesn't add hidden state to sync.

**Integration with QMD:** GRAPH.md is searchable. "What entities are connected to Brinc?" → search hits the graph file.

**Risk:** Graph file grows large if many entities. Mitigation: Cap at top 50 entities. Full graph lives in archive if needed.

**Impact:** Agent can quickly understand the shape of its knowledge. "What's connected to what?" no longer requires mental reconstruction.

---

### 3.3 Priority-Based Weekly Reflection

**What:** A weekly cron (Sunday 9AM HKT) that generates a reflection doc by aggregating the week's P1/P2 items, checking for stale commitments, and suggesting MEMORY.md updates.

**Output: `memory/reflections/week-YYYY-WW.md`**
```markdown
---
type: reflection
period: 2026-W07
created: 2026-02-16
---

# Weekly Reflection — Week 7 (Feb 10-16, 2026)

## P1 Items This Week
- [Feb 15] Decided: Star Wars theme for Leonardo's sub-agents
- [Feb 15] Committed: Fix Gmail OAuth on Feb 19
- [Feb 13] Decided: Install gogcli for Google Suite access

## Open Commitments
- ⏳ Gmail OAuth fix — due Feb 19 (Guillermo returns)
- ⏳ Pikachu content pipeline — no due date set
- ⚠️ 1Password for TMNT squad — overdue since Feb 9

## Suggested MEMORY.md Updates
- Add: gogcli installed, auth pending
- Add: Sub-Agent Operating Standard v1.0 finalized
- Remove: "Email broken until Feb 19" (will resolve this week)

## Knowledge Gaps
- No entity file for: Ernest/Earnest (webinar contact)
- Stale info: Brinc outreach plan overdue, no update logged

## Stats
- Daily logs written: 5/7
- P1 items logged: 8
- P2 items logged: 14
- Entity files updated: 3
```

**This replaces nothing** — it's additive. The agent (or Guillermo) reads it on Sunday/Monday to stay oriented.

**Cron setup:**
```
# Sunday 9AM HKT — weekly reflection
0 9 * * 0 openclaw session --prompt "Generate weekly reflection from this week's daily logs and priorities.md. Save to memory/reflections/week-$(date +%Y-W%V).md" --model flash
```

**Risk:** Reflection quality depends on consistent P1/P2 tagging during the week. If Phase 1 tagging isn't adopted, reflections will be thin. Mitigation: The reflection cron itself can do a best-effort extraction even without tags (LLM can identify decisions/commitments from untagged text).

**Impact:** Systematic knowledge curation instead of ad-hoc. MEMORY.md stays fresh because the agent is prompted weekly to update it.

---

### 3.4 Cross-Agent Entity Sync (Shared Vault)

**What:** Shared entity files in `/data/shared/memory-vault/people/` that all agents can read (and carefully write to).

**Current state:** Syncthing already shares folders (`mv-people`, `mv-projects`, etc.) between agents. But there's no convention for how these files are structured or maintained.

**Proposed convention:**
- Shared entity files use the same YAML frontmatter format as local entity files
- **Write rule:** Only the *owning agent* updates a shared entity file. Others read only.
  - Molty owns: `guillermo.md`, general squad files
  - Raphael owns: Brinc-related person/project files
  - Leonardo owns: Launchpad-related person/project files
- **Conflict resolution:** If two agents need to update the same file, they post to `#squad-updates` and the owner merges

**Risk:** Syncthing conflicts if write rules aren't followed. Mitigation: Ownership is explicit in frontmatter (`owner: molty`). Agents check before writing.

**Impact:** "What does the squad know about person X?" is answered from shared files. No more relying on Discord relay or Guillermo forwarding context.

---

## Implementation Timeline

```
Week 1 (Feb 16-17): Phase 1 — Quick Wins
├── Day 1: Add inline tags to MEMORY.md lessons (1.1)
├── Day 1: Create memory/INDEX.md (1.2)
├── Day 1: Start using [[wiki-links]] in daily logs (1.3)
└── Day 2: Start using [P1/type] tags in daily logs (1.4)

Week 2 (Feb 18-24): Phase 2 — Structural
├── Create memory/priorities.md + update boot sequence (2.1, 2.2)
├── Add YAML frontmatter to memory/refs/ files (2.3)
└── Add INDEX.md auto-generation to 8AM cron (2.4)

Week 3-4 (Feb 25 - Mar 8): Phase 3 — Advanced
├── Week 3: Create entity files for top 10 entities (3.1)
├── Week 3: Build wiki-link graph script (3.2)
├── Week 4: Set up weekly reflection cron (3.3)
└── Week 4: Establish shared entity conventions (3.4)
```

---

## Risk Summary

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agents don't consistently tag P1/P2 | Medium | High (undermines Phase 2+3) | Keep tagging simple. P1-only minimum. |
| INDEX.md drifts from reality | Low | Low (8AM cron auto-fixes) | Cron regeneration |
| Entity files become stale | Medium | Medium | Weekly reflection flags gaps |
| Frontmatter format inconsistency | Medium | Low | Strict enum in instructions |
| Increased boot context usage | Low | Medium | priorities.md replaces ad-hoc searches |
| Syncthing conflicts on shared entities | Low | Medium | Ownership rules in frontmatter |

---

## Success Metrics (After 2 Weeks of Phase 1+2)

1. **"Show me all decisions about X"** → Answerable via `memory_search "P1/decision X"` without reading multiple files
2. **No lost commitments** → `memory/priorities.md` catches all P1 items during compaction
3. **Faster orientation** → Agent reads INDEX.md instead of searching blindly
4. **Richer daily logs** → Wiki-links make logs navigable; priority tags make them filterable
5. **Cleaner MEMORY.md** → Weekly reflections prompt systematic curation

---

## Files Created/Modified Summary

| File | Action | Phase |
|------|--------|-------|
| `MEMORY.md` | Add inline `[lesson]` `[P1]` tags | 1.1 |
| `memory/INDEX.md` | **New** — vault index | 1.2 |
| Daily logs | Convention: use `[[wiki-links]]` and `[P1/type]` tags | 1.3, 1.4 |
| `AGENTS.md` | Update boot sequence to include priorities.md + INDEX.md | 2.2 |
| `memory/priorities.md` | **New** — auto-collected P1 items | 2.1 |
| `memory/refs/*.md` | Add YAML frontmatter | 2.3 |
| 8AM guardrail cron | Add INDEX.md auto-generation | 2.4 |
| 11PM compaction cron | Add priority-aware extraction | 2.1 |
| `memory/entities/` | **New** directory — entity dossiers | 3.1 |
| `memory/GRAPH.md` | **New** — wiki-link graph (weekly) | 3.2 |
| `memory/reflections/` | **New** directory — weekly reflections | 3.3 |
| Shared vault conventions | Ownership rules for cross-agent entities | 3.4 |

---

*This plan is designed to be implemented incrementally. Each phase builds on the previous one, but none are blocking. If Phase 3 never happens, Phase 1+2 alone significantly improve memory quality.*
