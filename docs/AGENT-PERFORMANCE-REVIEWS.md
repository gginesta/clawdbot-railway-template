# Agent Performance Review Framework
<!-- Last updated: molty | 2026-03-06 | Initial creation -->

**Version:** 1.0  
**Created:** 2026-03-06  
**Owner:** Molty 🦎 (Fleet Coordinator)  
**Inspired by:** Kevin Simback's agent management article  

---

## Philosophy

Performance reviews are **for learning and improvement, not gatekeeping.** Every agent gets full autonomy from day 1. Reviews exist to help agents do better work and to help Guillermo understand how the fleet is performing.

> *"Trust + coaching > restrictions"* — Guillermo, Mar 2026

---

## Review Cadence

| Type | Frequency | Trigger |
|------|-----------|---------|
| **Milestone Review** | After each major project/plan completion | Auto: whenever MC task marked done with plan reference |
| **Monthly Review** | First Monday of each month | Cron: 09:00 HKT |
| **Incident Review** | Within 24h of a significant failure/mistake | Manual: Guillermo or Molty triggers |
| **Onboarding Review** | 2 weeks after new agent deploys | One-shot cron at agent deploy |

---

## Who Reviews

- **Primary reviewer:** Molty 🦎 (compiles, writes first draft)
- **Approver:** Guillermo (reviews, adds comments, signs off)
- **Self-assessment:** Each agent writes a self-section (optional but encouraged)

---

## Evaluation Criteria

### 1. Output Quality (0–5)
- Does the work meet the brief?
- Is the output accurate, well-structured, and complete?
- Does it need Guillermo to fix things after delivery?

### 2. Goal Completion Rate (0–5)
- What % of assigned tasks were completed vs skipped/failed?
- Were time budgets respected (overnight: 90-min target)?
- Were blockers surfaced early or did tasks stall silently?

### 3. Judgment & Autonomy (0–5)
- Did the agent make good calls without needing to ask?
- When the agent flagged something, was the flag warranted?
- Did it avoid over-flagging trivial decisions to Guillermo?

### 4. Communication Quality (0–5)
- Are MC updates clear and timely?
- Are failure reasons specific (not just "it failed")?
- Are blocked tasks unblocked with a specific ask (not vague)?

### 5. Collaboration (0–5)
- Does the agent coordinate well with other agents?
- Are shared files updated correctly with headers?
- Does it acknowledge others' work in group channels?

### 6. Learning Velocity (qualitative)
- Are the same mistakes repeated across sessions?
- Has the agent improved on previously noted weaknesses?
- Did new skills or approaches appear this period?

---

## Rating Scale

| Score | Label | Meaning |
|-------|-------|---------|
| 5 | ⭐ Exceptional | Exceeded expectations, creative solution, zero rework |
| 4 | ✅ Strong | Met brief fully, minor polish only |
| 3 | 🟡 Solid | Mostly good, one notable gap |
| 2 | ⚠️ Developing | Significant gaps but effort visible |
| 1 | 🔴 Needs Work | Missed the mark, fundamental issues |

Overall score = average across 5 rated dimensions. Learning Velocity is qualitative only.

---

## Feedback Loop

1. **Molty writes draft** → saves to `/data/workspace/reviews/YYYY-MM-{agent}-review.md`
2. **Guillermo reviews** → adds inline comments, approves
3. **Post to MC** → POST `/api/task` with review summary + link
4. **Share with agent** → Post in agent's private Discord channel (e.g., #brinc-private for Raphael)
5. **Agent acknowledges** → replies in channel, updates SOUL.md if needed
6. **Archive** → Move to `/data/workspace/reviews/archive/` after 90 days

---

## Storage

| Location | What |
|----------|------|
| `/data/workspace/reviews/` | Active + recent reviews |
| `/data/workspace/reviews/archive/` | Reviews older than 90 days |
| MC task feed | Summary post after each review |
| Agent's private Discord channel | Review notification + agent response |

---

## Review Template

See: `/data/workspace/templates/agent-review-template.md`

---

## Metrics We Track Over Time

- Average score per agent per month
- Score trend (improving / flat / declining)
- Most common failure category (quality / judgment / communication)
- Task completion rate: assigned → done (vs skipped/blocked)
- Overnight run success rate

---

## Anti-patterns to Avoid

- ❌ Using reviews as punishment or justification for restricting access
- ❌ Reviewing only when something went wrong (do regular reviews too)
- ❌ Vague feedback ("could be better") — always specific
- ❌ Letting reviews pile up and doing 3 at once — review at cadence
- ❌ Skipping self-assessment — agents should reflect too

---

## Fleet Rollout

Once Guillermo approves this framework:
1. Molty posts directive to `#command-center`
2. All agents update their `AGENTS.md` with the Performance Review section
3. Molty schedules the Monthly Review cron
4. First reviews run at end of March 2026

---

*This document is a living framework. Update as the fleet evolves.*
