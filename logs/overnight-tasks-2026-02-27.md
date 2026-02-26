# Overnight Tasks — 2026-02-27

## ✅ Completed (1)
- **Fix Discord read access for Molty** → [Notion: 🔍 Discord Read Access Investigation — Feb 27 2026](https://www.notion.so/Discord-Read-Access-Investigation-Feb-27-2026-31339dd69afd81d185ebd881f9ee3734)

## ⏭️ Flagged — needs input (0)

## ❌ Failed (0)

---

## Investigation Summary

**Task:** Fix Discord read access for Molty (message tool action enum restricted to send only)

**Root Cause Found:** The message tool action enum is **dynamically scoped to the current session channel** at startup. When Molty runs from Telegram (cron/overnight sessions), `resolveMessageToolSchemaActions()` calls `listChannelSupportedActions({ channel: "telegram" })` — which only returns Telegram actions. Discord actions (`read`, `search`) are never added to the enum.

- **Config is fine:** `channels.discord.actions.messages=true` and `search=true` are both set correctly in `/data/.openclaw/openclaw.json`
- **The scoping is intentional:** Code in `src/agents/tools/message-tool.ts` explicitly scopes to `currentChannelProvider` when present

**Key files:**
- `src/agents/tools/message-tool.ts` → `resolveMessageToolSchemaActions()` (line ~448)
- `src/channels/plugins/actions/discord.ts` → `discordMessageActions.listActions()`
- `src/channels/plugins/actions/telegram.ts` → Telegram's `listActions()`

**Recommended fix options:**
1. **Use Discord-bound sessions** for Discord read tasks (no code change needed — works today from #command-center)
2. **Spawn Discord sub-agent** from cron when Discord reads are needed
3. **OpenClaw feature request:** `tools.message.includeAllChannelActions: true` config to bypass per-channel scoping
