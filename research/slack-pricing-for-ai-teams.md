# Slack Pricing for AI Agent Teams

*Research completed: 2026-02-01 13:05 HKT*

## Key Finding: Bots are FREE

From [Slack's official docs](https://api.slack.com/bot-users):
> "Like other APIs and integrations, **bot users are free**. Unlike regular users, the actions they can perform are somewhat limited."

## Pricing Tiers (2026)

| Plan | Monthly (annual) | Message History | Integrations | Notes |
|------|------------------|-----------------|--------------|-------|
| Free | $0 | 90 days | 10 apps | Each bot = 1 integration |
| Pro | $7.25/user | Unlimited | Unlimited | 3-user minimum ($21.75/mo) |
| Business+ | $15/user | Unlimited | Unlimited | AI features, SSO |
| Enterprise | Custom | Unlimited | Unlimited | No downgrade possible |

## Our Scenario

**Setup:** Guillermo (1 human) + Molty + 5 project leads + sub-agents

| Component | Cost |
|-----------|------|
| Guillermo | 1 paid user |
| All AI bots | **FREE** |
| **Total (Pro)** | **$21.75/mo** (3-user minimum) |

## Free Plan Limitations

- **10 integration limit** — Each bot counts as 1
- Our team: Molty + 5 leads + sub-agents = likely >10 bots
- **90-day message history** — Messages disappear after

## Alternatives

### Discord (Recommended for AI teams)
- **Cost:** $0
- **Bots:** Unlimited, free
- **Message history:** Unlimited, forever
- **API:** Full-featured, well-documented
- **Downsides:** Less "professional" perception

### Matrix (Self-hosted)
- **Cost:** Server hosting only
- **Bots:** Unlimited
- **Control:** Full data ownership
- **Downsides:** Setup complexity

## Recommendation

**For AI agent communication:** Discord

- Zero cost
- Unlimited bots
- No message limits
- Great API for automation
- Webhook support

**Use Slack for:** External client communication (if needed)

---

*Sources:*
- https://api.slack.com/bot-users
- https://slack.com/help/articles/218915077-Slacks-Fair-Billing-Policy
- https://userjot.com/blog/slack-pricing-2025-plans-costs-hidden-fees
