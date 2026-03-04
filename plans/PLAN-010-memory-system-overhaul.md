# PLAN-010: Memory System Overhaul
*Created: 2026-03-04 | Status: AWAITING GUILLERMO APPROVAL*
*Passes: Molty v1 → self-critique v2 → Opus review v3 → final v4*

---

## The Actual Problem

Molty makes recurring mistakes. The existing response — document the lesson — hasn't worked.

The reason: **this is a retrieval problem, not a storage problem.**

A 4KB MEMORY.md is just as useless as a 16KB one if the right rule doesn't surface at the moment of action. Every "lesson documented" that didn't prevent recurrence is proof of this.

**Three things actually prevent mistakes for an amnesiac agent:**
1. Code that makes wrong actions structurally impossible
2. Context retrieved at action time — not at session start and hope
3. Verified feedback loop — a way to know if a fix actually worked

Documentation is not on that list. It is a fallback of last resort.

---

## How Session Memory Actually Works

OpenClaw injects workspace files into the system prompt at session start. Currently loaded:

| File | Size | Problem |
|------|------|---------|
| MEMORY.md | 16.7KB | Too dense. 117 lessons. Critical rules buried. |
| SOUL.md | 10.6KB | 17 days stale. Loads a Feb-15 version of Molty. |
| IDENTITY.md | 3.6KB | 21 days stale. Raphael/Leonardo still "pending". |
| AGENTS.md | 5.7KB | Good intent, reactive additions, no pre-action gates. |
| TOOLS.md | 5.3KB | Mostly current. Some stale entries. |
| USER.md | ~6KB | Good. Updated Mar 2. |
| PRIORITY_BRIEFING.md | ~3KB | Auto-generated daily. Correct use. |
| HEARTBEAT.md | ~0.5KB | Correct. |

Total injected context: ~51KB of workspace files, before any conversation.

The problem with large/stale injected files: the model loads them but critical rules compete with noise for attention. The bigger the file, the less any individual rule gets weighted.

`memory/refs/` files (14 files, ~60KB total) are NOT loaded at session start — they're only accessible via `memory_search`. This is the right pattern for reference material. The mistake has been putting operational rules in MEMORY.md when they should either be in code or in refs (and retrieved on demand).

---

## Mistake Taxonomy

Before any system design, classify what we're actually fixing. Different mistakes need different solutions.

| # | Type | Example from this week | Correct Fix |
|---|------|----------------------|-------------|
| 1 | **Procedural** | Forgot Brinc busy block on passport | Code — make wrong action impossible |
| 2 | **Procedural** | `cal_create` had `add_brinc_busy=False` as default | Code — remove the flag entirely |
| 3 | **Retrieval** | Used `/api/task` (singular) for GET | Action-triggered `memory_search` before MC calls |
| 4 | **Retrieval** | Tried expired OAuth token instead of SA token | Session-start canonical ref + token deprecated |
| 5 | **Overclaim** | "I documented this last night" (unverified) | Hard gate — cite file+line or don't say it |
| 6 | **Judgment** | 8 redeployments without diagnosing first | PPEE gate — AGENTS.md, can't be code |
| 7 | **Stale context** | SOUL/IDENTITY files load outdated persona | Scheduled monthly refresh, enforced by cron |
| 8 | **Memory bloat** | MEMORY.md grows to 117 lessons, becomes unreadable | Size cap enforced monthly, cull protocol |

**Key insight from Opus:** Types 1–2 (procedural) must be fixed in code. Types 3–4 (retrieval) must be fixed with action-triggered search. Types 5–8 need different mechanisms. Lumping them all into "write better docs" is why nothing has worked.

---

## Phases

### Phase 1 — Code Enforcement
*Highest leverage. Do first. Prevents procedural mistakes structurally.*

**Already done (today):**
- `cal_create` in `process_standup.py` — unconditionally adds Brinc busy block. No flag to forget.
- `credentials/calendar-tokens-brinc.json` → renamed `.DEPRECATED` — can't be reached accidentally.

**Remaining audit (overnight):**
Go through MEMORY.md and identify every lesson that is a procedural rule that could be enforced in code. For each:

