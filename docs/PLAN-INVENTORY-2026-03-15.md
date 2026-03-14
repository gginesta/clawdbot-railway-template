# PLAN Inventory — Molty Fleet

**Generated:** 2026-03-15 03:00 HKT  
**Author:** Molty 🦎  
**Purpose:** Single-source view of all PLANs with current status, completion date, and what's left.

---

## Summary

| Status | Count |
|--------|-------|
| ✅ Complete | 13 |
| 🔄 In Progress | 3 |
| 📋 Approved / Pending | 1 |
| ⚠️ Superseded | 1 |
| 🔍 Under Review | 1 |

**Current frontier:** PLAN-016 (Todoist↔MC Sync v2) — approved, implementation starting

---

## Full Plan List

### PLAN-001: Bidirectional Todoist ↔ Mission Control Sync
- **File:** `plans/PLAN-001-standup-sync-fix.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-02-24
- **What it did:** Established the first Todoist↔MC sync bridge. Molty owns syncing tasks. Foundation for all agent task coordination.

---

### PLAN-002: Autonomous Task Worker
- **File:** `plans/PLAN-002-task-worker.md`
- **Status:** ✅ LIVE (continuous)
- **Completed:** 2026-02-25 (first run)
- **What it did:** The nightly cron system — this very script. Molty runs at 03:00 HKT, Raphael 00:30, Leonardo 01:30. Results feed morning briefing.

---

### PLAN-003: Persistent Standup Database
- **File:** `plans/PLAN-003-persistent-standup-db.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-02-26
- **What it did:** Built the standup DB. Superseded in part by PLAN-013 (webchat-native standup).

---

### PLAN-004: Squad Overnight Workflow + Morning Briefing
- **Files:** `plans/PLAN-004-morning-briefing-squad.md` + `plans/PLAN-004-squad-overnight-workflow.md`
- **Status:** ✅ COMPLETE → partially SUPERSEDED by PLAN-013
- **Completed:** 2026-02-25 (overnight workflow live)
- **What it did:** Established the overnight workflow: each agent writes `/data/shared/logs/overnight-{agent}-{date}.md`, Molty consolidates at 03:00 and posts to #squad-updates, morning briefing reads consolidated log.

---

### PLAN-005: Molty Fleet Update Manager
- **File:** `plans/PLAN-005-molty-fleet-update-manager.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-02-27
- **What it did:** Molty owns all OpenClaw version upgrades. Template repo `gginesta/clawdbot-railway-template` → push to main → Railway auto-rebuilds all 4 agents. `gateway update.run` is READ-ONLY on Railway — do not use.

---

### PLAN-006: Fleet Directive System
- **File:** `plans/PLAN-006-fleet-directives.md`
- **Status:** ✅ COMPLETE (core system live; secrets migration deferred)
- **Completed:** 2026-02-27
- **What it did:** Established system for Molty to send directives to Raphael/Leonardo. Webhook-based. Secrets management improved.

---

### PLAN-007: Fleet Security Hardening + Overnight Workflow Overhaul
- **Files:** `plans/PLAN-007-SECURITY-HARDENING.md` + `plans/PLAN-007-overnight-workflow-overhaul.md`
- **Status:** ✅ COMPLETE
- **Completed:** ~2026-03-06
- **What it did:** Security hardening across all agents. Overnight workflow moved to Model B (isolated subagent with announce delivery). Two files tracked the security work and the workflow overhaul separately.

---

### PLAN-008: Smarter Calendar Booking Logic + Overnight Consolidation
- **Files:** `plans/PLAN-008-CALENDAR-BOOKING-LOGIC.md` + `plans/PLAN-008-overnight-consolidation.md`
- **Status:** ✅ COMPLETE
- **Completed:** ~2026-03-07
- **What it did:** Calendar booking improvements (SA token, protected slots, Brinc busy block). Overnight consolidation script to merge agent logs + post to Discord.

---

### PLAN-009: Phase 3 Feature Sprint (Mission Control)
- **File:** `plans/PLAN-009-phase3-features.md`
- **Status:** 🔄 IN PROGRESS (ongoing MC sprint)
- **Active tasks:** C4 Settings, D1 Templates, D2 Notifications, D4 Memory Timeline, D6 Auth, C5 Attachments
- **Completed tasks:** C1 Project Views, C2 Todoist Sync, C3 Memory Auto-Sync, D3 Activity Analytics, D5 Fleet Alerts, B1-B5 polish items, A1-A4 features
- **Next:** C4 Settings (next overnight MC sprint target)

---

### PLAN-010: Memory System Overhaul
- **File:** `plans/PLAN-010-memory-system-overhaul.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-03-10 (per MC task `jn75rqgkrgbj6zmbqw0afb84qs82804x` = done)
- **What it did:** Daily memory logs (`memory/YYYY-MM-DD.md`), long-term `MEMORY.md`, Shared Vault (`/data/shared/memory-vault/`), Syncthing distribution. MEMORY.md kept under 15KB.

