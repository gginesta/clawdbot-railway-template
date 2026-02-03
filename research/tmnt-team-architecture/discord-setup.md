# Discord Server Setup Guide - Molty HQ

## Step 1: Create the Server

1. Open Discord → Add a Server → Create My Own → For me and my friends
2. Name: **Molty HQ** (or your preference)
3. Note the **Server ID** (Enable Developer Mode in Settings → Advanced, then right-click server → Copy Server ID)

## Step 2: Create Categories & Channels

### Category: 📋 MANAGEMENT
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #command-center | Strategy, coordination | Molty |
| #team-standup | Daily agent summaries | Molty (all post here) |
| #escalations | Cross-project issues | Molty |

### Category: 🔴 BRINC
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #brinc-general | Main Brinc discussion | Raphael |
| #brinc-deals | Deal pipeline | Raphael |
| #brinc-squad | Employee sub-agents | Raphael |

### Category: 🔵 CEREBRO
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #cerebro-general | Main Cerebro discussion | Leonardo |
| #cerebro-pipeline | Startup pipeline | Leonardo |
| #cerebro-squad | Employee sub-agents | Leonardo |

### Category: 🟠 MANA
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #mana-general | Investment discussions | Mikey (sub-agent) |
| #mana-deals | Deal analysis | Mikey |

### Category: 🟣 TINKER
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #tinker-lab | Research discussions | Donatello (sub-agent) |
| #tinker-experiments | Experiment logs | Donatello |

### Category: 📰 PERSONAL
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #personal | Life admin | April (sub-agent) |

### Category: 🛠️ SYSTEM
| Channel | Purpose | Bound Agent |
|---------|---------|-------------|
| #bot-logs | Activity logs | None (read-only) |
| #errors | Error notifications | None (read-only) |

## Step 3: Create Discord Bot

1. Go to https://discord.com/developers/applications
2. New Application → Name: "Molty Bot"
3. Go to Bot tab → Add Bot
4. Enable these Intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent
5. Copy the **Bot Token** (keep secret!)
6. Go to OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Read Message History`, `Add Reactions`, `Embed Links`, `Attach Files`, `Use Slash Commands`
7. Copy the generated URL and open it to invite the bot to your server

## Step 4: Get Channel IDs

For each channel you want to bind:
1. Right-click the channel → Copy Channel ID
2. Add to config template with the agent binding

## Step 5: Configure OpenClaw

Add to your `openclaw.json`:

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN_HERE"
    }
  },
  "bindings": [
    { "agentId": "molty", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "COMMAND_CENTER_ID" } } },
    { "agentId": "raphael", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "BRINC_GENERAL_ID" } } },
    { "agentId": "leonardo", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "CEREBRO_GENERAL_ID" } } },
    { "agentId": "molty", "match": { "channel": "discord" } }  // Fallback
  ]
}
```

## Step 6: Test

1. Restart OpenClaw gateway
2. Post a message in #command-center → should get Molty
3. Post in #brinc-general → should get Raphael
4. Post in an unbound channel → should fall back to Molty

## Notes

- **One bot, multiple agents:** The same Discord bot can route to different agents based on channel
- **Mention behavior:** Set `mentionRequired: false` in dedicated channels so agents respond without @mention
- **DM routing:** DMs go to the default agent (Molty) unless you set up per-user bindings

---

*Setup complete! Your agents now have their own Discord channels.*
