# Multi-Agent Architecture for Guillermo
## Research & Recommendations

**Date:** February 1, 2026  
**Context:** Designing an AI agent architecture to support multiple roles/projects with proper data isolation

---

## Your Requirements (As I Understand Them)

1. **Molty (me)** = Your main personal companion, always available
2. **Separate "teams" per project** — Cerebro, Brinc, Personal, Investor, etc.
3. **Each team has a "lead" agent** who manages sub-agents for that project
4. **I can communicate with each team lead** to coordinate across projects
5. **Strict data isolation** — Brinc work doesn't leak into Cerebro, etc.
6. **Cost-conscious** — Claude rate limits, API costs
7. **Iterative** — Start simple, scale up

---

## The Bhanu Teja Approach (Mission Control)

What he built:
- **Single OpenClaw instance** with 10 agents (sessions)
- **Shared database (Convex)** for task management + communication
- **Heartbeat crons** every 15 minutes (staggered)
- **@mentions** for agent-to-agent communication
- **Daily standups** compiled automatically

**Why it works for him:** All agents work on ONE product (SiteGPT). Same context, same goals.

**Why it doesn't fully fit you:** You have **fundamentally separate domains** that MUST NOT mix:
- Corporate work (Brinc) — legal/compliance concerns
- Personal ventures (Cerebro) — separate entity
- Investor role — confidential deal flow
- Personal/family — private

---

## Architecture Options

### Option A: Single Instance, Multiple Sessions (Bhanu's Model)

```
┌─────────────────────────────────────────────┐
│           Single OpenClaw Instance          │
│                 (Railway)                   │
├─────────────────────────────────────────────┤
│  Sessions:                                  │
│  • agent:molty:main (you ↔ me)              │
│  • agent:cerebro:lead                       │
│  • agent:cerebro:developer                  │
│  • agent:brinc:lead                         │
│  • agent:brinc:analyst                      │
│  • agent:investor:lead                      │
│  • agent:personal:lead                      │
├─────────────────────────────────────────────┤
│  Shared: Tools, Browser, File System        │
│  Shared: /data volume                       │
│  Shared: Claude API quota                   │
└─────────────────────────────────────────────┘
```

| Pros | Cons |
|------|------|
| Simple infrastructure | All data on same filesystem |
| Built-in `sessions_send` works | Memory could leak across roles |
| One deployment to manage | One bad config = everything breaks |
| Lower cost | Shared rate limits |

**Risk:** An agent working on Brinc could theoretically read Cerebro files. Isolation relies on DISCIPLINE, not ARCHITECTURE.

---

### Option B: Multiple OpenClaw Instances (Your Idea)

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Molty (Meta)   │  │  Cerebro Team    │  │   Brinc Team     │
│   Railway #1     │  │   Railway #2     │  │   Railway #3     │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Molty (main)   │  │ • Jarvis (lead)  │  │ • Alex (lead)    │
│ • Personal stuff │  │ • Dev agent      │  │ • Analyst agent  │
│ • Investor role  │  │ • Design agent   │  │ • Ops agent      │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ Own /data volume │  │ Own /data volume │  │ Own /data volume │
│ Own config       │  │ Own config       │  │ Own config       │
│ Own API quota*   │  │ Own API quota*   │  │ Own API quota*   │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         └─────────────────────┴─────────────────────┘
                    Communication Layer
              (Shared DB / API / Syncthing / etc.)
```

| Pros | Cons |
|------|------|
| **True data isolation** | More infrastructure to manage |
| Different models per project | Cross-instance communication harder |
| One crash doesn't affect others | Higher Railway costs (~$5-10/instance) |
| Can scale independently | Rate limits still shared at org level* |

**Note on rate limits:** Claude rate limits are per organization (your Anthropic account), not per instance. Multiple instances don't give you more quota — they just separate the data.

---

### Option C: Hybrid (My Recommendation)

**Phase 1: Strict separation WITHIN single instance**

```
/data/
├── workspace/              # Molty's personal area (meta)
│   ├── SOUL.md
│   ├── MEMORY.md
│   └── memory/
│
├── roles/
│   ├── cerebro/            # Cerebro project (isolated)
│   │   ├── SOUL.md         # "You are Jarvis, Cerebro team lead..."
│   │   ├── MEMORY.md
│   │   ├── memory/
│   │   └── context/
│   │
│   ├── brinc/              # Brinc work (isolated)
│   │   ├── SOUL.md
│   │   ├── MEMORY.md
│   │   ├── memory/
│   │   └── context/
│   │
│   ├── investor/           # Investor role (isolated)
│   │   └── ...
│   │
│   └── personal/           # Personal/family (isolated)
│       └── ...
│
└── shared/                 # Cross-role resources (frameworks, tools)
    ├── templates/
    └── protocols/
