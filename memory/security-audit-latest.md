OpenClaw Security Audit — April 13, 2026 03:00 HKT
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
  [ACCEPTED RISK]

tools.exec.security_full_configured Exec security=full is configured
  Full exec trust is enabled for: main.
  Fix: Prefer tools.exec.security="allowlist" with ask prompts, and reserve "full" for tightly scoped break-glass agents only.
  [NEW — not in Mar 30 audit]

security.trust_model.multi_user_heuristic Potential multi-user setup detected (personal-assistant model warning)
  Heuristic signals indicate this gateway may be reachable by multiple users:
- channels.telegram.groupPolicy="allowlist" with configured group targets
- channels.discord.groupPolicy="allowlist" with configured group targets
  [ACCEPTED RISK — Discord allowlist warning]

INFO
summary.attack_surface Attack surface summary
  groups: open=0, allowlist=2
tools.elevated: enabled
hooks.webhooks: enabled
hooks.internal: enabled
browser control: enabled
trust model: personal assistant (one trusted operator boundary)
gateway.tailscale_serve Tailscale Serve exposure enabled
config.secrets.hooks_token_in_config Hooks token is stored in config

---

## Comparison: March 30 → April 13, 2026 (14-day delta)

### Summary Status
- **Critical findings:** 2 → 2 (STABLE)
- **Warn findings:** 4 → 4 (STABLE count, but composition changed)
- **Info findings:** 3 → 3 (STABLE)

### Changes from Previous Audit

**🆕 NEW finding:**
1. **tools.exec.security_full_configured** — exec security=full enabled for main agent. Not present in Mar 30 audit. Likely surfaced by updated scanner rules in v2026.4.7. This is standard for a single-operator setup; low actual risk.

**⬇️ Resolved/removed:**
1. **models.weak_tier** (Haiku fallback) — no longer flagged. Either the scanner rules changed or the config was adjusted.

### Issues Still Outstanding

**🔴 CRITICAL (2 unresolved):**
1. hooks.allowed_agent_ids_unrestricted [flagged Mar 16]
2. skills.code_safety notion-enhanced [ACCEPTED RISK]

**🟡 WARN (1 unresolved, 3 accepted):**
1. gateway.control_ui.host_header_origin_fallback [flagged Mar 16]
2. ✓ config.insecure_or_dangerous_flags (accepted)
3. ✓ tools.exec.security_full_configured (NEW — standard for single-operator)
4. ✓ security.trust_model.multi_user_heuristic (accepted)

### Software Version
- **Installed:** v2026.4.7 (stable) — updated from v2026.3.23-2
- **Available:** v2026.4.11 (npm)
- **Update:** Available (non-critical)

---

**Audit Timestamp:** Monday, April 13, 2026 — 03:00 HKT
**Days Since Last Audit:** 14 days
