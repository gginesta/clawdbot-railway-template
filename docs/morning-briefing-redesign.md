# Morning Briefing Redesign — Options for Guillermo

*Drafted: 2026-03-30 | Author: Molty*  
*Context: Guillermo said current format "just doesn't work" (2026-03-21). Full redesign needed on his return from London.*

---

## Why the Current Version Fails

Based on analysis of the spec and known failure modes:

1. **Token fragility** — Uses `calendar-tokens-brinc.json` (OAuth, expires) + `gmail-tokens.json`. When tokens expire headlessly, the whole briefing silently breaks.
2. **Too much data, wrong priority** — Tasks due + upcoming + email highlights + weather = information overload at 7:30am on mobile. Nothing stands out.
3. **Telegram at 7:30am** — May arrive when Guillermo is in school drop-off (MO/WE/FR). Gets buried.
4. **No SA calendar access** — The script bypasses the working SA token and uses fragile OAuth for calendar.
5. **No squad status** — Doesn't reflect what the fleet did overnight (increasingly relevant).

---

## Option A: "The 60-Second Scan" (Minimal + Reliable)

**Philosophy:** Less is more. One screen. Actionable only.

**Delivery:** Telegram, 07:45 HKT (after drop-off window)

```
📅 Mon Mar 30 — HKT

CALENDAR (3 events today)
09:00 Brinc Weekly
12:30 Lunch w/ Marco
16:00 Mana call

TASKS (2 urgent)
• [P1] Send Brinc investor update (30m)
• [P2] Bank of China follow up (30m, overdue Mar 19)

SQUAD overnight
• Raphael: ✅ 5 LinkedIn outreach sequences drafted → needs your LinkedIn to send
• Leonardo: no log
• Molty: ✅ Patagonia Phase 3+4 complete, Notion updated

WEATHER: 22–28°C, rain 30%
```

**Pros:** Fits one phone screen. Squad update included. SA token for calendar = reliable.  
**Cons:** No email. No upcoming week. Very lean.

---

## Option B: "The 3-Section Brief" (Structured + Scannable)

**Philosophy:** Three fixed sections — only what changes daily.

**Delivery:** Telegram, 07:45 HKT weekdays; 09:00 weekends

```
Good morning — Mon Mar 30

— TODAY —
09:00 Brinc Weekly (Brinc)
12:30 Lunch w/ Marco (Personal)
No P1 tasks due · 2 P2 overdue (Bank of China +1)
🌤 22–28°C · Rain 30%

— THIS WEEK —
Tue  14:00  Cerebro demo prep
Wed  school pick-up 10:30
Fri  Memo's swimming class

— OVERNIGHT —
Raphael drafted BRI-53 LinkedIn sequences → review + send
Molty updated Patagonia property list to 49 props (Phase 4 done)
Leonardo: no activity
```

**Pros:** Fixed 3-section structure is predictable. Overnight log = useful context for Guillermo. Weekday/weekend modes.  
**Cons:** Still needs email integration for full picture.

---

## Option C: "The Priority Stack" (One-Line Tasks, Email Top-of-Mind)

**Philosophy:** Email-first (it's what Guillermo actually uses), then calendar, then brief squad update.

**Delivery:** Telegram, 07:45 HKT

```
Guillermo · Mon Mar 30

📧 Email: 14 unread
  ⚡ Jane Ng — URGENT: Q1 budget sign-off
  ⚡ Tim — Confirm Tokyo travel dates

📅 Calendar
  09:00 Brinc Weekly · 12:30 Lunch Marco · 16:00 Mana

🎯 Top 3 to-do
  1. [P1] Brinc investor update
  2. [P2] Bank of China follow up (9 days overdue ⚠️)
  3. [P2] Review Raphael's LinkedIn sequences

🌙 Overnight: Raphael ✅ BRI-53 done · Molty ✅ Patagonia Notion updated

🌤 22–28°C
```

**Pros:** Email leads (where urgent items live). Integrates squad overnight naturally. Very compact.  
**Cons:** Email needs Gmail SA token (currently not set up — only OAuth). Requires re-wiring auth.

---

## Technical Changes Needed (All Options)

| Fix | Effort | Impact |
|-----|--------|--------|
| Switch calendar to SA token (no expiry) | Low | Eliminates calendar failures |
| Squad overnight log integration | Low | Already exists in `/data/shared/logs/` |
| Email via gws CLI (reliable auth) | Medium | Fixes email reliability |
| Deliver at 07:45 vs 07:30 | Trivial | Avoids drop-off overlap |
| Add "overdue age" to tasks | Low | More context for old tasks |

---

## Recommendation

**Option B** is the safest redesign:
- Predictable 3-section structure Guillermo can skim in 10 seconds
- Overnight squad log is the new value-add (this is now useful data)
- No email dependency = no auth headaches for now
- Easy to add email back in a v2 once gws CLI is wired

**Minimum viable implementation:** ~1 hour to rebuild the script with SA token + overnight log integration.

---

## Next Step (for Guillermo to decide)

1. Which format? A / B / C (or mix)
2. Should email be included? (requires gws CLI auth setup ~30min)
3. Delivery time OK at 07:45? Or prefer earlier/later?
4. Want squad overnight included, or too noisy?

*File: /data/workspace/docs/morning-briefing-redesign.md*
