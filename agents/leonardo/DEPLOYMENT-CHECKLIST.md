# Leonardo Deployment Checklist

## ✅ Completed
- [x] Railway project created (ID: `56793cec-6283-4af0-ae1f-ac10ec622e58`)
- [x] Railway URL: `https://leonardo-production.up.railway.app`
- [x] Volume mounted at `/data`
- [x] Service linked to template repo (`gginesta/clawdbot-railway-template`)
- [x] TZ=Asia/Hong_Kong set
- [x] Discord category "🚀 Launchpad" created (ID: `1470919402605121761`)
- [x] Discord #launchpad-general created (ID: `1470919420791619758`)
- [x] Discord #launchpad-private created (ID: `1470919437975814226`)
- [x] Workspace files scaffolded (SOUL, IDENTITY, USER, AGENTS, MEMORY, TOOLS, HEARTBEAT, PRIORITY_BRIEFING)
- [x] Gateway config: full config pushed (models, Discord, Telegram, hooks, memory, browser)
- [x] Discord bot token set + bot invited to TMNT Squad server
- [x] Discord Message Content Intent enabled
- [x] Telegram bot token set (8297252066)
- [x] Anthropic OAuth configured
- [x] API keys set in Railway env vars (Brave, Gemini, Google, Notion, OpenAI, OpenRouter, XAI)
- [x] Gateway running (Health OK)
- [x] Webchat accessible (dangerouslyDisableDeviceAuth: true)
- [x] Workspace files sent via webhook (7 files + PRIORITY_BRIEFING)
- [x] ownerAllowFrom configured (Guillermo only)
- [x] Channel permissions: launchpad-general, launchpad-private, command-center, squad-updates

## ⏳ In Progress
- [ ] Verify Leonardo wrote all workspace files correctly
- [ ] Telegram pairing (Guillermo needs to message the bot)

## 🔜 Remaining
- [ ] Set up Codex OAuth (GPT-5.3 as primary model — currently on Claude Opus)
- [ ] Set up Syncthing (connect to Molty + Raphael + Guillermo)
- [ ] Set up agent-to-agent webhooks (update Leonardo's TOOLS.md with webhook URLs)
- [ ] Configure Notion workspace
- [ ] Set up Tailscale (then disable dangerouslyDisableDeviceAuth)
- [ ] Announce deployment in #squad-updates
- [ ] Remove SETUP_PASSWORD env var from Railway
- [ ] Install skills (email, todoist, notion, etc.)

## 🔑 Key Config
| Item | Value |
|------|-------|
| Gateway token | `27190324b3905f13c2f0fb3310d35afe6a09d9dcefe475b1dfacb759f59bd99f` |
| Hooks token | `b990098bbdbcefafbd7b8fb65e97e9a18baae8b4ee1cdcfc2d9b95c80fa52b87` |
| Discord bot ID | `1470919061763522570` |
| Telegram bot token | `8297252066:AAGpC5oCmsrbBgkoMux11i7s_4DYzjiDBw4` |
| Primary model | Claude Opus 4.6 (temporary) → GPT-5.3 (target) |
| Setup password | `leo-setup-temp-2026` (remove after setup complete) |
