# PLAN-018: Paperclip Adoption — Fleet Control Plane Migration
**Status:** APPROVED (2026-03-17, Guillermo)
**Author:** Molty 🦎
**Priority:** P0 — Active now
**MC Task:** jn736xwrt4n2k4fptjn7p6yxnh833vp1
**Started:** 2026-03-17 16:37 HKT

---

## Why

We've been building fleet orchestration piecemeal:
- **MC** — custom Convex dashboard (limited, no cost tracking, flat tasks)
- **Agent-link** — home-grown webhooks (just deployed HMAC, but still manual)
- **Todoist** — Guillermo's task list (sync keeps breaking, 3 plans trying to fix it)
- **Discord** — summaries and coordination (noisy, no audit trail)

Paperclip replaces all of this with one purpose-built system: org charts, goal hierarchy, cost tracking, governance, audit trails, multi-company isolation.

**What it obsoletes:** MC task system, agent-link for task routing, PLAN-016 (Todoist sync), parts of PLAN-017

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│            Paperclip (Railway)                   │
│                                                  │
│  Board: Guillermo (full control, all companies)  │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │  Brinc   │ │ Cerebro  │ │  Molty's Den  │   │
│  │  Co.     │ │  Co.     │ │     Co.       │   │
│  │          │ │          │ │               │   │
│  │ Raphael  │ │ Leonardo │ │ Molty, April  │   │
│  │ 🔴       │ │ 🔵       │ │ 🦎 🌸         │   │
│  └──────────┘ └──────────┘ └───────────────┘   │
│                                                  │
│  Postgres · REST API · React Dashboard           │
└──────────────────┬───────────────────────────────┘
                   │ HTTP adapter (heartbeat invocations)
                   ▼
┌──────────────────────────────────────────────────┐
│       Railway-hosted OpenClaw Agents             │
│  Each agent has Paperclip skill installed        │
│  Receives tasks · Reports work · Tracks costs    │
└──────────────────────────────────────────────────┘
```

---

## Phase 0: Local Spike — Prove It Works
**Goal:** Verify Paperclip works with our OpenClaw agents before committing
**Time:** ~2h | **When:** Now (Mar 17 afternoon)

### 0.1 Install & Boot
- [ ] Clone repo: `git clone https://github.com/paperclipai/paperclip.git`
- [ ] Install deps: `cd paperclip && pnpm install`
- [ ] Start dev server: `pnpm dev`
- [ ] Verify API: `curl http://localhost:3100/api/health`
- [ ] Verify UI loads in browser: `http://localhost:3100`
- [ ] Note: embedded PGlite DB auto-created, no config needed

### 0.2 Create Test Company
- [ ] Create company "TMNT Test" via UI or API
- [ ] Create a company-level goal: "Test fleet integration"
- [ ] Create a project: "Spike Testing"
- [ ] Note company ID for later steps

### 0.3 Configure Test Agent (Molty)
- [ ] Create agent "Molty" with role "Fleet Coordinator"
- [ ] Set adapter_type: `http`
- [ ] Configure adapter_config:
  ```json
  {
    "url": "https://ggvmolt.up.railway.app/hooks/agent",
    "method": "POST",
    "headers": {"Authorization": "Bearer <molty-webhook-token>"},
    "timeoutMs": 15000
  }
  ```
- [ ] Generate API key for Molty agent
- [ ] Note agent ID and API key

### 0.4 Test Heartbeat Invocation
- [ ] Trigger manual heartbeat: `POST /agents/:agentId/heartbeat/invoke`
- [ ] Verify Molty receives the webhook (check OpenClaw logs)
- [ ] Verify the payload format — what does the agent receive?
- [ ] Document: does the heartbeat include task context? Or just a wake signal?

### 0.5 Test Task Flow
- [ ] Create a task in Paperclip: "Test task — respond with status update"
- [ ] Assign task to Molty agent
- [ ] Verify: can Molty read assigned tasks via `GET /companies/:id/issues?assignee=<agentId>`
- [ ] Verify: can Molty checkout task via `POST /issues/:id/checkout`
- [ ] Verify: can Molty post a comment via `POST /issues/:id/comments`
- [ ] Verify: can Molty update status via `PATCH /issues/:id`
- [ ] Verify: can Molty report cost via `POST /companies/:id/cost-events`

### 0.6 Test Budget Controls
- [ ] Set Molty agent budget to $1/month
- [ ] Report cost event of $0.50
- [ ] Verify dashboard shows spend
- [ ] Report cost event pushing over $1
- [ ] Verify agent auto-pauses at budget limit

