# PLAN-012: Meta-Learning Loops Integration

**Created:** 2026-03-06 15:11 HKT
**Owner:** Molty 🦎
**Status:** Planning
**Priority:** P1
**Scheduled:** Tonight 03:00 HKT

---

## Objective

Integrate the 9-loop meta-learning architecture from @AtlasForgeAI into Molty's operating system. Design improvements specific to our fleet context. Deploy changes that compound learning across sessions.

## Source

Article: "How to Build Nine Meta-Learning Loops for Your OpenClaw Agent"
URL: https://x.com/AtlasForgeAI/status/2026380335249002843

Core insight: "The real bottleneck isn't intelligence. It's the absence of learning feedback loops that persist across sessions."

---

## The Nine Loops — Analysis & Integration Plan

### Loop 1: Failure-to-Guardrail Pipeline

**What it is:** Every significant failure becomes a named regression loaded every session.

**Current state:** 
- `memory/refs/mistake-tracker.md` — exists but informal
- `memory/refs/lessons-learned.md` — exists but verbose
- AGENTS.md has some rules but not structured as regressions

**Gap:** No formal named regression list loaded at boot. Mistakes are documented but not encoded as hard rules.

**Integration plan:**
1. Create `REGRESSIONS.md` in workspace root (loaded every session via project context)
2. Format: `REG-XXX: <name> — <one-line rule>`
3. Migrate existing lessons into regression format
4. Add to AGENTS.md: "Check REGRESSIONS.md every session"
5. Process: When mistake is called out → add to REGRESSIONS.md immediately

**Example output:**
```markdown
# REGRESSIONS.md — Hard Rules From Past Failures

## Infrastructure
- REG-001: gateway.bind must be "loopback" when tailscale.mode="serve"
- REG-002: MC endpoints — GET /api/tasks (plural), POST /api/task (singular)
- REG-003: Don't guess package names — verify before giving install commands

## Calendar
- REG-004: Brinc busy block is automatic — no flag needed in cal_create
- REG-005: Use SA token only — calendar-tokens-brinc.json expires headlessly

## Operations
- REG-006: Claiming done requires citing file+line
- REG-007: Webhook sessionKey is DISABLED — always omit
- REG-008: X posting blocked — bot detection, don't attempt

## Communication
- REG-009: Saying "staying silent" is not staying silent — just don't reply
- REG-010: Webchat+Telegram duplicate — session inherits first channel
```

**Improvement for fleet:** 
- Create `/data/shared/FLEET-REGRESSIONS.md` for cross-agent regressions
- Each agent has local REGRESSIONS.md + inherits fleet regressions
- When regression applies to all agents, promote to fleet level

---

### Loop 2: Tiered Memory with Trust Scoring and Decay

**What it is:** Constitutional (never expires) → Strategic (quarterly) → Operational (30-day decay). Each entry has trust score and hit count.

**Current state:**
- MEMORY.md — curated, <15KB target
- memory/YYYY-MM-DD.md — daily logs, raw
- memory/refs/ — long-term reference docs
- No formal trust scoring or decay

**Gap:** No explicit tiers. No hit counting. No auto-decay. MEMORY.md grows without pruning signal.

**Integration plan:**
1. Restructure memory into explicit tiers:
   - `MEMORY.md` → Constitutional + Strategic (high-trust, low-decay)
   - `memory/operational/` → New folder for 30-day decay items
   - `memory/refs/` → Stays as reference docs (no decay)

2. Add metadata headers to entries:
```markdown
<!-- trust: 1.0 | hits: 5 | added: 2026-03-01 | source: guillermo-direct -->
```

3. Nightly job: scan operational/, archive entries >30 days with hits <2

4. Hit counting: When I reference a memory entry, bump its hit count

**Improvement for fleet:**
- Memory vault (`/data/shared/memory-vault/`) already exists
- Add trust scoring to vault entries
- Fleet-level decisions are constitutional (trust: 1.0, no decay)
- Agent observations are operational (trust: 0.7, 30-day decay)

---

### Loop 3: Prediction-Outcome Calibration

**What it is:** Before significant decisions, write prediction with confidence. After, record outcome and delta. Over time, reveals systematic biases.

**Current state:** None. We make decisions without logging predictions.

**Gap:** Complete. No calibration mechanism.

