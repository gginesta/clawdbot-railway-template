# PLAN Registry — TMNT Squad
*Compiled by Molty 🦎 | Updated: 2026-03-13*
*Source: /data/workspace/plans/ + Mission Control*

---

## Summary
| Status | Count |
|--------|-------|
| ✅ Complete | 13 |
| 🔄 In Progress | 3 |
| ⏸ Parked/Deferred | 0 |
| ❌ Superseded | 1 |

---

## PLAN-001 — Bidirectional Todoist ↔ Mission Control Sync
**File:** `plans/PLAN-001-standup-sync-fix.md`  
**Created:** 2026-02-24  
**Status:** ✅ COMPLETE  
**What it did:** Established bidirectional sync between Todoist and Mission Control. Daily standup now cross-checks both systems. MC is source of truth; Todoist gets project tags.  
**Key output:** `process_standup.py` three-way routing, `standup-audit-YYYY-MM-DD.md` post-standup audit.

---

## PLAN-002 — Autonomous Nightly Task Worker
**File:** `plans/PLAN-002-task-worker.md`  
**Created:** 2026-02-24  
**Status:** ✅ COMPLETE (LIVE — this cron)  
**What it did:** Created the overnight cron system. Molty runs at 03:00 HKT, picks 1-3 tasks from Todoist/MC, executes, logs results.  
**Key output:** Overnight cron `80105aa4`, this very task worker prompt.

---

## PLAN-003 — Persistent Standup Database
**File:** `plans/PLAN-003-persistent-standup-db.md`  
**Created:** 2026-02-24  
**Status:** ✅ COMPLETE (2026-02-26)  
**What it did:** Replaced ephemeral per-day standup pages with a single persistent Notion DB reused daily. `get_or_create_persistent_db()` in `daily_standup.py`.  
**Key output:** Notion DB `2fe39dd69afd81f189f7e58925dad602`.

---

## PLAN-004 — Squad Overnight Workflow + Morning Briefing Squad
**Files:** `plans/PLAN-004-morning-briefing-squad.md`, `plans/PLAN-004-squad-overnight-workflow.md`  
**Created:** 2026-02-24 / 2026-02-25  
**Status:** ✅ COMPLETE → morning briefing component SUPERSEDED by PLAN-013  
**What it did:** Established overnight workflow for all three agents (Raphael 00:30, Leonardo 01:30, Molty 03:00). MC discipline rules. Todoist queue routing. Morning briefing squad section.  
**Key output:** Overnight crons for all agents, MC task lifecycle (Backlog→In Progress→Under Review→Done).

---

## PLAN-005 — Fleet Update Manager
**File:** `plans/PLAN-005-molty-fleet-update-manager.md`  
**Created:** 2026-02-26  
**Status:** ✅ COMPLETE (2026-02-27)  
**What it did:** Molty owns OpenClaw version updates for the whole fleet. Release monitor cron, staged rollout script, health checks.  
**Key output:** `check-openclaw-releases.py`, `fleet-update.py`, cron `c0705ffd` (05:15 HKT daily).  
**Latest run:** Fleet updated to v2026.3.7 on Mar 9.

---

## PLAN-006 — Fleet Directive System
**File:** `plans/PLAN-006-fleet-directives.md`  
**Created:** 2026-02-27  
**Status:** ✅ COMPLETE (core live; secrets migration deferred)  
**What it did:** Standardized how Molty broadcasts config/behavior changes to Raphael and Leonardo. Breaking change automation for config patches.  
**Key output:** Fleet directive broadcast pattern, config patch automation.

---

## PLAN-007 — Overnight Workflow Overhaul (Model B) + Security Hardening
**Files:** `plans/PLAN-007-overnight-workflow-overhaul.md`, `plans/PLAN-007-SECURITY-HARDENING.md`  
**Created:** 2026-02-28 / 2026-03-02  
**Status:** ✅ COMPLETE  
**What it did (workflow):** Replaced memory_search with exec+cat pre-flight (faster, more reliable). All three agents patched to use cat+curl overnight.  
**What it did (security):** Remediated `dangerouslyDisableDeviceAuth`, `HostHeaderOriginFallback`, `hooks.defaultSessionKey`, multi-user sandboxing. Credentials dir fixed.

---

## PLAN-008 — Overnight Consolidation + Calendar Booking Logic
**Files:** `plans/PLAN-008-overnight-consolidation.md`, `plans/PLAN-008-CALENDAR-BOOKING-LOGIC.md`  
**Created:** 2026-03-01 / 2026-03-02  
**Status:** ✅ COMPLETE  
**What it did (consolidation):** Molty 03:00 now reads Raphael+Leonardo shared logs, posts ONE consolidated message to #squad-updates. Morning briefing reads consolidated log first.  
**What it did (calendar):** Standardized calendar booking rules — 3 calendars, SA token, Brinc busy blocks automatic, protected time slots.

---

