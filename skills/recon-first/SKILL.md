---
name: recon-first
description: Enforce reconnaissance before any code edit, config change, or file modification. Use when agent is about to edit files, change configurations, fix bugs, refactor code, or modify infrastructure. Prevents brute-force approaches by requiring agents to read and cite source material before acting. Cuts error rates by enforcing PPEE (Pause → Plan → Evaluate → Execute).
---

# Recon First

**Before touching any file, you must read first.**

This skill enforces a mandatory reconnaissance phase before edits. No exceptions.

## The Rule

Before ANY edit to code, config, or documentation:

1. **READ** the relevant source files (not just skim — actually read)
2. **CITE** what you read: `Source: <filepath>#L<start>-L<end>` or `Source: <filepath> — <section>`
3. **PLAN** your change in one sentence
4. **EXECUTE** only after steps 1-3 are complete

## What Counts as "Read First"

| Action | Required Reading |
|--------|------------------|
| Edit code file | Read the file (or relevant section) first |
| Fix a bug | Read the error context + the code causing it |
| Change config | Read current config + any docs explaining the keys |
| Refactor | Read all files you're about to touch |
| Add feature | Read existing patterns in the codebase |
| Infrastructure change | Read current state + relevant docs |

## Citation Format

Always include your source citation before stating your plan:

```
Source: backend/app/engine/assemble_proposal.py#L45-L67 — BRAND dict definition

Plan: Update primary color from #002B5C to #111111
```

Or for documentation:

```
Source: docs/gateway/configuration.md — "bind" section

Plan: Change gateway.bind from "0.0.0.0" to "loopback" for Tailscale serve mode
```

## Violations

These are **recon-first violations** — don't do them:

- ❌ Editing a file you haven't read this session
- ❌ Guessing at config keys without checking docs
- ❌ "I think this is how it works" without citing source
- ❌ Multiple failed attempts before reading the relevant code
- ❌ Copy-pasting solutions without understanding the context

## When to Skip (Rare)

Only skip recon-first when:
- Creating a brand new file with no existing patterns to follow
- The change is trivial AND you've edited this exact code <5 minutes ago
- Emergency rollback to a known-good state

Even then, state: `Skipping recon: <reason>`

## Enforcement

If you catch yourself about to edit without reading first: **STOP.**

Read the file. Cite it. Then proceed.

This isn't bureaucracy — it's how you avoid the 8-redeploy debugging spiral.
