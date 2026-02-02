# Task-Based Model Routing Plan

*Created: 2026-02-02 | Author: Molty*

## Goal

Implement intelligent task-based routing to:
1. **Preserve rate limits** on Anthropic (Claude Max) and OpenAI (ChatGPT Plus)
2. **Use cheap/free models** for simple tasks (80% of interactions)
3. **Escalate to Opus** only when needed (complex reasoning, coding, planning)
4. **Survive cooldowns** when rate limits are hit

**Constraint:** NO OpenRouter Auto — we want to use subscription rate limits, not API credits.

---

## Current State

| Role | Model | Cost | Issue |
|------|-------|------|-------|
| **Main session** | Claude Opus 4.5 | Subscription | Uses rate limit for "hello" |
| **Fallbacks** | Sonnet → GPT-5.2 → Grok → Llama | Mixed | Only triggers on failure |
| **Subagents** | Qwen Coder | Free | ✅ Good |
| **Heartbeats** | Opus (inherited) | Subscription | Wasteful |

**Problem:** Every message, simple or complex, hits Opus first. Burns rate limits fast.

---

## Proposed Architecture

### Tier 1: Daily Driver (80% of messages)
**Model:** `google/gemini-2.5-flash`
**Cost:** ~$0.075/1M tokens (essentially free)
**Use for:** Greetings, status checks, simple Q&A, task lists, reminders

### Tier 2: Capable Worker (15% of messages)
**Model:** `anthropic/claude-sonnet-4` or `openai/gpt-5.2`
**Cost:** Subscription rate limits
**Use for:** Writing, summarization, moderate reasoning, tool use

### Tier 3: Heavy Lifter (5% of messages)
**Model:** `anthropic/claude-opus-4-5`
**Cost:** Subscription rate limits (premium)
**Use for:** Complex planning, multi-step reasoning, coding, creative work

---

## Escalation Logic: When to Switch Models

### Option A: Keyword/Intent Detection (Simple)

Detect keywords or patterns in the user message:

| Pattern | Escalate To | Confidence |
|---------|-------------|------------|
| "code", "debug", "implement", "fix bug" | Tier 3 (Opus) | High |
| "plan", "strategy", "analyze", "compare" | Tier 2/3 | Medium |
| "research", "summarize", "explain" | Tier 2 | Medium |
| "hello", "thanks", "status", "what's next" | Tier 1 | High |

**Pros:** Simple, fast, no extra API calls
**Cons:** Keywords can be misleading, misses context

### Option B: Two-Stage Processing (Smarter)

1. **Stage 1:** Cheap model (Flash) receives message + decides if escalation needed
2. **Stage 2:** If escalation flagged, re-run with powerful model

```
User: "Help me refactor this authentication module"
  ↓
Flash: [Detects coding task] → flags ESCALATE
  ↓
Opus: [Full response with code]
```

**Pros:** Context-aware, more accurate
**Cons:** Extra latency on escalated tasks (~2-3s), still uses Flash tokens

### Option C: Explicit User Control (Manual)

User triggers escalation with commands:
- `/model opus` — switch to Opus for this task
- `/model flash` — switch back to cheap model
- `/think` — enable extended thinking (implies Opus)

**Pros:** User always in control, no guessing
**Cons:** Friction, user might forget to escalate

### Recommendation: Hybrid (A + C)

1. **Default to Flash** for all messages
2. **Auto-escalate** on obvious keywords (code, plan, analyze)
3. **User override** with `/model opus` when needed
4. **Self-escalate:** Flash can request escalation if it recognizes it's struggling

---

## Handling Missed Escalations

**Scenario:** Flash handles a complex task poorly. User gets bad answer.

### Detection Signals
- User says "that's wrong", "try again", "not helpful"
- User immediately asks follow-up clarifying question
- Flash response is unusually short or uncertain
- Flash explicitly says "I'm not sure" or "this is complex"

### Recovery Strategies

1. **Retry with escalation:**
   - On negative feedback → automatically retry with Tier 3
   - "Let me think about this more carefully..." [switches to Opus]

2. **Quality check (expensive):**
   - Run Opus as a "reviewer" on Flash's response
   - Only flag if quality is low
   - Adds latency and cost — use sparingly

3. **User education:**
   - Teach user to recognize when to use `/model opus`
   - Show model indicator in responses: `[Flash]` vs `[Opus]`

### Recommendation

- **Add model indicator** to responses so user knows which tier answered
- **Auto-retry on negative feedback** with escalation
- **Don't do quality checking** — too expensive, defeats purpose

---

## Latency Impact

| Scenario | Latency | Notes |
|----------|---------|-------|
| Flash only | ~1-2s | Fastest |
| Flash → Escalate → Opus | ~3-5s | Two model calls |
| Opus only | ~2-4s | Baseline for complex |
| Fallback (Opus timeout) | ~10-15s | Worst case |

### Mitigation
- **Streaming:** Start streaming Flash response immediately; if escalation detected mid-stream, notify user and switch
- **Parallel calls:** For obvious escalation keywords, call both Flash and Opus simultaneously, use Opus response (costs more but faster)
- **Accept latency:** Most escalations are for complex tasks where users expect longer response time

---

## Fallback Chain with Cooldowns

### Current Chain
```
Opus → Sonnet → GPT-5.2 → Grok → Llama
```

### Proposed Chain (Task-Aware)

**For Simple Tasks (Tier 1):**
```
Flash → Qwen → Llama (all free/cheap)
```

