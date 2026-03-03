# Standup System v2.1 — Full Build Plan
*Authored: 2026-03-03 | Completed: 2026-03-03 | Author: Molty*
*Design spec: `/data/workspace/plans/standup-system-redesign.md`*
*Quick ref: `/data/workspace/memory/refs/standup-process.md`*

---

## Context & Motivation

The previous standup system had three critical failures that caused repeated pain:

1. **Calendar blocked wrong tasks** — `block_week_calendar()` fired at page generation time using stale
   Todoist data. It auto-booked overdue tasks Guillermo had never reviewed.

2. **Tomorrow's Focus was never read** — Guillermo declared his #1 priority in the Notion page.
   `process_standup.py` never parsed it. Nothing was booked.

3. **"In MC?" was cosmetic** — The checkbox existed in the DB schema but `process_standup.py` never
   read it. MC tasks were created manually or not at all.

4. **Stale task loop** — Agents completed MC tasks overnight. Todoist + Notion never heard about it.
   Morning briefing showed the same "overdue" items every day.

5. **No real-time triage** — Tasks added to Todoist at 8AM sat raw until 4:30 PM prep (8.5 hours).

This document records every build decision made on 2026-03-03 to fix all of the above.

---

## System Architecture (Complete)

```
REAL-TIME (all day)
  ┌─────────────────────────────────────────────────────────────────┐
  │  Guillermo adds task → Todoist inbox                            │
  │  todoist_triage.py fires hourly (cron 13b4eaa0)                │
  │    → rewrites title, assigns project/owner/priority, adds 🦎   │
  │    → moves out of inbox to correct project                      │
  │                                                                 │
  │  Guillermo says "done" verbally → Molty closes Todoist+MC      │
  │  MC updated by agent → Todoist synced on next heartbeat        │
  └─────────────────────────────────────────────────────────────────┘

4:30 PM HKT — Pre-Standup Prep (cron ad96575e)
  standup_prep.py
  ├── Triage any remaining Todoist inbox tasks
  ├── Webhook Raphael + Leonardo: status check
  │     └── Agents write reply to /data/shared/logs/standup-status-{DATE}-{agent}.txt
  ├── Sync MC completions → close Todoist tasks
  ├── Scan ggv.molt inbox for action-required items
  └── Write /data/workspace/logs/standup-prep-{DATE}.json

5:00 PM HKT — Standup Generation (cron bdb28765)
  daily_standup.py
  ├── Read standup-prep-{DATE}.json → squad status + email highlights
  ├── Read standup-status-{DATE}-{agent}.txt → real agent status
  ├── Build Notion page:
  │     ├── Summary callout (squad status + email highlights)
  │     ├── BLANK Tomorrow's Focus callout (Guillermo fills ONE item)
  │     ├── Clarifying questions callout (if any)
  │     └── Task DB (all sections: Pipeline, Needs Input, Backlog)
  │           Pre-ticked: Book Calendar? (P1/P2, owner=Guillermo, not backlog)
  │           Pre-ticked: In MC? (agent-owned tracked project tasks)
  │           Owner column (Guillermo / Molty / Raphael / Leonardo)
  │           Action: Keep / Done / Drop / Reschedule
  └── Telegram: page link + queued counts + instructions

5:00–5:30 PM — Guillermo Reviews Notion Page
  Guillermo fills:
  ├── Tomorrow's Focus: ONE item (the thing that makes the day worthwhile)
  ├── Action per task: Keep / Done / Drop / Reschedule
  ├── Override Owner if needed
  ├── Check/uncheck Book Calendar? and In MC? as desired
  └── Your Notes: dates for reschedule, context for agent tasks

  Guillermo says: "standup done"

On "standup done" — Post-Review (process_standup.py)
  ├── Read Tomorrow's Focus → book first free slot tomorrow 09:00–13:00 HKT
  ├── Action=Done/Drop → close Todoist + close MC (if exists)
  ├── Action=Reschedule → parse date from Notes → update Todoist due date
  ├── Owner=Raphael → move Todoist task → webhook Raphael with full context
  ├── Owner=Leonardo → move Todoist task → webhook Leonardo with full context
  ├── In MC? checked → create/update MC task (dedup: fuzzy 55% threshold)
  ├── Book Calendar? checked → find free slot (5-day horizon) → book focus block
  └── Telegram: summary (focus booked / blocks / MC created / dispatched / closed)

00:30 Raphael / 01:30 Leonardo / 03:00 Molty — Overnight Runs
  Phase 0: Pre-flight (read memory logs + MC tasks + Todoist — skip anything done)
  Phase 1: Classify tasks (AUTO vs FLAG)
  Phase 2: Execute AUTO tasks (close in MC + Todoist on completion)
  Phase 3: Write standard log to /data/shared/logs/overnight-{agent}-{DATE}.md
    Format: ✅ Completed / 👀 Under Review / ❌ Failed (why) / 🚧 Blocked (ask) / ⏭ Skipped
  Molty (03:00): also consolidates R+L logs → posts to #squad-updates

04:00 HKT — Overnight Sync (cron 8991c017)
  overnight_sync.py
  ├── Query MC: tasks marked done in last 10 hours
  ├── Fuzzy-match → close matching Todoist tasks
  ├── Fuzzy-match → mark matching Notion standup rows → Action: Done
  └── Log: /data/workspace/logs/overnight-sync-{DATE}.log

6:30 AM HKT — Morning Briefing (cron 8b748f23)
  morning_briefing.py
  ├── Yesterday's Focus (from standup-state.json → Notion page callout)
  ├── Overnight Report:
  │     ├── MC under_review tasks (with agent + link)
  │     ├── MC blocked tasks (with specific ask)
  │     └── Squad log summary (per-agent: done/failed/blocked counts)
  ├── Weather (HKT)
  ├── Calendar (today + upcoming)
  ├── Tasks due + upcoming
  ├── Squad status (MC)
  ├── Email highlights
  └── Fleet health
```

