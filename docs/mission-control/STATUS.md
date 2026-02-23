# 🐢 TMNT Mission Control — Project Status

**Last Updated:** 2026-02-23 12:55 HKT
**Owner:** Molty 🦎
**Live URL:** https://tmnt-mission-control.vercel.app

---

## Current State: Phase 1 ✅ + Phase 2 ✅ Complete

---

## Phase 1: Foundation + Core ✅

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1 | Init NextJS + Convex, push to GitHub | ✅ | Commit `5dc3743` |
| 1.2 | Deploy to Vercel, confirm Convex connection | ✅ | Free tier, $0/month |
| 1.3 | Convex schema (5 tables) | ✅ | agents, tasks, activities, comments, memories |
| 1.4 | The Dojo (home dashboard) | ✅ | Real-time stats, priority tasks, fleet cards, activity feed |
| 1.5 | The War Room (kanban) | ✅ | Kanban with create task mutation, clickable → detail view |
| 1.6 | The Sewer (activity feed) | ✅ | Real-time feed with agent/project filters, sub-agent attribution |
| 1.7 | Turtle Tracker (agent status) | ✅ | Fleet health bar, agent cards with Kingdom sub-agents |
| 1.8 | HTTP API endpoints | ✅ | 8 endpoints (activity, status, heartbeat, task, tasks, memory, memories, notifications) |
| 1.9 | `mission-control` skill | ✅ | `/data/workspace/skills/mission-control/SKILL.md` + shared via Syncthing |
| 1.10 | Connect Molty to MC | ✅ | Cron heartbeat every 2h + API tested |
| 1.11 | Seed initial data | ✅ | 3 agents, 4 tasks, 5+ activities, 2 memories |
| 1.12 | API auth | ✅ | Bearer token validated against `MC_API_KEY` env var in Convex |

---

## Phase 2: Agent Integration + Memory ✅

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2A | Deploy MC skill to Raphael + Leonardo | ✅ | Skill copied to `/data/shared/skills/`, webhooks sent |
| 2B | Heartbeat integration | ✅ | Cron `46d1ca32` every 2h, Haiku model, `HEARTBEAT.md` kept empty |
| 2C | Shell Calendar | ✅ | Week/month view, agent swim lanes, task timeline by due/completed date |
| 2D | The Vault (memory browser) | ✅ | Search, agent filter, stats, markdown content viewer, 2 memories synced |
| 2E | Comment threads | ✅ | Task detail modal with @mention autocomplete, chronological comments |
| 2F | Task notifications | ✅ | `GET /api/notifications?agentId=X&since=T` for @mention alerts |
| 2G | Sub-agent tracking | ✅ | Activity feed shows "Lead → Sub-agent: action" attribution |

**Deferred from Phase 2:** Todoist sync (optional, low priority)

---

## Phase 3: Polish + Intelligence — In Progress

### Tier 1 ✅ Complete

| # | Item | Status | Notes |
|---|------|--------|-------|
| A1 | Pizza Tracker — Metrics | ✅ Done | Velocity chart, activity volume, project/priority breakdown, agent table |
| A3 | Daily Standup Auto-Gen | ✅ Done | Cron `62aaf754` at 08:00 HKT, queries MC tasks, delivers formatted standup |
| C3 | Memory Auto-Sync | ✅ Done | Heartbeat cron now also pushes daily memory to Vault |
| D5 | Fleet Alerts | ✅ Done | Stale detection (>4h), amber border + warning banner on agent cards |
| B5 | Loading & Empty States | ✅ Done | Empty Kanban columns, all screens have loading spinners |

### Tier 2 — Not Started

| # | Item | Status |
|---|------|--------|
| B1 | Mobile-Responsive Polish | ❌ |
| C1 | Project Views | ❌ |
| B3 | Enhanced Dojo | ❌ |
| A2 | Cost Tracking | ❌ |
| B4 | Drag-and-Drop Kanban | ❌ |

### Tier 3+ — Not Started

See `PHASE3-PLAN.md` for full breakdown.

