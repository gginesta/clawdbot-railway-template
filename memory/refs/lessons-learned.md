## 📚 Lessons Learned

### Day 1 (2026-01-31)

1. **Config changes can crash the gateway** — Always back up before major config changes. The "subagent configuration syntax error" took us offline for 7 hours.

2. **Railway containers need special browser flags** — `headless: true` and `noSandbox: true` are required.

3. **Backup configs have timestamps** — `/data/.openclaw/openclaw.json.bak-*` files saved us when config was corrupted.

4. **Skills need OpenClaw-compatible frontmatter** — Claude Code frontmatter (`allowed-tools`, `context`) doesn't work. Use `metadata.clawdbot` format.

5. **Browser profile matters** — Default is "chrome" (extension relay), but we need "openclaw" (headless). Set `browser.defaultProfile`.

6. **Zombie processes happen** — Chromium crashes leave defunct processes. They're cosmetic and clear on redeploy.

7. **Git remote URLs shouldn't contain tokens** — Store tokens in credential files with proper permissions (600).

### Day 2 (2026-02-01)

8. **Context TTL causes memory loss** — 1h TTL was too aggressive. Increased to 4h. Session JSONL files retain full history for recovery if needed.

9. **Always use HKT** — Guillermo is in Hong Kong (UTC+8). Use HKT when discussing times.

### Day 4 (2026-02-04)

10. **Do it yourself first** — When you have access to systems (Discord, Notion, GitHub), don't give instructions — do it yourself. Only ask Guillermo to act when you genuinely can't.

11. **Discord allowBots** — Required for agent-to-agent communication. Default is false (bots ignore other bots).

12. **Channel permissions vs server permissions** — Even with server-level access, private channels need explicit permission overwrites via Discord API.

13. **Bot invites require human action** — Generate OAuth URL, human must click it. Bots can't invite other bots.

14. **Think ahead about the full flow** — When setting up step A, anticipate what step B will need.

15. **Context overflow = death** — Never read entire log/session files. Session JSONL can be 15MB+. Always use `tail -100`, `limit` param, or targeted `grep`. Check file size with `wc -l` before reading unknown files.

### Raphael Deployment Lessons (2026-02-04)

16. **Check shared folders FIRST** — `/data/shared/` via Syncthing is source of truth for cross-agent data. Don't search session logs when the file is already synced.

17. **Sales agents need FULL files** — Objection handlers, case studies, ICP qualification must be complete, not summaries. They need to QUOTE specific content.

18. **Set up Syncthing BEFORE KB transfer** — Files auto-sync once configured. Manual paste is wasted effort.

19. **Verify KB access explicitly** — Ask agent to `ls` the folder AND read a specific file. Sync issues are silent failures.

20. **Quiz before marking "onboarded"** — 10+ questions minimum for sales agents. Require explicit answers.

21. **Audit against SOP at the end** — Run through checklist to catch gaps before declaring complete.

22. **Document blockers clearly** — Raphael was ready but waiting on Guillermo for HubSpot/leads. Make handoff explicit.

23. **PERSIST PLANS TO FILES IMMEDIATELY** — Never just discuss plans in chat. Context pruning will erase them. Any significant plan, decision, or deliverable must be written to a file THE MOMENT it's created. Lost the Todoist integration plan because of this. (2026-02-04)

24. **Document config changes BEFORE applying** — QMD was installed and configured but the context got compacted before I documented it. Guillermo asked "did you upload this?" and I had no memory of doing it. Always write to memory files BEFORE running config.patch or gateway changes. (2026-02-04)

### Day 5 (2026-02-05)

25. **Sub-agents are insanely productive** — 6 parallel agents produced 5 major specs + 1 working system in under 2 hours. GPT-5.2 with high thinking is the sweet spot for technical specs.

26. **Model name precision matters** — `anthropic/claude-sonnet-4` ≠ `anthropic/claude-sonnet-4-0`. The `-0` suffix caused a sub-agent spawn to fail. Always use exact model IDs from config.

27. **Python `.format()` vs bash templates** — Never use `.format()` for bash script templates. Bash arrays, curl codes, and variable expansions all conflict. Use `.replace()` instead.

28. **Test against real sites immediately** — Unbrowse MVP had a template bug only surfaced when generating actual scripts. Quick test cycle caught it in minutes.

29. **last30days script OOMs on Railway** — Gets SIGKILL. Use direct web_search + web_fetch instead.

30. **Security updates need coordinated token rotation** — When rotating shared tokens, update the OTHER instance BEFORE changing your own config (using the old token to authenticate).

