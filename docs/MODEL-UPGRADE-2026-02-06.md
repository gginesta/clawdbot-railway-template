# Model Upgrade Notes — 2026-02-06

## Upgraded Models

| Model | From | To | Status |
|-------|------|-----|--------|
| **Primary (Molty/Raphael)** | Claude Opus 4.5 | **Claude Opus 4.6** | ✅ Live |
| **Fallback 1** | Claude Sonnet 4.0 | Claude Sonnet 4.0 | ✅ (unchanged) |
| **Fallback 2** | GPT-5.2 | **GPT-5.3** | ⏳ API "coming soon" — keeping 5.2 as backup |
| **Sub-agents** | Qwen Coder | Qwen Coder | ✅ (unchanged, cost-effective) |

---

## Claude Opus 4.6 — Key Features

### 🎯 Core Improvements
- **1M token context window** (beta) — 5x larger than Opus 4.5!
- **128k output tokens** — larger outputs in single requests
- Plans more carefully, sustains agentic tasks longer
- Better at large codebases, code review, debugging
- Less "context rot" — 76% on MRCR v2 vs 18.5% for Sonnet 4.5

### 🛠️ New API Features

| Feature | Description | TMNT Implication |
|---------|-------------|------------------|
| **Adaptive Thinking** | Claude decides when deeper reasoning helps | Can optimize cost vs quality automatically |
| **Effort Controls** | low/medium/high (default)/max | Use `low` for simple tasks, `max` for complex |
| **Context Compaction** | Auto-summarizes older context | Longer sessions without hitting limits |
| **Agent Teams** | Multiple Claudes working in parallel | Matches our Pokémon Squad pattern! |

### 📊 Benchmarks (vs competition)
- **Terminal-Bench 2.0**: #1 (agentic coding)
- **Humanity's Last Exam**: #1 (complex reasoning)
- **GDPval-AA**: +144 Elo vs GPT-5.2, +190 vs Opus 4.5
- **BrowseComp**: #1 (finding info online)

---

## GPT-5.3-Codex — Key Features

### 🎯 Core Improvements
- Combines GPT-5.2-Codex (coding) + GPT-5.2 (reasoning)
- **25% faster** than 5.2
- First model that helped create itself
- Interactive steering — talk to it *while* it works
- State-of-the-art on SWE-Bench Pro, Terminal-Bench 2.0, OSWorld

### ⚠️ API Status
- Available via: Codex app, CLI, IDE extension, web
- API access: **"Coming soon"** — not live yet
- Our `openai-codex/gpt-5.3` failed with "model not allowed"
- Keeping `openai-codex/gpt-5.2` as active fallback

---

## Agent Teams Pattern (from Anthropic engineering blog)

Anthropic built a 100k-line C compiler using 16 parallel Claudes. Key learnings for TMNT:

### Architecture Insights

1. **Task Locking via Git**
   - Agents claim tasks by writing lock files
   - Git sync prevents duplicates
   - Maps to our Discord channel ownership pattern

2. **Multiple Agent Roles** (matches our Pokémon Squad!)
   - Main problem solvers (Squirtle, Charmander, Bulbasaur)
   - Code quality (Mewtwo)
   - Documentation (Jigglypuff)
   - Performance (Machamp)
   - Specialized domains (Arcanine, Porygon, etc.)

3. **Test Harness Design**
   - High-quality tests are critical
   - Avoid context pollution — short outputs, log to files
   - Time blindness — need progress tracking with random sampling
   - Use oracle comparisons for parallelization

4. **Session Loop Pattern**
   ```bash
   while true; do
     claude --dangerously-skip-permissions \
       -p "$(cat AGENT_PROMPT.md)" \
       --model claude-opus-4-6
   done
   ```

### Implications for TMNT

| Their Pattern | Our Implementation |
|---------------|-------------------|
| Lock files in `current_tasks/` | Discord channel ownership |
| Multiple agent roles | Pokémon Squad (13 sub-agents) |
| Oracle comparison | Existing tests + human review |
| Session loops | OpenClaw cron + sessions_spawn |

---

## Sub-Agent Model Strategy

### Updated Recommendations

| Role | Current Model | Recommended | Notes |
|------|---------------|-------------|-------|
| **Spec Writer (Squirtle)** | GPT-5.2 | **GPT-5.3** when available | Complex planning |
| **Builder (Charmander)** | GPT-5.2 | **GPT-5.3** when available | Agentic coding |
| **Researcher (Bulbasaur)** | Gemini Flash | Gemini Flash | Fast + cheap for research |
| **Strategist (Alakazam)** | Claude Sonnet | **Claude Sonnet 4.0** | Complex decisions |
| **Code Reviewer (Mewtwo)** | Claude Sonnet | **Claude Sonnet 4.0** | Precision matters |
| **Security (Arcanine)** | Gemini Flash | Gemini Flash | Fast audits |
| **Data Wrangler (Porygon)** | Qwen | Qwen | Cost-effective |
| **Writer (Jigglypuff)** | Claude Sonnet | **Claude Sonnet 4.0** | Quality writing |
| **Scheduler (Abra)** | Qwen | Qwen | Simple scheduling |
| **Monitor (Electrode)** | Qwen | Qwen | Quick alerts |
| **Batch (Machamp)** | GPT-5.2 | **GPT-5.3** when available | Parallel work |
| **Flex (Eevee)** | Gemini Flash | Gemini Flash | Adaptable |
| **Marketing (Pikachu)** | Claude Sonnet | **Claude Sonnet 4.0** | Brand voice |

### Cost Tiers
- **Premium (complex tasks)**: Opus 4.6, GPT-5.3
- **Standard (quality tasks)**: Sonnet 4.0, GPT-5.2
- **Economy (simple tasks)**: Gemini Flash, Qwen

---

## Maintenance Rule

**🔄 REVIEW MODELS ON EVERY UPGRADE**

When a new model releases:
1. Read release notes for new features
2. Check API availability (some have delayed rollout)
3. Update primary/fallback chain
4. Update sub-agent model assignments
5. Test critical paths
6. Update this doc + MEMORY.md
7. Notify all fleet agents

---

## Files Updated

- `/data/.openclaw/openclaw.json` — primary model + fallbacks
- `/data/workspace/docs/MODEL-UPGRADE-2026-02-06.md` — this file
- `/data/workspace/MEMORY.md` — model config section
- Sent webhook to Raphael with upgrade instructions

---

*Last updated: 2026-02-06 03:05 UTC by Molty 🦎*
