# Deployment Lessons Learned — Leonardo (2026-02-11)

## What Went Wrong

### 1. Webhook Message Flooding
**Problem:** Sent 10+ webhook messages to Leonardo in rapid succession (workspace files, pairing commands, diagnostic requests). He couldn't process them coherently — messages piled up, context got confused, and he started failing on basic tool calls ("read tool called without path").

**Root cause:** Each webhook message creates a new turn in the agent's session. Flooding him with 10 turns of "write this file" while he's also bootstrapping = chaos. He's trying to follow BOOTSTRAP.md, process webhook files, approve pairing, and run diagnostics all at once.

**Fix for next time:** 
- Send ONE onboarding message with clear, sequential instructions
- OR better: pre-populate the workspace files BEFORE the agent boots (see #5 below)
- Never send more than 2-3 webhook messages before waiting for confirmation

### 2. Setup API Timeouts
**Problem:** The `/setup/api/config/raw` and `/setup/api/console` endpoints consistently timed out (15-60s). Wasted ~30 minutes retrying.

**Root cause:** Railway's proxy + the setup wrapper has slow response times when the gateway is starting/restarting. The setup API waits for gateway readiness before responding.

**Fix for next time:**
- Use longer timeouts (120s) for setup API calls
- Don't wait for "gateway ready" confirmation — just push config and move on
- Accept `{"ok":false,"error":"Gateway did not become ready in time"}` as "config saved, gateway will catch up"

### 3. Missing hooks.token
**Problem:** Gateway crashed with `hooks.enabled requires hooks.token`. Config was missing the token field.

**Root cause:** Our config template had `hooks.enabled: true` but no `hooks.token`. The wizard-generated config didn't include hooks at all, and our overlay missed this required field.

**Fix for next time:**
- Config template MUST include `hooks.token` (auto-generate with `secrets.token_hex(32)`)
- Add hooks.token to the pre-flight checklist
- Validate config against OpenClaw's schema before pushing

### 4. Discord Message Content Intent
**Problem:** Gateway crashed with `Fatal Gateway error: 4014` because Message Content Intent wasn't enabled.

**Root cause:** Discord requires this privileged intent to be manually enabled in Developer Portal. We created the bot + invited it but forgot this step.

**Fix for next time:**
- Add "Enable Message Content Intent" as a MANDATORY step in the Discord bot setup checklist
- Check this BEFORE pushing the Discord config
- Include in the deployment guide with screenshots

### 5. Empty Workspace on First Boot
**Problem:** Leonardo booted with an empty `/data/workspace/`. He hit BOOTSTRAP.md and started the "who am I?" flow instead of being onboarded.

**Root cause:** The Railway template creates a fresh volume. Workspace files need to be placed there BEFORE the agent starts processing. We tried to fix this post-boot via webhooks, which created problem #1.

**Fix for next time — THE BIG ONE:**
- **Pre-populate workspace via setup import.** The setup page has a "Import backup (.tar.gz)" feature. Create a tarball of the workspace files and import it BEFORE running the setup wizard.
- **Or:** Add a `/setup/api/files` endpoint request to OpenClaw (feature request)
- **Or:** Use Syncthing — connect the new agent to Molty first, sync the workspace files, THEN boot the gateway
- **Sequence should be:** Files first → Config second → Gateway boot third

### 6. Config Got Corrupted
**Problem:** After pushing config via setup API, the JSON was malformed (duplicate keys, broken structure at line 69).

**Root cause:** Unclear — possibly the setup API's config save merges rather than replaces, or there was a race condition between our push and the gateway's own config writes.

**Fix for next time:**
- Always read config back after writing to verify
- Use the config editor's "Reload" to check what's actually on disk
- Keep a local copy of the intended config for comparison

### 7. Model Order Wrong Initially
**Problem:** Set Claude Opus as primary when Guillermo wanted GPT-5.3.

**Root cause:** Assumed based on my own config. Guillermo had mentioned GPT-5.3 preference for Leonardo multiple times.

**Fix for next time:**
- Confirm model preference explicitly before setting config
- Document each agent's intended model in their deployment checklist
- Don't assume agents share my config preferences

### 9. Railway Redeploy Wipes Auth
**Problem:** Redeployed Leonardo to fix the restart storm, but the redeploy wiped `/root/.openclaw/agents/main/agent/auth-profiles.json` — killing all model auth.

**Root cause:** Railway persistent volume is `/data`, but OpenClaw stores auth profiles under `/root/.openclaw/` which is ephemeral. Redeploy = fresh container = auth gone.

**Fix for next time:**
- NEVER redeploy to fix runtime issues — use `gateway.stop` + `gateway.start` via the setup console instead
- If redeploy is unavoidable, know that auth needs to be re-established afterward
- Feature request: OpenClaw should store auth on the persistent volume, not `/root`

### 8. Gateway Restart Storm
**Problem:** Multiple gateway restart attempts competing (pid lock conflicts, port already in use).

**Root cause:** The setup API's config save triggers a restart. Our webhook messages asking Leonardo to run `openclaw gateway restart` added more restart attempts. Plus the gateway's own crash-restart loop from the hooks.token error.

**Fix for next time:**
- Never ask the agent to restart the gateway while we're also pushing config changes
- Let the setup API handle restarts
- Wait for stability before sending any operational commands

## Improved Deployment Playbook

### Phase 0: Pre-requisites (Before touching Railway)
- [ ] Discord bot created in Developer Portal
- [ ] **Message Content Intent ENABLED** ✅
- [ ] Bot invited to server with correct permissions
- [ ] Telegram bot created via @BotFather
- [ ] All API keys collected (Anthropic OAuth, Brave, Gemini, OpenAI, OpenRouter, XAI, Notion)
- [ ] Confirm primary model preference with Guillermo
- [ ] SOUL.md reviewed and approved by Guillermo

### Phase 1: Railway Setup (Infrastructure)
- [ ] Railway project + service created
- [ ] Volume mounted at `/data`
- [ ] Template repo linked
- [ ] TZ=Asia/Hong_Kong set
- [ ] SETUP_PASSWORD set
- [ ] All API keys set as env vars (NOT tokens that go in config — those go in Phase 3)
- [ ] Wait for first deployment to complete (SUCCESS status)

### Phase 2: Pre-populate Workspace (BEFORE gateway config)
- [ ] Create workspace tarball from `agents/<name>/` directory:
  ```bash
  cd /data/workspace/agents/<name>
  tar czf /tmp/<name>-workspace.tar.gz \
    SOUL.md IDENTITY.md USER.md AGENTS.md TOOLS.md \
    MEMORY.md HEARTBEAT.md SECURITY.md PRIORITY_BRIEFING.md
  ```
- [ ] Import via setup page: `POST /setup/api/import` or upload via browser
- [ ] **OR** use setup page config editor to write files manually
- [ ] Verify files exist on the instance
- [ ] Delete BOOTSTRAP.md from the workspace

### Phase 3: Configure Gateway
- [ ] Access setup page with SETUP_PASSWORD
- [ ] Run setup wizard (select auth provider, add channel tokens)
- [ ] Wait for gateway to start
- [ ] Push full config via `/setup/api/config/raw` — ensure it includes:
  - [ ] `hooks.token` (auto-generated)
  - [ ] `hooks.enabled: true`
  - [ ] `channels.discord.token`
  - [ ] `channels.telegram.botToken`
  - [ ] `gateway.controlUi.dangerouslyDisableDeviceAuth: true` (temporary)
  - [ ] `gateway.bind: "auto"` (not loopback)
  - [ ] `commands.ownerAllowFrom` (Guillermo's IDs)
  - [ ] Correct model order per agent preference
- [ ] Read config back to verify JSON validity
- [ ] Check gateway logs for errors (no crash loop)

### Phase 4: Verify & Connect
- [ ] Webchat accessible (test "Hello")
- [ ] Agent reads SOUL.md correctly (not running BOOTSTRAP.md)
- [ ] Telegram pairing (Guillermo messages bot → approve)
- [ ] Discord bot shows online in server
- [ ] Send ONE test webhook from Molty → verify response
- [ ] Install QMD: `curl -fsSL https://bun.sh/install | bash && bun install -g qmd`
- [ ] Restart gateway after QMD install
- [ ] Verify `openclaw status` shows memory working

### Phase 5: Fleet Integration
- [ ] Set up Syncthing (connect to Molty + existing agents)
- [ ] Configure agent-to-agent webhooks (update TOOLS.md on all agents)
- [ ] Set up Tailscale
- [ ] Disable `dangerouslyDisableDeviceAuth`
- [ ] Remove SETUP_PASSWORD from Railway env vars
- [ ] Install skills (email, todoist, notion, etc.)
- [ ] Configure Notion workspace
- [ ] Announce in #squad-updates
- [ ] Update Molty's MEMORY.md with new agent info
- [ ] Update all agents' TOOLS.md with new webhook URLs

### Phase 6: Smoke Test
- [ ] Agent responds on webchat ✓
- [ ] Agent responds on Telegram ✓
- [ ] Agent responds on Discord (in owned channels) ✓
- [ ] Agent stays silent in non-owned channels ✓
- [ ] Webhook from Molty → agent responds ✓
- [ ] Webhook from agent → Molty receives ✓
- [ ] Memory search returns results ✓
- [ ] Heartbeat fires correctly ✓

## Time Estimate

With this playbook: **~1.5 hours** (vs 4+ hours for Leonardo)

| Phase | Time |
|-------|------|
| Phase 0 (Pre-reqs) | 15 min (mostly Guillermo in Discord Dev Portal) |
| Phase 1 (Railway) | 10 min |
| Phase 2 (Workspace) | 10 min |
| Phase 3 (Config) | 15 min |
| Phase 4 (Verify) | 15 min |
| Phase 5 (Fleet) | 20 min |
| Phase 6 (Smoke) | 10 min |

## Agents Remaining to Deploy

| Agent | Theme | Status |
|-------|-------|--------|
| Donatello 🟣 | Tinker Labs (Research) | Not started |
| Michelangelo 🟠 | Mana Capital (Investment) | Not started |
| April 📰 | Personal (Fitness, Family) | Not started |

Each should follow this playbook exactly.