31. **Check shared files before proposing new systems** — Proposed fleet-wide lessons file; it already existed in OPERATIONAL-GUIDELINES.md. Always check `/data/shared/memory-vault/` first.

32. **Unbrowse is 70/30** — Great for REST CRUD (70% of SaaS integrations). Falls short on OAuth flows, WebSocket, GraphQL, stateful workflows. Best as discovery + scaffolding (80%) then human polish (20%).

33. **Formalizing sub-agents pays off** — Ad-hoc spawning works but named roles with pre-loaded instructions = faster + more consistent results.

### Day 7 (2026-02-07)

35. **Sub-agent SOUL.md gold standard template (APPROVED BY GUILLERMO)** — Peach (Brinc Head of Marketing) is the reference for all future sub-agent definitions. Must include: role, responsibilities, behaviors, direct reports, model choice, brand guidelines, communication channels, and a SOUL.md. Reference: `/data/shared/memory-vault/knowledge/projects/brinc/team/peach/SOUL.md`. Guillermo approved this as the standard. (2026-02-07)

### Day 6 (2026-02-06)

### Day 8 (2026-02-08)

36. **Daily standup is a 3-step process — don't skip steps.** The correct procedure is: (1) Process Todoist inbox first (rewrite titles, add descriptions, assign projects, set priorities, estimate time), (2) Create Notion standup page using approved template (callout + inline Task Review child_database + Tomorrow's Priority + Blockers sections), (3) THEN present summary to Guillermo. Never present a standup without having processed inbox AND created the Notion page first. Template reference: Feb 7 page `30039dd6-9afd-8137-b854-e9701a0b7648`. (2026-02-08)

38. **Calendar time-blocking is step 3 of standup.** After processing Guillermo's standup decisions, create Google Calendar time blocks for the next 1-2 days. Use energy schedule (deep work 9-12, light 12-14, meetings 14-17) and respect life commitments (school dropoff MWF 8-8:30, pickup 10:30-11). Calendar token is in `calendar-tokens-brinc.json` (NOT gmail-tokens.json — different OAuth scopes). Write to personal calendar for non-Brinc, Brinc calendar for work. (2026-02-08)

45. **Agent deployment: FILES FIRST, CONFIG SECOND, BOOT THIRD.** Leonardo deployment took 4+ hours because we booted the gateway before populating workspace files. The agent hit BOOTSTRAP.md and got confused. Then we flooded him with 10+ webhook messages trying to fix it — he couldn't process them coherently. Correct order: (1) pre-populate workspace via setup import/tarball, (2) delete BOOTSTRAP.md, (3) push config, (4) boot gateway. Full playbook in `docs/DEPLOYMENT-LESSONS-LEONARDO.md`. (2026-02-11)

46. **Never flood a fresh agent with webhook messages.** Send ONE message, wait for confirmation, then send the next. 10 concurrent webhook messages = context chaos + failed tool calls. (2026-02-11)

47. **Discord Message Content Intent is MANDATORY.** Must enable in Developer Portal → Bot → Privileged Gateway Intents BEFORE pushing Discord config. Without it: Fatal Gateway error 4014, instant crash. Add to every bot setup checklist. (2026-02-11)

48. **hooks.enabled requires hooks.token.** Config template MUST include a generated token when hooks are enabled. Auto-generate with `secrets.token_hex(32)`. Gateway refuses to start without it. (2026-02-11)

49. **Setup API "Gateway did not become ready" is usually OK.** The config WAS saved — the API just timed out waiting for the restart. Read config back to verify instead of retrying the write. (2026-02-11)

42. **NEVER brute-force config changes.** Three crashes in one session trying to fix openai-codex provider config. Each "fix" broke something new. Rule: research first, use config.patch (validates), stop after first failure and ask for help. Guillermo had to get Raphael to rescue. (2026-02-10)

43. **Perplexity Sonar has NO tool use.** Sonar models via OpenRouter are search/chat only — they cannot call exec, gmail.sh, or any tools. Error: "No endpoints found that support tool use". Use Sonar for pure research queries only; for research+action tasks use Opus/Sonnet sub-agents. (2026-02-10)

44. **Perplexity Sonar via OpenRouter replaces paid Perplexity.** Added `sonar` (fast search) and `deep-research` (synthesis) aliases. Good for research but remember lesson #43. (2026-02-10)

