# Syncthing Setup for Agent Containers

This guide documents how to add Syncthing to OpenClaw agent containers running on Railway.

## Why Syncthing?

- **File sync between agents** — Share documents, KB files, configs
- **Sync with Guillermo's PC** — Direct file access to his Obsidian vault
- **No cloud intermediary** — P2P sync, privacy-preserving

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Guillermo-PC   │◄───►│  Molty-Railway  │◄───►│ Raphael-Railway │
│  (Windows/Mac)  │     │   (Container)   │     │   (Container)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                      ▲                       ▲
         └──────────────────────┴───────────────────────┘
                    Syncthing P2P mesh
```

## Device IDs

| Device | ID | Status |
|--------|-----|--------|
| Guillermo-PC | `NSIAS7W-YAOTA6B-7A5I43O-6JCQHM7-ET4SPCF-6TB73UA-APHNHS5-2QLTVQP` | ✅ Active |
| Molty-Railway | `3SM5RVG-SI2I5NF-EVETYF4-NIHFBDO-4244FJH-GSAAYNA-RUXA4UA-ZIEBBQU` | ✅ Active |
| Raphael-Railway | `SA5L4UC-JDKR64B-ATFEIZT-FDZ5IU5-ZNXCG2R-AQUQAJU-DZYLPSB-OPCETAN` | ⏳ Needs setup |

## Shared Folders

| Folder ID | Path | Type | Shared With |
|-----------|------|------|-------------|
| `brinc-kb` | `/data/shared/brinc` | sendreceive | Molty ↔ Raphael |
| `mv-daily` | `/data/shared/memory-vault/daily` | sendreceive | All |
| `mv-projects` | `/data/shared/memory-vault/knowledge/projects` | sendreceive | All |
| `mv-people` | `/data/shared/memory-vault/knowledge/people` | sendonly (Molty) | All |
| `mv-resources` | `/data/shared/memory-vault/knowledge/resources` | sendonly (Molty) | All |
| `mv-squad` | `/data/shared/memory-vault/knowledge/squad` | sendonly (Molty) | All |

## Dockerfile Changes

Add to your Dockerfile:

```dockerfile
# Install Syncthing
RUN apt-get update && apt-get install -y syncthing && rm -rf /var/lib/apt/lists/*

# Create shared directories
RUN mkdir -p /data/shared/brinc \
    /data/shared/memory-vault/daily \
    /data/shared/memory-vault/knowledge/projects \
    /data/shared/memory-vault/knowledge/people \
    /data/shared/memory-vault/knowledge/resources \
    /data/shared/memory-vault/knowledge/squad
```

## Startup Script Changes

Syncthing needs to start alongside OpenClaw. Add to your entrypoint:

```bash
# Start Syncthing in background
/usr/bin/syncthing serve --home=/data/.syncthing --gui-address=0.0.0.0:8384 --no-browser &
```

## Initial Configuration

After first boot, Syncthing generates keys. You'll need to:

1. **Get your device ID:**
   ```bash
   curl -s http://localhost:8384/rest/system/status | grep myID
   ```

2. **Add remote devices:**
   ```bash
   # Add Molty-Railway
   curl -X POST -H "X-API-Key: YOUR_API_KEY" \
     http://localhost:8384/rest/config/devices \
     -d '{"deviceID": "3SM5RVG-SI2I5NF-EVETYF4-NIHFBDO-4244FJH-GSAAYNA-RUXA4UA-ZIEBBQU", "name": "Molty-Railway"}'
   
   # Add Guillermo-PC
   curl -X POST -H "X-API-Key: YOUR_API_KEY" \
     http://localhost:8384/rest/config/devices \
     -d '{"deviceID": "NSIAS7W-YAOTA6B-7A5I43O-6JCQHM7-ET4SPCF-6TB73UA-APHNHS5-2QLTVQP", "name": "Guillermo-PC"}'
   ```

3. **Add shared folders** (same folder IDs for mesh to work)

## API Key

Use a consistent API key across agents for scripting:
- Recommended: `molty-syncthing-key` (or agent-specific like `raphael-syncthing-key`)

## Verification

After setup, verify connectivity:
```bash
# Check connections
curl -s -H "X-API-Key: YOUR_API_KEY" http://localhost:8384/rest/system/connections

# Check folder status
curl -s -H "X-API-Key: YOUR_API_KEY" "http://localhost:8384/rest/db/status?folder=brinc-kb"
```

## Troubleshooting

### "Connection refused" to other devices
- Check firewall allows port 22000 (data) and 8384 (GUI)
- Railway containers should allow outbound; relays help with NAT

### Folders not syncing
- Verify folder ID matches exactly on both ends
- Check folder path exists and is writable
- Trigger rescan: `curl -X POST "http://localhost:8384/rest/db/scan?folder=FOLDER_ID"`

### High CPU usage
- Normal during initial sync/indexing
- Set `fsWatcherEnabled: false` if filesystem watching is expensive

---

*Created: 2026-02-04 | Molty 🦎*
