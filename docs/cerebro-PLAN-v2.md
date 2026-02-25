# Cerebro Plan v2 — Critique + Enhanced Execution Plan (Prepare / Execute / Evaluate)

Date: 2026-02-23 (HKT) | Last updated: 2026-02-25 (HKT)
Owner: Leonardo 🔵 (execution) + Molty 🦎 (infra + security)
Objective: 10 paid users by 2026-03-31 (HKT)

This is v2. It keeps v1 as reference: `./PLAN.md`.
Coordinator review + security hardening added: 2026-02-25 (Molty).

---

## 0) Critique of v1 (What was good / what was missing)

### What v1 did well
- Clear outcome target (10 paid by Mar 31) and pragmatic revenue path (Stripe payment links + manual entitlement).
- Sensible phased framing: make it work → make it good → make it sell.
- Identified the right metrics categories (funnel, usage, retention, revenue).

### Gaps fixed in v2
1. **Sequencing wasn't tight enough**: Phase 1 and Phase 2 overlapped in dates; execution order and gates weren't explicit.
2. **No explicit "Aha Moment" definition**: we said "Aha moment is flawless" but didn't specify what it is, how we detect it, or what must be true.
3. **Milestones lacked acceptance criteria**: "validated" can mean anything; we need test scripts + pass/fail gates.
4. **Conversion mechanism not fully operationalized**: payment links are easy, but entitlement + confirmation + support routing needs an SOP and a visible daily loop.
5. **No explicit risk register**: e.g., OCR failures, enrichment latency, mobile camera permissions, PWA cache regressions, onboarding confusion.
6. **Feedback loop needs structure**: where feedback comes in, how it becomes issues/PRs, and cadence/ownership.

### Gaps added after coordinator review (2026-02-25)
7. **Phase 0 gate date was unrealistic**: S0 not done, known prod blocker (white screen), no device testing owner. Gate shifted to Mar 3.
8. **Real device QA had no named owner**: explicitly assigned to Guillermo.
9. **Stripe Live not scheduled before Phase 2**: added as M1.x tail task.
10. **Beta candidate list didn't exist**: added as Phase 0 parallel task (owned by Raphael).
11. **S0 (Codex-ready repo) had no hard deadline**: pinned to Feb 26 EOD.
12. **PR merge ownership was ambiguous**: defined review SLA and merge authority.
13. **Known prod blocker (white screen) missing from plan**: added as P0 in Section 9.
14. **Security hardening not planned**: added as Section 10 with full multi-step breakdown.

---

## 1) North Star + Aha Moments

### North Star (product)
A **mobile-first** workflow that turns a real-world business card (or contact info) into a **clean, enriched, useful contact** in seconds — and helps a "superconnector" make better introductions with confidence.

### ICP Definition (concrete, for beta sourcing and messaging)
**Primary ICP — The Superconnector:**
- Title/role: Founder, investor, BD lead, VC partner, accelerator manager, senior sales
- Behavior: Meets 5–20 new people per week at events, dinners, or via intros
- Pain: Business cards pile up unprocessed; "I know I met someone in X" but can't find them; intro requests need manual memory search
- Network size: 200–2000 professional contacts
- Device: Mobile-primary; will use on the spot at events

This definition is Raphael's brief for beta sourcing. Do not invite people who don't fit.

### MVP definition (customer-outcome shaped)
**MVP in one sentence:** Cerebro turns business cards into clean, enriched contacts and lets a superconnector ask "who should I introduce to X?" and get reliable, actionable suggestions.

**The 5 proof deliverables (what proves MVP is real):**
1. **Capture reliability:** scan/import works on mobile end-to-end.
2. **Contact quality:** editable fields + enrichment visible (with clear status).
3. **Retrieval/chat usefulness:** recommendations are grounded in contact fields + notes (no hallucination-y answers).
4. **Next-action:** right after save, user sees one concrete next step (note / follow-up / intro draft).
5. **Paywall:** Free is limited; Pro/Premium unlock meaningful value without runaway AI cost.

### Aha Moments

**Aha #1 — "Magic capture" (Primary, Phase 0 gate)**
- User scans/imports a card → clean contact created with correct name + company + role + email/phone
- Contact saved and visible in list immediately
- This is the gate for Phase 0 → Beta

