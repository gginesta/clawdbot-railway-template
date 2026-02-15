## 🤖 Model Configuration

### Primary Stack (Updated 2026-02-06)
| Role | Model | Provider | Notes |
|------|-------|----------|-------|
| **Primary** | **Claude Opus 4.6** | Anthropic | 1M context, adaptive thinking, agent teams |
| **Fallback 1** | Claude Sonnet 4.0 | Anthropic | |
| **Fallback 2** | GPT-5.3 | OpenAI Codex (OAuth) | ⏳ API "coming soon" — 5.2 backup in chain |
| **Fallback 3** | GPT-5.2 | OpenAI Codex (OAuth) | Active fallback until 5.3 API live |
| **Fallback 4** | Grok 3 | xAI | |
| **Images** | Qwen Vision | Qwen Portal (free!) | |
| **Subagents** | Qwen Coder | Cheap/fast for background work | |

### Opus 4.6 New Features
- **1M token context** (beta) — 5x larger!
- **Adaptive thinking** — Claude decides when to think deeper
- **Effort controls** — low/medium/high/max
- **Context compaction** — auto-summarize older context
- **Agent teams** — parallel Claudes (matches Pokémon Squad!)
- **128k output tokens** — larger responses

### 🔄 Model Review Rule
**On every model upgrade:**
1. Read release notes for new features
2. Check API availability (some delayed)
3. Update primary/fallback chain
4. Update sub-agent model assignments
5. Test critical paths
6. Document in `/data/workspace/docs/MODEL-UPGRADE-*.md`
7. Notify all fleet agents

### Available via OpenRouter
- `openrouter/anthropic/claude-sonnet-4`
- `openrouter/google/gemini-2.5-pro-preview` (1M context!)
- `openrouter/openai/gpt-4o`
- `openrouter/meta-llama/llama-3.3-70b-instruct`

### Available via OpenAI Direct
- `openai/gpt-4o`
- `openai/gpt-4o-mini`
- `openai/o1` (reasoning)

### Per-Agent Model Configuration

| Agent | Primary | Fallback Chain | Notes |
|-------|---------|----------------|-------|
| **Molty 🦎** | Claude Opus 4.6 | Sonnet 4 → GPT-5.2 → Grok 3 | Coordinator, heavy reasoning |
| **Raphael 🔴** | Claude Opus 4.6 | Sonnet 4 → GPT-5.2 → Grok 3 | Brinc lead |
| **Leonardo 🔵** | GPT-5.2 | GLM-5 → Gemini Flash → Grok 3 → Opus → DeepSeek R1 → Sonnet | Alternates providers (no same-provider adjacency) |

**Leonardo model change (2026-02-15):** Guillermo directed switch from Sonnet → GPT-5.2 primary. GLM-5 must be top 3 fallback. No same-provider back-to-back in fallback chain.

### Model Aliases
- `qwen` → `qwen-portal/coder-model`

---
