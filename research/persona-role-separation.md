# AI Assistant Persona/Role Separation Frameworks

**Research Report for Multi-Faceted Users**  
*Prepared: January 31, 2026*

---

## 1. Overview of the Challenge

Multi-faceted users—those who wear multiple "hats" in life (employee, investor, entrepreneur, family member, etc.)—face a unique challenge when working with AI assistants:

**The Core Problem:** Information and context from one role can "leak" into another, creating risks:
- **Professional embarrassment**: Personal opinions surfacing in work contexts
- **Confidentiality breaches**: Client data from one venture mixing with another
- **Relationship damage**: Wrong tone/persona when interacting on your behalf
- **Fiduciary conflicts**: Investment insights mixing with entrepreneurial activities
- **Cognitive overhead**: Constantly re-establishing context with the AI

**Why This Matters:**
- 78% of organizations now use AI in business functions (up from 55% in 2023)
- AI assistants are increasingly "always on" across multiple contexts
- Enterprise-grade isolation patterns are emerging but not well-documented for individuals
- Most consumer AI products (like OpenAI's ChatGPT) use global memory—great for convenience, risky for separation

---

## 2. Frameworks and Approaches Found in the Wild

### 2.1 The Personal.ai Multi-Persona Model

**Approach:** Separate AI personas with isolated memory banks

Key features:
- Each persona has its own identity, directives, and memory bank
- Sub-personas can share information while maintaining data privacy
- Primary persona integrates unified memories but sub-personas stay isolated
- Information sharing between personas is controlled

**Real-world use cases:**
- Lawyers: Legal persona trained on documents and precedents
- Financial advisors: Investment expertise persona
- Executives: "Chief of Staff" persona for coordination
- Family: Daily task automation persona

**Quote from Personal.ai:** "Separating information across AI Personas is key as it controls which kinds of data different users have access to."

### 2.2 Claude Projects (Anthropic's Approach)

**Approach:** Project-based workspaces with hard boundaries

Key features:
- Self-contained workspaces with own chat histories and knowledge bases
- Project-specific custom instructions (tone, format, behavior)
- RAG (Retrieval Augmented Generation) for larger document collections
- Team/Enterprise plans allow shared projects with permission levels
- Memory summaries are separate per project—no cross-pollination

**Critical insight:** "Nothing from Project A can bleed into Project B" — this is by design.

**Developer pattern:** CLAUDE.md files in repo roots for context injection—version-controlled, reviewable.

### 2.3 MemGPT / Letta: The OS Paradigm

**Approach:** Treat memory as a computational resource to be managed

Key features:
- Hierarchical memory: Primary context (RAM) + External context (Disk)
- LLM autonomously manages what to keep/discard
- Archival storage for long-term, vector-based memory
- Recall storage for full historical record

**Strength:** Creates illusion of infinite memory within finite context  
**Weakness:** All reasoning uses single agent—cognitive overhead for memory management

### 2.4 LangChain/Autogen Toolkit Approach

**Approach:** Composable primitives for custom memory architectures

Memory module types:
- Buffer/Window Memory (short-term chat windows)
- Summary Memory (periodic LLM summaries)
- Entity Memory (structured capture of people/orgs/concepts)
- Knowledge-Graph Memory (relational querying)

**Key trend:** Industry moving from unstructured snippets → knowledge graphs for relational queries like "Which decisions were influenced by facts from source X?"

### 2.5 OpenClaw Workspace Pattern

**Approach:** File-based configuration with session isolation

Standard files:
- `AGENTS.md` — Operating instructions for the agent
- `SOUL.md` — Persona, tone, and boundaries
- `USER.md` — Who the user is (context about you)
- `MEMORY.md` — Curated long-term memory (only load in main/private sessions)
- `memory/YYYY-MM-DD.md` — Daily memory logs

**Critical security note from docs:** "MEMORY.md — Only load in the main, private session (not shared/group contexts)"

**Advanced:** Multi-agent routing can use different workspaces per agent.

---

## 3. Recommended Structure for Guillermo's Roles

Based on the research, here's a proposed structure for five distinct roles:

### Role Taxonomy

| Role | Short Code | Description | Risk Level |
|------|------------|-------------|------------|
| **Corporate** | `corp` | Full-time employment | HIGH (employer data) |
| **Personal** | `personal` | Family, friends, self | MEDIUM (privacy) |
| **Investor** | `invest` | Angel/VC investments | HIGH (fiduciary, confidential) |
| **Entrepreneur** | `venture` | Business ventures | MEDIUM-HIGH (competitive info) |
| **Meta** | `meta` | Tools, frameworks, self-improvement | LOW (mostly public) |

### Isolation Requirements Matrix

| From/To | Corp | Personal | Invest | Venture | Meta |
|---------|------|----------|--------|---------|------|
| Corp | ✓ | ✗ | ✗ | ✗ | △ |
| Personal | ✗ | ✓ | ✗ | ✗ | △ |
| Invest | ✗ | ✗ | ✓ | ✗ | △ |
| Venture | ✗ | ✗ | ✗ | ✓ | △ |
| Meta | △ | △ | △ | △ | ✓ |

- ✓ = Full access within role
- ✗ = Hard isolation required
- △ = Selective sharing (frameworks, not data)

---

## 4. Implementation Strategies

### 4.1 Workspace Structure (File/Folder Separation)

```
~/.openclaw/workspace/          # Main workspace (meta-level)
├── AGENTS.md
├── SOUL.md
├── USER.md
├── MEMORY.md                   # Only in main session
├── memory/
│   └── YYYY-MM-DD.md
└── roles/
    ├── corp/
    │   ├── ROLE.md            # Corporate persona, constraints
    │   ├── context/           # Corporate docs, style guides
    │   └── memory/            # Corporate-specific memory
    ├── personal/
    │   ├── ROLE.md
    │   ├── context/
    │   └── memory/
    ├── invest/
    │   ├── ROLE.md            # Investor persona, deal flow notes
    │   ├── context/           # Investment theses, company profiles
    │   └── memory/            # Deal memos, meetings
    └── venture/
        ├── ROLE.md
        ├── context/
        └── memory/
```

### 4.2 Channel-Based Separation

Map communication channels to roles:

| Channel | Role | Notes |
|---------|------|-------|
| Work Slack/Teams | corp | Never discuss invest/venture |
| Personal WhatsApp | personal | Family/friends context |
| Investor Discord/Signal | invest | Deal flow, portfolio |
| Venture Slack | venture | Specific to startup |
| Main session | meta | Full access, your command center |

**Implementation:** Use OpenClaw's channel routing to enforce role context per channel.

### 4.3 Role-Specific Prompts (ROLE.md examples)

**Corporate Role (roles/corp/ROLE.md):**
```markdown
# Corporate Role: [Company Name]

## Identity
You are assisting Guillermo in his role as [Title] at [Company].

## Boundaries
- NEVER reference investment portfolio or deal flow
- NEVER mention startup ventures
- NEVER share personal/family information
- Use formal, professional tone
- Follow [Company] communication standards

## Context
- Primary stakeholders: [list]
- Key projects: [list]
- Communication preferences: [guidelines]
```

**Investor Role (roles/invest/ROLE.md):**
```markdown
# Investor Role

## Identity
You are assisting Guillermo as an angel investor.

## Boundaries
- NEVER reference employer or corporate role
- NEVER share proprietary deal information between portfolio companies
- Maintain confidentiality of term sheets, valuations
- May reference public market knowledge

## Fiduciary Considerations
- Be careful about information asymmetry
- Note potential conflicts of interest
- Separate companies have separate contexts
```

### 4.4 Memory Isolation Patterns

**Approach 1: Separate Memory Files per Role**
```
roles/corp/memory/2026-01-31.md   # Corporate daily log
roles/invest/memory/2026-01-31.md # Investor daily log
```

**Approach 2: Memory Tags**
In `memory/YYYY-MM-DD.md`:
```markdown
## 2026-01-31

### [corp] Meeting with product team
- Discussed Q2 roadmap
- Action: Review specs by Friday

### [invest] Call with Acme Corp founder
- Series A pricing discussion
- CONFIDENTIAL: [details redacted from main memory]

### [personal] Family dinner planning
- Reservations for Saturday
```

**Approach 3: Role-Specific MEMORY.md Files**
Each role has its own long-term memory, loaded only when in that role context.

### 4.5 Context-Switching Protocol

When switching roles, the AI should:

1. **Clear active context** — Don't carry forward conversation state
2. **Load role-specific files** — ROLE.md, role memory, role context
3. **Acknowledge the switch** — "Now operating in [role] context"
4. **Apply role constraints** — Boundaries from ROLE.md
5. **Log the transition** — For audit trail

**Prompt pattern for role switch:**
```
[Switching to {role} context. Loading role configuration. 
Previous context cleared. Boundaries active.]
```

---

## 5. Trade-offs and Considerations

### 5.1 Convenience vs. Security

| Approach | Convenience | Security | Maintenance |
|----------|-------------|----------|-------------|
| Single global memory (OpenAI style) | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Project-based isolation (Claude style) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| File-based workspaces | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Separate AI instances per role | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

**Recommendation:** File-based workspaces with channel routing offers best balance for power users.

### 5.2 Cross-Session Leak Prevention

From security research (Giskard, Microsoft):

**Key safeguards:**
1. **Strict session isolation** — Each role's context, cache, and memory completely separated
2. **Output redaction** — Automated detection/removal of sensitive data patterns
3. **Access control** — Verify role permissions before retrieving prior context
4. **Prompt injection protection** — Sanitize inputs to prevent adversarial extraction
5. **Monitoring** — Detect abnormal query patterns across sessions

### 5.3 The "Meta" Role Dilemma

The meta role (tools, frameworks, self-improvement) presents unique challenges:
- It naturally contains knowledge that applies across all roles
- Yet it shouldn't access role-specific confidential data
- **Solution:** Meta can access *patterns* and *frameworks* but not *instances*

**Example:**
- ✅ Meta can know: "I use a GTD-style task management approach"
- ❌ Meta cannot access: "Specific corporate project deadlines"

### 5.4 When Roles Overlap

**Scenario:** Considering investing in a company that might compete with employer.

**Protocol:**
1. Acknowledge the potential conflict
2. Do not mix contexts — handle in invest role only
3. Note the conflict in invest/memory for future reference
4. Consider whether to proceed at all (human decision)

---

## 6. Iterative Improvement Path

### Phase 1: Foundation (Week 1-2)
- [ ] Create role folder structure
- [ ] Write initial ROLE.md for each role
- [ ] Set up separate memory directories
- [ ] Configure channel → role mapping

### Phase 2: Refinement (Week 3-4)
- [ ] Test each role in isolation
- [ ] Identify leakage points (where context bleeds)
- [ ] Refine boundaries in ROLE.md
- [ ] Add role-specific context files

### Phase 3: Automation (Month 2)
- [ ] Set up automatic role detection from channel
- [ ] Implement memory isolation checks
- [ ] Create role-switch protocol
- [ ] Add audit logging for cross-role queries

### Phase 4: Hardening (Month 3+)
- [ ] Regular review of cross-role boundaries
- [ ] Update ROLE.md based on lessons learned
- [ ] Consider sandboxing for highest-risk roles (corp, invest)
- [ ] Periodic security review of memory files

### Ongoing Maintenance
- Daily: Log significant interactions in role-specific memory
- Weekly: Review and clean up memory files
- Monthly: Update ROLE.md with lessons learned
- Quarterly: Full audit of role separation effectiveness

---

## 7. Quick Reference Implementation Checklist

```markdown
## For Each Role:

1. [ ] Create roles/{role}/ROLE.md with:
   - Identity description
   - Hard boundaries (what to NEVER do)
   - Soft boundaries (what to be careful about)
   - Stakeholder context
   - Communication preferences

2. [ ] Create roles/{role}/memory/ directory
   - Daily logs go here
   - Role-specific MEMORY.md for long-term

3. [ ] Create roles/{role}/context/ directory
   - Style guides, reference docs
   - Key relationships and contacts
   - Project/deal briefs (as appropriate)

4. [ ] Map channels to this role
   - Update AGENTS.md or config
   - Test that role loads correctly

5. [ ] Test isolation
   - Attempt to access other role's data
   - Verify boundaries hold
   - Document any leakage
```

---

## 8. Sources and Further Reading

1. **Personal.ai** — Multi-persona AI with separate memory banks
   - https://www.personal.ai/pai-academy/organize-your-expertise-with-a-persona

2. **Claude Projects** — Anthropic's workspace isolation approach
   - https://support.claude.com/en/articles/9517075-what-are-projects

3. **Serokell: Design Patterns for Long-Term Memory**
   - https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures

4. **Giskard: Cross Session Leak Prevention**
   - https://www.giskard.ai/knowledge/cross-session-leak-when-your-ai-assistant-becomes-a-data-breach

5. **OpenClaw: Agent Workspace**
   - https://docs.openclaw.ai/concepts/agent-workspace

6. **The Persona Pattern (Towards AI)**
   - https://towardsai.net/p/artificial-intelligence/the-persona-pattern-unlocking-modular-intelligence-in-ai-agents

7. **Building AI Agents with Personas, Goals, and Dynamic Memory (Medium)**
   - https://medium.com/@leviexraspk/building-ai-agents-with-personas-goals-and-dynamic-memory-6253acacdc0a

---

*This research synthesizes approaches from commercial AI products, open-source frameworks, academic research, and practitioner patterns. The recommended structure is designed for practical implementation while maintaining the flexibility to evolve as usage patterns become clearer.*