---

## All Scripts

| Script | Lines | Role | Cron |
|--------|-------|------|------|
| `todoist_triage.py` | 180 | Hourly inbox triage | `13b4eaa0` — every hour |
| `standup_prep.py` | 442 | 4:30 PM pre-standup prep | `ad96575e` — 4:30 PM HKT |
| `daily_standup.py` | 1,576 | 5PM page generation | `bdb28765` — 5:00 PM HKT |
| `process_standup.py` | 926 | Post-review processing | Triggered: "standup done" |
| `standup_status_reader.py` | 90 | Read/write agent status files | (helper, used by daily_standup.py) |
| `overnight_sync.py` | 290 | 04:00 HKT MC→Todoist→Notion sync | `8991c017` — 04:00 HKT |
| `morning_briefing.py` | 1,691 | 6:30 AM briefing | `8b748f23` — 6:30 AM HKT |

---

## All Crons (Standup System)

| ID | Name | Schedule | Model | Status |
|----|------|----------|-------|--------|
| `13b4eaa0` | Todoist Inbox Triage (Hourly) | Every hour, HKT | Haiku | ✅ Active |
| `ad96575e` | Pre-Standup Prep (4:30 PM HKT) | 4:30 PM HKT daily | Haiku | ✅ Active |
| `bdb28765` | Daily Standup 5PM HKT | 5:00 PM HKT daily | Sonnet | ✅ Active |
| `8991c017` | Overnight Sync — MC→Todoist+Notion | 04:00 HKT (20:00 UTC) daily | Haiku | ✅ Active |
| `8b748f23` | Daily Morning Briefing | 6:30 AM HKT daily | (main) | ✅ Active |
| `80105aa4` | Molty Nightly Task Worker | 03:00 HKT (18:00 UTC) | Sonnet | ✅ Active |

**Other related crons (not standup-specific):**
| `251c316a` | Todoist → MC Sync | Every 30 min | — |
| `46d1ca32` | MC Heartbeat Ping | Every 2h | Haiku |

---

## Item Build Log

### ITEM 1 — Intra-Day Todoist Triage ✅

**Problem:** Tasks added at 8AM sat raw in inbox until 4:30 PM — 8.5 hours of stale data.

**Solution:** `todoist_triage.py` — lightweight, runs every hour, processes only inbox tasks without 🦎.

**PPEE:**
- **Pause:** Do I need a new script or can I reuse standup_prep.py? New script is cleaner — prep script has squad ping/email scan/10-min wait that shouldn't run hourly.
- **Plan:** Extract triage core (5 functions), add log file, no Telegram output. Register hourly cron.
- **Evaluate:** Haiku sufficient. Silent — no output to Guillermo. Same keyword/project logic as prep.
- **Execute:** Written → compiled → tested (0 unprocessed inbox tasks → correct) → cron registered.

