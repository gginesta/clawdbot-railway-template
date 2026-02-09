OpenClaw security audit
Summary: 2 critical · 1 warn · 3 info
Run deeper: openclaw security audit --deep

CRITICAL
security.exposure.open_groups_with_elevated Open groupPolicy with elevated tools enabled
  Found groupPolicy="open" at:
- channels.discord.groupPolicy
With tools.elevated enabled, a prompt injection in those rooms can become a high-impact incident.
  Fix: Set groupPolicy="allowlist" and keep elevated allowlists extremely tight.
channels.discord.warning.1 Discord security warning
  Discord guilds: groupPolicy="open" allows any channel not explicitly denied to trigger (mention-gated). Set channels.discord.groupPolicy="allowlist" and configure channels.discord.guilds.<id>.channels.

WARN
models.weak_tier Some configured models are below recommended tiers
  Smaller/older models are generally more susceptible to prompt injection and tool misuse.
- anthropic/claude-sonnet-4-0 (Below Claude 4.5) @ agents.defaults.model.fallbacks
  Fix: Use the latest, top-tier model for any bot with tools or untrusted inboxes. Avoid Haiku tiers; prefer GPT-5+ and Claude 4.5+.

INFO
summary.attack_surface Attack surface summary
  groups: open=1, allowlist=1
tools.elevated: enabled
hooks: enabled
browser control: enabled
gateway.tailscale_serve Tailscale Serve exposure enabled
  gateway.tailscale.mode="serve" exposes the Gateway to your tailnet (loopback behind Tailscale).
config.secrets.hooks_token_in_config Hooks token is set in the config file; keep config perms tight and treat it like an API secret.

OpenClaw update status

┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Item     │ Value                                                                                                    │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Install  │ git (/openclaw)                                                                                          │
│ Channel  │ dev (main)                                                                                               │
│ Git      │ main · @ 95263f4e                                                                                        │
│ Update   │ available · git main · ↔ origin/main · dirty · behind 32 · npm latest 2026.2.6-3 · deps ok               │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

Update available (git behind 32). Run: openclaw update
