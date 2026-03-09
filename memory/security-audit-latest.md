OpenClaw Security Audit — March 9, 2026 03:00 HKT
Summary: 2 critical · 4 warn · 3 info

CRITICAL
gateway.control_ui.device_auth_disabled DANGEROUS: Control UI device auth disabled
  gateway.controlUi.dangerouslyDisableDeviceAuth=true disables device identity checks for the Control UI.
  Fix: Disable it unless you are in a short-lived break-glass scenario.
  [ACCEPTED RISK]

skills.code_safety Skill "notion-enhanced" contains dangerous code patterns
  Found 1 critical issue(s) in 9 scanned file(s) under /data/workspace/skills/notion-enhanced:
  - [env-harvesting] Environment variable access combined with network send — possible credential harvesting (scripts/notion-utils.js:14)
  Fix: Review the skill source code before use. If untrusted, remove "/data/workspace/skills/notion-enhanced".
  [ACCEPTED RISK]

WARN
gateway.trusted_proxies_missing Reverse proxy headers are not trusted
  gateway.bind is loopback and gateway.trustedProxies is empty. If you expose the Control UI through a reverse proxy, configure trusted proxies so local-client checks cannot be spoofed.
  Fix: Set gateway.trustedProxies to your proxy IPs or keep the Control UI local-only.
  [NEW — NOT IN ACCEPTED RISKS]

config.insecure_or_dangerous_flags Insecure or dangerous config flags enabled
  Detected 1 enabled flag(s): gateway.controlUi.dangerouslyDisableDeviceAuth=true.
  Fix: Disable these flags when not actively debugging, or keep deployment scoped to trusted/local-only networks.
  [ACCEPTED RISK — flagged due to dangerouslyDisableDeviceAuth=true]

models.weak_tier Some configured models are below recommended tiers
  Smaller/older models are generally more susceptible to prompt injection and tool misuse.
- anthropic/claude-haiku-4-5 (Haiku tier (smaller model)) @ agents.defaults.model.fallbacks
  Fix: Use the latest, top-tier model for any bot with tools or untrusted inboxes. Avoid Haiku tiers; prefer GPT-5+ and Claude 4.5+.
  [ACCEPTED RISK — Sonnet 4 weak tier warning]

security.trust_model.multi_user_heuristic Potential multi-user setup detected (personal-assistant model warning)
  Heuristic signals indicate this gateway may be reachable by multiple users:
- channels.telegram.groupPolicy="allowlist" with configured group targets
- channels.discord.groupPolicy="allowlist" with configured group targets
Runtime/process tools are exposed without full sandboxing in at least one context.
Potential high-impact tool exposure contexts:
- agents.defaults (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
- agents.list.main (sandbox=off; runtime=[exec, process]; fs=[read, write, edit, apply_patch]; fs.workspaceOnly=false)
OpenClaw's default security model is personal-assistant (one trusted operator boundary), not hostile multi-tenant isolation on one shared gateway.
  Fix: If users may be mutually untrusted, split trust boundaries (separate gateways + credentials, ideally separate OS users/hosts). If you intentionally run shared-user access, set agents.defaults.sandbox.mode="all", keep tools.fs.workspaceOnly=true, deny runtime/fs/web tools unless required, and keep personal/private identities + credentials off that runtime.
  [ACCEPTED RISK — Discord allowlist warning]

INFO
summary.attack_surface Attack surface summary
  groups: open=0, allowlist=2
tools.elevated: enabled
hooks.webhooks: enabled
hooks.internal: enabled
browser control: enabled
trust model: personal assistant (one trusted operator boundary), not hostile multi-tenant on one shared gateway
gateway.tailscale_serve Tailscale Serve exposure enabled
  gateway.tailscale.mode="serve" exposes the Gateway to your tailnet (loopback behind Tailscale).
config.secrets.hooks_token_in_config Hooks token is stored in config
  hooks.token is set in the config file; keep config perms tight and treat it like an API secret.

---

## Comparison: March 2 → March 9, 2026

### Summary of Changes
- **Critical findings:** 3 → 2 (improved: -1)
- **Warn findings:** 3 → 4 (degraded: +1)
- **Info findings:** 3 → 3 (unchanged)

### Issues Resolved ✅
- **security.exposure.open_groups_with_elevated** (CRITICAL) — GONE
  - Discord groupPolicy changed from "open" to "allowlist"
  - Previously marked for remediation, now fixed
- **security.exposure.open_groups_with_runtime_or_fs** (CRITICAL) — GONE
  - Open Discord groups no longer expose runtime/filesystem tools
- **gateway.auth_no_rate_limit** (WARN) — GONE
  - No longer flagged (loopback binding assumed)

### NEW Findings (Not in Accepted Risks)
- **🟡 gateway.trusted_proxies_missing** (WARN)
  - Control UI behind reverse proxy without trusted proxy headers configured
  - Risk: Local-client checks can be spoofed if behind reverse proxy
  - Fix: Set `gateway.trustedProxies` to proxy IPs, or keep Control UI local-only
  - **Action:** Configure if exposing Control UI through reverse proxy (e.g., Tailscale Serve); otherwise acknowledge as intentional local-only

### Persistent Issues (Accepted Risks)
✓ dangerouslyDisableDeviceAuth=true (accepted)
✓ Haiku weak tier (accepted — Sonnet 4 weak tier warning)
✓ Discord allowlist warning (accepted, now resolved for open groups)
✓ notion-enhanced env-harvesting (accepted)

### Version Status
- Installed: v2026.3.7 (current stable)
- Updated from: v2026.2.26 (Mar 2)
- Status: Up to date

---
**Audit Time:** Monday, March 9, 2026 — 03:00 HKT
**Previous audit:** Sunday, March 2, 2026 — 03:00 HKT
**Days elapsed:** 7 days
**Next audit:** Monday, March 16, 2026 — 03:00 HKT