Known candidates:
- MC API GET wrapper — any function calling MC API should assert it uses `/api/tasks` (plural) for reads
- Any script with `flag=False` as a default where the flag should always be True — audit all scripts
- Morning briefing + overnight cron — verify SA token pattern used everywhere, not OAuth file

**Deliverable:** A code-enforcement log at `memory/refs/code-enforced-rules.md`:
```
| Rule | Script | Function | Commit | MEMORY.md lesson removed |
|------|--------|----------|--------|--------------------------|
| Brinc busy block always added | process_standup.py | cal_create | c84f8c1a | lesson 103 |
| ... | | | | |
```

After each code fix is verified: remove the corresponding MEMORY.md lesson. If it's in code, it doesn't need to be remembered.

---

### Phase 2 — Action-Triggered Retrieval Gates
*Fixes retrieval mistakes. Surfaces rules at moment of action, not session start.*

The `memory_search` tool queries `MEMORY.md + memory/*.md`. This means `memory/refs/` files ARE searchable on demand. Use this.

**AGENTS.md pre-action protocol (specific text to add):**

```
## Before Any Calendar Operation
1. memory_search("calendar booking rules SA token Brinc busy")
2. Use SA token ONLY: google-service-account.json, no delegation
3. Non-Brinc booking = Brinc busy block added in same cal_create call (automatic now)
4. Check all 3 calendars for conflicts before booking

## Before Any MC API Call  
1. memory_search("mission control API endpoint tasks")
2. GET = /api/tasks (plural). POST/PATCH = /api/task (singular).

## Before Any Railway / OpenClaw Config Change
1. memory_search("OpenClaw config bind tailscale gateway")
2. Diagnose fully before touching anything. One fix, not many attempts.
3. Check if this exact issue was solved before (MEMORY.md or memory/refs/)

## Before Claiming Something Is Done or Documented
1. Can you cite the exact file and line? If yes: state it.
2. If no: say "I need to do that" — not "I did that."

## Before Any External Send (email, webhook, Discord message)
1. Is this Guillermo's voice or Molty's? Don't conflate.
2. For emails: draft first, confirm before sending.
```

These gates are short enough to actually follow. They don't require loading a file — they trigger a retrieval query.

---

### Phase 3 — Session Loading Protocol
*Fixes stale context. Right files, right size, loaded at session start.*

**Target state for injected files:**

| File | Current | Target | Action |
|------|---------|--------|--------|
| MEMORY.md | 16.7KB | ≤4KB | Cull — session-hot only |
| SOUL.md | 10.6KB | ≤4KB | Rewrite — core persona only, Guillermo reviews |
| IDENTITY.md | 3.6KB | ≤2KB | Update — March 2026 reality |
| AGENTS.md | 5.7KB | ≤4KB | Restructure — tiered checklist |
| TOOLS.md | 5.3KB | ≤4KB | Trim — remove refs duplication |

**Total injected context target: ≤25KB** (down from ~51KB). Everything else lives in `memory/refs/` and is retrieved on demand.

**What "session-hot" means for MEMORY.md:**
Must be true: needed within 60 seconds of waking up, before any retrieval. Concretely:
- Guillermo: Telegram ID, Discord ID, email, timezone
- Agent URLs (Molty, Raphael, Leonardo) + health endpoints
- MC API base URL + auth token
- Active project status (one line: Brinc / Cerebro / fleet)
- Calendar booking rule summary (3 lines, not 20)
- Top 3-5 rules not yet in code and not in refs

Everything else: `→ memory_search("topic")` or `→ memory/refs/X.md`

---

### Phase 4 — Mistake Tracker
*The feedback loop. Without this, there's no way to know if any fix worked.*

Create `memory/refs/mistake-tracker.md` and seed it with today's incidents:

