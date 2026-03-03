# Standup System — Remaining Build Plan
*2026-03-03 | Target: complete before 5PM HKT | Author: Molty*

## What's Left

| # | Item | Type | Est. |
|---|------|------|------|
| 1 | Todoist intra-day triage cron | New script + cron | 30 min |
| 2 | Overnight log format — standardise all 3 agents | Prompt update + template | 45 min |
| 3 | Squad webhook reply handler — agents write status to shared file | Script + prompt update | 45 min |
| 4 | Post-overnight auto-sync — MC done → Todoist + Notion | New script + cron | 45 min |
| 5 | MC backlog review (15 tasks) | Discussion with Guillermo | 30 min |

**Total: ~3.5 hours. Deadline: 5PM. We have 6.5 hours. Comfortable.**

---

## ITEM 1 — Intra-Day Todoist Triage (Hourly Cron)

### Pause
Currently tasks Guillermo adds to Todoist at 8AM sit raw and unprocessed until 4:30 PM prep.
That's 8.5 hours of stale data. The "stay on top of work during the day" requirement means this needs to run continuously.

### Plan
1. Write `todoist_triage.py` — lightweight triage only. No squad ping, no email scan, no wait. Extract the triage core from standup_prep.py.
2. Logic: fetch Todoist inbox tasks → for each without 🦎 → rewrite title, assign project/owner/priority/time, add 🦎, move out of inbox
3. Logs to `/data/workspace/logs/triage-YYYY-MM-DD.log`
4. Register as hourly cron (Haiku, isolated, silent)

### Evaluate
- A separate script is cleaner than a flag on standup_prep.py — less risk of breakage
- Haiku is sufficient — pure Todoist API calls, no reasoning needed
- Runs silently — no Telegram output (would be noise)
- Already has all helper functions from standup_prep.py to copy

### Execute
→ Write script → compile check → test dry-run → register cron

---

## ITEM 2 — Overnight Log Format Standardisation (All 3 Agents)

### Pause
Current log format mixes "Flagged" and "Blocked" into one `🚩` section. Morning briefing can't distinguish:
- 🚧 Blocked (agent needs something specific from Guillermo to proceed)
- ❌ Failed (agent tried, something broke — need to know why)
- ⏭ Skipped (not attempted — need to know why)

All three agent prompts need updating. Molty's cron is updated directly. Raphael + Leonardo are on separate Railway instances — updated via fleet directives.

### Plan
**Step 1** — Write standard log template file at `/data/shared/overnight-log-template.md`

**Step 2** — Update Molty's cron prompt (`80105aa4`) to use new format:
- `## ✅ Completed` — what was done (with link/evidence)
- `## 👀 Under Review` — done but needs Guillermo's eyes (with link)
- `## ❌ Failed` — attempted, broke — **must include why**
- `## 🚧 Blocked` — could not start/finish — **must include specific ask for Guillermo**
- `## ⏭ Skipped` — not attempted (out of budget or context says already done)

**Step 3** — Write fleet directives for Raphael + Leonardo:
- File: `/data/shared/pending-directives/raphael/2026-03-03-overnight-log-format.md`
- File: `/data/shared/pending-directives/leonardo/2026-03-03-overnight-log-format.md`
- Directive: update their overnight cron prompt format to match the standard

### Evaluate
- Molty cron update is immediate via `openclaw cron update`
- Fleet directives picked up on next heartbeat (within 2h) — Raphael/Leonardo will have updated prompts before tonight's run at 00:30 / 01:30
- Template file gives all agents a single reference so format never drifts

### Execute
→ Write template → update Molty cron → write R+L directives → verify directive files exist

---

## ITEM 3 — Squad Webhook Reply Handler

### Pause
Current problem: standup_prep.py pings Raphael + Leonardo at 4:30, waits 10 min, then proceeds. But their replies come to Molty's MAIN session asynchronously — the isolated prep cron has no way to capture them. So the standup page shows "status check sent" not the actual status.

### Plan
**The solution: agents write their reply directly to a shared file instead of (or in addition to) messaging Molty.**

