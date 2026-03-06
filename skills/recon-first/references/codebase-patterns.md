# Codebase Reconnaissance Patterns

Quick reference for where to look before editing in our main codebases.

## Proposal Studio (Brinc)

| Change Type | Read First |
|-------------|------------|
| Slide styling | `backend/app/engine/assemble_proposal.py` — BRAND dict |
| Module logic | `backend/app/engine/modules/` — relevant module file |
| API endpoints | `backend/app/api/` — route handlers |
| Frontend styling | `frontend/src/index.css` — Tailwind tokens |
| HubSpot integration | `backend/app/services/hubspot.py` |

## Cerebro

| Change Type | Read First |
|-------------|------------|
| Database schema | `prisma/schema.prisma` |
| API routes | `app/api/` — route handlers |
| Auth logic | `lib/auth.ts` or `app/api/auth/` |
| UI components | `components/` — existing patterns |
| Stripe integration | `lib/stripe.ts` + `app/api/webhooks/stripe/` |

## OpenClaw Config

| Change Type | Read First |
|-------------|------------|
| Gateway config | `openclaw.yaml` — gateway section |
| Cron jobs | `openclaw.yaml` — crons section |
| Model routing | `openclaw.yaml` — models section |
| Skills | `workspace/skills/<skill>/SKILL.md` |

## Infrastructure (Railway)

| Change Type | Read First |
|-------------|------------|
| Environment vars | Railway dashboard OR `railway variables` |
| Deploy settings | Railway service settings |
| Scaling | Current replica count + metrics |

## Memory / Docs

| Change Type | Read First |
|-------------|------------|
| Agent behavior | `AGENTS.md` + `SOUL.md` |
| Credentials | `TOOLS.md` |
| Recent decisions | `memory/YYYY-MM-DD.md` (today + yesterday) |
| Long-term context | `MEMORY.md` |

## Pattern: Unknown Codebase

When working with unfamiliar code:

1. Find the entry point (main.py, index.ts, app.py)
2. Trace the code path for your specific change
3. Read existing similar implementations
4. Check for README, CONTRIBUTING, or docs/ folder
5. Look at recent git commits for patterns

```bash
# Find relevant files
rg -l "keyword" --type py
rg -l "keyword" --type ts

# See recent changes to a file
git log --oneline -10 path/to/file

# See what's in a directory
ls -la path/to/dir/
```
