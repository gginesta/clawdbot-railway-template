# Discord Message Ordering Fix

**Date:** 2026-02-07
**Issue:** Discord messages arriving out of order when agent sends multiple blocks
**Applies to:** ALL OpenClaw agents with Discord enabled

## Root Cause

By default, OpenClaw doesn't enable block streaming for non-Telegram channels. When the agent produces a long response that gets chunked into multiple Discord messages, they can arrive out of order due to API race conditions.

## Fix (config.patch)

```json
{
  "channels": {
    "discord": {
      "blockStreaming": true,
      "blockStreamingCoalesce": {
        "idleMs": 1500,
        "minChars": 1500
      }
    }
  },
  "agents": {
    "defaults": {
      "humanDelay": {
        "mode": "natural"
      }
    }
  }
}
```

## What Each Setting Does

| Setting | Value | Effect |
|---------|-------|--------|
| `blockStreaming` | `true` | Enables block streaming for Discord (off by default for non-Telegram) |
| `blockStreamingCoalesce.idleMs` | `1500` | Waits 1.5s of idle time before sending, allowing blocks to merge |
| `blockStreamingCoalesce.minChars` | `1500` | Minimum chars before sending a coalesced block |
| `humanDelay.mode` | `"natural"` | Adds 800-2500ms randomized pause between block replies |

## Status

- ✅ Molty — applied 2026-02-07
- ⏳ Raphael — sent via webhook, pending confirmation
- ⏳ Future team leads — apply on deployment

## Notes

- This is a **mandatory config** for all agents with Discord enabled
- Add to deployment checklist for new agents
