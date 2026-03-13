# Notification Formats — Standing Rules

*How to format notifications to Guillermo. These are permanent standards.*

---

## Email Check

**Format:**
```
📬 [TIME] Check

⚠️ [Subject] — [What they need from Guillermo]
📧 [Subject] — [What's being asked]

Nothing else.
```

**Rules:**
- One line per email, max 5 items
- Say WHAT they need — not "replied" or "2 in thread"
- Read full email content to extract the actual ask
- ⚠️ = needs response today
- 📧 = FYI or can wait
- Silent if nothing important (no "all clear" messages)
- Skip spam/newsletters/promos/Google security alerts
- If >5 items: "+N more, none urgent"

**Cron:** `25bd223c-78d0-428f-b0d3-f8dd5f959d02` (6AM, 9AM, 3PM HKT)

---

## Morning Briefing

**Format:** (from PLAN-013 v3.0)
```
Good morning — [Day] [Date]

🚧 Blocked (need you):
• [Agent]: [Task truncated]

👀 Ready for review:
• [Agent]: [Task truncated]

📅 Today: [events on one line]

🔜 [Notable upcoming]

🌤 [Weather one line]

🔧 OpenClaw: [status]
```

**Rules:**
- ~1 screen max
- Max 3 blocked, max 3 review items
- Calendar on one line
- Weather one line
- No overnight report details, no full task lists

**Cron:** `8b748f23-91d0-425d-9e4b-e7246e46ce8c` (6:30 AM HKT)

---

## General Principles

1. **Actionable over informative** — tell him what to DO, not what happened
2. **One line per item** — no paragraphs
3. **Silent if nothing** — don't send "all clear" messages
4. **Max 5 items** — summarize overflow as "+N more"
5. **Respect his time** — he's busy, every word must earn its place

---

*Last updated: 2026-03-13 by Molty*