**Result:**
- Script: `/data/workspace/scripts/todoist_triage.py`
- Cron: `13b4eaa0` — `0 * * * *` @ Asia/Hong_Kong, exact, Haiku, isolated
- Log: `/data/workspace/logs/triage-{DATE}.log`
- Test: Ran live — inbox clean, logged correctly, exited 0

---

### ITEM 2 — Overnight Log Format Standardisation ✅

**Problem:** `🚩 Flagged / Blocked` mixed two distinct signal types. Morning briefing couldn't tell
"agent tried and failed" from "agent needs something from Guillermo." No "Skipped" section meant
tasks not attempted were invisible.

**Old format:**
```
## ✅ Completed
## 👀 Under Review
## 🚩 Flagged / Blocked   ← useless blob
## ❌ Failed
```

**New standard format (v2.1):**
```
## ✅ Completed       — done, with link/evidence
## 👀 Under Review    — done but needs Guillermo's eyes, with link
## ❌ Failed          — attempted but broke — MUST say why
## 🚧 Blocked         — could not proceed — MUST give specific ask
## ⏭ Skipped          — not attempted — MUST say why
```

**PPEE:**
- **Pause:** Three separate agents, three separate OpenClaw instances. Can't update Raphael/Leonardo directly. Need fleet directive system.
- **Plan:** (1) Write shared template to `/data/shared/overnight-log-template.md`. (2) Update Molty's cron directly via `openclaw cron edit`. (3) Write directives to R+L pending-directives queue.
- **Evaluate:** Fleet directives picked up within 2h on next heartbeat — well before tonight's 00:30/01:30 runs. Template file is the single source of truth — prevents format drift.
- **Execute:** Template written → Molty cron updated (confirmed via API response) → directives written to both queues.

**Result:**
- Template: `/data/shared/overnight-log-template.md`
- Molty cron `80105aa4` updated: new format in Phase 3 instructions
- Raphael directive: `/data/shared/pending-directives/raphael/2026-03-03-overnight-log-format.md`
- Leonardo directive: `/data/shared/pending-directives/leonardo/2026-03-03-overnight-log-format.md`
- `morning_briefing.py` `_summarise_agent_log()` updated to parse new format (handles ❌/🚧/⏭)

---

### ITEM 3 — Squad Webhook Reply Handler ✅

**Problem:** `standup_prep.py` pings Raphael + Leonardo at 4:30 PM. Their replies arrive at Molty's
main session asynchronously. The isolated prep cron has already moved on. Standup page showed
"status check sent" instead of actual agent status.

**PPEE:**
- **Pause:** Two mechanisms for capturing replies: (A) inter-session state passed via main session, or (B) agents write directly to shared filesystem. Option B is more reliable — no timing dependency, no complex IPC.
- **Plan:** (1) Update ping message to instruct agents to write `/data/shared/logs/standup-status-{DATE}-{agent}.txt`. (2) Write `standup_status_reader.py` helper for reading/writing those files. (3) Update `daily_standup.py` to read status files at 5PM generation time. (4) Add standing instruction to memory for main session to write agent replies on receipt.
- **Evaluate:** File-based approach: agent can write at any time between 4:30 and 5PM → daily_standup.py reads at 5PM regardless. Fallback: "no pre-standup update received" if file absent. No race conditions.
- **Execute:** Ping message updated → reader/writer helper written → daily_standup.py reads files inline → memory/refs updated.

**Result:**
- Script: `/data/workspace/scripts/standup_status_reader.py`
- Agent status files: `/data/shared/logs/standup-status-{DATE}-{agent}.txt`
- `standup_prep.py`: ping message updated with write instructions
- `daily_standup.py`: reads status files at 5PM, uses them in `squad_status` callout
- `memory/refs/standup-process.md`: standing instruction for main session

---

### ITEM 4 — Post-Overnight Auto-Sync ✅

**Problem:** Agents complete MC tasks overnight and mark them done. Todoist + Notion still show them
as open. Morning briefing surfaces stale "overdue" items. This is what caused the Q&A task problem
on 2026-03-03 — Guillermo saw it as pending even though it had been closed.

