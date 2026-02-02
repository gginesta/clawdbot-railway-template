# Feature Request: Pre-Message Model Routing Hook

**Status:** Draft — ready to submit to GitHub/Discord
**Target:** https://github.com/openclaw/openclaw/issues/new

---

## Title

`message:received` hook for pre-processing model selection

## Description

### Problem

Currently, there's no way to dynamically select which model handles a message based on the message content. Every message goes to the configured primary model, which:

1. **Wastes rate limits** on simple tasks (e.g., "hello" uses Opus)
2. **Prevents cost optimization** (can't route simple tasks to cheap models)
3. **Limits multi-tier architectures** (like the tiered model strategy popularized by @code_rams)

### Proposed Solution

Add a `message:received` hook that fires **before** the message is processed by the agent, allowing hooks to:

1. Inspect the incoming message content
2. Set a model override for this specific message
3. Optionally transform the message

### Example Use Case

```typescript
// hooks/task-router/handler.ts
const handler: HookHandler = async (event) => {
  const message = event.context.messageContent;
  
  // Simple keyword-based routing
  const complexKeywords = ['code', 'debug', 'plan', 'analyze', 'think hard'];
  const isComplex = complexKeywords.some(k => message.toLowerCase().includes(k));
  
  if (isComplex) {
    event.context.modelOverride = 'anthropic/claude-opus-4-5';
  } else {
    event.context.modelOverride = 'google/gemini-2.5-flash';
  }
};
```

### Event Shape (Suggested)

```typescript
{
  type: 'message',
  action: 'received',
  sessionKey: string,
  timestamp: Date,
  context: {
    messageContent: string,
    channel: string,
    senderId: string,
    modelOverride?: string,  // Hook can set this
    skipProcessing?: boolean, // Hook can abort processing
  }
}
```

### Benefits

- **Cost optimization:** Route 80% of messages to cheap models
- **Rate limit preservation:** Save premium models for complex tasks
- **Flexibility:** Users can implement their own routing logic
- **No breaking changes:** Existing setups continue to work

### Prior Art

- OpenRouter Auto Model does this at the provider level
- @code_rams implemented this manually for their "Chiti" bot
- Many users are asking for tiered model strategies

### Notes

This was listed as a "Future Event" in the hooks documentation. Would love to see it prioritized!

---

**Submitted by:** Molty (on behalf of Guillermo / @gginesta)
**Date:** 2026-02-02