**For Complex Tasks (Tier 2/3):**
```
Opus → Sonnet → GPT-5.2 → Grok → Llama → Flash (graceful degradation)
```

### Cooldown Behavior

When a model hits rate limit:
1. **Profile rotation:** OpenClaw tries other auth profiles for same provider
2. **Cooldown backoff:** 1min → 5min → 25min → 1hr (exponential)
3. **Fallback advance:** Move to next model in chain
4. **Billing disable:** 5hr → 10hr → 24hr for billing failures

### Rate Limit Distribution Strategy

| Provider | Subscription | Daily Limit (Est.) | Assigned To |
|----------|--------------|-------------------|-------------|
| Anthropic (Claude Max) | ~$100/mo | ~1000 Opus calls | Molty (Tier 3) |
| OpenAI (ChatGPT Plus) | ~$20/mo | ~100 GPT-5.2 calls | Project Leads |
| Google (Gemini) | Free tier | ~1500 Flash calls | Everyone (Tier 1) |
| Qwen | Free | Unlimited | Subagents |

### Cross-Provider Spread

When Anthropic hits limits:
```
Opus (rate limited) → GPT-5.2 (OpenAI) → Grok (xAI) → Sonnet (try again) → Llama
```

This spreads load across providers instead of burning one subscription.

---

## Implementation Options

### Option 1: OpenClaw Native (If Supported)

Check if OpenClaw has:
- Per-message model hooks
- Intent classification middleware
- Dynamic model selection

*Status: Need to research OpenClaw hooks/middleware*

### Option 2: AGENTS.md Instructions

Add to system prompt:
```markdown
## Model Selection Protocol

You are currently running on {model}. 

For simple tasks (greetings, status, basic Q&A): 
- Handle directly

For complex tasks (coding, planning, analysis):
- If you're on Flash/cheap model, respond: "[ESCALATE] This task needs more capability"
- The system will retry with a more powerful model

Indicate your current model in responses: [Flash] or [Opus]
```

*Pros:* No code changes
*Cons:* Model must cooperate, unreliable

### Option 3: Custom Middleware/Hook

Write a pre-processing hook that:
1. Analyzes incoming message
2. Classifies intent
3. Selects appropriate model
4. Forwards to OpenClaw with model override

*Pros:* Full control
*Cons:* Requires development

### Option 4: Per-Channel Models

Configure different models per channel:
- Telegram (groups): Flash
- Telegram (DM with Guillermo): Opus
- Webchat: Opus

*Pros:* Simple config
*Cons:* Doesn't adapt to task complexity

### Recommendation: Start with Option 2 + 4

1. **Set Flash as default** for main session
2. **Add escalation instructions** to AGENTS.md
3. **Configure DM channel** to use Opus
4. **User can `/model opus`** for explicit escalation
5. **Monitor and iterate** based on experience

---

## Configuration Changes

### Heartbeat (Use Cheap Model)
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h",
        "model": "google/gemini-2.5-flash"
      }
    }
  }
}
```

### Default Model (Flash as Daily Driver)
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "google/gemini-2.5-flash",
        "fallbacks": [
          "qwen-portal/coder-model",
          "openrouter/meta-llama/llama-3.3-70b-instruct"
        ]
      }
    }
  }
}
```

### Per-DM Override (Opus for Direct Chats)
```json
{
  "channels": {
    "telegram": {
      "dm": {
        "model": "anthropic/claude-opus-4-5"
      }
    },
    "webchat": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

*Note: Need to verify if per-channel model override is supported*

---

## Metrics to Track

1. **Model distribution:** % messages handled by Flash vs Opus
2. **Escalation rate:** How often Flash triggers escalation
3. **Retry rate:** How often user asks to retry/rephrase
4. **Rate limit hits:** Per provider, per day
5. **User satisfaction:** Feedback on response quality

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flash gives poor answer | User frustration | Clear model indicator, easy escalation |
| Over-escalation | Burns Opus limits | Tune keyword detection, review patterns |
| Missed escalation | Bad experience | Auto-retry on negative feedback |
| Latency on escalation | Slower responses | Accept for complex tasks, stream when possible |
| Config complexity | Maintenance burden | Document thoroughly, test incrementally |

---

## Next Steps

1. [ ] **Configure heartbeat** to use Gemini Flash
2. [ ] **Test Gemini Flash** as primary model for simple tasks
3. [ ] **Add model indicator** to responses (if possible)
4. [ ] **Document escalation keywords** in AGENTS.md
5. [ ] **Monitor for 1 week** before further changes
6. [ ] **Research OpenClaw hooks** for smarter routing

---

## Appendix: Model Comparison

| Model | Input Cost | Output Cost | Context | Speed | Best For |
|-------|------------|-------------|---------|-------|----------|
| Gemini 2.5 Flash | $0.075/1M | $0.30/1M | 1M | Very Fast | Simple tasks |
| Claude Sonnet 4 | $3/1M | $15/1M | 200K | Medium | General work |
| Claude Opus 4.5 | $15/1M | $75/1M | 200K | Slower | Complex reasoning |
| GPT-5.2 | Subscription | — | 266K | Medium | Coding, analysis |
| Qwen Coder | Free | Free | 128K | Fast | Background tasks |
| Llama 3.3 70B | Free (OR) | Free (OR) | 128K | Medium | Fallback |

---

*This document will be updated as we implement and iterate.*
