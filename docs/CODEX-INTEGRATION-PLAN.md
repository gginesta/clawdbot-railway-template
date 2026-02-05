# OpenAI Codex Integration Plan (TMNT Squad)

**Audience:** Guillermo (principal), Molty 🦎 (coordinator), Raphael 🔴 (Brinc lead), future leads (Leonardo 🔵, Donatello 🟣, Michelangelo 🟠)

**Goal:** Add OpenAI Codex (cloud agent + GitHub-native workflows) to the TMNT Squad so large projects can be decomposed, executed in parallel, reviewed safely, and merged/deployed with minimal overhead—while keeping OpenClaw as the team’s coordination “operating system.”

---

## 0) Executive summary (what changes, in one page)

### The big shift
- **OpenClaw stays the coordinator layer** (planning, prompting standards, cross-project orchestration, Discord/Todoist/Notion glue, sub-agent spawning).
- **Codex becomes the “GitHub-native implementer”** (issue → isolated worktree → commits → PR → review queue → merge).

### Why this matters for large projects
Codex adds three things we currently have only partially:
1. **Worktree-level git isolation per task** (each issue runs in its own sandbox and branch).
2. **Native GitHub workflows** (tag/assign Codex from issues/PRs; Codex opens PRs).
3. **Built-in review queue** (human-in-the-loop before merge, plus strong traceability via logs/test output citations).

### The operating rule
- If a task’s output should be a **PR**, and it can be **well-scoped with clear acceptance criteria**, it’s a Codex task.
- If a task is **coordination-heavy**, **multi-repo**, **ambiguous**, **requires internal secrets / systems access**, or is **not PR-shaped**, it stays in OpenClaw (or is done by a human + OpenClaw).

---

## 1) Strategic assessment

### 1.1 Where Codex fits vs where OpenClaw sub-agents fit

#### Codex is best at
- **PR-shaped work**: features, bug fixes, refactors, test writing, docs updates that end as a pull request.
- **Parallel execution**: multiple issues in the same repo tackled simultaneously (each in its own cloud sandbox).
- **Repo-local reasoning**: understanding a codebase by reading files, running tests, and iterating until green.
- **GitHub-native review flows**: automatic code review, “tag @codex” patterns, PR proposals.

#### OpenClaw (our current system) remains best at
- **Orchestration across tools**: Discord → Todoist → Notion → GitHub, plus internal team routing.
- **Spec shaping & decomposition**: turning product intent into issues, milestones, acceptance criteria.
- **Long-running coordination**: status reporting, dependency management, reconciliation across PRs.
- **System integrations we control**: Syncthing context sharing, skills system, cron jobs, internal bots.
- **Sensitive operations**: anything that touches production secrets, billing, customer data, or privileged infra.

#### Key insight (for our architecture)
Codex should not replace OpenClaw sub-agents; it **specializes** them.
- **OpenClaw = program manager + glue + safety rails**
- **Codex = implementation agent that speaks GitHub natively**

#### Important distinction: “Codex the model” vs “Codex the GitHub agent”
We will use **three** Codex-shaped capabilities, with different strengths:

1. **Codex Cloud (ChatGPT Codex agent + GitHub integration)**
   - *Best for:* issue → sandbox → branch → PR, parallel work, review queue.
   - *This is the main integration target of this plan.*

2. **Codex CLI / API-key mode (token-priced, local execution)**
   - *Best for:* automation in CI, quick local edits, scripted workflows.
   - *Limitation:* no cloud features like GitHub automatic PR review/creation (per OpenAI’s Codex pricing docs).

3. **GPT-5.2-Codex model via OpenClaw (already in our config)**
   - *Best for:* “pair programming” inside OpenClaw sessions, code generation, refactors, review assistance.
   - *Limitation:* OpenClaw does not automatically give us Codex Cloud’s per-task git worktrees + GitHub-native PR flow.

### 1.2 Decision framework: “Use Codex when X, use OpenClaw sub-agents when Y”

Use this as a fast triage checklist.

#### Use Codex when…
- The work can be expressed as:
  - a **GitHub issue** with **acceptance criteria**
  - a **definition of done** (tests pass, lint pass, docs updated)
- The repo has:
  - deterministic setup commands
  - runnable tests/lint/typecheck
