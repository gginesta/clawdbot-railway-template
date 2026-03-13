# Notification Formats — Standing Rules

*How to format notifications to Guillermo. These are permanent standards.*

---

## Morning Briefing (v3.3 — Mar 13 2026)

**Format:**
```
☀️ **Fri 13 Mar** · 16-21°C

🚧 **Blocked**
→ Molty: Research pending your review
→ Raphael: Needs live proposal deck from you

👀 **Review**
→ TMNT Agent Management article
→ Ginesta.io website brief
→ Cerebro CRM Pipelines Phase B

📅 **Today**
→ Workout 07:00
→ GBA-HK: G&M Sync 10:00
→ Arlene / DVC x Brinc 10:30

🔜 **Coming up**
→ Sat: Max 2nd birthday 16:00

🔧 Update available: v2026.3.12
   Reply /update to install
```

**Rules:**
- **Bold section headers** — `**Blocked**`, `**Review**`, `**Today**`
- **Full descriptions** — no truncation, human-readable summaries
- **Blocked items** — say what's needed from Guillermo (e.g. "Needs live proposal deck")
- **Review items** — clean readable titles, not task IDs
- **Calendar** — list format, one event per line, full names
- **Weather** — temp range + rain outlook if coming
- **Coming up** — only truly notable (birthdays, travel, appointments)
- **OpenClaw** — show if update available + install hint

**Noise filtered out:**
- Mayleen, Mie, helpers, domestic
- School drop-off, pickup
- Focus time, deep work, desk work, admin blocks
- Busy blocks, lunch breaks

**Cron:** `8b748f23-91d0-425d-9e4b-e7246e46ce8c` (6:30 AM HKT)

---

## Email Check (v2 — Mar 13 2026)

**Format:**
```
📬 3 PM Check

⚠️ FY23-24 — Raeniel needs your sign-off on Q4 numbers by EOD
📧 Outstanding Issues — Jane asking for vendor list for pitch deck

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

## OpenClaw Update Summary

**When:** Fleet update check detects new version (cron `c0705ffd-9c7f-4f90-839b-7f3a9d660371` at 21:15 HKT)

**Format:**
```
**OpenClaw 2026.X.Y — Top Features for Us:**

| Feature | What It Does | How We Use It |
|---------|--------------|---------------|
| **🎛️ Feature Name** | One-line description | Practical application for TMNT |
| **⚡ Feature 2** | What it does | How it helps us |
| **🛡️ Feature 3** | Description | Our use case |

**Most Relevant for Us:**
1. **Feature A** — why it matters to our workflow
2. **Feature B** — specific benefit
3. **Feature C** — how it fixes a pain point

**To Update:**
`/update`
```

**Rules:**
- Fetch release notes from GitHub (`https://github.com/openclaw/openclaw/releases/tag/vX.Y.Z`)
- Table format: Feature | What It Does | How We Use It
- Focus on TMNT-relevant features (skip irrelevant providers like BlueBubbles)
- Call out fixes for issues we've hit (e.g., cron duplication)
- End with clear action: `/update`
- Use emoji prefixes for visual scanning

**Source:** Fetch tweet from @openclaw + GitHub release notes

---

## General Principles

1. **Readable over compact** — full sentences beat truncated gibberish
2. **Actionable** — tell him what to DO, not just what exists
3. **Bold headers** — visual hierarchy matters on mobile
4. **Filter noise** — don't show recurring/known events
5. **Silent if nothing** — don't send "all clear" messages
6. **Tables for comparisons** — easier to scan than paragraphs

---

*Last updated: 2026-03-13 by Molty*
