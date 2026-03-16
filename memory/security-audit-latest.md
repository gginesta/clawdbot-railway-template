OpenClaw Security Audit — March 16, 2026 03:00 HKT
Summary: 2 critical · 4 warn · 3 info

CRITICAL
hooks.allowed_agent_ids_unrestricted Hook agent routing allows any configured agent
  hooks.allowedAgentIds is unset or includes '*', so authenticated hook callers may route to any configured agent id.
  Fix: Set hooks.allowedAgentIds to an explicit allowlist (for example, ["hooks", "main"]) or [] to deny explicit agent routing.
  [NEW — NOT IN ACCEPTED RISKS]

skills.code_safety Skill "notion-enhanced" contains dangerous code patterns
  Found 1 critical issue(s) in 9 scanned file(s) under /data/workspace/skills/notion-enhanced:
  - [env-harvesting] Environment variable access combined with network send — possible credential harvesting (scripts/notion-utils.js:14)
  Fix: Review the skill source code before use. If untrusted, remove "/data/workspace/skills/notion-enhanced".
  [ACCEPTED RISK]

WARN
gateway.control_ui.host_header_origin_fallback DANGEROUS: Host-header origin fallback enabled
  gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true enables Host-header origin fallback for Control UI/WebChat websocket checks and weakens DNS rebinding protections.
  Fix: Disable gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback and configure explicit gateway.controlUi.allowedOrigins.
  [NEW — NOT IN ACCEPTED RISKS]

config.insecure_or_dangerous_flags Insecure or dangerous config flags enabled
  Detected 1 enabled flag(s): gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true.
  Fix: Disable these flags when not actively debugging, or keep deployment scoped to trusted/local-only networks.
  [ACCEPTED RISK — flagged due to dangerouslyDisableDeviceAuth=true reference]

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

## Comparison: March 9 → March 16, 2026

### Summary Changes
- **Critical findings:** 2 → 2 (stable)
- **Warn findings:** 4 → 4 (stable)
- **Info findings:** 3 → 3 (unchanged)

### Issues Resolved ✅
- **gateway.control_ui.device_auth_disabled** (CRITICAL) — GONE
  - Was marked ACCEPTED RISK on Mar 9, now not appearing
  - dangerouslyDisableDeviceAuth is no longer in current config
- **gateway.trusted_proxies_missing** (WARN) — GONE
  - No longer flagged (loopback binding only, reverse proxy config not required)

### ⚠️ NEW Findings (NOT in Accepted Risks)

**🔴 CRITICAL:**
1. **hooks.allowed_agent_ids_unrestricted**
   - Impact: Authenticated hook callers can route to ANY configured agent id
   - Current state: hooks.allowedAgentIds is unset or contains '*'
   - Fix: Set hooks.allowedAgentIds to explicit allowlist ["hooks", "main"] or [] to deny explicit agent routing
   - **Action required:** Review webhook routing configuration and restrict allowedAgentIds

**🟡 WARN:**
1. **gateway.control_ui.host_header_origin_fallback**
   - Impact: Host-header origin fallback enabled, weakens DNS rebinding protections
   - Current state: gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true
   - Fix: Disable the flag and configure explicit gateway.controlUi.allowedOrigins
   - **Action required:** Decide if this flag is still needed; disable if not actively debugging

### Persistent Issues (Accepted Risks)
✓ skills.code_safety notion-enhanced env-harvesting (accepted)
✓ models.weak_tier Haiku (accepted — Sonnet 4 weak tier warning)
✓ security.trust_model.multi_user_heuristic (accepted — Discord allowlist warning)
✓ config.insecure_or_dangerous_flags (accepted)

### Software Version
- Installed: v2026.3.12 (current stable)
- Update available: v2026.3.13 (npm)
- Status: Deps ok, update pending (no critical blockers)

---

**Audit Time:** Monday, March 16, 2026 — 03:00 HKT
**Previous audit:** Sunday, March 9, 2026 — 03:00 HKT
**Days elapsed:** 7 days
**Next audit:** Monday, March 23, 2026 — 03:00 HKT
