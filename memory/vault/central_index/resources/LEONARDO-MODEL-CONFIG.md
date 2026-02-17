# Leonardo 🔵 — Model Configuration (Current)
*Last updated: 2026-02-15*

This records Leonardo's **current** `agents.defaults.model` configuration (primary + fallbacks) as set in Discord #command-center.

## Main model routing

- **Primary:** `openai/gpt-5.2` (alias: `gpt5`)

### Fallback chain (in order)
1. `openrouter/z-ai/glm-5` (alias: `glm5`)  
2. `google/gemini-2.5-flash` (alias: `flash`)  
3. `xai/grok-3` (alias: `grok`)  
4. `anthropic/claude-opus-4-6` (alias: `opus`)  
5. `openrouter/deepseek/deepseek-r1-0528:free` (alias: `deepseek`)  
6. `anthropic/claude-sonnet-4-0` (alias: `sonnet`)  

## Rationale
- Avoids **same-provider adjacency** (Anthropic back-to-back) to reduce correlated failures.
- Keeps **GLM-5** in top 3 as a strong, inexpensive alternate.

## Notes
- Image model routing is unchanged here (handled separately under `agents.defaults.imageModel`).