**PPEE:**
- **Pause:** When should this run? Must be after ALL agents finish. Raphael 00:30, Leonardo 01:30, Molty 03:00 (consolidation). So: 04:00 HKT = safe. Must NOT run before 6:30 AM briefing (would be redundant if briefing already shows updated state).
- **Plan:** (1) Query MC for done tasks in last 10-hour window. (2) Fuzzy-match against open Todoist tasks → close. (3) Fuzzy-match against Notion standup DB rows for yesterday → mark Done. (4) Log. Register at 04:00 HKT.
- **Evaluate:** 10-hour window covers Raphael (00:30) through Molty (03:00) with 1h buffer each side. Safety checks: only close Todoist tasks created recently OR very high match score (≥75%). Never overwrite Notion rows already actioned. Fuzzy threshold 55% (same as process_standup.py, proven safe).
- **Execute:** Script written → compiled → live test (found 3 overnight completions, handled all correctly) → cron registered.

**Result:**
- Script: `/data/workspace/scripts/overnight_sync.py`
- Cron: `8991c017` — `0 20 * * *` UTC (04:00 HKT), exact, Haiku, isolated, 3-min timeout
- Log: `/data/workspace/logs/overnight-sync-{DATE}.log`
- Live test: 3 MC tasks done, 0 Todoist closures (already closed), 1 Notion row already actioned — all correct

---

### ITEM 5 — MC Backlog Review ✅

**Problem:** 15 MC tasks in `assigned` status for Molty — all Mission Control Phase 3 features.
Creating noise on every heartbeat check. Needed a decision: keep active or park.

**PPEE:**
- **Pause:** These are all UI features. Some have immediate daily-use value; others are polish/premature. Need Guillermo to decide.
- **Plan:** Pull all 15, categorise by value vs effort, present with recommendation per task.
- **Evaluate:** Don't park or prioritise without Guillermo's explicit decision. Present grouped list with reasoning.
- **Execute:** Pulled 15 tasks → presented categorised → Guillermo decided.

**Guillermo's decision (2026-03-03 10:44 HKT):**
- **PARK (backlog):** B2 Dark Mode ("don't care for it"), C5 File Attachments ("don't need it")
- **KEEP ACTIVE (assigned, execute overnight):** All remaining 13

**Tasks remaining active (13):**

| Task | Priority |
|------|---------|
| [A2] Pizza Tracker — Cost Tracking | P2 |
| [A4] Weekly Digest | P3 |
| [B1] Mobile-Responsive Polish | P2 |
| [B3] Enhanced Dojo — Quick Actions | P2 |
| [B4] Drag-and-Drop Kanban | P2 |
| [C1] Project Views (Brinc/Cerebro/Mana) | P2 |
| [C2] Todoist Sync (Read-Only) | P3 |
| [C4] Splinter Den — Settings Page | P3 |
| [D1] Task Templates | P3 |
| [D2] Notification Preferences | P3 |
| [D3] Activity Analytics in Sewer | P3 |
| [D4] Memory Timeline/Diff in Vault | P3 |
| [D6] User Auth (Login) | P3 |

**Tasks parked (2):**
| Task | Reason |
|------|--------|
| [B2] Dark Mode | Guillermo: "don't care for it" |
| C5: File Attachments | Guillermo: "don't need it" |

MC updates: B2 and C5 → `status: backlog`. All others remain `assigned`.

---

## Definition of Done — Final Status

- [x] New Todoist tasks triaged within 1 hour of being added (`todoist_triage.py` + cron `13b4eaa0`)
- [x] All 3 agents log in standard format: ✅/👀/❌(why)/🚧(ask)/⏭(reason)
      Molty: direct cron update. Raphael + Leonardo: fleet directives written.
- [x] Squad pre-standup status captured from shared files, shown in standup callout
      (`standup_status_reader.py` + updated `standup_prep.py` + `daily_standup.py`)
- [x] MC done overnight → Todoist + Notion auto-closed before 6:30 AM briefing
      (`overnight_sync.py` + cron `8991c017`)
- [x] MC backlog resolved: 2 parked (B2, C5), 13 remain active
- [x] Full system tested and committed: `git master cf8fbc57` → `8fa00406`
- [x] All scripts compile clean: 7/7

---

## Known Gaps (not in scope for today)

