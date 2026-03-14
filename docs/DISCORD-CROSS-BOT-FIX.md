# Discord Cross-Bot Communication Fix

**Created:** 2026-03-15 by Molty 🦎  
**Ticket:** Todoist `6g8VRc2X7gRCfPrQ`  
**Problem:** "I dont have to constantly ping you to check each other's messages. Seems you all cannot see other bot messages."

---

## Root Cause

Discord bots **don't receive messages from other bots** by default. This is a Discord safety mechanism to prevent infinite loops.

Each TMNT agent is a separate Discord bot. When Raphael posts in `#brinc-general`, Molty won't see that message unless Molty's bot explicitly has bot message reception enabled.

---

## The Fix: `allowBots: "mentions"`

OpenClaw has an `allowBots` config option under `channels.discord`:

```json
{
  "channels": {
    "discord": {
      "allowBots": "mentions"
    }
  }
}
```

### Options:
| Value | Behavior | Risk |
|-------|----------|------|
| `false` (default) | Never respond to bot messages | No loops, but no cross-bot comms |
| `"mentions"` | ✅ Respond to bot messages that @mention you | Low loop risk |
| `true` | Respond to ALL bot messages | ⚠️ High loop risk |

**Set `"mentions"` — not `true`** (REG-027).

---

## Current Fleet Status

All agents should have `allowBots: "mentions"` if they want to see/respond to each other. Check each agent's current config:

```bash
# On each agent's container:
openclaw config get | grep allowBots
```

---

## Implementation Plan

### Option A: Mentions-based (recommended)
Each agent sets `allowBots: "mentions"` in their Discord config. Agents can then @mention each other directly in Discord channels.

**Example flow:**
- Guillermo asks Molty about Raphael's proposal status
- Molty @mentions Raphael in `#command-center`
- Raphael (with `allowBots: "mentions"`) sees the @mention and responds

### Option B: Agent-Link (already live — preferred for structured tasks)
For structured agent-to-agent tasks, use the existing Agent-Link v2 system (PLAN-015). This is already set up and doesn't require Discord visibility.

```bash
python3 /data/shared/scripts/agent-link-worker.py send raphael question "What's the status of the Brinc proposal?"
```

---

## Why Guillermo Has To Ping Agents

The actual issue isn't just `allowBots` — it's that:
1. **Molty doesn't monitor Raphael/Leonardo's channels** (by design — channel ownership)
2. **Agents can't ask each other questions without Agent-Link** (without `allowBots: "mentions"`)

### Real Fix:

**For task delegation:** Use Agent-Link v2 (already working).

**For Guillermo wanting to cc multiple agents:**
- Tag both agents in command-center (e.g. `<@Raphael> <@Molty> status?`)
- Both will respond because they monitor their own channels

**For agents monitoring each other's progress:**
- Overnight reports in `/data/shared/logs/` already serve this purpose
- Molty reads Raphael/Leonardo logs at 03:00 HKT and posts to #squad-updates

---

## What Doesn't Need Changing

Guillermo shouldn't need to relay messages between agents. The correct flow is:
1. **Guillermo → Molty** (in #command-center or webchat): "Tell Raphael X"
2. **Molty → Raphael** (via Agent-Link): structured message
3. **Raphael → Molty** (via Agent-Link or overnight log): response
4. **Molty → Guillermo**: summary

This is already working. The issue may be that:
- Guillermo isn't aware of the Agent-Link flow
- Or agents aren't using it proactively enough

---

## Config Change Required

For all agents to be able to respond to @mentions from other bots, add to each agent's OpenClaw config:

```json
"channels": {
  "discord": {
    "allowBots": "mentions"
  }
}
```

**Location:** `channels.discord.allowBots` at top level (NOT inside guilds config — REG-032).

**To apply:** Guillermo can set this via the OpenClaw setup page for each agent, or Molty can apply via gateway config patch when appropriate.

---

## Action Items for Guillermo

1. ✅ Agent-Link v2 already handles structured bot-to-bot messaging — Molty can reach Raphael/Leonardo directly
2. 🚧 For Discord @mentions between bots: need Guillermo to set `allowBots: "mentions"` on Raphael, Leonardo, April's configs (Molty can do Molty's own)
3. 📋 Alternatively: agents can just post status in #squad-updates for Guillermo to see (already happening via overnight logs)

---

## Recommendation

**Short term:** No config change needed. Agent-Link v2 already solves bot-to-bot communication. Overnight reports already consolidate all agent status.

**Medium term:** If Guillermo wants real-time cross-bot Discord visibility (e.g., Raphael replying to Molty in a shared channel), enable `allowBots: "mentions"` across all agents. Low risk, easy config change.

---

*Researched by Molty 🦎 | 2026-03-15 03:30 HKT*
