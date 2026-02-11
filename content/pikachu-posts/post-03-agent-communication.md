# Post 3: Agent-to-Agent Communication

**Status:** ✅ Edited — Ready for review

---

## Thread

1/ How do you make AI agents talk to each other without everything turning into chaos? Here's my setup. 🧵

2/ The problem: if agents share a context window, they confuse each other's tasks. If they're completely isolated, they can't coordinate.

3/ My solution: Discord as the message bus. Each agent has its own channel + can ping others via webhooks.

4/ Channel ownership:
• #command-center → Molty owns, others @mention only
• #brinc-marketing → Raphael owns
• #squad-decisions → Shared forum for cross-agent topics

5/ Message format matters. When Molty pings Raphael, it's structured:
"@Raphael — Task: Review deck | Deadline: Friday | Context: [link] | Priority: P1"

6/ Agents can also use shared Notion databases. The Posting Queue DB is readable by both. But WRITE access is controlled—only one agent "owns" each record.

7/ Async by default. No agent waits for another. They post, move on, check replies on heartbeat cycles (every 30 min).

8/ The key insight: treat agent-to-agent comms like microservices. Clear contracts, explicit payloads, no implicit state.

It's not sexy. It's reliable. #AIAgents #BuildInPublic
