# WebClaw scope (deployment + enhanced UI)

Date: 2026-02-06 (UTC)  
Owner: TMNT squad / Squirtle 🐢 (scoping)

## 0) Executive summary

WebClaw is **not** a Next.js app; it’s a **Vite + TanStack Start** (React 19) application that renders a web chat UI and proxies all Gateway calls through **server routes** (so the Gateway token stays server-side). It already supports:

- **Multiple sessions** (via OpenClaw Gateway `sessions.*` APIs) with a **sidebar session list**
- **Create new session** flow (`/new` → creates session then navigates)
- **Rename session** (label) and **delete session**
- Basic mobile responsiveness (collapsible sidebar, `useChatMobile`)

It does **not** support Guillermo’s requested “topic-based threading” lifecycle (archive/close/reopen), promotion of an existing conversation into a new thread, or any real full-text search across sessions/threads.

The most important product decision: Guillermo’s “threads” should map to **Gateway sessions** (good fit), but we need a **metadata layer** to manage lifecycle state (open/closed/archived), pinning, and search indexes. This metadata can live either:

1) **client-side only** (localStorage) — fastest, but not shared across devices, or
2) **server-side DB** (Postgres/SQLite) — supports cross-device + multi-gateway + real search.

Given Guillermo’s “concurrent conversations blurring together” + “mobile-native” requirements, the recommended approach is:

- **Phase A (today):** deploy stock WebClaw to Railway pointing at Molty gateway.
- **Phase B1:** fork and add **multi-gateway selector** (Molty + Raphael).
- **Phase B2:** add **Thread Manager** (open/closed/archived), **promotion**, and **search** (requires persistence/indexing).

---

## 1) WebClaw architecture (as-is, from code)

### 1.1 Tech stack

From `package.json`:

- Runtime/tooling: **Vite** (`vite dev/build/preview`)
- App framework: **@tanstack/react-start** + **@tanstack/react-router**
- State/data fetching: **@tanstack/react-query**
- Local persistent settings: **zustand** (+ `persist` middleware)
- Styling: **tailwindcss v4** (`@tailwindcss/vite`) + CSS file `src/styles.css`
- UI primitives: `@base-ui/react` and custom components under `src/components/ui/*`
- Markdown rendering: `react-markdown`, `remark-gfm`, `remark-breaks`, `shiki`
- Animations: `motion`

### 1.2 Routing model

- Routes live under `src/routes/*` using TanStack file-based routing.
- Root route `src/routes/__root.tsx` provides:
  - document shell (`<html>`, `<head>`, `<body>`)
  - `QueryClientProvider` (React Query)
  - a small theme boot script reading `localStorage['chat-settings']`.
- `/` redirects immediately to `/chat/main` (`src/routes/index.tsx`).
- `/new` redirects to `/chat/new` (`src/routes/new.tsx`).
- `/connect` shows setup instructions for env vars.

### 1.3 Gateway connectivity model (critical)

**All Gateway access happens on the server**, via a websocket client using `ws`.

- `src/server/gateway.ts`:
  - Reads server env vars:
    - `CLAWDBOT_GATEWAY_URL` (default `ws://127.0.0.1:18789`)
    - `CLAWDBOT_GATEWAY_TOKEN` (recommended) or `CLAWDBOT_GATEWAY_PASSWORD`
  - Opens a WebSocket connection to the Gateway
  - Performs the required `connect` handshake
    - protocol `minProtocol/maxProtocol: 3`
    - client id `gateway-client`, displayName `webclaw`, role `operator`, scopes `['operator.admin']`
  - Implements a small request/response waiter keyed by `id`
  - Exposes:
    - `gatewayRpc(method, params)`
    - `gatewayConnectCheck()`

**Implication:** the web browser never sees the token. The browser calls local `/api/*` routes.

### 1.4 Server routes (API surface)

Implemented as TanStack Start server handlers:

- `GET /api/ping` → `gatewayConnectCheck()` (availability check)
- `GET /api/sessions` → `gatewayRpc('sessions.list', {limit:50, includeLastMessage:true, includeDerivedTitles:true})`
- `POST /api/sessions` → create new session:
  - generates a UUID `friendlyId`
  - `gatewayRpc('sessions.patch', { key: friendlyId, label? })`
  - then `sessions.resolve` to register mapping
  - returns `{ sessionKey, friendlyId }`
