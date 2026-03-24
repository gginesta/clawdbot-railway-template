# Codebase Map — Cerebro

*Generated: 2026-03-25 by Molty 🦎 (Cartographer v1.0)*
*Source: github.com/gginesta/cerebro (main branch)*

---

## Overview

Cerebro is an **AI-powered personal CRM** for superconnectors. Users create digital business card profiles, manage contacts with AI enrichment, get AI-driven chat assistance, and track their professional network — all through a PWA (Progressive Web App) that works on mobile and desktop.

**Live URL:** https://www.meetcerebro.com
**Deploy target:** Railway (Nixpacks)
**Repo:** Private (`gginesta/cerebro`)

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | React 18 + TypeScript + Vite | PWA-enabled, Zustand state management |
| **Backend** | Express 4 + TypeScript | REST API, JWT auth |
| **Database** | PostgreSQL (Railway/Neon) | 24 migrations, UUID primary keys |
| **AI (primary)** | xAI Grok (grok-3-fast, grok-4-1-fast) | Chat, enrichment (web search), introductions |
| **AI (fallback)** | OpenRouter (Perplexity Sonar) | Fallback when xAI is down |
| **Payments** | Stripe | Subscriptions, webhooks, founding member pricing |
| **Email** | Resend | Transactional emails, verification |
| **Media** | Cloudinary | Profile photo uploads |
| **Auth** | JWT + Google OAuth + LinkedIn OAuth | Email/password + social login |
| **CSS** | Tailwind (via PostCSS) | Utility-first |
| **Local storage** | IndexedDB (via idb) | Offline contact cache |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client (React PWA)             │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Screens  │ │Components│ │  Zustand Stores  │ │
│  │  (pages)  │ │  (UI)    │ │  auth/contact/   │ │
│  │           │ │          │ │  pipeline/toast   │ │
│  └─────┬─────┘ └────┬─────┘ └────────┬─────────┘ │
│        └─────────────┼────────────────┘           │
│                      │ api.ts (fetch)             │
│                      ▼                            │
├──────────────────── REST API ─────────────────────┤
│                                                   │
│                 Server (Express)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Routes   │ │Middleware│ │    Services       │  │
│  │  17 files │ │ auth/    │ │ aiClient.ts      │  │
│  │           │ │ guard/   │ │ enrichment.ts    │  │
│  │           │ │ rate/    │ │ stripe.ts        │  │
│  └─────┬─────┘ └────┬────┘ │ contactService   │  │
│        └─────────────┼──────│ pipelineAI.ts    │  │
│                      │      └────────┬─────────┘  │
│                      ▼               ▼            │
│              ┌──────────────┐  ┌──────────┐       │
│              │  PostgreSQL  │  │  xAI API  │       │
│              │  (pg pool)   │  │ OpenRouter│       │
│              └──────────────┘  └──────────┘       │
└───────────────────────────────────────────────────┘
```

---

## Module Breakdown

### `/client/src/` — Frontend (React PWA)

**Purpose:** Single-page app serving the entire user experience — landing page, auth, onboarding, dashboard, contacts, chat, settings, CRM pipelines, business card management.

#### Screens (pages)

| Screen | Path | Purpose |
|--------|------|---------|
| `LandingPage` | `/welcome` | Marketing/signup page |
| `LoginScreen` | `/login` | Email/password + Google/LinkedIn |
| `RegisterScreen` | `/register` | New user signup |
| `DashboardScreen` | `/` | Main hub — network stats, reconnect suggestions, stale alerts |
| `FreeUserDashboard` | `/free` | Limited dashboard for free tier |
| `ContactsListScreen` | `/contacts` | All contacts with search/filter |
| `ContactScreen` | `/contacts/:id` | Single contact detail + AI enrichment |
| `AddContactScreen` | `/contacts/new` | Manual add, OCR card scan, vCard import |
| `ChatScreen` | `/chat` | AI assistant (context-aware, uses contact data) |
| `PipelinesScreen` | `/pipelines` | CRM pipeline boards |
| `PipelineBoardScreen` | `/pipelines/:id` | Kanban board for a pipeline |
| `MeetingNotesHubScreen` | `/meeting-notes` | Meeting notes with AI summarization |
| `SettingsScreen` | `/settings` | Account, subscription, privacy |
| `PublicProfileScreen` | `/p/:slug` | Public digital business card (shareable) |
| `CardCustomizeScreen` | `/card/customize` | Design business card |
| `CardAnalyticsScreen` | `/card/analytics` | Card view tracking |
| `NFCWriterScreen` | `/card/nfc` | Write profile URL to NFC tag |
| `ReferralProgramScreen` | `/referral-program` | Refer friends for rewards |
| `AFFLandingPage` | `/aff` | Conference-specific landing page |
| `ConferenceModeScreen` | `/conference` | Quick contact exchange at events |
| `BetaDashboardScreen` | `/admin/beta` | Admin analytics dashboard |

#### Onboarding Flow
`/onboarding/type` → `/onboarding/profile` → `/onboarding/import` → `/onboarding/network` → `/onboarding/welcome`

Collects: profile type (networker/sales/founder), basic info, import contacts (Google/LinkedIn/phone/vCard), network preferences.

#### Key Services

| File | Purpose |
|------|---------|
| `services/api.ts` | Central HTTP client — all backend calls, token refresh, error handling |
| `services/db.ts` | IndexedDB wrapper for offline contact cache (idb) |
| `services/syncManager.ts` | Background sync — keeps local DB in sync with server |
| `services/analytics.ts` | Event tracking |

#### State Management (Zustand)

| Store | Manages |
|-------|---------|
| `authStore` | User session, tokens, login/logout, onboarding state |
| `contactStore` | Contacts list, search, filters, CRUD operations |
| `pipelineStore` | CRM pipeline boards and deal stages |
| `subscriptionStore` | Stripe subscription state, tier limits |
| `adminStore` | Admin dashboard data |
| `toastStore` | Toast notifications |

---

### `/server/src/` — Backend (Express API)

**Purpose:** REST API serving all data operations, AI integrations, auth, and payments.

#### Routes (17 route files)

| Route | Prefix | Key Endpoints |
|-------|--------|--------------|
| `auth.ts` | `/api/auth` | Login, register, refresh, Google/LinkedIn OAuth, verify email, forgot/reset password |
| `contacts.ts` | `/api/contacts` | CRUD, bulk import, search, enrichment trigger |
| `chat.ts` | `/api/chat` | AI chat with contact context injection |
| `profiles.ts` | `/api/profiles` | Digital business card CRUD, public profile, QR code generation |
| `pipelines.ts` | `/api/pipelines` | CRM pipeline boards + stages + deals |
| `meetingNotes.ts` | `/api/meeting-notes` | Create/list notes, AI summarization |
| `ocr.ts` | `/api/ocr` | Business card OCR (image → contact data) |
| `stripe.ts` | `/api/stripe` | Subscription management, webhook handler |
| `analytics.ts` | `/api/analytics` | Profile view tracking, dashboard stats |
| `reminders.ts` | `/api/reminders` | Reconnect reminders |
| `referrals.ts` | `/api/referrals` | Referral code generation, tracking |
| `variants.ts` | `/api/variants` | Business card template variants |
| `conference.ts` | `/api/conference` | Conference mode + event-specific features |
| `invite.ts` | `/api/invite` | Beta invite tracking |
| `feedback.ts` | `/api/feedback` | User feedback collection |
| `admin.ts` | `/api/admin` | Beta dashboard, user management, nudges |
| `spotlights.ts` | `/api/spotlights` | Feature spotlight/onboarding tips |
| `internal.ts` | `/api/internal` | Health checks, internal diagnostics |
| `users.ts` | `/api/users` | User profile updates, account deletion |

#### AI Services

| Service | Model | Purpose |
|---------|-------|---------|
| `aiClient.ts` | — | Unified provider: xAI primary → OpenRouter fallback |
| `enrichment.ts` | grok-4-1-fast (web search) | Contact enrichment — work history, education, skills, company info, news |
| `claude.ts` | (legacy?) | May be unused — check |
| `gemini.ts` | (legacy?) | May be unused — check |
| `grok.ts` | (legacy?) | May be unused — direct Grok calls before aiClient unification |
| `meetingNoteAI.ts` | grok-3-fast | AI meeting note summarization |
| `pipelineAI.ts` | grok-3-fast | Pipeline stage suggestions |
| `introduction.ts` | grok-3-fast | AI-generated introduction suggestions between contacts |
| `reEngage.ts` | grok-3-fast | Re-engagement message suggestions for stale contacts |
| `contentFilter.ts` | — | Chat guardrails — blocks off-topic/harmful prompts |

#### Middleware

| File | Purpose |
|------|---------|
| `auth.ts` | JWT verification + token refresh |
| `accountGuard.ts` | Block suspended accounts |
| `chatGuardrails.ts` | Filter dangerous/off-topic chat prompts |
| `contactOwnership.ts` | Ensure users can only access own contacts |
| `rateLimiter.ts` | Rate limiting (express-rate-limit + rate-limiter-flexible) |
| `requireAdmin.ts` | Admin-only route protection |
| `validate.ts` | Zod schema validation |
| `errorHandler.ts` | Global error handler with logging |

#### Background Jobs

- **Enrichment queue processor** — runs on startup, polls DB for pending contacts, enriches via xAI/OpenRouter
- **Violation decay** — periodic decay of content filter violation counts

---

### Database Schema (PostgreSQL)

**24 migrations** (000–024). Core tables:

| Table | Purpose | Key Relations |
|-------|---------|--------------|
| `users` | User accounts | Has many: contacts, profiles, chat_history |
| `user_profiles` | Digital business cards | Belongs to user. Has: slug, QR, card template, visibility settings |
| `contacts` | CRM contacts | Belongs to user. Has: AI enrichment data, meeting context, source tracking |
| `enrichment_queue` | Background AI enrichment | References contacts |
| `chat_history` | AI chat conversations | Per-user message history (JSONB) |
| `refresh_tokens` | JWT refresh tokens | Per-user |
| `pipelines` | CRM pipeline boards | Per-user |
| `pipeline_stages` | Kanban columns | Belongs to pipeline |
| `pipeline_deals` | Deals on board | Belongs to stage, references contact |
| `meeting_notes` | Meeting notes | Per-user, optional contact reference |
| `referral_codes` | Referral tracking | Per-user |
| `stripe_customers` | Stripe mapping | Per-user |
| `subscriptions` | Subscription state | Per-user, synced via Stripe webhooks |
| `waitlist` | Beta waitlist | Email collection |
| `feedback` | User feedback | Per-user |
| `admin_nudge_cohort` | Admin engagement nudges | Per-user |

---

### `/docs/` — Documentation

Key files: API docs, deployment guides, architecture decisions.

### `/cerebro/` — Marketing docs

Marketing strategies (v1–v7), beta candidate lists, getting started guides, Cyberport funding research.

### `/cerebro_deep_dive/` — Development artifacts

Leonardo's working directory — PR audits, fix plans, specs for features (contact sharing, CRM pipelines, meeting notes, referrals, smart reminders). Screenshots, component patches.

### `/cerebro_build/` — Build artifacts

Staged code for specific features (admin dashboard, migrations).

### `/launchpad/` — Deployment scripts

Launch/deploy utilities.

### `/scripts/` — Utility scripts

Maintenance, data migration, setup scripts.

---

## Key Data Flows

### Contact Enrichment Flow
```
User adds contact → POST /api/contacts → Insert DB → Add to enrichment_queue
                                                          │
