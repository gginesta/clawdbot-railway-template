# Webhook Policy — ALL AGENTS

**Updated: 2026-02-07 by Guillermo (via Molty)**

## ⛔ DO NOT send routine updates via webhook to other agents

Webhooks to `/hooks/agent` route to the receiving agent's **main session**, which forwards to **Guillermo's personal Telegram**. This means every webhook = a Telegram notification to Guillermo.

### Allowed webhook uses:
- 🆘 Agent is DOWN and cannot reach Discord
- ❓ Direct question that requires another agent's response
- 🔐 Security incidents

### NOT allowed:
- ❌ Deploy confirmations
- ❌ Build status updates  
- ❌ Bug fix notifications
- ❌ Routine status reports

### Where routine updates go:
→ **Discord channels** (each agent's designated channel)
→ This is Guillermo's explicit directive, repeated multiple times on Feb 7, 2026.