- You want:
  - **parallelization** (multiple PRs in flight)
  - isolated branches per task
  - reviewable diffs with evidence (test logs)

Examples from our roadmap:
- Smart Scheduling Engine: implement modules (calendar provider adapters, rules engine, DB migrations, API endpoints, test suites).
- Unbrowse DIY: implement next phases as discrete PRs (capture pipeline refinements, backfill jobs, schema evolution).
- WebClaw customization: implement UI components, auth flows, configuration, docker hardening.

#### Use OpenClaw sub-agents when…
- The task is **not PR-shaped**:
  - strategy, research, spec writing, stakeholder comms
- It requires **non-GitHub context**:
  - Notion databases, Todoist triage rules, Discord governance
- It requires **high-trust credentials**:
  - production API keys, CRM tokens, Railway secrets
- You need **interactive debugging** against live systems.

Examples:
- Morning Briefing: deployment coordination + cron scheduling + environment variables validation.
- Whoop integration: initial research, rate limit policy interpretation, data privacy plan.
- Brinc HubSpot: deciding pipeline stages, object model mapping, governance with sales ops.

### 1.3 Cost analysis (Codex vs our current model costs)

Because pricing and limits can evolve, we’ll manage cost with **measurable units**:
- **Per PR** (cloud task + code review)
- **Per 1M tokens** (API usage)
- **Per seat** (Plus/Pro/Business plans)

#### What OpenAI publishes for Codex (as of 2026-02-05)
From OpenAI’s Codex pricing page (developers.openai.com):
- Plans include **Local Messages / 5h**, **Cloud Tasks / 5h**, and **Code Reviews / week**.
- Example limits shown on that page:
  - **Plus**: 45–225 local messages / 5h; 10–60 cloud tasks / 5h; 10–25 code reviews / week
  - **Pro**: 300–1500 local messages / 5h; 50–400 cloud tasks / 5h; 100–250 code reviews / week
- Credit averages (for flexible usage) shown on that page:
  - GPT-5.2(-Codex) **local** task ≈ ~5 credits
  - GPT-5.2(-Codex) **cloud** task ≈ ~25 credits
  - **Code review** (per PR) ≈ ~25 credits

From OpenAI API pricing (platform.openai.com/docs/pricing):
- **gpt-5.2-codex** (Standard): $1.75 / 1M input tokens, $14.00 / 1M output tokens (cached input $0.175)
- **gpt-5.1-codex-mini** (Standard): $0.25 / 1M input tokens, $2.00 / 1M output tokens
- **codex-mini-latest** (Standard): $1.50 / 1M input tokens, $6.00 / 1M output tokens

> Note: ChatGPT seat pricing (e.g., Plus/Pro $/month) is displayed on chatgpt.com/pricing but may be dynamically rendered; treat seat costs as “check current price” at time of purchase.

#### Practical cost guidance for TMNT
1. **Default for large projects**: treat Codex cloud as a “PR factory.” Measure cost as **credits per PR** + **human review time saved**.
2. **Use mini models for breadth**:
   - Use **gpt-5.1-codex-mini** for quick edits, tests, docs, small refactors.
   - Reserve **gpt-5.2-codex** for multi-file changes, tricky debugging, or tasks needing stronger reasoning.
3. **Cap risk and spend**:
   - branch protection + required review ensures we never pay twice for bad merges.
   - label/queue discipline reduces rework loops.

#### How we’ll compare against current OpenClaw costs (practical)
- For OpenClaw-driven coding, track:
  - model used (Claude vs GPT-5.2-Codex)
  - rough token counts (where available)
  - engineer time spent reviewing/integrating
- For Codex Cloud, track:
  - PR count and cycle time
  - rework loops (how many follow-up prompts)
  - credits consumed (where visible in Codex usage dashboard)

**We declare success** when Codex reduces *human integration time* and/or enables parallelism that shortens overall delivery—even if raw token costs are similar.

#### A simple break-even heuristic
Codex is worth it when it saves:
- **≥30–60 minutes of senior engineering time per PR**, or
- it enables parallelism that shortens delivery by **days**, especially on multi-phase projects.

---

## 2) Workflow design (spec → Codex agents → review → merge → deploy)