39. **Grok is unreliable as a sub-agent model.** Spawned 3 tasks on Grok — all acknowledged and exited without executing. One hallucinated "compiled comprehensive report" but the file didn't exist. Sonnet completed the same task properly in ~2 minutes. **Rule: Use Sonnet or Flash for sub-agent execution tasks. Grok is chat-only.** (2026-02-09)

40. **Always check BOTH calendars before creating time blocks.** Personal + Brinc calendars have different events. I created blocks that overlapped existing Brinc meetings because I only checked the personal calendar. Pull all calendars → map free slots → THEN create blocks. (2026-02-09)

41. **Cron delivery needs explicit `to` field.** All isolated cron jobs delivering to Telegram must have `"to": "1097408992"` in their delivery config, not just `"channel": "telegram"`. Without it: "cron delivery target is missing" error. Fixed all 8 jobs on Feb 9. (2026-02-09)

37. **Twitter login in headless Brave requires cookie injection.** The login form renders blank due to anti-bot detection. Workaround: set `auth_token` and `ct0` cookies via `document.cookie` JS eval, then navigate. Cookies stored in `/data/workspace/credentials/twitter.env`. (2026-02-08)

50. **Memory search API key mismatch kills everything.** The memorySearch.remote.apiKey was a Google key being sent to OpenAI embeddings. Without working memory, every model switch fails. Always verify memorySearch key matches the configured provider. (2026-02-11)

34. **BACKUP BEFORE UPDATE — ALWAYS** — System crash reinforced this rule. The procedure was documented but as "after backup → check updates" not "before update → backup first". Made the rule explicit and bidirectional. Added to fleet-wide OPERATIONAL-GUIDELINES.md. No exceptions. (2026-02-06)

---

## Lessons

### 122. Railway containers are ephemeral — don't use `gateway update.run` (Mar 9 2026)
**Mistake:** Tried to update OpenClaw via `gateway update.run` + manual git operations on Railway. After restart, container reset to original deploy state. Made Guillermo manually redeploy.
**Fix:** On Railway, updates require a **redeploy** from the Railway dashboard/CLI, not in-container git operations. `update.run` only works on persistent hosts (VPS, local installs).
**Rule:** Before attempting `update.run`, check if running on ephemeral infrastructure (Railway, Render, etc.). If yes, tell user to trigger redeploy instead. #53-58 (Leonardo Deployment Post-Mortem, 2026-02-13)

53. **Verify workspace files AFTER every agent deployment** — Check SOUL/IDENTITY/AGENTS via webchat (not Railway CLI). Cross-contamination happens silently.
54. **The ONLY way to modify remote Railway files is webchat/webhook/setup-API** — `railway run` is LOCAL. If you think you fixed something via Railway CLI, you didn't.
55. **New agents MUST have coordinator authority in their SOUL.md from day one** — Otherwise they'll (correctly) refuse Molty's audit requests.
56. **QMD and imageModel must be verified as deployment checklist items** — Run `qmd status`, test screenshot processing, verify via webchat.
57. **Don't let deployments go stale** — If deferred, schedule a follow-up. Gaps lead to Guillermo deploying without Molty, which leads to misconfigurations.
58. **Agent authority must be confirmed by the human** — Agents rightfully question coordinator authority claims from peers. Guillermo must confirm directly.

50. **Combined backup+update cron is the standard.** Single cron job that: (1) runs backup.sh first, (2) fails safely if backup fails (no update), (3) git checkout -- . to clean dirty tree, (4) runs gateway update.run, (5) announces results to #command-center via delivery. Adopted from Raphael's pattern. All agents should use this. (2026-02-14)

51. **Daily status post via cron delivery.** Don't need a separate status cron — the combined backup+update cron announces its results to #command-center, which serves as the daily status. Leonardo has a dedicated status cron as an alternative pattern. (2026-02-14)

### March 2026 (PLAN-010 Migration)

**Migrated from MEMORY.md 2026-03-04:**

39. **Direct Anthropic Auth:** Prefer direct auth over OpenRouter. Sub-agents can't use exec tool or directly update Notion.

43. **Notion block reorder:** Use internal API (`/api/v3/saveTransactions`) with `token_v2` cookie.

47-48. **Python/venv:** System Python lacks pip — always use `/data/workspace/.venv/bin/python3`.

49. **message tool params:** `message` for text, `target` for recipient, `channel` for platform.

50. **Browser stale lock files:** Fixed in startup.sh (f0f39aa). Automatic cleanup on deploy.

51. **Anthropic is a built-in provider:** No `models.providers.anthropic` block needed.

54. **Calendar ownership rule:** NEVER put Molty tasks on Guillermo's calendar.