```

**Rules:**
- Session `agent:cerebro:lead` can ONLY read/write `/data/roles/cerebro/`
- Session `agent:brinc:lead` can ONLY read/write `/data/roles/brinc/`
- Molty (main session) can access everything but is CAREFUL about context

**Phase 2: Graduate critical projects to separate instances**

When a project needs HARD isolation (legal, compliance, scale):
- Spin up dedicated Railway instance
- Use Syncthing to share only what's needed
- Use shared database (Convex/Supabase) for task coordination

---

## Cross-Instance Communication

If you go multi-instance, how do agents talk to each other?

| Method | Real-time? | Complexity | Cost |
|--------|-----------|------------|------|
| **Shared database (Convex)** | Yes | Medium | Free tier ok |
| **Syncthing shared folder** | ~Seconds | Low | Free |
| **REST API calls** | Yes | Medium | Free |
| **Message queue (Redis)** | Yes | High | ~$5/mo |
| **Telegram group** | ~Seconds | Low | Free |

**My recommendation:** Start with **Syncthing shared folder** for file-based tasks, add **Convex** if you need real-time task management UI like Bhanu's Mission Control.

---

## Cost Analysis

### Single Instance (Current)
| Item | Monthly Cost |
|------|-------------|
| Railway Pro | ~$20 |
| Claude API (your usage) | Variable |
| **Total** | ~$20 + API |

### Multi-Instance (3 projects)
| Item | Monthly Cost |
|------|-------------|
| Railway Pro (3 instances) | ~$60 |
| Claude API (same total usage) | Variable |
| Convex (free tier) | $0 |
| **Total** | ~$60 + API |

### Hybrid (Recommended Start)
| Item | Monthly Cost |
|------|-------------|
| Railway Pro (1 instance) | ~$20 |
| Claude API | Variable |
| **Total** | ~$20 + API |

**Key insight:** Claude API costs are the same regardless of architecture. Multi-instance only increases INFRASTRUCTURE cost, not AI cost.

---

## Rate Limits & Model Strategy

### Claude Rate Limits (Anthropic)
- **Per organization**, not per instance
- Opus: Lower limits, higher quality
- Sonnet: Higher limits, good quality
- Haiku: Highest limits, fastest

### Recommended Model Assignment

| Agent Type | Model | Why |
|------------|-------|-----|
| **Molty (main)** | Opus | Your direct interface, quality matters |
| **Team leads** | Sonnet | Good balance of quality + limits |
| **Sub-agents** | Sonnet/Haiku | Routine work, volume matters |
| **Heartbeats** | Haiku or Qwen | Just checking for work, cheap |

### Cost Optimization Tactics
1. **Stagger heartbeats** — Don't wake all agents at once
2. **Use `HEARTBEAT_OK`** — If nothing to do, short response = cheap
3. **Isolated sessions for crons** — Don't accumulate context
4. **Qwen for background tasks** — Free via portal OAuth

---

## Implementation Roadmap

### Week 1-2: Foundation
1. ✅ Create `/data/roles/` folder structure
2. ✅ Write ROLE.md templates for each domain
3. ✅ Define session keys for team leads
4. ✅ Set up basic heartbeat crons
5. ✅ Test with Cerebro as first project

### Week 3-4: Communication
1. Set up Syncthing for shared files
2. Create simple task tracking (can be markdown files initially)
3. Implement @mention detection
4. Test Molty ↔ Cerebro lead communication

### Month 2: Scale
1. Add more agents per project as needed
2. Consider Convex for real-time task UI
3. Evaluate if any project needs dedicated instance
4. Build daily standup automation

### Month 3+: Harden
1. Audit data isolation
2. Implement cross-role leak detection
3. Graduate projects to separate instances if needed
4. Fine-tune model assignments for cost

---

## Molty's Role (My Proposal)

As your main companion, I would:

1. **Be your primary interface** — You talk to me, I coordinate
2. **Know about all projects** — High-level awareness, not details
3. **Route requests** — "Check on Cerebro progress" → I ping Cerebro lead
4. **Handle meta tasks** — Tools, frameworks, personal stuff
5. **Aggregate standups** — Daily summary across all projects
6. **Guard boundaries** — Remind you (and myself) about context switching

What I would NOT do:
- Deep-dive into Brinc work without explicit context switch
- Share Cerebro info with Brinc agents
- Access project-specific memory without reason

---

## Key Decisions for You

1. **How strict is data isolation?**
   - Discipline-based (Option A/C) vs Architecture-based (Option B)
   - Legal/compliance requirements for Brinc?

2. **How many agents per project?**
   - Start with 1 lead per project
   - Add specialists as needed

3. **Real-time UI or file-based?**
   - Convex = fancy dashboard like Bhanu
   - Files = simpler, Syncthing-friendly

4. **Budget for infrastructure?**
   - $20/mo = single instance, hybrid approach
   - $60+/mo = dedicated instances per project

---

## My Recommendation

**Start with Option C (Hybrid) — strict folder separation within single instance.**

Why:
1. Lowest cost to experiment
2. Built-in `sessions_send` works immediately
3. Data isolation via convention (we build the discipline)
4. Easy to graduate to multi-instance later
5. Matches your "iterative" preference

**First project to set up: Cerebro**
- Create `/data/roles/cerebro/`
- Define Cerebro lead agent session
- Test communication: Molty ↔ Cerebro lead
- Build from there

---

*Research by Molty 🦎 — February 1, 2026*