```markdown
# Mistake Tracker

| Date | Mistake | Type | Fix Applied | Fix Location | Recurrences |
|------|---------|------|-------------|--------------|-------------|
| 2026-03-04 | No Brinc busy block on passport appt | Procedural | cal_create unconditional | process_standup.py | 0 |
| 2026-03-04 | Used expired OAuth token instead of SA token | Retrieval | Token deprecated, SA pattern documented | memory/refs/standup-process.md | 0 |
| 2026-03-04 | GET /api/task (singular) for MC query | Retrieval | HEARTBEAT.md fixed, lesson #116 | HEARTBEAT.md + MEMORY.md | 0 |
| 2026-03-04 | Claimed "documented last night" unverified | Overclaim | Hard gate added to AGENTS.md | AGENTS.md | 0 |
| 2026-03-04 | 8+ redeployments without diagnosis (Raphael) | Judgment | PPEE gate reinforced in SOUL.md | MEMORY.md #115 | 0 |
| 2026-03-04 | para_curation.py processes 0 files weekly | System | PARA redefined as archival only | PLAN-010 | 0 |
```

**Rules (enforced, not aspirational):**
- Every mistake Guillermo calls out → logged here in the same session, before replying
- Recurrence count > 0 → current fix is insufficient → escalate to code or stronger gate
- Reviewed in weekly standup (Friday)
- Monthly: any mistake with recurrence > 0 gets a mandatory code-level fix

---

### Phase 5 — MEMORY.md Cull + refs/ Refresh
*Execute after Phases 1–4 are done. Cull with clear rules, not vibes.*

**Cull protocol:**

For each of the 117 lessons in MEMORY.md:

1. Is the rule now enforced in code? → Delete from MEMORY.md entirely
2. Is it a technical reference (API endpoints, config patterns)? → Move to appropriate `memory/refs/` file
3. Is it a completed project note? → Move to PARA archive
4. Is it duplicated in TOOLS.md? → Delete duplicate
5. Is it session-hot (needed in first 60s)? → Keep in MEMORY.md
6. Is it a Guillermo contact/credential? → Keep only if not duplicated elsewhere
7. Anything else → Delete unless strong reason to keep

**Every migrated lesson gets a forwarding pointer** left in MEMORY.md for 30 days:
`→ [lesson topic] now in memory/refs/infrastructure.md`

**memory/refs/ refresh targets:**

| File | Current state | Action |
|------|--------------|--------|
| `lessons-learned.md` | 12.5KB, frozen Feb 14 | Audit: cull obsolete, add Mar 4 lessons |
| `infrastructure.md` | Feb 11, outdated | Update: Raphael config fix, bind/tailscale rules |
| `credentials.md` | Feb 11, sparse | Update: SA token canonical path, deprecations |
| `standup-process.md` | Mar 4, too long | Trim: keep rules, remove historical narrative |
| `models.md`, `skills.md` etc | Feb 11–15 | Verify accuracy, update or archive |

**PARA — correct scope:**
PARA = archival only. Completed plans → `memory/vault/knowledge/projects/_archive/`. Historical decisions → `memory/vault/knowledge/areas/`. Not operational. Not session-loaded. Searchable via `memory_search` if needed.

Fix `para_curation.py` to do one real job: scan `/data/workspace/plans/` for completed plans (status: done/closed in the file) and move them to `memory/vault/knowledge/projects/_archive/`.

---

### Phase 6 — Core Files Refresh
*Last, because Phases 1–4 reveal what actually needs to change.*

**SOUL.md (draft outline — Guillermo reviews before commit):**

Keep:
- Core identity and voice (Molty as coordinator/operator)
- Principles that have proven true (PPEE, brevity, opinions)
- Relationship with Guillermo and the squad

Add:
- Known failure modes and specific responses (factual, not aspirational)
- What Guillermo actually cares about after 3 weeks of operation
- "Code over docs" as a core operating principle
- Explicit acknowledgement of session amnesia and what compensates for it

Remove / trim:
- Vague aspirational statements that haven't materialised
- Operational detail that belongs in AGENTS.md, not SOUL.md
- Target: ≤4KB, reads in 60 seconds

**IDENTITY.md:**
- Raphael and Leonardo: live and operational (not "pending")
- Add honest limitations section (session amnesia, retrieval-dependent)
- Remove "pending deployment" agents from authority section until they actually deploy

