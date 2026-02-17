# PARA Guide - Memory Vault Structure

*How knowledge flows through the TMNT system*

---

## Structure

```
knowledge/
├── projects/           # P: Active work with end dates
│   ├── brinc/          # Raphael's domain
│   ├── cerebro/        # Leonardo's domain
│   ├── personal/       # April's domain
│   ├── tinker-labs/    # Donatello's domain
│   ├── mana-capital/   # Michelangelo's domain
│   ├── master/         # Molty's domain (meta/infra)
│   └── _archive/       # Completed projects
│
├── areas/              # A: Ongoing responsibilities (no end date)
│   ├── sales/          # Sales processes, playbooks
│   ├── infrastructure/ # Tech setup, SOPs
│   ├── personal/       # Life admin, health, family
│   ├── investments/    # Portfolio, deals, tracking
│   └── research/       # Ongoing learning, trends
│
├── resources/          # R: Reference material
│   └── (shared read-only to all agents)
│
├── squad/              # Cross-agent operational rules
│   └── OPERATIONAL-GUIDELINES.md
│
├── people/             # Contact directory
│
└── archives/           # Old/inactive material
```

---

## Flow: How Knowledge Migrates

### 1. Team Lead Captures (Daily)

When you learn something reusable:
- **Project-specific** → Update your project's KB folder
- **Cross-project insight** → Flag to Molty: `LEARNING: [topic] — [insight]`

### 2. Molty Curates (Weekly)

Every week, Molty:
- Reviews flagged learnings from all team leads
- Migrates insights to appropriate PARA locations
- Cross-pollinates: shares relevant learnings across agents
- Archives completed project milestones

### 3. Syncthing Distributes (Automatic)

- `resources/` and `squad/` sync to ALL agents (read-only)
- `projects/{name}/` syncs only to that project's lead
- `areas/` syncs based on relevance

---

## What Goes Where

| Content Type | Location | Example |
|--------------|----------|---------|
| Active client work | `projects/{project}/` | Brinc proposal drafts |
| Reusable playbook | `areas/{area}/` | Sales objection handlers |
| Reference docs | `resources/` | Company overview, SOPs |
| Completed deliverable | `projects/_archive/` | Finished campaign |
| Contact info | `people/` | Client contacts |
| Team rules | `squad/` | Channel ownership |

---

## Flagging Learnings to Molty

Use webhook or Discord with format:
```
LEARNING: [category]
Topic: [what you learned]
Insight: [the takeaway]
Action: [what you did / recommend]
Migrate to: [suggested PARA location]
```

Example:
```
LEARNING: sales
Topic: Insurance objection handling
Insight: Leading with Manulife case study converts 3x better
Action: Updated objection handlers, used in 2 calls
Migrate to: areas/sales/objection-playbook.md
```

---

## Archiving Projects

When a project milestone completes:
1. Team lead marks deliverables as done
2. Molty reviews for reusable learnings
3. Learnings migrate to `areas/` or `resources/`
4. Project folder moves to `projects/_archive/`
5. Archive retains for reference, not active sync

---

*Maintained by Molty 🦎 | Weekly curation every Monday*