**Aha #2 — "Instant usefulness" (Secondary)**
- Immediately after saving, user sees one concrete next action:
  - "Add a note / context" OR "Set a follow-up reminder" OR "Draft an intro email" OR "Ask Cerebro: What should I do with this contact?"

**Aha #3 — "I look professional" (Social proof)**
- User can share a polished digital contact card / QR

### Instrumentation for Aha #1
- `scan_started` → `scan_completed` (or `import_completed`)
- `contact_created`
- `contact_viewed` within 60 seconds of creation
- `next_action_clicked` (note/reminder/chat)

---

## 2) Timeline (revised)

| Phase | Dates (HKT) | Theme |
|-------|-------------|-------|
| S0 — Codex-ready repo | Feb 25–26 | Prerequisite |
| P0 Fix — White screen | Feb 25–26 | Unblock |
| Phase 0 — Reliability + Aha #1 | Feb 27–Mar 3 | Make it work |
| Phase 1 — Beta loop + retention | Mar 4–Mar 17 | Make it good |
| Phase 2 — Conversion + expansion | Mar 18–Mar 31 | Make it sell |

**Phase 0 gate date shifted to Mar 3 (from Feb 27).** Reason: S0 not complete, white screen blocking QA, real-device session needs scheduling. Starting with a real 5-day window is better than declaring a gate passed that wasn't tested.

---

## 3) S0 — Codex-ready Repo (hard deadline: Feb 26 EOD HKT)

This is a prerequisite. No Codex issues dispatched until S0 is complete.

### S0 Acceptance Criteria
- Branch protection on `main`: PR required, CI must pass, 1 approval required, no force push
- Labels exist in repo: `codex-ready`, `codex-running`, `status:needs-review`, `risk:high`, `risk:medium`, `risk:low`, `area:auth`, `area:scan`, `area:contact`, `area:enrichment`, `area:chat`, `area:payments`, `area:security`, `area:infra`
- `.github/ISSUE_TEMPLATE/codex-ready.md` exists with: User story, repro steps, acceptance criteria, test steps, analytics impact
- `.github/pull_request_template.md` exists with: Summary, how to test (mobile steps), rollback procedure
- Root `AGENTS.md` exists: setup instructions, verify commands, no secrets, PR size guidance (≤400 lines, one concern per PR)
- GitHub Actions CI: lint + type-check + unit tests on every PR (even if tests are sparse)
- GitHub Actions security: `npm audit` gate (fail on high severity)

### S0 Execution (Codex issue: "S0: Make repo Codex-ready")
One Codex PR covers all file creation. Leonardo reviews and merges.

---

## 4) P0 Fix — White Screen (parallel with S0, also Feb 26 EOD)

**Known prod blocker:** `www.meetcerebro.com` renders a white page. SPA loads (API is healthy, 200ms responses) but React renders nothing. This must be fixed before any QA can begin.

### Investigation Steps
1. Open browser DevTools on `www.meetcerebro.com` → Console tab → capture all errors
2. Check Network tab: what JS bundle is loading? Are there 404s or CORS errors?
3. Check Railway logs: any server-side errors?
4. Likely causes:
   - `CLIENT_URL` env var mismatch blocking API requests
   - Missing env var causing undefined reference crash at startup
   - Build artifact not serving the correct `index.html`
   - Service worker caching a broken version

### Codex Issue: "Fix: white screen on production site"
- Area: `area:infra`
- Risk: `risk:high`
- Acceptance criteria: Loading `www.meetcerebro.com` on fresh mobile browser shows the app home/login screen within 5 seconds

---

## 5) Phase 0 (Feb 27–Mar 3): Reliability + Aha Moment Gate

### Goal
A brand-new user can complete Aha #1 on mobile without confusion or failure.

### Phase 0 Deliverables
1. Mobile QA Script + pass report (run by Guillermo)
2. Top-10 blocker list → codex-ready issues
3. Instrumentation live for the Aha funnel
4. Aha #1 pass gate on iOS + Android
5. Beta candidate list (run in parallel by Raphael)

### Milestones

