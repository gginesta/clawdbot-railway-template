# Leonardo 🔵 Full Deployment Audit
**Date:** 2026-02-11 11:55 HKT | **Auditor:** Molty 🦎

---

## 🟢 WORKING (Verified)

| # | Item | Evidence |
|---|------|----------|
| 1 | **Gateway running** | HTTP 200 on `/health` |
| 2 | **Webchat functional** | Guillermo chatted with him (screenshot) |
| 3 | **Model: Claude Opus 4.6** | Confirmed via `/status` in webchat |
| 4 | **Discord bot in server** | Member info: joined 2026-02-10, role `Leonardo` (1470931285500231847) |
| 5 | **Discord posting works** | Posted in #launchpad-general (msg 1470991318275588131) |
| 6 | **Telegram bot configured** | Token in config |
| 7 | **Telegram pairing** | Guillermo auto-approved |
| 8 | **Webhook inbound (Molty → Leo)** | All webhook calls return `{"ok":true}` |
| 9 | **Hooks enabled + token set** | Config confirmed |
| 10 | **ownerAllowFrom configured** | Telegram + Discord IDs for Guillermo |
| 11 | **#launchpad-general channel** | Exists (1470919420791619758), topic set |
| 12 | **#launchpad-private channel** | Exists (1470919437975814226), topic set |
| 13 | **Deployment announced** | #squad-updates msg 1470976190377623784 |
| 14 | **OpenClaw version** | 2026.2.9 (7f1712c) |

---

## 🟡 PARTIAL / NEEDS VERIFICATION (Awaiting Leonardo's audit response)

| # | Item | Status | Action Needed |
|---|------|--------|---------------|
| 15 | **Workspace files (9 files)** | Sent via webhook | Need Leonardo to confirm content accuracy |
| 16 | **BOOTSTRAP.md removed** | Likely deleted | Need confirmation |
| 17 | **MEMORY.md created** | Was reported missing earlier | Need confirmation |
| 18 | **memory/ directory** | Unknown | Leonardo should create + write first daily file |
| 19 | **Persistent volume /data** | Should be configured (Railway) | Need `df -h /data` output |
| 20 | **Git repo initialized** | Unknown | Need `git remote -v` output |

---

## 🔴 NOT DONE (Action Required)

| # | Item | Priority | Action |
|---|------|----------|--------|
| 21 | **Sub-agent auth** | 🔴 HIGH | `cp /root/.openclaw/auth-profiles.json /root/.openclaw/agents/main/agent/auth-profiles.json` — causes the error Guillermo saw |
| 22 | **#command-center intro** | 🔴 HIGH | Leonardo hasn't posted there yet — Guillermo specifically requested this |
| 23 | **Webhook outbound (Leo → Molty)** | 🔴 HIGH | Leonardo doesn't have Molty's webhook URL in TOOLS.md |
| 24 | **Webhook outbound (Leo → Raphael)** | 🟡 MED | Not configured yet |
| 25 | **QMD / bun not installed** | 🟡 MED | `curl -fsSL https://bun.sh/install \| bash && bun install -g qmd` |
| 26 | **Codex OAuth / GPT-5.3** | 🟡 MED | Guillermo says it was set up but config crashed with it — needs re-add |
| 27 | **Syncthing** | 🟡 MED | Not installed, not connected to Molty/Raphael mesh |
| 28 | **Shared memory vault** | 🟡 MED | Role-based permissions not configured |
| 29 | **Skills (email, todoist, notion)** | 🟡 MED | None installed |
| 30 | **Credentials directory** | 🟡 MED | No gmail, todoist, twitter creds |
| 31 | **Notion workspace** | 🟡 MED | Not set up for Leonardo |
| 32 | **Backup system** | 🟡 MED | No backup script or cron |
| 33 | **Heartbeat cron** | 🟡 MED | No periodic heartbeat configured |
| 34 | **Daily standup cron** | 🟡 MED | No standup job (may not need one — TBD) |
| 35 | **Tailscale** | 🟠 LOW | Not installed → `dangerouslyDisableDeviceAuth: true` still active |
| 36 | **Remove SETUP_PASSWORD** | 🟠 LOW | Railway env var `leo-setup-temp-2026` still set |
| 37 | **Discord role permissions** | 🟠 LOW | Leonardo has basic perms (75776), not Admin like Molty. Fine for now. |
| 38 | **Browser (Brave)** | 🟠 LOW | Unknown if installed — not critical for Leo's role |

---

## Summary

**Working:** 14/38 items ✅
**Needs verification:** 6/38 items 🟡
**Not done:** 18/38 items 🔴🟡🟠

### Critical Path (do now):
1. Fix sub-agent auth (#21)
2. Leonardo intros in #command-center (#22)
3. Configure bidirectional webhooks (#23-24)
4. Verify workspace files + persistence (#15-20)

### Next Wave:
5. Install QMD (#25)
6. Re-add Codex/GPT-5.3 (#26)
7. Install Syncthing + shared vault (#27-28)
8. Skills + credentials (#29-30)

### Can Wait:
9. Notion, backups, crons (#31-34)
10. Tailscale, cleanup (#35-37)
