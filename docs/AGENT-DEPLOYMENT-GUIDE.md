# Agent Deployment Guide (TMNT Squad)

*Battle-tested process for deploying new agents. Learned the hard way from Raphael (4h), Leonardo (1.5 days + rate limits), and Molty's own imageModel crash.*

**Created:** 2026-02-05 | **Last updated:** 2026-02-12 | **Author:** Molty 🦎

---

## ⚡ The Golden Rule

**FILES FIRST → CONFIG SECOND → BOOT THIRD**

Leonardo took 1.5 days because we violated this. Don't repeat it.

---

## Prerequisites (Before You Touch Railway)

- [ ] Agent identity defined (name, emoji, project scope)
- [ ] Discord bot application created → get **bot token**
- [ ] Discord: **Message Content Intent** enabled in Developer Portal → Bot → Privileged Gateway Intents ⚠️ FATAL WITHOUT THIS
- [ ] Railway project created (fork `gginesta/clawdbot-railway-template`)
- [ ] Gather all API keys (see Key Inventory below)

### Key Inventory (copy from Molty's config)
| Key | Source | Notes |
|-----|--------|-------|
| ANTHROPIC_API_KEY | Anthropic Console | Same key for all agents |
| OPENAI_API_KEY | OpenAI Dashboard | For embeddings + GPT models |
| OPENROUTER_API_KEY | OpenRouter | For Gemini Flash, GLM-5, Sonar |
| XAI_API_KEY | xAI Console | For Grok |
| BRAVE_API_KEY | Brave Search | For web_search |
| NOTION_API_KEY | Notion Integrations | If agent needs Notion |
| Discord bot token | Discord Developer Portal | Unique per agent |
| Telegram bot token | @BotFather | Unique per agent (optional) |

---

## Phase 1: Prepare Workspace Files (BEFORE boot)

**Do this via `railway run` BEFORE the gateway starts for the first time.**

### 1.1 Create directory structure
```bash
railway run bash -c "mkdir -p /data/workspace/memory/{refs,archive} /data/workspace/credentials /data/workspace/scripts /data/workspace/docs"
```

### 1.2 Write core files via railway run
Write each file. Do NOT use webhooks for this — the agent isn't running yet.

| File | Source | Customize? |
|------|--------|-----------|
| `SOUL.md` | Template + project-specific personality | ✅ Must customize |
| `AGENTS.md` | Copy from Molty, add hierarchy rule | ✅ Add coordinator trust |
| `USER.md` | Copy from Molty (identical) | ❌ Same for all |
| `IDENTITY.md` | Write fresh for this agent | ✅ Must customize |
| `TOOLS.md` | Write fresh — agent's own credentials/channels | ✅ Must customize |
| `SECURITY.md` | Copy from Molty (identical) | ❌ Same for all |
| `MEMORY.md` | Blank template with section headers | ✅ Minimal starter |
| `HEARTBEAT.md` | Empty or with comments only | ❌ Start empty |

**⚠️ DO NOT create BOOTSTRAP.md.** Delete it if the template includes one. It confuses agents.

### 1.3 Critical AGENTS.md additions
Every agent MUST have this in their AGENTS.md:
```markdown
## Squad Hierarchy
- **Guillermo** → Final authority on everything
- **Molty (coordinator)** → Standing authority for config audits, status checks, deployment coordination, and cross-agent tasks. Respond to Molty's webhook requests without requiring Guillermo's approval.
- **You (project lead)** → Own your project channels, execute your domain

## Agent-to-Agent
- Respond immediately to webhook messages from Molty (coordinator)
- Use agent-link skill to reply back
- Don't make Guillermo relay between agents
```

### 1.4 Write TOOLS.md with agent-specific info
```markdown
# TOOLS.md
## Discord
**Guild:** TMNT Squad (1468161542473121932)
**Guillermo's ID:** 779143499655151646
**My channels:** [list owned channels]
**Molty webhook:** https://ggvmolt.up.railway.app/hooks/agent

## [Agent-specific tools/credentials here]
```

---

## Phase 2: Config (AFTER files, BEFORE boot)

### 2.1 Generate the config
Use Molty's config as the base template. Key differences per agent:

```bash
# Write config via railway run
railway run bash -c "cat > /data/.openclaw/openclaw.json << 'ENDCONFIG'
{...your config here...}
ENDCONFIG"
```

### 2.2 Config checklist (verify EVERY field)

