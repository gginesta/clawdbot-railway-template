# PLAN-018: Paperclip Adoption — Fleet Control Plane Migration
**Status:** APPROVED (2026-03-17, Guillermo)
**Author:** Molty 🦎
**For:** Guillermo Ginesta
**Priority:** P1

---

## Why

We've been building fleet orchestration piecemeal — MC (custom Convex dashboard), agent-link (home-grown webhooks), Todoist sync (scripts that keep breaking), Discord summaries. It works, but it's fragile, has no cost tracking, and requires constant maintenance.

Paperclip is purpose-built for this. It replaces MC, agent-link, and Todoist-for-agent-work with one system that has proper data isolation, goal hierarchy, cost tracking, audit trails, and governance.

**What it obsoletes if successful:** PLAN-015 (agent-link), PLAN-016 (Todoist↔MC sync), parts of PLAN-017 (enforcement via governance gates)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           Paperclip (Railway)               │
│  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │
│  │  Brinc  │ │ Cerebro │ │ Molty's Den  │  │
│  │  Co.    │ │  Co.    │ │    Co.       │  │
│  └────┬────┘ └────┬────┘ └──────┬───────┘  │
│       │           │             │           │
│  Raphael 🔴  Leonardo 🔵   Molty 🦎       │
│                              April 🌸      │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │  Board: Guillermo (full control)     │   │
│  │  Dashboard · Budget · Governance     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │ HTTP adapter (webhooks)
         ▼
