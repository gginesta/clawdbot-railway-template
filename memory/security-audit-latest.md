OpenClaw security audit
Summary: 2 critical · 3 warn · 3 info
Run deeper: openclaw security audit --deep

CRITICAL
security.exposure.open_groups_with_elevated Open groupPolicy with elevated tools enabled
  Found groupPolicy="open" at:
- channels.discord.groupPolicy
With tools.elevated enabled, a prompt injection in those rooms can become a high-impact incident.
  Fix: Set groupPolicy="allowlist" and keep elevated allowlists extremely tight.
skills.code_safety Skill "notion-enhanced" contains dangerous code patterns
  Found 1 critical issue(s) in 9 scanned file(s) under /data/workspace/skills/notion-enhanced:
  - [env-harvesting] Environment variable access combined with network send — possible credential harvesting (scripts/notion-utils.js:14)
  Fix: Review the skill source code before use. If untrusted, remove "/data/workspace/skills/notion-enhanced".

WARN
gateway.auth_no_rate_limit No auth rate limiting configured
  gateway.bind is not loopback but no gateway.auth.rateLimit is configured. Without rate limiting, brute-force auth attacks are not mitigated.
  Fix: Set gateway.auth.rateLimit (e.g. { maxAttempts: 10, windowMs: 60000, lockoutMs: 300000 }).
hooks.default_session_key_unset hooks.defaultSessionKey is not configured
  Hook agent runs without explicit sessionKey use generated per-request keys. Set hooks.defaultSessionKey to keep hook ingress scoped to a known session.
  Fix: Set hooks.defaultSessionKey (for example, "hook:ingress").
models.weak_tier Some configured models are below recommended tiers
  Smaller/older models are generally more susceptible to prompt injection and tool misuse.
- anthropic/claude-haiku-4-5 (Haiku tier (smaller model)) @ agents.defaults.model.fallbacks
  Fix: Use the latest, top-tier model for any bot with tools or untrusted inboxes. Avoid Haiku tiers; prefer GPT-5+ and Claude 4.5+.

INFO
summary.attack_surface Attack surface summary
  groups: open=1, allowlist=1
tools.elevated: enabled
hooks.webhooks: enabled
hooks.internal: enabled
browser control: enabled
gateway.tailscale_serve Tailscale Serve exposure enabled
  gateway.tailscale.mode="serve" exposes the Gateway to your tailnet (loopback behind Tailscale).
config.secrets.hooks_token_in_config Hooks token is stored in config
  hooks.token is set in the config file; keep config perms tight and treat it like an API secret.

OpenClaw update status

┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Item     │ Value                                                                                                    │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Install  │ git (/openclaw)                                                                                          │
│ Channel  │ stable (v2026.2.21)                                                                                      │
│ Git      │ detached · tag v2026.2.21 · @ 5e34eb98                                                                   │
│ Update   │ git HEAD · dirty · npm latest 2026.2.21-2 · deps ok                                                      │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

---

## Audit Comparison (Feb 23, 2026 03:00 HKT)

### Summary of Changes
- **Critical findings:** 3 → 2 (improved)
- **Warn findings:** 2 → 3 (degraded)
- **Info findings:** 3 → 3 (unchanged)

### Fixed Issues
✅ `hooks.request_session_key_enabled` — RESOLVED in this audit

### New Findings (NOT in accepted risks)
❌ **hooks.default_session_key_unset** (WARN)
   - Hook agent runs without explicit sessionKey; generated per-request keys reduce scoping
   - Recommendation: Set hooks.defaultSessionKey (e.g., "hook:ingress")
   - **Status:** Requires attention — this is a configuration gap

### Persistent Issues (Accepted Risks)
✓ `security.exposure.open_groups_with_elevated` — open Discord groupPolicy (accepted)
✓ `skills.code_safety` (notion-enhanced) — env-harvesting pattern (accepted)
✓ `gateway.auth_no_rate_limit` — no brute-force mitigation configured (under review)

### Model Tier Change
⚠️ Fallback model changed: Sonnet 4.0 → Haiku-4-5
   - Haiku is a smaller tier; weaker for security
   - Previous "Sonnet 4 weak tier warning" (accepted) was for Sonnet
   - This new Haiku warning is technically a different model/tier escalation
   - **Status:** May require re-evaluation

### Update Status
- Installed: v2026.2.21 (stable)
- No pending updates; system is on latest stable channel

---
**Audit Time:** Monday, February 23, 2026 — 03:00 HKT
**Next audit recommended:** 7 days
