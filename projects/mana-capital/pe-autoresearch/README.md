# PE Cash-Flow Autoresearch — Mana Capital

## What This Is
Autonomous PE research loop inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch). Instead of optimizing an LLM's val_bpb, we're optimizing for **cash-on-cash yield** on a $50M private equity deployment.

## Origin
- **Idea:** Guillermo (2026-03-30), triggered by seeing people adapt Karpathy's autoresearch for non-ML use cases (conversion optimization, stock picks)
- **First run:** 2026-03-30, Sonnet 4.6, 6 rounds

## How It Works

### The Karpathy Pattern
One file gets mutated. One metric decides keep/discard. Loop until convergence.

| Karpathy (LLM training) | Mana Capital (PE research) |
|---|---|
| `train.py` — code that gets edited | `thesis.md` — investment thesis that gets refined |
| `val_bpb` — lower is better | **Cash-on-cash yield %** — higher is better |
| 5-min GPU training run | Web research + scoring per round |
| Keep/discard based on metric | Keep/discard sectors based on yield + risk |
| `program.md` — agent instructions | `program.md` — research instructions |
| `results.tsv` — experiment log | `results.tsv` — round-by-round scoring |

### Round Structure (6 rounds)
1. **Broad scan** — 15-20 sectors, score, cut bottom 50%
2. **Deep dive** — Real market data on survivors, re-score, cut to 6-8
3. **Stress test** — Recession, regulatory, operator risk. Cut to top 5
4. **Acquisition profiles** — Specific target characteristics, entry math
5. **Radical ideas** — Combinations, near-misses, portfolio vs single
6. **Final thesis** — Top 3 with full investment memos, declare winner

### Key Design Decisions
- Every yield/multiple claim must be backed by web search (no hallucinated data)
- Conservative estimates preferred (must survive due diligence)
- Scoring rubric: yield 35%, revenue predictability 20%, entry multiple 15%, operator risk 10%, recession resilience 10%, scalability 10%

## Files
```
pe-autoresearch/
├── README.md           # This file
├── program.md          # Agent instructions (the "skill")
├── thesis.md           # The mutating output (final thesis here)
├── results.tsv         # Round-by-round scoring log
└── research/
    ├── round-1.md      # Broad sector scan notes
    ├── round-2.md      # Deep dive notes
    ├── round-3.md      # Stress test notes
    ├── round-4.md      # Acquisition profile notes
    ├── round-5.md      # Radical ideas notes
    └── round-6.md      # Final thesis notes
```

## Constraints (from Guillermo)
- **Capital:** $50M
- **Objective:** Maximize cash-on-cash yield (distributions, not exits)
- **Geography:** Global, prefer EU / LatAm / APAC
- **Exclusions:** No vice
- **Operations:** Involved first 6-12 months, then hire world-class operator
- **Hold period:** Indefinite (permanent capital)

## Run 1 Results (2026-03-30)
- **Model:** Sonnet 4.6
- **Runtime:** 17 minutes, 6 rounds
- **Sectors scanned:** 18+ → cut to 5 → final 3
- **Winner:** Pest Control Platform (14.2% Yr3 CoC yield, unlevered)
- **Quality:** Good. Real data sourced, conservative estimates, proper scoring progression.
- **Cost:** ~41K output tokens, very efficient

## Improvements for Next Run

### What worked well
- [x] 6 rounds was the right number — convergence happened by Round 4, Rounds 5-6 added portfolio strategy + stress testing
- [x] Scoring rubric forced structured evaluation, not vibes
- [x] Keep/discard pattern prevented thesis drift
- [x] Web search requirement prevented hallucinated data

### What to improve
- [ ] **Add a "devil's advocate" round** — dedicated round where agent tries to KILL the thesis. Find every reason it fails.
- [ ] **Parallel sector deep-dives** — Round 2 could run multiple subagents in parallel (one per sector) for faster, deeper research
- [ ] **Real transaction database** — scrape PitchBook/CB Insights/Crunchbase for actual recent deal comps, not just industry reports
- [ ] **Geography-specific rounds** — current run was US-heavy despite LatAm/APAC preference. Add explicit geographic scoring.
- [ ] **Operator hiring research** — dedicated step to validate that world-class operators actually exist and can be recruited in the target sector
- [ ] **Model comparison** — run same program on Opus vs Sonnet vs Flash and compare output quality. Sonnet was fine but Opus might catch nuances.
- [ ] **Sensitivity analysis** — add a round that stress-tests yield assumptions (what if entry multiples are 1x higher? what if margins compress 5%?)
- [ ] **Track data quality** — flag which numbers are from real sources vs. estimates. Current run mixed both.
- [ ] **Longer time budget** — 17 min was fast. Allow 45-60 min for deeper web research per round.
