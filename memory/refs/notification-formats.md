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

**Format:** (v3.1 — Mar 13 2026)
```
Good morning — Fri 13 Mar

🚧 Blocked (need you):
• Molty: Research: Chrome extension + remote…
• Raphael: A8 (BLOCKED Fri): Use live proposal…

👀 Ready for review:
• Leonardo: CRM Pipelines Phase B — AI Layer…

📅 Event… 19:00 · Workout 07:00 · School… 08:00

🔜 Tue: Event 19:00, Sat: Birthday 16:00

🌤 16-21°C, 15% rain

🔧 OpenClaw: Update available: v2026.3.12 ⬆️
```

**Rules:**
- ~1 screen max (~15 lines)
- Max 3 blocked, max 3 review items
- Calendar: max 3 events, smart truncation at word boundary
- Weather: temp range + rain % (one line)
- OpenClaw: ACTUALLY checks version (runs `openclaw update status`)
- Smart truncation: cuts at word boundary, not mid-word

**Fixes (Mar 13 2026):**
- Weather was "unavailable" — HKO 9-day doesn't include today, now uses tomorrow as proxy
- OpenClaw was lying "Up to date" — now runs actual version check
- Truncation was ugly ("Pikachu co") — now smart word-boundary truncation

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
