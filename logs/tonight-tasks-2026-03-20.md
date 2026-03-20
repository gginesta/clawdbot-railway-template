# Tonight's Tasks — 2026-03-20 (03:00 HKT window)

## ✅ DONE: Fix "LLM request rejected: thinking blocks" spam
- **Root cause:** Daily Status Report cron (`e94b898e`) had `sessionKey` pointing to Discord #command-center session. That session accumulated thinking/redacted_thinking blocks from previous Opus runs. Every new run tried to resume the corrupted session → LLM rejected → error posted to Discord.
- **Fix:** Removed `sessionKey` from cron config so it creates fresh isolated sessions. Also updated payload from MC to Paperclip queries.
- **Also fixed:** Weekly MC Digest (`b6b54820`) — missing Discord channel target. Fleet Health Check (`65be2a8d`) — stale sessionKey removed.

## 🔧 TODO: Fix Paperclip Heartbeats (all agents in error state)

### Current State
| Agent | Company | Paperclip Status | Last Heartbeat |
|-------|---------|-----------------|----------------|
| Molty | TMNT | error | 2026-03-18 18:09 UTC |
| April | TMNT | idle | 2026-03-18 09:10 UTC |
| Raphael | Brinc | error | 2026-03-19 16:39 UTC |
| Leonardo | Cerebro | error | 2026-03-18 09:50 UTC |

### Investigation Steps
1. Check if Paperclip heartbeat invocation is configured (adapter settings per agent)
2. Check Paperclip logs for heartbeat failure reasons
3. Verify agent gateway URLs are reachable from Paperclip container
4. Test manual heartbeat invocation for each agent
5. Check if the overnight cron (Molty Nightly Task Worker) is supposed to trigger heartbeats
6. If heartbeats need a separate cron, create one

### Success Criteria
- All 4 agents show `status=idle` or `status=active` in Paperclip
- `lastHeartbeatAt` updated to today's date
- No error state

## 🔧 TODO: Clean up stale crons
- PLAN-017a MC Stale Task Escalation — still queries MC, should query Paperclip
- Daily Standup 5PM — still queries MC for squad status, should use Paperclip
- Pre-Standup Prep — runs `standup_prep.py` which may reference MC

## 📝 Notes
- Agents ARE active (posting to Discord via their own crons) but not heartbeating through Paperclip
- Raphael is actively using Paperclip API (created BRI-43,44,45, cleaned 37 stale tasks)
- TMN-6 (brief squad leads) marked done — onboarding happened
- Phase 4 (clean overnight cycle) can't pass until heartbeats work
