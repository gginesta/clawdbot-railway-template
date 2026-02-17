# Revert Snapshot — 2026-02-17 20:57 HKT

*Take this snapshot before switching from QMD to Option A1.*
*If anything goes wrong, restore this config and we're back to where we are now.*

---

## Current Config (QMD-based)

### memory section
```json
{
  "memory": {
    "backend": "qmd",
    "citations": "auto",
    "qmd": {
      "command": "/usr/local/bin/qmd",
      "includeDefaultMemory": true,
      "paths": [
        {
          "path": "/data/shared/memory-vault",
          "name": "shared-vault",
          "pattern": "**/*.md"
        }
      ],
      "sessions": {
        "enabled": true,
        "retentionDays": 30
      },
      "update": {
        "interval": "5m",
        "debounceMs": 15000,
        "onBoot": true
      },
      "limits": {
        "maxResults": 8,
        "timeoutMs": 30000
      }
    }
  }
}
```

### memorySearch section
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "extraPaths": ["/data/shared/memory-vault"],
        "provider": "openai",
        "remote": {
          "apiKey": "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",
          "model": "text-embedding-3-small"
        },
        "model": "text-embedding-3-small"
      }
    }
  }
}
```

## Current File State

### Molty QMD Index
- Path: `/data/.openclaw/agents/main/qmd/xdg-cache/qmd/index.sqlite` (42MB)
- Collections: memory-root (1), memory-alt (0), memory-dir (48), sessions (197), shared-vault (297)
- Total: 543 files, 7406 vectors

### Builtin OpenAI Index
- Path: `/data/.openclaw/memory/main.sqlite` (21MB)
- Files: 50, Chunks: 260, Embeddings: 542
- Source: workspace `memory/` only

### Shared Vault
- Path: `/data/shared/memory-vault/`
- Files: 297 .md files
- Key new files:
  - `decisions/2026-02-17-qmd-local-standardization.md`
  - `decisions/2026-02-17-test-central-feed.md`
  - `lessons/2026-02-17-dockerfile-runtime-persistence.md`
  - `CONTRIBUTION_PROTOCOL.md`
  - `SHARED_INDEX.md`

### Symlink
- `memory/shared-vault` → `/data/shared/memory-vault` (created during debugging)

### Installed Packages
- cmake 3.25.1-1 (installed for debugging, not needed)
- QMD binary at `/usr/local/bin/qmd`

## How to Revert

If Option A1 fails and we need to go back to this QMD state:

```bash
# 1. Restore memory config
openclaw config set memory.backend qmd
# (or use gateway config.patch with the JSON above)

# 2. Restore symlink if removed
ln -sf /data/shared/memory-vault /data/workspace/memory/shared-vault

# 3. Restart gateway
openclaw gateway restart
```

The QMD binary, index, and collections are all still on disk — they don't get deleted when we change config. QMD will pick up where it left off.