### 0.7 Evaluate UI
- [ ] Dashboard — is it clear at a glance?
- [ ] Task board — is it usable for daily work?
- [ ] Agent status — can you see who's running/idle/paused?
- [ ] Cost view — useful?
- [ ] Mobile — does it work on phone?
- [ ] Activity log — is the audit trail readable?

### 0.8 Spike Report
- [ ] Write findings: what works, what doesn't, blockers
- [ ] **GO/NO-GO decision** with Guillermo
- [ ] If GO → proceed to Phase 1
- [ ] If NO-GO → document why, assess if fixable, keep building our own

**Go criteria (ALL must pass):**
- ✅ HTTP adapter can wake an OpenClaw agent
- ✅ Agent can read tasks via API
- ✅ Agent can update task status + post comments
- ✅ Cost events work
- ✅ Dashboard is usable
- ❌ Any critical failure → stop, assess

---

## Phase 1: Deploy to Railway + Create Companies
**Goal:** Production Paperclip instance with our company structure
**Time:** ~4h | **When:** After GO decision
**Depends on:** Phase 0 GO

### 1.1 Railway Deployment
- [ ] Create new Railway project: "Paperclip"
- [ ] Add Postgres database service
- [ ] Deploy Paperclip server (Node.js)
- [ ] Set `DATABASE_URL` env var → Railway Postgres
- [ ] Set `NODE_ENV=production`
- [ ] Configure auth mode (local_trusted for now, authenticated later)
- [ ] Verify API health: `GET /api/health`
- [ ] Add Railway domain (e.g., `tmnt-paperclip.up.railway.app`)
- [ ] Verify UI accessible via domain
- [ ] Add to Tailscale if needed for private access

### 1.2 Create Companies
- [ ] **Brinc** — Company
  - Mission: "Drive Asia Pacific revenue, close proposals, grow pipeline"
  - Status: active
- [ ] **Cerebro** — Company
  - Mission: "10 paying customers in 12 weeks"
  - Status: active
- [ ] **Molty's Den** — Company
  - Mission: "Fleet operations, personal assistant, infrastructure"
  - Status: active
- [ ] *(Mana Capital — create placeholder, paused until ready)*

### 1.3 Create Goal Hierarchies

**Brinc:**
- [ ] Company goal: "Drive AP revenue and pipeline"
  - [ ] Project: "Sales Proposals"
    - [ ] Goal: "Close active proposals"
  - [ ] Project: "Marketing"
    - [ ] Goal: "Brinc brand content"

**Cerebro:**
- [ ] Company goal: "10 paying customers in 12 weeks"
  - [ ] Project: "CRM Platform"
    - [ ] Goal: "Ship Phase B features"
    - [ ] Goal: "Ship Phase C features"
  - [ ] Project: "Growth"
    - [ ] Goal: "Customer acquisition pipeline"

**Molty's Den:**
- [ ] Company goal: "Keep fleet running, support Guillermo"
  - [ ] Project: "Fleet Infrastructure"
    - [ ] Goal: "Agent reliability + observability"
  - [ ] Project: "Personal Assistant"
    - [ ] Goal: "Calendar, email, daily operations"

### 1.4 Create Agents

**Brinc company:**
- [ ] Raphael 🔴 — Role: Sales Lead, Title: VP Sales
  - Adapter: http → `https://ggv-raphael.up.railway.app/hooks/agent`
  - Reports to: none (company CEO for now)
  - Budget: TBD (set after baseline)
  - [ ] Generate API key

**Cerebro company:**
- [ ] Leonardo 🔵 — Role: Product Lead, Title: CTO
  - Adapter: http → `https://leonardo-production.up.railway.app/hooks/agent`
  - Reports to: none
  - Budget: TBD
  - [ ] Generate API key

**Molty's Den company:**
- [ ] Molty 🦎 — Role: Fleet Coordinator, Title: COO
  - Adapter: http → `https://ggvmolt.up.railway.app/hooks/agent`
  - Reports to: none
  - Budget: TBD
  - [ ] Generate API key
- [ ] April 🌸 — Role: Personal Assistant, Title: EA
  - Adapter: http → `https://april-agent-production.up.railway.app/hooks/agent`
  - Reports to: Molty
  - Budget: TBD
  - [ ] Generate API key

### 1.5 Configure Heartbeat Schedules

| Agent | Interval | Purpose |
|-------|----------|---------|
| Molty 🦎 | 2h | Fleet checks, task processing |
| Raphael 🔴 | 4h | Sales pipeline, proposal work |
| Leonardo 🔵 | 4h | CRM development, product work |
| April 🌸 | 4h | Personal tasks, calendar, family |

