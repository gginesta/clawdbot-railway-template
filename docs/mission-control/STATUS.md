# TMNT Mission Control — Status

**Last updated:** 2026-02-23 16:30 HKT
**Version:** v0.2.0 (Phase 3 complete)
**Live:** https://tmnt-mission-control.vercel.app

---

## Architecture

| Component | Tech | URL |
|-----------|------|-----|
| Frontend | Next.js 15 + React 19 + Tailwind CSS | Vercel (free tier) |
| Backend | Convex (real-time, serverless) | `rosy-crocodile-290.convex.cloud` |
| Auth | Middleware password gate | Set `MC_PASSWORD` env to enable |
| Repo | `gginesta/tmnt-mission-control` (private) | GitHub |
| Local path | `/data/workspace/tmnt-mission-control/` | — |

---

## Screens (11 routes + login)

| Route | Name | Description |
|-------|------|-------------|
| `/` | **The Dojo** | Dashboard: stats, priority tasks, fleet status, activity, Commander's Tasks (Todoist) |
| `/war-room` | **War Room** | Kanban board with drag-and-drop, create tasks, filter by project |
| `/sewer` | **The Sewer** | Real-time activity feed, filterable by agent/type/project |
| `/tracker` | **Turtle Tracker** | Agent health cards with stale detection (>4h) |
| `/calendar` | **Shell Calendar** | Week/month view with agent swim lanes |
| `/vault` | **The Vault** | Memory browser with search, browse by agent/date |
| `/pizza` | **Pizza Tracker** | Metrics: velocity, activity volume, per-project/priority breakdown, cost tracking |
| `/project/[slug]` | **Project Views** | Per-project filtered view (brinc, cerebro, mana) |
| `/settings` | **Splinter's Den** | Agent registry, task templates, cron status, API config |
| `/login` | **Login** | Password gate (dark themed) |
| `/_not-found` | **404** | Not found page |

---

## API Endpoints (12)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/activity` | Log agent activity |
| POST | `/api/status` | Update agent status |
| POST | `/api/heartbeat` | Agent heartbeat ping |
| POST | `/api/task` | Create task |
| PATCH | `/api/task` | Update task status/fields |
| GET | `/api/tasks` | Query tasks (filterable) |
| POST | `/api/memory` | Sync memory to Vault |
| GET | `/api/memories` | Query memories |
| GET | `/api/notifications` | Check @mentions |
| POST | `/api/cost` | Report token usage/cost |
| POST | `/api/todoist-sync` | Sync Todoist tasks |

All endpoints require `Authorization: Bearer <MC_API_KEY>`.

---

## Convex Tables (8)

| Table | Purpose |
|-------|---------|
| `agents` | Agent registry (status, heartbeat, sub-agents) |
| `tasks` | Fleet task board (kanban) |
| `comments` | Task comments with @mentions |
| `activities` | Activity feed (the sewer) |
| `costs` | Token usage + cost tracking |
| `memories` | Synced memory files (the vault) |
| `taskTemplates` | Reusable task templates |
| `todoistTasks` | Read-only Todoist sync |

---

## Cron Jobs

| Job | Schedule | ID | Status |
|-----|----------|----|--------|
| Heartbeat + Memory Sync | Every 2h | `46d1ca32` | ✅ Active |
| Daily Standup | 08:00 HKT | `62aaf754` | ✅ Active |
| Memory Health Check | Mon 10:00 HKT | `3db9477e` | ✅ Active |
| Todoist Sync | Every 30min | — | 📋 Planned |
| Weekly Digest | Fri 17:00 HKT | — | 📋 Planned |
| Usage Report | With heartbeat | — | 📋 Planned |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/mc-todoist-sync.sh` | Pull Todoist tasks → MC (API v1) |
| `scripts/mc-usage-report.sh` | Report OpenRouter credits + Anthropic tokens to MC |
| `scripts/mc-weekly-digest.sh` | Generate weekly fleet summary |

---

## Phase History

### Phase 1 ✅ (Feb 23 morning)
- Scaffold: Next.js 14 + Convex + Vercel
- 5 Convex tables, 5 HTTP routes, seed data
- 4 core screens: Dojo, War Room, Sewer, Tracker

### Phase 2 ✅ (Feb 23 morning)
- Auth hardened (MC_API_KEY)
- Sub-agent tracking, comment threads
- Shell Calendar, The Vault
- MC skill deployed to agents
- Heartbeat cron, task notifications

### Phase 3 ✅ (Feb 23 afternoon)

**Tier 1:**
- Pizza Tracker metrics dashboard
- Fleet alerts (stale >4h detection)
- Daily standup cron
- Memory auto-sync on heartbeat
- Loading & empty states

**Tier 2:**
- Mobile responsive (bottom nav, responsive grids)
- Project views (`/project/brinc`, `/project/cerebro`, `/project/mana`)
- Enhanced Dojo (quick actions, overdue alerts)
- Cost tracking (costs table + POST /api/cost + Pizza Tracker charts)
- Drag-and-drop Kanban

**Tier 3:**
- Todoist sync (29 tasks, read-only, API v1)
- Task templates (4 seeded + CRUD UI)
- Splinter's Den settings page
- Password auth (middleware + login page)
- Weekly digest script

**Skipped:** Dark mode (not needed)

---

## Remaining Work (tracked in MC War Room)

1. Wire Todoist sync cron (every 30min)
2. Wire weekly digest cron (Fri 17:00 HKT)
3. Integrate usage report into heartbeat cron
4. Enable MC_PASSWORD on Vercel
5. Clean up ESLint warnings

---

## Key Decisions

- **Next.js 16 → 15 downgrade:** Next.js 16 has a known prerender bug with useContext (#85668)
- **NODE_ENV=production in container:** Causes npm to skip devDependencies silently — always use `NODE_ENV=development npm install`
- **Todoist API v1:** REST v2 (`api.todoist.com/rest/v2/`) returns HTTP 410 Gone. Use `/api/v1/` instead.
- **No chart library:** CSS-based bar charts keep bundle small
- **Convex prod deployment:** `rosy-crocodile-290` (changed from `resilient-chinchilla-241` dev)
- **Auth is opt-in:** Set `MC_PASSWORD` env var to enable; disabled by default for easy dev

---

## Git History

| Hash | Description |
|------|-------------|
| `b3aecfd` | Phase 3 Tier 3 — Todoist, templates, settings, auth, digest |
| `9aa26a5` | Phase 3 Tier 2 — mobile, projects, Dojo, costs, DnD |
| `0acfb06` | Next.js 15 downgrade + ESLint fixes |
| `7b386e8` | TS types fix + error pages |
| `c3e2746` | PATCH /api/task endpoint |
| `0b3f234` | Phase 3 Tier 1 — Pizza Tracker, alerts, empty states |
| `dad8898` | Task notifications + comment @mentions |
| `c813a2b` | Phase 2 — sub-agents, comments, Calendar, Vault |
| `f2b6ce3` | Phase 1 seed data |
