# MEMORY.md - Working Memory

*Last updated: 2026-03-09 | Target: <4KB*

---

## 👤 Guillermo
- **Telegram:** @gginesta (1097408992) | **Discord:** 779143499655151646
- **Email:** guillermo.ginesta@gmail.com | **Mobile:** +852 5405 5953
- **Timezone:** HKT (GMT+8) — **ALWAYS think in HKT**
- **Style:** Casual, efficient, no fluff. Likes tables.

## 🖥️ Fleet
| Agent | URL | Model |
|-------|-----|-------|
| Molty 🦎 | ggvmolt.up.railway.app | Opus (primary) |
| Raphael 🔴 | ggv-raphael.up.railway.app | Sonnet |
| Leonardo 🔵 | leonardo-production.up.railway.app | Sonnet |

**Cron model:** Haiku direct | **Fallback:** Codex/GPT-5.2

## 🐢 Mission Control
- **URL:** https://tmnt-mission-control.vercel.app
- **API:** https://resilient-chinchilla-241.convex.site
- **Key:** Bearer 232e4ddf...c562
- **Endpoints:** GET `/api/tasks` (plural) | POST/PATCH `/api/task` (singular)

## 📅 Calendar
- **SA token:** `google-service-account.json` (no delegation)
- **Brinc busy block:** automatic in cal_create (enforced in code)
- **Full rules:** `memory/refs/standup-process.md`

## 📋 Active Projects
- **Cerebro:** www.meetcerebro.com — 10 customers in 12 weeks
- **WHOOP:** Research done, blocked on CLIENT_ID/SECRET from Guillermo. Notion spec: `31939dd6...`
- **MC Phase 3:** 13 tasks assigned, P2s first
- **ginesta.io:** Brief in Notion → https://www.notion.so/Personal-Website-Brief-www-ginesta-io-31a39dd69afd81cea223fbb9f2b2fe39. Waiting on Guillermo's content checklist.
- **April (agent):** Deployment pending. Notion pages: Setup Qs `31939dd6-9afd-8197` (Guillermo filled ✅), Steph Interview `31939dd6-9afd-81c5` (ready to share, Guillermo will send), Planning notes `31939dd6-9afd-8119`. Channels: WhatsApp (new SIM), Google Calendar + Shenanigans. Voice: yes.
- **Agent Performance Review:** P1 overnight work planned (PLAN-011). Design review process + add "Last updated by" headers to shared files. Trust/coaching model, not gatekeeping. Cascade to fleet after approval.
- **gws CLI:** v0.4.4 primary tool. Gmail ✅ Calendar ✅ Drive ✅ Docs ✅ Sheets ✅ (all 9 scopes). Config: `~/.config/gws/`. 11 skills at `/openclaw/skills/gws-*`. gog deprecated as fallback. GCP OAuth project: `847540297795` (separate from Gemini project `226575193033`).
- **Browser relay:** PARKED. Blocker: relay only included in full gateway, not `openclaw node run`. Node on GUILLERMO-DESKTOP is paired ✅. Resume when Guillermo wants Raphael to control Waalaxy.
- **Content/Pikachu:** Tamagotchi Trap posted (X + LinkedIn) 2026-03-05. Standing permission: generate kawaii robot images for future articles. Next article: "What AI Agents Actually Do For Me".

## ⏳ Pending (as of 2026-03-10)
- **Molty webchat:** Updated to v2026.3.8 (device auth bug fix). Testing now. NOT persistent on Railway yet — needs Docker image update if it works.
- **Molty webchat:** trustedProxies fix applied 22:12 HKT — pending confirmation it works
- **Raphael:** G4a test decks — awaiting Guillermo review. G2 exclusion matrix done (commit fb720fb). C1 recipe audit done.
- **Raphael:** A8 blocked — needs live Brinc proposal deck (Feb 2026 branding) from Guillermo
- **Raphael:** D2 (SlideCopier) blocked — needs Guillermo to review 15 source.pptx files on Windows (D:\Molty\brinc\module-library)
- **April:** Steph's interview page ready to share — Guillermo sends to Steph when ready
- **MC Phase 3 remaining:** D4 Memory Timeline, D2 Notification Prefs, [D6] Auth, [D1] Templates, [A4] Weekly Digest UI
- **MC Phase 3 done (Mar 7-8):** D3 Activity Analytics ✅ B4 Kanban DnD ✅ C1 Project Views ✅
- **Pikachu article:** "What AI Agents Actually Do For Me" — not started; TMNT Management article in MC review
- **Personal finance tasks:** Life insurance, car estimate, health insurance, joint accounts, last will, credit card — all need Guillermo to drive

