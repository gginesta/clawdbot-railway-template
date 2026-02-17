# OpenClaw Cron Job Configuration Template

## Design Principles
1. **Isolation First**: Every cron job MUST run in an isolated session
2. **Explicit Delivery**: Clear, intentional communication channels
3. **Minimal Surface Exposure**: No leaking of internal processes
4. **Robust Error Handling**: Graceful failure and logging

## Configuration Schema

```json5
{
  "id": "unique_job_identifier",
  "name": "Descriptive Job Name",
  "enabled": true,
  "schedule": {
    "kind": "cron",       // Supports: 'cron', 'at', 'every'
    "expr": "0 1 * * *",  // Cron expression
    "tz": "Asia/Hong_Kong"  // Timezone-aware
  },
  "sessionTarget": "isolated",  // MUST be 'isolated'
  "wakeMode": "now",            // 'now' or 'next-heartbeat'
  "payload": {
    "kind": "agentTurn",        // Preferred over 'systemEvent'
    "message": "Job description and exact execution instructions",
    "model": "openrouter/google/gemini-2.5-flash",  // Explicit model
    "timeoutSeconds": 180,      // Hard timeout
    "text": "Optional additional context"  // For logging/reference
  },
  "delivery": {
    "mode": "announce",         // 'announce', 'none'
    "channel": "discord",        // telegram, discord, etc.
    "to": "channel:ID_HERE",     // Specific target
    "bestEffort": true,          // Optional: continue if delivery fails
    "silent": true               // Suppress verbose logging
  }
}
```

## Best Practices

### 1. Session Isolation
- ALWAYS use `sessionTarget: "isolated"`
- Prevents leaking of internal processes
- Protects main session from unexpected interruptions

### 2. Delivery Mechanisms
- Use explicit `delivery` configuration
- Choose appropriate channel (Discord/Telegram)
- Provide specific target (channel ID or user ID)
- Set `bestEffort: true` for resilience

### 3. Model Selection
- Use explicit, full model identifiers
- Prefer OpenRouter models for reliability
- Avoid aliases (use full model path)

### 4. Error Handling
- Set reasonable `timeoutSeconds`
- Use `wakeMode: "now"` for immediate execution
- Implement logging in job script

## Example: Security Audit Cron Job

```json5
{
  "id": "weekly-security-audit",
  "name": "Weekly Security Scan",
  "schedule": {
    "kind": "cron",
    "expr": "0 3 * * 1",  // Every Monday at 3 AM
    "tz": "Asia/Hong_Kong"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Run comprehensive security audit:\n1. openclaw security audit --deep\n2. Log results\n3. Alert on new findings",
    "model": "openrouter/google/gemini-2.5-flash",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "channel:SECURITY_CHANNEL_ID",
    "bestEffort": true,
    "silent": false
  }
}
```

## Anti-Patterns to Avoid
- ❌ Using `main` as `sessionTarget`
- ❌ Omitting `delivery` configuration
- ❌ Using model aliases
- ❌ Extremely long-running jobs
- ❌ Jobs without explicit timeout

## Monitoring and Maintenance
- Regularly audit cron job configurations
- Review job performance and logs
- Update models and targets as infrastructure evolves

---

*Last Updated: 2026-02-16*
*Version: 1.0.0*