### 2.1 Canonical “Large Project” flow

**A. Spec & decomposition (OpenClaw-led)**
1. Spec lives in **Notion** (product intent, constraints, milestones).
2. Molty converts spec into:
   - GitHub **Milestones** (Phase 1/2/3…)
   - GitHub **Issues** (PR-sized chunks)
   - clear acceptance criteria + test plan per issue.
3. Todoist tracks *human coordination tasks* (approvals, stakeholder decisions), not every code micro-task.

**B. Execution (Codex-led)**
4. For each issue marked `codex-ready`, Molty (or the project lead) triggers Codex:
   - assign issue to Codex / tag @codex (depending on integration mode)
   - attach constraints (files to touch, style, commands to run).
5. Codex runs in isolated sandbox/worktree:
   - pulls repo
   - applies edits
   - runs tests/lint/typecheck
   - commits
   - opens PR referencing the issue.

**C. Review (Human-led + optional Codex review)**
6. PR enters **review queue**.
7. Required checks:
   - CI green (GitHub Actions)
   - human review by lead (Raphael for Brinc repos; Molty for infra; Guillermo for product-level acceptance)
8. Optional: request Codex auto-review on PRs for fast first-pass issues.

**D. Merge & deploy (OpenClaw-led)**
9. Merge via protected branch rules.
10. OpenClaw automation posts:
    - Discord update (PR merged, release notes)
    - Notion status update (phase progress)
    - Todoist follow-ups (deploy, verify, monitor).
11. Deploy (Railway / Docker) + run smoke tests.

### 2.2 Integration with GitHub, Discord, Todoist, Notion

#### Source of truth rules (reduce tool sprawl)
- **GitHub** = source of truth for **code work** (issues/PRs).
- **Notion** = source of truth for **product specs + milestone tracking**.
- **Todoist** = source of truth for **human actions** (approvals, coordination, reminders).
- **Discord** = real-time **ops + coordination** (status, blockers, handoffs).

#### Recommended linking conventions
- Every Notion deliverable links to:
  - the GitHub milestone
  - the “tracking issue” (one per phase)
- Every GitHub issue links back to:
  - the Notion spec section
  - a Todoist item only if human action is required.
- Discord messages always include:
  - issue/PR link(s)
  - current status label (e.g., `codex-running`, `needs-review`, `blocked`).

#### GitHub label/state machine (recommended)
To keep multi-agent parallel work sane, we standardize labels that act like a lightweight kanban:

**Issue labels**
- `status:triage` → created, not yet decomposed
- `status:scoped` → acceptance criteria + test plan exist
- `codex-ready` → safe to dispatch to Codex
- `codex-running` → Codex is currently executing
- `status:blocked` → missing decision, missing interface, failing CI without clear fix
- `status:needs-review` → PR open, awaiting human review
- `status:done` → merged and verified

**PR labels**
- `from:codex` (always)
- `needs-review` (always on open)
- `risk:low|med|high`
- `area:<module>`

**Discord automation trigger points (later Phase 3)**
- Issue becomes `codex-ready` → post to relevant Discord channel
- PR opened with `from:codex` → post link + reviewer assignment
- PR merged → post release note + follow-up checklist link

### 2.3 How Molty orchestrates Codex tasks

Molty’s role becomes a repeatable “delegation protocol.”

#### Molty’s Codex delegation checklist (per issue)
1. **Is it PR-sized?** (< ~300–600 LOC net change; 1–3 modules; clear boundary)
2. **Acceptance criteria present?** (behavior, tests, docs)
3. **Commands known?** (`pnpm test`, `pytest`, `make lint`, etc.)
4. **Secrets avoided?** (no real API keys; use mocks)
5. Add labels:
   - `codex-ready`
   - `area:<module>` (e.g., `area:scheduling-engine`)
   - `risk:low|med|high`
6. Trigger Codex and set a **timebox**:
   - first pass expected within 30–90 minutes
   - if stuck, Codex comments with blockers.

#### Molty’s integration responsibilities
- Maintain repo-level **AGENTS.md** templates.
- Maintain a lightweight **issue template** for Codex-ready work.
- Keep a weekly “Codex throughput” dashboard:
  - PRs opened, merged, reverted
  - average review time
  - defect rate post-merge

