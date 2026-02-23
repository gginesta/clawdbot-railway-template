# 🐢 TMNT Mission Control — Design Brief for Gemini

## Context
We're building a fleet dashboard called "Mission Control" for a team of AI agents themed after the Teenage Mutant Ninja Turtles. The app is built with NextJS 14 (App Router), Tailwind CSS, and Convex (real-time database). We need a complete UI design system and all screen layouts as React + Tailwind components.

## Design Direction
- **Light theme** — clean white/light gray backgrounds. No dark mode.
- **Modern and minimal** — think Linear, Notion, or Vercel dashboard aesthetics
- **TMNT themed** — subtle turtle/ninja references in naming, icons, and accent colors. Fun but professional. Not cartoonish.
- **Functional first** — every pixel should serve a purpose
- **Real-time feel** — the dashboard updates live as agents work

## Color System

### Agent Colors (these are fixed — each AI agent has their signature color)
| Agent | Role | Emoji | Primary Color | Use |
|-------|------|-------|---------------|-----|
| Molty 🦎 | Fleet Coordinator | 🦎 | `#4CAF50` (Green) | Cards, badges, activity |
| Raphael 🔴 | Brinc Sales Lead | 🔴 | `#EF4444` (Red) | Cards, badges, activity |
| Leonardo 🔵 | Venture Builder | 🔵 | `#3B82F6` (Blue) | Cards, badges, activity |
| Donatello 🟣 | R&D (pending) | 🟣 | `#8B5CF6` (Purple) | Cards, badges |
| Michelangelo 🟠 | Capital (pending) | 🟠 | `#F97316` (Orange) | Cards, badges |
| April 📰 | Personal Asst (pending) | 📰 | `#EAB308` (Yellow) | Cards, badges |
| Guillermo 👤 | Human Commander | 👤 | `#D4A017` (Gold) | Special accent |

### Project Colors
| Project | Emoji | Color |
|---------|-------|-------|
| Brinc | 🔴 | Red tones |
| Cerebro | 🧠 | Blue tones |
| Mana Capital | 🟠 | Orange tones |
| Personal | 🙂 | Emerald tones |
| Fleet | 🐢 | Green tones |

### UI Palette (design these)
- Background, surface, elevated surface
- Text primary, secondary, muted
- Borders
- Brand accent (TMNT green — the primary app color)
- Status colors: active (green), idle (amber), error (red), offline (gray)
- Priority colors: P0 (red), P1 (orange), P2 (blue), P3 (gray)

## Typography
- Font: Inter (already loaded)
- Clean hierarchy: page titles, section headers, card titles, body, captions, badges

## Screens to Design

### 1. Sidebar Navigation
- Fixed left sidebar, ~256px wide
- Logo area: 🐢 turtle emoji + "Mission Control" + "TMNT Fleet Operations" subtitle
- Navigation items with emoji + label + description:
  - 🏠 The Dojo — Dashboard
  - 🕳️ The Sewer — Activity Feed  
  - 🗺️ War Room — Task Board
  - 🐢 Turtle Tracker — Agent Status
  - 🗓️ Shell Calendar — Timeline
  - 📚 The Vault — Memory Browser
  - 🍕 Pizza Tracker — Metrics
- Footer: ⚙️ Splinter's Den (settings) + version number
- Active state, hover state
- Light theme sidebar (subtle background differentiation from main content)

### 2. 🏠 The Dojo (Home Dashboard) — Route: /
The command center overview. At a glance: is the fleet healthy? What needs attention?

**Layout:**
- Top: Page title + subtitle
- Stats row: 4 cards showing Fleet Status (X/Y active), In Progress tasks, Awaiting Review, Done This Week
- Three-column grid below:
  - Left: 🎯 Priority Tasks — list of P0/P1 tasks with priority badge, project badge, title, assignees
  - Center: 🐢 Fleet — compact agent cards showing emoji, name, status dot, current task, last seen
  - Right: 🕳️ Recent Activity — mini activity feed (last 10 items)

### 3. 🗺️ War Room (Task Board) — Route: /war-room
Kanban-style task board. The shared brain for fleet work.

**Layout:**
- Top bar: Title + project filter pills (All, Brinc, Cerebro, Mana, Personal, Fleet) + "New Task" button
- Horizontal scrollable Kanban with 6 columns:
  - 📥 Inbox | 📋 Assigned | 🔨 In Progress | 👀 Review | ✅ Done | 🚫 Blocked
