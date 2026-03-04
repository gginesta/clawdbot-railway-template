# Code-Enforced Rules

Rules that are now structurally enforced in code. These do NOT need to be remembered — they are automatic.

| Rule | Script/Location | Enforcement | MEMORY.md Lesson | Status |
|------|-----------------|-------------|------------------|--------|
| Brinc busy block auto-added | process_standup.py:cal_create | unconditional, no flag | #103 | ✅ Enforced 2026-03-04 |
| SA token for calendar (not OAuth) | token file deprecated | file renamed .DEPRECATED | #117 | ✅ Enforced 2026-03-04 |
| MC API GET = /api/tasks (plural) | HEARTBEAT.md | documented, needs wrapper | #116 | ⚠️ Documented only |
| venv Python for cron scripts | all scripts | shebang line | #48 | ✅ Enforced |
| Browser lock file cleanup | startup.sh | automatic on deploy | #50 | ✅ Enforced (f0f39aa) |

---

## Pending Code Enforcement

These rules SHOULD be in code but are currently just documented:

| Rule | Current State | Proposed Fix |
|------|--------------|--------------|
| MC API GET uses plural | Documented in MEMORY.md #116 | Add wrapper function in scripts that validates endpoint |
| Cron agentId not empty | Documented in #97 | Add validation in cron creation |
| Notion property name validation | Documented in #105 | Add response body logging on non-200 |

---

*Last updated: 2026-03-04*
