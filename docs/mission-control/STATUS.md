# 🐢 TMNT Mission Control — Project Status

**Last Updated:** 2026-02-23 11:40 HKT
**Owner:** Molty 🦎
**Live URL:** https://tmnt-mission-control.vercel.app

---

## Current State: Phase 1 — 90% Complete

### ✅ Done (Phase 1)

| # | Item | Spec Ref | Status |
|---|------|----------|--------|
| 1.1 | Init NextJS + Convex, push to GitHub | Phase 1 | ✅ Done |
| 1.2 | Deploy to Vercel, confirm Convex connection | Phase 1 | ✅ Done |
| 1.3 | Convex schema (5 tables: agents, tasks, activities, comments, memories) | Phase 1 | ✅ Done |
| 1.4 | The Dojo (home dashboard) | Phase 1 | ✅ Live — real-time stats, tasks, agents, activity |
| 1.5 | The War Room (kanban task board) | Phase 1 | ✅ Live — Kanban with create task mutation |
| 1.6 | The Sewer (activity feed) | Phase 1 | ✅ Live — real-time feed with filters |
| 1.7 | Turtle Tracker (agent status) | Phase 1 | ✅ Live — health bar + agent cards |
| 1.8 | HTTP API endpoints for agents | Phase 1 | ✅ Done (5 endpoints on Convex) |
| 1.9 | `mission-control` OpenClaw skill | Phase 1 | ❌ Not started |
| 1.10 | Connect Molty to Mission Control | Phase 1 | ⚠️ Partial — API tested manually, skill not built |
| 1.11 | Seed initial data | Phase 1 | ✅ Done (3 agents, 4 tasks, 5 activities) |
| 1.12 | Basic auth | Phase 1 | ❌ Not started |

### ✅ Convex Wiring Complete (Feb 23, 11:45 HKT)

All 4 screens now pull real data from Convex via `useQuery`/`useMutation`:
- **ConvexClientProvider** mounted in root layout
- **convex-helpers.ts** mapping layer bridges Convex data shapes ↔ UI interfaces
- **tasks.stats** query added for Dojo computed stats (fleet status, in-progress, review, done this week)
- **Loading states** added to all pages (spinner while Convex hydrates)
- **Create Task** form in War Room wired to `tasks.create` mutation
- **API verified**: activity POST + heartbeat POST confirmed working end-to-end

### UI Component Library

11 shared components (Gemini Flash designed, commit `518a5bf`):
Badge, TaskCard, AgentCard, ActivityItem, FilterBar, KanbanColumn, Modal, HealthBar, StatCard, PageHeader, PlaceholderScreen

---

## Phase 1 Remaining Work (Priority Order)

| Priority | Task | Est. Time | Notes |
|----------|------|-----------|-------|
| **P1** | Build `mission-control` OpenClaw skill | 2h | Lets agents post activity/status/tasks via natural language |
| **P1** | Connect Molty's heartbeat to MC | 1h | First live agent integration |
| **P2** | Basic auth (token or password) | 1h | Currently open to anyone with the URL |

**Total remaining Phase 1 effort: ~4 hours**

---

## Phase 2 — Not Started

| # | Item | Spec Ref | Status |
|---|------|----------|--------|
| 2.1 | Deploy MC skill to Raphael + Leonardo | Phase 2 | ❌ |
| 2.2 | Heartbeat integration (all agents) | Phase 2 | ❌ |
| 2.3 | Comment threads with @mentions | Phase 2 | ❌ |
| 2.4 | The Vault (memory browser) | Phase 2 | ❌ (placeholder exists) |
| 2.5 | Memory sync to Convex | Phase 2 | ❌ |
| 2.6 | Task notification system | Phase 2 | ❌ |
| 2.7 | Sub-agent tracking (Kingdom view) | Phase 2 | ❌ (static roster in seed data) |
| 2.8 | Todoist sync (optional) | Phase 2 | ❌ |
| 2.9 | Shell Calendar (timeline view) | Phase 2 | ❌ (placeholder exists) |

