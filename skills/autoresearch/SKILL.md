---
name: autoresearch
description: Auto-improve OpenClaw skills using a Karpathy-inspired test-score-tweak loop. Use when asked to "improve a skill", "auto-tune a skill", "run the autoresearch loop", "benchmark a skill", or "self-improve". Takes a skill directory, generates synthetic test cases, scores how well the current SKILL.md handles them, identifies gaps, and produces an improved version. Iterates until score plateaus or max rounds reached.
---

# Autoresearch — Auto-Improve Skills

Karpathy-inspired loop: **generate test cases → score current skill → identify gaps → tweak → repeat.**

## Workflow

### Phase 1: Load Target Skill

```bash
SKILL_DIR=/path/to/skill
cat $SKILL_DIR/SKILL.md
ls $SKILL_DIR/{scripts,references,assets}/ 2>/dev/null
```

Read the full skill. Understand what it's supposed to do.

### Phase 2: Generate Test Cases

Spawn a sub-agent (or do it inline) to produce 10–20 synthetic user prompts that *should* trigger and exercise this skill.

Vary by:
- **Happy path** — canonical use cases matching the description
- **Edge cases** — boundary conditions, unusual inputs
- **Adversarial** — prompts that look similar but should NOT use this skill
- **Complex** — multi-step workflows that stress the skill's depth

Write test cases to `autoresearch/tmp/test-cases-{skill-name}.json`:
```json
[
  {"id": 1, "prompt": "...", "expected_behavior": "...", "case_type": "happy|edge|adversarial|complex"},
  ...
]
```

### Phase 3: Score Current Skill

For each test case, evaluate (inline reasoning — no need to run code):

| Criterion | Weight | Question |
|-----------|--------|----------|
| **Trigger precision** | 30% | Does the description correctly trigger/skip for this prompt? |
| **Workflow coverage** | 30% | Does SKILL.md give enough guidance to execute correctly? |
| **Reference completeness** | 20% | Are needed API docs / schemas / examples present? |
| **Conciseness** | 20% | Does the skill avoid unnecessary tokens / duplication? |

Score each case 0–10. Compute weighted average.

Write scores to `autoresearch/tmp/scores-{skill-name}-round{N}.json`.

**Stop condition:** score ≥ 8.5 OR round ≥ 3 OR no improvement > 0.3 from last round.

### Phase 4: Identify Gaps

Analyze low-scoring cases. Common failure modes:

- **Trigger miss** — description doesn't mention key phrases → add to description
- **Workflow gap** — SKILL.md skips a step users struggle with → add section
- **Missing reference** — agent has to rediscover schema/API every run → create references file
- **Over-specification** — skill forces one approach when flexibility needed → loosen
- **Under-specification** — skill too vague on fragile steps → tighten with example or script

List each gap with: `[case_id] [criterion] [gap description] [proposed fix]`

### Phase 5: Tweak

Apply fixes. For SKILL.md edits: use `edit` tool with surgical changes.

For new reference files: write to `{skill-dir}/references/{topic}.md`.

For new scripts: write to `{skill-dir}/scripts/{name}.py` and **test by running them**.

Keep changes minimal — one gap per edit, not a full rewrite unless score < 4.

### Phase 6: Re-score and Loop

Repeat Phase 3–5. Track score delta per round.

If score improves < 0.3 between rounds, stop — marginal returns.

### Phase 7: Package + Report

```bash
python3 /openclaw/skills/skill-creator/scripts/package_skill.py /path/to/skill /data/workspace/skills/dist/
```

Write summary report to `autoresearch/tmp/report-{skill-name}.md`:

```markdown
# Autoresearch Report — {skill-name}

## Rounds run: N
## Score trajectory: 6.2 → 7.8 → 8.6 (stopped: threshold met)

## Changes made
- [round 1] Added "audit" trigger phrase to description
- [round 1] Added references/api-schema.md with endpoint examples
- [round 2] Tightened Phase 3 scoring guidance

## Remaining gaps (score < threshold)
- Case 14: edge case around X — would require human input to resolve

## Packaged: /data/workspace/skills/dist/{skill-name}.skill
```

## Usage Notes

- Run in an isolated sub-agent (`sessions_spawn`) to avoid polluting main context
- Tmp files live in `/data/workspace/skills/autoresearch/tmp/` — safe to delete after run
- For skills with large reference files, only read the table of contents first, then load sections on demand
- If a skill scores > 8.5 on first pass: skip to Phase 7 and report "no improvements needed"

## References

- **Scoring rubric details**: `references/scoring-rubric.md`
- **Common gap patterns + fixes**: `references/gap-patterns.md`
