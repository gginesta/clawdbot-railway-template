# MEMORY.md - Long-Term Memory

*Last updated: 2026-02-15*

---

## 👤 Guillermo

- **Location:** Hong Kong (GMT+8) — **ALWAYS think in HKT!**
- **Telegram:** @gginesta (id: 1097408992)
- **Email:** guillermo.ginesta@gmail.com
- **Mobile:** +852 5405 5953
- **Discord:** 779143499655151646
- **Style:** Casual, efficient, no fluff. Likes tables. Not super technical but learns fast.
- **Travelling:** Cebu Feb 13-18, back HK Feb 19

## 📧 Email

| What | Value |
|------|-------|
| My email | ggv.molt@gmail.com |
| Guillermo's email | guillermo.ginesta@gmail.com |
| Script | `/data/workspace/scripts/gmail.sh` |
| **Status** | ⚠️ **BROKEN** — OAuth client disabled until Feb 19 |

**Rules:** TO=reply if relevant, CC=don't reply unless necessary, BCC=NEVER reply

---

## 🖥️ Infrastructure

### Agents
| Agent | URL | Status |
|-------|-----|--------|
| Molty 🦎 | ggvmolt.up.railway.app | ✅ Active |
| Raphael 🔴 | ggv-raphael.up.railway.app | ✅ Active |
| Leonardo 🔵 | leonardo-production.up.railway.app | ✅ Active |