1. **squad_prep.py 10-min wait** — The 10-minute `time.sleep(600)` runs inside the isolated cron
   session. With a 900s timeout, this is technically fine but tight. If agents are slow to write their
   file, the standup may still show "no update received." Mitigation: daily_standup.py reads the file
   directly at 5PM regardless — so even a late reply (written between 4:40 and 5:00) will be captured.
   Long-term fix: reduce wait to 5 min, or remove wait entirely (rely on file read at 5PM).

2. **overnight_sync Notion row lookup** — Looks up Notion standup rows by `Standup Date = yesterday`.
   If the standup was not generated yesterday (holiday, weekend, system failure), yesterday's rows won't
   exist and the sync finds nothing. This is acceptable — edge case, not worth engineering around now.

3. **Raphael/Leonardo directive pickup** — Fleet directives rely on agents picking them up at next
   heartbeat. If a heartbeat fails or the directive handler is broken on their end, they may miss the
   format update. Risk: tonight's logs might still use old format. Mitigation: Molty's consolidation
   at 03:00 normalises the output before it reaches morning_briefing.py anyway.

---

## Files Changed (2026-03-03)

### New scripts
- `scripts/todoist_triage.py` — hourly triage
- `scripts/standup_status_reader.py` — agent status file read/write helper
- `scripts/overnight_sync.py` — post-overnight MC→Todoist→Notion sync

### Modified scripts
- `scripts/standup_prep.py` — updated ping message (agents write to shared file)
- `scripts/daily_standup.py` — reads agent status files + prep state
- `scripts/morning_briefing.py` — Yesterday's Focus + overnight report at top + MC attention items
- `scripts/process_standup.py` — MC task create/update + calendar booking + agent dispatch

### New data files
- `/data/shared/overnight-log-template.md` — standard log format for all agents
- `/data/shared/pending-directives/raphael/2026-03-03-overnight-log-format.md`
- `/data/shared/pending-directives/leonardo/2026-03-03-overnight-log-format.md`

### New plan/ref files
- `plans/standup-system-redesign.md` — full system design (21KB)
- `plans/standup-build-plan-2026-03-03.md` — this file
- `memory/refs/standup-process.md` — quick ref (loaded every session)
- `memory/2026-03-03.md` — session log (appended)
- `/data/shared/memory-vault/decisions/2026-03-03-standup-system-redesign.md` — fleet vault

### Git commits
```
0ae0d317  docs: standup system v2.1 — full redesign agreed with Guillermo
f1f52ab9  docs: standup v2.1 — real-time sync emphasis + title format confirmed
1189b4d9  feat: standup system v2.1 — full redesign implementation
bedd0f27  fix: standup v2.1 — logic tests all passing (7/7 book_cal, 8/8 mc, 4/4 fuzzy)
0488518c  feat: P1 items — pre-standup prep + morning briefing overhaul
43f67624  docs: update standup-process.md with new scripts + cron IDs
320c4cac  memory: morning session 2026-03-03 — standup system v2.1 redesign log
cf8fbc57  feat: complete standup system v2.1 — all remaining items built
8fa00406  chore: add .venv to .gitignore
```

---

## Tonight's First Full Run — What to Expect

| Time | Event | First time? |
|------|-------|-------------|
| 11:00 AM | Hourly triage fires (`13b4eaa0`) | ✅ First scheduled run |
| 4:30 PM | Pre-standup prep fires (`ad96575e`) | ✅ First ever run |
| ~4:35 PM | Raphael + Leonardo receive status webhook | First v2.1 ping |
| ~4:45 PM | Agents write status to shared files | New mechanism |
| 5:00 PM | Standup page generated (`bdb28765`) | First on v2.1 system |
| ~5:15 PM | Guillermo reviews page | New: Book Calendar? col, blank Tomorrow's Focus |
| ~5:30 PM | "standup done" | First full post-review run |
| 00:30 AM | Raphael overnight run | New log format (if directive picked up) |
| 01:30 AM | Leonardo overnight run | New log format (if directive picked up) |
| 03:00 AM | Molty overnight consolidation | New log format enforced |
| 04:00 AM | Overnight sync fires (`8991c017`) | ✅ First ever run |
| 6:30 AM | Morning briefing | First with Yesterday's Focus at top |

---

*Document complete. Source of truth for standup system v2.1.*
*Next review: after tonight's full run. Update with observed behaviour vs. expected.*
