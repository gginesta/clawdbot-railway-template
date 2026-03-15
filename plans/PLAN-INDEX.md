# PLAN Index — Audit 2026-03-15

## ✅ COMPLETE (Archive-Ready)

| ID | Name | Completed | Notes |
|----|------|-----------|-------|
| 001 | Todoist↔MC Sync | 2026-02-24 | Working, superseded by 016 |
| 003 | Persistent Standup Database | 2026-02-26 | Working |
| 004 | Morning Briefing Squad Status | 2026-02-24 | Superseded by 013 |
| 005 | Fleet Update Manager | 2026-02-27 | Working |
| 006 | Fleet Directive System | 2026-02-27 | Working |
| 007 | Security Hardening | 2026-03-02 | Working |
| 008 | Calendar Booking Logic | 2026-03-02 | Working (now in cal.py) |
| 013 | Briefing v3.0 Condensed | 2026-03-12 | Working |
| 015 | Agent-Link v2 | 2026-03-12 | Working |

## 🔄 IN PROGRESS

| ID | Name | Status | Next Action | Owner |
|----|------|--------|-------------|-------|
| 011 | Agent Performance Reviews | 60% | Design review framework + add "Last updated" headers | Molty |
| 014 | April Full Squad Integration | 80% | WhatsApp morning briefing, Steph USER.md interview | Molty/April |
| 016 | Todoist↔MC Sync v2 | 0% | Implement Phase 1-2 | Molty |

## ⏸️ AWAITING DECISION

| ID | Name | Status | Blocker |
|----|------|--------|---------|
| 010 | Memory System Overhaul | Awaiting Approval | Needs Guillermo's review of approach |

## ❌ ABANDONED / MERGED

| ID | Name | Reason |
|----|------|--------|
| 002 | Autonomous Task Worker | Concept merged into overnight workflows (004b, 007b) |
| 004b | Squad Overnight Workflow | Not a plan — moved to AGENTS.md as operational doc |
| 007b | Overnight Workflow Overhaul | Merged into ongoing ops, no discrete deliverable |
| 008b | Overnight Consolidation | Merged into daily ops, no discrete deliverable |
| 009 | Phase 3 Feature Sprint | One-night sprint complete, remaining items tracked in MC |
| 012 | Meta-Learning Loops | Partially implemented (REGRESSIONS.md, predictions). Remaining loops need Guillermo decision. |
| 015-DEBUG | Agent-Link Debug | Fixed, delete this file |

## 🗑️ FILES TO DELETE

- `PLAN-004-squad-overnight-workflow.md` → content moved to AGENTS.md
- `PLAN-007-overnight-workflow-overhaul.md` → ops doc, not plan
- `PLAN-008-overnight-consolidation.md` → ops doc, not plan  
- `PLAN-015-DEBUG.md` → debugging notes, fixed
- `PLAN-002-task-worker.md` → concept absorbed

## 📋 REMAINING WORK (MC Tasks Needed)

### From PLAN-011 (Agent Performance Reviews)
1. Design review framework document
2. Create review template
3. Add "Last updated by" headers to all shared files

### From PLAN-014 (April Integration)
1. WhatsApp morning briefing cron for Steph
2. Steph USER.md interview

### From PLAN-016 (Todoist↔MC Sync v2)
1. Phase 1: Detect fleet tasks in Todoist
2. Phase 2: Mirror to MC with assignee
3. Phase 3: Completion sync
4. Phase 4: Standup reconciliation

### From PLAN-010 (Memory Overhaul) — IF APPROVED
1. Split MEMORY.md into domain files
2. Action-triggered retrieval rules
3. Prediction logging system

### From PLAN-012 (Meta-Learning) — IF APPROVED
1. Friction log implementation
2. Prediction → outcome tracking
3. 90-day regression archival
