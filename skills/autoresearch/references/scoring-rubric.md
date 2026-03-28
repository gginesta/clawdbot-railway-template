# Scoring Rubric — Autoresearch

## Per-Case Scoring (0–10)

### Trigger Precision (30% weight)

| Score | Meaning |
|-------|---------|
| 10 | Description perfectly triggers on happy paths, correctly skips adversarial cases |
| 7–9 | Minor over/under-triggering on 1–2 edge cases |
| 4–6 | Misses 2–4 key trigger phrases OR incorrectly fires on off-topic prompts |
| 1–3 | Description too vague or too narrow — skill often missed or mis-applied |
| 0 | Description doesn't match skill function at all |

**How to evaluate**: Imagine another agent reading only the `description:` field. Would it pick this skill for the test prompt? Would it correctly skip it for adversarial cases?

### Workflow Coverage (30% weight)

| Score | Meaning |
|-------|---------|
| 10 | SKILL.md provides clear, ordered steps covering all major decisions in the test case |
| 7–9 | Minor gaps — 1 step missing, or guidance slightly ambiguous at one branch |
| 4–6 | Key decision point not addressed; agent would have to improvise or guess |
| 1–3 | Workflow guidance is mostly absent; skill is a description with no procedural content |
| 0 | No workflow content |

### Reference Completeness (20% weight)

| Score | Meaning |
|-------|---------|
| 10 | All needed schemas, API docs, and examples are present in references/ or scripts/ |
| 7–9 | 1 reference file missing but the information is findable via other means |
| 4–6 | Key API schema or example missing — agent would have to rediscover it each run |
| 1–3 | References absent for a skill that clearly needs them |
| 0 | N/A only if skill genuinely needs no external reference (pure reasoning task) |

**Note**: Score 10 for N/A cases (skill is self-contained and needs no references).

### Conciseness (20% weight)

| Score | Meaning |
|-------|---------|
| 10 | Every token earns its place; no duplication; no "Codex already knows this" filler |
| 7–9 | 1–2 redundant paragraphs or over-explained concepts |
| 4–6 | Multiple sections that duplicate each other or repeat model knowledge |
| 1–3 | Significant bloat — skill is 2x longer than it needs to be |
| 0 | Massive duplication or filler that wastes context budget |

## Aggregate Score

```
score = 0.30 * trigger + 0.30 * workflow + 0.20 * reference + 0.20 * conciseness
```

Compute per case, average across all cases.

## Stop Thresholds

| Condition | Action |
|-----------|--------|
| avg score ≥ 8.5 | Stop — skill is high quality |
| round ≥ 3 | Stop — diminishing returns |
| delta < 0.3 from last round | Stop — plateaued |
| score < 4.0 | Escalate — skill may need full rewrite |
