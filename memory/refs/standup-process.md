# Daily Standup & Productivity System — Process Reference
*Source of truth: /data/workspace/plans/standup-system-redesign.md*
*Last updated: 2026-03-03 08:48 HKT — v2.1 approved by Guillermo*

---

## Core Rules (never forget these)

1. **Verbal "done" = immediate action** — close Todoist + Notion + MC in the same response. No "I'll note that."
2. **Tomorrow's Focus = ONE item** — the single thing that makes tomorrow worthwhile. Left blank by the script. Guillermo writes it. It becomes a calendar event.
3. **Calendar booking = post-review ONLY** — never at generation time
4. **Calendar bias = BLOCK** — better to book than miss. Guillermo can move it.
5. **Clarifying questions = always ask** — preferred over silence + mistakes. Both Telegram + Notion.
6. **Design changes = update the plan doc immediately** — /data/workspace/plans/standup-system-redesign.md

---

## Agreed Settings (2026-03-03)

| Setting | Value |
|---------|-------|
| Tomorrow's Focus max items | 1 |
| Calendar horizon | 5 working days |
| Squad pre-standup check | Webhook at 4:30, wait 10 min, proceed regardless |
| Task title edit format | Silent rewrite (specific + actionable = the signal) |
| Clarifying questions | Both Telegram + Notion |
| MC backlog (15 tasks) | Review together with Guillermo |

---

## The Six Phases

### Phase 0: Real-time (all day) — THE FOUNDATION
- G says done → Todoist closed + Notion row updated + MC done. Same message. No exceptions.
- New Todoist task → rewrite title (ONCE, first intake only): "Reply to Raeniel re: accounts — 30min 🦎" (specific + actionable + time + 🦎 at end)
- Every heartbeat (2h): check MC for new/completed tasks → sync to Todoist. The two must never diverge >2h.
- MC task completed by squad lead → close Todoist immediately
- Todoist task closed → close MC immediately
- Context from chat → update Todoist + MC immediately, not at standup

### Phase 1: Pre-standup prep (4:30 PM, silent)
1. Fetch new Todoist tasks → process each (title, priority, owner, project, time, calendar flag, MC flag)
2. Webhook Raphael + Leonardo → "what did you complete today not in MC?" → wait 10 min
3. MC check: cross-reference done tasks with Todoist, sync both ways
4. ggv.molt inbox scan → flag relevant items
5. Sync Notion DB: mark completed, add new, update statuses
6. Form clarifying questions (genuine uncertainty only)

### Phase 2: Standup generation (5:00 PM)
Notion page structure:
- Summary callout (situation, squad status from pre-standup check)
- Tomorrow's Focus (blank yellow callout — Guillermo fills in ONE item)
- Email highlights (if any)
- Clarifying questions callout (if any — answer before reviewing table)
- Task DB (persistent, filtered to active + new)
- Blockers section (MC blocked tasks from agents)

Telegram: "Standup ready + link + questions if any"

### Phase 3: Guillermo reviews
- Answer questions → fill Tomorrow's Focus → review table → say "standup done"
- Should NOT need to re-enter anything discussed during the day

### Phase 4: Post-review processing (on "standup done")
1. Tomorrow's Focus → calendar event tomorrow, first free slot 9–13 HKT
2. Action=Done/Drop → close Todoist + MC + Notion
3. Action=Reschedule → update Todoist due date (parse from Your Notes)
4. Owner=Raphael/Leonardo → move Todoist + webhook with full context
5. In MC? ticked → create/update MC task (deduplicate first — fuzzy ≥55%)
6. Book Calendar? ticked → book focus block (check both cals, 5-day horizon)
7. Telegram summary: booked / MC updated / dispatched / closed / open questions

### Phase 5: Overnight
- Raphael 00:30 → Leonardo 01:30 → Molty 03:00
- Each: pull MC assigned → work (90-min budget) → update MC → write log
- Log sections: ✅ Completed / 👀 Under Review / ❌ Failed (why) / 🚧 Blocked (ask) / ⏭ Skipped
- Molty 03:00: read R+L logs, check ggv.molt, update MC, consolidate, post #squad-updates

### Phase 6: Morning briefing (06:30)
Order: Yesterday's Focus (did it happen?) → Overnight Report → Calendar → Squad → P1/P2 tasks → Email → Fleet

---

## Notion DB Columns (in order)
Task | Your Notes | Action (Keep/Done/Drop/Reschedule) | Owner (G/Molty/Raphael/Leonardo) | Book Calendar? | In MC? | Due Date | Priority | Time Est. | Project | Section | Molty's Notes | Standup Date

## Pre-tick logic
- Book Calendar? YES: P1/P2 + owner=G + not already in cal. Default to YES when uncertain.
- Book Calendar? NO: agent-owned, P3/P4, already in cal
- In MC? YES: agent-owned + multi-step + project=Brinc/Cerebro/Mana/Fleet + not already in MC open

## Calendar settings
- Brinc tasks → Brinc cal | Everything else → Personal cal
- Horizon: 5 working days | Hours: 9–18 HKT (morning preferred)
- Format: 🎯 [P1] Task name | 15-min popup | Duration from Time Est.
- Check BOTH cals for conflicts

## MC task creation
- Deduplicate: fuzzy ≥55% match first
- Required: title, project, priority, assignees, createdBy="molty", status="assigned"
- Description = Guillermo's Notes + Molty's Notes
- Update if exists + open. Skip if exists + done. Create only if genuinely new.

## Overnight log location
/data/shared/logs/overnight-<agent>-YYYY-MM-DD.md
Consolidated: /data/shared/logs/overnight-consolidated-YYYY-MM-DD.md