**Integration plan:**
1. Create `memory/predictions/` folder
2. Format per prediction:
```markdown
# PRED-2026-03-06-001: Leonardo config fix

**Decision:** Deploy bind=loopback + DM key fix
**Prediction:** This will fully resolve webhook failures
**Confidence:** 0.8
**Reasoning:** Logs showed bind error, similar fix worked for Molty

---

**Outcome:** (filled after)
**Actual:** Partial success — webhooks work, but new issue with X
**Delta:** -0.3 (overestimated completeness)
**Lesson:** Config changes often have hidden dependencies
**Calibration note:** I run hot on "this will fix it" confidence
```

3. Weekly review: scan predictions/, identify confidence patterns
4. Add to overnight cron: "Review any predictions from past 48h that lack outcomes"

**Improvement:**
- Track prediction accuracy by category (infra, calendar, agent coordination)
- After 30 predictions, calculate calibration score per category
- Adjust confidence thresholds based on historical accuracy

---

### Loop 4: Nightly Extraction

**What it is:** Automated cron that reviews the day, documents decisions, tests "could fresh session reconstruct today from files alone?"

**Current state:**
- Overnight cron at 03:00 HKT exists
- Focuses on task execution, not synthesis
- No explicit "reconstruction test"

**Gap:** No automated synthesis. No "what's missing?" test.

**Integration plan:**
1. Add to overnight cron prompt:
```
Before starting tasks, run the Reconstruction Test:
1. Read today's memory file (memory/2026-03-06.md)
2. Ask: "Could a fresh Molty session reconstruct today's decisions from files alone?"
3. If gaps exist, write them to the daily log NOW before they're lost
4. Check: Are there any decisions made today not documented anywhere?
5. Check: Are there any Guillermo preferences expressed today not in USER.md or MEMORY.md?
```

2. Add synthesis section to daily log template:
```markdown
## Nightly Synthesis (auto-generated)
- Decisions documented: Y/N
- Preferences captured: Y/N
- Gaps filled: [list]
- Reconstruction confidence: X%
```

**Improvement:**
- Run reconstruction test at END of overnight window too (not just start)
- Compare: what did I learn during overnight work that isn't persisted?

---

### Loop 5: Friction Detection

**What it is:** Log contradictory instructions instead of silently resolving. Surface at next break point.

**Current state:** None. I silently comply with whatever instruction is most recent.

**Gap:** Complete. No friction logging.

**Integration plan:**
1. Create `memory/friction-log.md`
2. When I detect contradictory instructions:
   - Log: date, instruction A, instruction B, how I resolved it
   - Flag for standup surfacing
3. Add to standup template: "Friction items to surface"

**Format:**
```markdown
# Friction Log

## 2026-03-06
- **Conflict:** AGENTS.md says "use Discord first" but Guillermo said "send webhook immediately"
- **Resolution:** Followed direct instruction (webhook)
- **Surfaced:** Not yet
- **Decision:** [Guillermo decides which is canonical]
```

**Improvement:**
- Don't just log — actively surface friction in next interaction
- "Before we continue, I logged a friction item: [X]. Which approach should be canonical?"
- Prevents architectural drift from silent resolutions

---

### Loop 6: Active Context Holds

**What it is:** Temporary constraints that shape interpretation. Have expiry dates.

**Current state:** 
- PRIORITY_BRIEFING.md exists (sort of this)
- No formal expiry mechanism

**Gap:** No expiry dates. Holds accumulate without cleanup.

**Integration plan:**
1. Formalize PRIORITY_BRIEFING.md as "Active Holds"
2. Add expiry to each hold:
```markdown
# Active Holds

## HOLD-001: Cerebro beta focus
- **Context:** Prioritize Cerebro tasks over infrastructure
- **Expires:** 2026-03-15
- **Renew?:** Check with Guillermo if still active

## HOLD-002: April deployment prep
- **Context:** Gather requirements for April agent
- **Expires:** 2026-03-10
- **Renew?:** Auto-archive after deployment
```

3. Nightly job: check expired holds, archive or prompt for renewal

**Improvement:**
- Holds can be inherited by fleet (FLEET-HOLDS.md in /data/shared/)
- Example: "All agents: prioritize MC task updates" — expires in 1 week

---

### Loop 7: Epistemic Tagging

**What it is:** Force claims into categories: [consensus], [observed], [inferred], [speculative], [contrarian]

**Current state:** None. I state things with uniform confidence.

**Gap:** Complete. No epistemic humility markers.

