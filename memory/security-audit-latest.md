OpenClaw Security Audit — March 2, 2026 03:00 HKT
Summary: 3 critical · 3 warn · 3 info
Run deeper: openclaw security audit --deep

CRITICAL
security.exposure.open_groups_with_elevated Open groupPolicy with elevated tools enabled
  Found groupPolicy="open" at:
- channels.discord.groupPolicy
With tools.elevated enabled, a prompt injection in those rooms can become a high-impact incident.
  Fix: Set groupPolicy="allowlist" and keep elevated allowlists extremely tight.
security.exposure.open_groups_with_runtime_or_fs Open groupPolicy with runtime/filesystem tools exposed
  Found groupPolicy="open" at:
- channels.discord.groupPolicy
Risky tool exposure contexts:
- agents.defaults (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
- agents.list.main (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
Prompt injection in open groups can trigger command/file actions in these contexts.
  Fix: For open groups, prefer tools.profile="messaging" (or deny group:runtime/group:fs), set tools.fs.workspaceOnly=true, and use agents.defaults.sandbox.mode="all" for exposed agents.
skills.code_safety Skill "notion-enhanced" contains dangerous code patterns
  Found 1 critical issue(s) in 9 scanned file(s) under /data/workspace/skills/notion-enhanced:
  - [env-harvesting] Environment variable access combined with network send — possible credential harvesting (scripts/notion-utils.js:14)
  Fix: Review the skill source code before use. If untrusted, remove "/data/workspace/skills/notion-enhanced".

WARN
gateway.auth_no_rate_limit No auth rate limiting configured
  gateway.bind is not loopback but no gateway.auth.rateLimit is configured. Without rate limiting, brute-force auth attacks are not mitigated.
  Fix: Set gateway.auth.rateLimit (e.g. { maxAttempts: 10, windowMs: 60000, lockoutMs: 300000 }).
models.weak_tier Some configured models are below recommended tiers
  Smaller/older models are generally more susceptible to prompt injection and tool misuse.
- anthropic/claude-haiku-4-5 (Haiku tier (smaller model)) @ agents.defaults.model.fallbacks
  Fix: Use the latest, top-tier model for any bot with tools or untrusted inboxes. Avoid Haiku tiers; prefer GPT-5+ and Claude 4.5+.
security.trust_model.multi_user_heuristic Potential multi-user setup detected (personal-assistant model warning)
  Heuristic signals indicate this gateway may be reachable by multiple users:
- channels.telegram.groupPolicy="allowlist" with configured group targets
- channels.discord.groupPolicy="open"
Runtime/process tools are exposed without full sandboxing in at least one context.
Potential high-impact tool exposure contexts:
- agents.defaults (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
- agents.list.main (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
OpenClaw's default security model is personal-assistant (one trusted operator boundary), not hostile multi-tenant isolation on one shared gateway.
  Fix: If users may be mutually untrusted, split trust boundaries (separate gateways + credentials, ideally separate OS users/hosts). If you intentionally run shared-user access, set agents.defaults.sandbox.mode="all", keep tools.fs.workspaceOnly=true, deny runtime/fs/web tools unless required, and keep personal/private identities + credentials off that runtime.

INFO
summary.attack_surface Attack surface summary
  groups: open=1, allowlist=1
tools.elevated: enabled
hooks.webhooks: enabled
hooks.internal: enabled
browser control: enabled
trust model: personal assistant (one trusted operator boundary), not hostile multi-tenant on one shared gateway
gateway.tailscale_serve Tailscale Serve exposure enabled
  gateway.tailscale.mode="serve" exposes the Gateway to your tailnet (loopback behind Tailscale).
config.secrets.hooks_token_in_config Hooks token is stored in config
  hooks.token is set in the config file; keep config perms tight and treat it like an API secret.

OpenClaw update status
┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Item     │ Value                                                                                                    │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Install  │ git (/openclaw)                                                                                          │
│ Channel  │ stable (v2026.2.26)                                                                                      │
│ Git      │ detached · tag v2026.2.26 · @ bc507080                                                                   │
│ Update   │ git HEAD · dirty · npm latest 2026.2.26 · deps ok                                                        │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

---

## Audit Comparison (Previous: Feb 23 → Current: Mar 2, 2026)

### Summary of Changes
- **Critical findings:** 2 → 3 (degraded: +1 new critical)
- **Warn findings:** 3 → 3 (stable)
- **Info findings:** 3 → 3 (unchanged)

### ⚠️ NEW FINDINGS (NOT in accepted risks)

**🔴 CRITICAL: security.exposure.open_groups_with_runtime_or_fs**
   - Open Discord channel exposes runtime (exec/process) and filesystem (read/write/edit) tools
   - Risk: Prompt injection in #command-center or other open channels can execute commands or modify workspace files
   - Fix: Set channels.discord.groupPolicy="allowlist" or use tools.profile="messaging" for open channels
   - **Severity:** High — requires immediate attention
   - **Action needed:** Review Discord channel access policies; consider restricting to allowlist-only

**🟡 WARN: security.trust_model.multi_user_heuristic**
   - Detector identified potential multi-user setup (Telegram allowlist + open Discord groups)
   - With elevated tools exposed, this is a security gap for a personal-assistant model
   - Current assumption: single trusted operator. If that changes, separate trust boundaries required.
   - **Action needed:** Acknowledge this is intentional single-user setup, or split gateways/users

### Resolved Issues
✅ `hooks.default_session_key_unset` — no longer present (improved)

### Persistent Issues (Previously Accepted)
✓ `security.exposure.open_groups_with_elevated` — open Discord groupPolicy (accepted)
✓ `skills.code_safety` (notion-enhanced env-harvesting) — accepted risk
✓ `gateway.auth_no_rate_limit` — no brute-force mitigation (accepted; loopback-only in practice)

### Version Status
- Installed: v2026.2.26 (stable)
- Updated from: v2026.2.21 (Feb 23)
- No pending updates

---
**Audit Time:** Monday, March 2, 2026 — 03:00 HKT (cron job)
**Previous audit:** Sunday, February 23, 2026 — 03:00 HKT
**Days elapsed:** 7 days
**Next audit:** March 9, 2026 — 03:00 HKT
