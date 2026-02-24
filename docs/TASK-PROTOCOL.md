# TASK-PROTOCOL.md — Task Packet Schema, Lifecycle & Examples

*Owner: Molty 🦎 | Created: 2026-02-24*

---

## Purpose

Defines how tasks move from Todoist → Mission Control → Standup. Every task that enters the system should be fully processed before it hits Guillermo's view. "Processed" means it has a clear title, owner, priority, time estimate, and next action.

---

## 1. Task Packet Schema

Every task in the standup should have these fields populated:

| Field | Required | Source | Notes |
|---|---|---|---|
| `title` | ✅ | Rewritten from Todoist | Actionable verb + object. Never raw Todoist import. |
| `owner` | ✅ | Auto-assigned or manual | Guillermo / Molty / Raphael / Leonardo |
| `priority` | ✅ | Todoist P1-P4 | P1=critical, P2=important, P3=normal, P4=someday |
| `status` | ✅ | Lifecycle state | See Section 2 |
| `project` | ✅ | Todoist project | Brinc / Personal / Molty's Den / etc. |
| `time_est` | ✅ | Auto-estimated | 15min / 30min / 1h / 2h+ |
| `due_date` | ⚠️ Optional | Todoist due | Required if overdue or P1 |
| `molty_notes` | ✅ | Generated | Context, blockers, next action. Never "needs triage". |
| `your_notes` | — | Guillermo fills | Blank on creation — Guillermo's column |
| `action` | — | Guillermo fills | Keep / Reschedule / Drop / Delegate / Done |

### Title Rewrite Rules

Raw Todoist titles are often shorthand. Before adding to Notion:
- Add an actionable verb if missing: "IRD reply" → "Reply to IRD tax inquiry"
- Clarify ambiguous references: "Brinc Chile Vietnam" → "Explore Brinc partnership with Startup Chile for Vietnam portfolio"
- Keep under 80 chars
- Remove trailing punctuation

---

## 2. Task Lifecycle

```
[Todoist Inbox]
      ↓  (5PM standup processing)
[Needs Your Input]   ← Guillermo makes a call (Action column)
      ↓
[Active Pipeline]    ← Owner is executing
      ↓
[Done / Blocked]     ← Closed in Todoist → synced to MC
```

### States

| State | Meaning | Owner action |
|---|---|---|
| `inbox` | Just added, unprocessed | Molty processes before standup |
| `assigned` | Owner identified, not started | Owner picks up |
| `in_progress` | Actively being worked | Owner updates progress |
| `review` | Done by owner, needs Guillermo sign-off | Guillermo reviews |
| `done` | Complete | Auto-synced from Todoist close |
| `blocked` | Waiting on dependency | Note blocker explicitly |

### Owner Responsibility

- **Guillermo tasks:** Surface in standup. Don't chase. Flag if overdue >3 days.
- **Molty tasks:** Execute proactively. DO NOT surface in standup unless blocked or needs input. Close in Todoist when done.
- **Raphael / Leonardo tasks:** Route via webhook. Track in MC. Surface blockers only.

---

## 3. Processing Rules (Molty's Standup Prep)

Before generating each standup, Molty runs through every new Todoist task:

1. **Rewrite title** — actionable, clear, no abbreviations
2. **Assign owner** — is this Molty's job or Guillermo's?
3. **If Molty's job:** assign to self, set due date, execute — do NOT put in Guillermo's view
4. **If Guillermo's job:** add to Needs Your Input with full context in Molty's Notes
5. **Set priority** — based on urgency + impact
6. **Estimate time** — honest estimate
7. **Write Molty's Notes** — context + recommended action. Never blank.

---

## 4. Examples

### Example A: Clear Molty task
**Raw Todoist:** `Research kinesiology centres in Hong Kong`  
**Owner:** Molty  
**Processing:** Research it. Write up top 5 with reviews + pricing. Send to Guillermo. Close in Todoist.  
**In standup:** Does NOT appear (Molty owns it, just do it)

### Example B: Ambiguous task needing clarification
**Raw Todoist:** `Brinc startup chile program for Vietnam`  
**Owner:** Guillermo (strategic decision)  
**Rewritten title:** `Evaluate Brinc × Startup Chile partnership for Vietnam`  
**Molty's Notes:** `Startup Chile is CORFO's government accelerator — Brinc could partner to source/accelerate Chilean startups through Vietnam ops. Needs: confirm intent (explore vs execute), assign lead, set timeline.`  
**In standup:** Appears in Needs Your Input — Guillermo decides next action

### Example C: Overdue Guillermo task
**Raw Todoist:** `Fill Brinc Deep Dive Q&A for Raphael` (due Feb 23, overdue)  
**Owner:** Guillermo  
**Molty's Notes:** `⚠️ Overdue 1 day. Raphael is blocked on this for Stream A brand work. Recommend: complete today or delegate to Molty to draft with Raphael's guidance.`  
**In standup:** Appears in Needs Your Input with urgency flag

---

## 5. What "Processed" Means

A task is processed when:
- ✅ Title is clear and actionable
- ✅ Owner is set
- ✅ Molty's Notes has real context (not "needs triage")
- ✅ If Molty's task: it's either done or on a committed timeline
- ✅ If Guillermo's task: he has everything he needs to make a decision in 30 seconds

A task is NOT processed if:
- ❌ Title is raw Todoist shorthand
- ❌ Owner is unclear
- ❌ Molty's Notes says anything like "needs triage", "to be processed", "review when ready"
- ❌ It's a Molty task that's been sitting >24h without action

---

*This protocol applies to all agents. Violations = noise in Guillermo's standup.*