┌─────────────────────────────────────────────┐
│  Railway-hosted OpenClaw agents             │
│  Molty · Raphael · Leonardo · April         │
│  (each receives heartbeat invocations +     │
│   reports back via Paperclip REST API)      │
└─────────────────────────────────────────────┘
```

### Companies

| Company | Mission | Agents | Owner |
|---------|---------|--------|-------|
| **Brinc** | Drive AP revenue, close proposals | Raphael 🔴 | Guillermo |
| **Cerebro** | 10 paying customers in 12 weeks | Leonardo 🔵 | Guillermo |
| **Mana Capital** | PE operations (TBD) | TBD (Michelangelo?) | Guillermo |
| **Molty's Den** | Fleet ops, personal assistant, infra | Molty 🦎, April 🌸 | Guillermo |

---

## Phases

### Phase 0: Spike (Tonight, Tue Mar 18 03:00 HKT)
**Goal:** Prove it works with our stack

| Task | Detail | Time |
|------|--------|------|
| Install Paperclip locally | `npx paperclipai onboard --yes` or clone + pnpm dev | 15min |
| Create test company | "TMNT Test" with 1 agent (Molty) | 10min |
| Configure HTTP adapter | Point at Molty's webhook URL | 15min |
| Test heartbeat invocation | Does Paperclip successfully wake Molty? | 30min |
| Test task flow | Create task → assign → agent picks up → completes | 30min |
| Test cost reporting | Can agent report token usage back? | 15min |
| Evaluate UI | Is the dashboard usable? Mobile? | 15min |
| **Write spike report** | Go/no-go with findings | 15min |
| **Total** | | **~2.5h** |

**Go/no-go criteria:**
- ✅ HTTP adapter can invoke OpenClaw agent
- ✅ Agent can read assigned tasks via API
- ✅ Agent can update task status + post comments
- ✅ Cost events can be reported
- ✅ Dashboard is usable
- ❌ Any of the above fails = document why, assess fixability

### Phase 1: Deploy + Migrate (Wed-Thu, Mar 19-20)
*Only if Phase 0 is GO*

| Task | Detail | Time |
|------|--------|------|
| Deploy Paperclip to Railway | Node.js service + Postgres | 1h |
| Create 3 companies | Brinc, Cerebro, Molty's Den | 30min |
| Set up org charts | Agents in correct companies with roles | 30min |
| Define goal hierarchies | Company missions → projects → goals | 1h |
| **Migrate MC tasks** | Script: pull MC tasks → push to Paperclip tickets | 2h |
| Verify migration | Count check, spot check 20 tasks | 30min |
| Configure agent budgets | Monthly limits per agent | 15min |
| Set up Guillermo as Board | Auth, dashboard access | 15min |
| **Total** | | **~6h** |

### Phase 2: Agent Onboarding (Fri-Sat, Mar 21-22)
**Critical: update every agent so they know how to use Paperclip**

| Task | Detail | Time |
|------|--------|------|
| **Create Paperclip skill** | SKILL.md for agents — how to read tasks, update status, post comments, report costs via Paperclip API | 1h |
| **Update Molty's AGENTS.md** | New task source = Paperclip, not MC. Overnight flow uses Paperclip heartbeat. Remove MC task references. | 30min |
| **Update Raphael's AGENTS.md** | Tasks come from Paperclip Brinc company. Goal context included. Report costs. | 30min |
| **Update Leonardo's AGENTS.md** | Tasks come from Paperclip Cerebro company. Same pattern. | 30min |
| **Update April's AGENTS.md** | Tasks come from Paperclip Molty's Den company. | 30min |
| **Deploy Paperclip skill to all agents** | Via Syncthing to /data/shared/skills/ or per-agent workspace | 30min |
| **Update overnight cron scripts** | Agents wake via Paperclip heartbeat instead of custom crons | 1h |
| **Update heartbeat scripts** | Report health to Paperclip instead of agent-link health files | 30min |
| Test: Raphael overnight run via Paperclip | Full cycle — heartbeat → task pickup → work → report | 1h |
| Test: Leonardo overnight run via Paperclip | Same | 1h |
| **Total** | | **~7h (2 nights)** |

### Phase 3: Cutover + Cleanup (Sun-Mon, Mar 23-24)

| Task | Detail | Time |
|------|--------|------|
| Run full overnight cycle (all agents) | Sat night — all 4 agents work via Paperclip | Monitor |
| Morning review with Guillermo | Walk through dashboard, verify everything | 30min |
| **Decommission MC task system** | Stop writing to Convex, keep read-only for history | 30min |
| **Decommission agent-link for task routing** | Keep for ad-hoc messaging, but tasks flow through Paperclip | 30min |
| **Update Todoist integration** | Todoist = Guillermo's personal tasks only. Agent work = Paperclip only. | 15min |
| Update MEMORY.md | New control plane documented | 15min |
| Update TOOLS.md | Paperclip credentials + URLs | 15min |
| Update PLAN-REGISTRY.md | Close PLAN-015/016/017 affected items, document Paperclip | 15min |
| Post to #squad-updates | "Fleet now running on Paperclip" | 5min |
| **Total** | | **~2.5h** |

---

## Agent Update Checklist

Each agent needs these changes:

### AGENTS.md Updates
```markdown
## Task Management — Paperclip
- **Your tasks come from Paperclip, not MC or Todoist**
- API: https://<paperclip-url>/api
- Auth: Bearer <agent-api-key>
- On heartbeat: GET /companies/:companyId/issues?assignee=<agentId>&status=todo,in_progress
- Before starting work: POST /issues/:id/checkout (atomic — prevents double-work)
- While working: POST /issues/:id/comments (progress updates)
- When done: PATCH /issues/:id {status: "in_review"} or {status: "done"}
- Report costs: POST /companies/:companyId/cost-events
- Your work traces to company goals — read the goal chain for context
```

### Paperclip Skill (shared)
- Location: `/data/shared/skills/paperclip/SKILL.md`
- Covers: task discovery, checkout, updates, comments, cost reporting, delegation
- Every agent gets this via Syncthing

### Overnight Flow Change
**Before (current):**
```
Cron → wake agent → read MC tasks → work → update MC → post Discord
```

**After (Paperclip):**
```
Paperclip heartbeat → wake agent → agent reads Paperclip tasks (with goal context) 
→ atomic checkout → work → update ticket + report cost → Guillermo sees in dashboard
```

---

## What We Keep vs. Replace

| System | Keep? | Notes |
|--------|-------|-------|
| **MC Dashboard** | Archive (read-only) | Historical reference. Stop writing new tasks. |
| **MC Heartbeat API** | Keep for now | Still useful for fleet health independent of Paperclip |
| **Agent-link (PLAN-015)** | Keep for ad-hoc messaging | Task routing moves to Paperclip. Direct agent-to-agent messages stay on agent-link. |
| **Todoist** | Keep for Guillermo's personal tasks | Agent work = Paperclip only. No more sync scripts. |
| **Discord channels** | Keep | Agents still post summaries. Paperclip doesn't replace Discord for communication. |
| **Overnight crons** | Replace with Paperclip heartbeats | Paperclip handles scheduling natively |
| **PLAN-016 (Todoist↔MC sync)** | Cancel | No longer needed — single source of truth |

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Paperclip is V1, may have bugs | Phase 0 spike tests critical paths before committing |
| Migration loses task history | Keep MC read-only as archive |
| Agents confused during transition | Update AGENTS.md BEFORE switching — agents never see both systems |
| Paperclip goes down | It's self-hosted on Railway — we own uptime. Add health check. |
| HTTP adapter doesn't work with OpenClaw webhooks | Phase 0 tests this explicitly — go/no-go gate |
| Cost reporting requires agent code changes | Paperclip skill handles this — agents learn it at runtime |

---

## Success Criteria

- [ ] All 4 agents receive tasks from Paperclip
- [ ] All 4 agents report work back (status updates, comments, cost events)
- [ ] Dashboard shows real-time fleet status across all companies
- [ ] Overnight runs work end-to-end via Paperclip heartbeats
- [ ] Budget tracking shows per-agent monthly spend
- [ ] Guillermo can manage everything from one dashboard
- [ ] No more Todoist↔MC sync issues
- [ ] Task audit trail is complete and useful

---

## Timeline

| Night | Phase | Focus |
|-------|-------|-------|
| **Tue (tonight)** | 0 | PLAN-015 first, then Paperclip spike |
| **Wed** | 1 | Deploy to Railway + migrate MC tasks |
| **Thu** | 1 | Goal hierarchies + budgets + board setup |
| **Fri** | 2 | Paperclip skill + update Molty & Raphael |
| **Sat** | 2 | Update Leonardo & April + test overnight runs |
| **Sun** | 3 | Full overnight test (all agents) |
| **Mon** | 3 | Morning review with Guillermo + cutover |

**Target completion:** Mon Mar 24, morning standup

---

## MC Tasks

| Task | MC ID | Phase |
|------|-------|-------|
| Phase 0: Paperclip spike | TBD (create tonight) | 0 |
| Phase 1: Deploy + migrate | TBD | 1 |
| Phase 2: Agent onboarding | TBD | 2 |
| Phase 3: Cutover | TBD | 3 |

---

*This is the biggest infrastructure change since the fleet launched. If it works, we go from duct tape to a real control plane. If it doesn't, we're out 2.5 hours and keep building our own.*