- `PATCH /api/sessions` → rename session (label) by `sessions.patch`
- `DELETE /api/sessions?sessionKey=…&friendlyId=…` → `sessions.delete`
- `GET /api/history?limit=200&sessionKey=…|friendlyId=…` → `gatewayRpc('chat.history', { sessionKey, limit })`
- `POST /api/send` → `gatewayRpc('chat.send', { sessionKey, message, thinking, deliver:false, timeoutMs:120000, idempotencyKey })`

There is also `GET /api/paths` which returns the *default local Clawdbot sessions directory* based on env:
- `CLAWDBOT_AGENT_ID` (default `main`)
- `CLAWDBOT_STATE_DIR` (default `~/.clawdbot`)

This endpoint is informational for the UI settings dialog; it’s not used for search/history.

### 1.5 Client-side chat screen

Key file: `src/screens/chat/chat-screen.tsx`

What it does:

- Loads session list (`useChatSessions`) and history (`useChatHistory`) via React Query.
- Renders:
  - `ChatSidebar` (sessions list + rename/delete + settings)
  - `ChatHeader`
  - `ChatMessageList`
  - `ChatComposer`
- New-chat flow:
  - `/chat/new` stores optimistic message in a local “new” cache (`appendHistoryMessage(queryClient, 'new','new', …)`)
  - calls `POST /api/sessions` to create a real session
  - stashes “pending send” and navigates to the new session
  - uses `moveHistoryMessages()` to move optimistic history from `('new','new')` to `(friendlyId, sessionKey)`.

Mobile handling:
- There is a UI state `isSidebarCollapsed` stored in React Query cache (`chat-ui.ts`).
- `useChatMobile` is used to auto-collapse after selecting a session.

Settings:
- `useChatSettingsStore` (Zustand persist) stores:
  - showToolMessages
  - showReasoningBlocks
  - theme

---

## 2) What WebClaw already supports vs Guillermo’s requirements (gap analysis)

### Requirement 1: Topic-based threading (side panel + close/archive)

**Already present (partial):**
- Side panel exists: `ChatSidebar` lists **Gateway sessions**.
- Session rename exists (label) and delete exists.

**Missing:**
- No notion of “thread/topic” beyond session label/title.
- No “close/resolved” or “archive” state.
- No filtering views (Open vs Closed vs Archived), pinning, grouping.

### Requirement 2: General chat → Thread promotion

**Already present (partial):**
- Can start in `/new` (a temporary client-only buffer) and get promoted to a real session.

**Missing:**
- Promotion from an *existing* session (e.g., `main`) into a new named thread.
- No UI action “Promote to thread” for an ongoing conversation.
- No Gateway API used for copying/moving history between sessions.

### Requirement 3: Thread lifecycle (close/resolved, reopen, search)

**Missing:**
- Lifecycle states don’t exist.
- No “reopen” flow.
- Search not implemented (see Req 6).

### Requirement 4: Mobile-native (PWA or responsive)

**Already present (partial):**
- Responsive sidebar with slide-in panel.
- Uses `viewport` meta.

**Missing:**
- No PWA manifest/service worker.
- No installable app behavior.
- No offline considerations.

### Requirement 5: Multi-session support per topic/workstream

**Already present:**
- Yes: sessions are first-class; `/chat/$sessionKey` routes per session.
- New session creation supported.

**Missing / improvements:**
- Better information architecture: “threads” are currently just a flat list of sessions.
- No per-topic status, tags, or organization.

### Requirement 6: Search (past threads/topics)

**Already present (minimal):**
- Gateway returns `derivedTitle` and `lastMessage` (useful for quick scanning).

**Missing:**
- No search UI.
- No server API for searching.
- No indexing across message history.

---

## 3) Product/technical design proposal for Guillermo’s requirements

### 3.1 Core mapping: “Thread” == Gateway Session + Metadata

- Treat every “thread” as a Gateway session (good alignment with existing code).
- Add a **Thread Metadata Store** keyed by:
  - `gatewayId` (multi-gateway support)
  - `sessionKey` (canonical key) and/or `friendlyId`

Metadata fields:

```ts
type ThreadStatus = 'open' | 'closed' | 'archived'

type ThreadMeta = {
  gatewayId: string
  sessionKey: string
  friendlyId: string
  title: string // display title; default to session.label/title/derivedTitle
  status: ThreadStatus
  tags: string[]
  createdAt: number
  updatedAt: number
  closedAt?: number
  pinned?: boolean
  // optional: lastViewedAt, unreadCount heuristics, etc.
}
```

Where to persist metadata:

- **Option A (fast): localStorage (client-only)**
  - Pros: quickest, no infra.
  - Cons: not shared between desktop + mobile; can lose state.

