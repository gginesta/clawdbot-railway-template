# PLAN-020: Autoresearch — Auto-Improve OpenClaw Skills

**Created:** 2026-03-25 | **Status:** Planning | **Owner:** Molty 🦎
**Paperclip:** TMN-12 | **Review:** Saturday 2026-03-29 with Guillermo before deploy
**Inspired by:** [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) + [Ole Lehmann's adaptation](https://x.com/itsolelehmann/status/2033919415771713715)

---

## Concept

Take Karpathy's "loop forever, measure, keep/discard" pattern and apply it to OpenClaw skill prompts. An agent runs a skill, scores the output against a checklist, tweaks the prompt, and repeats — autonomously improving any skill overnight.

## Core Pattern

```
LOOP:
  1. Run skill with test input
  2. Score output against yes/no checklist (e.g. 6 questions)
  3. Calculate pass rate (e.g. 4/6 = 67%)
  4. Analyze which checks failed
  5. Make ONE small change to the skill prompt
  6. Run again with same input
  7. Score improved? → KEEP change
     Score worse?   → REVERT change
  8. Repeat until 95%+ pass rate (3 consecutive) or max rounds
```

## Architecture

### The Skill: `/skills/autoresearch/SKILL.md`

**Inputs:**
- Target skill path (e.g. `/openclaw/skills/weather/SKILL.md`)
- Test inputs (1-3 example prompts to run the skill against)
- Quality checklist (3-6 yes/no questions defining "good output")
- Max rounds (default: 20)

**Outputs:**
- `{skill}-improved.md` — the optimised skill (original untouched)
- `{skill}-changelog.md` — every change tried, why, kept/reverted
- `{skill}-results.tsv` — round-by-round scores

### How It Works

1. **Setup agent** reads the target skill, understands its purpose
2. **Baseline run** — execute skill with test inputs, score against checklist, record starting %
3. **Analysis** — which checklist items fail most? That's the first target
4. **Mutation** — make one surgical change to the skill prompt (add a rule, add an example, tighten wording, ban a pattern)
5. **Test** — run skill again, score again
6. **Decision** — keep or revert (git-style, but on the prompt text)
7. **Loop** — next failing check, next mutation

### Scoring Engine

Each checklist question is evaluated by a separate LLM call (cheap model — Haiku):
```
Given this skill output: {output}
Question: {checklist_item}
Answer YES or NO only.
```

Pass rate = YES count / total questions. Simple, deterministic, consistent.

### Cost Estimate

Per round: 1 skill execution + 6 scoring calls
- Skill execution: ~$0.01-0.05 (Haiku sub-agent)
- 6 scoring calls: ~$0.006 (Haiku, tiny prompts)
- **Per round: ~$0.02-0.06**
- **20 rounds: ~$0.50-1.20**
- **Full overnight (100 rounds): ~$2-6**

Cheap enough to run freely.

---

## Phase 1: Weekend Build (Mar 29-30)

### Saturday — Build + Test

| # | Task | Time |
|---|------|------|
| 1 | Build autoresearch skill (SKILL.md + runner script) | 2h |
| 2 | Define checklist for overnight worker | 30min |
| 3 | Dry run: 5 rounds on overnight worker prompt | 30min |
| 4 | Review with Guillermo — discuss results, adjust | — |

### Sunday — First Real Run

| # | Task | Time |
|---|------|------|
| 5 | Run autoresearch overnight on 2-3 skills | Autonomous |
| 6 | Review results Monday morning | 30min |

## Phase 2: Fleet Rollout (Week of Mar 31)

### Targets by Priority

| Priority | Skill/Prompt | Agent | Checklist Ideas |
|----------|-------------|-------|-----------------|
| **P1** | Overnight worker | Molty | Completes tasks? Stays <90min? Posts summary? No fabricated data? No stale memory parroting? |
| **P1** | Contact enrichment prompts | Leonardo | Valid work history? Real company info? No hallucinated URLs? Skills extracted? Under token budget? |
| **P2** | Morning briefing | Molty | Actionable items clear? Calendar accurate? Right length? No noise? |
| **P2** | Outreach email templates | Raphael | Personalised? <75 words? Specific ask? No buzzwords? Mentions prospect's company? |
| **P3** | Chat system prompt (Cerebro) | Leonardo | Stays on-topic? Uses contact context? No hallucinations? Helpful tone? |
| **P3** | Content article drafts | Molty | Guillermo's voice? Concrete examples? Under word count? No fluff? |

### Meta-Application (Phase 3)

| Target | Metric |
|--------|--------|
| AGENTS.md instructions | Across N test scenarios, how often does agent violate a REGRESSIONS.md rule? |
| SOUL.md persona | Does output match tone guidelines? Rate across 20 sample responses |
| Skill discovery (new) | Given a workflow description, does the agent pick the right skill? |

---

## Design Decisions

1. **Original skill never modified** — improved version saved as separate file. Human decides when to promote.
2. **One change per round** — isolates what works. Multiple changes = can't tell what helped.
3. **Checklist, not vibes** — yes/no only. No 1-10 scales. Consistent, auditable.
4. **Haiku for scoring** — cheap, fast, good enough for binary yes/no.
5. **Changelog is the real output** — even if the improved skill isn't much better, the changelog tells you what works and what doesn't for that specific prompt. Transferable knowledge.
6. **Git-style keep/revert** — clean. Only improvements survive.

## Risks

| Risk | Mitigation |
|------|-----------|
| Checklist gaming — agent optimises for checks but output gets weird | Keep checklist to 3-6 items. Review outputs manually after run. |
| Overfitting to test inputs | Use 3+ diverse test inputs. Rotate inputs across rounds. |
| Cost runaway | Hard cap at max rounds. Haiku for all scoring. Budget alert at $5. |
| Agent breaks the skill prompt | Original untouched. Worst case: revert entirely. |
| Metric doesn't capture quality | Start conservative. Iterate on checklists based on results. |

---

## References

- Karpathy autoresearch: `/data/workspace/research/autoresearch/`
- Ole Lehmann's X article: https://x.com/itsolelehmann/status/2033919415771713715
- Paperclip task: TMN-12

---

*Review Saturday 2026-03-29 before any deployment. No autonomous runs until Guillermo approves.*
