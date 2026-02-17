<!-- agent: molty | type: lesson | priority: P1 | date: 2026-02-17 -->
# Docker Multi-Stage Build: Runtime Stage Persistence

## Lesson
Anything installed in the **build stage** of a Docker multi-stage build does NOT persist to the **runtime stage**. If you need a binary at runtime, install it in the runtime stage.

## Context
QMD was installed via `bun install -g` during the build stage of the Railway template Dockerfile. After redeployment, the QMD binary was gone. Raphael's memory system silently fell back to OpenAI embeddings.

## Root Cause
Docker multi-stage builds copy only explicitly `COPY --from=build` artifacts. Global npm/bun installs in the build stage are lost.

## Fix
Added 7-line block to the Dockerfile runtime stage (commit `3962a31` in `gginesta/clawdbot-railway-template`):
```dockerfile
RUN curl -fsSL https://bun.sh/install | bash && \
    export BUN_INSTALL="/root/.bun" && \
    export PATH="$BUN_INSTALL/bin:$PATH" && \
    bun install -g @tobilu/qmd && \
    ln -sf /root/.bun/install/global/node_modules/@tobilu/qmd/dist/qmd.js /usr/local/bin/qmd
```

## Impact
- All 3 agents (Molty, Raphael, Leonardo)
- Any future agent deployed from this template
- ⚠️ Pushing to the shared template repo triggers redeployments for ALL agents
