# PLAN Registry — Master Index
**Last Updated:** 2026-03-17 00:50 HKT (Molty)  
**Scope:** All PLAN-XXX files across `/plans/` and `/plans/archive/`

---

## Summary

| Status | Count | List |
|--------|-------|------|
| ✅ COMPLETE | 9 | 001, 003, 004, 005, 006, 007, 008, 011, 013 |
| 🔄 IN PROGRESS | 5 | 009, 014, 015, 016, 017 |
| ⏳ BLOCKED/DEFERRED | 2 | 010, 012 |
| 📚 ARCHIVED | 3 | PLAN-002, PLAN-004 (squad), PLAN-007, PLAN-008 |

---

## Active Plans (2026)

### ✅ PLAN-001: Bidirectional Todoist ↔ MC Sync (v1)
- **Created:** 2026-02-24
- **Status:** ✅ COMPLETE
- **Implemented:** 2026-02-24
- **Owner:** Molty
- **Summary:** Initial sync framework. Script-based, one-way polling. Works but limited.
- **Note:** Superseded by PLAN-016 (v2, full bidirectional)
- **File:** `/plans/PLAN-001-standup-sync-fix.md`

### ✅ PLAN-003: Persistent Standup Database
- **Created:** 2026-02-24
- **Status:** ✅ COMPLETE (2026-02-26)
- **Owner:** Molty
- **Summary:** Mission Control as task database. Live and running.
- **File:** `/plans/PLAN-003-persistent-standup-db.md`

### ✅ PLAN-004: Morning Briefing Integration
- **Created:** 2026-02-24
- **Status:** ✅ COMPLETE → **SUPERSEDED by PLAN-013**
- **Owner:** Molty
- **Summary:** Early briefing system. Replaced by v3.0 (condensed format).
- **File:** `/plans/PLAN-004-morning-briefing-squad.md`

### ✅ PLAN-005: Fleet Update Manager
- **Created:** 2026-02-26
- **Status:** ✅ COMPLETE (2026-02-27)
- **Owner:** Molty
- **Summary:** Molty owns fleet OpenClaw version updates. Manual review required.
- **File:** `/plans/PLAN-005-molty-fleet-update-manager.md`

### ✅ PLAN-006: Fleet Directive System
- **Created:** 2026-02-27
- **Status:** ✅ COMPLETE (core live, secrets migration deferred)
- **Owner:** Molty
- **Summary:** cron job system for sending tasks to agents. SEC-008 in use.
- **File:** `/plans/PLAN-006-fleet-directives.md`

### ✅ PLAN-007: Fleet Security Hardening
- **Created:** 2026-03-02
- **Status:** ✅ COMPLETE
- **Owner:** Molty
- **Summary:** Tailscale, REG-025 (Docker user), REG-027 (allowBots). All hardened.
- **File:** `/plans/PLAN-007-SECURITY-HARDENING.md`

### ✅ PLAN-008: Smart Calendar Booking Logic
- **Created:** 2026-03-02
- **Status:** ✅ COMPLETE
- **Owner:** Molty
- **Summary:** Brinc busy block automation. REG-006 enforced in code.
- **File:** `/plans/PLAN-008-CALENDAR-BOOKING-LOGIC.md`

### 🔄 PLAN-009: Phase 3 Features
- **Created:** 2026-03-01
- **Status:** 🔄 IN PROGRESS
- **Owner:** Molty
- **Target:** Tonight (03:00 HKT)
- **Summary:** MC UI improvements (C4 Splinter Den, D1 Templates, D2 Notifs, D6 Auth, etc.)
- **File:** `/plans/PLAN-009-phase3-features.md`

### ⏳ PLAN-010: Memory System Overhaul
- **Created:** 2026-03-04
- **Status:** ⏳ AWAITING GUILLERMO APPROVAL
- **Owner:** Molty
- **Summary:** MEMORY.md size management, lesson curation, meta-learning loops.
- **File:** `/plans/PLAN-010-memory-system-overhaul.md`

