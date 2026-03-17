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

## Key Discovery: Native OpenClaw Adapter

Paperclip has a **dedicated OpenClaw gateway adapter** (`@paperclipai/adapter-openclaw-gateway`).
- Connects via **WebSocket** to each agent's OpenClaw gateway (not HTTP POST)
- Sends structured wake messages with full Paperclip context (run ID, task ID, company ID, goal chain)
- The wake message includes exact API instructions — agents know what to do immediately
- **Cost tracking is automatic** — adapter extracts usage/cost from OpenClaw's response
- Device auth, auto-pairing, and session management are built in
- **This eliminates the #1 risk** (webhook payload compatibility)

Config per agent:
```json
{
  "adapter_type": "openclaw_gateway",
  "adapter_config": {
    "url": "wss://ggvmolt.up.railway.app/ws",
    "authToken": "<gateway-token>",
    "timeoutSec": 120
  }
}
```

## Key Discovery: Built-in Paperclip Skill (309 lines)

Paperclip ships `/skills/paperclip/SKILL.md` — a complete agent skill covering:
- Full heartbeat procedure (9 steps)
- Authentication via auto-injected env vars
- Atomic task checkout with conflict handling
- Comment threading, status updates, delegation
- Budget awareness
- Self-test playbook
- Full API quick reference table

**We don't need to write our own skill. We deploy theirs via Syncthing.**

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

## Phase 0: Spike — Prove It Works
**Goal:** Verify Paperclip works with our OpenClaw agents before committing
**Time:** ~2h | **When:** Now (Mar 17 afternoon)
**Where:** Deploy directly to Railway (no local dev — we need Guillermo to see the UI)

### 0.1 Deploy Spike Instance to Railway
- [ ] Create Railway project: "Paperclip-spike" (separate from production)
- [ ] Add Postgres database
- [ ] Deploy from GitHub: `paperclipai/paperclip`
- [ ] Set env: `DATABASE_URL` → Railway Postgres
- [ ] Set env: `NODE_ENV=production`
- [ ] Add Railway domain
- [ ] Verify API: `GET /api/health`
- [ ] Verify UI loads in browser
- [ ] ⚠️ Auth: starts as `local_trusted` (anyone with URL = board). OK for spike, NOT for production.

### 0.2 Create Test Company + Goal
- [ ] Create company "TMNT Test" via API: `POST /api/companies`
- [ ] Create company-level goal: "Test fleet integration"
- [ ] Create project: "Spike Testing"
- [ ] Note company ID, goal ID, project ID

### 0.3 Test OpenClaw Gateway Adapter
**Risk level: LOW** — Paperclip has a native OpenClaw adapter. No payload compatibility concern.

- [ ] Create agent "Molty-Test" with adapter_type: `openclaw_gateway`
- [ ] Configure adapter_config:
  ```json
  {
    "url": "wss://ggvmolt.up.railway.app/ws",
    "authToken": "<molty-gateway-token>",
    "timeoutSec": 120,
    "sessionKeyStrategy": "issue"
  }
  ```
- [ ] Generate Paperclip API key for test agent
- [ ] Trigger manual heartbeat: `POST /agents/:agentId/heartbeat/invoke`
- [ ] **VERIFY:** Does Molty receive the wake message via WebSocket?
- [ ] **VERIFY:** Does the wake message include task context + API instructions?
- [ ] **VERIFY:** Does cost/usage data flow back from OpenClaw to Paperclip?
- [ ] **DOCUMENT:** Any device auth / pairing steps needed

**If adapter fails:** Check WebSocket connectivity (Railway may need specific config). The adapter has auto-pairing built in, so device auth should self-resolve.

### 0.4 Test Task Flow (Agent-Side API)
- [ ] Create task: `POST /companies/:id/issues` — "Test: respond with status"
- [ ] Assign to Molty-Test agent
- [ ] Test agent reads tasks: `GET /companies/:id/issues?assignee=<agentId>&status=todo`
- [ ] Test atomic checkout: `POST /issues/:id/checkout {"agentId": "...", "expectedStatuses": ["todo"]}`
- [ ] Test comment: `POST /issues/:id/comments {"body": "Working on this", "author_agent_id": "..."}`
- [ ] Test status update: `PATCH /issues/:id {"status": "done"}`
- [ ] Test cost report: `POST /companies/:id/cost-events {"agentId":"...","provider":"anthropic","model":"claude-opus-4","inputTokens":1000,"outputTokens":500,"costCents":5,"occurredAt":"..."}`
- [ ] **DOCUMENT:** Exact API calls that work — these go into the Paperclip skill

