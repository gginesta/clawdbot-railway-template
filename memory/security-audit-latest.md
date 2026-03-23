OpenClaw Security Audit — March 23, 2026 03:00 HKT
Summary: 2 critical · 4 warn · 3 info

CRITICAL
hooks.allowed_agent_ids_unrestricted Hook agent routing allows any configured agent
  hooks.allowedAgentIds is unset or includes '*', so authenticated hook callers may route to any configured agent id.
  Fix: Set hooks.allowedAgentIds to an explicit allowlist (for example, ["hooks", "main"]) or [] to deny explicit agent routing.
  [UNRESOLVED — flagged continuously since Mar 16]

skills.code_safety Skill "notion-enhanced" contains dangerous code patterns
  Found 1 critical issue(s) in 9 scanned file(s) under /data/workspace/skills/notion-enhanced:
  - [env-harvesting] Environment variable access combined with network send — possible credential harvesting (scripts/notion-utils.js:14)
  Fix: Review the skill source code before use. If untrusted, remove "/data/workspace/skills/notion-enhanced".
  [ACCEPTED RISK]

WARN
gateway.control_ui.host_header_origin_fallback DANGEROUS: Host-header origin fallback enabled
  gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true enables Host-header origin fallback for Control UI/WebChat websocket checks and weakens DNS rebinding protections.
  Fix: Disable gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback and configure explicit gateway.controlUi.allowedOrigins.
  [UNRESOLVED — flagged continuously since Mar 16]

config.insecure_or_dangerous_flags Insecure or dangerous config flags enabled
  Detected 1 enabled flag(s): gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true.
  Fix: Disable these flags when not actively debugging, or keep deployment scoped to trusted/local-only networks.
  [ACCEPTED RISK — dangerouslyDisableDeviceAuth=true reference]

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

## Comparison: March 16 → March 23, 2026 (7-day delta)

### Summary Status
- **Critical findings:** 2 → 2 (STABLE)
- **Warn findings:** 4 → 4 (STABLE)
- **Info findings:** 3 → 3 (STABLE)
- **Overall posture:** No improvement or degradation

### Issues Still Outstanding (Not Resolved)

**🔴 CRITICAL (2 unresolved):**
1. **hooks.allowed_agent_ids_unrestricted** [flagged Mar 16, UNRESOLVED]
   - Authenticated hook callers can route to ANY configured agent
   - hooks.allowedAgentIds is unset or '*'
   - Requires explicit allowlist config

2. **skills.code_safety notion-enhanced** [ongoing, ACCEPTED RISK]
   - env-harvesting pattern in scripts/notion-utils.js:14
   - Marked as accepted risk (skill is in use)

**🟡 WARN (1 unresolved, 3 accepted):**
1. **gateway.control_ui.host_header_origin_fallback** [flagged Mar 16, UNRESOLVED]
   - dangerouslyAllowHostHeaderOriginFallback=true
   - Weakens DNS rebinding protections
   - Requires config change to disable

2. ✓ config.insecure_or_dangerous_flags (accepted risk)
3. ✓ models.weak_tier Haiku (accepted risk)
4. ✓ security.trust_model.multi_user_heuristic (accepted risk)

### Software Version Status
- **Installed:** v2026.3.12 (stable)
- **Available:** v2026.3.13 (npm)
- **Deps:** OK
- **Update:** Recommended (non-critical)

---

## NEW Findings (Not Previously Accepted)

✅ **NONE.** The two unresolved findings (hooks.allowed_agent_ids_unrestricted and gateway.control_ui.host_header_origin_fallback) are **persistent** from March 16 — they remain flagged but are neither new nor accepted in risk whitelist.

---

**Audit Timestamp:** Monday, March 23, 2026 — 03:00 HKT
**Days Since Last Audit:** 7 days
**Audit Command:** `openclaw security audit --deep`
**Update Status:** v2026.3.13 available (defer unless urgent)