## 📣 Standup Delivery (directive 2026-03-05)
Send daily standup to **both** webchat AND Telegram going forward.
- Webchat: primary (Guillermo at computer)
- Telegram: backup (convenient on phone)

## ⚠️ Core Rules
1. **PPEE:** Pause → Plan → Evaluate → Execute. One fix, not many.
2. **Don't claim done without citing file+line.**
3. **Mistakes → `memory/refs/mistake-tracker.md` immediately.**
4. **Code > docs.** If a rule can be enforced in code, do that.
5. **Before answering "what's the status of X"** — search Notion + plans/ + memory/ first. Never claim "nothing exists" without checking all sources.

## 📖 Reference Pointers
- Technical lessons → `memory/refs/lessons-learned.md`
- Standup/calendar rules → `memory/refs/standup-process.md`
- Code-enforced rules → `memory/refs/code-enforced-rules.md`
- Mistake tracking → `memory/refs/mistake-tracker.md`
- Infrastructure → `memory/refs/infrastructure.md`
- Credentials → `TOOLS.md`

---

*Full lesson archive: `memory/refs/lessons-learned.md`*

118. **Webchat→Telegram duplicate messages (Mar 6 2026):** When session is initiated via Telegram, then accessed via webchat, replies go to BOTH. Root cause: session "channel" is set to the initiating provider. Fix: start session from webchat first, or `/reset` in webchat. Metadata shows `channel: telegram, provider: webchat, surface: webchat` when this happens.
119. **gws auth export bug:** Encrypted credentials don't export properly. Workaround: manually copy `.encryption_key`, `accounts.json`, and `credentials.<base64-email>.enc` files from authenticated machine. Base64-encode the .enc file for transfer.
120. **gws CLI correct package:** `@googleworkspace/cli` (npm). NOT `@anthropic-ai/...`. Always verify package names before giving install commands.
121. **Silent crons need `delivery.mode: "none"` (Mar 6 2026):** Three crons were sending bare "DONE" to Telegram overnight (`13b4eaa0` Todoist Triage, `ad96575e` Pre-Standup Prep, `8991c017` Overnight Sync). Fix: set `delivery.mode: "none"` and change prompt endings to `HEARTBEAT_OK` not "Reply DONE". Always audit new crons for this before activating.
122. **Fleet outage 2026-03-09 ("Rough Monday"):** After v2026.3.7 update, Molty Discord, Raphael, Leonardo Discord, and Molty webchat all went down. Root cause: untested Python `startCommand` in Raphael used `json.load()` on JSONC config → container crash. Lesson: no fleet infra changes without Guillermo sign-off. REG-017/018 added.
123. **Working Molty webchat (controlUi) config:** `"dangerouslyAllowHostHeaderOriginFallback": true` + `"dangerouslyDisableDeviceAuth": true`. Also requires `gateway.trustedProxies: ["127.0.0.1", "100.64.0.0/10"]` — Railway's CGNAT range must be trusted or websocket connections fail silently. REG-021 added.
124. **Leonardo Discord token rotation + region fix (Mar 9 2026):** Discord bot token expired/rotated. After updating token, Discord was still blocked (Cloudflare 429 on Railway us-west2). Fix: change Railway region to Singapore → fresh IP → Discord online. REG-022 added.
125. **Policy: no fleet infrastructure changes without explicit Guillermo sign-off** — Guillermo's words after the Rough Monday outage: "Every time you try to update OpenClaw you break the fleet." Do not push version bumps, startCommands, or config patches fleet-wide without approval.
