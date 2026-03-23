# TODO.md - Molty's Task Tracker

*Last updated: 2026-03-17 18:36 HKT*

---

## 🔴 URGENT: Cerebro Deploy Debugging (Tue 18:36 HKT)
**Status:** Blocking Leonardo | **Issue:** Server starts but Railway kills container after schedulers init

| Task | Detail |
|------|--------|
| Monitor Leonardo's fix | Waiting on enrichment queue / violation decay scheduler review |
| Stand by for retest | Next deploy attempt will show if the background scheduler was the issue |
| Escalate if still failing | May need to revert migrations 019+ or add timeout guards |

---

## 🔴 Tonight (Tue 03:00 HKT) — PLAN-015 Phase 2 Full Deploy [PARKED]
**MC Task:** jn7empmf7mavh1tjad5j39aswn833f0d | **Priority:** P1

| # | Task | Effort | Detail |
|---|------|--------|--------|
| 1 | Fix R/L/A heartbeats → update agent-link health | 20min | Add `update-health` call to their HEARTBEAT.md or cron scripts |
| 2 | Integrate HMAC signing into worker | 30min | Wire `agent-link-signing.py` into `agent-link-worker.py` send path |
| 3 | Add queue processor cron | 15min | Every 5min, retries pending messages |
| 4 | Update all agent AGENTS.md with signature verification | 30min | R/L/A need verification instructions + code snippet |
| 5 | Flush 2 stuck queue messages | 5min | Retry the April messages sitting at 0 attempts |
| 6 | End-to-end test: signed message Molty→each agent | 30min | Send, verify delivery, confirm ACK |
| 7 | Troubleshoot any failures | 30min | Budget for issues |
| 8 | Update docs: PLAN-015, PLAN-REGISTRY, MEMORY.md | 15min | Mark Phase 2 complete |
| 9 | Update MC task → done | 5min | Close it out |
| | **Total** | **~3h** | |

## 🟡 PLAN-016: Todoist↔MC Sync v2 (slipped — reschedule after PLAN-015)
| Phase | Task | Status |
|-------|------|--------|
| 1 | Prefix parsing (`Raphael:` → `[Raphael]` + MC task) | Pending |
| 2 | Standup triage ("2 Raphael" processing) | Pending |
| 3 | Bi-directional completion sync | Pending |
| 4 | Test full cycle | Pending |
| 5 | First real test at standup | Pending |

## 🟡 MC Sprint Backlog (after PLAN-016)
| Task | Effort | Night |
|------|--------|-------|
| [D1] Task Templates | 3h | TBD |
| [D6] User Auth (Login) | 4h | TBD |
| D2: Notification Preferences | 2h | TBD |
| D4: Memory Timeline/Diff | 3h | TBD |
| C5: File Attachments | 3h | TBD |

## 🔴 Morning Briefing Format Overhaul
**Context:** Guillermo said current format "just doesn't work" — not one useful day (2026-03-21). Needs full redesign, not tweaks.
- [ ] Review what info is actually useful vs noise
- [ ] Draft new format options
- [ ] Get Guillermo's sign-off on new format
- [ ] Update briefing script + cron

## 🟡 Pending
- [x] ~~Test new webchat standup flow at 5PM today~~ (done, fixed cron bug)

## 🟢 Done (last 7 days)
- [x] **2026-03-14:** Standup v3.0 — webchat-native, Notion task DB dropped, crons + docs updated
- [x] **2026-03-14:** TODO.md tracking system created and linked
- [x] **2026-03-14:** April tools.allow fix — removed restriction, she can execute tools now
- [x] **2026-03-13:** Productivity framework audit → `docs/PRODUCTIVITY-FRAMEWORK-AUDIT-2026-03-13.md`
- [x] **2026-03-13:** Morning briefing v3.3 approved — condensed format live
- [x] **2026-03-12:** Agent-Link v2 (PLAN-015) — fleet messaging with retry queue
- [x] **2026-03-12:** Discord @mentions format fix (REG-026)
- [x] **2026-03-11:** April deployment — Railway + Discord + WhatsApp + Calendar

## 🚧 Blocked
- [ ] WHOOP integration — waiting on CLIENT_ID/SECRET from Guillermo (rescheduled to Mar 17)
- [ ] ginesta.io website — waiting on content checklist from Guillermo
- [ ] Cerebro CRM PR #76 — waiting on Guillermo review

---

*Sync: Check this file at session start. Update after completing significant work.*
