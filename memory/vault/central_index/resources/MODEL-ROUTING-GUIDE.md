# TMNT Squad — Official Model Routing Guide
*Effective: 2026-02-10 | Approved by: Guillermo*

## Model Assignment

| Need | Model | Alias | Provider |
|------|-------|-------|----------|
| Main session | Claude Opus 4.6 | `opus` | Anthropic |
| Sub-agents (heavy) | GPT-5.3 | `codex` | OpenAI Codex (OAuth) |
| Fast web search | Perplexity Sonar Pro | `sonar` | OpenRouter |
| Deep research | Perplexity Deep Research | `deep-research` | OpenRouter |
| Quick/cheap tasks | Qwen Coder | `qwen` | Qwen Portal (free) |
| Heartbeats | Gemini 2.5 Flash | `flash` | Google |
| X/Twitter data | Grok 3 | `grok` | xAI |
| Last resort fallback | Grok 3 | `grok` | xAI |

## Rules

1. **Do NOT use Grok for sub-agent tasks** — it acknowledges then exits without executing (lesson #39)
2. **Use Sonar instead of Brave** for web searches when accuracy matters
3. **Use Deep Research** for thorough multi-source reports (market research, competitive analysis, due diligence)
4. **Grok is ONLY for** X/Twitter-native research and last-resort fallback
5. **Default sub-agent model:** Codex 5.3 → 5.2 → Opus (fallback chain)

## When to Use Perplexity

| Scenario | Model |
|----------|-------|
| Quick factual lookup | `sonar` |
| "What's happening with X lately?" | `sonar` |
| "Research topic X thoroughly" | `deep-research` |
| Recurring "what's new" monitoring | `sonar` (fast, cheap) |
| One-off deep dive reports | `deep-research` |
| Specific URL scraping | `web_fetch` (free) |
| General knowledge | Main model (no search needed) |

## Config Requirements

For each agent to use these models, their `openclaw.json` needs:
1. `openai-codex` in `models.providers` (with baseUrl!)
2. `openai-codex:default` in `auth.profiles` (OAuth)
3. Perplexity models in `openrouter.models` array
4. ALL models in `agents.defaults.models` allowlist

⚠️ OAuth providers MUST have `models.providers` entries — not just `auth.profiles` — or you get "model not allowed" errors.