### 2.4 How project leads use Codex (Raphael, Leonardo, etc.)

#### Project lead responsibilities
- Own the domain AGENTS.override.md rules.
- Decide which tasks are safe to delegate.
- Review & merge PRs (or assign reviewers).

#### Practical lead workflow
- Lead creates issues + marks `codex-ready`.
- Lead assigns to Codex.
- Lead reviews PR diffs + runs staging verification.
- Molty handles cross-tool updates (Discord/Todoist/Notion) unless lead requests otherwise.

---

## 3) Repository strategy

### 3.1 AGENTS.md patterns for our repos

Codex supports **layered** instructions via AGENTS.md and AGENTS.override.md, discovered from global → repo root → nested directory (up to size limits).

#### Pattern 1 — Root `AGENTS.md` (required in every active repo)
Keep this *short* and *operational*. Example skeleton:

```markdown
# AGENTS.md (Repo Root)

## Goal
This repo is part of the TMNT Squad (Guillermo + Molty + Raphael). Prioritize small, reviewable PRs.

## Dev environment
- Node: 22.x (or specify)
- Package manager: pnpm

## Setup
- Install: pnpm install
- Test: pnpm test
- Lint: pnpm lint
- Typecheck: pnpm typecheck

## PR rules
- Prefer 1 issue → 1 PR.
- Update or add tests for behavior changes.
- Do not add new production dependencies without explicit approval in the PR description.

## Security
- Never print, commit, or request secrets.
- If an integration needs credentials, use mocks and document required env vars in `.env.example`.
```

#### Pattern 2 — Module overrides (only when necessary)
Example: `services/hubspot/AGENTS.override.md` for Brinc integrations.
- Put “special rules” close to the code.
- Keep override limited to what differs.

#### Pattern 3 — Global defaults (Molty-maintained)
Codex supports a global `~/.codex/AGENTS.md` for consistent behavior across repos.
Recommendation:
- Molty maintains global agreements (small PRs, test-first, no new deps without approval, log conventions).

### 3.2 Branch/PR conventions for Codex-generated code

Standardize so humans can scan quickly.

#### Branch naming
- `codex/<issue-number>-<short-slug>`
  - Example: `codex/123-scheduler-rule-engine`

#### PR title
- `Codex: <issue title>`

#### PR description template (required)
- **What changed** (bullets)
- **Why** (link to issue/spec)
- **How to test** (exact commands)
- **Risks / roll-back**
- **Open questions**

#### Labels
- `from:codex`
- `needs-review`
- `risk:low|med|high`
- `area:<module>`

#### Repo plumbing that makes Codex dramatically better (do this once per repo)
- `.github/pull_request_template.md` with the PR checklist (What/Why/How to test/Risks)
- `.github/ISSUE_TEMPLATE/codex-ready.md` (Appendix A)
- `CODEOWNERS` to auto-request the right reviewer (Raphael for Brinc, Molty for infra)
- Branch protection on `main`:
  - require PR
  - require CI
  - require 1–2 approvals depending on `risk:*`
- `CONTRIBUTING.md` with:
  - how to run tests
  - how to run lint
  - how releases/deploys happen

### 3.3 Structuring repos so Codex is effective

Codex performs best when repos are “agent-friendly.” For each active repo, we should add:

1. **Single-command setup**
   - `make setup` or `./scripts/setup.sh`
2. **Single-command verification**
   - `make verify` runs lint + typecheck + tests
3. **Fast unit test layer**
   - keep a <2–5 minute suite for agent iteration
4. **Clear boundaries**
   - `src/`, `tests/`, `docs/`, `scripts/`
5. **Golden paths**
   - examples in `docs/` showing “how to add a new provider,” etc.

> If Codex can’t reliably run tests, it will produce larger diffs, more rework, and higher human review burden.

### 3.4 Monorepo vs multi-repo considerations (for TMNT)

#### Monorepo advantages (for Codex)
- Easy cross-module refactors.
- Single PR can update shared types/utilities.

#### Monorepo risks (for Codex)
- Context size balloons; instructions and navigation become harder.
- More CI complexity; slower feedback.

#### Multi-repo advantages (for Codex)
- Smaller context → better task focus.
- Clean isolation by domain (Brinc vs OpenClaw vs personal automations).

