## 🖥️ System Architecture

### Hosting
- **Platform:** Railway (Docker containers)
- **Template Repo:** https://github.com/gginesta/clawdbot-railway-template ⚠️ OUR FORK
- **Original Template:** vignesh07/clawdbot-railway-template
- **Volume:** `/data` (persistent storage per instance)

### Instances
| Agent | URL | Webchat Token | Status |
|-------|-----|---------------|--------|
| **Molty** | ggvmolt.up.railway.app | (main gateway token) | ✅ Active |
| **Raphael** | ggv-raphael.up.railway.app | `5i3cumY3CVtCmuLlo2JHlDu7` | ✅ **DEPLOYED** (2026-02-04 04:33 UTC) |
| **Leonardo** | leonardo-production.up.railway.app | `27190324b3905f13c2f0fb3310d35afe6a09d9dcefe475b1dfacb759f59bd99f` | ✅ **DEPLOYED** (2026-02-11 10:45 HKT) |

### Discord Bots (TMNT Squad Server)
| Bot | Application ID | Guild | Status |
|-----|----------------|-------|--------|
| Molty-Bot | 1468162520958107783 | TMNT Squad (1468161542473121932) | ✅ Active |
| Raphael-Bot | 1468164929285783644 | TMNT Squad (1468161542473121932) | ✅ Active |

**Discord Channels:**
- `#command-center` (1468164160398557216) — Strategy & coordination
- `#brinc-general` (1468164121420628081) — Brinc project general
- `#brinc-private` (1468164139674238976) — Brinc private comms
- `#squad-updates` (1468164181155909743) — Team announcements

**Key Config:** `allowBots: true` required for agent-to-agent visibility

### Agent-to-Agent Communication (WORKING)
```bash
curl -X POST https://{agent}.up.railway.app/hooks/agent \
  -H "Authorization: Bearer HSYgqkBANp8ChScOEs2bo09fQ2hnFw0lqW5tZjOPmvkrCffmcuce6aVyF7p1vfTU" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your message here",
    "sessionKey": "agent:main:main",
    "wakeMode": "now"
  }'
```
**Critical:** Must include `"sessionKey": "agent:main:main"` to route to main session.

### Key Paths
| Path | Purpose |
|------|---------|
| `/data/workspace` | My workspace (git repo) |
| `/data/.openclaw` | OpenClaw state + config |
| `/data/.openclaw/openclaw.json` | Main config file |
| `/data/.openclaw/credentials/` | Telegram allowlists, pairing |
| `/data/.openclaw/browser/openclaw/` | Chromium profile |
| `/root/.cache/qmd/index.sqlite` | QMD memory index |
| `/root/.bun/bin/qmd` | QMD binary |
| `~/.config/git/credentials` | GitHub token |
| `~/.config/last30days/.env` | API keys for last30days skill |

### Memory Backend (QMD)

**Status:** ✅ Live (configured 2026-02-04)

| Setting | Value |
|---------|-------|
| Backend | `qmd` (local-first, by Tobias Lütke) |
| Binary | `/root/.bun/bin/qmd` |
| Index | `/root/.cache/qmd/index.sqlite` |
| Update interval | 5 minutes |
| Session retention | 30 days |
| Max results | 8 |
| Timeout | 5000ms |

**Collections:**
- `memory-root` → MEMORY.md
- `memory-dir` → memory/*.md
- `sessions` → Session transcripts (markdown exports)

**Why QMD over alternatives:**
- ✅ Local-first (no third-party cloud)
- ✅ Official OpenClaw support (v2026.2.2+)
- ✅ Hybrid search (BM25 + vectors + reranking)
- ✅ Author: Tobias Lütke (Shopify CEO) — credible
- ⚠️ Slow on CPU (no GPU in Railway container)

### Browser
- **Binary:** `/usr/bin/brave-browser` (installed via Dockerfile, 2026-02-04)
- **Mode:** Headless, no-sandbox, attachOnly (required for Railway containers)
- **Default profile:** `openclaw`
- **User data:** `/data/.openclaw/browser/openclaw/user-data`
- **Note:** Chromium has timeout issues with OpenClaw browser control (#3941). Brave works better.
- **Workaround:** Must manually start Brave before using browser tool:
  ```bash
  nohup brave-browser --headless=new --no-sandbox --disable-gpu \
    --remote-debugging-port=18800 --remote-debugging-address=127.0.0.1 \
    --disable-dev-shm-usage > /dev/null 2>&1 &
  ```

---