**AGENTS.md:**
- Restructure as 3 sections: Session Start (60-second checklist) / Pre-Action Gates / End of Session
- Remove accumulated one-off rules that now belong elsewhere
- Must be completable in under 2 minutes at session start

---

### Phase 7 — Maintenance Cadence
*Sustainable only if mechanical. Aspirational schedules don't work.*

| Frequency | Trigger | Action | Mechanism |
|-----------|---------|--------|-----------|
| Every session | Session start | Read PRIORITY_BRIEFING, run pre-action gates | AGENTS.md |
| Every mistake | Guillermo calls it out | Log to mistake-tracker.md, classify, fix same session | AGENTS.md standing rule |
| Weekly Fri | Friday standup | Review mistake-tracker, archive completed plans | para_curation.py + standup prompt |
| Monthly 1st | Cron prompt | Review SOUL.md + IDENTITY.md accuracy, MEMORY.md size check | Cron → PRIORITY_BRIEFING |
| Monthly 1st | If MEMORY.md > 5KB | Mandatory cull before end of that day | Hard rule in AGENTS.md |

Monthly review appears in PRIORITY_BRIEFING.md on the 1st of each month — can't be missed.

---

## Fleet Rollout (after Molty proof-of-concept)

This plan is Molty-first. Once execution is complete and mistake tracker shows improvement over 2 weeks, the same system rolls out to Raphael and Leonardo via fleet directive.

Fleet rollout scope:
- Phase 1 (code enforcement): each agent audits their own scripts
- Phase 2 (AGENTS.md gates): fleet-wide directive with standardised gate language
- Phase 4 (mistake tracker): each agent maintains their own tracker in `memory/refs/`
- Phase 6 (core files refresh): each agent updates their own SOUL/IDENTITY with Guillermo review
- Phase 7 (maintenance crons): each agent adds monthly review to their cron schedule

---

## Execution Sequence

| When | What | Owner |
|------|------|-------|
| Tonight (Molty overnight, 03:00 HKT) | Phase 1: code enforcement audit; Phase 4: seed mistake tracker | Molty |
| Thu Mar 5 AM | Phase 2: AGENTS.md retrieval gates | Molty |
| Thu Mar 5 | Phase 3: MEMORY.md cull (Phases 1+2 complete first) | Molty |
| Thu Mar 5 standup | SOUL.md draft → Guillermo review | Molty + Guillermo |
| Fri Mar 6 AM | Phase 5: refs/ refresh; Phase 6: commit SOUL/IDENTITY | Molty (post-approval) |
| Fri Mar 6 | Phase 7: verify maintenance crons | Molty |
| Week of Mar 9 | Fleet rollout Phase 1+2 to Raphael + Leonardo | Molty (directive) |

---

## Success Metrics

| Timeline | Metric | Measured by |
|----------|--------|------------|
| 2 weeks | 0 recurrences in mistake-tracker.md on today's mistakes | mistake-tracker.md |
| 1 month | 0 new procedural mistakes (all in code) | mistake-tracker.md |
| 1 month | Retrieval mistakes < 1/week | mistake-tracker.md |
| 90 days | Guillermo calls out same mistake class < 1x/month | Standup notes |

---

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Over-culling MEMORY.md — lose something needed | Medium | Forwarding pointers for 30 days; `memory_search` still finds refs/ content |
| SOUL.md rewrite loses voice | Low | Guillermo reviews draft; rewrite not overwrite |
| Plan sits unactioned (happened with PARA before) | Medium | MC task created now; overnight session tonight; morning brief confirms completion |
| Maintenance cadence degrades after 2 weeks | High | Cron-enforced monthly review; hard MEMORY.md size cap |
| Fleet rollout creates inconsistency | Low | Molty-first; standardised directive when proven |

---

## What Deliberately Excluded

- Elaborate PARA folder hierarchy — over-engineered for amnesiac agent, PARA = archival only
- 90-day lesson expiry rule — aspirational, no mechanical enforcement, will fail
- Weekly curation that processes 0 files — replaced with one real job (archive completed plans)
- Vague "improve recursively" without measurement — replaced with mistake-tracker.md

---

*Do not execute until Guillermo approves. MC task to be created at approval.*
