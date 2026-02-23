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

## Convex Wiring — Feb 23, 2026, 11:45 HKT

### All 4 Screens Wired to Real-Time Data

**Problem:** All screens rendered mock data from `src/lib/utils.ts`. Convex backend had real data but UI wasn't connected.

**Data Shape Mismatches Found:**
| Field | Convex | UI |
|-------|--------|-----|
| Priority | `"p0"` | `"P0"` |
| Task status | `"in_progress"` | `"In Progress"` |
| Task assignees | `string[]` | `{ id, name, emoji }[]` |
| Activity | no agent name/emoji/color | needs all three |
| Agent | `kingdom`, `lastHeartbeat` (ms) | `kingdomTheme`, `lastSeen` ("2 min ago") |

**Solution:** Created `src/lib/convex-helpers.ts` mapping layer (200 lines):
- `mapTask()`, `mapActivity()`, `mapAgent()` — Convex → UI
- `priorityToConvex()`, `statusToConvex()`, `projectToConvex()` — UI → Convex
- `timeAgo()`, `formatDueDate()` — timestamp formatting

**Changes:**
| File | Change |
|------|--------|
| `src/lib/convex-helpers.ts` | **NEW** — data mapping layer |
| `src/app/layout.tsx` | Mount ConvexClientProvider |
| `convex/tasks.ts` | Add `stats` query |
| `src/app/tracker/page.tsx` | Wire to `api.agents.list` |
| `src/app/sewer/page.tsx` | Wire to `api.activities.list` + `api.agents.list` |
| `src/app/war-room/page.tsx` | Wire to `api.tasks.list` + `api.tasks.create` |
| `src/app/page.tsx` | Wire to 4 queries (tasks, agents, activities, stats) |

**Verified:** TypeScript clean, Convex deployed, Next.js build passes, API tested (activity POST + heartbeat POST both return `{"ok":true}`), Vercel production deploy successful.

**Commit:** `f030afa`

---

## Phase 2 — Feb 23, 2026, 12:00–12:50 HKT

### 1A. API Auth Hardening (12:00)

- Generated proper API key: `232e4ddf...` (64 hex chars)
- Set as `MC_API_KEY` env var in Convex dashboard
- Updated `validateAuth()` in `http.ts` to check `process.env.MC_API_KEY`
- **Verified:** Old key returns 401, new key returns 200, no key returns 401
- Updated MC skill with new key
- **Commit:** `f2b6ce3`

### 2G. Sub-Agent Tracking (12:02)

- Added `subAgentId`, `subAgentName`, `subAgentEmoji` to Activity interface
- Updated `mapActivity()` to look up sub-agent from lead's roster
- Updated `ActivityItem` component: shows "Lead → 🤖 Sub-agent" attribution
- **Quick win:** Schema already supported `subAgentId`, just needed UI wiring

### 2E. Comment Threads (12:03)

- **New component:** `src/components/ui/task-detail.tsx` (170 lines)
  - Modal with task header (badges, assignees, due date)
  - Chronological comment list with author avatars
  - @mention autocomplete dropdown (filters as you type)
  - Mentions rendered in emerald green with agent emoji
  - Comment timestamps formatted
- **Updated:** `TaskCard` now clickable → opens TaskDetail modal
- **Backend:** Used existing `comments.listByTask` + `comments.add`

### 2C. Shell Calendar (12:04)

- **New page:** `src/app/calendar/page.tsx` (250 lines)
- **Features:**
  - Week/month toggle
  - Navigate forward/backward with arrows + "Today" button
  - Agent swim lanes (horizontal rows per agent with emoji + role)
  - Tasks plotted by `dueDate` (scheduled) or `completedAt` (done)
  - Color-coded: green = done (strikethrough), red = P0/blocked, blue = scheduled
  - Today column highlighted in emerald
  - Legend bar
- **Data:** Uses existing `tasks.list` + `agents.list` queries (no new backend needed)

### 2D. The Vault — Memory Browser (12:05)

- **New file:** `convex/memories.ts` — `list`, `stats`, `sync` queries/mutations
- **New endpoints:** `POST /api/memory` (push) + `GET /api/memories` (query)
- **Memory sync is upsert:** same agent + date + source updates existing entry
- **New page:** `src/app/vault/page.tsx` (200 lines)
  - Two-panel layout: memory list (left) + content viewer (right)
  - Search bar (filters title + content + tags)
  - Agent filter tabs
  - Stats row (total memories, per-agent breakdown)
  - Date and source shown per entry
  - Tag badges
  - Selected memory renders full markdown content
- **Seeded:** Pushed Molty's daily memory + MEMORY.md as test data

### 2A. Deploy Skill to Raphael + Leonardo (12:06)

- Copied `skills/mission-control/` to `/data/shared/skills/mission-control/`
- Sent webhooks to both agents with installation instructions
- Both acknowledged: Raphael `runId: 0751d427`, Leonardo `runId: a41f1124`

### 2B. Heartbeat Integration (12:07)

- **Decision:** Use dedicated cron instead of HEARTBEAT.md
  - HEARTBEAT.md spins up full agent session on every cycle (wasteful)
  - Cron uses Haiku (cheapest), isolated session, auto-discards HEARTBEAT_OK
- **Cron created:** `MC Heartbeat Ping` (`46d1ca32-...`)
  - Schedule: `0 */2 * * *` (every 2 hours)
  - Model: `anthropic/claude-haiku-4-5`
  - Action: curl MC heartbeat endpoint, reply HEARTBEAT_OK
  - Delivery: `--best-effort-deliver`
- **HEARTBEAT.md:** Kept empty with comment pointing to cron

### 2F. Task Notifications (12:08)

- **New query:** `comments.mentionsFor(agentId, since?)` — returns recent @mentions with task title
- **New endpoint:** `GET /api/notifications?agentId=X&since=T`
- Agents can poll this on heartbeat to check for new @mentions

### Phase 2 Commits

| Commit | Description |
|--------|-------------|
| `f2b6ce3` | API auth hardening + memory endpoints |
| `c813a2b` | Sub-agent tracking, comments, Calendar, Vault |
| `dad8898` | Task notifications + @mentions query |

### Deployment

All changes deployed to Vercel production and Convex in sequence.
Total Phase 2 build time: **~50 minutes**.

---

## What's Next

See `/data/workspace/docs/mission-control/PHASE3-PLAN.md` for detailed Phase 3 plan.