- [ ] Set heartbeat intervals in agent adapter_config
- [ ] Verify scheduler picks them up

### 1.6 Set Up Board Access
- [ ] Configure Guillermo as board operator
- [ ] Verify dashboard shows all 3 companies
- [ ] Verify quick actions work (pause agent, create task, approve)
- [ ] Test mobile access (Guillermo's phone)
- [ ] Bookmark dashboard URL

---

## Phase 2: Migrate MC Tasks
**Goal:** All existing tasks moved to Paperclip with correct company/goal mapping
**Time:** ~2h | **When:** After Phase 1
**Depends on:** Phase 1 complete

### 2.1 Export MC Tasks
- [ ] `GET /api/tasks` from MC API
- [ ] Count total tasks by status and project
- [ ] Save raw export: `/data/workspace/migration/mc-tasks-export.json`

### 2.2 Build Migration Map

| MC Project | Paperclip Company | Default Project | Default Goal |
|-----------|-------------------|-----------------|--------------|
| brinc | Brinc | Sales Proposals | Close active proposals |
| cerebro | Cerebro | CRM Platform | Ship Phase B |
| fleet | Molty's Den | Fleet Infrastructure | Agent reliability |
| personal | Molty's Den | Personal Assistant | Daily operations |

| MC Status | Paperclip Status |
|-----------|-----------------|
| inbox | backlog |
| assigned | todo |
| in_progress | in_progress |
| review | in_review |
| done | done |
| blocked | blocked |

| MC Assignee | Paperclip Agent ID |
|------------|-------------------|
| molty | Molty agent in Molty's Den |
| raphael | Raphael agent in Brinc |
| leonardo | Leonardo agent in Cerebro |
| april | April agent in Molty's Den |

### 2.3 Write Migration Script
- [ ] Script: `/data/workspace/scripts/migrate-mc-to-paperclip.py`
- [ ] For each MC task:
  - Map project → company
  - Map status → Paperclip status
  - Map assignee → Paperclip agent ID
  - Map priority (p0→critical, p1→high, p2→medium, p3→low)
  - Create issue via `POST /companies/:id/issues`
  - Preserve title, description, due date
- [ ] Dry run first (log what would be created, don't create)
- [ ] Review dry run output with Guillermo

### 2.4 Execute Migration
- [ ] Run migration script (live mode)
- [ ] Count verification: MC task count == Paperclip issue count
- [ ] Spot-check 10 random tasks — correct company, status, assignee, priority
- [ ] Verify goal linkage — tasks trace to correct goals
- [ ] Screenshot dashboard for before/after comparison

### 2.5 Migration Verification Checklist
- [ ] Total task count matches
- [ ] No orphaned tasks (every task has a company)
- [ ] Assignees correct (cross-check 5 per agent)
- [ ] Priorities mapped correctly
- [ ] Blocked tasks show as blocked
- [ ] Done tasks show as done (historical record)
- [ ] In-progress tasks show current assignee

---

## Phase 3: Agent Onboarding — Update the Squad
**Goal:** Every agent knows Paperclip is their task source and how to use it
**Time:** ~4h | **When:** After Phase 2
**Depends on:** Phase 2 verified
**Critical:** Agents must be updated BEFORE cutover — they should never see both systems

### 3.1 Create Paperclip Skill (shared)
- [ ] Write `/data/shared/skills/paperclip/SKILL.md`
- [ ] Contents:
  - Paperclip API base URL + auth pattern
  - How to discover assigned tasks
  - How to checkout a task (atomic)
  - How to post progress comments
  - How to update task status
  - How to report cost events (tokens, model, cost)
  - How to read goal context (why am I doing this?)
  - How to create subtasks for delegation
  - How to handle budget pause (what to do when stopped)
- [ ] Include code examples for each operation
- [ ] Include error handling (409 checkout conflict, 403 budget exceeded)
- [ ] Verify skill is accessible via Syncthing on all agents

### 3.2 Update Molty's AGENTS.md
- [ ] Replace MC task references with Paperclip
- [ ] Update "Before Any MC API Call" section → Paperclip API patterns
- [ ] Update overnight work section → Paperclip heartbeat flow
- [ ] Add Paperclip credentials (API key, base URL, company ID)
- [ ] Remove Todoist sync references for agent tasks
- [ ] Keep agent-link for ad-hoc messaging (non-task)
- [ ] Update HEARTBEAT.md → report to Paperclip
- [ ] Update TOOLS.md → Paperclip credentials

### 3.3 Update Raphael's AGENTS.md
- [ ] Add Paperclip section: Brinc company, his agent ID, API key
- [ ] Task source: Paperclip (not MC, not Todoist)
- [ ] On heartbeat: check Paperclip for assigned Brinc tasks
- [ ] Report costs after work (model, tokens, cost)
- [ ] Goal context: every task traces to "Drive AP revenue"
- [ ] Remove MC references
- [ ] Deploy updated AGENTS.md (Syncthing or direct)
- [ ] Verify Raphael acknowledges the change

### 3.4 Update Leonardo's AGENTS.md
- [ ] Add Paperclip section: Cerebro company, his agent ID, API key
- [ ] Task source: Paperclip
- [ ] On heartbeat: check Paperclip for assigned Cerebro tasks
- [ ] Report costs after work
- [ ] Goal context: every task traces to "10 paying customers"
- [ ] Remove MC references
- [ ] Deploy updated AGENTS.md
- [ ] Verify Leonardo acknowledges the change

### 3.5 Update April's AGENTS.md
- [ ] Add Paperclip section: Molty's Den company, her agent ID, API key
- [ ] Task source: Paperclip
- [ ] On heartbeat: check Paperclip for assigned tasks
- [ ] Reports to Molty in org chart
- [ ] Report costs after work
- [ ] Remove MC references
- [ ] Deploy updated AGENTS.md
- [ ] Verify April acknowledges the change

### 3.6 Update Overnight Cron/Heartbeat
- [ ] Review each agent's overnight cron configuration
- [ ] Option A: Keep OpenClaw crons, agents read from Paperclip instead of MC
- [ ] Option B: Use Paperclip heartbeat scheduler to wake agents (cleaner)
- [ ] Decision: ______ (decide during implementation)
- [ ] Whichever option: verify agents wake on schedule and pick up tasks

### 3.7 Agent Onboarding Verification
For EACH agent (Molty, Raphael, Leonardo, April):
- [ ] Agent's AGENTS.md updated and deployed
- [ ] Agent has Paperclip skill available
- [ ] Agent has valid API key
- [ ] Agent can read assigned tasks from Paperclip
- [ ] Agent can checkout a task
- [ ] Agent can post a comment
- [ ] Agent can update task status
- [ ] Agent can report cost event
- [ ] Agent acknowledges the change (ACK message)

---

## Phase 4: Live Test — Full Overnight Cycle
**Goal:** All agents work a real overnight session via Paperclip
**Time:** One overnight cycle | **When:** First night after Phase 3
**Depends on:** All agents verified in Phase 3

### 4.1 Pre-flight
- [ ] All agents have pending tasks in Paperclip
- [ ] All agents are status: active (not paused)
- [ ] Heartbeat schedules configured
- [ ] Budget limits set (generous for first run)
- [ ] Guillermo briefed: "Tonight is the first Paperclip overnight"

### 4.2 Monitor
- [ ] Watch dashboard during overnight window
- [ ] Verify each agent wakes on schedule
- [ ] Verify task checkouts happen (no conflicts)
- [ ] Verify comments posted as work progresses
- [ ] Verify cost events reported
- [ ] Check for errors in activity log

### 4.3 Morning Review (with Guillermo)
- [ ] Walk through dashboard together
- [ ] Show: tasks completed, in-progress, blocked
- [ ] Show: cost per agent, total overnight spend
- [ ] Show: activity log / audit trail
- [ ] Show: goal progress (how much closer to company missions)
- [ ] Guillermo verdict: keep Paperclip? Adjust anything?

---

## Phase 5: Cutover — Decommission Old Systems
**Goal:** Clean transition, no straddling
**Time:** ~1h | **When:** After successful overnight + Guillermo approval
**Depends on:** Phase 4 successful, Guillermo says GO

### 5.1 Decommission MC Task System
- [ ] Stop writing new tasks to MC
- [ ] Keep MC API running (read-only, historical reference)
- [ ] Remove MC task-related crons
- [ ] Update MEMORY.md — MC is archive, Paperclip is active
- [ ] Keep MC heartbeat/status endpoints (still useful for fleet health)

### 5.2 Decommission Todoist for Agent Work
- [ ] Todoist = Guillermo's personal tasks ONLY
- [ ] Remove overnight_sync.py MC→Todoist sync
- [ ] Remove PLAN-016 from active plans (no longer needed)
- [ ] Update TODO.md — point to Paperclip for Molty's tasks

### 5.3 Update Agent-Link Scope
- [ ] Agent-link stays for ad-hoc messaging (alerts, questions, status)
- [ ] Task routing moves to Paperclip (no more task-type messages via agent-link)
- [ ] Document the boundary: agent-link = chat, Paperclip = work

### 5.4 Update Documentation
- [ ] MEMORY.md — Paperclip as control plane
- [ ] TOOLS.md — Paperclip credentials, URLs
- [ ] PLAN-REGISTRY.md — Close PLAN-016, update PLAN-015/017, add PLAN-018 as complete
- [ ] REGRESSIONS.md — any new rules from migration
- [ ] HEARTBEAT.md — updated for Paperclip

### 5.5 Communication
- [ ] Post to #squad-updates: "Fleet now running on Paperclip"
- [ ] Brief each agent via agent-link: "MC is archived, Paperclip is your task source"
- [ ] Share dashboard URL with Guillermo (bookmark on phone)

### 5.6 Cutover Verification
- [ ] No agent is reading from MC for tasks
- [ ] No Todoist sync scripts running
- [ ] All agents report costs to Paperclip
- [ ] Dashboard shows real-time fleet status
- [ ] Guillermo can create/assign tasks from dashboard
- [ ] Guillermo can pause/resume agents from dashboard

---

## What We Keep vs. Replace

| System | Action | Notes |
|--------|--------|-------|
| **MC Dashboard** | Archive (read-only) | Historical reference, stop writing |
| **MC Heartbeat API** | Keep | Fleet health independent of Paperclip |
| **Agent-link (PLAN-015)** | Keep for messaging | Tasks → Paperclip. Ad-hoc messages → agent-link |
| **Todoist** | Keep for Guillermo only | Personal tasks. NO agent work. |
| **Discord** | Keep | Communication channel, not task system |
| **Overnight crons** | Evaluate | May replace with Paperclip heartbeats |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Paperclip V1 has bugs | High | Medium | Phase 0 spike tests critical paths first |
| HTTP adapter incompatible with OpenClaw webhooks | Medium | High | Phase 0 tests this explicitly — go/no-go gate |
| Migration loses task data | Low | Medium | Keep MC read-only as archive, export backup |
| Agents confused during transition | Medium | Medium | Update AGENTS.md BEFORE cutover, test individually |
| Paperclip goes down overnight | Medium | High | Self-hosted on Railway, add health check + alert |
| Cost reporting needs agent code changes | Certain | Low | Paperclip skill handles this, agents learn at runtime |
| Guillermo doesn't like the UI | Medium | High | Phase 0 evaluates UI, get feedback early |

---

## Success Criteria

- [ ] All 4 agents receive and complete tasks from Paperclip
- [ ] All 4 agents report costs (token usage visible in dashboard)
- [ ] Dashboard shows real-time status across all 3 companies
- [ ] Overnight runs work end-to-end via Paperclip
- [ ] Guillermo can manage everything from one dashboard
- [ ] No more Todoist↔MC sync issues (single source of truth)
- [ ] Goal hierarchy visible (tasks → goals → company mission)
- [ ] Budget tracking shows per-agent monthly spend
- [ ] Audit trail is complete and useful
- [ ] No straddling — MC fully archived

---

## Timeline (Compressed — Starting Now)

| When | Phase | Focus | Checklist |
|------|-------|-------|-----------|
| **Now (Tue PM)** | 0 | Local spike with Guillermo | 0.1-0.8 |
| **Tue evening** | 1 | Deploy to Railway, create companies + goals | 1.1-1.6 |
| **Tue-Wed** | 2 | Migrate MC tasks | 2.1-2.5 |
| **Wed** | 3 | Agent onboarding (all 4 agents) | 3.1-3.7 |
| **Wed night** | 4 | First overnight run via Paperclip | 4.1-4.3 |
| **Thu AM** | 4+5 | Morning review + cutover | 4.3, 5.1-5.6 |

**Target completion:** Thursday Mar 20, morning

---

## Credentials (fill during deployment)

| Item | Value |
|------|-------|
| Paperclip URL | TBD |
| Railway project | TBD |
| Postgres URL | TBD (Railway) |
| Board auth | TBD |
| Molty API key | TBD |
| Raphael API key | TBD |
| Leonardo API key | TBD |
| April API key | TBD |
| Brinc company ID | TBD |
| Cerebro company ID | TBD |
| Molty's Den company ID | TBD |

---

*This is the biggest infrastructure change since the fleet launched. We go from duct tape to a real control plane — or we find out in 2 hours that it doesn't work and lose nothing.*