## PLAN-009 — MC Phase 3 Feature Sprint
**File:** `plans/PLAN-009-phase3-features.md`  
**Created:** 2026-03-01  
**Status:** ✅ COMPLETE (all tier-1 + tier-2 features shipped; tier-3 mostly done)  
**What it did:** 20-feature sprint for Mission Control UI. Metrics dashboard, cost tracking, drag-and-drop kanban, weekly digest, Todoist sync, project views, mobile polish, analytics, stale agent detection, etc.  
**Key output:** Deployed to `tmnt-mission-control.vercel.app`. Most features live. [B2] Dark Mode + [C4] Splinter Den + [D1] Task Templates still parked.

---

## PLAN-010 — Memory System Overhaul
**File:** `plans/PLAN-010-memory-system-overhaul.md`  
**Created:** 2026-03-04  
**Status:** ✅ COMPLETE (all 7 phases executed 2026-03-04)  
**What it did:** Shrank session loading from 51KB→30.8KB. MEMORY.md from 16.7KB→1.9KB. SOUL.md 10.6KB→3KB. Created REGRESSIONS.md, mistake-tracker, monthly review cron.  
**Key output:** `REGRESSIONS.md`, `memory/refs/mistake-tracker.md`, cron for monthly reviews.

---

## PLAN-011 — Agent Management Improvements
**File:** `plans/PLAN-011-agent-management-improvements.md`  
**Created:** 2026-03-05  
**Status:** 🔄 IN PROGRESS (partial — some items complete, article in review)  
**What it did so far:** Last-updated headers on shared files, agent performance review framework, TMNT article drafted.  
**Remaining:** TMNT article in MC "review" status (needs Guillermo final approval + publish). Agent reviews cadence running monthly.

---

## PLAN-012 — Meta-Learning Loops Integration
**File:** `plans/PLAN-012-meta-learning-loops.md`  
**Created:** 2026-03-06  
**Status:** ✅ COMPLETE (implemented overnight 2026-03-06/07)  
**What it did:** REGRESSIONS.md as session-load rule. Prediction-outcome system in `memory/predictions/`. Friction log at `memory/friction-log.md`. Nightly synthesis. Active holds system.

---

## PLAN-013 — Morning Briefing v3.0 Condensed
**File:** `plans/PLAN-013-briefing-v3-condensed.md`  
**Created:** 2026-03-12  
**Status:** ✅ COMPLETE  
**What it did:** Compressed morning brief from 4-screen wall to ~1 screen. 6 sections: Focus / Blocked / Ready for Review / Today / Heads Up / Weather + OpenClaw status.  
**Key output:** `morning_briefing.py` `build_message()` rewritten. Commits `1c785f33`, `6f74558d`.

---

## PLAN-014 — April Full Squad Integration
**File:** `plans/PLAN-014-april-full-squad-integration.md`  
**Created:** 2026-03-12  
**Status:** 🔄 IN PROGRESS (core live; webhook latency issue outstanding)  
**What it did so far:** April deployed on Railway. Discord bot live. WhatsApp connected. Calendars (Shenanigans + personal) accessible. Heartbeat, overnight (02:00 HKT), Steph briefing (06:30 HKT) crons running. Overnight log writing confirmed.  
**Outstanding:** April webhook (`/hooks/agent`) hangs on delivery — queued via Agent-Link v2. April needs `message` tool patch (Discord send capability).

---

## PLAN-015 — Agent-Link v2 (Reliable Fleet Communication)
**File:** `plans/PLAN-015-agent-link-v2.md`  
**Created:** 2026-03-12  
**Status:** ✅ COMPLETE (approved + implemented 2026-03-12)  
**What it did:** Replaced direct webhook calls with queued delivery system. `tmnt-v1` envelope format for trusted fleet messages. Retry backoff (30s→2m→10m→1h). Health-aware routing via `/data/shared/health/`. Queue processor cron every 5 min.  
**Key output:** `/data/workspace/scripts/agent-link-worker.py`, cron `57a4956a`. Raphael ✅ delivering; Leonardo ⚠️ retry loop.

---

## Other Notable Documents
| File | Description |
|------|-------------|
| `plans/APRIL-DEPLOYMENT-PLAN-V2.md` | April's deployment playbook (v2 with lessons) |
| `plans/WHOOP-INTEGRATION-STATUS.md` | Whoop spec — parked until Mar 17 |
| `plans/ginesta-io-website-brief.md` | ginesta.io brief — in MC review |
| `plans/IDEAS-BACKLOG.md` | Unplanned ideas/opportunities |
| `plans/cerebro-crm-reminders-spec.md` | Cerebro CRM reminder spec |
| `plans/cerebro-future-paid-acquisition.md` | Cerebro growth ideas |

---

## What's Next (No Plan Yet)
- **Donatello deployment** — R&D/tinkerer agent, no plan created yet
- **Michelangelo deployment** — Mana Capital, no plan created yet
- **Waalaxy Chrome extension access** — blocked (PLAN-???)
- **Stripe Live migration** — needs Guillermo
- **Personal finance batch** — needs Guillermo input
- **Discrawl exploration** — research task queued

---

*Auto-generated by Molty overnight worker. Source: /data/workspace/plans/ + MC task history.*
*Next update: when a new plan is created or status changes significantly.*