---

### PLAN-011: Agent Management Improvements
- **File:** `plans/PLAN-011-agent-management-improvements.md`
- **Status:** 🔄 IN PROGRESS
- **Pending:** Documentation update (Todoist `6g8RFQXc45fVChHx`) — based on April deployment learnings
- **What it does:** Standardize agent deployment process, capture lessons from April's 2-day deployment.

---

### PLAN-012: Meta-Learning Loops Integration
- **File:** `plans/PLAN-012-meta-learning-loops.md`
- **Status:** ✅ COMPLETE (per MC task `jn7f8k0ccbnp8rq2rs77r0q4ed82d0r7` = done)
- **Completed:** ~2026-03-12
- **What it did:** REGRESSIONS.md (don't repeat mistakes), `memory/predictions/` (track predictions vs outcomes), `memory/friction-log.md` (log contradictions).

---

### PLAN-013: Morning Briefing v3.0 — Condensed Format
- **File:** `plans/PLAN-013-briefing-v3-condensed.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-03-13
- **What it did:** Condensed briefing format, webchat-native, dropped Notion task DB from standup workflow. Standup v3.0 live.

---

### PLAN-014: April Full Squad Integration
- **File:** `plans/PLAN-014-april-full-squad-integration.md`
- **Status:** 🔄 IN PROGRESS
- **Completed phases:** Railway deploy, Discord binding, WhatsApp channel, Calendar access, Agent-Link v2 integration
- **Pending:** Full autonomy testing, Steph-specific workflow setup, voice/call capabilities (researched)
- **Notes:** tools.allow bug fixed 2026-03-14. WhatsApp debounce added.

---

### PLAN-015: Agent-Link v2 — Reliable Fleet Communication
- **Files:** `plans/PLAN-015-agent-link-v2.md` + `plans/PLAN-015-DEBUG.md`
- **Status:** ✅ COMPLETE
- **Completed:** 2026-03-12
- **What it did:** TMNT-v1 envelope protocol, webhook delivery with retry queue, health tracking (`/data/shared/health/<agent>.json`), all 4 agents (Molty, Raphael, Leonardo, April) connected.
- **Key file:** `/data/shared/scripts/agent-link-worker.py`

---

### PLAN-016: Todoist↔MC Sync v2
- **File:** `plans/PLAN-016-todoist-mc-sync-v2.md`
- **Status:** 📋 APPROVED — Implementation starting this week
- **Goal:** Keep Todoist as Guillermo's single dashboard. Fleet tasks stay in Todoist with `[Agent]` prefix, mirrored to MC for agent execution. Bi-directional completion sync.
- **Phases:**
  - Phase 1-2 (prefix parsing + standup triage): **Sun night → Mon**
  - Phase 3-4 (completion sync + test): **Mon night → Tue**
  - Phase 5 (first real Monday standup test): **Mon 5PM HKT**

---

## Numbering Notes

- PLAN-007 and PLAN-008 each have two files (one for MC sprint, one for standalone feature). Both count as the same PLAN number.
- PLAN-004 has two files (morning briefing + overnight workflow) — same number, different scope docs.
- No gaps in numbering 001–016.

---

## What's Been Archived / Superseded

| Plan | Superseded By |
|------|---------------|
| PLAN-001 (basic sync) | PLAN-016 (Sync v2) |
| PLAN-004 morning briefing | PLAN-013 (briefing v3.0) |
| PLAN-003 standup DB | Standup v3.0 (webchat-native, Notion dropped) |

---

## Open Questions / Next PLANs

1. **PLAN-017?** — ginesta.io website (brief ready: `plans/ginesta-io-website-brief.md`, blocked on content checklist)
2. **PLAN-018?** — Donatello deployment (research/tinkerer agent)
3. **PLAN-019?** — Michelangelo deployment (Mana Capital agent)
4. **WHOOP integration** — spec at `scripts/WHOOP-INTEGRATION-SPEC.md`, blocked on API keys

---

*Compiled by Molty 🦎 | 2026-03-15 03:00 HKT | Source: /data/workspace/plans/*