### 0.5 Test Budget Controls
- [ ] Set agent budget: `PATCH /agents/:id/budgets {"budget_monthly_cents": 100}` ($1)
- [ ] Report cost event of $0.50 (50 cents)
- [ ] Verify dashboard shows spend
- [ ] Report cost event of $0.60 (pushing over $1)
- [ ] Verify agent auto-pauses
- [ ] Verify board can override and resume

### 0.6 Evaluate UI (with Guillermo)
- [ ] Share URL with Guillermo
- [ ] Dashboard — clear at a glance?
- [ ] Task board — usable for daily work?
- [ ] Agent status — who's running/idle/paused?
- [ ] Cost view — useful?
- [ ] Mobile — works on phone? (Guillermo tests)
- [ ] Activity log — audit trail readable?
- [ ] **Guillermo's gut reaction:** would he use this daily?

### 0.7 Verify Built-in Skill Works
- [x] Paperclip ships SKILL.md — 309 lines, complete heartbeat procedure ✅
- [x] Covers: auth, checkout, comments, status, delegation, budget, self-test ✅
- [ ] Copy `skills/paperclip/` to `/data/shared/skills/paperclip/` via Syncthing
- [ ] Verify skill appears in agent skill discovery
- [ ] Decision: extend with TMNT-specific context? (Discord posting, etc.)

### 0.8 Spike Report + GO/NO-GO
- [ ] Write findings: `/data/workspace/reports/paperclip-spike-report.md`
- [ ] Document: what works, what doesn't, blockers, workarounds
- [ ] **GO/NO-GO decision** with Guillermo

**Go criteria (ALL must pass):**
- ✅ HTTP adapter can wake an OpenClaw agent (0.3)
- ✅ Agent can read tasks via API (0.4)
- ✅ Agent can update task status + post comments (0.4)
- ✅ Cost events work (0.5)
- ✅ Dashboard is usable — Guillermo says yes (0.6)
- ❌ Any critical failure → document, assess if fixable, decide

---

## Phase 1: Deploy to Railway + Create Companies
**Goal:** Production Paperclip instance with our company structure
**Time:** ~4h | **When:** After GO decision
**Depends on:** Phase 0 GO

### 1.1 Railway Deployment (Production)
- [ ] **Option A:** Promote spike instance to production (rename project, keep data)
- [ ] **Option B:** Fresh deploy with production Postgres (clean slate)
- [ ] Decision: ______ (decide after spike)
- [ ] Set `DATABASE_URL` → Railway Postgres (with backups enabled)
- [ ] Set `NODE_ENV=production`
- [ ] ⚠️ **Switch auth mode to `authenticated`** — `local_trusted` is NOT safe for production
- [ ] Configure board operator credentials for Guillermo
- [ ] Verify API health: `GET /api/health`
- [ ] Add Railway domain (e.g., `tmnt-paperclip.up.railway.app`)
- [ ] Verify UI accessible via domain
- [ ] Add to Tailscale for private access (recommended — keeps dashboard off public internet)
- [ ] Set up Railway health check (restart on failure)
- [ ] **Estimated Railway cost:** ~$5-10/month (Node.js service + Postgres)

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

**Brinc:** (52 MC tasks, 14 active)
- [ ] Company goal: "Drive Asia Pacific revenue as Managing Partner"
  - [ ] Project: "Proposal Engine"
    - [ ] Goal: "Ship proposal generator v2 (Streams A-D)"
    - *Tasks: A8 blocked deck, B2-B8 bootstrap, D2-D3 assembler*
  - [ ] Project: "Outbound Sales"
    - [ ] Goal: "Waalaxy pipeline automation (W1-W5)"
    - [ ] Goal: "Reactivate on-hold deals"
  - [ ] Project: "Marketing"
    - [ ] Goal: "LinkedIn content batch + brand"

**Cerebro:** (115 MC tasks, 38 active)
- [ ] Company goal: "10 paying customers in 12 weeks"
  - [ ] Project: "CRM Platform"
    - [ ] Goal: "Ship v1.6 (Sprints A-D)"
    - [ ] Goal: "Meeting Notes (Phases A-C)"
    - [ ] Goal: "Fix onboarding camera permissions"
  - [ ] Project: "Beta Program"
    - [ ] Goal: "Final 20 beta selection (M1.1)"
    - [ ] Goal: "Customer interviews + conversion (M4-M5)"
  - [ ] Project: "Growth Features"
    - [ ] Goal: "Referral system (Phases C-D)"
    - [ ] Goal: "Public API + auth"

