# Productivity Framework Audit
*Compiled by Molty 🦎 | 2026-03-13 | Todoist task `6g8RCV7RMVrh6qhx`*

---

## What We Currently Run

```
CAPTURE        → Todoist (Guillermo adds tasks throughout day)
SQUAD WORK     → Mission Control (agent tasks, projects, overnight)
DAILY REVIEW   → Notion standup DB page (generated at 5PM)
DELIVERY       → Telegram (morning brief + standup notification)
STORAGE        → Notion cover page (docs, reference)
```

**The full loop:**
1. Guillermo captures in Todoist all day
2. 4:30PM — Molty pre-standup prep (sync Todoist → Notion DB)
3. 5:00PM — Cron generates Notion page, sends Telegram notification
4. Guillermo reviews Notion page, fills Action column, adds Tomorrow's Focus
5. Guillermo says "standup done"
6. Molty processes Action column, syncs MC, schedules Tomorrow's Focus
7. 06:30AM — Morning briefing (Telegram) with overnight squad results

---

## How Each Layer Is Actually Used

### Todoist ✅ Working well
- Guillermo captures freely throughout the day
- Molty can read tasks in real time
- Quick closure ("done" → closed immediately)
- Good for atomic personal actions
- **Friction:** Naming quality varies; tasks need rewriting to be actionable

### Mission Control ✅ Working well
- All agent work tracked here
- Overnight results surfaced in morning briefing
- War Room kanban for visual status
- Pizza Tracker for velocity + costs
- **Friction:** Occasionally out of sync with Todoist (PLAN-001 mitigates this)

### Notion Standup DB ⚠️ Questionable value
- Generated daily at 5PM as a structured review page
- Guillermo uses the Action column (Keep/Done/Drop/Reschedule) to give feedback
- Tomorrow's Focus lives here
- **Problems:**
  - One more system to load, another sync to maintain
  - Column order bugs (REG-026 added because of standup cross-check failures)
  - Guillermo rarely links to or references Notion standup pages outside the review session
  - The standup page is a *means* (structured review) not an *end* (the work itself)
  - April's overnight log shows she ignores Notion entirely — works fine
  - Requires Notion API call + page creation overhead in the standup cron

### Telegram ✅ Working well
- Preferred delivery channel
- Morning briefing v3.0 (condensed) is working
- Immediate response from Guillermo

---

## The Core Question

> **Does the Notion task database add value that Todoist + MC don't already provide?**

### What Notion DB provides that others don't:
1. **Action column** — structured way for Guillermo to say Keep/Done/Drop/Reschedule on multiple tasks at once
2. **Tomorrow's Focus** — the single "most important thing" slot
3. **Visual table** — all tasks in one view with columns (owner, priority, calendar flag, MC flag)
4. **Historical standup archive** — searchable record of past reviews

### What we could do without Notion:
1. **Action column** → Guillermo just tells Molty verbally (already happens anyway — "done" in chat)
2. **Tomorrow's Focus** → Ask via Telegram at standup time, Molty books it
3. **Visual table** → Todoist's project view + MC War Room covers this
4. **Historical archive** → MC has full task history; Todoist archive exists

---

## My Assessment

**The Notion standup DB is the weakest link in the chain.**

Evidence:
- The standup DB exists mainly because we *thought* Guillermo would review a structured table. In practice, he uses chat more than Notion pages.
- Every Notion sync is a failure point: API rate limits, token expiry, column order bugs, page creation failures — all real incidents.
- We've written 3+ versions of the standup code to handle Notion edge cases. That complexity exists to support one review step.
- The "Action column" workflow requires Guillermo to switch from Telegram → browser → Notion → back. This friction is real.

**The Notion cover page has value as a docs hub. The task DB does not.**

---

## Recommendation: Drop Notion Task DB

### Proposed simplified stack:
```
Todoist     → Personal task capture (unchanged)
MC          → Squad/project management (unchanged)
Telegram    → All delivery + quick review interactions (enhanced)
Notion      → Docs, specs, plans only (cover page stays; task DB dropped)
```

### What changes in the standup flow:
- **5PM standup** becomes Telegram-native:
  - Molty sends formatted message: tasks due today, completions, outstanding, clarifying questions
  - Guillermo replies inline ("drop", "done", "tomorrow focus: X")
  - Molty processes inline — no Notion page to generate or sync
- **Tomorrow's Focus** — Guillermo states it in chat; Molty books as calendar event
- **Historical record** — MC activity feed + Molty daily logs (already happening)

### What we keep from Notion:
- Cover page as landing page / docs hub
- Any specs/plans stored there (ginesta.io brief, TMNT article)
- We do NOT sync tasks to or from Notion

---

## Implementation Effort

| Item | Effort | Owner |
|------|--------|-------|
| Strip Notion sync from `daily_standup.py` | 1h | Molty |
| Rewrite standup delivery to pure Telegram | 2h | Molty |
| Update `morning_briefing.py` (no Notion fallback) | 30min | Molty |
| Archive existing Notion standup DB pages | 15min | Molty |
| Update AGENTS.md + standup-process.md | 30min | Molty |

**Total: ~4h, one overnight run**

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Lose historical standup pages | Archive DB before dropping sync; MC history preserved |
| Guillermo misses the structured table view | MC War Room covers visual task management |
| Tomorrow's Focus gets lost | Molty confirms it in morning briefing + books calendar event |

---

## Verdict

**Simplify to: Todoist + MC + Telegram. Drop Notion as a task step.**

Keep Notion cover page as a docs hub. Remove all task sync, standup page generation, and Notion API calls from the automation stack.

Estimated benefit: 20% less standup failure surface area, faster delivery, simpler codebase, one fewer system Guillermo needs to check.

**Needs Guillermo approval before implementation.** Flagging as a decision point.

---

*For discussion at next standup or morning briefing.*
