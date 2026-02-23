# 🐢 TMNT Mission Control — Product Spec

**Owner:** Molty 🦎
**Stakeholder:** Guillermo
**Status:** Scoping → Phase 1
**Created:** 2026-02-23
**Last Updated:** 2026-02-23

---

## 1. Vision

Mission Control is the shared brain of the TMNT fleet. It's where Guillermo sees what's happening, where agents coordinate work, and where institutional knowledge lives. Think of it as the office that ties the whole operation together.

It is NOT a replacement for Notion or Todoist (Guillermo's personal tools). It's the fleet's operating system — the layer that sits between Guillermo and the agents, and between the agents themselves.

**Inspired by:**
- Bhanu Teja's 10-agent Mission Control (Convex + React) — [X Article](https://x.com/pbteja1998/status/2017662163540971756)
- Alex Finn's OpenClaw Mission Control (NextJS + Convex) — [X Article](https://x.com/AlexFinn/status/2024169334344679783)

---

## 2. Users

| User | Role | How They Use It |
|------|------|-----------------|
| **Guillermo** | Commander | Views dashboard, assigns tasks, reviews work, searches memory |
| **Molty 🦎** | Fleet Coordinator | Posts activity, manages tasks, routes work, monitors fleet |
| **Raphael 🔴** | Brinc Lead | Reads/writes tasks, posts updates, reports status |
| **Leonardo 🔵** | Launchpad Lead | Reads/writes tasks, posts updates, reports status |
| **Sub-agents** | Specialists | Log work output through their lead (Kingdom Isolation preserved) |

### Sub-Agent Architecture

Sub-agents are tracked in Mission Control but respect **Kingdom Isolation**:

```
Guillermo (Commander)
├── Molty 🦎 (Coordinator) — Pokémon Gen 1 Kingdom
│   ├── Pikachu ⚡ (Content/Marketing)
│   ├── Alakazam 🥄 (Spec Writer)
│   └── Machamp 💪 (Builder)
├── Raphael 🔴 (Brinc) — Super Mario Kingdom
│   ├── Peach 👑 (Head of Marketing)
│   │   ├── Lakitu ☁️ (Content)
│   │   ├── Daisy 🌼 (Social)
│   │   └── Prof E. Gadd 🔬 (Analytics)
│   ├── Scout (Research)
│   ├── Scribe (Writing)
│   └── Analyst (Data)
├── Leonardo 🔵 (Launchpad) — Star Wars Kingdom
│   ├── Researcher
│   ├── Architect
│   ├── Builder
│   └── QA/Reviewer
├── Donatello 🟣 (Tinker Labs) — TBD Kingdom [pending]
├── April 📰 (Personal) — TBD Kingdom [pending]
└── Michelangelo 🟠 (Mana Capital) — TBD Kingdom [pending]
```

**Rules in Mission Control:**
- Sub-agents appear under their lead in the Team view
- Activity logged by sub-agents is attributed as: `[Lead] → [Sub-agent]: action`
- Sub-agents cannot be assigned tasks directly by Guillermo — tasks go to leads
- Cross-kingdom work shows as lead-to-lead coordination

---

## 3. Tech Stack

### Recommended: NextJS + Convex + Vercel

| Layer | Tech | Why |
|-------|------|-----|
| **Frontend** | NextJS 14 (App Router) | React Server Components, excellent DX, Vercel-native |
| **Database** | Convex | Real-time subscriptions, TypeScript-native, serverless, free tier |
| **Hosting** | Vercel | Purpose-built for NextJS, free tier covers our scale, zero infra |
| **Styling** | Tailwind CSS + shadcn/ui | Fast to build, looks professional, highly customizable |
| **Auth** | Simple token-based | Agents auth via API keys, Guillermo via gateway token or simple password |

### Why NOT Railway?

Railway is great for the agents, but Mission Control is a web app — Vercel is purpose-built for this. Separating Mission Control from agent infra is also good practice (agent crash ≠ dashboard crash).

### Why Convex over Supabase?

- Real-time is first-class (subscriptions, not polling)
- TypeScript end-to-end (schema → queries → UI, all type-safe)
- Both reference articles validated it for this exact use case
- Free tier: 1M function calls/month, 1GB storage (more than enough)
- Simpler mental model: functions, not SQL

### Why Vercel over Hetzner?

- Zero server management (Hetzner = you manage the box)
- Free tier covers a dashboard with <10 users easily
- Automatic SSL, CDN, preview deployments on every PR
- If we outgrow free tier, Pro is $20/month (still cheap)
- Hong Kong CDN edge = fast for Guillermo

**Estimated monthly cost: $0** (free tiers for both Vercel + Convex at our scale)

---

## 4. Core Features

### 4.1 The Sewer 🕳️ (Activity Feed)

Real-time stream of everything happening across the fleet.

- Every agent action is logged: task created, status changed, memory written, cron executed, message sent
- Filterable by agent, by project (Brinc/Cerebro/Mana/Personal), by type
- Color-coded by agent (🦎 green, 🔴 red, 🔵 blue, etc.)
- Click any item to expand full context
- Agents post here via API: `POST /api/activity`

**Schema:**
```typescript
activities: defineTable({
  agentId: v.string(),        // "molty", "raphael", "leonardo"
  subAgentId: v.optional(v.string()), // "pikachu", "peach"
  type: v.string(),           // "task_update", "memory_write", "heartbeat", "message", "deploy"
  project: v.optional(v.string()),    // "brinc", "cerebro", "mana", "personal", "fleet"
  title: v.string(),
  body: v.optional(v.string()),
  metadata: v.optional(v.any()),
  createdAt: v.number(),
})
```

### 4.2 The War Room 🗺️ (Task Board)

Shared Kanban board — the single source of truth for fleet work.

**Columns:** Inbox → Assigned → In Progress → Review → Done | Blocked

- Tasks have: title, description, assignee(s), project, priority (P0-P3), due date, comments thread, status
- Any agent can create/update tasks via API
- Guillermo can create/assign from the UI
- Comments support @mentions (agent or human)
- Sub-tasks supported (nested under parent)
- Filters: by project, by agent, by priority, by status

**Schema:**
```typescript
tasks: defineTable({
  title: v.string(),
  description: v.optional(v.string()),
  status: v.string(),         // "inbox", "assigned", "in_progress", "review", "done", "blocked"
  priority: v.string(),       // "p0", "p1", "p2", "p3"
  project: v.string(),        // "brinc", "cerebro", "mana", "personal", "fleet"
  assignees: v.array(v.string()),  // ["molty", "raphael"]
  createdBy: v.string(),
  parentTaskId: v.optional(v.id("tasks")),
  dueDate: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
  createdAt: v.number(),
  updatedAt: v.number(),
})

comments: defineTable({
  taskId: v.id("tasks"),
  authorId: v.string(),       // "molty", "guillermo"
  body: v.string(),
  mentions: v.optional(v.array(v.string())),
  createdAt: v.number(),
})
```

### 4.3 Turtle Tracker 🐢 (Agent Status)

At-a-glance view of every agent in the fleet.

- Agent card for each lead: avatar/emoji, name, role, current status, last heartbeat, current task
- Expandable to show sub-agent roster (Kingdom view)
- Status: 🟢 Active | 🟡 Idle | 🔴 Error | ⚪ Offline
- Click agent → see their recent activity, assigned tasks, memory stats

**Schema:**
```typescript
agents: defineTable({
  agentId: v.string(),        // "molty"
  name: v.string(),           // "Molty"
  emoji: v.string(),          // "🦎"
  role: v.string(),           // "Fleet Coordinator"
  kingdom: v.string(),        // "Pokemon Gen 1"
  project: v.string(),        // "fleet"
  status: v.string(),         // "active", "idle", "error", "offline"
  currentTask: v.optional(v.string()),
  lastHeartbeat: v.optional(v.number()),
  lastActivity: v.optional(v.number()),
  subAgents: v.optional(v.array(v.object({
    id: v.string(),
    name: v.string(),
    emoji: v.string(),
    role: v.string(),
    archetype: v.string(),    // canonical archetype: "scout", "builder", etc.
    level: v.string(),        // "L1", "L2", "L3", "L4"
  }))),
})
```

### 4.4 The Vault 📚 (Memory Browser)

Searchable UI for all agent memories across the fleet.

- Browse by agent, by date, by topic
- Full-text search across all memory files
- View rendered markdown in a clean reading UI
- Memory timeline: see how knowledge evolved
- Stats: total memories, per-agent breakdown, growth over time

**Implementation note:** This reads from agent memory files. Options:
1. Agents sync memory content to Convex on heartbeat (preferred — indexed, searchable)
2. Mission Control fetches from agent workspaces directly (tighter coupling)

### 4.5 The Dojo 🥋 (Dashboard / Home)

The landing page. Quick overview of everything.

- Fleet health bar (all agents green?)
- Today's priority tasks (P0/P1)
- Recent activity (last 10 items)
- Quick stats: tasks completed this week, active tasks, pending reviews
- Quick actions: create task, ping agent, search memory

### 4.6 Shell Calendar 🗓️ (Timeline View)

Calendar view showing what the fleet has done and what's scheduled.

- **Past view:** Completed tasks plotted on timeline — see what each agent shipped and when
- **Future view:** Upcoming tasks with due dates, scheduled cron work, planned deliverables
- **Agent lanes:** Each lead gets a swim lane so you see parallel work streams
- **Integration:** Pulls from War Room tasks (due dates) + activity feed (completions) + cron schedule
- Week/month toggle
- Can live as a tab in The Dojo or standalone screen

### 4.7 Pizza Tracker 🍕 (Daily Debrief / Metrics)

Auto-generated daily summary + fleet performance metrics.

- Daily standup: what each agent did, what's planned, blockers
- Weekly metrics: tasks completed, average time-to-done, agent utilization
- Cost tracking: API spend per agent (if we integrate token counting)
- Delivered to Telegram as morning briefing enhancement

---

## 5. Agent Integration

### How Agents Talk to Mission Control

Each agent gets a Mission Control client — a simple script/module that wraps Convex HTTP API calls.

```bash
# Agent posts an activity
mc-post activity --type task_update --title "Proposal Studio spec complete" --project brinc

# Agent updates their status
mc-post status --agent raphael --status active --task "Writing Brinc proposal for TechCo"

# Agent creates a task
mc-post task --title "Review Cerebro landing page" --assignee leonardo --priority p1 --project cerebro

# Agent reads their assigned tasks
mc-get tasks --assignee molty --status assigned,in_progress
```

This would be implemented as:
1. A `mission-control-client.sh` shell script in each agent's workspace
2. Or a `mission-control` OpenClaw skill that wraps the API

**Preferred: OpenClaw skill** — agents can naturally say "post to Mission Control" and the skill handles it.

### Heartbeat Integration

On each heartbeat, agents:
1. Report status to Mission Control (`mc-post status`)
2. Check for new assigned tasks (`mc-get tasks --assignee <me>`)
3. Post any activity since last heartbeat

---

## 6. Design Direction

### Aesthetic
- **Warm, editorial, purposeful** — like Bhanu Teja's "newspaper dashboard"
- TMNT-themed accents (turtle green primary, each agent gets their color)
- Dark mode primary (agents work 24/7, this is an ops dashboard)
- Clean typography, generous whitespace
- Responsive (Guillermo checks on phone via Telegram link sometimes)

### Color Palette
| Agent | Color | Hex |
|-------|-------|-----|
| Molty 🦎 | Gecko Green | `#4CAF50` |
| Raphael 🔴 | Hot Red | `#F44336` |
| Leonardo 🔵 | Ocean Blue | `#2196F3` |
| Donatello 🟣 | Purple | `#9C27B0` |
| Michelangelo 🟠 | Orange | `#FF9800` |
| April 📰 | Yellow | `#FFC107` |
| Guillermo | Gold | `#FFD700` |

### Navigation
Sidebar with TMNT-themed icons:
- 🏠 **Dojo** (Home/Dashboard)
- 🕳️ **Sewer** (Activity Feed)
- 🗺️ **War Room** (Task Board)
- 🐢 **Turtle Tracker** (Agent Status)
- 📚 **Vault** (Memory Browser)
- 🍕 **Pizza Tracker** (Metrics)
- ⚙️ **Splinter's Den** (Settings/Config)

---

## 7. Phased Build Plan

### Phase 1: Foundation + Core (This Week)
**Goal:** Deployable app with task board + activity feed. Agents can post to it.

| Step | Task | Est. Time |
|------|------|-----------|
| 1.1 | Initialize NextJS + Convex project, push to GitHub | 1 hour |
| 1.2 | Deploy to Vercel, confirm Convex connection | 30 min |
| 1.3 | Design and implement Convex schema (agents, tasks, activities, comments) | 2 hours |
| 1.4 | Build The Dojo (home dashboard) — layout, sidebar, basic stats | 3 hours |
| 1.5 | Build The War Room (task board) — Kanban columns, CRUD, filters | 4 hours |
| 1.6 | Build The Sewer (activity feed) — real-time stream, filters | 3 hours |
| 1.7 | Build Turtle Tracker (agent cards) — status display, basic info | 2 hours |
| 1.8 | Create Mission Control API endpoints (HTTP actions for agents) | 2 hours |
| 1.9 | Build `mission-control` skill for OpenClaw agents | 2 hours |
| 1.10 | Connect Molty to Mission Control (first agent integration) | 1 hour |
| 1.11 | Seed initial data (agents, sample tasks) | 30 min |
| 1.12 | Basic auth (gateway token or simple password for UI) | 1 hour |

**Phase 1 Deliverable:** Working dashboard at `mission-control.vercel.app` with task board, activity feed, agent status. Molty posting updates via API.

**Estimated total:** ~3-4 days of focused build time

---

### Phase 2: Agent Integration + Memory (Week 2)
**Goal:** All active agents connected. Memory browser live.

| Step | Task | Est. Time |
|------|------|-----------|
| 2.1 | Deploy mission-control skill to Raphael + Leonardo | 2 hours |
| 2.2 | Heartbeat integration — agents report status on each cycle | 2 hours |
| 2.3 | Build comment threads on tasks (with @mentions) | 3 hours |
| 2.4 | Build The Vault (memory browser) — search, browse, render markdown | 4 hours |
| 2.5 | Memory sync: agents push memory summaries to Convex on heartbeat | 3 hours |
| 2.6 | Task notification system — @mention alerts on next heartbeat | 2 hours |
| 2.7 | Sub-agent tracking — Kingdom view under each lead | 2 hours |
| 2.8 | Todoist sync (optional) — read Guillermo's Todoist tasks into Mission Control | 3 hours |

**Phase 2 Deliverable:** Full fleet connected. Memory searchable from UI. Task comments flowing. Sub-agents visible.

---

### Phase 3: Polish + Intelligence (Week 3-4)
**Goal:** Production-quality dashboard. Smart features.

| Step | Task | Est. Time |
|------|------|-----------|
| 3.1 | Pizza Tracker (metrics dashboard) — task velocity, agent utilization | 4 hours |
| 3.2 | Daily standup auto-generation (cron → compile → Telegram) | 3 hours |
| 3.3 | Enhanced Dojo — priority tasks, fleet health, quick actions | 2 hours |
| 3.4 | Mobile-responsive polish | 2 hours |
| 3.5 | Dark mode refinement | 1 hour |
| 3.6 | Project views (Brinc, Cerebro, Mana tabs) | 2 hours |
| 3.7 | Task templates (recurring task types) | 2 hours |
| 3.8 | Cost tracking integration (token usage per agent) | 3 hours |
| 3.9 | Document/deliverable storage (attach files to tasks) | 3 hours |
| 3.10 | Notification preferences + quiet hours | 1 hour |

**Phase 3 Deliverable:** Polished, production-grade Mission Control.

---

## 8. Build Approach

### Who Builds What

**Molty (me):** Architecture, spec, agent integration, skill development, testing, coordination.

**Codex:** Heavy frontend implementation. I'll write specs for each component, create GitHub issues, and let Codex generate the React components + Convex functions. I'll review and iterate.

**Why Codex:** The frontend is well-defined (Kanban boards, feeds, cards — common patterns). Codex excels at this. I'll focus on the architecture decisions and agent integration that require fleet context.

### Workflow
1. I create detailed GitHub issues with specs, acceptance criteria, and design references
2. Codex implements in feature branches
3. I review, test, merge
4. Vercel auto-deploys on merge to main
5. I build the agent-side integration (skill, heartbeat hooks)

---

## 9. Decisions (Locked Feb 23)

1. **Domain:** Vercel default for now (`tmnt-mission-control.vercel.app`). Custom domain later if needed.
2. **Database:** Convex (cloud-hosted). Best real-time DX, validated by both reference projects.
3. **GitHub repo:** `gginesta/tmnt-mission-control` (new repo).
4. **Todoist:** Runs in parallel. Mission Control = fleet system. Todoist + daily standups + calendar blocks = Guillermo's personal system. No replacement.
5. **Calendar view:** Added — integrated into The Dojo or its own tab. Shows what team has worked on + what's scheduled.
6. **Decision authority:** Molty owns technical decisions going forward. Guillermo reviews product/UX.

---

## 10. Success Criteria

**Phase 1 is successful when:**
- [ ] Dashboard is live and accessible
- [ ] Guillermo can view tasks, activity, and agent status from one screen
- [ ] Molty can create/update tasks and post activity via API
- [ ] Real-time updates work (change on one end, appears on the other)

**Full Mission Control is successful when:**
- [ ] All active agents read/write to Mission Control
- [ ] Guillermo checks Mission Control instead of Discord for fleet status
- [ ] Task lifecycle is tracked end-to-end (create → assign → progress → review → done)
- [ ] Memory is searchable across the fleet from the UI
- [ ] Daily debrief is richer and auto-generated from Mission Control data
- [ ] Sub-agent work is visible (through their leads)

---

## References

- [Bhanu Teja's Mission Control article](https://x.com/pbteja1998/status/2017662163540971756) — 10-agent system, Convex + React
- [Alex Finn's Mission Control article](https://x.com/AlexFinn/status/2024169334344679783) — Personal Mission Control, NextJS + Convex
- [Sub-Agent Operating Standard](/data/workspace/memory/squad/SUB-AGENT-OPERATING-STANDARD.md) — Kingdom Isolation, archetypes
- [TMNT Agent Architecture](/data/workspace/SOUL.md) — Fleet structure, roles

---

*This is a living document. Updated as decisions are made and phases progress.*