---

## Phase 3 — Not Started

| # | Item | Spec Ref | Status |
|---|------|----------|--------|
| 3.1 | Pizza Tracker (metrics) | Phase 3 | ❌ (placeholder exists) |
| 3.2 | Daily standup auto-generation | Phase 3 | ❌ |
| 3.3 | Enhanced Dojo (priority tasks, quick actions) | Phase 3 | ❌ |
| 3.4 | Mobile-responsive polish | Phase 3 | ❌ |
| 3.5 | Dark mode refinement | Phase 3 | ❌ |
| 3.6 | Project views (Brinc/Cerebro/Mana tabs) | Phase 3 | ❌ |
| 3.7 | Task templates | Phase 3 | ❌ |
| 3.8 | Cost tracking | Phase 3 | ❌ |
| 3.9 | Document/deliverable storage | Phase 3 | ❌ |
| 3.10 | Notification preferences | Phase 3 | ❌ |

---

## Architecture

```
┌──────────────────────┐     ┌──────────────────────┐
│   Vercel (Frontend)  │     │   Convex (Backend)   │
│                      │     │                      │
│  NextJS 14 App       │────▶│  Schema (5 tables)   │
│  React Components    │     │  Queries/Mutations   │
│  Tailwind CSS        │     │  HTTP API (5 routes)  │
│  Component Library   │     │  Real-time subs      │
└──────────────────────┘     └──────────────────────┘
                                       ▲
                                       │ POST /api/*
                              ┌────────┴────────┐
                              │   TMNT Agents    │
                              │                  │
                              │  Molty 🦎        │
                              │  Raphael 🔴      │
                              │  Leonardo 🔵     │
                              └─────────────────┘
```

## File Structure

```
tmnt-mission-control/
├── convex/                    # Backend (DEPLOYED)
│   ├── schema.ts              # 5 tables
│   ├── agents.ts              # Agent queries & mutations
│   ├── tasks.ts               # Task CRUD
│   ├── activities.ts          # Activity feed
│   ├── comments.ts            # Task comments
│   ├── http.ts                # HTTP API for agents
│   └── seed.ts                # Seed data
├── src/
│   ├── app/                   # Pages (DEPLOYED, mock data)
│   │   ├── page.tsx           # The Dojo
│   │   ├── war-room/page.tsx  # War Room
│   │   ├── sewer/page.tsx     # The Sewer
│   │   ├── tracker/page.tsx   # Turtle Tracker
│   │   ├── calendar/page.tsx  # Placeholder
│   │   ├── vault/page.tsx     # Placeholder
│   │   ├── pizza/page.tsx     # Placeholder
│   │   └── settings/page.tsx  # Placeholder
│   ├── components/
│   │   ├── ui/                # 11 shared components
│   │   ├── layout/sidebar.tsx
│   │   └── providers/convex-provider.tsx
│   └── lib/utils.ts           # Mock data + helpers
└── package.json
```

## Credentials & URLs

| Resource | URL / Value |
|----------|-------------|
| Live site | https://tmnt-mission-control.vercel.app |
| Convex dashboard | https://dashboard.convex.dev/t/guillermo-ginesta/tmnt-mission-control |
| Convex HTTP API | https://resilient-chinchilla-241.convex.site |
| Convex deployment | dev:resilient-chinchilla-241 |
| GitHub repo | github.com/gginesta/tmnt-mission-control (private) |
| Vercel project | tmnt-mission-control |

---

## Next Action

**Wire screens to Convex.** This is the single highest-impact task. Once done, the dashboard shows real data, updates in real-time, and agents can post to it via API. Everything else builds on this.

---

*This file tracks implementation status. Spec lives at `/data/workspace/docs/mission-control/SPEC.md`.*