#### Recommended position for TMNT (pragmatic)
- Keep **separate repos by domain** (OpenClaw infra, Brinc automations, personal systems).
- Within a domain repo, allow a “mini-monorepo” only if:
  - each package has its own `AGENTS.override.md`
  - `make verify` can target a package (`make verify PACKAGE=...`).

---

## 4) Concrete workflows (A–D)

### Workflow A — Molty spawns Codex agents for infrastructure/tooling builds

**Use case examples:** WebClaw deployment/customization, OpenClaw gateway enhancements, CI hardening.

**Step-by-step**
1. Molty creates GitHub issues:
   - “Add `make verify` + CI for repo”
   - “Dockerize service X for Railway”
   - “Implement config loader + env validation”
2. Add `codex-ready` and attach:
   - exact commands
   - target files
   - acceptance criteria
3. Trigger Codex cloud task.
4. Codex opens PR.
5. Molty reviews focusing on:
   - security (no secrets)
   - deploy correctness
   - idempotent scripts
6. Merge → OpenClaw cron/skills updated.
7. OpenClaw posts release note in Discord `#command-center` (owned by Molty) + updates Notion.

**Guardrails**
- Infra PRs must pass:
  - lint + tests
  - container build check
  - a “dry-run deploy” job when applicable.

---

### Workflow B — Raphael uses Codex for Brinc-specific development

**Use case examples:** HubSpot CRM integration, lead management workflows, sales automation.

**Step-by-step**
1. Raphael creates a Brinc issue with:
   - object model mapping (Contacts/Companies/Deals)
   - required webhooks/events
   - acceptance criteria (e.g., “create/update contact on inbound lead; de-dup by email; log to audit table”)
2. Raphael marks `codex-ready` only when:
   - API endpoints are defined
   - secrets are NOT required for the PR (use stubs)
3. Codex produces PR with:
   - adapters
   - request/response schemas
   - unit tests using mock server
   - `.env.example` additions
4. Raphael reviews:
   - data correctness
   - idempotency + retries
   - PII handling
5. Merge to staging → manual credential wiring by Raphael (or Molty) using GitHub Actions/Railway secrets.

**Brinc-specific guardrails**
- No direct calls to HubSpot in unit tests; use recorded fixtures/mocks.
- All CRM writes must be:
  - idempotent
  - rate-limit aware
  - logged (audit trail).

---

### Workflow C — Large multi-phase project (Smart Scheduling Engine)

**Project reality:** spec done, ~61h build; ideal candidate for parallel Codex execution.

#### Decomposition strategy (what to parallelize)
Create milestones:
- **Phase 1: Core domain model + storage**
- **Phase 2: Provider integrations (Google/Outlook/etc.)**
- **Phase 3: Scheduling rules engine**
- **Phase 4: API + UI surfaces**
- **Phase 5: Observability + hardening**

Create “PR-sized” issues per phase:
- Domain entities + migrations
- Availability computation module
- Conflict detection
- Rule evaluation DSL
- Provider adapter skeletons
- Test harness + fixtures
- API endpoints + OpenAPI spec

#### Parallel execution pattern
- Run **3–6 Codex tasks in parallel**, each owning a module.
- Molty acts as integration manager:
  - ensures shared types/interfaces are agreed upfront
  - merges foundational PRs first
  - rebases/updates downstream tasks.

#### Integration loop (repeat per week)
1. Monday: Molty posts “weekly plan” in Discord + Notion.
2. Create/refresh `codex-ready` issues.
3. Codex opens PRs.
4. Human review queue daily (30–60 min blocks).
5. End of week: integration PR + staging deploy + demo.

#### Definition of done (Phase-level)
- CI green
- module docs updated (`docs/scheduling/`)
- sample scenario tests added (golden test cases)
- telemetry hooks present (log events for decisions)

---

### Workflow D — Bug fix / maintenance

**Goal:** minimize cycle time while keeping safety.

**Issue → Codex → PR → review → merge**
1. Create GitHub issue with:
   - reproduction steps
   - expected vs actual
   - logs/stack traces
2. Label `bug` + `codex-ready` if reproducible locally.
3. Codex task:
   - add failing test first
   - implement fix
   - ensure regression test passes