### 🔄 PLAN-011: Agent Performance Reviews
- **Created:** 2026-03-05
- **Status:** ✅ COMPLETE (2026-03-16)
- **Owner:** Molty
- **Summary:** Monthly review framework + template. First reviews due April 7.
- **File:** `/plans/PLAN-011-agent-management-improvements.md`

### ⏳ PLAN-012: Meta-Learning Loops
- **Created:** 2026-03-06
- **Status:** ⏳ PLANNING
- **Owner:** Molty
- **Summary:** Predictions + outcomes logging. Tied to REG audits.
- **File:** `/plans/PLAN-012-meta-learning-loops.md`

### ✅ PLAN-013: Morning Briefing v3.0
- **Created:** 2026-03-12
- **Status:** ✅ COMPLETE
- **Owner:** Molty
- **Summary:** Condensed format. Live since 2026-03-12.
- **File:** `/plans/PLAN-013-briefing-v3-condensed.md`

### 🔄 PLAN-014: April Full Squad Integration
- **Created:** 2026-03-12
- **Status:** 🔄 IN PROGRESS
- **Owner:** Molty
- **Summary:** April deployment to all comms (Discord ✅, WhatsApp ✅, Calendar ✅, agent-link ✅). Config fixed 2026-03-16.
- **File:** `/plans/PLAN-014-april-full-squad-integration.md`
- **Status:** Ready for next phase (messaging integration)

### 🔄 PLAN-015: Agent-Link v2 (Reliable Fleet Communication)
- **Created:** 2026-03-12
- **Status:** ✅ APPROVED | 🔄 Phase 2 deploying tonight (Tue)
- **Owner:** Molty
- **Summary:** Fleet messaging with queue + retry + health-aware routing. Core live. Phase 2 (HMAC signing) deploying Tue night.
- **File:** `/plans/PLAN-015-agent-link-v2.md`
- **MC Task:** jn7empmf7mavh1tjad5j39aswn833f0d
- **Progress:**
  - Phase 1: ✅ DONE (tmnt-v1 envelope + queue)
  - Phase 2: 🔄 TONIGHT (HMAC integration + health fix + queue cron + e2e test)
  - Phase 3: After 48h — strict mode (reject unsigned messages)

### 🔄 PLAN-016: Todoist↔MC Sync v2 (Full Bidirectional)
- **Created:** 2026-03-14
- **Status:** 🔄 IN PROGRESS (overdue)
- **Owner:** Molty
- **Summary:** Replace PLAN-001 with full sync (both directions, completion sync, live updates).
- **File:** `/plans/PLAN-016-todoist-mc-sync-v2.md`
- **Note:** Implementation slipped Sat/Sun. Needed ASAP (MC data is stale).

### 🔄 PLAN-017: Behavior Enforcement Architecture
- **Created:** 2026-03-16 → 2026-03-17
- **Status:** ✅ APPROVED (2026-03-17) | 🔄 IN PROGRESS
- **Owner:** Molty
- **Summary:** Replace documentation-only rules with code enforcement. 3-layer approach: automatic (80%), retrieval (15%), human escalation (5%).
- **File:** `/plans/PLAN-017-behavior-enforcement.md`
- **Schedule:**
  - Tue night: PLAN-015 Phase 2 (HMAC fleet deploy)
  - Wed night: 017a (stale escalation), 017b (close notifications), 017c (Discord validation)
  - Thu-Fri: PLAN-016 (Todoist↔MC sync)
  - Sat: Full test + close
- **MC Tasks:** jn7c22vy..., jn73rprd..., jn7c18qa..., jn780mb8..., jn711ngj...

---

## Archived Plans (Legacy)

### 📚 PLAN-002: Autonomous Task Worker
- **Status:** Approved, archived
- **Reason:** Core logic evolved into PLAN-003/006/009

### 📚 PLAN-004: Squad Overnight Workflow
- **Status:** Archived (superseded by PLAN-006)
- **Reason:** Directives system replaces manual scheduling