### Key Config
- **OpenClaw version:** 2026.2.16 (commit `6244ef9`)
- **Primary model:** Claude Opus 4.6 | Fallbacks: Sonnet 4, GPT-5.2, Grok 3
- **Sub-agents:** Qwen Coder (cheap) or Flash (capable)
- **Cron model:** `openrouter/anthropic/claude-3.5-haiku` (Flash had issues)
- **Memory backend:** OpenAI `text-embedding-3-small` (switched from QMD 2026-02-17 21:00 HKT)
- **Architect pattern:** Only Molty indexes the shared vault (under `memory/vault/`). Other agents search only their own workspace.
- **Browser:** Brave headless (not Chromium — #3941 timeout bug)
- **Heartbeat:** 1h | Context pruning: cache-ttl 4h

### Webhooks (agent-to-agent)
- Token: `HSYgqkBANp8ChScOEs2bo09fQ2hnFw0lqW5tZjOPmvkrCffmcuce6aVyF7p1vfTU`
- Must include `"sessionKey": "agent:main:main"`
- ⚠️ Raphael/Leonardo need `hooks.allowRequestSessionKey: true` (breaking change in 2026.2.12)

### Todoist (API v1)
| Project | ID |
|---------|-----|
| Inbox | 6M5rpCXmg7x7RC2Q |
| Personal | 6M5rpGfw5jR9Qg9R |
| Brinc | 6M5rpGgV6q865hrX |
| Mana Capital | 6Rr9p6MxWHFwHXGC |
| Molty's Den | 6fwH32grqrCJF23R |
| Ideas | 6fx5GV7Q93Hp4QgM |

⚠️ Todoist priority is INVERTED: `priority=4` = P1 display!

### Notion
- **API Key:** `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`
- **Mission Control:** https://www.notion.so/Molty-s-Mission-Control-2fa39dd69afd80be89dae91e20d30a38
- **Standup DB:** `2fe39dd69afd81f189f7e58925dad602`
- **Content Pipeline DB:** `30739dd6-9afd-8131-8f2d-e2ad52fd147c`

### Syncthing
- Molty, Raphael, Leonardo, Guillermo-PC all connected
- Shared folders: `shared`, `mv-daily`, `mv-projects`, `mv-resources`, `mv-squad`, `mv-people`

### Backup
- **Cron:** Daily 00:30 HKT (backup → git clean → update → announce to Discord)
- **Script:** `/data/workspace/backups/backup.sh` | Keeps last 5
- **GitHub:** https://github.com/gginesta/moltybackup (private)

---

## 🐢 TMNT Squad

| Agent | Role | Emoji | Status |
|-------|------|-------|--------|
| Molty | Coordinator | 🦎 | ✅ Active |
| Raphael | Brinc Corporate | 🔴 | ✅ Active |
| Leonardo | Launchpad/Venture | 🔵 | ✅ Active (GPT-5.2) |
| Donatello | Research/Incubation | 🟣 | ⏳ Pending |
| April | Personal Assistant | 📰 | ⏳ Pending |
| Michelangelo | Mana Capital | 🟠 | ⏳ Pending |

### Sub-Agent Operating Standard
- **Doc:** `/data/workspace/docs/SUB-AGENT-OPERATING-STANDARD.md`
- **Themes:** Pokemon (Molty), Mario (Raphael), Star Wars (Leonardo)
- **Notion:** `30839dd6-9afd-8167-9201-d52dfcacc5f8`

### Pikachu ⚡ (Content/Marketing)
- Content Hub: https://www.notion.so/Pikachu-Content-Hub-30039dd69afd81308861fc93bee4dfae
- Content Pipeline DB with 12 posts (Post 1 published on X)
- X account: @Molton_Sanchez (posting blocked by bot detection)

---

## 📋 Daily Standup (5PM HKT)

**4-step process:**
1. Process Todoist inbox (rewrite, estimate, categorize, prioritize)
2. Create Notion standup page (callout + Task Review DB + priorities + blockers)
3. After Guillermo reviews → process decisions + create calendar time blocks
4. Send Telegram summary with Notion link

**Cron:** `bdb28765-f508-4271-a04d-9408d39f49fd`

---

## 🔑 Blocked Items

- **Google Calendar + Gmail:** OAuth client disabled. Fix Feb 19 (Guillermo returns to HK, has 2FA phone)
- **Strategy:** New GCP service account under guillermo.ginesta@gmail.com for Calendar (no token expiry)

---

## 📝 Key Lessons (Curated)

1. **Backup before update — ALWAYS.** Non-negotiable.
2. **Think in HKT.** System clock is UTC but Guillermo is HKT.
3. **Do it yourself first.** Don't give instructions when you have access.
4. **Sub-agents can't exec.** last30days, gmail.sh etc must run in main session.
5. **Use x-fetch for Twitter URLs.** Pipeline: fxtwitter API → Jina reader → Grok. No auth needed. x-reader only for browsing/screenshots.
6. **Railway env vars trigger redeploy.** Use `--skip-deploys` flag.
7. **Cron delivery needs explicit `to` field.** Always include `"to": "1097408992"`.
8. **Grok is unreliable as sub-agent.** Use Sonnet or Flash for execution tasks.
9. **Never dump raw Todoist tasks into standup.** Process every one.
10. **Perplexity Sonar has NO tool use.** Search/chat only.
11. **Files first, config second, boot third** for agent deployment.
12. **Never brute-force config changes.** Research first, stop after first failure.
13. **Context overflow = death.** Never read entire log files. Use tail/grep/limit.
14. **Persist plans to files immediately.** Context pruning will erase chat-only plans.
15. **Check shared files before proposing new systems.** Things may already exist.
16. **Read Discord messages before responding.** Always `message read` the last 10-20 msgs first. Acknowledge what others said. Post conclusions, not internal process. One clean message, not stream-of-consciousness.

17. **Cron jobs MUST use explicit model IDs, never aliases.** The `flash` alias routes to `google/gemini-2.5-flash` (direct API, 5 req/min free tier) — NOT OpenRouter. For cron reliability, use `glm5` (`openrouter/z-ai/glm-5`) which has no rate limits or OAuth expiry issues.
18. **One change per cycle.** Make one change → test → proceed or rollback. No parallel fixes.
19. **One owner per incident.** Everyone else supplies evidence, not competing fixes.
20. **STOP means STOP.** When Guillermo says stop, all agents cease and answer questions only.
21. **No risky change without a rollback target.** Name the backup file/config hash/timestamp first.
22. **Cron prompts must say "Do NOT post to any channel; return plain text only."** Delivery handles posting.
23. **Cron delivery.to must use `channel:<discord_id>` format.** Never raw IDs.
24. **Maintenance runs in isolated sessions only.** Never leak tool output into Telegram/webchat.
25. **Declare blast radius up front.** State if change affects one agent, one surface, or fleet-wide.
26. **No mixed objectives during incidents.** Fix reliability first, improvements after incident is closed.
27. **Before restart: confirm active runs = 0** or wait for drain. Don't force-restart repeatedly.
28. **Model allowlist ≠ provider models.** `agents.defaults.models` and `models.providers.*.models` are separate. Both must exist or "model not allowed" errors.
29. **Pushing to shared Railway template repo triggers redeployments for ALL agents.** Use a staging branch or coordinate timing. Don't push to main and then get surprised when you go down.
30. **Always check XDG paths for OpenClaw-managed QMD.** Default `qmd status` shows empty index. Real index at `~/.openclaw/agents/<id>/qmd/xdg-cache/qmd/index.sqlite`.
31. **QMD hybrid search needs ~6GB RAM.** Reranker + query expansion models OOM on Railway. Not viable until lighter models ship.
32. **OpenClaw builtin only indexes `MEMORY.md` + `memory/**/*.md`.** `extraPaths` is QMD-only. To index external files, put them under `memory/`.
33. **Evaluate before brute-forcing.** PPEE exists for a reason.
34. **Simpler is almost always better.** 3 lines of config beats a complex multi-system architecture.

---

*Daily logs: `memory/YYYY-MM-DD.md` | Archive: `memory/archive/`*
