# Fleet Timezone Standard

**Effective:** 2026-02-08
**Standard:** Asia/Hong_Kong (HKT, UTC+8)

## Why
Guillermo is in HKT. All agents should think and display times in HKT natively instead of converting from UTC.

## Setup (every agent, every deploy)
```bash
ln -sf /usr/share/zoneinfo/Asia/Hong_Kong /etc/localtime
```

Verify: `date` should show HKT.

## Notes
- Railway containers default to UTC — this must be set on every deploy/restart
- Add to Dockerfile or startup script for persistence
- No more "tonight" when it's morning, no more UTC-brain
