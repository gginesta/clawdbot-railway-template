# Inbox Processing Protocol

## Trigger
- Heartbeat check (hybrid mode — process hourly, move at standup)
- Manual: "process inbox"

## Processing Steps

For each Inbox item:

1. **Read the raw input** — could be a snippet, idea, or full task
2. **Classify**: Task vs Idea
   - Tasks get processed into actionable items
   - Ideas get `@idea` label + note for standup discussion
3. **Rewrite title** — Clear, actionable, starts with a verb
   - Bad: "website thing"
   - Good: "Review and update Brinc website copy for Q1 launch"
4. **Expand description** — Add context, acceptance criteria, links if obvious
5. **Estimate duration** — 15m increments (15m, 30m, 1h, 2h, 4h, 8h)
6. **Assign project** — Based on content:
   - Personal 🙂 (id: 2300781387)
   - Brinc 🔴 (id: 2300781386)
   - Wedding 💍 (id: 2329980736)
   - Mana Capital 🟠 (id: 2330246839)
   - Molty's Den 🦎 (id: 2366746501)
7. **Set priority** — Eisenhower matrix:
   - P1 (urgent + important) — DO NOW
   - P2 (important, not urgent) — SCHEDULE
   - P3 (urgent, not important) — DELEGATE
   - P4 (neither) — DEFER/DELETE
8. **Leave in Inbox** — Don't move yet! Standup review moves items.

## At Standup
- Present all processed items
- Guillermo confirms/adjusts priority, project, due date
- Move confirmed items to their projects
- Set due dates based on discussion

## Brinc Task Coordination (Raphael)
- Relay Brinc tasks to Raphael via **Discord** (#brinc-private / #brinc-general)
- Raphael creates **mirror tasks in Notion** for execution tracking
- Completion flow: Raphael done in Notion → Molty reviews → tick off in Todoist
- **Future:** Same pattern for ALL team leads (Todoist → Discord → agent's Notion → review → Todoist ✅)

## Model for Processing
- Use `qwen` (cheap/fast) for simple rewrites
- Escalate to sonnet for ambiguous items needing interpretation

## Todoist API Notes
- Labels: create `@idea`, `@processed`, `@standup-review` as needed
- Duration field: `duration` and `duration_unit` in task creation
- Priority: 1=p4(lowest), 2=p3, 3=p2, 4=p1(highest) — ⚠️ INVERTED from display!
