# PLAN-004 — Squad Overnight Workflow & Mission Control Discipline
*Status: DRAFT — pending approval*
*Owner: Molty | Created: 2026-02-25 | Last updated: 2026-02-25*

---

## Problem

- Tasks pile up and Guillermo is the bottleneck — nothing moves unless he reviews and manually delegates
- Raphael and Leonardo are idle overnight even though they could be shipping
- Mission Control isn't proactively updated — agents only log work when asked
- No standing rule exists for when a task qualifies for MC vs. a one-shot

---

## Goal

By morning standup (incorporated into 06:30 HKT daily brief), Guillermo should see:
- What each agent worked on overnight
- What got completed (with links to deliverables where relevant)
- What's Under Review and needs his input
- What's blocked and needs unblocking
- No surprises, no silent failures

---

## Standing Rules (for all agents — AGENTS.md update)

### Mission Control
- Any task with 3+ steps or spanning multiple sessions → create a full plan, document it in `/data/workspace/plans/`, and create matching MC tasks **before starting work**
- One-shot tasks don't need MC
- Own your MC tasks: update status immediately when it changes (not at end of day)
- Check MC before starting any new work — no duplicate tasks, no ghost starts
- **Claim before starting**: set task to "In Progress" in MC *before* doing the work
- **Under Review**: when work is done but needs Guillermo's eyes → set MC status to "Under Review" and include a direct link to the deliverable. **Notion page preferred** — any URL accepted as fallback

### Overnight Work
- Each agent has a scheduled overnight window (see schedule below)
- **Plan before doing (PPEE)**: review your task backlog in MC strategically — pick tasks that are high-value and completable within ~90 mins. Do NOT try to clear the entire backlog. Use good judgment.
- **Time budget: target 90 mins, hard stop at 2h.** If a task will take longer, work on the first completable milestone and leave a clear "stopping point" note in MC.
- After the window: update MC task statuses (completed/blocked/in-progress) + post activity to MC feed + post summary to #squad-updates
- If blocked or something failed → post it clearly with a specific ask for Guillermo. **Never be silent.**
- **No re-delegating up at runtime**: if a task is too large or unclear, break it down or ask clarifying questions at 5PM standup — not at 1am mid-run.

---

## Overnight Schedule

| Time (HKT) | Agent | Focus |
|------------|-------|-------|
| 00:30 | Raphael 🔴 | Brinc tasks |
| 01:30 | Leonardo 🔵 | Cerebro / Launchpad tasks |
| 03:00 | Molty 🦎 | Infra, coordination, cross-cutting |

Staggered to avoid API contention. All three done by ~05:30 HKT.

---

## Todoist Structure (topic-based, not agent-based)

Projects are organised by topic so any agent can contribute where needed:

| Project | Primary Agent | Others can contribute |
|---------|--------------|----------------------|
| Brinc 🔴 | Raphael | Molty (infra/coordination support) |
| Cerebro 🔵 | Leonardo | Others as needed |
| Molty's Den 🦎 | Molty | — |
| Mana Capital 🟠 | TBD | — |
| Ideas 💡 | Anyone | — |

---

## Daily Standup Integration (5PM)

The standup "Action" column expands from `Keep / Delegate / Drop` to:

| Action | Routes to |
|--------|-----------|
| Keep | Guillermo handles it |
| Molty | Molty's Den |
| Raphael | Brinc project |
| Leonardo | Cerebro project |
| Drop | Close the task |

Each agent's overnight cron pulls from their designated Todoist project.

---

## MC Status Flow

```
Backlog → In Progress → Under Review → Done
                     ↘ Blocked
```

- **In Progress**: claimed and being worked on
- **Under Review**: work complete, needs Guillermo's eyes — always include a link to the deliverable
- **Blocked**: agent can't proceed — include specific ask for Guillermo
- **Done**: Guillermo approved, or no review needed

---

## Morning Briefing (06:30 HKT)

Absorbed into the existing daily brief — no separate report. Added section:

