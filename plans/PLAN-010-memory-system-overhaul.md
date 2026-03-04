# PLAN-010: Memory System Overhaul
*Created: 2026-03-04 | Author: Molty | Status: DRAFT v3 — Ready for Guillermo Review*
*Passes: self-critique (v2) + Opus independent review (v3)*

---

## The Actual Problem

Molty makes recurring mistakes. The existing response — document the lesson — hasn't worked because it doesn't address how knowledge arrives at the moment of action.

This is not a storage problem. It's a retrieval problem.

A 4KB MEMORY.md is just as useless as a 16KB one if the critical rule isn't surfacing when I'm about to do the thing. Every "lesson documented" that didn't prevent a recurrence is proof of this.

Three things actually prevent mistakes for an amnesiac agent:
1. **Code that makes wrong actions structurally impossible**
2. **Context injected at action time** — right before the action, not at session start
3. **Verified retrieval** — memory_search queried on-demand, not passively loaded

Documentation is not on that list. It's a fallback, not a solution.

---

## What Opus Identified That My First Draft Missed

1. PARA is over-engineered for an amnesiac agent. Folders multiply hiding places. An agent that wakes up cold doesn't browse — it needs a searchlight, not a filing cabinet.
2. The "recursive improvement system" assumed discipline that session amnesia prevents. Rules that require future-me to remember to run them will fail. Only mechanical enforcement (cron, code) works.
3. The sequencing was backwards. Phase 5 (how lessons are tracked) should be designed first, because it determines what the rest of the system needs to capture.
4. No mistake taxonomy. Calendar booking error and "claiming things are done" are completely different failure modes requiring completely different fixes. The plan treated them as one problem.
5. Session loading protocol was never defined. The most critical mechanism — what files actually load, in what order — wasn't addressed.

---

## Mistake Taxonomy (Phase 0 — must come first)

Before designing any system, define what we're actually fixing.

| Type | Example | Fix type |
|------|---------|----------|
| **Procedural** | Forgot Brinc busy block | Code enforcement — wrong action made impossible |
| **Retrieval** | Used wrong API endpoint | Action-triggered memory_search before the action |
| **Overclaim** | "I documented this last night" (unverified) | Hard gate — cannot claim done without citing file+line |
| **Stale context** | Used expired token | Session-start load of canonical references |
| **Judgment** | Didn't diagnose before acting (whack-a-mole) | PPEE checklist — can't be code, but can be a hard prompt |

These need different solutions. Bundling them into "better documentation" is why nothing has worked.

---

## The Plan

### Phase 1: Code Enforcement (highest leverage — do first)

For every **procedural** mistake: make the wrong action structurally impossible.

Already done today:
- `cal_create` unconditionally adds Brinc busy block — no flag to forget
- Stale OAuth token file renamed to `.DEPRECATED` — can't be reached by accident

Remaining procedural rules to code-enforce (audit MEMORY.md for these):
- Any script that calls the MC API uses `/api/tasks` for GET — enforce with a wrapper
- Any external send (email, webhook) that should have a Brinc-equivalent → add validation layer
- Identify all other "flag defaults to False" patterns in the codebase

**Deliverable:** A list of procedural rules that are now in code, with the MEMORY.md lesson they replace. Remove those lessons from MEMORY.md after code is verified.

### Phase 2: Action-Triggered Retrieval

For every **retrieval** mistake: surface the right rule at the right moment.

Instead of loading everything at session start and hoping, query `memory_search` right before each action type.

Proposed gates in AGENTS.md:
- **Before any calendar operation:** `memory_search("calendar booking rules SA token")`
- **Before any MC API call:** `memory_search("mission control API endpoints")`
- **Before any Railway/infra change:** `memory_search("OpenClaw config rules bind tailscale")`
- **Before claiming something is done:** cite exact file + line, or say "I need to do that" instead

This doesn't require perfect session-start loading. It retrieves on demand, at the moment of action.

**Deliverable:** Updated AGENTS.md with pre-action retrieval gates. These gates should be short enough that they actually get followed.

### Phase 3: Session Loading Protocol

Define exactly what loads, in what order, at session start — and make sure it's right.

Currently loaded as project context (from OpenClaw config):
- AGENTS.md, SOUL.md, USER.md, TOOLS.md, IDENTITY.md, MEMORY.md, HEARTBEAT.md, BOOTSTRAP.md, PRIORITY_BRIEFING.md

Problems:
- MEMORY.md is 16.7KB — loads into context but is too dense to absorb
- SOUL.md is 10.6KB and 17 days stale — loads a slightly wrong version of Molty
- AGENTS.md now has the right pre-action gates (Phase 2) — but needs to be short enough to read

**Changes:**
- MEMORY.md target: **4KB hard cap** — session-hot facts only, everything else moves to `memory/refs/` where it's retrieval-accessible
- SOUL.md: trim to under 4KB — core persona only, not a full ops manual; reviewed with Guillermo before committing
- IDENTITY.md: update to March 2026 reality (Raphael + Leonardo are live, not pending)
- AGENTS.md: restructure as a short tiered checklist, not a wall of rules

**What "session-hot" means:** information needed within 60 seconds of waking up, before any retrieval step. Everything else can live in `memory/refs/` and be retrieved on demand.

### Phase 4: Mistake Tracker (measurement)

Without measurement, there's no way to know if any of this is working.

A simple `memory/refs/mistake-tracker.md`:

