# Codex OAuth Migration Reference

*Created: 2026-04-29 | Last updated: 2026-04-29 09:40 HKT | Agent: Molty*

## Critical Finding

`openclaw onboard --mode remote` configures the **local CLI** to talk to a remote gateway, but the Codex OAuth token produced by the device-code flow is written to the **local machine**:

```powershell
$env:USERPROFILE\.openclaw\agents\main\agent\auth-profiles.json
```

It does **not** automatically write the OAuth token into the Railway container's auth store.

For Railway agents, the migration therefore has two phases:

1. Generate/refresh Codex OAuth locally via PowerShell.
2. Copy the resulting `openai-codex:*` OAuth profile into the target Railway container's:

```text
/data/.openclaw/agents/main/agent/auth-profiles.json
```

Do not assume device-code completion means the remote agent is authenticated. Always verify the token inside the container.

## Prerequisites

- OpenClaw CLI installed locally:

```powershell
npm install -g openclaw
```

- Railway CLI installed and logged in:

```powershell
npm install -g @railway/cli
railway login
```

## Per-Agent Migration Flow

### Step 1: Update Railway Environment Variables

Use Railway GraphQL API to set on the target service:

```text
OPENCLAW_PRIMARY_MODEL=openai-codex/gpt-5.5
OPENCLAW_FALLBACK_MODELS=zai/glm-5.1,deepseek/deepseek-v4-flash,openrouter/anthropic/claude-sonnet-4.6,anthropic/claude-sonnet-4-6
```

### Step 2: Link Railway CLI Locally

```powershell
railway link
# Select: target project → production → target service
```

### Step 3: Configure Local CLI for the Agent's Remote Gateway

```powershell
openclaw onboard --mode remote --remote-url wss://<agent-domain>.up.railway.app --remote-token <gateway-token> --flow manual --accept-risk
```

The gateway token is sensitive. Retrieve it from Railway env vars when needed; do not store it in docs or chat.

### Step 4: Run Codex Device-Code Auth Locally

```powershell
openclaw onboard --auth-choice openai-codex-device-code --accept-risk
```

This prints a code and asks the user to open:

```text
https://auth.openai.com/codex/device
```

After completion, the fresh OAuth profile is local, not remote.

### Step 5: Copy Local OAuth Profile to Target Container

Ask Guillermo to paste local auth profiles:

```powershell
Get-Content "$env:USERPROFILE\.openclaw\agents\main\agent\auth-profiles.json"
```

Then copy the fresh `openai-codex:<email>` profile into the remote container's `/data/.openclaw/agents/main/agent/auth-profiles.json`, usually as `openai-codex:default` if the agent config uses that profile.

Also clear stale Codex cooldowns in:

```text
/data/.openclaw/agents/main/agent/auth-state.json
```

### Step 6: Restart/Reload Gateway

Container wrapper/supervisor may restart the gateway process automatically. Verify via `session_status` or `/status` that the active model is:

```text
openai-codex/gpt-5.5 · oauth
```

### Step 7: Verify Token Freshness

Inside the container, verify:

- OAuth profile exists at `/data/.openclaw/agents/main/agent/auth-profiles.json`
- `expires` is in the future
- JWT `iat` matches the current login date
- `session_status` shows `openai-codex/gpt-5.5` and `oauth`

## Known Agent Domains

| Agent | Domain |
|-------|--------|
| Molty | ggvmolt.up.railway.app |
| Raphael | ggv-raphael.up.railway.app |
| Leonardo | leonardo-production.up.railway.app |
| April | april-agent-production.up.railway.app |

## How WS Proxy Works

- Railway maps `https://<domain>` to container port `8080`.
- `/app/src/server.js` proxies WebSocket upgrades to `127.0.0.1:18789`.
- Therefore `wss://<domain>.up.railway.app` can reach the gateway via the wrapper proxy.
- This only configures the local CLI connection; it does not make OAuth token storage remote.

## OAuth Token Notes

- Fresh Codex access tokens are valid for ~10 days.
- Refresh should be automatic once the token is in the container auth store.
- This should **not** require manual re-auth every 10 days. Manual device-code auth is only required if refresh fails.
- **Do not copy the same refresh token to multiple agents.** OAuth refresh tokens rotate on use; if two containers share one refresh token, the first refresh can invalidate the others and cause `refresh_token_reused`.
- For fleet migration, generate a fresh device-code OAuth profile per agent and copy it into that agent's container before moving to the next.
- If refresh fails with `refresh_token_reused`, re-auth is required.
- Do not conclude refresh is broken until a fresh per-agent token has actually been copied into the container and allowed to expire/refresh there.
- Molty's first real auto-refresh test is around 2026-05-09 09:31 HKT.

## PowerShell Context / Switching Agents

The local OpenClaw CLI has one active remote gateway target at a time. If it is currently pointed at Molty, getting Raphael's OAuth profile does **not** require a new PowerShell window/process, but it does require repointing the local CLI to Raphael first:

```powershell
openclaw onboard --mode remote --remote-url wss://ggv-raphael.up.railway.app --remote-token <raphael-gateway-token> --flow manual --accept-risk
openclaw onboard --auth-choice openai-codex-device-code --accept-risk
Get-Content "$env:USERPROFILE\.openclaw\agents\main\agent\auth-profiles.json"
```

Important operational rule: paste/copy the fresh local `auth-profiles.json` output into the target container **immediately after each agent's device-code flow**, before switching the local CLI to another agent. The local profile is keyed by account/email, not by Railway agent, so the latest local login is the one you must capture for that target.

`railway link` is useful for operator orientation but does not by itself move OAuth into the container. The decisive steps are remote OpenClaw onboarding, local device-code auth, copy profile into container, verify container.

## Image Tool Issue

- In this container, the `image` tool may fail with `Failed to optimize image` even when inbound screenshots arrive under `/data/.openclaw/media/inbound/`.
- Likely image preprocessing dependency issue, not model selection.
- Workaround until fixed: locate latest inbound image path and inspect/convert via another available path, or ask user to paste text.

## Per-Agent Post-Migration Checklist

- [ ] Railway env: `OPENCLAW_PRIMARY_MODEL=openai-codex/gpt-5.5`
- [ ] Railway env: fallbacks set
- [ ] Local device-code auth completed
- [ ] Fresh OAuth profile copied into remote container `auth-profiles.json`
- [ ] Stale Codex cooldown cleared in `auth-state.json`
- [ ] Gateway restarted/reloaded
- [ ] `session_status` or `/status` shows Codex OAuth active
- [ ] `openclaw.json`: image model/config reviewed
- [ ] Cron jobs updated to `openai-codex/gpt-5.4`

## Current Verified State

- Molty: fresh Codex OAuth profile copied into container on 2026-04-29 09:34 HKT; active model verified via `session_status` as `openai-codex/gpt-5.5 · oauth`.
- Raphael: fully migrated to Codex and working well (user-reported by Guillermo 2026-04-29 11:22 HKT). If troubleshooting later, still verify with Raphael `/status` or `session_status`.
- Leonardo/April: still pending. Do not reuse Molty's or Raphael's refresh token for them; generate/copy/verify one agent at a time.
