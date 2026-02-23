# 🐢 TMNT Mission Control — Phase 3 Plan

**Created:** 2026-02-23 12:55 HKT
**Owner:** Molty 🦎
**Status:** Planning
**Prerequisite:** Phase 1 ✅ + Phase 2 ✅ complete

---

## Vision

Phase 3 transforms Mission Control from a functional dashboard into a **production-grade ops platform**. Focus areas: intelligence (auto-generated insights), polish (mobile, dark mode), and integration depth (project views, cost tracking, Todoist).

---

## Work Streams

Phase 3 is organized into **4 independent work streams** that can be executed in parallel or sequentially. Within each stream, steps are ordered by dependency.

---

### Stream A: Intelligence & Automation (highest value)

**Goal:** MC generates insights and automates routine reporting.

| Step | Task | Description | Est. | Depends On |
|------|------|-------------|------|------------|
| A1 | **Pizza Tracker — Metrics Dashboard** | Replace placeholder with real metrics page. Show: tasks completed per agent (bar chart), average time-to-done, task velocity (weekly trend), tasks by project (pie chart), tasks by priority distribution. Data: all computable from existing `tasks` table. | 3h | — |
| A2 | **Pizza Tracker — Cost Tracking** | Add token usage tracking. New `costs` table: `agentId, date, inputTokens, outputTokens, model, estimatedCost`. New endpoint `POST /api/cost` for agents to report. Pizza Tracker renders daily/weekly cost per agent. | 3h | A1 |
| A3 | **Daily Standup Auto-Generation** | Cron job (morning, ~08:00 HKT) that queries MC for: yesterday's completed tasks, today's assigned tasks, any blocked items, agent statuses. Compiles into a formatted standup report. Delivers to Telegram as enhanced morning briefing. | 2h | A1 |
| A4 | **Weekly Digest** | Friday cron that generates a weekly summary: tasks completed, velocity trends, cost breakdown, notable activities. Posts to #command-center Discord + Telegram. | 2h | A3 |

**Stream A total: ~10h**

---

### Stream B: UI Polish & UX (user-facing quality)

**Goal:** Production-quality UI that works on all devices and looks great.

| Step | Task | Description | Est. | Depends On |
|------|------|-------------|------|------------|
| B1 | **Mobile-Responsive Polish** | Audit all 6 live screens for mobile breakpoints. Fix: sidebar → bottom nav on mobile, calendar → vertical scroll, War Room → horizontal scroll with snap. Test at 375px, 768px, 1024px. | 3h | — |
| B2 | **Dark Mode** | Add theme toggle (stored in localStorage). Dark palette: `bg-gray-900`, `text-gray-100`, card borders `gray-700`. Respect `prefers-color-scheme`. All components need dark variants. | 2h | — |
| B3 | **Enhanced Dojo** | Add quick actions to home: "Create Task" button, "Ping Agent" dropdown, "Search Memory" shortcut. Add "This Week" mini-calendar widget. Show overdue tasks with red badge. | 2h | — |
| B4 | **Task Status Transitions** | In War Room, add drag-and-drop between Kanban columns (react-beautiful-dnd or native DnD). Currently uses click → context menu. | 2h | — |
| B5 | **Loading & Empty States** | Audit all screens for: skeleton loaders (replace spinners), meaningful empty states with CTAs, error boundaries with retry. | 1h | — |

**Stream B total: ~10h**

---

### Stream C: Integration Depth (connecting systems)

**Goal:** MC becomes the central hub that pulls from and pushes to external systems.

| Step | Task | Description | Est. | Depends On |
|------|------|-------------|------|------------|
| C1 | **Project Views** | Add tabs/routes for project-specific views: `/project/brinc`, `/project/cerebro`, `/project/mana`. Each shows: tasks, activity, agents filtered to that project. Sidebar gets project shortcuts. | 3h | — |
| C2 | **Todoist Sync (Read-Only)** | Pull Guillermo's Todoist tasks into MC. New `todoist` table + cron that syncs every 30min via Todoist API. Show in Dojo as "Commander's Tasks" section. Read-only — MC doesn't write back. | 3h | — |
| C3 | **Memory Auto-Sync** | On heartbeat, agents automatically push today's memory file to MC `/api/memory`. Add to heartbeat cron: read memory file → POST. The Vault stays current without manual syncing. | 2h | — |
| C4 | **Splinter's Den — Settings** | Replace placeholder with settings page: manage agents (add/edit), view/rotate API key, configure notification preferences, see cron job status, Convex usage stats. | 3h | — |
| C5 | **Document/Deliverable Attachments** | Allow attaching files/links to tasks. New `attachments` field on tasks table. Upload to Convex file storage or link external URLs. Show in TaskDetail modal. | 2h | C4 |

**Stream C total: ~13h**

---

### Stream D: Advanced Features (nice-to-haves)

**Goal:** Power features for when the basics are solid.

