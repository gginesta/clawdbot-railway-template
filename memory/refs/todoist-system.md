## 📋 Todoist Productivity System (Configured 2026-02-05)

### Projects
| ID | Name | Emoji |
|----|------|-------|
| 2300781375 | Inbox | 📥 (capture bucket) |
| 2300781387 | Personal | 🙂 |
| 2300781386 | Brinc | 🔴 |
| 2329980736 | Wedding | 💍 (shared) |
| 2330246839 | Mana Capital | 🟠 |
| 2366746501 | Molty's Den | 🦎 |

### Inbox Processing Flow
1. Guillermo dumps raw tasks/ideas into Inbox throughout the day
2. I process hourly (hybrid mode) — rewrite, estimate, categorize, prioritize
3. Daily standup at **5PM HKT** — review processed items, confirm, move to projects with due dates

### Daily Standup (4-step process — NON-NEGOTIABLE)
1. **Process Todoist inbox** — rewrite titles, add descriptions, assign projects, set priorities, estimate time
2. **Create Notion standup page** — approved template: callout instruction block + inline "Task Review" child_database (columns: Task, Section, Project, Owner, Priority, Due Date, Time Est., Action, Molty's Notes, Your Comments) + Tomorrow's Priority heading + Blockers heading
3. **After Guillermo reviews ("standup done")** — process decisions in Todoist + **create Google Calendar time blocks** for next 1-2 days based on priorities, energy schedule, and life commitments
4. **Send Telegram summary** with Notion link

- **Time:** 5:00 PM HKT (09:00 UTC)
- **Cron:** `bdb28765-f508-4271-a04d-9408d39f49fd`
- **Channel:** Webchat first → Telegram fallback after 15min
- **If skipped:** Guillermo says "skip standup" → move to next morning
- **Template ref:** Feb 7 page `30039dd6-9afd-8137-b854-e9701a0b7648`, DB schema at `30039dd6-9afd-81fc-9994-f2dabec49f83`

### Brinc Task Coordination with Raphael
- Brinc tasks I process stay in **Todoist** (Guillermo's command view)
- I relay Brinc tasks to Raphael via **Discord** (`#brinc-private` or `#brinc-general`), NOT webhooks
- Raphael creates **mirror tasks in his Notion** for tracking execution
- **Completion flow:** Raphael marks done in Notion → I review/approve → tick off in Todoist
- ⚠️ **Future pattern:** Mirror this coordination model for ALL team leads when deployed (Leonardo, Donatello, Michelangelo, April) — Todoist = Guillermo's view, agent's Notion = execution tracking, Discord = communication channel

### Priority = Eisenhower Matrix
- P1 = Urgent + Important → DO NOW
- P2 = Important, not urgent → SCHEDULE
- P3 = Urgent, not important → DELEGATE
- P4 = Neither → DEFER
- ⚠️ Todoist API inverted: `priority=4` = P1 display!

---