**M0.1 — Mobile QA Pass (iOS + Android)**
- **Owner for execution: Guillermo** (Leonardo cannot run on real devices)
- Pre-condition: white screen fix must be deployed first
- Devices: at least 1 real iPhone + 1 real Android (not emulator)
- QA script is written by Leonardo first, then Guillermo runs it
- Pass criteria:
  - App loads (no blank screen, no crash)
  - Login/signup completes on both platforms
  - Camera permissions + photo library permissions prompt correctly and can be granted
  - Landscape and portrait both render without layout breakage

**M0.2 — Core Flow Pass (end-to-end)**
- Flow: signup → scan/import → contact created → contact saved → contact listed → contact detail → enrichment status visible
- Pass criteria:
  - 90%+ success across 10 attempts (mix of lighting conditions and card types)
  - Median time: scan/import → contact created ≤ 20 seconds
  - Enrichment visible as `pending / success / fail` with retry path
  - Save works even if enrichment fails (enrichment must never block save)
  - No silent failure states: all errors show an actionable message to the user

**M0.2b — Chat / Recommendations Quality Gate**
- 10 scripted queries must produce useful, grounded answers
- Example queries:
  - "Who should I intro to an AI SDR founder?"
  - "Which of my contacts are investors in SEA?"
  - "Who can help with hiring a PM?"
  - "Who do I know at healthcare companies?"
  - "What should I do with [contact name]?"
- Pass criteria:
  - Answers reference actual contact data (not hallucinated)
  - Model says "I don't know" or "add more info" when it genuinely doesn't have the data
  - Zero confident hallucinations in 10 scripted runs
- Failure → issue per failing query type (grounding, retrieval, prompt, UI)

**M0.3 — Aha #1 Instrumentation Verified**
- Events `scan_started`, `scan_completed`, `contact_created`, `contact_viewed` are visible in analytics
- Can compute: signup → scan completed → contact created funnel
- At least one complete Aha #1 flow visible in analytics data

**Gate: Phase 0 complete only when M0.1 + M0.2 + M0.2b + M0.3 are all green.**

### Phase 0 Execution Process
1. Leonardo writes QA script for M0.1 → shares with Guillermo
2. Guillermo runs QA on real devices, records results (screen recordings welcome)
3. Triage together: P0 (blocks Aha) / P1 (hurts retention) / P2 (polish)
4. Leonardo converts P0/P1 to codex-ready issues (acceptance criteria + repro + test steps)
5. Dispatch Codex: max 3 tasks in parallel to avoid merge conflicts
6. PR review SLA: Leonardo reviews within 4 hours of PR open, merges same day if passing
7. Merge authority: Leonardo merges; Molty does Railway deploy
8. Re-test: Guillermo re-runs affected QA steps after each deploy

### Codex PR Rules (Phase 0)
- One PR = one change theme (no kitchen-sink PRs)
- All PRs must include: "How to test on mobile" section
- PRs touching auth, payments, or env vars must be flagged `risk:high` and reviewed by Leonardo + Molty before merge

### Parallel Task: Beta Candidate List (owned by Raphael)
- **Owner: Raphael** (GTM)
- **Deadline: Mar 1** (before Phase 0 gate)
- Deliverable: 30-person shortlist matching the ICP definition in Section 1
- Format: Name, role, how they're connected to Guillermo, why they fit (1 line each)
- Guillermo + Raphael finalise to 20 invitees (2 cohorts of 10)
- This list is needed for Phase 1 onboarding; prepping it now means no delay at Phase 1 start

---

## 6) Phase 1 (Mar 4–Mar 17): Beta Loop + Retention

### Goal
10–20 beta users use Cerebro weekly; we can reliably learn and ship improvements.

