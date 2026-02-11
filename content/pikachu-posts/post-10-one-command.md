# Post 10: One-Command Agent Creation

**Status:** ✅ Edited — Ready for review (based on Revised Feb 9 content)

---

## Thread

1/ Creating a new AI agent should be as easy as creating a new folder. With OpenClaw, it nearly is. 🧵

2/ The old way: set up a new project, configure APIs, write orchestration code, handle memory, deploy infrastructure. Days of work.

3/ The OpenClaw way:
```bash
openclaw agent create raphael
```

That's it. New agent, ready to customize.

4/ What that command does:
• Creates workspace folder with standard structure
• Generates SOUL.md template (agent identity)
• Sets up MEMORY.md, TOOLS.md, AGENTS.md
• Configures default model and channel bindings

5/ Customize in markdown. SOUL.md defines personality:
```markdown
You are Raphael 🔴, the corporate specialist.
Tone: Direct, deadline-focused.
Focus: Brinc deal flow, proposals, investor comms.
```

6/ Deploy with:
```bash
openclaw deploy raphael --target railway
```

Agent goes live. Starts processing messages.

7/ The magic: agents are mostly configuration, not code. You describe WHAT you want in plain English. OpenClaw handles HOW.

8/ Time to first working agent: ~30 minutes if you know what you want. Most of that is thinking, not typing.

One command to create. One command to deploy. That's the goal. #OpenClaw #AIAgents
