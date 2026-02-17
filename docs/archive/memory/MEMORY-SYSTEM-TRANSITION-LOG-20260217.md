# Memory System Transition Log — 2026-02-17

## Current State

### Overall Goal
Switch from QMD hybrid search to OpenAI builtin search with Molty as the central memory architect.

### Completed Steps

#### Preparation
- Created shared vault structure in `/data/shared/memory-vault/`
- Wrote `CONTRIBUTION_PROTOCOL.md`
- Seed content added (2 decisions, 1 lesson)
- Syncthing configured to sync vault

#### Configuration
- Removed QMD backend config
- Set OpenAI as primary search provider
- Disabled QMD binary by renaming

#### Indexing
- Moved vault to `/data/workspace/memory/vault/`
- Builtin indexer started processing vault files
  - Current progress: 2/297 files indexed
  - High-confidence searches working
  - Gradual background indexing ongoing

### Pending Actions
- Confirmation from Raphael and Leonardo about their config update
- Complete vault file indexing
- Verify contribution flow
- Final documentation update

## Checkpoint Details

### Step 1: Vault Directory
- Location: `/data/workspace/memory/vault/`
- Total files: 297
- Indexed files: 2
- Syncthing sync: Configured to `/data/shared/memory-vault/`

### Step 2: Configuration
- QMD backend: Removed
- Search provider: OpenAI text-embedding-3-small
- Timeout: No artificial delay
- QMD binary: Renamed to `qmd.disabled`

### Step 3: Indexing Status
- Builtin SQLite index: `/data/.openclaw/memory/main.sqlite`
- Total files in index: 52
- Vault files indexed: 2
- High-confidence searches working
- Gradual background indexing in progress

## Revert Strategies

### Complete Revert
1. Restore `/data/workspace/backups/openclaw-pre-a1-20260217.json`
2. Restore QMD binary: `mv /usr/local/bin/qmd.disabled /usr/local/bin/qmd`
3. Restart gateway

### Partial Revert
- Restore specific config sections
- Keep new vault structure
- Potentially switch back to QMD with modified timeout

## Next Checkpoint Criteria
- Raphael and Leonardo confirm OpenAI search works
- 50+ vault files indexed
- Contribution flow test passes
- No unexpected data loss or search failures

## Risks
- Incomplete vault indexing
- Potential search performance issues
- Sync conflicts during transition

## Decision Log
- 2026-02-17 15:16 HKT: Initial QMD hybrid search attempt
- 2026-02-17 20:53 HKT: Switch to OpenAI builtin with Molty as architect