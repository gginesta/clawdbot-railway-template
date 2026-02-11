# Post 2: Pokémon Sub-Agent Architecture

**Status:** ✅ Edited — Ready for review

---

## Thread

1/ Why I named my AI agents after TMNT characters (and how it actually helps with architecture). 🧵

2/ The team:
• Molty 🦎 — Coordinator, like Splinter. Routes tasks, manages memory
• Raphael 🔴 — Corporate/Brinc work. Aggressive on deadlines
• Leonardo (WIP) — Research & strategy
• Donatello (WIP) — Dev & technical

3/ Why personas matter: it's not just cute naming. Each agent has a distinct SOUL.md file defining its personality, priorities, and communication style.

4/ Molty is chill, asks clarifying questions, never rushes. Raphael is direct, deadline-focused, slightly impatient. The contrast is intentional.

5/ Inter-agent communication: they talk via Discord webhooks. Molty can ping Raphael: "Hey, Guillermo wants the Brinc deck by Friday." Raphael confirms or pushes back.

6/ Memory is per-agent. Each has its own workspace, MEMORY.md, daily logs. No shared context means no cross-contamination of tasks.

7/ The "council" pattern: for big decisions, I bring both agents into a thread. They debate, I decide. Two perspectives > one.

8/ Pro tip: start with ONE agent. Get it stable. Then add specialists. Growing the team too fast = chaos.

The TMNT theme keeps it fun. And fun systems get maintained. #AIAgents #BuildInPublic
