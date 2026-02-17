# Model Sanity Check SOP

Purpose: prevent gateway thrash/crashes from invalid model IDs or provider allowlists.

## When
- Before changing `agents.defaults.model.primary`
- Before adding a new model to fallbacks
- After every upstream model announcement (Opus, Sonnet, GPT-Codex)

## Steps

1. **Probe model in an isolated run** (don’t change defaults yet)
   - Spawn a short subagent with the exact model ID.
   - Success criteria: the spawn response shows `modelApplied: true` and the agent replies normally.

2. **Only then patch defaults**
   - Update `agents.defaults.model.primary` and fallbacks.

3. **Restart + re-probe**
   - After restart, re-run the same probe.

4. **If probe fails**
   - Do not keep flipping configs.
   - Roll back to last-known-good primary.
   - Record the exact error text and model ID.

## Notes
- Many failures are just **nomenclature** (e.g. `anthropic/claude-sonnet-4` vs `anthropic/claude-sonnet-4-0`).
- Availability can differ between:
  - provider API vs product UI
  - main session vs subagent policy allowlist

