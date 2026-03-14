# PLAN-016: Todoist↔MC Sync v2

**Status:** Approved for implementation
**Created:** 2026-03-14
**Owner:** Molty

---

## Objective

Keep Todoist as Guillermo's single view for all tasks (personal + fleet), with fleet tasks mirrored to MC for agent execution.

---

## Core Principle

**Todoist = Guillermo's dashboard**
**MC = Agent workspace**
**Sync keeps them aligned**

---

## Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Capture   │ ──► │   Triage    │ ──► │   Execute   │
│  (Todoist)  │     │  (Standup)  │     │ (MC/Agent)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Edit + Sync │
                    │  (Molty)    │
                    └─────────────┘
```

---

## Task Assignment Methods

### Method A: Natural Language Prefix (inline)
At capture time, if obvious who owns it:
```
"Raphael: update pitch deck by Friday"
"Leo: fix Cerebro onboarding bug"
"Molty: set up weekly digest cron"
```

### Method B: Triage at Standup (batch)
For tasks captured without a prefix:
- Standup shows new/unassigned tasks
- Guillermo replies: "1 mine, 2 Raphael, 3 drop"
- Molty processes assignments

---

## What Molty Does on Assignment

When a task is assigned to an agent:

1. **Edit Todoist task:**
   - Add prefix: `[Raphael] Update pitch deck`
   - Keep in Todoist for Guillermo's visibility

2. **Create MC task:**
   - Title: "Update pitch deck"
   - Assignee: raphael
   - Due date: from Todoist
   - Status: assigned
   - Link back to Todoist task ID (for sync)

3. **Store mapping:**
   - `todoist_id: 12345 → mc_id: abc123`
   - Used for bi-directional completion sync

---

## Completion Sync

### Agent completes in MC:
1. MC task → done
2. Molty detects completion (via heartbeat or webhook)
3. Todoist task → completed
4. Guillermo sees it done in Todoist

### Guillermo completes in Todoist:
1. Todoist task → completed
2. Molty detects via sync script
3. MC task → done (if exists)

---

## Task Prefixes

| Prefix | Meaning |
|--------|---------|
| `[Molty]` | Assigned to Molty |
| `[Raphael]` | Assigned to Raphael |
| `[Leo]` | Assigned to Leonardo |
| `[April]` | Assigned to April |
| `[Don]` | Assigned to Donatello |
| `[Mike]` | Assigned to Michelangelo |
| *(no prefix)* | Guillermo's task |

---

## Implementation Steps

### Phase 1: Prefix Parsing (Day 1)
- [ ] Update standup to detect `Agent:` prefix in new tasks
- [ ] Auto-edit Todoist task to `[Agent] task title`
- [ ] Create corresponding MC task with assignment

### Phase 2: Standup Triage (Day 1)
- [ ] Show unassigned tasks in standup
- [ ] Parse Guillermo's reply: "2 Raphael, 3 Leo"
- [ ] Execute edits + MC creation

### Phase 3: Completion Sync (Day 2)
- [ ] On MC task completion → complete Todoist task
- [ ] On Todoist completion → complete MC task (if mapped)
- [ ] Store task mappings in `/data/workspace/data/task-mappings.json`

### Phase 4: Testing (Day 2)
- [ ] Test prefix capture: "Raphael: do X"
- [ ] Test standup triage assignment
- [ ] Test bi-directional completion
- [ ] Verify Guillermo sees all tasks in Todoist

---

## Files to Create/Update

| File | Purpose |
|------|---------|
| `scripts/todoist-mc-sync-v2.py` | Main sync logic |
| `data/task-mappings.json` | Todoist↔MC ID mappings |
| `memory/refs/standup-process.md` | Update triage section |

---

## What Stays the Same

- Todoist remains Guillermo's primary capture tool
- MC remains agent workspace
- Standup at 5PM HKT
- Agents work from MC, not Todoist

---

## What Changes

| Before | After |
|--------|-------|
| Fleet tasks moved OUT of Todoist | Fleet tasks STAY in Todoist with `[Agent]` prefix |
| Guillermo checks MC for fleet status | Guillermo sees everything in Todoist |
| Assignment unclear | Clear prefix shows owner |

---

## Rollout

- **Tonight:** Phase 1-2 (prefix parsing + triage)
- **Tomorrow:** Phase 3-4 (completion sync + testing)
- **Monday standup:** First real test

---

## Success Criteria

1. ✅ Guillermo captures task fast in Todoist
2. ✅ Assignment happens via prefix OR standup triage
3. ✅ Fleet tasks show `[Agent]` prefix in Todoist
4. ✅ Fleet tasks appear in MC for agents
5. ✅ Completion syncs both directions
6. ✅ Guillermo never needs to check MC for task status

---

*Ready for implementation. Starting tonight.*
