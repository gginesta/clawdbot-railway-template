# 🔒 Security Hardening Plan — TMNT Fleet

**Created:** 2026-02-05 13:43 UTC  
**Status:** IN PROGRESS  
**Scope:** Molty (ggvmolt.up.railway.app) + Raphael (ggv-raphael.up.railway.app)  
**Approved by:** Guillermo (2026-02-05)

---

## Audit Summary

### Molty 🦎
| Severity | Count | Details |
|----------|-------|---------|
| 🔴 CRITICAL | 2 | Device auth disabled, small model without sandbox |
| ⚠️ WARN | 3 | Short hooks token, weak fallback model, Discord no allowlists |
| ℹ️ INFO | 2 | Attack surface summary, hooks token in config |
| 🔄 UPDATE | 1 | 86 commits behind on main branch |

### Raphael 🔴
| Severity | Count | Details |
|----------|-------|---------|
| 🔄 PENDING | — | Audit request sent, awaiting response |

---

## Remediation Checklist

### Phase 1: Config Hardening (No Restart Required)

- [ ] **1.1 — MOLTY: Remove Llama 70B from fallback chain** 🔴 CRITICAL
  - **Why:** 70B param model with full web tool access = prompt injection risk
  - **Action:** Remove `openrouter/meta-llama/llama-3.3-70b-instruct` from `agents.defaults.model.fallbacks`
  - **New chain:** `claude-sonnet-4 → gpt-5.2 → grok-3` (all large enough to be safe)
  - **Risk:** None — Llama was a last-resort fallback we never hit

- [ ] **1.2 — MOLTY: Generate new 64-char hooks token** ⚠️ WARN
  - **Why:** Current token is only 20 chars; webhooks are externally reachable
  - **Action:** Generate cryptographic random token, update config
  - **Dependency:** Must also update Raphael's webhook URL/token if he calls our hooks
  - **Risk:** Breaks existing webhook integrations until tokens are synced

- [ ] **1.3 — MOLTY: Add Discord allowlists** ⚠️ WARN
  - **Why:** Slash commands are enabled but rejected for everyone (no allowlist)
  - **Action:** Add Guillermo's Discord user ID to `channels.discord.dm.allowFrom`
  - **Need from Guillermo:** Your Discord user ID (right-click your name → Copy User ID)
  - **Risk:** None

- [ ] **1.4 — MOLTY: Evaluate device auth** 🔴 CRITICAL (ACCEPTED RISK)
  - **Why:** `dangerouslyDisableDeviceAuth=true` lets anyone with the URL access Control UI
  - **Current mitigation:** Railway provides a unique URL, not easily guessable
  - **Options:**
    1. ✅ Keep disabled + add IP allowlist if Railway supports it (it doesn't natively)
    2. Re-enable device auth + use Telegram/webchat only (lose web Control UI)
    3. Keep as-is (accepted risk — documented)
  - **Recommendation:** Keep as accepted risk, document it, revisit when OpenClaw adds better auth
  - **Risk:** Medium — URL is obscure but not secret

- [ ] **1.5 — RAPHAEL: Mirror all applicable fixes from 1.1–1.4**
  - Raphael runs his own audit and applies same standards
  - Specific items TBD after his audit report comes back

### Phase 2: Update OpenClaw (Requires Restart)

- [ ] **2.1 — MOLTY: Backup before update**
  - **Action:** Run `/data/workspace/backups/backup.sh` + `git push backup master`
  - **Why:** 86 commits is a significant update — need rollback point

- [ ] **2.2 — MOLTY: Update OpenClaw**
  - **Action:** `openclaw update` (git pull + restart)
  - **Expected:** Update from `4a5d3689` to latest on main
  - **Risk:** Breaking changes possible after 86 commits — monitor for errors post-restart

- [ ] **2.3 — MOLTY: Post-update verification**
  - Re-run `openclaw security audit --deep`
  - Verify all channels working (Telegram, Discord, webchat)
  - Verify cron jobs intact
  - Check that config changes from Phase 1 persisted

- [ ] **2.4 — RAPHAEL: Update OpenClaw**
  - Same process: backup → update → verify
  - Coordinate timing to avoid both agents being down simultaneously

### Phase 3: Verification & Documentation

- [ ] **3.1 — Re-run audits on both instances**
  - Target: 0 critical, 0 warn (or all documented as accepted risks)

- [ ] **3.2 — Document accepted risks in MEMORY.md**
  - Device auth disabled (accepted, documented)
  - Syncthing ports exposed (auth-protected, accepted)
  - Any other consciously accepted items

- [ ] **3.3 — Set up periodic audit cron**
  - Schedule weekly `openclaw security audit --deep` for both instances
  - Alert to Telegram if findings change

- [ ] **3.4 — Sync hooks tokens between agents**
  - After new tokens generated, update both agents' webhook configs
  - Test agent-to-agent communication still works

---

## Port Audit (Molty)

| Port | Binding | Service | Verdict |
|------|---------|---------|---------|
| 8080 | 0.0.0.0 | OpenClaw Gateway | ✅ Required — Railway routes here |
| 8384 | 0.0.0.0* | Syncthing GUI | ⚠️ Config says 127.0.0.1 but IPv6 shows :: — verify binding |
| 22000 | 0.0.0.0 | Syncthing data | ✅ Required for sync — has device auth |
| 64019 | 0.0.0.0 | OpenClaw internal | ✅ Gateway process — likely metrics/debug |
| 18789 | 127.0.0.1 | OpenClaw internal | ✅ Localhost only |
| 18792 | 127.0.0.1 | OpenClaw internal | ✅ Localhost only |
| 18800 | 127.0.0.1 | Brave debugger | ✅ Localhost only |

---

## Execution Order

```
Phase 1.1 (remove Llama) ──┐
Phase 1.2 (hooks token)  ──┼── All config changes batched → single restart
Phase 1.3 (Discord allow) ─┘
         │
         ▼
Phase 1.4 (device auth) ── Decision needed from Guillermo
         │
         ▼
Phase 2.1 (backup) → Phase 2.2 (update) → Phase 2.3 (verify)
         │
         ▼
Phase 1.5 + 2.4 (Raphael mirrors everything)
         │
         ▼
Phase 3.1-3.4 (verify + document + schedule)
```

---

## Decision Log

| # | Decision | Status | Notes |
|---|----------|--------|-------|
| D1 | Device auth | PENDING | Need Guillermo's call — keep disabled or re-enable? |
| D2 | Discord user ID | PENDING | Need Guillermo's Discord user ID for allowlist |
| D3 | Hooks token | APPROVED | Will generate 64-char replacement |
| D4 | Remove Llama 70B | APPROVED | No reason to keep a risky fallback we never use |

---

*This plan is tracked live. Check boxes are updated as items complete.*
