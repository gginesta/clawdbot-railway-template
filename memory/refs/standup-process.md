# Daily Standup — Process Reference
*Last updated: 2026-03-14 08:54 HKT — v3.0 webchat-native*

---

## Core Design (v3.0)

**Primary channel:** Webchat (where Guillermo works)  
**Backup channel:** Telegram (when mobile)  
**Notion:** Docs hub only — NO task sync, NO standup pages

```
Todoist     → Personal task capture
MC          → Squad/project management  
Webchat     → Daily review + delivery
Telegram    → Backup delivery when mobile
Notion      → Docs only (specs, briefs, plans)
```

---

## Core Rules

1. **Verbal "done" = immediate action** — close Todoist + MC in the same response
2. **Tomorrow's Focus = ONE item** — becomes a calendar event
3. **Calendar booking = post-review ONLY** — never at generation time
4. **Clarifying questions = always ask** — in the standup message itself
5. **Webchat first, Telegram backup** — respect Guillermo's preference

---

## Daily Flow

### Phase 0: Real-time (all day)
- G says done → Todoist closed + MC done. Same message. No exceptions.
- New Todoist task → rewrite title (specific + actionable + 🦎)
- Every heartbeat (2h): MC ↔ Todoist sync
- Context from chat → update immediately, not at standup

### Phase 1: Pre-standup prep (4:30–5:00 PM)

**What I check before sending:**

| Source | What | Why |
|--------|------|-----|
| ✅ Todoist | Tasks due today + overdue | Core task list |
| ✅ MC | In_progress tasks per agent | Squad status |
| ✅ ggv.molt inbox | Important emails | Flag for review |
| ❌ Notion task DB | **Not checked** | Dropped in v3.0 |
| 📄 Notion docs | Only if context needed | Specs, briefs |

Steps:
1. Fetch Todoist tasks → categorize (today/overdue)
2. Query MC → get squad in_progress tasks
3. Scan ggv.molt inbox → flag important emails
4. Form clarifying questions (genuine uncertainty only)
5. Write prep state file

### Phase 2: Standup delivery (5:00 PM)

**Send to webchat** (primary) or Telegram (backup if mobile):

```
📋 Daily Standup — {Day}, {Date}

TODAY'S TASKS:
1. ⬜ Task A (Todoist)
2. ⬜ Task B (Todoist)
3. ⬜ Review PR #76 (MC)

OVERDUE:
4. ⚠️ Task C (due Mar 12)

UPCOMING:
• Apr 30 — 💼 Personal finance batch (7 subtasks)
  → Life insurance, car estimate, health insurance, joint accounts, last will, credit cards

SQUAD:
• Raphael: [in_progress task or 'clear']
• Leonardo: [in_progress task or 'clear']

❓ QUESTIONS:
• [clarifying question if any]

TOMORROW'S FOCUS?
→ What's the ONE thing?

_Reply inline: "1 done, 2 drop" etc. Then state tomorrow's focus._
```

**Subtask display rule (REG-039):** Tasks with `parent_id` set MUST be grouped under their parent in the standup. Never show subtasks as standalone items. Show parent with count + summary line of subtasks. Example: `Apr 30 — 💼 Personal finance batch (7 subtasks)` followed by `→ Life insurance, car estimate, ...` on the next line.

### Phase 3: Guillermo replies inline

Example response:
> "1 done, 2 drop, 4 reschedule monday. Tomorrow focus: Cerebro outreach"

### Phase 4: Post-review processing

**What I do after your reply:**

| Action | System | Details |
|--------|--------|---------|
| 1. Parse decisions | — | done/drop/reschedule/delegate |
| 2. Close "done" items | Todoist + MC | Both systems, same response |
| 3. Reschedule items | Todoist | Update due date as specified |
| 4. Delegate to agents | Webhook | Full context to Raphael/Leonardo |
| 5. Book Tomorrow's Focus | Calendar | First free slot 9–13 HKT |
| 6. Confirm actions | Webchat | Summary of what was done |

**Calendar booking rules:**
- Check ALL 3 calendars for conflicts (Brinc, Personal, Shenanigans)
- Tomorrow's Focus → morning slot preferred (9–13 HKT)
- Non-Brinc bookings → also add "Busy [private]" on Brinc calendar
- Respect protected slots (school drop-off, pick-up, focus time)

### Phase 5: Overnight
- Raphael 00:30 → Leonardo 01:30 → Molty 03:00
- Each: pull MC assigned → work (90-min budget) → update MC → write log
- Log sections: ✅ Completed / 👀 Under Review / ❌ Failed / 🚧 Blocked / ⏭ Skipped

### Phase 6: Morning briefing (06:30)
**Format v3.0** (condensed):
1. 🎯 Focus — the ONE thing for today
2. 🚧 Blocked — max 3 items needing input
3. 👀 Ready for review — max 3 items
4. 📅 Today — condensed calendar
5. 🔜 Heads up — notable upcoming only
6. 🌤 Weather — single line
7. 🔧 OpenClaw — update status

---

## What Was Removed (v3.0)

- ❌ Notion standup page generation
- ❌ Notion task database sync
- ❌ Action column workflow (replaced by inline chat replies)
- ❌ Notion API calls in standup crons

---

## Calendar Rules (unchanged)

### Check ALL 3 calendars before booking:
- Brinc: `guillermo.ginesta@brinc.io`
- Personal: `guillermo.ginesta@gmail.com`
- Shenanigans: `vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com`

### Write rules:
- Brinc work → Brinc calendar
- Family → Shenanigans
- Personal/Mana → Personal calendar
- **Every non-Brinc booking → also add "Busy [private]" on Brinc**

### Protected slots:
- 08:00–08:30 Mo/We/Fr — School drop-off (LOCKED)
- 10:30–11:00 Mo/We/Fr — School pick-up
- 08:30–10:30 We/Fr — Focus time (no calls)

---

## Calendar Token Access

Use SA token pattern (NOT calendar-tokens-brinc.json):
```python
from google.oauth2 import service_account
creds = service_account.Credentials.from_service_account_file(
    "/data/workspace/credentials/google-service-account.json",
    scopes=["https://www.googleapis.com/auth/calendar"],
)
```

---

## Scripts & Crons

| Cron | Time | Script | Purpose |
|------|------|--------|---------|
| ad96575e | 4:30 PM | standup_prep.py | Triage, sync, prep state |
| bdb28765 | 5:00 PM | standup_webchat.py | Send review to webchat |
| 8b748f23 | 6:30 AM | morning_briefing.py | Morning summary |

---

## Overnight Logs

Location: `/data/shared/logs/overnight-<agent>-YYYY-MM-DD.md`
Consolidated: `/data/shared/logs/overnight-consolidated-YYYY-MM-DD.md`