Step 1 — Update `standup_prep.py` ping message to include this instruction:
> "Please write your status update to `/data/shared/logs/standup-status-{DATE}-{agent}.txt` in addition to any reply. Format: COMPLETED: [list] | BLOCKED: [list] | IN_PROGRESS: [list]"

Step 2 — Update `daily_standup.py` to read those files at 5PM and incorporate into the standup summary callout (replaces the generic "status check sent" text).

Step 3 — Write `standup_status_reader.py` — simple helper that reads the agent status files and returns formatted text for the standup page.

Step 4 — Add a standing instruction to memory so Molty (main session) also writes agent replies to the status file when they arrive via webhook.

### Evaluate
- Writing to shared file is more reliable than real-time capture — the file persists regardless of timing
- daily_standup.py reads it at 5PM so timing of agent reply (anytime between 4:30 and 5PM) doesn't matter
- Doesn't require complex inter-session state management
- Fallback: if file doesn't exist → show "no pre-standup update received"

### Execute
→ Update ping message in standup_prep.py → update daily_standup.py reader → write status_reader helper → test

---

## ITEM 4 — Post-Overnight Auto-Sync (MC → Todoist → Notion)

### Pause
After Raphael (00:30), Leonardo (01:30), and Molty (03:00) run overnight and mark MC tasks done, Todoist and the Notion standup DB still show those tasks as open. Morning briefing then shows stale "overdue" items. This is the same class of problem that burned us with the Q&A task this morning.

### Plan
**Step 1** — Write `overnight_sync.py`:
- Runs at 04:00 HKT (after all agents, including Molty consolidation at 03:00)
- Query MC for all tasks with `status=done` updated in the last 6 hours (since ~22:00 previous day)
- For each: fuzzy-match against open Todoist tasks → close if matched
- For each: find matching Notion DB row (by title) → mark done
- Log: `/data/workspace/logs/overnight-sync-YYYY-MM-DD.log`

**Step 2** — Register as cron at 04:00 HKT (Haiku, isolated)

**Step 3** — Add overnight_sync summary to morning briefing:
- "Overnight sync: X Todoist tasks closed, Y Notion rows updated"

### Evaluate
- 04:00 HKT timing is correct — 1 hour after Molty finishes, before 6:30 morning briefing
- Fuzzy matching threshold 55% (same as process_standup.py) — proven to work
- Must NOT close tasks that were done BEFORE last standup (avoid closing backlog items agents happened to touch)
- Safety check: only close Todoist tasks that were opened/due in the last 7 days

### Execute
→ Write script → compile check → test against MC → register cron → morning briefing integration

---

## ITEM 5 — MC Backlog Review (15 Tasks)

### Pause
15 MC tasks are sitting in `status=assigned` for Molty — all Phase 3 features that were created but never prioritised. They create noise in heartbeat checks and need a decision.

### Plan
Pull all 15, categorise by value vs effort, present to Guillermo with a recommended action per task (park/prioritise/drop). Quick discussion, Guillermo decides, I update MC statuses immediately.

### Evaluate
This is a discussion item — no code needed. Can be done inline in this chat.

### Execute
→ Pull MC tasks → present categorised list → Guillermo decides → update MC statuses

---

## Build Sequence

```
10:30–11:00  ITEM 1  todoist_triage.py + hourly cron
11:00–11:45  ITEM 2  overnight log format (template + Molty cron + R+L directives)
11:45–12:30  ITEM 3  squad webhook reply handler
12:30–13:15  ITEM 4  overnight_sync.py + cron + morning briefing hook
13:15–13:45  ITEM 5  MC backlog review with Guillermo
13:45–14:00  Final verification + documentation
```

**Buffer: 3 hours before 5PM standup. Comfortable.**

---

## Definition of Done

The system is complete when:
- [ ] New Todoist tasks triaged within 1 hour of being added (not 8.5 hours)
- [ ] All 3 agents log in standard format: Completed / Under Review / Failed (why) / Blocked (ask) / Skipped
- [ ] Squad pre-standup status captured from shared files, shown in standup callout
- [ ] MC done overnight → Todoist + Notion auto-closed before 6:30 AM briefing
- [ ] MC backlog resolved (parked/prioritised/dropped)
- [ ] Full system runs tonight without manual intervention
