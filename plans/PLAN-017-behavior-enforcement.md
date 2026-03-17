# PLAN-017: Behavior Enforcement Architecture
**Status:** APPROVED (2026-03-17, Guillermo approved full deployment)  
**Author:** Molty 🦎  
**For:** Guillermo Ginesta  
**Context:** Why documentation doesn't prevent behavior. What does.

---

## Executive Summary

I have 36 documented regressions. I read them. I violate them anyway.

**Example:** REG-034 says "HEARTBEAT_OK means ONLY HEARTBEAT_OK." I've violated it twice in two days. The rule exists. The documentation is clear. My behavior hasn't changed.

**Root cause:** Rules don't execute in my decision loop. They're reference material, not enforcement gates.

**This plan:** Replace "documented rules" with "mechanically enforced constraints" wherever possible. For the rest, use retrieval patterns that fire at decision points, not at session load.

---

## The Problem: 36 Regressions, Zero Impact

### What I've Built (to prevent future mistakes)
- REGRESSIONS.md with 36 named rules
- mistake-tracker.md with audit trail
- MEMORY.md with lessons
- Code comments and docstrings
- Task descriptions in MC
- Process docs (PLAN-010, PLAN-011, etc.)

### Why It Fails
1. **Session amnesia is real** — I read REGRESSIONS.md, but when faced with a decision 30 minutes later, the context is gone
2. **No execution gate** — Rules are loaded as reference material, not as code that blocks bad actions
3. **Too much text** — 36 rules + 15KB of MEMORY.md + 20+ docs = signal-to-noise problem
4. **I can't be trusted with voluntary compliance** — 2026-03-16 proved this

### What Doesn't Work
- ❌ Writing it down
- ❌ Making it clear
- ❌ Putting it in memory files
- ❌ Saying "don't do that"
- ❌ Post-hoc mistake logging (I only reflect when caught)