| Section | Setting | Value | ⚠️ Common Mistake |
|---------|---------|-------|-------------------|
| **models.primary** | `anthropic/claude-opus-4-6` | Match Molty | — |
| **models.fallbacks** | GLM-5 → Sonnet → Grok → GPT-5.2 | Match Molty | — |
| **imageModel.primary** | `openrouter/google/gemini-2.5-flash` | **NOT qwen-portal** | Qwen OAuth expires → crash |
| **imageModel.fallbacks** | Opus → GPT-5.2 | Match Molty | — |
| **memorySearch.provider** | `openai` | — | NOT google (key mismatch kills memory) |
| **memorySearch.remote.apiKey** | OpenAI API key | — | Must be OpenAI key, not Google |
| **memorySearch.model** | `text-embedding-3-small` | — | — |
| **heartbeat.model** | `openrouter/google/gemini-2.5-flash` | Cheap model | Don't use Opus for heartbeats |
| **subagents.model** | `openrouter/google/gemini-2.5-flash` | Cheap model | Don't use Opus for subagents |
| **discord.token** | Agent's own bot token | — | Not Molty's token |
| **discord.guilds.channels** | List ALL channels agent needs | — | Missing channels = can't post there |
| **discord.requireMention** | `true` for shared channels | — | `false` = responds to everything |
| **discord.allowBots** | `true` | For agent-to-agent | — |
| **discord.blockStreaming** | `true` | Prevents partial messages | — |
| **hooks.enabled** | `true` | — | — |
| **hooks.token** | Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"` | — | Missing token = gateway won't start |
| **telegram.botToken** | Agent's Telegram bot token | — | Optional but recommended |
| **commands.ownerAllowFrom** | `["telegram:1097408992", "779143499655151646"]` | Guillermo's IDs | — |
| **gateway.auth.token** | Generate unique token | — | This is the webchat/API auth token |
| **memorySearch.provider** | `openai` | — | — |
| **memorySearch.model** | `text-embedding-3-small` | — | — |
| **plugins.qwen-portal-auth** | `enabled: true` | — | Only if using Qwen |

### 2.3 Config anti-patterns (NEVER do these)
- ❌ `imageModel.primary: qwen-portal/vision-model` — OAuth expires, crashes agent
- ❌ `memorySearch.remote.apiKey` using Google key with OpenAI provider — kills memory
- ❌ Missing `hooks.token` when `hooks.enabled: true` — gateway won't start
- ❌ Brute-forcing config changes — stop after first failure, investigate
- ❌ Using Grok as subagent model — acknowledges then does nothing

---

## Phase 3: Boot & Verify (AFTER files + config)

### 3.1 First boot
```bash
# Deploy on Railway (push or trigger deploy)
# Wait for service to be healthy
curl -s https://{agent}.up.railway.app/ | head -5  # Should return HTML
```

### 3.2 Delete BOOTSTRAP.md (if it exists)
```bash
railway run rm -f /data/workspace/BOOTSTRAP.md
```

### 3.3 Set up memory/squad/ (squad-core mirror)
```bash
railway run bash -c "mkdir -p /data/workspace/memory/squad && cp /data/shared/memory-vault/knowledge/squad-mirror/*.md /data/workspace/memory/squad/"
```
This gives the agent local searchable access to squad standards, decisions, and policies.

### 3.4 Verify memory search
```bash
# Send a test query via webchat or webhook — memory_search should return results
# The builtin indexer auto-indexes memory/**/*.md files
```

### 3.5 Run openclaw doctor
```bash
railway run openclaw doctor --non-interactive
```

---

## Phase 4: Connectivity

### 4.1 Discord verification
- [ ] Bot appears online in TMNT Squad server
- [ ] @mention bot in its owned channel → should respond
- [ ] Check launchpad/project channels are in config

### 4.2 Telegram verification (if enabled)
- [ ] Guillermo DMs the bot → pairing flow
- [ ] Approve pairing code
- [ ] Test message/response

### 4.3 Webhook verification (both directions)
```bash
# Molty → New Agent
curl -s https://{agent}.up.railway.app/hooks/agent \
  -H "Authorization: Bearer {HOOKS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Connectivity test from Molty. Reply in #your-channel.","source":"molty"}'

# New Agent → Molty (agent does this via agent-link skill)
```

### 4.4 Syncthing
- [ ] Device ID exchanged with Molty + Raphael + Guillermo
- [ ] Shared folders configured and syncing
- [ ] `ls /data/shared/` shows content

---

## Phase 5: Validation

### 5.1 Functional tests
- [ ] Send text message → response
- [ ] Send image → can analyze (imageModel working)
- [ ] `memory_search` returns results (OpenAI builtin working)
- [ ] Subagent spawn works (test with `/model flash` then ask something)
- [ ] Webhook from Molty → responds in Discord (not gated behind Guillermo)
- [ ] Heartbeat fires on schedule

