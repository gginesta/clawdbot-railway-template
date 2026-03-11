# PLAN-013: Morning Briefing v3.0 — Condensed Format
**Created:** 2026-03-12  
**Status:** ✅ COMPLETE  
**Author:** Molty 🦎  
**Requested by:** Guillermo (webchat, Mar 12 2026 07:11 HKT)

---

## Problem

The morning briefing had grown to 4 screens on Telegram mobile. Sections included:
- Good morning + school day notice
- Today's Focus
- Overnight Report (under review, blocked, squad summary)
- Active Plans
- Weather (with 3-day outlook)
- Today's Calendar (full list)
- Tasks Due (grouped by project)
- Squad status (P0s, blockers, agent tasks, MC queue)
- Next 5 days (full list)
- Email highlights
- Notion comments
- OpenClaw Update

**Guillermo's feedback:** "It's not really usable right now"

---

## Solution

Condensed to ~1 screen with only actionable items:

```
Good morning — Thu 12 Mar

🎯 Focus: Reply to Raeniel. Book this in my calendar. Its Urgent.

🚧 Blocked (need you):
• Molty: Research: Chrome extension + remote gateway setup 
• Raphael: A8 (BLOCKED Fri): Use live proposal deck as master

👀 Ready for review:
• Molty: Write TMNT Agent Management article
• Leonardo: CRM Pipelines Phase B — AI Layer

📅 Today: Workout 07:00 · Economist 08:00 · Anita 10:30 · Lunch 12:00

🔜 Fri: School Drop-off 08:00, Arlene/DVC 09:00

🌤 17-24°C, 15% rain

🔧 OpenClaw: Up to date ✅
```

---

## What's Kept

| Section | Why |
|---------|-----|
| 🎯 Focus | The ONE thing for today |
| 🚧 Blocked | Needs Guillermo's input — max 3 |
| 👀 Ready for review | Work done, awaiting eyes — max 3 |
| 📅 Today | Condensed to one line — up to 5 events |
| 🔜 Heads up | Only if notable (school, family, P1 deadline) — max 2 items |
| 🌤 Weather | Single line (temp + rain %) |
| 🔧 OpenClaw | Always shown per Guillermo's request |

---

## What's Removed

| Section | Why Removed |
|---------|-------------|
| School day notice | Implicit from calendar if notable |
| Overnight Report details | Squad logs → available on demand |
| Active Plans | Noise — check MC if needed |
| Weather 3-day outlook | Overkill for daily briefing |
| Tasks Due (full list) | Todoist is the source — briefing is for blockers |
| Squad status (full) | Noise — under review + blocked is enough |
| Next 5 days (full list) | Replaced with notable-only "Heads up" line |
| Email highlights | Molty triages — don't surface anxiety |
| Notion comments | Edge case — rarely actionable |

---

## Notable Upcoming Logic

The `🔜 Heads up` line only appears if there's something notable in the next 5 days:

**Notable keywords:**
- school, drop-off, pickup, pick-up
- meeting, call, sync
- birthday, anniversary, dinner, lunch with
- flight, travel, trip
- deadline, due, submit

**Always notable:**
- Family calendar events
- P1 tasks due

**Format:** `🔜 Fri: School Drop-off 08:00, Tue: Dinner with parents`

If nothing notable → line is omitted entirely.

---

## Files Changed

1. `/data/workspace/scripts/morning_briefing.py`
   - Rewrote `build_message()` function (~270 lines → ~110 lines)
   - Added `_get_notable_upcoming()` helper function

2. `/data/workspace/plans/PLAN-004-morning-briefing-squad.md`
   - Updated to reference v3.0 format

3. `/data/workspace/memory/refs/standup-process.md`
   - Updated "Morning Briefing Order" section

---

## Testing

Ran `morning_briefing.py` manually — output is now ~10 lines vs ~50+ lines before.

---

## Commit

*(pending)*
