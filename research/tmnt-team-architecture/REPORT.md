# TMNT Team Architecture Report
## Multi-Agent AI Team Design for Guillermo's Projects

*Generated: 2026-02-03 | Author: Molty 🦎*

---

## Executive Summary

This report analyzes architecture options for deploying a multi-agent AI team (TMNT structure) with true isolation, cross-agent communication, and cost efficiency. Based on OpenClaw's multi-agent capabilities and Bhanu Teja's "Mission Control" approach, we recommend a **hybrid deployment** starting on a single Railway instance with full agent isolation, with a clear path to multi-instance deployment as complexity grows.

---

## Table of Contents

1. [Inspiration: Bhanu Teja's Mission Control](#1-inspiration-bhanu-tejas-mission-control)
2. [Architecture Options](#2-architecture-options)
3. [Recommended Architecture](#3-recommended-architecture)
4. [Deployment Strategy](#4-deployment-strategy)
5. [Cost Analysis](#5-cost-analysis)
6. [Memory & Context Sharing](#6-memory--context-sharing)
7. [Communication Structure (Discord/Slack)](#7-communication-structure)
8. [Team Structure & Personalities](#8-team-structure--personalities)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Risk Mitigation](#10-risk-mitigation)

---

## 1. Inspiration: Bhanu Teja's Mission Control

Bhanu Teja (founder of SiteGPT) built a system where **10 AI agents work together like a real team**:

### Key Principles from His Approach:
- **Departmental Structure**: Agents organized by function (Engineering, Marketing, Sales, etc.)
- **Persistent Memory**: Each agent reads `AGENTS.md` on startup — the "operating manual"
- **Isolation + Coordination**: Agents make independent decisions but share a workspace
- **Configuration-driven**: JSON config defines models, channels, tools, prompts per agent
- **Hierarchy**: CEO agent coordinates, department heads execute, specialists contribute

### What Makes It Work:
1. **Clear responsibilities** — each agent knows its domain
2. **Shared context files** — `AGENTS.md`, `SOUL.md`, workspace files
3. **Communication channels** — Slack/Discord for organized discussions
4. **Human oversight** — CEO (human) + coordinator agent review key decisions

---

## 2. Architecture Options

### Option A: Single Instance, Multi-Agent (Same Gateway)

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Instance                      │
│  ┌─────────────────────────────────────────────────────┐│
│  │                 OpenClaw Gateway                     ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  ││
│  │  │  Molty  │ │Raphael  │ │Leonardo │ │Donatello│  ││
│  │  │  🦎     │ │   🔴    │ │   🔵    │ │   🟣    │  ││
│  │  │ Master  │ │  Brinc  │ │ Cerebro │ │ Tinker  │  ││
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  ││
│  │       │           │           │           │        ││
│  │  ┌────┴───────────┴───────────┴───────────┴────┐  ││
│  │  │           Shared Infrastructure              │  ││
│  │  │  • Single config (multi-agent bindings)      │  ││
│  │  │  • Shared /data volume                       │  ││
│  │  │  • Shared API keys                           │  ││
│  │  │  • Single Discord/Slack bot                  │  ││
│  │  └─────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Simplest to set up and manage
- ✅ Single Railway project, single bill
- ✅ Agents can easily share files/memory
- ✅ Native `sessions_spawn` for sub-agent coordination
- ✅ ~$5-15/month Railway cost

**Cons:**
- ❌ One gateway failure = all agents down
- ❌ Resource contention under heavy load
- ❌ Can't use different OpenClaw versions per agent
- ❌ Shared API rate limits

---

### Option B: Fully Separate Instances (Multi-Gateway)

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Railway Proj 1  │  │ Railway Proj 2  │  │ Railway Proj 3  │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │  Molty    │  │  │  │ Raphael   │  │  │  │ Leonardo  │  │
│  │    🦎     │  │  │  │    🔴     │  │  │  │    🔵     │  │
│  │  Gateway  │  │  │  │  Gateway  │  │  │  │  Gateway  │  │
│  └─────┬─────┘  │  │  └─────┬─────┘  │  │  └─────┬─────┘  │
│        │        │  │        │        │  │        │        │
│  Own Volume     │  │  Own Volume     │  │  Own Volume     │
│  Own Config     │  │  Own Config     │  │  Own Config     │
│  Own Bot Token  │  │  Own Bot Token  │  │  Own Bot Token  │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Discord Server   │
                    │   (Shared comms)   │
                    └───────────────────┘
```

**Pros:**
- ✅ True isolation (failures don't cascade)
- ✅ Independent scaling per agent
- ✅ Different models/versions per agent
- ✅ Separate API rate limits

**Cons:**
- ❌ More complex to manage (6 deployments)
- ❌ Higher cost (~$5-15 × 6 = $30-90/month)
- ❌ Cross-agent communication via webhooks/Discord (not native)
- ❌ Shared memory requires external sync (Syncthing, Git)

---

### Option C: Hybrid (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Railway Project: Molty HQ                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    OpenClaw Gateway                          ││
│  │                                                              ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │              COMMAND (Full Agents)                   │   ││
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │   ││
│  │  │  │ Molty 🦎│  │Raphael🔴│  │Leonardo🔵│            │   ││
│  │  │  │Coordinator│ │  Brinc  │  │ Cerebro │            │   ││
│  │  │  │ + Master │  │Corporate│  │ Venture │            │   ││
│  │  │  └─────────┘  └─────────┘  └─────────┘            │   ││
│  │  └───────────────────────────────────────────────────────┘   ││
│  │                                                              ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │           SUPPORT (Sub-Agents on demand)             │   ││
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │   ││
│  │  │  │Donatello│  │  Mikey  │  │  April  │  │ Squad  │ │   ││
│  │  │  │   🟣    │  │   🟠    │  │   📰    │  │Members │ │   ││
│  │  │  │ Tinker  │  │  Mana   │  │Personal │  │ (...) │ │   ││
│  │  │  └─────────┘  └─────────┘  └─────────┘  └────────┘ │   ││
│  │  └───────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Shared: /data volume, API keys, Discord bot, Memory Vault      │
└─────────────────────────────────────────────────────────────────┘
```

**Architecture Details:**
- **Command agents** (Molty, Raphael, Leonardo): Full `agents.list[]` entries with own workspaces, bindings, Discord channels
- **Support agents** (Donatello, Mikey, April, squad): Spawn on-demand via `sessions_spawn`, cheaper models, task-focused
- **Promotion path**: When a support agent needs more autonomy, promote to command agent

**Pros:**
- ✅ Single deployment, easy management
- ✅ Native multi-agent with full isolation
- ✅ Sub-agents for cost efficiency
- ✅ Clear promotion path to Option B if needed
- ✅ ~$10-20/month Railway cost

**Cons:**
- ⚠️ Still single point of failure (acceptable for now)
- ⚠️ Sub-agents can't spawn sub-agents (no deep nesting)

---

## 3. Recommended Architecture

### **Hybrid (Option C)** with Command + Support structure

#### Why This Works for Your Use Case:

| Requirement | How Hybrid Meets It |
|-------------|---------------------|
| True isolation | Each command agent has own workspace, agentDir, sessions |
| You + Molty access all | Molty coordinates; you can message any agent via Discord |
| Cost efficient | Support agents run on cheap models (Qwen), spawn on demand |
| Future-proof | Easy to promote agents or split to separate instances |
| Discord organization | Bind channels to specific agents |

#### Agent Classification:

| Agent | Role | Type | Model | Why |
|-------|------|------|-------|-----|
| Molty 🦎 | Coordinator + Master | Command | Opus | Complex coordination, your main interface |
| Raphael 🔴 | Brinc (Corporate) | Command | Sonnet | Active projects, needs autonomy |
| Leonardo 🔵 | Cerebro (Venture) | Command | Sonnet | Strategic decisions, needs autonomy |
| Donatello 🟣 | Tinker Labs | Support | Qwen | Research tasks, spawn when needed |
| Michelangelo 🟠 | Mana Capital | Support | Sonnet | Deal analysis, spawn when needed |
| April 📰 | Personal | Support | Flash | Admin tasks, spawn when needed |

---

## 4. Deployment Strategy

### Phase 1: Foundation (Week 1)

**Goal:** Get multi-agent config working with Molty + Raphael

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-opus-4-5" },
      "subagents": { "model": "qwen-portal/coder-model" }
    },
    "list": [
      {
        "id": "molty",
        "name": "Molty 🦎",
        "default": true,
        "workspace": "/data/workspace",
        "agentDir": "/data/.openclaw/agents/molty/agent"
      },
      {
        "id": "raphael",
        "name": "Raphael 🔴",
        "workspace": "/data/workspace-brinc",
        "agentDir": "/data/.openclaw/agents/raphael/agent",
        "model": { "primary": "anthropic/claude-sonnet-4-0" }
      }
    ]
  },
  "bindings": [
    { "agentId": "molty", "match": { "channel": "telegram" } },
    { "agentId": "molty", "match": { "channel": "webchat" } },
    { "agentId": "molty", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "MANAGEMENT_CHANNEL_ID" } } },
    { "agentId": "raphael", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "BRINC_CHANNEL_ID" } } }
  ]
}
```

### Phase 2: Add Leonardo (Week 2)

Add Cerebro agent, create Discord channels, test cross-agent messaging.

### Phase 3: Support Squad (Week 3)

Configure sub-agent spawning for Donatello, Mikey, April. Define task templates.

### Phase 4: Employees (Week 4+)

Add "employee" sub-agents per project (e.g., Brinc-Engineer, Brinc-Marketing).

---

## 5. Cost Analysis

### Monthly Infrastructure Costs (Railway)

| Component | Cost | Notes |
|-----------|------|-------|
| Railway Starter | $5/month | Base plan |
| Compute (Pro estimate) | $10-20/month | ~512MB-1GB RAM, always-on |
| Volume storage | Included | Up to 10GB |
| **Total Infrastructure** | **~$15-25/month** | Single instance |

### Monthly AI API Costs (Estimates)

| Model | Usage | Cost/1M tokens | Estimated Monthly |
|-------|-------|----------------|-------------------|
| Claude Opus 4.5 | Molty main | $15 in / $75 out | $50-150 |
| Claude Sonnet 4 | Raphael, Leonardo | $3 in / $15 out | $20-60 |
| Qwen Coder | Sub-agents | FREE | $0 |
| Gemini Flash | Heartbeats | FREE | $0 |
| **Total API** | | | **$70-210/month** |

### Total Cost Projection

| Scenario | Infrastructure | API | Total |
|----------|---------------|-----|-------|
| Light use | $15 | $70 | **$85/month** |
| Medium use | $20 | $120 | **$140/month** |
| Heavy use | $25 | $200 | **$225/month** |

### Multi-Instance Cost (if needed later)

If you split to 6 separate Railway projects:
- Infrastructure: $15 × 6 = $90/month
- API: Similar (~$70-210/month)
- **Total: $160-300/month**

---

## 6. Memory & Context Sharing

### Recommended: Hierarchical Access

```
┌─────────────────────────────────────────────────────────────────┐
│                      Memory Vault (Git)                          │
│                    /data/shared/memory-vault                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    /tacit   │  │  /knowledge │  │    /daily   │             │
│  │  Shared     │  │  /projects  │  │   Shared    │             │
│  │  Preferences│  │             │  │   Timeline  │             │
│  └─────────────┘  │  ┌───────┐  │  └─────────────┘             │
│                   │  │ brinc │←── Raphael: read/write          │
│  All agents:      │  │cerebro│←── Leonardo: read/write         │
│  read             │  │ mana  │←── Mikey: read/write            │
│                   │  │master │←── Molty: read/write            │
│                   │  └───────┘  │                               │
│                   └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### Access Rules

| Agent | Own Project | Other Projects | Tacit | Daily |
|-------|-------------|----------------|-------|-------|
| Molty 🦎 | RW (master) | RW (all) | RW | RW |
| Raphael 🔴 | RW (brinc) | R | R | R |
| Leonardo 🔵 | RW (cerebro) | R | R | R |
| Donatello 🟣 | RW (tinker) | R | R | R |
| Mikey 🟠 | RW (mana) | R | R | R |
| April 📰 | RW (personal) | R | R | R |

### Implementation

Each agent's `AGENTS.md` includes:
```markdown
## Memory Access
- Your project: `/data/shared/memory-vault/knowledge/projects/brinc/` (read/write)
- Other projects: `/data/shared/memory-vault/knowledge/projects/*/` (read-only)
- Shared preferences: `/data/shared/memory-vault/tacit/` (read-only)
- Cross-project updates: Ask Molty to propagate important changes
```

---

## 7. Communication Structure

### Discord Server Layout

```
MOLTY HQ (Discord Server)
├── 📋 MANAGEMENT
│   ├── #command-center      ← Molty, You (strategy, coordination)
│   ├── #team-standup        ← All agents post daily summaries
│   └── #escalations         ← Cross-project issues
│
├── 🔴 BRINC (Raphael)
│   ├── #brinc-general       ← Raphael primary channel
│   ├── #brinc-deals         ← Deal discussions
│   └── #brinc-squad         ← Raphael's employees
│
├── 🔵 CEREBRO (Leonardo)
│   ├── #cerebro-general     ← Leonardo primary channel
│   ├── #cerebro-pipeline    ← Startup pipeline
│   └── #cerebro-squad       ← Leonardo's employees
│
├── 🟠 MANA (Michelangelo)
│   ├── #mana-general        ← Mikey primary channel
│   └── #mana-deals          ← Investment discussions
│
├── 🟣 TINKER (Donatello)
│   ├── #tinker-lab          ← Donatello primary channel
│   └── #tinker-experiments  ← Research logs
│
├── 📰 PERSONAL (April)
│   └── #personal            ← April primary channel
│
└── 🛠️ SYSTEM
    ├── #bot-logs            ← Agent activity logs
    └── #errors              ← Error notifications
```

### Channel Bindings

```json
{
  "bindings": [
    // Management
    { "agentId": "molty", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "CMD_CENTER_ID" } } },
    
    // Project channels
    { "agentId": "raphael", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "BRINC_GENERAL_ID" } } },
    { "agentId": "leonardo", "match": { "channel": "discord", "peer": { "kind": "channel", "id": "CEREBRO_GENERAL_ID" } } },
    
    // Sub-channels inherit from parent agent or route to Molty
    { "agentId": "molty", "match": { "channel": "discord" } }  // Fallback
  ]
}
```

### Communication Flows

**You → Agent:**
- Post in agent's channel → routed to that agent
- DM Molty via Telegram → Molty handles or delegates

**Agent → Agent:**
- Use `sessions_send` (same instance) or Discord mentions
- Molty acts as message broker for complex coordination

**Agent → You:**
- Post in Discord channel
- Urgent: Molty messages you on Telegram

---

## 8. Team Structure & Personalities

### Command Agents (Full Autonomy)

#### Molty 🦎 — Master Coordinator
```markdown
# SOUL.md
You are Molty, the coordinator of a team of AI agents.

## Personality
- Calm, efficient, sees the big picture
- Balances competing priorities across projects
- Knows when to delegate vs. handle directly

## Responsibilities
- Coordinate cross-project work
- Maintain shared memory vault
- Route escalations to appropriate agent
- Interface with Guillermo on strategy

## Communication Style
- Concise status updates
- Proactive about blockers
- Suggests solutions, not just problems
```

#### Raphael 🔴 — Brinc (Corporate)
```markdown
# SOUL.md
You are Raphael, head of Brinc operations.

## Personality
- Direct, action-oriented, gets things done
- Impatient with bureaucracy
- Loyal to the mission, pushes for results

## Responsibilities
- Corporate accelerator operations
- Partner relationships
- Deal execution

## Communication Style
- Brief, punchy updates
- Flags blockers immediately
- Prefers action over analysis
```

#### Leonardo 🔵 — Cerebro (Venture)
```markdown
# SOUL.md
You are Leonardo, head of Cerebro ventures.

## Personality
- Strategic, analytical, long-term thinker
- Calm under pressure
- Values data-driven decisions

## Responsibilities
- Venture pipeline management
- Investment thesis development
- Startup evaluation

## Communication Style
- Structured analysis
- Weighs pros/cons explicitly
- Asks clarifying questions
```

### Support Agents (Spawn on Demand)

#### Donatello 🟣 — Tinker Labs
- Research-focused, technical deep dives
- Spawned for: technology analysis, prototypes, experiments

#### Michelangelo 🟠 — Mana Capital
- Creative, relationship-oriented
- Spawned for: deal analysis, LP communications, portfolio reviews

#### April 📰 — Personal
- Organized, thorough, good at research
- Spawned for: travel planning, family admin, health tracking

### Employee Agents (Task-Specific)

Each command agent can spawn specialized employees:

| Project | Employees | Tasks |
|---------|-----------|-------|
| Brinc | Brinc-Engineer, Brinc-Marketing, Brinc-Legal | Technical reviews, content, contracts |
| Cerebro | Cerebro-Analyst, Cerebro-Scout | Due diligence, deal sourcing |
| Mana | Mana-Analyst, Mana-Compliance | Financial analysis, regulatory |

---

## 9. Implementation Roadmap

### Week 1: Foundation
- [ ] Create Discord server with channel structure
- [ ] Configure multi-agent in openclaw.json (Molty + Raphael)
- [ ] Create workspace directories and SOUL.md files
- [ ] Test Discord bindings
- [ ] Verify isolation (separate sessions, no cross-talk)

### Week 2: Expand Command
- [ ] Add Leonardo (Cerebro) as full agent
- [ ] Create Memory Vault access rules
- [ ] Test cross-agent communication via Molty
- [ ] Document escalation procedures

### Week 3: Support Squad
- [ ] Configure sub-agent settings (models, tools, limits)
- [ ] Create task templates for Donatello, Mikey, April
- [ ] Test spawn → execute → announce flow
- [ ] Set up auto-archive for sub-agent sessions

### Week 4: Polish
- [ ] Add remaining support agents
- [ ] Create employee templates
- [ ] Write comprehensive AGENTS.md for each
- [ ] Performance tuning (model selection, caching)

### Month 2+: Scale
- [ ] Evaluate if multi-instance needed
- [ ] Add more specialized employees
- [ ] Automate routine coordination
- [ ] Consider voice/video integration

---

## 10. Risk Mitigation

### Single Point of Failure
- **Risk:** Gateway crash takes all agents offline
- **Mitigation:** Railway auto-restart, health checks, backup config
- **Future:** Split to multi-instance if uptime critical

### API Rate Limits
- **Risk:** Heavy use hits Anthropic limits
- **Mitigation:** Model diversity (Sonnet for leads, Qwen for sub-agents)
- **Future:** Multiple API keys across agents

### Context Overflow
- **Risk:** Long sessions exceed context window
- **Mitigation:** Aggressive pruning (4h TTL), sub-agent isolation
- **Future:** Compaction summaries

### Cross-Agent Confusion
- **Risk:** Agents step on each other's work
- **Mitigation:** Clear ownership, Memory Vault access rules
- **Future:** Explicit handoff protocols

---

## Appendix A: Config Template

See `/data/workspace/research/tmnt-team-architecture/config-template.json5`

## Appendix B: SOUL.md Templates

See `/data/workspace/research/tmnt-team-architecture/templates/`

## Appendix C: Discord Setup Guide

See `/data/workspace/research/tmnt-team-architecture/discord-setup.md`

---

*Report complete. Ready for review and decision.*

**Next step:** Confirm architecture choice, then begin Phase 1 implementation.