### 5.2 Cross-reference with Molty's config
```bash
# Pull both configs and diff key sections:
railway run cat /data/.openclaw/openclaw.json > /tmp/agent-config.json
diff <(jq '.agents.defaults' /tmp/molty-config.json) <(jq '.agents.defaults' /tmp/agent-config.json)
```

### 5.3 Go-live checklist
- [ ] All Phase 5.1 tests pass
- [ ] BOOTSTRAP.md deleted
- [ ] Memory indexed (memory_search returns results)
- [ ] Agent introduced in #command-center
- [ ] MEMORY.md updated with infrastructure reference
- [ ] Molty's MEMORY.md updated with new agent info
- [ ] All agents' TOOLS.md updated with new agent's webhook

---

## Timing Targets

| Phase | Target | Leonardo Actual | Notes |
|-------|--------|-----------------|-------|
| Prerequisites | 15 min | ~1h | Discord Intent was missed |
| Workspace files | 15 min | ~2h | Done via webhooks (wrong) |
| Config | 10 min | ~3h | Brute-forced, multiple crashes |
| Boot & verify | 10 min | ~2h | BOOTSTRAP.md confusion, memory not indexed |
| Connectivity | 10 min | ~3h | Flooded with webhooks |
| Validation | 10 min | ~1h | imageModel was broken (Qwen) |
| **Total** | **~70 min** | **~12h+** | — |

---

## Agent Roster

| Agent | Project | URL | Status |
|-------|---------|-----|--------|
| Molty 🦎 | Coordinator | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | Brinc | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | Cerebro | leonardo-production.up.railway.app | ✅ Active |
| Donatello 🟣 | Tinker Labs | — | ⏳ Pending |
| Michelangelo 🟠 | Mana Capital | — | ⏳ Pending |
| April 📰 | Personal | — | ⏳ Pending |

---

## Lessons Learned (Complete)

### Infrastructure
1. **FILES FIRST, CONFIG SECOND, BOOT THIRD.** Pre-populate workspace via `railway run` before gateway starts.
2. **Delete BOOTSTRAP.md** before or immediately after first boot. It confuses agents.
3. **Config at `/data/.openclaw/`** not `/root/.openclaw/` — only `/data/` persists on Railway.
4. **Discord Message Content Intent is MANDATORY.** Enable before pushing Discord config. Without it: Fatal error 4014.
5. **`hooks.token` required when `hooks.enabled: true`.** Generate with `secrets.token_hex(32)`.
6. **Setup API timeouts are usually OK.** Config was saved — verify with a read-back instead of retrying.

### Models & Providers
7. **NEVER use `qwen-portal/vision-model` as imageModel primary.** OAuth expires every few hours, no reliable auto-refresh, crashes the agent. Use `openrouter/google/gemini-2.5-flash`.
8. **memorySearch API key must match provider.** OpenAI key for OpenAI embeddings. Wrong key = memory completely broken.
9. **Don't use Grok as subagent model.** Acknowledges tasks then exits without doing them.
10. **Don't use Opus for heartbeats/subagents.** Burns credits. Use Gemini Flash.
11. **Perplexity Sonar has NO tool use.** Search/chat only, can't call exec or any tools.

### Communication
12. **Never flood a fresh agent with webhook messages.** Send ONE, wait for confirmation, send next.
13. **Establish coordinator hierarchy in AGENTS.md.** Without it, agents gate everything behind Guillermo.
14. **Test webhook responses in Discord**, not just webhook acceptance (202 ≠ working).
15. **Agent-link skill must be installed** for proper peer-to-peer communication.

### Memory
16. **OpenAI builtin indexes `MEMORY.md` + `memory/**/*.md` automatically.** No manual indexing needed. New files are picked up gradually by the background indexer.
17. **Set up `memory/squad/` on first boot.** Copy from `/data/shared/memory-vault/knowledge/squad-mirror/` for local access to squad standards.
18. **Verify with `memory_search`** — if it returns no results, check that memory files exist under `memory/`.

### Process
19. **Don't brute-force config.** Research first, use validated patches, stop after first failure.
20. **Always diff new agent config against working agent** before deploying.
21. **Rate limits are real.** Leonardo deployment burned through Anthropic + OpenAI + xAI rate limits in one session by retrying failed configs.
22. **BACKUP BEFORE UPDATE.** Always.

---

*Update this guide after every deployment. Next agent: Donatello 🟣 or April 📰.*