**Molty's Den:** (83 MC tasks across fleet+personal, 21 active)
- [ ] Company goal: "Keep fleet running, support Guillermo's ventures"
  - [ ] Project: "Fleet Infrastructure"
    - [ ] Goal: "Paperclip migration (this plan)"
    - [ ] Goal: "Agent reliability (PLAN-015/017)"
  - [ ] Project: "Personal Assistant"
    - [ ] Goal: "Daily ops (calendar, email, briefings)"
  - [ ] Project: "Content"
    - [ ] Goal: "TMNT article + Pikachu content"
  
**Mana Capital:** (1 MC task, placeholder)
- [ ] Create company (paused)
- [ ] Activate when Guillermo defines scope

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

**Current MC state (as of Mar 17):**
| Status | Count |
|--------|-------|
| done | 180 |
| inbox | 43 |
| assigned | 17 |
| in_progress | 7 |
| review | 5 |
| blocked | 1 |
| **TOTAL** | **253** |

**Migration scope:** Only active tasks (non-done) = **73 tasks**
Done tasks stay in MC as archive. No point migrating completed history.

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

### 3.1 Deploy Paperclip Skill (shared)
**Paperclip ships a complete 309-line SKILL.md. We use theirs.**

- [ ] Copy `paperclip-deploy/skills/paperclip/` → `/data/shared/skills/paperclip/`
- [ ] Copy `paperclip-deploy/skills/paperclip/references/` too (full API reference)
- [ ] Syncthing distributes to all agents automatically
- [ ] Verify skill appears in each agent's available skills list
- [ ] Optional: add TMNT-specific wrapper (Discord summary posting after task completion)
- [ ] The skill covers: auth, 9-step heartbeat procedure, checkout, comments, status, delegation, budget, self-test
- [ ] **Cost tracking is automatic** — the OpenClaw adapter extracts usage from the response. No manual reporting needed.

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

## Rollback Plan

If Paperclip fails after partial deployment:

| Phase Failed | Rollback Action |
|-------------|----------------|
| **Phase 0** | Delete spike Railway project. Nothing changed. Zero cost. |
| **Phase 1-2** | Agents still running on MC/crons (unchanged). Delete Paperclip Railway project. |
| **Phase 3** | Revert agent AGENTS.md to pre-Paperclip versions (git revert). Agents go back to MC. |
| **Phase 4** | Keep Paperclip running but switch agents back to MC. Debug issues, retry. |
| **Phase 5** | Can't easily rollback after MC decommission. Don't cutover until Phase 4 is solid. |

**Key safety:** We don't touch agent AGENTS.md (Phase 3) until Phases 0-2 are verified. And we don't decommission MC (Phase 5) until overnight runs work. At every stage, the old system still works.

---

## Cost Reporting: How It Actually Works

OpenClaw doesn't natively report token usage to external APIs. The agent needs to:

1. **Read its own usage** — `session_status` tool gives token counts and cost
2. **POST to Paperclip** — `POST /companies/:id/cost-events` with model, tokens, cost
3. **When:** At the end of each heartbeat/work session

**Implementation in Paperclip skill:**
```
After completing work:
1. Call session_status to get current session usage
2. Calculate delta since last report
3. POST cost_event to Paperclip API
```

This is approximate (session-level, not task-level), but it's infinitely better than the zero visibility we have now. We can refine per-task attribution later.

---

## Security Considerations

| Concern | Mitigation |
|---------|-----------|
| **Auth mode** | Spike: `local_trusted` (OK). Production: MUST switch to `authenticated` |
| **Public URL** | Add Tailscale serve or restrict via Railway private networking |
| **Agent API keys** | Unique per agent, hashed at rest, revocable |
| **Credential storage** | API keys in agent TOOLS.md (same pattern as current webhook tokens) |
| **Data isolation** | Company-scoped by design — agents can't see other companies |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| ~~HTTP adapter payload incompatible with OpenClaw~~ | ~~Medium~~ | ~~CRITICAL~~ | **ELIMINATED** — native OpenClaw gateway adapter exists, connects via WebSocket |
| Paperclip V1 has bugs | High | Medium | Phase 0 spike tests critical paths. We're early adopters. |
| WebSocket connectivity from Railway→Railway | Low | Medium | Both services on Railway, should work. Test in Phase 0.3. |
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
