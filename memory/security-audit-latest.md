OpenClaw security audit
Summary: 3 critical · 2 warn · 3 info
Run deeper: openclaw security audit --deep

CRITICAL
hooks.request_session_key_enabled External hook payloads may override sessionKey
  hooks.allowRequestSessionKey=true allows `/hooks/agent` callers to choose the session key. Treat hook token holders as full-trust unless you also restrict prefixes.
  Fix: Set hooks.allowRequestSessionKey=false (recommended) or constrain hooks.allowedSessionKeyPrefixes.
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
models.weak_tier Some configured models are below recommended tiers
  Smaller/older models are generally more susceptible to prompt injection and tool misuse.
- anthropic/claude-sonnet-4-0 (Below Claude 4.5) @ agents.defaults.model.fallbacks
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

Doctor warnings
- Telegram allowFrom contains 1 non-numeric entries (e.g. -5298647132); Telegram authorization requires numeric sender IDs.
- Run "openclaw doctor --fix" to auto-resolve @username entries to numeric IDs (requires a Telegram bot token).

OpenClaw update status

┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Item     │ Value                                                                                                    │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Install  │ git (/openclaw)                                                                                          │
│ Channel  │ dev (main)                                                                                               │
│ Git      │ main · @ 188c4cd0                                                                                        │
│ Update   │ available · git main · ↔ origin/main · behind 836 · npm update 2026.2.14 · deps ok                       │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Update available (git behind 836 · npm 2026.2.14). Run: openclaw update