| Step | Task | Description | Est. | Depends On |
|------|------|-------------|------|------------|
| D1 | **Task Templates** | Pre-defined task templates for recurring work: "Weekly Report", "Client Proposal", "Security Audit". Create from template → pre-fills title, description, assignees, tags. Store in `taskTemplates` table. | 2h | — |
| D2 | **Notification Preferences** | Per-agent notification config: which @mentions trigger alerts, quiet hours, delivery channel preference. Store in `agents` table or new `preferences` table. | 2h | — |
| D3 | **Activity Analytics** | In The Sewer, add analytics: activity volume over time (sparkline), most active agent today, activity type breakdown. Simple charts using existing data. | 2h | A1 |
| D4 | **Memory Timeline** | In The Vault, add timeline view: see how knowledge evolved over time. Diff view between memory versions (same source, different dates). | 2h | — |
| D5 | **Fleet Alerts** | If an agent hasn't sent a heartbeat in >4h, flag as "stale" in Turtle Tracker. Optional: send alert to Telegram/Discord. | 1h | — |
| D6 | **User Auth (Login)** | Add proper authentication: NextAuth.js with a simple password or Google OAuth. Protect all routes. Currently URL-obscured only. | 2h | — |

**Stream D total: ~11h**

---

## Recommended Execution Order

**Priority tiers based on impact/effort ratio:**

### Tier 1: Do First (highest ROI)
1. **A1** Pizza Tracker — Metrics (gives Guillermo fleet visibility)
2. **A3** Daily Standup Auto-Gen (reduces Molty's morning briefing work)
3. **C3** Memory Auto-Sync (keeps Vault current with zero effort)
4. **D5** Fleet Alerts (safety net — know when agents are down)
5. **B5** Loading & Empty States (quick polish, big UX impact)

### Tier 2: Do Next (solid value)
6. **B1** Mobile-Responsive (Guillermo checks on phone)
7. **C1** Project Views (organized by work stream)
8. **B3** Enhanced Dojo (home page becomes actionable)
9. **A2** Cost Tracking (understand fleet spend)
10. **B4** Drag-and-Drop Kanban (natural interaction)

### Tier 3: When Ready (nice-to-haves)
11. **B2** Dark Mode (aesthetic, not urgent)
12. **A4** Weekly Digest (automates reporting)
13. **C2** Todoist Sync (connects personal + fleet)
14. **C4** Splinter's Den (admin panel)
15. **D1** Task Templates
16. **D6** User Auth

### Tier 4: Future (when bored)
17. **D2** Notification Preferences
18. **D3** Activity Analytics
19. **D4** Memory Timeline
20. **C5** Document Attachments

---

## Estimated Totals

| Stream | Hours | Description |
|--------|-------|-------------|
| A: Intelligence | ~10h | Metrics, cost tracking, standup, weekly digest |
| B: UI Polish | ~10h | Mobile, dark mode, enhanced Dojo, DnD, empty states |
| C: Integration | ~13h | Project views, Todoist, memory sync, settings, attachments |
| D: Advanced | ~11h | Templates, notifications, analytics, timeline, alerts, auth |
| **Total** | **~44h** | Full Phase 3 |

**Tier 1 only: ~9h** (highest impact subset)

---

## Build Approach

### Who Builds What

**Molty:** Architecture decisions, agent integration (cron, heartbeat, memory sync), API endpoints, Convex functions.

**Codex (optional):** Frontend components — metrics charts, dark mode variants, mobile responsive fixes, drag-and-drop. Well-defined specs → GitHub issues → Codex implements → Molty reviews.

### Workflow
1. Pick a step from the priority order
2. Create detailed spec (acceptance criteria, data requirements, UI sketch)
3. Build backend (Convex functions + API) first
4. Build frontend
5. Test locally (`tsc --noEmit` + `npm run build`)
6. Deploy Convex → Vercel
7. Verify live
8. Update BUILD-LOG.md + STATUS.md
9. Commit

---

## Success Criteria

Phase 3 is complete when (Tier 1+2 at minimum):
- [ ] Pizza Tracker shows real metrics (task velocity, per-agent stats)
- [ ] Daily standup auto-generates from MC data
- [ ] Memory auto-syncs on heartbeat (Vault stays current)
- [ ] Fleet alerts flag stale agents
- [ ] All screens have proper loading/empty states
- [ ] Dashboard is usable on mobile
- [ ] Project-specific views exist
- [ ] Dojo has quick actions (create task, search memory)

---

## Dependencies & Risks

| Risk | Mitigation |
|------|------------|
| Convex free tier limits (1M calls/mo) | Monitor usage in dashboard. At current scale (~3 agents, few users), well under limit |
| Todoist API rate limits | Use 30min sync interval, cache locally |
| Dark mode breaks component library | Test each component individually, use CSS variables |
| Cost tracking accuracy | Agents self-report — may miss some calls. Acceptable for fleet visibility |
| Mobile sidebar navigation | Replace with bottom nav bar at `md` breakpoint |

---

*This plan is a living document. Updated as steps are completed.*
