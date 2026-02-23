# 🐢 TMNT Mission Control — Build Log

## Phase 1, Day 1 — Feb 23, 2026

### What We Built

**Full-stack fleet dashboard** for the TMNT AI agent squad.

### Tech Stack
- **Frontend:** NextJS 14 (App Router, TypeScript, Tailwind CSS)
- **Database:** Convex (real-time, serverless, TypeScript-native)
- **Hosting:** Vercel (free tier)
- **Repo:** github.com/gginesta/tmnt-mission-control (private)

### Live URLs
- **Dashboard:** https://tmnt-mission-control.vercel.app
- **Convex Dashboard:** https://dashboard.convex.dev/t/guillermo-ginesta/tmnt-mission-control
- **GitHub:** https://github.com/gginesta/tmnt-mission-control

### Screens Built (Phase 1)

| Screen | Route | Status | Description |
|--------|-------|--------|-------------|
| 🏠 The Dojo | `/` | ✅ Live | Home dashboard — fleet stats, priority tasks, agent cards, recent activity |
| 🗺️ War Room | `/war-room` | ✅ Live | Kanban task board — create/move tasks, project filters, priority badges |
| 🕳️ The Sewer | `/sewer` | ✅ Live | Real-time activity feed — agent/project/type filters |
| 🐢 Turtle Tracker | `/tracker` | ✅ Live | Agent status — fleet health bar, agent cards with Kingdom sub-agents |
| 🗓️ Shell Calendar | `/calendar` | 📋 Placeholder | Coming Phase 2 — agent swim lanes + task timeline |
| 📚 The Vault | `/vault` | 📋 Placeholder | Coming Phase 2 — searchable memory browser |
| 🍕 Pizza Tracker | `/pizza` | 📋 Placeholder | Coming Phase 3 — metrics, velocity, cost tracking |
| ⚙️ Splinter's Den | `/settings` | 📋 Placeholder | Coming Phase 2 — config, API keys, notifications |

### Convex Schema (5 tables)

| Table | Purpose | Fields |
|-------|---------|--------|
| `agents` | Fleet roster | agentId, name, emoji, role, kingdom, project, status, color, subAgents, heartbeat |
| `tasks` | Shared task board | title, description, status (kanban), priority (p0-p3), project, assignees, dates |
| `activities` | Activity feed | agentId, subAgentId, type, project, title, body, metadata, timestamp |
| `comments` | Task threads | taskId, authorId, body, mentions |
| `memories` | Memory sync | agentId, date, title, content (markdown), source |

### HTTP API Endpoints (for agent integration)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/activity` | POST | Agents post activity updates |
| `/api/status` | POST | Agents update their status |
| `/api/heartbeat` | POST | Agents send heartbeat pings |
| `/api/task` | POST | Agents create tasks |
| `/api/tasks` | GET | Agents query their assigned tasks |

Base URL: `https://resilient-chinchilla-241.convex.site`

### Seed Data
- 3 agents: Molty 🦎, Raphael 🔴, Leonardo 🔵 (with full sub-agent rosters)
- 4 tasks: Mission Control build, Proposal Studio, Cerebro dev, IRD reply
- 4 activities: Recent fleet actions

### UI Features
- Dark mode (TMNT-themed, green accents)
- TMNT-themed sidebar navigation with emojis
- Agent color coding (green/red/blue/purple/orange)
- Priority badges (P0 critical → P3 low)
- Project filters (Brinc/Cerebro/Mana/Personal/Fleet)
- Kanban drag-to-move via context menu
- Create task modal with assignee selection
- Fleet health bar (visual status of all agents)
- Kingdom sub-agent display under each lead
- Responsive layout

### Decisions Made
1. **Vercel + Convex** over Railway/Hetzner — zero infra management, free tier, purpose-built
2. **Convex over Supabase** — better real-time, TypeScript-native, validated by community
3. **Separate from agent infra** — agent crash ≠ dashboard crash
4. **Kingdom Isolation preserved** — sub-agents shown under leads, tasks flow to leads only
5. **Todoist runs in parallel** — Mission Control = fleet system, Todoist = Guillermo's personal
6. **Molty owns the build** — technical decisions delegated, Guillermo reviews product/UX
7. **Shell Calendar added** — Guillermo requested timeline view for team work visibility

### Credentials
| Service | Key Info |
|---------|----------|
| Convex | Team: guillermo-ginesta, Project: tmnt-mission-control, Deployment: dev:resilient-chinchilla-241 |
| Vercel | Project: tmnt-mission-control, Token in TOOLS.md |
| GitHub | Repo: gginesta/tmnt-mission-control (private) |

### File Structure
```
tmnt-mission-control/
├── convex/
│   ├── schema.ts          # Database schema (5 tables)
│   ├── agents.ts          # Agent queries & mutations
│   ├── tasks.ts           # Task CRUD
│   ├── activities.ts      # Activity feed queries & mutations
│   ├── comments.ts        # Comment threads
│   ├── http.ts            # HTTP API for agent integration
│   └── seed.ts            # Initial data seeding
├── src/
│   ├── app/
│   │   ├── layout.tsx     # Root layout with sidebar
│   │   ├── globals.css    # Dark mode styles
│   │   ├── page.tsx       # The Dojo (home)
│   │   ├── war-room/      # Kanban task board
│   │   ├── sewer/         # Activity feed
│   │   ├── tracker/       # Agent status
│   │   ├── calendar/      # Shell Calendar (placeholder)
│   │   ├── vault/         # Memory browser (placeholder)
│   │   ├── pizza/         # Metrics (placeholder)
│   │   └── settings/      # Config (placeholder)
│   ├── components/
│   │   ├── layout/
│   │   │   └── sidebar.tsx
│   │   └── providers/
│   │       └── convex-provider.tsx
│   └── lib/
│       └── utils.ts       # Colors, emojis, helpers
├── .env.local             # Convex connection (not in git)
└── package.json
```

---

## What's Next

### Phase 2 (Week 2) — Agent Integration + Memory
- Deploy mission-control skill to all agents
- Heartbeat integration (agents report status automatically)
- Comment threads with @mentions
- The Vault (memory browser with search)
- Memory sync (agents push summaries to Convex)
- Sub-agent tracking in activity feed
- Optional Todoist sync

### Phase 3 (Week 3-4) — Polish + Intelligence
- Pizza Tracker (metrics, velocity, cost tracking)
- Shell Calendar (timeline with agent swim lanes)
- Daily standup auto-generation from Mission Control data
- Mobile-responsive polish
- Project views (Brinc/Cerebro/Mana tabs)
- Task templates, notification preferences
