# Email Triage Process

*Last updated: 2026-03-11*

## Summary

Guillermo wants email triage, not just unread counts. The morning briefing should not show "Unread: 82" — it causes anxiety without being actionable.

## Current State

- **CLI:** gog v0.11.0 works for Gmail access (gws has auth issues)
- **Account:** ggv.molt@gmail.com
- **Briefing:** Now hides raw unread count, only shows highlights

## Triage Categories

| Category | Action | Mark Read? |
|----------|--------|------------|
| Self-sent (from Guillermo) | Archive | Yes |
| Automated (Google, newsletters) | Archive | Yes |
| Active threads (awaiting reply) | Keep visible | No |
| New from VIPs | Surface in briefing | No |
| School/Family | Keep visible | No |

## Implementation TODO

1. [ ] Fix gws CLI auth (version mismatch?)
2. [ ] Add automated triage cron (mark self-sent as read)
3. [ ] Add VIP sender list for surfacing
4. [ ] Integrate with morning briefing highlights

## VIP Senders (surface in briefing)
- stephanie@ (wife)
- meiling.yik@yca.com.hk (accountant)
- raeniel@imsg.com.hk (auditor)
- @guidepost.hk (school)
- @brinc.io (work)

## Commands

```bash
# Search unread
GOG_KEYRING_PASSWORD=molty2026 gog gmail messages search "is:unread newer_than:7d" --max 20

# Mark thread as read
GOG_KEYRING_PASSWORD=molty2026 gog gmail thread modify <threadId> --remove UNREAD

# Get message details
GOG_KEYRING_PASSWORD=molty2026 gog gmail get <messageId>
```