---

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐
│   Vercel (Frontend)  │     │   Convex (Backend)   │
│                      │     │                      │
│  NextJS 14 App       │────▶│  Schema (5 tables)   │
│  12 UI components    │     │  Queries/Mutations   │
│  Tailwind CSS        │     │  HTTP API (8 routes) │
│  convex-helpers.ts   │     │  Real-time subs      │
└──────────────────────┘     └──────────────────────┘
                                       ▲
                                       │ POST /api/*
                              ┌────────┴────────┐
                              │   TMNT Agents    │
                              │                  │
                              │  Molty 🦎 (2h)   │
                              │  Raphael 🔴      │
                              │  Leonardo 🔵     │
                              └─────────────────┘
```

## Screens

| Screen | Route | Status | Description |
|--------|-------|--------|-------------|
| 🏠 The Dojo | `/` | ✅ Live | Home — stats, priority tasks, fleet, recent activity |
| 🗺️ War Room | `/war-room` | ✅ Live | Kanban board — create tasks, click → comment threads |
| 🕳️ The Sewer | `/sewer` | ✅ Live | Activity feed — agent/project filters, sub-agent attribution |
| 🐢 Turtle Tracker | `/tracker` | ✅ Live | Fleet health bar, agent cards, Kingdom view |
| 🗓️ Shell Calendar | `/calendar` | ✅ Live | Week/month timeline, agent swim lanes |
| 📚 The Vault | `/vault` | ✅ Live | Memory browser — search, stats, markdown viewer |
| 🍕 Pizza Tracker | `/pizza` | 📋 Placeholder | Metrics/analytics — Phase 3 |
| ⚙️ Splinter's Den | `/settings` | 📋 Placeholder | Settings/config — Phase 3 |

## HTTP API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/activity` | POST | Agents post activity updates |
| `/api/status` | POST | Agents update their status |
| `/api/heartbeat` | POST | Agents send heartbeat pings |
| `/api/task` | POST | Agents create tasks |
| `/api/tasks` | GET | Agents query their assigned tasks |
| `/api/memory` | POST | Agents push memory summaries |
| `/api/memories` | GET | Query memories (agent filter + text search) |
| `/api/notifications` | GET | Agents check for @mention alerts |

**Base URL:** `https://resilient-chinchilla-241.convex.site`
**Auth:** `Authorization: Bearer <MC_API_KEY>`

## File Structure

```
tmnt-mission-control/
├── convex/                    # Backend
│   ├── schema.ts              # 5 tables (agents, tasks, activities, comments, memories)
│   ├── agents.ts              # Agent queries & mutations (list, get, upsert, updateStatus, heartbeat)
│   ├── tasks.ts               # Task CRUD + stats query
│   ├── activities.ts          # Activity feed (list, recent, post)
│   ├── comments.ts            # Comments (listByTask, mentionsFor, add)
│   ├── memories.ts            # Memory browser (list, stats, sync)
│   ├── http.ts                # HTTP API (8 endpoints, auth validation)
│   └── seed.ts                # Initial data seeding
├── src/
│   ├── app/                   # Pages (all wired to Convex)
│   │   ├── page.tsx           # The Dojo
│   │   ├── war-room/page.tsx  # War Room
│   │   ├── sewer/page.tsx     # The Sewer
│   │   ├── tracker/page.tsx   # Turtle Tracker
│   │   ├── calendar/page.tsx  # Shell Calendar
│   │   ├── vault/page.tsx     # The Vault
│   │   ├── pizza/page.tsx     # Placeholder
│   │   └── settings/page.tsx  # Placeholder
│   ├── components/
│   │   ├── ui/                # 12 components (Badge, TaskCard, TaskDetail, AgentCard, ActivityItem, FilterBar, KanbanColumn, Modal, HealthBar, StatCard, PageHeader, PlaceholderScreen)
│   │   ├── layout/sidebar.tsx
│   │   └── providers/convex-provider.tsx
│   └── lib/
│       ├── utils.ts           # Types, constants, color helpers
│       └── convex-helpers.ts  # Convex ↔ UI data mapping layer
└── package.json
```

## Credentials & URLs

| Resource | Value |
|----------|-------|
| Live site | https://tmnt-mission-control.vercel.app |
| Convex dashboard | https://dashboard.convex.dev/t/guillermo-ginesta/tmnt-mission-control |
| Convex HTTP API | https://resilient-chinchilla-241.convex.site |
| Convex deployment | dev:resilient-chinchilla-241 |
| GitHub repo | github.com/gginesta/tmnt-mission-control (private) |
| Vercel project | tmnt-mission-control |
| MC API key | In Convex env var `MC_API_KEY` + skill SKILL.md |
| MC Heartbeat Cron | `46d1ca32-0bd0-43f4-bfa9-3e9e385271cd` (every 2h) |

## Git History

| Commit | Description |
|--------|-------------|
| `dad8898` | Task notifications + comment @mentions query |
| `c813a2b` | Phase 2 — sub-agent tracking, comments, Calendar, Vault |
| `f2b6ce3` | API auth hardening + memory endpoints |
| `f030afa` | Wire all screens to Convex (replace mock data) |
| `bb388f4` | Gemini-designed light theme UI + component library |
| `aa05d29` | Seed data, Vercel deployment config |
| `5dc3743` | TMNT Mission Control v0.1.0 — scaffold |

---

*This file tracks implementation status. Spec: `SPEC.md` | Build log: `BUILD-LOG.md` | Phase 3 plan: `PHASE3-PLAN.md`*
