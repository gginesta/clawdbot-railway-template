# PLAN-014: April Full Squad Integration
**Created:** 2026-03-12  
**Status:** 🔄 IN PROGRESS  
**Author:** Molty 🦎  
**Requested by:** Guillermo (webchat, Mar 12 2026 08:00 HKT)

---

## Goal

Make April a full TMNT squad member — same tier as Raphael/Leonardo, no dilution.

---

## Checklist

### Step 1: Models ✅ DECIDED
- [x] Primary: `anthropic/claude-sonnet-4-6`
- [x] Fallback 1: `anthropic/claude-haiku-4-5`
- [x] Fallback 2: `openrouter/anthropic/claude-sonnet-4` (insurance if Anthropic down)

### Step 2: Cron Jobs ✅ DECIDED
- [ ] Heartbeat: every 2h
- [ ] Overnight: 02:00 HKT (before Molty's 03:00 consolidation)
- [ ] Morning briefing to Steph: 06:30 HKT via WhatsApp

**Overnight scope:**
- Check MC for assigned tasks
- Family calendar review
- Steph's tasks/reminders
- Research tasks → output as Google Doc, email link to Steph
- WhatsApp message triage

**Morning briefing to Steph (WhatsApp):**
- Today's family calendar
- Kids schedule / school
- Reminders Steph set
- Weather
- Research ready for review

### Step 3: Memory Setup 🔄 IN PROGRESS
- [ ] Verify MEMORY.md exists
- [ ] Verify memory/ folder structure
- [ ] Verify memory/refs/ exists
- [ ] Set up memory vault access (`/data/shared/memory-vault/`)
- [ ] Configure overnight log output: `/data/shared/logs/overnight-april-YYYY-MM-DD.md`

### Step 4: MC Integration 🔄 IN PROGRESS
- [ ] Verify mission-control skill is accessible
- [ ] April can read tasks assigned to her
- [ ] April can update task status
- [ ] April can create tasks for: herself, Guillermo, Molty (infra/updates)
- [ ] April understands MC workflow (documented in her AGENTS.md)

### Step 5: Config Update ✅ DONE
- [x] Apply model config via setup page (Guillermo pasted full config)
- [x] Model: Sonnet 4.6 primary, Haiku + OpenRouter fallbacks
- [x] April restarted automatically

### Step 6: Cron Jobs ✅ DONE (by April)
- [x] Heartbeat cron (2h) — created
- [x] Overnight work (02:00 HKT) — created
- [x] Steph briefing (06:30 HKT) — created

### Step 7: Memory/MC Setup ✅ DONE (by April)
- [x] Mission Control API added to TOOLS.md
- [x] HEARTBEAT.md updated with MC check
- [x] MEMORY.md documented cron schedule
- [x] /data/shared/logs/ ready for overnight logs

### Step 8: Testing ⏳ PENDING
- [ ] Test heartbeat (wait for next 2h cycle)
- [ ] Test overnight run (tonight 02:00)
- [ ] Test morning briefing to Steph (tomorrow 06:30)
- [ ] Verify overnight log appears in /data/shared/logs/

### Step 9: Molty Integration ⏳ PENDING
- [ ] Update morning_briefing.py to include April in squad report
- [ ] Update TOOLS.md with April's overnight schedule

---

## Decisions Log

| Time | Decision | By |
|------|----------|-----|
| 08:06 | Sonnet 4.6 primary, same tier as R/L | Guillermo |
| 08:12 | Add OpenRouter fallback for Anthropic redundancy | Guillermo |
| 08:12 | Overnight scope: family, Steph tasks, research → email+GDoc | Guillermo |
| 08:17 | Run at 02:00 HKT so Molty can consolidate at 03:00 | Guillermo |
| 08:17 | April sends Steph morning briefing via WhatsApp at 06:30 | Guillermo |
| 08:24 | April can assign tasks to Molty (infra/updates) | Guillermo |
| 08:27 | Scope: family/personal only. No Brinc/Cerebro access yet | Guillermo |

---

## Current Status

Working through Step 3 (Memory) and Step 4 (MC Integration) with Guillermo.