```
| Date | Mistake | Type | Fix Applied | Recurrences |
|------|---------|------|-------------|-------------|
| 2026-03-04 | Used /api/task (singular) for GET | Retrieval | Code wrapper | 0 |
| 2026-03-04 | No Brinc busy block on passport | Procedural | cal_create unconditional | 0 |
| 2026-03-04 | OAuth token instead of SA token | Retrieval | Token deprecated + docs | 0 |
| 2026-03-04 | Claimed "documented last night" without citing | Overclaim | Hard gate in AGENTS.md | 0 |
```

Rules:
- Every mistake Guillermo calls out → logged here within the same session
- Recurrence count increments every time it happens again
- If recurrence count > 0, the fix was insufficient — escalate to code enforcement or a stronger gate
- Reviewed at weekly standup and monthly core file review

**This is the feedback loop that was missing.** Not a vague "lessons learned" file — a specific tracked list of exact mistakes with fix status and recurrence data.

### Phase 5: MEMORY.md Cull + refs/ Refresh

Now that phases 1–4 are defined, the cull has clear rules:

**Remove from MEMORY.md:**
- Any lesson whose rule is now in code → delete entirely (it's enforced, not needed)
- Any lesson that is a retrieval/reference item → move to appropriate `memory/refs/` file
- Any completed project context → move to `memory/refs/` or PARA archive
- Any credential that's also in TOOLS.md → remove duplicate

**Keep in MEMORY.md (session-hot only):**
- Guillermo contact info (quick-ref for messaging)
- Active project status: one line per project (Brinc, Cerebro, fleet)
- Agent URLs + key tokens (infrastructure quick-ref)
- The top 5–8 rules that are genuinely not yet in code and not retrieval-accessible

**Refresh `memory/refs/`:**
- `lessons-learned.md` — currently 12.5KB from Feb 14. Audit: what's obsolete, what needs updating through Mar 4
- `infrastructure.md` — update for Raphael outage fix, bind/tailscale rules
- `credentials.md` — verify all entries still accurate
- Other refs files: flag staleness dates

**PARA — reduced scope:**
Opus is right that PARA is over-engineered for an amnesiac agent. Revised scope:
- PARA = archival only. Completed plans, historical project context, deep reference.
- Not operational. Not retrieved at session start.
- `para_curation.py` — fix it to actually move completed plans to archive. That's its real job.
- Stop pretending PARA is operational memory. It's an archive. That's fine. That's enough.

### Phase 6: Core Files Refresh

Last, not first — because Phase 1–4 will reveal what actually needs to change.

**SOUL.md:**
- Add: Molty's known failure modes and specific responses to them (not aspirational, factual)
- Add: What Guillermo actually cares about (from 3 weeks of operation, not a first interview)
- Remove: anything that hasn't proven true in practice
- Trim from 10.6KB to under 4KB — core persona, not an ops manual
- **Guillermo reviews before committing** — SOUL.md is too important to change unilaterally

**IDENTITY.md:**
- Update: Raphael and Leonardo are live (not "pending")
- Update: actual domains Molty owns vs. coordinates vs. stays out of
- Add: honest operational limitations (session amnesia, retrieval-dependent, not self-correcting without mechanical enforcement)

### Phase 7: Maintenance Cadence

Sustainable only if mechanical:

| Frequency | What | Mechanism |
|-----------|------|-----------|
| Every session | Pre-action retrieval gates | AGENTS.md checklist |
| Every mistake | Log to mistake-tracker.md, classify, fix | AGENTS.md rule + Guillermo calls out |
| Weekly Friday | PARA curation (archive completed plans), mistake tracker review | para_curation.py + standup |
| Monthly 1st | SOUL.md + IDENTITY.md review, MEMORY.md size check | Cron prompt |
| Monthly 1st | If MEMORY.md > 5KB — mandatory cull before end of day | Cron + hard rule |

Monthly review is a cron-prompted session, not a hope. It shows up in PRIORITY_BRIEFING.md and can't be skipped.

---

## Execution Sequence

1. **Tonight (overnight session):** Phase 1 (code enforcement audit + fixes) + Phase 4 (mistake tracker seeded with today's incidents)
2. **This week:** Phase 2 (AGENTS.md retrieval gates) + Phase 3 (session loading — MEMORY.md cull, SOUL.md draft)
3. **At standup (Mar 4 5PM):** Guillermo reviews SOUL.md draft
4. **After standup approval:** Phase 5 (refs refresh) + Phase 6 (commit core files)
5. **End of week:** Phase 7 (maintenance crons verified)

---

## What's Not In This Plan (deliberately)

- Elaborate PARA folder hierarchy — too complex for an amnesiac agent
- 90-day lesson expiry without mechanical enforcement — won't happen
- Weekly curation scripts that process 0 files — we'll keep PARA as archival only, fix curation script to do one real job

---

## Success Metrics

**2 weeks:** Mistake-tracker.md has 0 recurrences on mistakes logged today.
**1 month:** No new procedural mistakes (those are now in code). Retrieval mistakes rate < 1/week.
**90 days:** Guillermo doesn't call out the same mistake twice in a single month.

Measured from mistake-tracker.md, not vibes.

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Over-culling MEMORY.md | Every removed lesson has a forwarding pointer: `→ see memory/refs/X.md` |
| SOUL.md edit loses voice | Guillermo reviews draft before commit |
| Plan sits unactioned | MC task created + overnight session scheduled tonight |
| Fleet agents not covered | Molty-first. Once proven: Raphael + Leonardo get the same treatment. |
| Phases 2+ never happen after Phase 1 | Phase 1 deliverable includes a specific list of what phases 2+ must address |

---

*Status: Ready for Guillermo review. Do not execute until approved.*
