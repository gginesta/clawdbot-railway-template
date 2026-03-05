# PLAN-011: Agent Management Improvements

**Created:** 2026-03-05
**Source:** Kevin Simback article (https://x.com/KSimback/status/2019804584273657884)
**Status:** In Progress
**Priority:** P1 (overnight Mar 5-6)

---

## Background

Guillermo shared Kevin Simback's article on managing AI agent teams. Two ideas worth implementing:

1. **Agent Performance Reviews** — Structured evaluation process
2. **"Last updated by" headers** — Track who touched shared context files

Guillermo's guidance:
- ❌ Agent Leveling (L1-L4): "I trust the way you build them... don't want to handicap new teammates"
- ✅ Performance Reviews: "Good idea. Add this"
- ❌ ACCESS.md per project: "How we have it works well"
- ✅ Last updated by headers: "Good idea. Add this"

---

## Task 1: Agent Performance Reviews

**MC Task ID:** jn7a2x5w3vcm8xfph5q5dve52n82brx9
**Priority:** P1
**Assignee:** Molty

### Deliverables

1. **Review Framework Document** (`/data/workspace/docs/AGENT-PERFORMANCE-REVIEWS.md`)
   - Review cadence recommendation
   - Evaluation criteria
   - Rating system
   - Feedback loop mechanism
   - Storage location for reviews

2. **Review Template** (`/data/workspace/templates/agent-review-template.md`)
   - Standardized format for conducting reviews

3. **AGENTS.md Update**
   - Add Performance Review section to fleet-wide AGENTS.md

4. **Fleet Cascade**
   - Post directive to #command-center
   - Verify all agents acknowledge and update their AGENTS.md

### Design Decisions (to propose)

- **Cadence:** Bi-weekly? Monthly? After major milestones?
- **Who reviews:** Guillermo? Molty as coordinator? Self-review?
- **Storage:** MC database? Notion? Local memory files?
- **Metrics:** Output quality, goal completion, token efficiency, autonomy decisions, collaboration

---

## Task 2: "Last Updated By" Headers

**MC Task ID:** jn7ezhnm725ec3vt1n2zpprvzd82bc1j
**Priority:** P1
**Assignee:** Molty

### Deliverables

1. **Header Format Standard**
   ```
   <!-- Last updated: {agent} | {date} | {reason} -->
   ```

2. **Files to Update**
   - `/data/shared/` — all cross-agent files
   - `/data/shared/memory-vault/` — vault contributions
   - Any file multiple agents touch

3. **AGENTS.md Update**
   - Add rule: "When editing shared files, add/update the Last updated by header"

4. **Fleet Cascade**
   - Post directive to #command-center
   - All agents update their AGENTS.md

### Implementation

- Add headers to existing shared files
- Update CONTRIBUTION_PROTOCOL.md in vault
- Add to agent onboarding checklist for future agents

---

## Execution Timeline

**Tonight (Mar 5-6 overnight):**
1. Design Performance Review framework
2. Create review template
3. Implement "Last updated by" headers on shared files
4. Update AGENTS.md with both practices
5. Post fleet directive to #command-center

**Tomorrow (Mar 6 morning):**
- Present deliverables to Guillermo in morning briefing
- Get approval before full fleet cascade

---

## Parked Tasks

**Chrome Extension Research** (demoted to P2)
- MC Task ID: jn7aww7z6bepw61f0rbyjh343n82a148
- Will tackle after these management improvements are done

---

## Notes

- Guillermo's philosophy: "Trust + coaching > restrictions"
- New agents (Donatello, April) should get full autonomy from day 1
- Performance reviews are for learning and improvement, not gatekeeping