4. PR review:
   - ensure minimal diff
   - ensure test coverage
5. Merge + patch release.

**When NOT to use Codex for bugs**
- production-only issues requiring sensitive logs
- bugs needing access to customer data
- outages where time-to-mitigate < review time

---

## 5) Security & governance

### 5.1 Access control

#### Who can trigger Codex tasks (recommended)
- **Guillermo**: can approve strategy + priorities; should not be required to manage daily GitHub mechanics.
- **Molty**: primary “Codex dispatcher” across repos.
- **Raphael**: dispatcher for Brinc repos only.
- Future leads (Leonardo/Donatello/Michelangelo): dispatch within their domain repos.

#### GitHub permissions model
- Use least privilege:
  - Codex needs repo read/write to create branches + PRs.
  - Humans keep admin.
- Prefer organization-level policy:
  - Codex enabled only on selected repos during pilot.

### 5.2 Secret management (Codex sandboxes)

Rules:
- **No secrets in prompts**.
- Keep secrets in:
  - GitHub Actions secrets
  - Railway environment variables
  - `.env` never committed
- Provide `.env.example` + documented required vars.
- For integration PRs, Codex uses:
  - mocks
  - fixtures
  - local stub servers.

Internet access:
- Codex cloud tasks may support toggling internet access.
- Default stance for TMNT: **internet OFF** unless the task explicitly needs it (e.g., updating dependencies or consulting public docs).

### 5.3 Review requirements before merge

Branch protection (recommended baseline for all repos using Codex):
- Require PRs (no direct pushes to `main`).
- Require:
  - CI checks
  - ≥1 human approval (Molty or domain lead)
- Require “conversation resolved.”

High-risk labels require stricter review:
- `risk:high` requires:
  - 2 approvals
  - staging deploy + smoke test checklist

### 5.4 Audit trail

We already get a strong audit trail from GitHub:
- issue discussion
- PR diff
- CI logs

Add explicit conventions:
- PRs created by Codex must include:
  - “How to test” commands
  - evidence of test runs (paste key outputs)
  - list of files changed

If we later move to Business/Enterprise with Compliance API, we can also centralize usage logs; until then, GitHub artifacts are sufficient.

---

## 6) Implementation roadmap

### 6.0 Rollout order by project (recommended)

We’ll get faster adoption if we start where tasks are most PR-shaped and least secret-dependent.

**Tier 1 (start here; clean PR-shaped work)**
- **WebClaw deployment + customization**: Docker/Railway, UI tweaks, auth/config, CI hardening.
- **Morning Briefing system**: packaging, deployment scripts, config validation, tests around the briefing generator.

**Tier 2 (high leverage; some integration complexity, still PR-shaped with mocks)**
- **Unbrowse DIY — API Skill Auto-Capture (Phases 2–5)**
  - Structure each phase as a GitHub milestone.
  - Each milestone should have 5–15 PR-sized issues (schema changes, pipeline steps, backfills, error handling, test coverage).
- **Whoop Health Integration (4-phase build)**
  - Keep Codex focused on: client SDK wrapper, data models, sync jobs, unit tests, docs.
  - Keep humans focused on: credentialing, privacy decisions, production rollout.

**Tier 3 (best once the team has muscle memory)**
- **Smart Scheduling Engine (~61h build)**
  - Run as a “parallel PR program” (Workflow C) with Molty as integration manager.

**Brinc track (parallel, Raphael-owned)**
- **HubSpot CRM integration** → best first Brinc Codex target
- **Lead management + sales automation** → next, once mapping + rules are stable

### Phase 1 — Pilot (1 project, 1 agent)

**Duration:** ~1–2 weeks

**Pick one pilot project** (recommended order):
1. **WebClaw deployment + customization** (clear infra scope, PR-shaped)
2. **Morning Briefing deployment** (if repo is already clean + tests exist)

**Prerequisites (must-do first)**
- Connect Codex Cloud to GitHub and **enable it only on the pilot repo** (least privilege; expand later).
- Add root `AGENTS.md`.
- Add `make verify` (or equivalent) + CI.
- Add issue templates:
  - `codex-ready` template
  - bug template