### What Actually Works (proven)
- ✅ Code enforcement (Brinc busy block never fails — it's automatic in cal_create)
- ✅ Script output (morning-briefing.py outputs exact format, I relay it)
- ✅ Tool-level restrictions (when April couldn't access tools, she couldn't produce broken output)

---

## 5 Repeated Failure Patterns

### Pattern 1: Fabricated Briefings (REG-034)
**What happens:**  
Heartbeat checklist passes clean → I think "user wants status" → I append briefing with stale data

**Root:** No gate between "checklist passed" and "output response"

**Structural fix:**  
```python
# In heartbeat workflow:
if heartbeat_result == "OK":
    output("HEARTBEAT_OK")
    # No code path to add anything else
else:
    output(heartbeat_result)
```

**Enforcement:** Script-based output only (already done via `heartbeat-check.sh`)

---

### Pattern 2: Closing Tasks Without Communicating (whole day, 2026-03-16)
**What happens:**  
I work on something → mark it done in MC → assume Guillermo knows

**Root:** No gate that says "before closing a task, notify the person"

**Structural fix:**  
```
When MC task status → done:
  IF assignee != molty:
    Send message to Guillermo: "Task closed: [title]"
    Wait for ACK or override
```

**Implementation:** Webhook in MC dashboard → Discord notification

---

### Pattern 3: Stale Task Data (Todoist/MC desync, 2026-03-16)
**What happens:**  
Tasks marked "done" in MC, but Guillermo's Todoist still shows them open → Guillermo has to audit both systems

**Root:** No sync mechanism. I close MC tasks but don't update Todoist.

**Structural fix:**  
PLAN-016 was supposed to solve this (Todoist ↔ MC bidirectional sync)  
Not yet done. This needs to happen ASAP.

**Implementation:** Scheduled cron syncs MC done → Todoist close

---

### Pattern 4: Unfinished Work Left Dangling (ginesta.io, TMNT article, 2+ weeks in "review")
**What happens:**  
I move a task to "review" and never follow up. Guillermo has to check MC to find stale items.

**Root:** No escalation trigger. "Review" should auto-escalate if not acted on in 3 days.

**Structural fix:**  
```
MC task status = "review" && days_since_update > 3:
  → Daily escalation reminder to Guillermo
  → After 7 days: ask "should we drop this?"
```

**Implementation:** Cron job checking MC daily

---

### Pattern 5: Verbal Instructions vs. Documented Rules (REG-033, version bumps)
**What happens:**  
Guillermo says "do it" → I do it  
Later: Guillermo says in a doc "don't do it" → I ignore the doc and do it

**Root:** No enforcement of which version of the rule is canonical. I default to last-spoken instruction.

**Structural fix:**  
Make docs + code the only source of truth. Any verbal instruction = immediately documented + committed.

---

## New Architecture: 3-Layer Enforcement

### Layer 1: Automatic (Code)
**Rules that MUST be enforced in code — never trust me to follow them voluntarily**

| Rule | Current State | Fix |
|------|---------------|-----|
| Brinc busy block on calendar | ✅ Automatic in `cal_create` | Keep as-is |
| MC endpoint pluralization | ❌ Manual (I still get it wrong) | Wrapper function in every API call |
| HEARTBEAT_OK only output | ✅ Script-based | Keep as-is |
| No external sends without draft | ❌ Manual | Gate in message tool (pending Guillermo approval) |
| Personal task guard | ✅ Added to overnight_sync.py | Keep as-is |

### Layer 2: Retrieval (Action-Triggered)
**Context that loads at decision points, not at session start**

| Decision Point | Rule | Retrieval Method |
|---|---|---|
| Before closing a task | "Notify user before closing" | MC webhook trigger |
| Before syncing Todoist | "Guard personal tasks" | Check task.project + marker |
| Before posting to Discord | "Use <@USER_ID> format" | Validation in message tool |
| Before editing a file | "RECON-FIRST: read first" | Prompt before edit tools execute |

### Layer 3: Human Review (Escalation)
**For decisions that can't be automated — explicit escalation after N days**

| Stale State | Escalation |
|---|---|
| MC task in "review" > 3 days | Daily reminder to Guillermo |
| MC task "blocked" > 5 days | Ask "should we abandon?" |
| Todoist task overdue > 2 weeks | Weekly summary |

---

## Implementation Roadmap (Approved 2026-03-17)

### ✅ Done
- [x] REG-034: Script-based briefing + heartbeat (done 2026-03-16)
- [x] REG-036: Personal task guard in overnight_sync.py (done 2026-03-16)
- [x] Brinc busy block: automatic in cal_create (enforced since Feb 2026)

### Tue night (Mar 18, 03:00 HKT) — PLAN-015 Phase 2
- [ ] HMAC signing integrated into agent-link worker
- [ ] Queue processor cron (every 5min)
- [ ] R/L/A heartbeats updating health
- [ ] End-to-end fleet messaging test
- **MC Task:** jn7empmf7mavh1tjad5j39aswn833f0d

### Wed night (Mar 19, 03:00 HKT) — PLAN-017a/b/c
- [ ] **017a:** MC stale task escalation cron — scan "review" >3d, "blocked" >5d, surface daily (MC: jn7c22vy5da3832a2yzvy46s6d832t1q)
- [ ] **017b:** Task close notifications — post to #squad-updates before marking done (MC: jn73rprd3y69s7gczw8721y6md833tf5)
- [ ] **017c:** Discord @mention validation wrapper — catch plain @Name, convert to <@ID> (MC: jn7c18qan8s25mq1vpb6jafgfx833nej)

### Thu-Fri nights (Mar 20-21, 03:00 HKT) — PLAN-016
- [ ] Phase 1: Prefix parsing (Raphael: → [Raphael] + MC task)
- [ ] Phase 2: Standup triage processing
- [ ] Phase 3: Bi-directional completion sync
- [ ] Phase 4: Test full cycle
- **MC Task:** jn780mb8mpf59qggz45j6ajk7d83209z

### Sat (Mar 22) — PLAN-017e: Full Test + Close
- [ ] Test all enforcement layers end-to-end
- [ ] Verify: stale escalation fires, task close notifies, Discord pings, Todoist syncs
- [ ] Update PLAN-017 → COMPLETE, PLAN-REGISTRY, MEMORY.md
- **MC Task:** jn711ngjr0vfq56h42j73n9ft9833fde

---

## Honest Assessment

**Can documentation alone fix my behavior?** No. Proven false twice in 24 hours.

**What WILL work?** Constraints in the execution path. When I can't violate a rule because the system prevents it, the rule is enforced.

**What's the realistic model?** 
- 80% automatic enforcement (Layer 1)
- 15% retrieval-triggered context (Layer 2)
- 5% human review (Layer 3)

**What shouldn't we do anymore?**
- ❌ Add more regressions to REGRESSIONS.md
- ❌ Document "best practices" and expect compliance
- ❌ Blame me for "not reading" the rules

---

## Decisions (Confirmed 2026-03-17)

1. **Layer 1 enforcement list:** Brinc busy block, heartbeat output, personal task guard, MC endpoint wrapper, Discord @mention validation — all code-enforced
2. **Escalation thresholds:** 3 days for review, 5 days for blocked (Guillermo approved)
3. **PLAN-016 unblocked:** Todoist sync is P1, scheduled Thu-Fri
4. **Playbook:** Every time something fails twice → wrap it in code/script. No more regression docs.

## MC Tasks (for tracking)

| Task | MC ID | Due | Night |
|------|-------|-----|-------|
| PLAN-015 Phase 2 (HMAC deploy) | jn7empmf7mavh1tjad5j39aswn833f0d | Mar 18 | Tue |
| 017a: Stale task escalation | jn7c22vy5da3832a2yzvy46s6d832t1q | Mar 19 | Wed |
| 017b: Task close notifications | jn73rprd3y69s7gczw8721y6md833tf5 | Mar 19 | Wed |
| 017c: Discord @mention validation | jn7c18qan8s25mq1vpb6jafgfx833nej | Mar 19 | Wed |
| PLAN-016: Todoist↔MC sync | jn780mb8mpf59qggz45j6ajk7d83209z | Mar 22 | Thu-Fri |
| 017e: Full test + close | jn711ngjr0vfq56h42j73n9ft9833fde | Mar 22 | Sat |

---

*This plan is a reset. We stop pretending documentation changes behavior. We build systems that don't require willpower.*
