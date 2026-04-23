## 🤖 Model Configuration

### Molty Primary Stack (Updated 2026-04-22)
| Role | Model | Provider | Notes |
|------|-------|----------|-------|
| **Primary** | **Claude Sonnet 4.6** | Anthropic (subscription token) | `sk-ant-oat01-...` — subscription billing |
| **Fallback 1** | Gemini 2.5 Flash | OpenRouter | Fast, cheap |
| **Fallback 2** | Claude Sonnet 4.6 | OpenRouter | Same model, different provider |
| **Images** | Grok 3 | xAI | |
| **Cron** | Grok 3 Fast | xAI | Cron/background jobs |

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
| **Molty 🦎** | Claude Sonnet 4.6 (Anthropic direct) | Gemini 2.5 Flash → OR Sonnet 4.6 | Z.AI discontinued; moved to Anthropic subscription |
| **Raphael 🔴** | Claude Opus 4.6 | Sonnet 4 → GPT-5.2 → Grok 3 | Brinc lead |
| **Leonardo 🔵** | GPT-5.2 | GLM-5 → Gemini Flash → Grok 3 → Opus → DeepSeek R1 → Sonnet | Alternates providers (no same-provider adjacency) |

**Leonardo model change (2026-02-15):** Guillermo directed switch from Sonnet → GPT-5.2 primary. GLM-5 must be top 3 fallback. No same-provider back-to-back in fallback chain.

### Model Aliases
- `qwen` → `qwen-portal/coder-model`

---