**Success criteria**
- ≥5 Codex PRs merged
- median PR review time ≤ 30 minutes
- no secret leakage
- defect rate acceptable (≤1 revert / 5 PRs)

### Phase 2 — Team adoption (all active agents)

**Duration:** ~2–4 weeks after pilot

**Scope**
- Enable Codex on:
  - Unbrowse DIY repo (next phases)
  - Brinc HubSpot integration repo
- Train Raphael on:
  - `codex-ready` issue writing
  - review discipline + risk labels

**Success criteria**
- Parallel PR throughput increases (2–4 PRs/day possible)
- Fewer “big bang” merges; more incremental PRs
- Clear weekly cadence (plan → execute → integrate → demo)

### Phase 3 — Full integration (automation pipelines)

**Duration:** ~4–8 weeks after Phase 2

**Enhancements**
- Discord automation:
  - post when issues become `codex-ready`
  - post PR links + status changes
- Notion automation:
  - update phase progress from GitHub milestone completion
- Codex auto-review on selected repos/branches

**Success criteria**
- End-to-end traceability from Notion spec → issues → PRs → deploys
- Predictable delivery for large builds (e.g., Smart Scheduling Engine)

---

## 7) Specific recommendations for Raphael (Brinc)

### 7.1 How Raphael should structure Brinc repos for Codex

**Recommended repo layout (agent-friendly)**
- `src/`
  - `integrations/hubspot/`
  - `integrations/email/`
  - `workflows/lead-routing/`
- `tests/`
  - `hubspot/` (fixtures + mock responses)
- `docs/`
  - `hubspot-mapping.md`
  - `lead-workflows.md`
- `scripts/`
  - `setup.sh`
  - `verify.sh`

Add:
- `AGENTS.md` at root
- `src/integrations/hubspot/AGENTS.override.md` with HubSpot-specific rules (idempotency, PII, rate limits)

### 7.2 Which Brinc projects are best suited for Codex

Best suited (high leverage, PR-shaped):
- **HubSpot CRM integration**: adapters, schema mapping, webhook handlers, sync jobs, tests.
- **Lead management automation**: deterministic workflows, rule-based routing, audit logging.
- **Sales automation scripts**: enrichment pipelines (with mocked APIs), reporting dashboards.

Less suited (keep human-led / OpenClaw):
- Pipeline design decisions (stages, SLAs, ownership)
- Anything requiring live HubSpot credentials or customer data
- Sensitive operations like dedup/merge in production CRM

### 7.3 Workflow for Raphael to request Codex builds via Discord

Because Discord is our coordination hub, make it simple:

**Message format (Raphael → Molty in Discord)**
- Repo: <link>
- Issue: <link>
- Priority: P1/P2/P3
- Risk: low/med/high
- Notes: (any constraints)

Molty replies with:
- “Codex dispatched” + ETA window
- PR link when opened
- “Needs review” checklist

> If/when Raphael has direct Codex dispatch access on Brinc repos, this becomes self-serve; Discord remains the audit log for status.

### 7.4 Review/approval process for Brinc code changes

**Minimum**
- Raphael approval required for merges to `main`.

**If risk:high**
- Add a second reviewer (Molty or another lead)
- Require staging deploy + checklist:
  - create/update contact
  - create deal
  - verify dedup logic
  - verify audit logs

---

## Appendix A — GitHub Issue template: `codex-ready`

Copy/paste into GitHub issues.

```markdown
## Summary
(What to build/fix.)

## Acceptance Criteria
- [ ] …
- [ ] …

## Constraints
- Only touch: …
- Do not touch: …

## How to test
- Setup: …
- Verify: …

## Notes
- Links: Notion spec section …
- Risks: …
```

## Appendix B — Minimum repo checklist (before enabling Codex)

- [ ] Root `AGENTS.md`
- [ ] `make verify` (or `./scripts/verify.sh`)
- [ ] CI workflow runs verify on PR
- [ ] `.env.example` documented
- [ ] Branch protection enabled
- [ ] Issue templates created

---

### References (OpenAI docs)
- Codex pricing: https://developers.openai.com/codex/pricing/
- AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- Codex cloud overview: https://developers.openai.com/codex/cloud
- API pricing: https://platform.openai.com/docs/pricing
