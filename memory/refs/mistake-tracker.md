# Mistake Tracker

Track recurring mistakes, their fixes, and whether fixes actually work.

| Date | Mistake | Type | Fix Applied | Fix Location | Recurrences |
|------|---------|------|-------------|--------------|-------------|
| 2026-03-04 | No Brinc busy block on passport appt | Procedural | cal_create unconditional | process_standup.py | 0 |
| 2026-03-04 | Used expired OAuth token instead of SA token | Retrieval | Token deprecated + SA pattern documented | memory/refs/standup-process.md | 0 |
| 2026-03-04 | GET /api/task (singular) for MC query | Retrieval | HEARTBEAT.md fixed | HEARTBEAT.md + MEMORY.md #116 | 0 |
| 2026-03-04 | Claimed "documented last night" unverified | Overclaim | Hard gate in AGENTS.md | AGENTS.md | 0 |
| 2026-03-04 | 8+ redeployments without diagnosis (Raphael) | Judgment | PPEE reinforced | MEMORY.md #115 | 0 |
| 2026-03-04 | para_curation.py processes 0 files weekly | System | PARA = archival only | PLAN-010 | 0 |
| 2026-03-04 | MEMORY.md 117 lessons, unreadable | System | Cull to <4KB | PLAN-010 Phase 5 | 0 |

---

## Rules

1. Every mistake Guillermo calls out → logged here in same session
2. Recurrence count > 0 → current fix insufficient → escalate to code
3. Review weekly (Friday standup)
4. Monthly: any recurrence > 0 gets mandatory code-level fix

---

*Last updated: 2026-03-04*