- **Option B (recommended): server DB**
  - Use Railway Postgres.
  - Thread metadata shared across devices.
  - Enables real search indexes, analytics, and future multi-user.

### 3.2 Thread lifecycle behaviors

- Open: default state.
- Closed: “resolved” state; still visible (separate tab) and can be reopened.
- Archived: hidden from default list; accessible via archive view.

UI changes:
- Sidebar: add tabs/filters: **Open / Closed / Archived**.
- Session item menu: add actions:
  - Close
  - Reopen
  - Archive
  - Unarchive
  - Rename (existing)
  - Delete (existing)

### 3.3 “General chat → thread promotion” designs

We need to choose what “promotion” means operationally.

**Constraint:** current WebClaw only uses Gateway APIs `chat.history`, `chat.send`, and `sessions.*`. There’s no implemented API for “move messages from session A to session B”.

Therefore promotion can be implemented in one of these ways:

1) **Soft promotion (recommended): create a new thread/session and continue there**
   - When user clicks “Promote”, WebClaw:
     - creates a new session (`POST /api/sessions`)
     - sets label to the provided thread name
     - navigates to it
     - optionally posts a “context transfer” message containing a summary and/or a link to prior thread.
   - Pros: no need to copy history; aligns with Gateway.
   - Cons: original conversation history remains in general chat session.

2) **Copy-forward promotion (best UX, more work):**
   - Fetch last N messages from current session via `chat.history`.
   - Create new session.
   - Send a “seed” message to the new session that includes:
     - either a summary (LLM-generated) or a formatted quote of recent messages.
   - Pros: new thread starts with context; still no true history move.
   - Cons: still not a true “move”, but feels close.

3) **True promotion (only if Gateway supports it):**
   - Requires a Gateway/server feature that can duplicate or reparent session logs.
   - Not in WebClaw today; would require OpenClaw changes.

### 3.4 Search design

Search comes in levels:

- **Level 0:** filter by title/label/derivedTitle (client-side)
  - Uses `sessions.list` payload.
  - Quick to implement.
  - Doesn’t search message content.

- **Level 1:** search local cached history for currently loaded sessions
  - Not great; incomplete.

- **Level 2 (recommended):** server-side indexing
  - Store thread metadata + optional message snippets.
  - Index in Postgres using:
    - `pg_trgm` for fuzzy title search, and/or
    - `tsvector` for full-text search.
  - To index message content, server must be able to read messages.

**But:** WebClaw does not have a “list all messages across all sessions” API. It can call `chat.history` per session.

So for full-text search you either:

- periodically crawl sessions (`sessions.list` then `chat.history`) and index (slow but workable for small volume), or
- add a new Gateway endpoint for search (requires OpenClaw work).

Recommended practical approach:

- Implement Level 0 immediately (search by session titles/labels).
- Add optional “deep search” (Level 2) via background indexing job in WebClaw server for the last X sessions.

### 3.5 Multi-gateway support (Molty + Raphael + future)

Current state:
- Single gateway configured by env vars in `src/server/gateway.ts`.

Goal:
- Let user choose a gateway (Molty vs Raphael) in the same UI.

Recommended implementation:

- Replace single env var set with **one JSON env var**:

```bash
WEBCLAW_GATEWAYS='[
  {"id":"molty","name":"Molty","url":"wss://molty-railway.tail3486b9.ts.net","token":"..."},
  {"id":"raphael","name":"Raphael","url":"wss://raphael-railway.tail3486b9.ts.net","token":"..."}
]'
```

- Server picks gateway per request using one of:
  - cookie `webclaw_gateway=molty`
  - header `x-webclaw-gateway: molty`
  - URL prefix `/api/:gatewayId/send` (explicit routes)

- Update `gatewayRpc` signature:

```ts
gatewayRpc(gatewayId: string, method: string, params?: unknown)
```

- Update all `/api/*` handlers to accept a gatewayId.
- Add UI selector in sidebar header.

Security note:
- Keep tokens server-side only. Never send gateway list with secrets to the browser.
- Browser only needs: `{id, name}` list (no url/token). Provide `GET /api/gateways` returning safe subset.

---

## 4) Deployment plan (Railway + Tailscale)

### 4.1 Phase A: deploy stock WebClaw

WebClaw runs as a **TanStack Start** app built by Vite.

Railway setup (high-level):

