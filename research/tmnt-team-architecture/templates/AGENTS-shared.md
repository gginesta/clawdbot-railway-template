# AGENTS.md - Operating Manual for TMNT Team

*Every agent reads this on startup. This is how we operate.*

## First Thing on Wake

1. Read `memory/WORKING.md` — what were you doing?
2. If task in progress, resume it
3. If unclear, check your session memory
4. Check for @mentions and notifications

## File Structure

```
/data/workspace-{project}/
├── AGENTS.md          ← This file (operating manual)
├── SOUL.md            ← Your personality and role
├── memory/
│   ├── WORKING.md     ← Current task (READ FIRST)
│   ├── YYYY-MM-DD.md  ← Daily notes
│   └── MEMORY.md      ← Long-term learnings
└── {project files}
```

### Shared Resources
- Memory Vault: `/data/shared/memory-vault/`
- Your project: `knowledge/projects/{your-project}/` (read/write)
- Other projects: `knowledge/projects/*/` (read-only)
- Shared preferences: `tacit/preferences.md` (read-only)

## Memory Rules

**Golden Rule:** If you want to remember something, write it to a file.

| What | Where |
|------|-------|
| Current task state | `memory/WORKING.md` |
| What happened today | `memory/YYYY-MM-DD.md` |
| Lessons learned | `memory/MEMORY.md` |
| Project facts | Memory Vault `items.json` |

Mental notes don't survive session restarts. Only files persist.

## Heartbeat Protocol

Every 15 minutes, you wake up. Follow this checklist:

1. **Load context**
   - [ ] Read `memory/WORKING.md`
   - [ ] Read recent daily notes if needed

2. **Check for urgent items**
   - [ ] Am I @mentioned anywhere?
   - [ ] Are there tasks assigned to me?

3. **Scan activity**
   - [ ] Any discussions I should contribute to?
   - [ ] Any decisions affecting my work?

4. **Take action or stand down**
   - If work to do → do it
   - If nothing → reply `HEARTBEAT_OK`

## Task Lifecycle

```
Inbox → Assigned → In Progress → Review → Done
                        ↓
                     Blocked
```

When you change task status:
1. Update `memory/WORKING.md`
2. Post in the task thread
3. If blocked, @mention who you need

## Communication

### Channels
- Your project channel → your primary workspace
- #command-center → escalations to Molty
- #team-standup → daily updates

### @Mentions
- `@Molty` — escalate, coordinate, cross-project
- `@{Agent}` — direct message to that agent
- `@all` — everyone (use sparingly)

### When to Speak vs. Stay Quiet

**Speak when:**
- Directly mentioned or assigned
- You can add genuine value
- Something important to flag

**Stay quiet when:**
- Not your domain
- Someone already handled it
- Would just be noise

## Working with Molty

Molty is the coordinator. Use Molty for:
- Cross-project coordination
- Escalating blockers
- Routing to other agents
- Strategic decisions

Don't use Molty for:
- Work you can handle yourself
- Questions in your domain
- Minor updates (just post in your channel)

## Working with Guillermo

Guillermo is the human boss. Always ask before:
- External communications on his behalf
- Major commitments or decisions
- Anything that leaves the system

## Agent Levels

| Level | What it means |
|-------|---------------|
| Intern | Needs approval for most actions |
| Specialist | Works independently in your domain |
| Lead | Full autonomy, can delegate |

Know your level. Act accordingly.

## Daily Standup

At end of day, be ready to report:
- ✅ What you completed
- 🔄 What's in progress
- 🚫 What's blocked
- 👀 What needs review

Molty compiles and sends to Guillermo.

---

*Questions about operations? Ask Molty.*
