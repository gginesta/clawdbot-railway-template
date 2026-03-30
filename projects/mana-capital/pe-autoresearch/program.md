# PE Cash-Flow Autoresearch — Mana Capital

Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch). One thesis gets mutated. One metric decides keep/discard. Loop until convergence.

## Objective

Find the highest cash-on-cash returning private equity investment for a $50M deployment. The goal is **recurring cash distributions** — NOT capital appreciation or exit multiples. We are buying to hold and collect.

## Constraints

- **Capital:** USD $50M
- **Geography:** Global. Prefer EU, Latin America, APAC. US acceptable if yield is compelling.
- **Exclusions:** No vice (gambling, tobacco, alcohol, cannabis, weapons, adult entertainment). Everything else is fair — including agriculture, industrials, healthcare, services, tech-enabled businesses.
- **Objective function:** Maximize annual cash-on-cash yield to investors (distributions / invested capital). This is THE metric. Everything else is secondary.
- **Control:** Whatever structure maximizes cash returns — full buyout, majority stake, structured minority with strong governance. Let the math decide.
- **Operations:** Investor will be operationally involved in first 6-12 months, then hire a world-class CEO/operator. Factor in operator availability and cost.
- **Deployment:** Single acquisition or portfolio — whichever maximizes distributions. Timeline flexible.
- **Hold period:** Indefinite. This is a permanent capital vehicle. No exit planning needed.

## The Metric

**Projected Year 3 Cash-on-Cash Yield (%)** = Annual distributable cash flow / Total invested capital × 100

Higher is better. This is the ONLY metric that matters for keep/discard decisions.

Secondary tiebreakers (only when yield is within 1% of each other):
1. Revenue predictability (recurring/contracted > project-based)
2. Recession resilience
3. Operator dependency risk (lower = better)
4. Scalability via bolt-on acquisitions

## Files

- `program.md` — this file. Instructions for the agent. Do not modify during a run.
- `thesis.md` — the investment thesis. This is the file that gets mutated each round.
- `results.tsv` — experiment log. Tab-separated. Records every round's output.
- `research/round-{N}.md` — detailed research notes per round.

## Setup

1. Read this file fully.
2. Read `thesis.md` (starts as empty scaffold).
3. Initialize `results.tsv` with header row.
4. Begin the experiment loop.

## Scoring Rubric

Each sector/candidate is scored 0-100 on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Cash-on-cash yield (Yr 3) | 35% | Projected annual distributions as % of invested capital |
| Revenue predictability | 20% | % recurring/contracted revenue, customer concentration |
| Entry multiple | 15% | EV/EBITDA attractiveness vs. sector median |
| Operator risk | 10% | Ease of hiring a CEO, industry talent pool depth |
| Recession resilience | 10% | How did this sector perform in 2008-09 and 2020? |
| Scalability | 10% | Bolt-on acquisition opportunities, organic growth potential |

**Composite score** = weighted average. Round to 1 decimal.

## The Experiment Loop

LOOP FOR 6 ROUNDS MINIMUM:

### Round 1: Broad Sector Scan
- Use web search to identify 15-20 sectors known for high cash-flow yields.
- For each: estimate entry multiples, typical EBITDA margins, cash conversion rates.
- Score all sectors. Cut bottom 50%.
- Write surviving sectors to `thesis.md`.
- Log round to `results.tsv`.
- Save detailed notes to `research/round-1.md`.

### Round 2: Deep Dive on Survivors
- For each surviving sector: web search for real data.
  - Recent transaction multiples (2023-2026)
  - Typical EBITDA margins for $10-50M revenue companies
  - Cash conversion rate (FCF/EBITDA)
  - Geographic opportunities (EU, LatAm, APAC focus)
- Re-score with real data replacing estimates.
- Cut to top 6-8 sectors.
- Update `thesis.md`. Log to `results.tsv`. Save to `research/round-2.md`.

### Round 3: Stress Test
- For each surviving sector:
  - How did it perform in 2008-09 recession? 2020 COVID?
  - Regulatory risk in target geographies?
  - Customer concentration typical?
  - Operator dependency — how hard to hire a great CEO?
  - Technology disruption risk in 5-10 years?
- Apply penalty/bonus adjustments to scores.
- Re-rank. Cut to top 5.
- Update `thesis.md`. Log to `results.tsv`. Save to `research/round-3.md`.

### Round 4: Acquisition Profiles
- For top 5 sectors: define the ideal acquisition target.
  - Revenue range, EBITDA range, employee count
  - Specific company characteristics (founder-led? PE-backed? family-owned?)
  - Entry multiple range (what you'd actually pay)
  - Expected cash-on-cash yield math: purchase price → EBITDA → FCF → distributions
  - Geographic sweet spots
- Search for real examples / comparable transactions.
- Re-score with concrete numbers.
- Update `thesis.md`. Log to `results.tsv`. Save to `research/round-4.md`.

### Round 5: Radical Ideas + Combinations
- Look at near-misses from earlier rounds. Any combinations?
- Try at least 2 "radical" ideas: sectors/structures nobody's talking about.
- Consider portfolio approach: would 3x $15M deals beat 1x $45M deal?
- Platform + bolt-on strategy: buy a platform at 5-6x, add bolt-ons at 3-4x, blended yield?
- Re-score everything including new ideas.
- Update `thesis.md`. Log to `results.tsv`. Save to `research/round-5.md`.

### Round 6: Final Thesis
- Top 3 investment opportunities, fully specified.
- For each: one-page investment memo covering:
  - Sector & geography
  - Target profile
  - Entry valuation range
  - Year 1-5 cash flow projection
  - Projected cash-on-cash yield (Yr 1, Yr 3, Yr 5)
  - Key risks + mitigants
  - Operator hiring plan
  - Why this beats the alternatives
- Declare a winner.
- Update `thesis.md` with final output. Log to `results.tsv`. Save to `research/round-6.md`.

## Research Method

For EVERY claim about yields, multiples, or market data:
- Use web_search to find real sources (industry reports, deal databases, fund performance data).
- Cite sources. No made-up numbers.
- When exact data isn't available, state the assumption clearly and note confidence level.
- Prefer data from 2023-2026. Older data is context, not evidence.

## Results Format

`results.tsv` columns (tab-separated):

```
round	top_sector	yield_pct	composite_score	status	notes
```

Example:
```
1	Waste Management	18.5	82.3	keep	Strong FCF, 5-6x entry, recession-proof
1	SaaS Vertical	14.2	71.0	cut	Good recurring rev but entry multiples 12-15x kill yield
```

## Output

When all 6 rounds are complete, write the final thesis to `thesis.md` and produce a summary message suitable for sending to the investor (Guillermo) via Telegram. The summary should be:
- Concise (under 4000 chars)
- Lead with the winner and its projected yield
- Include the top 3 with key numbers
- End with recommended next steps

## IMPORTANT

- Do NOT ask for permission between rounds. Run all 6 autonomously.
- Every claim needs a web search backing it. No hallucinated market data.
- When in doubt, be conservative on yield estimates. Overpromising kills trust.
- Think like a GP pitching an LP. The numbers need to survive due diligence.