1) Create a Railway project/service from GitHub repo (or a fork).
2) Build command: `npm install && npm run build`
3) Start command: likely `npm run preview -- --host 0.0.0.0 --port $PORT`.
   - Validate in repo docs/build output; TanStack Start can ship a server build. If preview is insufficient for SSR/server routes, use TanStack Start’s recommended production command (may be `vinxi start` depending on version). Verify during implementation.
4) Set env vars in Railway:

```bash
CLAWDBOT_GATEWAY_URL=wss://molty-railway.tail3486b9.ts.net
CLAWDBOT_GATEWAY_TOKEN=***
```

Notes:
- `CLAWDBOT_GATEWAY_URL` must be **wss://** since served over HTTPS.
- Ensure Railway service has outbound WebSocket connectivity.

### 4.2 Tailscale integration considerations

Your gateway endpoint is exposed via Tailscale Serve and already reachable at public HTTPS/WSS URL.

- WebClaw server needs to connect to `wss://...tail...ts.net`.
- If the gateway is only accessible inside tailnet, Railway will not be inside tailnet by default.
  - In your case, the URL is already the public Serve endpoint, so OK.
- Token auth: server-side only.

### 4.3 Observability

Add basic health endpoints:
- `GET /api/ping` already exists and returns 200/503.

Recommend adding:
- Railway health check configured to `/api/ping`.

---

## 5) Implementation scope & estimates

Estimates assume one experienced engineer familiarizing with codebase.

### Phase A — Deploy stock WebClaw to Railway (Molty only)

- Repo fork/clone, configure Railway, env vars, test end-to-end: **2–4 hours**
- Gotchas: TanStack Start production start command may need verification.

### Phase B1 — Multi-gateway support (Molty + Raphael)

Scope:
- Add server-side gateway registry (env JSON)
- Add gateway selector UI
- Namespacing React Query caches by gatewayId
- Add `GET /api/gateways` safe list

Estimate: **1–2 days**

Risks:
- Cache key collisions if not carefully namespaced.
- Need to ensure session route includes gateway context (e.g., `/g/:gatewayId/chat/:sessionKey`), or store in cookie and keep `/chat/:sessionKey`.

### Phase B2 — Thread manager (status: open/closed/archived)

Option A (localStorage-only):
- Add `ThreadMeta` store in zustand persist
- Sidebar filters + actions
- Status badges

Estimate: **1–2 days**

Option B (server DB, recommended):
- Add DB + migrations (Prisma/Drizzle/etc.)
- CRUD API for thread metadata
- Update UI to read/write metadata

Estimate: **3–5 days**

### Phase B3 — “Promote to thread”

Soft promotion:
- UI action from header or message actions
- Create new session with label
- Navigate

Estimate: **0.5–1 day**

Copy-forward promotion (with summary):
- Fetch last N messages
- Generate summary (would require an LLM call; could be done via OpenClaw itself or a separate model)
- Send summary as first message in new session

Estimate: **2–4 days** (depends on summary mechanism)

### Phase B4 — Search

Level 0 (title/label search in sidebar): **0.5 day**

Deep search (server indexing in Postgres): **3–7 days**
- Requires designing crawl/index strategy and performance constraints.

### Phase B5 — Mobile-native / PWA

- Add manifest + icons, service worker (Vite PWA plugin), install prompt UX: **1–2 days**
- Validate iOS quirks (no true push without native, caching rules): **0.5–1 day**

---

## 6) Risks, unknowns, blockers

1) **TanStack Start production deployment details**
   - Need to confirm the correct start command for SSR/server routes on Railway.

2) **Gateway API limitations for promotion/search**
   - No existing “move history” API in WebClaw.
   - Full-text search across messages requires crawling per session or Gateway feature work.

3) **Multi-gateway routing & cache partitioning**
   - Must avoid mixing sessions/history across gateways.

4) **Persistence choice affects UX**
   - If we do localStorage-only thread lifecycle, Guillermo won’t see the same closed/archived threads on phone vs desktop.

5) **Railway filesystem is ephemeral**
   - Don’t rely on `~/.clawdbot` paths for anything meaningful in hosted WebClaw.

---

## 7) Concrete next steps

1) Phase A: deploy WebClaw to Railway using Molty gateway env vars.
2) Decide persistence strategy for threads:
   - localStorage MVP vs Postgres for cross-device.
3) Implement multi-gateway selector (Phase B1) to support Molty + Raphael.
4) Add thread lifecycle UI and metadata store.
5) Add promotion flow (soft promotion first).
6) Add sidebar search (Level 0) quickly, then decide on deep search.