### Deliverables
- Beta onboarding kit (email + 2-minute setup steps + "Try this first" → Aha #1)
- Feedback intake + triage pipeline
- Weekly release cadence
- D1, D7 retention measurement
- Stripe Live configured and tested (pre-Phase-2 requirement)

### Milestones

**M1.1 — Beta onboarding kit ready**
- Onboarding email written by Raphael/Leia (sub-agent), finalised by Guillermo
- Contents: "Try this first" (forces Aha #1: scan 2 cards, verify list, do 1 next action); where to give feedback; known limitations + expected response time
- In-app "Getting Started" flow or prompt mirrors the email

**M1.2 — Feedback loop operational**
- Single intake channel live (link/form/email — pick one, stick to it)
- Triage 3x/week minimum (Leonardo)
- Every item → (a) issue, (b) decision, or (c) explicitly rejected with written reason
- Triage output logged in `LOG.md`

**M1.3 — Retention baseline established**
- D1 and D7 measurable for the first beta cohort
- At least 3 changes queued from observed drop-offs before Phase 2 starts

**M1.4 — Stripe Live configured + tested (critical, required before Phase 2)**
- **Owner: Guillermo** (requires Stripe dashboard access to create live keys)
- **Deadline: Mar 14** (before Phase 2 starts)
- Steps:
  1. Guillermo activates Stripe Live mode in dashboard
  2. Generates Live `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`
  3. Molty adds to Railway prod env vars
  4. Creates payment links for Pro and Premium tiers
  5. Webhook endpoint verified: Stripe → Railway → DB update works end-to-end
  6. End-to-end test: create test transaction in live mode with $1 product → confirm entitlement toggle + confirmation email
- If this isn't done by Mar 14, Phase 2 start date slips

### Phase 1 Execution Process
1. Invite cohort 1 (10 users): personalised email with onboarding kit
2. Daily 10-min metric check: Aha funnel + errors
3. Weekly Beta Review (45 min):
   - Metrics → top drop-off → top 5 issues → codex-ready tickets → PRs → deploy
4. After cohort 1 week 1 data, invite cohort 2
5. Add 1 improvement explicitly targeting Aha #2 (instant usefulness) before end of Phase 1

---

## 7) Phase 2 (Mar 18–Mar 31): Conversion + Expansion

### Goal
Convert 10 users to paid using Stripe payment links + manual entitlement.

### Deliverables
- Pricing tiers + upgrade CTA in-app
- Manual entitlement SOP
- Daily revenue ops loop

### Milestones

**M2.1 — Payment links created (Pro + Premium)**
- Links tested end-to-end in live mode
- Price points confirmed by Guillermo
- Pre-condition: M1.4 Stripe Live must be complete

**M2.2 — Manual entitlement SOP finalised**
- Who checks payments: Guillermo (daily, twice/day)
- Where: Stripe dashboard + DB
- How to identify user and upgrade: email lookup → DB `subscription_tier` update
- Confirmation message template ready
- Refund/support process defined

**M2.3 — Free limits + cost guardrails in-app**
- Hard contact/scan cap enforced (Free: 50 contacts, 5 scans/mo — already in code, verify it's enforced)
- AI usage cap enforced per tier (rate limiter active)
- Upgrade CTA fires **after Aha #1** (not before)
- Clear messaging: what each tier unlocks

**M2.4 — Conversion targets**
- 3 paid by Mar 21
- 10 paid by Mar 31

### Phase 2 Execution Process
1. At Phase 2 start: verify Free limits enforced in prod
2. Add in-app upgrade CTA (Codex issue)
3. Run daily conversion ops: check payments → upgrade → confirm → log (10 min, 2x/day)
4. Weekly pricing/positioning review: is the value prop landing?

---

## 8) Operating System (Roles, Cadence, Issue Format)

### Roles
| Agent | Domain | Owns |
|-------|--------|------|
| Leonardo 🔵 | Product + execution | Codex issues, PR review/merge, QA scripts, PLAN/TRACKER/DECISIONS |
| Molty 🦎 | Infra + security | Railway env, deploys, monitoring, change control, security review |
| Raphael 🔴 | GTM | Beta candidate sourcing, outreach ops, upgrade messaging, follow-ups |
| Guillermo 👤 | Product owner + device QA | Final call on ICP/pricing, real-device testing, introductions to beta users, Stripe setup |

### Cadence
- **Daily (Mon–Fri):**
  - 30–60 min build/review window (PRs, merges, deployments)
  - 10 min metric check: Aha funnel + errors
  - Update Mission Control War Room task status
  - Log to `LOG.md` in this folder (5-line minimum)
- **Weekly:**
  - Beta Review (45 min): metrics → top drop-off → top 5 fixes → codex-ready → ship

### Codex-Ready Issue Format (mandatory)
Every issue dispatched to Codex must include:
- **User story**: As a [role], I want [action] so that [outcome]
- **Repro steps** (if bug): numbered, specific
- **Acceptance criteria**: pass/fail testable statements
- **How to test on mobile**: step-by-step (including device OS, browser if relevant)
- **Analytics impact**: any events added, changed, or removed
- **Risk level**: `risk:low` / `risk:medium` / `risk:high`
- **Area label**: `area:auth` / `area:scan` / `area:contact` / `area:enrichment` / `area:chat` / `area:payments` / `area:security`

### PR Review Protocol
- SLA: Leonardo reviews within 4 hours of PR open
- Same-day merge target for PRs opened before 14:00 HKT
- Merge authority: Leonardo
- Any `risk:high` PR: Leonardo reviews + Molty signs off before merge
- No kitchen-sink PRs: one concern per PR, ≤400 lines changed (excluding tests)
- Required in every PR description: "How to test" + rollback procedure

---

## 9) Risks + Mitigations

0. **Scope creep into "full CRM"**
   - Mitigation: lock March scope to capture → enriched contacts → grounded recommendations → basic paywall; explicitly defer deal tracker, pipeline, heavy integrations

1. **White screen in production (P0 — known)**
   - Status: Active blocker, must fix before any QA
   - Mitigation: debug prod bundle, check env vars, check service worker cache

2. **Mobile permissions / camera instability**
   - Mitigation: explicit permission screens + retry UX + QA on real iOS + Android devices

3. **OCR accuracy variability**
   - Mitigation: show confidence + quick edit UI + save even if enrichment fails (enrichment must never block save)

4. **Enrichment latency / failures**
   - Mitigation: async enrichment with visible `pending/success/fail` UI; fallback states always render; retry available

5. **PWA/service worker cache regressions**
   - Mitigation: release checklist includes SW version bump + cache invalidation test on every deploy

6. **Manual entitlement errors**
   - Mitigation: SOP + single source of truth (Stripe dashboard) + audit log entry per upgrade in DB

7. **Stripe Live not set up before Phase 2**
   - Mitigation: M1.4 deadline is Mar 14; if delayed, Phase 2 start slips (no workaround)

8. **Beta user quality mismatch**
   - Mitigation: ICP definition enforced by Raphael; Guillermo approves final list

9. **Codex PR quality / incomplete implementations**
   - Mitigation: detailed codex-ready format; Leonardo re-tests before merge; reject and re-dispatch if not meeting acceptance criteria

10. **AI cost overrun**
    - Mitigation: per-tier AI usage caps enforced server-side; Free tier has no chat access; monitor costs weekly

---

## 10) Security Hardening Plan

This section is owned by Molty 🦎 (review, tracking, deployment) in coordination with Leonardo (implementation via Codex).

### Current Security Posture (audited 2026-02-25)
**Already in place (good foundation):**
- Helmet.js with CSP and HSTS for production ✅
- CORS locked to `CLIENT_URL` in production ✅
- Auth rate limiting: PostgreSQL-backed, 5 login attempts/min, 20/hr, 3 registrations/hr ✅
- Chat guardrails: in-memory rate limiting + prompt injection detection + content filter ✅
- File upload validation: mimetype + file size limits on OCR and profile routes ✅
- HTTPS redirect in production ✅
- JWT with refresh token + blacklist on logout ✅

**Gaps identified (prioritised):**

#### SEC-P0 — Fix before Phase 0 gate (required)

**SEC-1: Remove `unsafe-inline` from CSP script-src**
- Current: `scriptSrc: ["'self'", "'unsafe-inline'"]` — negates most XSS protection from CSP
- Fix: migrate to nonce-based or hash-based inline scripts; or compile away inline scripts
- Codex issue: `area:security`, `risk:high`
- Note: React production builds don't typically need unsafe-inline — investigate why it's there

**SEC-2: Add global API rate limiting (non-auth endpoints)**
- Current: rate limiting only on auth + chat endpoints; contact CRUD, OCR uploads, enrichment triggers are unprotected
- Fix: add global rate limiter middleware (e.g., 100 req/min per IP) applied before all route handlers
- Codex issue: `area:security`, `risk:medium`

**SEC-3: Input sanitization / validation middleware**
- Current: no joi/zod or express-validator; TypeScript types don't validate at runtime
- Fix: add `zod` schema validation on all request bodies (contacts, notes, chat messages, profile updates)
- Codex issue: `area:security`, `risk:medium`
- Why: malformed requests can reach DB or AI without sanitization

**SEC-4: Multi-tenant data isolation audit**
- Current: not verified — unknown if contact routes properly scope all queries to `req.userId`
- Fix: audit every DB query in contacts, chat, profiles, analytics routes to confirm `WHERE user_id = $userId` is applied
- Codex issue: `area:security`, `risk:high`
- Test: user A must never be able to read/write user B's contacts via any API call

**SEC-5: Stripe webhook signature verification**
- Current: webhook endpoint exists but verification status unconfirmed
- Fix: verify `stripe.webhooks.constructEvent(rawBody, sig, STRIPE_WEBHOOK_SECRET)` is used; raw body must be preserved (not parsed JSON)
- Codex issue: `area:payments area:security`, `risk:high`
- Required before Stripe Live goes live (M1.4)

#### SEC-P1 — Fix during Phase 1

**SEC-6: Chat guardrail rate limiter is in-memory only**
- Current: chat guardrails use `RateLimiterMemory` — resets on container restart (deployments reset all chat limits)
- Fix: migrate chat guardrail rate limiter to PostgreSQL-backed (same pattern as auth limiter) or Redis
- Codex issue: `area:security`, `risk:medium`

**SEC-7: Indirect prompt injection via stored contact data**
- Current: contentFilter.ts catches direct user input injection; but malicious prompts stored in contact notes are passed to AI during chat without sanitization
- Fix: sanitize/escape contact notes + context passed to AI; add a "context safety" wrapper that strips known injection patterns from DB data before AI submission
- Codex issue: `area:security area:chat`, `risk:high`

**SEC-8: JWT storage location**
- Investigate: are JWTs stored in localStorage (XSS-accessible) or httpOnly cookies?
- If localStorage: migrate to httpOnly cookie + CSRF token pattern
- Codex issue: `area:auth area:security`, `risk:high`

**SEC-9: Dependency audit in CI**
- Add `npm audit --audit-level=high` step to GitHub Actions CI on every PR
- Fail the build on high-severity vulnerabilities
- Codex issue: `area:security area:infra`, `risk:low`

**SEC-10: Secret scanning in CI**
- Add `git-secrets` or `gitleaks` as a GitHub Actions step
- Prevent accidental commit of API keys, tokens, or secrets
- Codex issue: `area:security area:infra`, `risk:medium`

#### SEC-P2 — Fix during Phase 2 or post-launch

**SEC-11: Owner/admin endpoint protection**
- The `owner` tier has elevated limits; verify there are no admin-only API endpoints accessible without explicit owner-tier check
- Add an `isOwner` middleware guard if any exist
- Codex issue: `area:auth area:security`, `risk:medium`

**SEC-12: Session invalidation on password change**
- On password change or account recovery, all existing refresh tokens should be invalidated
- Verify the blacklist covers this case
- Codex issue: `area:auth area:security`, `risk:medium`

**SEC-13: File upload path traversal audit**
- Verify Multer disk storage (if used) doesn't expose path traversal
- Prefer memory storage + direct cloud upload (Cloudinary); confirm no temp files persist on Railway disk
- Codex issue: `area:security`, `risk:medium`

**SEC-14: CORS preflight for all mutation routes**
- Audit that OPTIONS preflight is handled correctly for all POST/PUT/DELETE routes
- Ensure CORS doesn't fall back to permissive mode on error
- Codex issue: `area:security`, `risk:low`

### Security Gate Requirements per Phase
| Phase | Required | Recommended |
|-------|----------|-------------|
| Phase 0 gate | SEC-1, SEC-2, SEC-3, SEC-4, SEC-5 | SEC-9 |
| Phase 1 gate | SEC-6, SEC-7, SEC-8, SEC-10 | SEC-11 |
| Phase 2 gate | SEC-11, SEC-12, SEC-13 | SEC-14 |

### Security Change Control
Any change touching auth, payments, env vars, or AI prompts:
- Must be tagged `risk:high`
- Requires Leonardo review + Molty sign-off before merge
- One change per deploy; no mixed security + feature PRs
- Rollback target must be declared before merge

---

## 11) Evaluate (What "Progress" Looks Like)

### Phase 0 success metrics
- Signup → scan completion rate
- Scan → contact created rate
- Time-to-Aha (signup → contact created)
- Error rate (camera / OCR / enrichment)

### Phase 1 success metrics
- D1 retention, D7 retention
- Weekly active users in beta cohort
- Feedback items processed/week + time-to-fix

### Phase 2 success metrics
- Paid conversions/week
- Time from signup to paid
- Support load per paid user

---

## 12) Competitive Context (2-hour scan, non-blocking)

**To do before Phase 1 messaging is written (by Mar 3):**
- HiHello: digital business card app — how do they position enrichment?
- LinkedIn: what does their "contact" experience feel like on mobile?
- Clay: AI enrichment for sales teams — what are they missing for individuals?
- Focus: identify 3 table-stakes features we might be missing; identify 2 positioning angles competitors haven't claimed

Owner: sub-agent Han (Scout) or Leonardo during Phase 0 downtime.
Output: 1-page summary in `/data/shared/cerebro/cerebro_deep_dive/COMPETITIVE-SCAN.md`

---

## 13) Mission Control Tracking

**All Cerebro work tracked in TMNT Mission Control War Room:**
- Dashboard: https://tmnt-mission-control.vercel.app
- API: https://resilient-chinchilla-241.convex.site
- Leonardo creates tasks in War Room via `POST /api/task` (project=cerebro)
- Leonardo logs activity via `POST /api/activity` after each meaningful work session
- Status updates: inbox → assigned → in_progress → review → done → blocked
- Skill reference: `/data/shared/skills/mission-control/SKILL.md`

**Existing anchor task:** "Cerebro — first 10 paying customers" (In Progress)

**Task tree to create (Leonardo to do before Phase 0 starts):**
- S0: Make repo Codex-ready (assignee: leonardo, due: Feb 26)
- P0-Fix: White screen on production (assignee: leonardo, due: Feb 26)
- M0.1: Mobile QA pass — iOS + Android (assignee: guillermo, due: Mar 1)
- M0.2: Core flow reliability + enrichment status (assignee: leonardo, due: Mar 3)
- M0.2b: Chat quality gate — 10 scripted queries (assignee: leonardo, due: Mar 3)
- M0.3: Aha funnel instrumentation verified (assignee: leonardo, due: Mar 3)
- Beta candidate list 30→20 (assignee: raphael, due: Mar 1)
- SEC-1: Fix unsafe-inline CSP (assignee: leonardo, due: Mar 3)
- SEC-2: Global API rate limiting (assignee: leonardo, due: Mar 3)
- SEC-3: Input validation middleware (assignee: leonardo, due: Mar 3)
- SEC-4: Multi-tenant data isolation audit (assignee: leonardo, due: Mar 3)
- SEC-5: Stripe webhook signature verification (assignee: leonardo, due: Mar 14)
- M1.4: Stripe Live keys configured + tested (assignee: guillermo, due: Mar 14)

---

## 14) Immediate Next Actions (ordered)

1. **Leonardo:** Create all War Room tasks from Section 13 above (do this before anything else)
2. **Leonardo:** Create and dispatch Codex issue for S0 (Codex-ready repo)
3. **Leonardo:** Debug white screen issue (inspect prod bundle + env + network)
4. **Raphael:** Begin beta candidate sourcing per ICP definition in Section 1
5. **Guillermo:** Commit to a 2-hour real-device QA session during Phase 0 window (Feb 27–Mar 3)
6. **All:** Do not start Phase 1 until Phase 0 gate is confirmed green

---

## References
- v1 plan: `./PLAN.md`
- Tracker: `./TRACKER.md`
- Decisions: `./DECISIONS.md`
- Log: `./LOG.md`
- Mission Control doc: `./MISSION-CONTROL.md`
- Railway prod settings: `/data/shared/cerebro/RAILWAY-PROD-SETTINGS.md`
- CODEX integration plan: `/data/shared/cerebro/CODEX-INTEGRATION-PLAN.md`