```
🌙 Overnight Report
Raphael:  ✅ [task] | ⏳ Under Review: [task + link] | ❌ Blocked: [task + ask]
Leonardo: ✅ [task] | ⏳ Under Review: [task + link]
Molty:    ✅ [task] | ❌ Blocked: [task + ask]
```

---

## Escalation Protocol

When blocked, agents post to #squad-updates:
> "🚧 Blocked: [task name]. Why: [specific reason]. Need from Guillermo: [specific ask]."

When Under Review:
> "👀 Under Review: [task name]. Link: [url]. Waiting on: [what decision/feedback is needed]."

---

## Guillermo's Morning Unblock Window

Reserve 10-15 mins after the 06:30 brief to action any "Under Review" items and unblock flagged tasks. Agents can then continue in their next session. Predictable, fast.

---

## Staged Rollout (MC tasks created — pending approval)

### Stage 0 — Prerequisites `jn79ypa14hcv9b2ajg7dmevdw181vd61`
*Gate: must be done before Stage 3*
- ☐ Confirm Leonardo sub-agent fix is live (anthropic/claude-haiku-4-5)
- ☐ Verify Todoist API token in `/data/shared/credentials/` for Raphael + Leonardo
- ☐ Confirm Raphael has exec tool available for overnight cron use

### Stage 1 — Rules in place `jn79cbk1g4n7w2cgnkz1jrnkpd81vgpn`
*Can run parallel to Stage 0*
- ☐ Update AGENTS.md on all three agents (MC discipline + overnight work rules)
- ☐ Notify Raphael and Leonardo via webhook

### Stage 2 — Todoist queues + standup routing `jn74z0w8qy0qdb0v369p41y72s81t6c8`
*Depends on Stage 0*
- ☐ Confirm Todoist project IDs: Brinc (Raphael) + Cerebro (Leonardo)
- ☐ Update Notion standup template: add Raphael/Leonardo as Action options
- ☐ Update `process_standup.py` to route to all three queues
- ☐ Test routing end-to-end

### Stage 3 — Overnight crons `jn7fn5mb0308sqfyrk440vnhms81t8zh`
*Depends on Stage 0 + Stage 2*
- ☐ Add Raphael cron (00:30 HKT)
- ☐ Add Leonardo cron (01:30 HKT)
- ☐ Update Molty 03:00 cron to include MC feed post + #squad-updates

### Stage 4 — Morning briefing update `jn7fdjjarmxya2kkyatp1wa1ps81vatg`
*Depends on Stage 3*
- ☐ Update `morning_briefing.py` to query MC overnight activity per agent
- ☐ Format overnight report section into 06:30 Telegram brief
- ☐ Highlight Under Review items (with links) + blocked items

### Stage 5 — Backfill + go live `jn7ex2wpx6ge1vrhgjz014sn9d81t7b8`
*Depends on Stages 1-4*
- ☐ Each agent runs MC backfill audit (active multi-step tasks not yet in MC)
- ☐ Confirm overnight queues populated from standup
- ☐ First full overnight cycle — all three agents
- ☐ Review morning brief output, adjust if needed
- ☐ Sign off with Guillermo

---

## Decisions Locked

- ✅ Overnight summaries go to **both** MC activity feed AND #squad-updates + morning brief — more visibility preferred
- ✅ "Under Review" links → **Notion pages preferred**. Any URL accepted as fallback (GitHub PR, doc, etc.) — just needs to be something Guillermo can open and review without context-switching

---

## Audit Improvements (added Feb 25)
- Added **Stage 0** as prerequisite gate — Leonardo sub-agent fix must be confirmed before overnight crons go live
- Added **Notion standup template update** to Stage 2 — Action column needs Raphael/Leonardo options
- Added **Todoist token distribution check** — Raphael/Leonardo need API access before Stage 3
- Made **Stage 5 backfill concrete** — specific per-agent audit command, not vague "review"

---

*Last updated: 2026-02-25 14:15 HKT by Molty — staged into MC (6 tasks), audit improvements added*