56. **OpenClaw upgrades:** `gateway restart` reloads config only. Full Railway redeploy required for binary upgrades.

60. **Shared credentials rule:** Go in `/data/shared/credentials/`. Webhooks deliver messages, not file writes.

61. **Change control:** One change per cycle, declare blast radius, no mixed objectives.

65. **OpenClaw auth:** auth.json is TRUE source, auth-profiles.json is derived. Path: `/data/.openclaw/agents/main/agent/auth.json`.

66. **Isolated sub-agent webhook processes:** Do NOT inherit container env vars. Must hardcode values.

74. **Model fallback chain:** Primary → Haiku → Grok-3 → Codex/GPT-5.2.

77. **Verify current state:** Check config files, APIs, and MC before claiming something isn't done.

80. **Anthropic token is fleet-wide:** Same `sk-ant-*` token for Molty, Raphael, Leonardo.

82. **Fleet Directive System:** Queue: `/data/shared/pending-directives/<agent>/`.

84. **Railway API GraphQL:** Use inline IDs, not `$variable` syntax.

87. **Isolated crons:** Can't use memory_search — use `cat` + `curl`. Pre-flight checks.

89. **Fleet directives:** Go to #command-center. One message, all agents.

91. **Memory index corruption:** `openclaw memory index --force` if 0 files but >0 embeddings.

92. **Three-agent overnight system:** Raphael 00:30, Leonardo 01:30, Molty 03:00 HKT.

95. **Notion comment monitoring:** Public API returns empty. Use internal API loadPageChunk.

96. **process_standup.py:** Dedup via in-memory dict. Threshold: 55% fuzzy match.

97. **Cron agentId:** Must not be empty string — set to "main".

104. **Standup script:** Never run debug/test after showing Guillermo the URL.

105. **Notion property names:** Strict matching. Log response body on non-200.

106. **Fleet update cron:** Check + notify only. NEVER auto-update.

108-109. **Fleet crons:** Daily status 09:00 HKT. Backup = each agent's own cron.

112. **Python variable shadowing:** Local var shadows module function → UnboundLocalError.

113. **OpenClaw config:** `gateway.bind="loopback"` when `tailscale.mode="serve"`.

114. **OpenClaw config:** `channels.discord.dm` is deprecated. Use `dmPolicy` at top level.

115. **PPEE lesson:** Diagnose before acting. One fix, not many attempts.

116. **MC API endpoints:** GET `/api/tasks` (plural). POST/PATCH `/api/task` (singular).

117. **Calendar token fix:** SA token (no delegation). Don't use calendar-tokens-brinc.json.

118. **"Initiate call" means CALL:** Sending prep questions to Telegram is not initiating. Send a voice message or call the phone. Prep materials ≠ the call itself.

119. **Never json.load() OpenClaw configs (Mar 9 2026):** Attempted to patch Raphael's config with `json.load()` startCommand. Failed because OpenClaw configs are JSON5/JSONC — they contain comments and trailing commas. `json.load()` crashes on comments. Use proper JSON5 parser or YAML loader, not standard json module.

120. **No untested startCommands in production (Mar 9 2026):** Added a broken `startCommand` script to Raphael without testing. Container crashed on startup — couldn't recover without Guillermo's manual redeploy via Railway dashboard. **Rule: Test all startCommands locally or in a throwaway container BEFORE pushing to production.**

121. **Railway CGNAT range must be in gateway.trustedProxies (Mar 9 2026):** Molty webchat was broken due to "untrusted proxy" errors. Logs showed: `Proxy headers detected from untrusted address. Connection will not be treated as local.` Root cause: Railway's internal proxies (100.64.0.0/10 CGNAT range) were not in `gateway.trustedProxies` — only had `127.0.0.1`. Fix: Add `"trustedProxies": ["127.0.0.1", "100.64.0.0/10"]` to gateway config. **Rule: On Railway deployments, ALWAYS include Railway's CGNAT range in trustedProxies from the start.**

122. **Discord blocking Railway IPs (Cloudflare 429) — change region (Mar 9 2026):** Leonardo's Discord bot token appeared to expire/rotate. Actually caused: Railway us-west2 region's IPs were Cloudflare-blocked by Discord. Symptoms: 429 errors, bot offline, token "appears invalid". Fix: Change Railway region to Singapore (or any non-west region) to get fresh IP allocation that Discord hasn't blocked. **Rule: If Discord API returns 429 and token is valid, change Railway region before assuming auth failure.**