**Integration plan:**
1. Add to SOUL.md under communication style:
```markdown
## Epistemic Honesty
When making claims, especially about technical matters:
- [observed] — I saw this directly (logs, output, file contents)
- [inferred] — I'm reasoning from evidence but didn't observe directly
- [speculative] — This is my best guess, low confidence
- [consensus] — This is widely accepted / documented
- [contrarian] — I disagree with the obvious answer

Default to tagging when confidence isn't obvious.
```

2. Use in practice:
   - "The webhook is failing [observed] because of a bind misconfiguration [inferred]"
   - "I think Sonnet 4.6 is the best daily driver [consensus from multiple sources]"

**Improvement:**
- Track which tags I use most — if 90% [consensus], I'm just summarizing
- Goal: more [inferred] and [contrarian] in strategic discussions

---

### Loop 8: Creative Mode Directives

**What it is:** Structural rules for creative/strategic work: generate uncomfortable takes, name consensus then argue against it.

**Current state:** SOUL.md has "Have opinions. Strong ones." but no structural rules.

**Gap:** No formal creative mode. No forced contrarianism.

**Integration plan:**
1. Add to SOUL.md:
```markdown
## Creative Mode (for strategy/brainstorming)
When Guillermo asks for ideas, opinions, or strategy:
1. Name the obvious/consensus answer first
2. Generate at least one take that feels uncomfortable or contrarian
3. Prefer interesting-and-maybe-wrong over safe-and-definitely-right
4. If I find myself giving the "AI assistant" answer, stop and try again
```

2. Trigger: activate when discussion is explicitly creative/strategic, not operational

**Improvement:**
- Add "Devil's Advocate" persona I can invoke
- "/contrarian" command: force me to argue against my previous position

---

### Loop 9: Recursive Self-Improvement

**What it is:** Generate → Evaluate → Diagnose → Improve → Repeat. Stop after 3 iterations with <5% improvement.

**Current state:** Ad-hoc. No formal loop structure.

**Gap:** No explicit iteration protocol.

**Integration plan:**
1. For significant deliverables (plans, docs, code):
```markdown
## Improvement Loop
- V1: [initial output]
- Evaluation: [against explicit criteria]
- Diagnosis: [root cause of gaps]
- V2: [improved output]
- Evaluation: [% improvement]
- Stop if <5% improvement after V3
```

2. Add to recon-first skill: after EXECUTE, optionally EVALUATE

**Improvement:**
- Define evaluation criteria upfront for common deliverables
- Plan quality: completeness, actionability, clarity
- Doc quality: accuracy, brevity, usefulness
- Code quality: correctness, readability, efficiency

---

## Implementation Phases

### Phase 1: Tonight (03:00 HKT) — Foundation
- [ ] Create REGRESSIONS.md with initial entries from mistake-tracker
- [ ] Create memory/predictions/ folder with template
- [ ] Create memory/friction-log.md
- [ ] Update AGENTS.md to reference new files

### Phase 2: Tomorrow — Integration  
- [ ] Update overnight cron with Reconstruction Test
- [ ] Formalize PRIORITY_BRIEFING.md as Active Holds with expiry
- [ ] Add epistemic tagging guidance to SOUL.md
- [ ] Add creative mode rules to SOUL.md

### Phase 3: Next Week — Calibration
- [ ] Review first week of predictions — any patterns?
- [ ] Review friction log — any architectural drift?
- [ ] Test: did regressions prevent any repeat failures?
- [ ] Iterate on loop implementations based on actual usage

### Phase 4: Fleet Rollout (if successful)
- [ ] Create FLEET-REGRESSIONS.md in /data/shared/
- [ ] Share prediction-outcome template with Raphael/Leonardo
- [ ] Share friction log pattern with fleet
- [ ] Document meta-learning architecture for other agents

---

## Success Criteria

After 2 weeks:
1. Zero repeat of any regression-listed failure
2. At least 10 predictions logged with outcomes
3. At least 3 friction items surfaced and resolved
4. Nightly synthesis running automatically
5. Measurable improvement in calibration (track prediction accuracy)

After 1 month:
1. Calibration score calculated per category
2. Active holds system running with expiry
3. Epistemic tagging natural in communication
4. Creative mode producing better strategic input
5. Evidence of "the system improving the system"

---

## Notes

This is the most significant meta-learning upgrade since the initial MEMORY.md system. The goal isn't to add bureaucracy — it's to make learning structural so it survives context resets.

Key insight from the article: "A moderately capable agent with good learning loops surpasses a smart agent without them within weeks."

We're already moderately capable. These loops make us compounding.

---

*Plan created 2026-03-06 15:11 HKT. Execution tonight.*