### 📚 PLAN-007: Overnight Workflow Overhaul
- **Status:** Archived
- **Reason:** Integrated into PLAN-006 (fleet directives)

### 📚 PLAN-008: Overnight Consolidation
- **Status:** Archived
- **Reason:** Consolidation logic now in `overnight_sync.py`

---

## Critical Dependencies (Execution Order)

### Tier 1: Required Before Others
- ✅ PLAN-001 (sync foundation)
- ✅ PLAN-003 (MC database)
- ✅ PLAN-006 (cron directives)

### Tier 2: Required for Agent Work
- ✅ PLAN-007 (security)
- ✅ PLAN-014 (April deployment)
- ⏳ PLAN-015 Phase 1 (webhooks)

### Tier 3: Quality + Optimization
- 🔄 PLAN-009 (UI improvements)
- 🔄 PLAN-016 (sync v2)
- 📝 PLAN-017 (enforcement strategy)

### Tier 4: Meta + Learning
- ⏳ PLAN-010 (memory overhaul)
- ⏳ PLAN-012 (meta-loops)

---

## Delivery Timeline

| Plan | Started | Done | Days | Owner | Next |
|------|---------|------|------|-------|------|
| 001 | Feb 24 | Feb 24 | 0 | Molty | v2 (PLAN-016) |
| 003 | Feb 24 | Feb 26 | 2 | Molty | ✅ |
| 005 | Feb 26 | Feb 27 | 1 | Molty | ✅ |
| 006 | Feb 27 | Feb 27 | 0 | Molty | ✅ |
| 007 | Mar 02 | Mar 02 | 0 | Molty | ✅ |
| 008 | Mar 02 | Mar 02 | 0 | Molty | ✅ |
| 013 | Mar 12 | Mar 12 | 0 | Molty | v4 (TBD) |
| 014 | Mar 12 | Mar 16 | 4 | Molty | Config fix done, integration next |
| 015 | Mar 12 | Mar 16 | 4 | Molty | Phase 2 done, deploy next |
| 011 | Mar 05 | Mar 16 | 11 | Molty | ✅ |

---

## Status by Urgency

### 🔴 URGENT (Blocking Work)
- **PLAN-016:** Todoist sync incomplete. MC data stale. Caused cleanup work Mar 16.
  - **Blocker:** Estimation: 4-6 hours
  - **Recommended:** Start this week

### 🟡 HIGH (In Progress)
- **PLAN-009:** Phase 3 features. Design-complete, implementation pending.
- **PLAN-015 Phase 2:** HMAC integration — code done, needs rollout.
- **PLAN-014:** April config fixed, ready for next phase.

### 🟢 MEDIUM (Planned)
- **PLAN-010:** Memory overhaul. Needs Guillermo direction.
- **PLAN-012:** Meta-learning. Depends on PLAN-010.
- **PLAN-017:** Output for Guillermo review (delivered this session).

---

## Metrics

**Completion Rate:**
- 8 / 17 active = 47% done
- 4 / 17 in progress = 24% active
- 3 / 17 deferred = 18% blocked
- 1 / 17 draft = 6% new

**Velocity:** ~1.5 plans/week (Feb 24 – Mar 17 = 22 days, 8 done)

**Risk:** PLAN-016 overdue by 3 days. PLAN-015 Phase 2 needs integration.

---

## Approvals & Status

| Plan | Approved By | Approval Date | Status |
|------|------------|---------------|--------|
| 001-008, 013 | Guillermo | Various (Feb-Mar 2) | ✅ LIVE |
| 011 | Guillermo | Mar 16 afternoon | ✅ LIVE |
| 014, 015, 016 | Guillermo | Mar 14-16 | 🔄 IN PROGRESS |
| 009 | Design-complete | — | Pending start |
| 010, 012 | — | — | ⏳ AWAITING DIRECTION |
| 017 | — | Under review | 📝 DRAFT |

---

*Registry compiled during overnight session (2026-03-17 00:50 HKT).*  
*Next audit: 2026-04-01 (monthly review).*