- Each column: header with count badge, scrollable list of task cards
- Task card: priority badge (P0-P3), project badge, title, description preview, assignee avatars/emojis, due date
- Cards have subtle hover effect and a "..." menu for moving between columns
- "New Task" opens a modal with: title, description, project dropdown, priority dropdown, assignee multi-select (with agent emojis), due date

### 4. 🕳️ The Sewer (Activity Feed) — Route: /sewer
Real-time log of everything happening. The pulse of the fleet.

**Layout:**
- Top: Title + subtitle
- Filter bar: Agent filter pills (All, Molty, Raphael, Leonardo) + Project filter pills
- Activity stream: vertical list, each item has:
  - Agent avatar (circular, colored background with emoji)
  - Agent name (colored) + optional "→ sub-agent" + timestamp + project badge
  - Activity icon (📋 task, ✏️ edit, 🔄 status, 💓 heartbeat, 🧠 memory, 🚀 deploy, 💬 message)
  - Title text + optional body text
  - Subtle separator between items

### 5. 🐢 Turtle Tracker (Agent Status) — Route: /tracker
Fleet roster with detailed agent cards.

**Layout:**
- Top: Title + subtitle
- Fleet health bar: horizontal bar divided into segments, one per agent, colored by status
- Grid of agent cards (2-3 columns):
  - Each card has:
    - Header: Large emoji + Agent name (colored) + Status badge (🟢 Active / 🟡 Idle / 🔴 Error / ⚪ Offline)
    - Info rows: Kingdom theme, Project, Current task, Last heartbeat
    - Sub-agents section: bordered area showing kingdom name + count + list of sub-agent chips (emoji + name + level badge)
  - Card border uses agent's color (subtle)

### 6. 🗓️ Shell Calendar (Timeline) — Route: /calendar
**Placeholder for Phase 2** — show a clean "Coming Soon" state with the emoji, title, and brief description of what's coming.

### 7. 📚 The Vault (Memory Browser) — Route: /vault
**Placeholder for Phase 2** — same clean placeholder pattern.

### 8. 🍕 Pizza Tracker (Metrics) — Route: /pizza  
**Placeholder for Phase 3** — same clean placeholder pattern.

### 9. ⚙️ Splinter's Den (Settings) — Route: /settings
**Placeholder for Phase 2** — same clean placeholder pattern.

## Component Library Needed
- `StatCard` — for the Dojo stats row
- `TaskCard` — for Kanban and priority lists
- `AgentCard` — for Turtle Tracker
- `ActivityItem` — for the Sewer feed
- `Badge` — priority, status, project, agent
- `FilterBar` — pill-style toggle filters
- `KanbanColumn` — column wrapper with header + count
- `Modal` — for task creation
- `Sidebar` — navigation
- `PageHeader` — consistent page title + subtitle
- `HealthBar` — fleet status visualization
- `SubAgentChip` — small chip for sub-agent display
- `PlaceholderScreen` — for "Coming Soon" screens

## Technical Constraints
- All components must be React functional components with TypeScript
- Use Tailwind CSS classes only (no CSS modules or styled-components)
- Use `clsx` + `tailwind-merge` via a `cn()` utility for conditional classes
- Import icons from `lucide-react` where needed
- Data comes from Convex hooks (`useQuery`, `useMutation`) — but for the design, use placeholder/mock data inline
- Use Inter font (already configured)
- Responsive: should look good on 1440px+ screens, acceptable on 1024px

## Deliverables
Please provide complete, production-ready React + Tailwind code for:
1. `src/lib/utils.ts` — color system, constants, helper functions
2. `src/components/layout/sidebar.tsx` — sidebar navigation  
3. `src/app/layout.tsx` — root layout
4. `src/app/globals.css` — global styles (light theme)
5. `src/app/page.tsx` — The Dojo (home)
6. `src/app/war-room/page.tsx` — War Room (Kanban)
7. `src/app/sewer/page.tsx` — The Sewer (Activity Feed)
8. `src/app/tracker/page.tsx` — Turtle Tracker (Agent Status)
9. `src/app/calendar/page.tsx` — Shell Calendar (placeholder)
10. `src/app/vault/page.tsx` — The Vault (placeholder)
11. `src/app/pizza/page.tsx` — Pizza Tracker (placeholder)
12. `src/app/settings/page.tsx` — Splinter's Den (placeholder)
13. Any shared components in `src/components/ui/`

Use mock data that matches our real schema so I can easily swap in Convex queries later. The mock data should include our actual agents (Molty, Raphael, Leonardo) with their real roles and sub-agents.