Enrichment worker (background) ◄──────────────────────────┘
    │
    ├─ Build prompt from: name + title + company + LinkedIn
    ├─ Call xAI grok-4-1-fast (with web search)
    │   └─ Fallback: OpenRouter (Perplexity Sonar)
    ├─ Parse: work_history, education, skills, company_info, news, ai_summary
    └─ UPDATE contacts SET enrichment_status='completed'
```

### AI Chat Flow
```
User message → POST /api/chat
    │
    ├─ chatGuardrails middleware (block harmful prompts)
    ├─ Load user's contacts as context
    ├─ Build system prompt with CRM context
    ├─ Call xAI grok-3-fast (fallback: OpenRouter)
    └─ Stream response → Save to chat_history
```

### Auth Flow
```
Register → email + password (bcrypt) → JWT issued
        OR Google OAuth → callback → JWT issued
        OR LinkedIn OAuth → callback → JWT issued

Login → verify credentials → access_token (15min) + refresh_token (7d)
Refresh → POST /api/auth/refresh → new token pair
```

### Subscription Flow
```
User → Stripe Checkout → webhook → update subscriptions table
                                  → update user account_type
Tiers: free (3 contacts) → pro ($9.99/mo, 500 contacts) → founding ($4.99/mo lifetime)
```

---

## Navigation Guide

| "I want to..." | Look at... |
|----------------|-----------|
| Understand the app's pages | `client/src/App.tsx` (all routes) |
| Add a new API endpoint | `server/src/routes/` + register in `server/src/index.ts` |
| Change AI behavior | `server/src/services/aiClient.ts` (provider logic) |
| Modify contact enrichment | `server/src/services/enrichment.ts` |
| Update the database schema | Add migration in `server/src/models/migrations/` |
| Change auth logic | `server/src/routes/auth.ts` + `server/src/middleware/auth.ts` |
| Update business card templates | `client/src/components/CardTemplates.tsx` |
| Change subscription tiers | `server/src/config/pricing.ts` + `server/src/services/usageTracker.ts` |
| Modify the landing page | `client/src/components/landing/` directory |
| Add a new dashboard widget | `client/src/components/dashboard/` directory |
| Debug deployment | `railway.toml` + check `/api/health` endpoint |
| Understand state management | `client/src/store/` (Zustand stores) |
| Add chat guardrails | `server/src/middleware/chatGuardrails.ts` + `server/src/services/contentFilter.ts` |

---

## Gotchas & Non-Obvious Things

1. **Legacy AI files:** `claude.ts`, `gemini.ts`, `grok.ts` in services/ may be dead code — all AI calls should go through `aiClient.ts` now. Verify before deleting.
2. **Enrichment uses xAI Responses API** (`/v1/responses`) not Chat API — this enables web search for contact enrichment.
3. **JSONB everywhere** — contacts store emails, phones, work_history, skills as JSONB. Flexible but hard to query.
4. **PWA with IndexedDB** — contacts are cached locally. `syncManager.ts` handles bidirectional sync. Watch for stale cache bugs.
5. **Conference mode** — special UX for events (AFF conference). Has its own route, theme, and signup flow.
6. **Founding member pricing** — special $4.99/mo lifetime tier. Logic in `subscriptionStore` + `server/src/config/pricing.ts`.
7. **Multiple AI model references** — `grok-3-fast` for chat/general, `grok-4-1-fast` for enrichment (web search capable). Models are hardcoded in service files.
8. **cerebro_deep_dive/ is Leonardo's workspace** — not production code. Don't merge directly.
9. **No test database** — tests in `__tests__/` directories but CI may need DATABASE_URL.
10. **Stripe webhooks** — critical for subscription state. If Railway URL changes, update Stripe webhook endpoint.

---

## File Stats

| Directory | Files | Purpose |
|-----------|-------|---------|
| `client/src/` | ~140 | React app (screens, components, stores, services) |
| `server/src/` | ~65 | Express API (routes, services, middleware, models) |
| `server/src/models/migrations/` | 25 | DB schema evolution |
| `cerebro/` | ~10 | Marketing docs |
| `cerebro_deep_dive/` | ~35 | Dev artifacts (Leonardo) |
| `docs/` | ~5 | Documentation |
| `scripts/` | ~10 | Utilities |
| **Total** | ~505 | |

---

*This map is a point-in-time snapshot. Run cartographer again after major changes.*
