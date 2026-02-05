# API Skill Auto-Capture — Technical Specification

**Codename:** Unbrowse DIY  
**Version:** 1.0  
**Date:** 2026-02-05  
**Author:** Molty 🦎 (Systems Architect)  
**Status:** Draft — Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [CDP Network Capture](#3-cdp-network-capture)
4. [API Endpoint Extraction & Classification](#4-api-endpoint-extraction--classification)
5. [Skill Auto-Generation](#5-skill-auto-generation)
6. [Fleet Distribution via Syncthing](#6-fleet-distribution-via-syncthing)
7. [Smart Fallback & Self-Healing](#7-smart-fallback--self-healing)
8. [Sub-Agent Integration](#8-sub-agent-integration)
9. [Security Considerations](#9-security-considerations)
10. [Edge Cases](#10-edge-cases)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Example Walkthrough](#12-example-walkthrough-hubspot)

---

## 1. Executive Summary

### Problem

Every time a TMNT agent needs data from a website, it fires up a headless Brave browser, waits 10-45 seconds for page load, scrapes DOM, and extracts text. This is slow, fragile, bandwidth-heavy, and unavailable to sub-agents (who lack browser access).

### Solution

**Intercept, don't scrape.** When any agent visits a site via browser, we silently capture the underlying API calls the site makes (via Chrome DevTools Protocol). We then auto-generate a reusable OpenClaw skill (bash/curl scripts) that calls those APIs directly. The skill is shared across the fleet via Syncthing.

### Value Proposition

| Metric | Before (Browser) | After (API Skill) |
|--------|------------------|--------------------|
| Latency | 10-45s | 100-500ms |
| Bandwidth | 2-10 MB (full page) | 5-100 KB (JSON) |
| Sub-agent access | ❌ Blocked | ✅ Via exec + curl |
| Reliability | ~70% (DOM changes) | ~95% (API contracts) |
| Fleet learning | Per-agent | Fleet-wide (Syncthing) |
| Token cost | High (parse HTML) | Low (structured JSON) |

### Key Principles

1. **Zero third-party dependencies** — no plugins, no native binaries, no external services
2. **Files + curl + CDP** — everything is bash scripts, JSON files, and curl commands
3. **Fleet-wide sharing** — Syncthing distributes skills; one agent learns, all benefit
4. **Self-healing** — if an API skill fails, fall back to browser, re-capture, update
5. **Compounding returns** — more agents × more sites × more time = exponentially faster fleet

---

## 2. System Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SINGLE AGENT (e.g., Molty)                       │
│                                                                         │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │   OpenClaw    │    │  CDP Interceptor  │    │   Skill Generator    │  │
│  │   Gateway     │───▶│  (cdp-capture.sh) │───▶│  (skill-gen.py)     │  │
│  │              │    │                   │    │                      │  │
│  │  browser_use │    │  • Network.enable │    │  • Parse captures    │  │
│  │  web_fetch   │    │  • requestWill... │    │  • Cluster endpoints │  │
│  │  exec        │    │  • responseRecvd  │    │  • Generate SKILL.md │  │
│  └──────┬───────┘    │  • getResponseBdy │    │  • Generate .sh      │  │
│         │            └────────┬─────────┘    │  • Generate .json    │  │
│         │                     │               └──────────┬───────────┘  │
│         │                     ▼                          │              │
│         │            ┌──────────────────┐                │              │
│         │            │  Raw Captures    │                │              │
│         │            │  /data/workspace/│                ▼              │
│         │            │  .api-captures/  │    ┌──────────────────────┐  │
│         │            │  {domain}/{ts}/  │    │  Local Skills        │  │
│         │            │  capture.jsonl   │    │  /data/workspace/    │  │
│         │            └──────────────────┘    │  skills/api-{domain}/│  │
│         │                                    │  ├── SKILL.md        │  │
│  ┌──────▼───────┐                            │  ├── api.sh          │  │
│  │  Sub-Agents  │◀───exec api.sh─────────────│  ├── endpoints.json  │  │
│  │  (no browser)│                            │  └── .auth/          │  │
│  └──────────────┘                            └──────────┬───────────┘  │
│                                                         │              │
└─────────────────────────────────────────────────────────┼──────────────┘
                                                          │ Syncthing
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      /data/shared/api-skills/                           │
│                      (Syncs across all agents)                          │
│                                                                         │
│  ├── hubspot.com/                                                       │
│  │   ├── SKILL.md              # OpenClaw skill definition              │
│  │   ├── api.sh                # Main entry point script                │
│  │   ├── endpoints.json        # Endpoint catalog                       │
│  │   ├── .meta.json            # Versioning, origin, confidence         │
│  │   └── scripts/              # Per-endpoint scripts                   │
│  │       ├── deals-list.sh                                              │
│  │       ├── deals-get.sh                                               │
│  │       ├── contacts-list.sh                                           │
│  │       └── contacts-search.sh                                         │
│  ├── notion.so/                                                         │
│  ├── twitter.com/                                                       │
│  └── _registry.json            # Global index of all captured skills    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
 ┌─────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │  Agent   │    │  Browser   │    │  CDP      │    │  Skill    │    │ Syncthing│
 │  Request │───▶│  Session   │───▶│  Capture  │───▶│  Gen      │───▶│  Sync    │
 └─────────┘    └───────────┘    └──────────┘    └──────────┘    └──────────┘
      │                                                                  │
      │  Check skill exists?                                             │
      │  ┌──────────┐                                                    │
      └─▶│ Skill    │  YES → curl directly (200ms)                      │
         │ Router   │  NO  → browser + capture + generate               │
         │          │  FAIL → fallback browser → re-capture             │
         └──────────┘                                                    │
              ▲                                                          │
              └──────────────────────────────────────────────────────────┘
                        Other agents receive skill via sync
```

### 2.3 Filesystem Layout

```
/data/workspace/
├── scripts/
│   ├── api-capture/                    # Core system scripts
│   │   ├── cdp-capture.sh             # CDP network interceptor
│   │   ├── cdp-capture.py             # Python CDP capture (primary)
│   │   ├── skill-gen.py               # Skill generator from captures
│   │   ├── skill-router.sh            # Decision: skill vs browser
│   │   ├── api-classifier.py          # Endpoint extraction & scoring
│   │   ├── auth-extractor.py          # Auth token/cookie detection
│   │   ├── noise-filter.py            # Filter analytics/tracking
│   │   └── self-heal.sh              # Health check & re-capture
│   └── ...
├── .api-captures/                      # Raw capture data (local only)
│   ├── hubspot.com/
│   │   ├── 2026-02-05T14:30:00Z/
│   │   │   ├── capture.jsonl          # Raw network events
│   │   │   ├── cookies.json           # Session cookies
│   │   │   └── meta.json             # Capture metadata
│   │   └── 2026-02-04T09:15:00Z/     # Previous captures (history)
│   └── ...
├── skills/                             # Local OpenClaw skills (highest precedence)
│   └── api-hubspot/                   # Symlink → /data/shared/api-skills/hubspot.com/
└── ...

/data/shared/api-skills/                # Syncthing-shared directory
├── _registry.json                      # Global skill index
├── _blocklist.json                     # Sites to never auto-capture
├── hubspot.com/
│   ├── SKILL.md
│   ├── api.sh
│   ├── endpoints.json
│   ├── .meta.json
│   ├── .auth/                         # Credential references (NOT actual secrets)
│   │   └── auth-config.json           # Points to local credential store
│   └── scripts/
│       ├── deals-list.sh
│       └── ...
└── ...

/data/workspace/credentials/            # Local-only credential store (NOT synced)
├── api-auth/
│   ├── hubspot.com.env                # HUBSPOT_BEARER_TOKEN=...
│   ├── notion.so.env                  # NOTION_API_KEY=...
│   └── ...
└── ...
```

### 2.4 Integration with OpenClaw Skill System

OpenClaw discovers skills in three locations (highest to lowest precedence):
1. `<workspace>/skills/` — per-agent workspace skills
2. `~/.openclaw/skills/` — managed/local skills (shared across agents on same machine)
3. Bundled skills — shipped with OpenClaw

**Our approach:** Use `skills.load.extraDirs` in `~/.openclaw/openclaw.json` to add `/data/shared/api-skills/` as a skill source. This makes every auto-generated skill automatically available to OpenClaw without manual installation.

```json
// ~/.openclaw/openclaw.json
{
  "skills": {
    "load": {
      "extraDirs": ["/data/shared/api-skills"]
    }
  }
}
```

Each generated skill folder contains a proper `SKILL.md` with YAML frontmatter that OpenClaw can parse. The agent sees `api-hubspot` as a native skill and can invoke its scripts via `exec`.

**Naming convention:** `api-{domain-slug}` (e.g., `api-hubspot-com`, `api-notion-so`). The slug is the domain with dots replaced by hyphens.

---

## 3. CDP Network Capture

### 3.1 How CDP Interception Works

Chrome DevTools Protocol exposes the `Network` domain which allows full visibility into all network requests a page makes. OpenClaw already uses Brave headless with CDP for its browser tool. We piggyback on the same CDP connection.

**The key CDP events we subscribe to:**

| CDP Method | Purpose |
|-----------|---------|
| `Network.enable` | Start receiving network events |
| `Network.requestWillBeSent` | Capture outgoing request (URL, method, headers, body) |
| `Network.responseReceived` | Capture response metadata (status, headers, MIME type) |
| `Network.loadingFinished` | Know when response body is ready to fetch |
| `Network.getResponseBody` | Fetch the actual response body content |
| `Network.webSocketCreated` | Detect WebSocket connections |
| `Network.webSocketFrameSent` | Capture outgoing WS messages |
| `Network.webSocketFrameReceived` | Capture incoming WS messages |
| `Fetch.enable` | Intercept requests before they leave (for auth analysis) |

### 3.2 Capture Data Schema

Each captured network event is stored as a JSON line in `capture.jsonl`:

```jsonc
{
  "id": "req-001",                          // Request ID (from CDP)
  "timestamp": "2026-02-05T14:30:12.456Z",  // ISO 8601
  "url": "https://api.hubapi.com/crm/v3/objects/deals?limit=50&properties=dealname,amount",
  "method": "GET",
  "request": {
    "headers": {
      "Authorization": "Bearer pat-na1-xxx",
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    "body": null,                           // null for GET, string for POST
    "bodySize": 0
  },
  "response": {
    "status": 200,
    "statusText": "OK",
    "headers": {
      "Content-Type": "application/json; charset=utf-8",
      "X-RateLimit-Remaining": "95",
      "X-RateLimit-Limit": "100"
    },
    "body": "{\"results\":[...],\"paging\":{...}}", // Actual response (truncated at 500KB)
    "bodySize": 12847,
    "mimeType": "application/json"
  },
  "timing": {
    "started": 1707142212456,
    "ttfb": 145,                            // Time to first byte (ms)
    "total": 230                            // Total request time (ms)
  },
  "resourceType": "XHR",                   // XHR, Fetch, WebSocket, Document, etc.
  "initiator": {
    "type": "script",
    "url": "https://app.hubspot.com/bundle.js",
    "lineNumber": 4521
  },
  "frameId": "main",                       // Which frame initiated
  "isRedirect": false,
  "redirectChain": [],                      // For redirect flows
  "classification": null                    // Filled by classifier later
}
```

### 3.3 Noise Filtering

The average modern website makes 50-200+ network requests per page load. Most are noise. We filter aggressively.

**Noise Filter Rules (applied in order):**

```python
NOISE_PATTERNS = {
    # Analytics & Tracking
    "analytics": [
        r"google-analytics\.com", r"googletagmanager\.com",
        r"facebook\.com/tr", r"px\.ads\.", r"analytics\.",
        r"segment\.io", r"segment\.com", r"mixpanel\.com",
        r"amplitude\.com", r"hotjar\.com", r"fullstory\.com",
        r"heap\.io", r"intercom\.io/widget", r"sentry\.io",
        r"bugsnag\.com", r"datadog", r"newrelic",
        r"doubleclick\.net", r"adsense", r"adservice",
    ],
    # CDN & Static Assets
    "static": [
        r"\.(css|js|woff2?|ttf|eot|svg|png|jpg|jpeg|gif|ico|webp|avif)(\?|$)",
        r"cdn\.", r"static\.", r"assets\.", r"fonts\.",
        r"cloudflare\.com", r"jsdelivr\.net", r"unpkg\.com",
        r"googleapis\.com/.*fonts", r"gstatic\.com",
    ],
    # Browser/Chrome internals
    "internal": [
        r"^chrome-extension://", r"^devtools://",
        r"^data:", r"^blob:",
        r"favicon\.ico",
    ],
    # Social widgets
    "widgets": [
        r"platform\.twitter\.com/widgets",
        r"connect\.facebook\.net",
        r"apis\.google\.com/js/platform",
    ],
    # Prefetch / Beacon
    "telemetry": [
        r"beacon\.", r"/collect\?", r"/pixel\?",
        r"ping\.", r"/log\?", r"telemetry",
    ],
}

# Keep rules — what we DO want
KEEP_RULES = [
    # JSON API responses
    lambda r: "application/json" in r.get("response", {}).get("headers", {}).get("Content-Type", ""),
    # GraphQL
    lambda r: "/graphql" in r.get("url", ""),
    # API path patterns
    lambda r: re.search(r"/api/|/v[0-9]+/|/rest/|/query|/search|/rpc/", r.get("url", "")),
    # XHR/Fetch resource types
    lambda r: r.get("resourceType") in ("XHR", "Fetch"),
    # Successful responses with JSON content
    lambda r: r.get("response", {}).get("status", 0) in range(200, 300)
              and r.get("response", {}).get("bodySize", 0) > 50,
]
```

**Filtering algorithm:**
1. Reject if URL matches any `NOISE_PATTERNS`
2. Reject if `resourceType` is `Image`, `Font`, `Stylesheet`, `Media`
3. Reject if response `Content-Type` is image/*, font/*, text/css, text/html (unless it's the initial document)
4. Reject if response body is empty or < 20 bytes
5. Keep if ANY `KEEP_RULES` match
6. For everything else: keep but mark as `confidence: "low"`

### 3.4 Implementation: Python CDP Capture

**Why Python over bash:** CDP requires WebSocket communication, event-driven parsing, and JSON manipulation. Python handles this cleanly with the built-in `websockets` and `json` modules. No pip dependencies needed — we use only stdlib + the `websockets` module (or raw WebSocket via `asyncio`).

**Actually, let's reconsider.** We want zero external dependencies. Python stdlib doesn't include a WebSocket client. Options:

1. **Use Node.js** — OpenClaw already has Node.js installed (it runs on Node). Node has native WebSocket support (or `ws` which is already a dependency of OpenClaw).
2. **Use Python with a vendored websocket lib** — copy a minimal WebSocket client into our scripts.
3. **Use bash + websocat** — but that's a native binary, violating our no-binary rule.
4. **Use Python 3.11+ `websockets`** — pre-installed on most systems.

**Decision: Node.js script.** OpenClaw runs on Node v22, which has native WebSocket support via `undici`. This is the path of least resistance — zero extra installs.

```javascript
// cdp-capture.js — CDP Network Capture Agent
// Runs alongside browser session, captures API traffic
// Usage: node cdp-capture.js <cdp-ws-url> <domain> <output-dir>

const { WebSocket } = require('ws'); // Already available in OpenClaw's node_modules
const fs = require('fs');
const path = require('path');

class CDPCapture {
  constructor(cdpUrl, domain, outputDir) {
    this.cdpUrl = cdpUrl;
    this.domain = domain;
    this.outputDir = outputDir;
    this.requests = new Map();  // requestId → partial request data
    this.captured = [];          // completed request/response pairs
    this.ws = null;
    this.msgId = 1;
  }

  async connect() {
    this.ws = new WebSocket(this.cdpUrl);
    await new Promise((resolve, reject) => {
      this.ws.on('open', resolve);
      this.ws.on('error', reject);
    });

    this.ws.on('message', (data) => this.handleEvent(JSON.parse(data)));

    // Enable Network domain
    await this.send('Network.enable', {
      maxTotalBufferSize: 50 * 1024 * 1024, // 50MB buffer
      maxResourceBufferSize: 10 * 1024 * 1024, // 10MB per resource
    });

    // Enable Fetch domain for request interception (read-only)
    // We use this to see request bodies for POST/PUT before they're sent
    await this.send('Fetch.enable', {
      patterns: [{ urlPattern: '*', requestStage: 'Request' }],
    });

    console.error(`[cdp-capture] Connected to ${this.cdpUrl}, monitoring ${this.domain}`);
  }

  send(method, params = {}) {
    const id = this.msgId++;
    return new Promise((resolve) => {
      const handler = (data) => {
        const msg = JSON.parse(data);
        if (msg.id === id) {
          this.ws.off('message', handler);
          resolve(msg.result);
        }
      };
      this.ws.on('message', handler);
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  handleEvent(msg) {
    if (!msg.method) return;

    switch (msg.method) {
      case 'Network.requestWillBeSent':
        this.onRequestWillBeSent(msg.params);
        break;
      case 'Network.responseReceived':
        this.onResponseReceived(msg.params);
        break;
      case 'Network.loadingFinished':
        this.onLoadingFinished(msg.params);
        break;
      case 'Fetch.requestPaused':
        this.onFetchRequestPaused(msg.params);
        break;
      case 'Network.webSocketCreated':
        this.onWebSocketCreated(msg.params);
        break;
      case 'Network.webSocketFrameReceived':
        this.onWebSocketFrame(msg.params, 'received');
        break;
      case 'Network.webSocketFrameSent':
        this.onWebSocketFrame(msg.params, 'sent');
        break;
    }
  }

  onRequestWillBeSent(params) {
    const { requestId, request, timestamp, type, initiator, redirectResponse } = params;
    this.requests.set(requestId, {
      id: requestId,
      timestamp: new Date(timestamp * 1000).toISOString(),
      url: request.url,
      method: request.method,
      request: {
        headers: request.headers,
        body: request.postData || null,
        bodySize: request.postData ? request.postData.length : 0,
      },
      response: null,
      timing: { started: timestamp * 1000 },
      resourceType: type,
      initiator: {
        type: initiator.type,
        url: initiator.url || null,
        lineNumber: initiator.lineNumber || null,
      },
      isRedirect: !!redirectResponse,
    });
  }

  onResponseReceived(params) {
    const { requestId, response, type } = params;
    const entry = this.requests.get(requestId);
    if (!entry) return;

    entry.response = {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      mimeType: response.mimeType,
      body: null,  // Fetched on loadingFinished
      bodySize: response.encodedDataLength || 0,
    };
    entry.timing.ttfb = response.timing
      ? Math.round(response.timing.receiveHeadersEnd)
      : null;
  }

  async onLoadingFinished(params) {
    const { requestId, timestamp } = params;
    const entry = this.requests.get(requestId);
    if (!entry || !entry.response) return;

    entry.timing.total = Math.round(timestamp * 1000 - entry.timing.started);

    // Fetch response body
    try {
      const result = await this.send('Network.getResponseBody', { requestId });
      if (result) {
        const body = result.base64Encoded
          ? Buffer.from(result.body, 'base64').toString('utf-8')
          : result.body;
        // Truncate large bodies
        entry.response.body = body.length > 500000
          ? body.substring(0, 500000) + '...[TRUNCATED]'
          : body;
        entry.response.bodySize = body.length;
      }
    } catch (e) {
      // Response body might not be available (e.g., redirects)
      entry.response.body = null;
    }

    this.captured.push(entry);
    this.requests.delete(requestId);
  }

  async onFetchRequestPaused(params) {
    // Continue the request (we're only observing, not modifying)
    await this.send('Fetch.continueRequest', { requestId: params.requestId });
  }

  onWebSocketCreated(params) {
    const { requestId, url } = params;
    this.requests.set(`ws-${requestId}`, {
      id: `ws-${requestId}`,
      timestamp: new Date().toISOString(),
      url,
      method: 'WEBSOCKET',
      resourceType: 'WebSocket',
      frames: [],
    });
  }

  onWebSocketFrame(params, direction) {
    const { requestId, response } = params;
    const entry = this.requests.get(`ws-${requestId}`);
    if (!entry) return;
    entry.frames.push({
      direction,
      timestamp: new Date().toISOString(),
      data: response.payloadData.substring(0, 100000), // Limit frame size
      opcode: response.opcode,
    });
  }

  async stop() {
    // Write captured data
    const outDir = path.join(this.outputDir, this.domain,
      new Date().toISOString().replace(/[:.]/g, '-'));
    fs.mkdirSync(outDir, { recursive: true });

    // Write JSONL (one request per line)
    const captureFile = path.join(outDir, 'capture.jsonl');
    const stream = fs.createWriteStream(captureFile);
    for (const entry of this.captured) {
      stream.write(JSON.stringify(entry) + '\n');
    }
    stream.end();

    // Write metadata
    const meta = {
      domain: this.domain,
      capturedAt: new Date().toISOString(),
      totalRequests: this.captured.length,
      captureDir: outDir,
      agent: process.env.AGENT_NAME || 'unknown',
    };
    fs.writeFileSync(path.join(outDir, 'meta.json'), JSON.stringify(meta, null, 2));

    console.error(`[cdp-capture] Captured ${this.captured.length} requests to ${captureFile}`);

    if (this.ws) this.ws.close();
    return outDir;
  }
}

module.exports = { CDPCapture };
```

### 3.5 Hooking into OpenClaw's Browser Sessions

**The challenge:** OpenClaw's browser tool manages its own CDP connection. We need to attach a *second* CDP client to the same browser session to observe traffic without interfering.

**Approach: Attach to the same browser via CDP endpoint.**

When OpenClaw launches Brave headless, it connects to a CDP WebSocket URL (e.g., `ws://127.0.0.1:9222/devtools/page/XXXXX`). The browser's CDP endpoint is typically available at `http://127.0.0.1:9222/json/version`.

**Integration strategy:**

1. **Before browser_use:** The skill-router checks if there's an existing skill for the target domain. If yes, use the API skill instead.

2. **During browser_use:** A wrapper script starts the CDP capture alongside the browser session:
   ```bash
   # skill-router.sh — wraps browser usage
   #!/usr/bin/env bash
   DOMAIN=$(echo "$1" | awk -F/ '{print $3}')
   CAPTURE_DIR="/data/workspace/.api-captures"
   
   # Get CDP endpoint from the running browser
   CDP_URL=$(curl -s http://127.0.0.1:9222/json/version | jq -r '.webSocketDebuggerUrl')
   
   # Start capture in background
   node /data/workspace/scripts/api-capture/cdp-capture.js \
     "$CDP_URL" "$DOMAIN" "$CAPTURE_DIR" &
   CAPTURE_PID=$!
   
   # Let the browser session proceed normally...
   # (OpenClaw's browser tool does its thing)
   
   # After session ends, stop capture and generate skill
   kill $CAPTURE_PID 2>/dev/null
   wait $CAPTURE_PID 2>/dev/null
   
   # Trigger skill generation
   python3 /data/workspace/scripts/api-capture/skill-gen.py \
     --domain "$DOMAIN" \
     --capture-dir "$CAPTURE_DIR/$DOMAIN"
   ```

3. **After browser_use:** The skill generator processes captures and creates/updates the skill.

**Alternative (simpler) approach — Post-hoc capture analysis:**

Instead of running a parallel CDP client, we can configure the browser to dump Network logs via CDP's `Network.enable` and `Page.enable` before the agent's browser session begins. Many CDP-based tools support a "HAR export" mode.

**Recommended: Use a CDP proxy/wrapper.** The cleanest approach is a thin wrapper around the browser launch that:
1. Discovers the CDP port from the running Brave process
2. Attaches a second CDP session to the same target (Chrome supports multiple debugger clients)
3. Enables `Network` domain on the second session
4. Captures all traffic while the primary session (OpenClaw) uses the browser normally
5. On disconnect, flushes captures to disk

### 3.6 WebSocket Handling

For WebSocket-heavy sites (Slack, Discord, real-time dashboards), we capture:
- The initial WebSocket handshake URL and headers
- The first N frames (configurable, default: 100) in each direction
- Frame patterns (message types, schemas)

WebSocket skills are generated differently — instead of curl commands, they produce scripts that use `websocat` (if available) or a Node.js one-liner for WS communication.

### 3.7 Auth Token Detection

The auth extractor examines captured requests for authentication patterns:

```python
AUTH_PATTERNS = [
    # Bearer tokens
    {
        "type": "bearer",
        "detect": lambda h: "authorization" in {k.lower(): v for k, v in h.items()}
                            and "bearer" in h.get("Authorization", h.get("authorization", "")).lower(),
        "extract": lambda h: h.get("Authorization", h.get("authorization", "")).split(" ", 1)[1],
        "header": "Authorization",
        "template": "Bearer {token}",
    },
    # API keys in headers
    {
        "type": "api_key_header",
        "detect": lambda h: any(k.lower() in ("x-api-key", "api-key", "apikey", "x-auth-token")
                               for k in h.keys()),
        "extract": lambda h: next(v for k, v in h.items()
                                   if k.lower() in ("x-api-key", "api-key", "apikey", "x-auth-token")),
        "header_names": ["X-Api-Key", "Api-Key", "apikey", "X-Auth-Token"],
    },
    # API keys in URL params
    {
        "type": "api_key_param",
        "detect": lambda url: any(p in url.lower()
                                   for p in ("api_key=", "apikey=", "key=", "token=", "access_token=")),
        "extract": lambda url: parse_qs(urlparse(url).query),
    },
    # Cookie-based auth
    {
        "type": "cookie",
        "detect": lambda h: "cookie" in {k.lower() for k in h.keys()},
        "extract": lambda h: h.get("Cookie", h.get("cookie", "")),
        "sensitive_cookies": ["session", "sid", "auth", "token", "jwt", "csrf", "_csrf"],
    },
    # OAuth (detect from URL patterns)
    {
        "type": "oauth",
        "detect": lambda url: any(p in url for p in ("/oauth", "/authorize", "/token",
                                                       "grant_type=", "client_id=")),
    },
    # CSRF tokens
    {
        "type": "csrf",
        "detect": lambda h: any(k.lower() in ("x-csrf-token", "x-xsrf-token", "csrf-token")
                               for k in h.keys()),
        "extract": lambda h: next(v for k, v in h.items()
                                   if k.lower() in ("x-csrf-token", "x-xsrf-token", "csrf-token")),
    },
]
```

The extractor identifies:
1. **Auth method** (Bearer, API key, Cookie, OAuth)
2. **Auth location** (header name, query param, cookie name)
3. **Token value** (stored separately in `/data/workspace/credentials/api-auth/`)
4. **Token characteristics** (JWT? decode to check expiry. API key? Check format.)
5. **Refresh mechanism** (if we see `/token` or `/refresh` calls, record the flow)

---

## 4. API Endpoint Extraction & Classification

### 4.1 Extraction Algorithm

After noise filtering, we have a clean set of API requests. The classifier runs this pipeline:

```
Raw Captures → Noise Filter → URL Normalization → Endpoint Clustering
    → CRUD Detection → Parameter Inference → Auth Classification
    → Confidence Scoring → Endpoint Catalog (endpoints.json)
```

### 4.2 URL Normalization

Convert specific URLs into parameterized patterns:

```python
def normalize_url(url):
    """Convert specific URLs to patterns.
    
    Examples:
        /api/v3/objects/deals/12345          → /api/v3/objects/deals/{id}
        /api/v3/objects/deals/12345/notes    → /api/v3/objects/deals/{id}/notes
        /users/john@email.com/profile        → /users/{email}/profile
        /api/v2/records?offset=50&limit=25   → /api/v2/records?offset={offset}&limit={limit}
    """
    parsed = urlparse(url)
    path_parts = parsed.path.split('/')
    normalized_parts = []
    
    for part in path_parts:
        if not part:
            normalized_parts.append(part)
            continue
        # UUID pattern
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', part, re.I):
            normalized_parts.append('{id}')
        # Numeric ID
        elif re.match(r'^\d+$', part):
            normalized_parts.append('{id}')
        # MongoDB ObjectId
        elif re.match(r'^[0-9a-f]{24}$', part, re.I):
            normalized_parts.append('{id}')
        # Email-like
        elif re.match(r'^[^@]+@[^@]+\.[^@]+$', part):
            normalized_parts.append('{email}')
        # Slug-like with numbers (e.g., deal-12345)
        elif re.match(r'^[a-z]+-\d+$', part, re.I):
            normalized_parts.append('{slug}')
        # Date patterns
        elif re.match(r'^\d{4}-\d{2}-\d{2}', part):
            normalized_parts.append('{date}')
        else:
            normalized_parts.append(part)
    
    return '/'.join(normalized_parts)
```

### 4.3 Endpoint Clustering

Group normalized URLs into resource clusters:

```python
def cluster_endpoints(captured_requests):
    """Group requests into logical API resource clusters.
    
    Returns:
        {
            "deals": {
                "base_path": "/api/v3/objects/deals",
                "endpoints": [...],
                "auth": "bearer",
                "confidence": 0.95,
            },
            "contacts": { ... }
        }
    """
    clusters = defaultdict(list)
    
    for req in captured_requests:
        normalized = normalize_url(req['url'])
        parsed = urlparse(normalized)
        
        # Extract resource name from path
        # Strategy: find the most meaningful path segment
        path_parts = [p for p in parsed.path.split('/') if p and not p.startswith('{')]
        
        # Skip version segments (v1, v2, v3, etc.)
        resource_parts = [p for p in path_parts if not re.match(r'^v\d+$', p)]
        
        # Skip common prefixes (api, rest, query, etc.)
        skip_prefixes = {'api', 'rest', 'query', 'rpc', 'graphql', 'data', 'objects'}
        resource_parts = [p for p in resource_parts if p.lower() not in skip_prefixes]
        
        if resource_parts:
            resource_name = resource_parts[0]  # Primary resource
            cluster_key = resource_name.lower()
        else:
            cluster_key = '_root'
        
        clusters[cluster_key].append({
            'raw_url': req['url'],
            'normalized_url': normalized,
            'method': req['method'],
            'request': req['request'],
            'response': req['response'],
            'timing': req['timing'],
        })
    
    return dict(clusters)
```

### 4.4 CRUD Pattern Detection

For each cluster, identify the REST/CRUD operations available:

```python
CRUD_PATTERNS = {
    "list": {
        "method": "GET",
        "path_pattern": r"^/.*/{resource}/?(\?.*)?$",  # No ID segment at end
        "response_hints": ["results", "items", "data", "records", "total", "count"],
        "description": "List {resource}",
    },
    "get": {
        "method": "GET",
        "path_pattern": r"^/.*/{resource}/\{id\}",  # Has ID segment
        "description": "Get single {resource} by ID",
    },
    "create": {
        "method": "POST",
        "path_pattern": r"^/.*/{resource}/?$",  # POST to collection
        "description": "Create new {resource}",
    },
    "update": {
        "method": ["PUT", "PATCH"],
        "path_pattern": r"^/.*/{resource}/\{id\}",
        "description": "Update {resource} by ID",
    },
    "delete": {
        "method": "DELETE",
        "path_pattern": r"^/.*/{resource}/\{id\}",
        "description": "Delete {resource} by ID",
    },
    "search": {
        "method": ["GET", "POST"],
        "path_pattern": r"^/.*/{resource}/(search|query|find)",
        "description": "Search {resource}",
    },
}

def detect_crud(cluster_name, endpoints):
    """Identify CRUD operations within a cluster."""
    operations = {}
    
    for ep in endpoints:
        normalized = ep['normalized_url']
        method = ep['method']
        
        # Check response body for list indicators
        is_list = False
        if ep['response']['body']:
            try:
                body = json.loads(ep['response']['body'])
                if isinstance(body, dict):
                    is_list = any(isinstance(body.get(k), list) for k in 
                                 ['results', 'items', 'data', 'records', 'rows', 'entries'])
                elif isinstance(body, list):
                    is_list = True
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Classify
        has_id = '{id}' in normalized
        
        if method == 'GET' and not has_id and is_list:
            operations.setdefault('list', []).append(ep)
        elif method == 'GET' and has_id:
            operations.setdefault('get', []).append(ep)
        elif method == 'GET' and ('search' in normalized or 'query' in normalized):
            operations.setdefault('search', []).append(ep)
        elif method == 'POST' and not has_id:
            operations.setdefault('create', []).append(ep)
        elif method in ('PUT', 'PATCH') and has_id:
            operations.setdefault('update', []).append(ep)
        elif method == 'DELETE' and has_id:
            operations.setdefault('delete', []).append(ep)
        elif method == 'POST' and ('search' in normalized or 'query' in normalized or 'filter' in normalized):
            operations.setdefault('search', []).append(ep)
        else:
            operations.setdefault('other', []).append(ep)
    
    return operations
```

### 4.5 Parameter Inference

For each endpoint, infer the parameter schema:

```python
def infer_parameters(endpoints_in_cluster):
    """Infer path params, query params, and body schema from observed traffic.
    
    Given multiple requests to the same endpoint pattern, we can:
    1. Identify which path segments vary (= path params)
    2. Collect all observed query parameters and their value types
    3. Analyze POST/PUT bodies to infer JSON schema
    """
    params = {
        "path": {},     # {param_name: {"type": "string", "examples": [...]}}
        "query": {},    # {param_name: {"type": "string", "required": bool, "examples": [...]}}
        "body": None,   # JSON schema (inferred)
        "headers": {},  # Required non-standard headers
    }
    
    for ep in endpoints_in_cluster:
        # Query params
        parsed = urlparse(ep['raw_url'])
        qp = parse_qs(parsed.query)
        for key, values in qp.items():
            if key not in params["query"]:
                params["query"][key] = {
                    "type": infer_type(values[0]),
                    "required": False,
                    "examples": [],
                    "seen_count": 0,
                }
            params["query"][key]["examples"].extend(values[:3])
            params["query"][key]["seen_count"] += 1
        
        # Body schema
        if ep['request']['body']:
            try:
                body = json.loads(ep['request']['body'])
                if params["body"] is None:
                    params["body"] = infer_json_schema(body)
                else:
                    params["body"] = merge_schemas(params["body"], infer_json_schema(body))
            except (json.JSONDecodeError, TypeError):
                pass
    
    # Mark query params as required if seen in ALL requests
    total = len(endpoints_in_cluster)
    for key, info in params["query"].items():
        info["required"] = info["seen_count"] >= total * 0.8  # 80% threshold
        del info["seen_count"]
        info["examples"] = list(set(info["examples"]))[:5]
    
    return params

def infer_type(value):
    """Infer JSON type from a string value."""
    if value.lower() in ('true', 'false'):
        return 'boolean'
    try:
        int(value)
        return 'integer'
    except ValueError:
        pass
    try:
        float(value)
        return 'number'
    except ValueError:
        pass
    return 'string'

def infer_json_schema(obj, max_depth=5):
    """Infer a JSON schema from an example object."""
    if max_depth <= 0:
        return {"type": "object"}
    if isinstance(obj, dict):
        return {
            "type": "object",
            "properties": {
                k: infer_json_schema(v, max_depth - 1)
                for k, v in obj.items()
            }
        }
    elif isinstance(obj, list):
        if obj:
            return {"type": "array", "items": infer_json_schema(obj[0], max_depth - 1)}
        return {"type": "array"}
    elif isinstance(obj, bool):
        return {"type": "boolean"}
    elif isinstance(obj, int):
        return {"type": "integer"}
    elif isinstance(obj, float):
        return {"type": "number"}
    elif obj is None:
        return {"type": "null"}
    else:
        return {"type": "string"}
```

### 4.6 Confidence Scoring

Each endpoint gets a confidence score (0.0 – 1.0) based on multiple signals:

| Signal | Weight | Score Logic |
|--------|--------|-------------|
| Returns JSON | 0.20 | 1.0 if Content-Type is application/json, 0.0 otherwise |
| Has API path pattern | 0.15 | 1.0 if matches `/api/`, `/v\d/`, etc. |
| Successful response | 0.15 | 1.0 if 2xx status |
| Meaningful response body | 0.15 | 0.0 if <100 bytes, 0.5 if 100-1KB, 1.0 if >1KB |
| Not a known tracker | 0.10 | 1.0 if domain is same as page domain, 0.5 if known API provider |
| Has auth headers | 0.10 | 1.0 if Bearer/API key present (indicates protected resource) |
| Seen multiple times | 0.10 | 0.5 if seen once, 1.0 if seen 2+ times |
| Low latency | 0.05 | 1.0 if <500ms TTFB (typical API), 0.5 if 500ms-2s |

**Threshold:** Endpoints with confidence ≥ 0.60 are included in generated skills. Those with 0.40–0.59 are included but marked as `"experimental": true`. Below 0.40: discarded.

### 4.7 GraphQL Special Handling

GraphQL sites use a single endpoint (e.g., `/graphql`) with query-based operations. We handle this differently:

1. **Detect GraphQL:** URL contains `/graphql` OR request body contains `"query"` field with GraphQL syntax
2. **Extract operations:** Parse the `query` field to extract operation names, types (query/mutation/subscription), and variables
3. **Cluster by operation name** instead of URL path
4. **Generate per-operation scripts** that send the specific GraphQL query with variable substitution

```python
def extract_graphql_operations(captured_requests):
    """Extract individual GraphQL operations from captured traffic."""
    operations = {}
    
    for req in captured_requests:
        if req['method'] != 'POST':
            continue
        try:
            body = json.loads(req['request']['body'])
        except (json.JSONDecodeError, TypeError):
            continue
        
        query = body.get('query', '')
        if not query or not any(kw in query for kw in ['query ', 'mutation ', 'subscription ', '{']):
            continue
        
        op_name = body.get('operationName', extract_operation_name(query))
        variables = body.get('variables', {})
        
        operations[op_name or f'unnamed_{len(operations)}'] = {
            'url': req['url'],
            'query': query,
            'variables': variables,
            'variable_schema': infer_json_schema(variables) if variables else None,
            'response_sample': req['response']['body'][:10000] if req['response']['body'] else None,
            'auth': detect_auth(req['request']['headers']),
        }
    
    return operations
```

---

## 5. Skill Auto-Generation

### 5.1 Output Structure

For each captured domain, we generate a complete OpenClaw skill:

```
/data/shared/api-skills/{domain}/
├── SKILL.md                    # OpenClaw skill definition (agent reads this)
├── api.sh                      # Main entry point (dispatcher)
├── endpoints.json              # Machine-readable endpoint catalog
├── .meta.json                  # Versioning & provenance metadata
├── .auth/
│   └── auth-config.json        # Auth method description (NO actual tokens)
└── scripts/
    ├── deals-list.sh           # GET /api/v3/objects/deals
    ├── deals-get.sh            # GET /api/v3/objects/deals/{id}
    ├── deals-create.sh         # POST /api/v3/objects/deals
    ├── contacts-list.sh        # GET /api/v3/objects/contacts
    ├── contacts-search.sh      # POST /api/v3/objects/contacts/search
    └── ...
```

### 5.2 SKILL.md Template

```markdown
---
name: api-{domain_slug}
description: Auto-captured API skill for {domain}. Direct API access to {resource_summary}.
metadata: {"openclaw":{"requires":{"bins":["curl","jq"]}}}
---

# {Domain} API Skill (Auto-Captured)

**Generated:** {timestamp}
**Captured by:** {agent_name}
**Confidence:** {avg_confidence}
**Last verified:** {last_verified}

## Quick Start

Use `{baseDir}/api.sh` to interact with {domain}'s API directly.

### Available Actions

{for each resource_cluster}
#### {Resource Name}
- **List:** `exec {baseDir}/scripts/{resource}-list.sh [--limit N] [--offset N]`
- **Get:** `exec {baseDir}/scripts/{resource}-get.sh --id {ID}`
- **Search:** `exec {baseDir}/scripts/{resource}-search.sh --query "TERM"`
- **Create:** `exec {baseDir}/scripts/{resource}-create.sh --data '{"field":"value"}'`
{end for}

### Dispatcher

For convenience, use the main dispatcher:
```bash
exec {baseDir}/api.sh {resource} {action} [--param value]
```

Examples:
```bash
exec {baseDir}/api.sh deals list --limit 10
exec {baseDir}/api.sh deals get --id 12345
exec {baseDir}/api.sh contacts search --query "john@example.com"
```

## Authentication

This API requires **{auth_type}** authentication.
Credentials are loaded from `/data/workspace/credentials/api-auth/{domain}.env`.

To set up authentication:
```bash
echo '{AUTH_VAR}=your-token-here' > /data/workspace/credentials/api-auth/{domain}.env
```

## Endpoints

| Resource | Action | Method | Path | Confidence |
|----------|--------|--------|------|------------|
{for each endpoint}
| {resource} | {action} | {method} | {path} | {confidence} |
{end for}

## Notes

- Auto-generated from browser traffic capture. May not cover all API endpoints.
- If an endpoint fails, the system will fall back to browser and re-capture.
- Run `exec {baseDir}/api.sh --health` to verify all endpoints are working.
```

### 5.3 Shell Script Template

Each endpoint gets its own script:

```bash
#!/usr/bin/env bash
# Auto-generated API script for: {method} {path}
# Domain: {domain}
# Resource: {resource}
# Action: {action}
# Confidence: {confidence}
# Generated: {timestamp}
# Captured by: {agent}
#
# Usage: {script_name}.sh [OPTIONS]
# Options:
#   --id VALUE        Resource ID (for get/update/delete)
#   --limit N         Number of results (default: {default_limit})
#   --offset N        Pagination offset (default: 0)
#   --query STRING    Search query
#   --data JSON       Request body (for create/update)
#   --raw             Output raw JSON (no jq formatting)
#   --dry-run         Show curl command without executing
#   --help            Show this help

set -euo pipefail

# === Configuration ===
BASE_URL="{base_url}"
ENDPOINT="{endpoint_path}"
METHOD="{method}"
CRED_FILE="/data/workspace/credentials/api-auth/{domain}.env"

# === Load credentials ===
if [[ -f "$CRED_FILE" ]]; then
  source "$CRED_FILE"
else
  echo "ERROR: No credentials found at $CRED_FILE" >&2
  echo "Run: echo '{AUTH_VAR}=your-token' > $CRED_FILE" >&2
  exit 1
fi

# === Parse arguments ===
ID=""
LIMIT="{default_limit}"
OFFSET="0"
QUERY=""
DATA=""
RAW=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id) ID="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --offset) OFFSET="$2"; shift 2 ;;
    --query) QUERY="$2"; shift 2 ;;
    --data) DATA="$2"; shift 2 ;;
    --raw) RAW=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help) head -20 "$0" | grep '^#' | sed 's/^# \?//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# === Build URL ===
URL="${BASE_URL}${ENDPOINT}"

# Substitute path parameters
if [[ -n "$ID" ]]; then
  URL="${URL//\{id\}/$ID}"
fi

# Add query parameters
QUERY_STRING=""
{for each query_param}
if [[ -n "${param_var}" ]]; then
  QUERY_STRING="${QUERY_STRING:+$QUERY_STRING&}{param_name}=${param_var}"
fi
{end for}
if [[ -n "$LIMIT" ]]; then
  QUERY_STRING="${QUERY_STRING:+$QUERY_STRING&}limit=$LIMIT"
fi
if [[ -n "$OFFSET" && "$OFFSET" != "0" ]]; then
  QUERY_STRING="${QUERY_STRING:+$QUERY_STRING&}offset=$OFFSET"
fi
if [[ -n "$QUERY_STRING" ]]; then
  URL="${URL}?${QUERY_STRING}"
fi

# === Build curl command ===
CURL_CMD=(curl -s -w "\n%{http_code}" -X "$METHOD")

# Auth header
{auth_header_block}

# Content type
CURL_CMD+=(-H "Accept: application/json")
if [[ "$METHOD" != "GET" && "$METHOD" != "DELETE" ]]; then
  CURL_CMD+=(-H "Content-Type: application/json")
fi

# Request body
if [[ -n "$DATA" ]]; then
  CURL_CMD+=(-d "$DATA")
fi

CURL_CMD+=("$URL")

# === Execute ===
if [[ "$DRY_RUN" == true ]]; then
  echo "${CURL_CMD[@]}"
  exit 0
fi

RESPONSE=$("${CURL_CMD[@]}" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

# === Handle response ===
if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  if [[ "$RAW" == true ]]; then
    echo "$BODY"
  else
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  fi
elif [[ "$HTTP_CODE" == "401" || "$HTTP_CODE" == "403" ]]; then
  echo "AUTH_EXPIRED" >&2
  echo "$BODY" >&2
  exit 2  # Special exit code: auth failure (triggers re-auth flow)
elif [[ "$HTTP_CODE" == "429" ]]; then
  echo "RATE_LIMITED" >&2
  # Extract retry-after if available
  echo "$BODY" >&2
  exit 3  # Special exit code: rate limited
elif [[ "$HTTP_CODE" == "404" ]]; then
  echo "ENDPOINT_GONE" >&2
  echo "$BODY" >&2
  exit 4  # Special exit code: endpoint may have changed
else
  echo "API_ERROR:$HTTP_CODE" >&2
  echo "$BODY" >&2
  exit 1
fi
```

**Auth header block templates** (inserted based on detected auth type):

```bash
# Bearer token
CURL_CMD+=(-H "Authorization: Bearer ${AUTH_TOKEN}")

# API key in header
CURL_CMD+=(-H "X-Api-Key: ${API_KEY}")

# Cookie-based
CURL_CMD+=(-H "Cookie: ${AUTH_COOKIES}")

# Multiple headers (e.g., CSRF + cookie)
CURL_CMD+=(-H "Cookie: ${AUTH_COOKIES}" -H "X-CSRF-Token: ${CSRF_TOKEN}")
```

### 5.4 Main Dispatcher (api.sh)

```bash
#!/usr/bin/env bash
# API Skill Dispatcher for {domain}
# Auto-generated: {timestamp}
#
# Usage: api.sh <resource> <action> [OPTIONS]
#        api.sh --list          List available resources/actions
#        api.sh --health        Check all endpoints

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

case "${1:-}" in
  --list)
    echo "Available endpoints for {domain}:"
    for script in "$SCRIPT_DIR"/scripts/*.sh; do
      name=$(basename "$script" .sh)
      desc=$(head -5 "$script" | grep '# Action:' | sed 's/.*: //')
      printf "  %-30s %s\n" "$name" "$desc"
    done
    exit 0
    ;;
  --health)
    echo "Health check for {domain} API skill:"
    PASS=0; FAIL=0
    for script in "$SCRIPT_DIR"/scripts/*-list.sh "$SCRIPT_DIR"/scripts/*-get.sh; do
      [[ -f "$script" ]] || continue
      name=$(basename "$script" .sh)
      if bash "$script" --limit 1 >/dev/null 2>&1; then
        echo "  ✅ $name"
        ((PASS++))
      else
        echo "  ❌ $name (exit code: $?)"
        ((FAIL++))
      fi
    done
    echo "Results: $PASS passed, $FAIL failed"
    exit $([[ $FAIL -eq 0 ]] && echo 0 || echo 1)
    ;;
  --help|"")
    head -10 "$0" | grep '^#' | sed 's/^# \?//'
    echo ""
    bash "$0" --list
    exit 0
    ;;
esac

RESOURCE="$1"
ACTION="${2:-list}"
shift 2 || shift 1

SCRIPT="$SCRIPT_DIR/scripts/${RESOURCE}-${ACTION}.sh"

if [[ ! -f "$SCRIPT" ]]; then
  echo "Error: No script for ${RESOURCE}/${ACTION}" >&2
  echo "Available:" >&2
  ls "$SCRIPT_DIR"/scripts/"${RESOURCE}"-*.sh 2>/dev/null | \
    sed "s|.*/||;s|\.sh||;s|${RESOURCE}-||" | \
    sed "s/^/  ${RESOURCE} /" >&2
  exit 1
fi

exec bash "$SCRIPT" "$@"
```

### 5.5 endpoints.json Schema

```jsonc
{
  "domain": "hubspot.com",
  "base_url": "https://api.hubapi.com",
  "generated_at": "2026-02-05T14:30:00Z",
  "captured_by": "molty",
  "version": 1,
  "auth": {
    "type": "bearer",
    "header": "Authorization",
    "template": "Bearer {token}",
    "credential_env_var": "HUBSPOT_BEARER_TOKEN",
    "credential_file": "/data/workspace/credentials/api-auth/hubspot.com.env",
    "token_type": "pat",  // pat, oauth, api_key, cookie, session
    "refresh_url": null,   // URL to refresh token (if OAuth)
    "expires_at": null     // ISO 8601 or null if unknown
  },
  "resources": {
    "deals": {
      "base_path": "/crm/v3/objects/deals",
      "confidence": 0.95,
      "endpoints": [
        {
          "action": "list",
          "method": "GET",
          "path": "/crm/v3/objects/deals",
          "params": {
            "query": {
              "limit": { "type": "integer", "required": false, "default": 50 },
              "offset": { "type": "integer", "required": false, "default": 0 },
              "properties": { "type": "string", "required": false, "description": "Comma-separated property names" }
            }
          },
          "response_schema": {
            "type": "object",
            "properties": {
              "results": { "type": "array", "items": { "type": "object" } },
              "paging": { "type": "object" }
            }
          },
          "script": "scripts/deals-list.sh",
          "confidence": 0.97,
          "last_verified": "2026-02-05T14:30:00Z",
          "avg_latency_ms": 230,
          "sample_response_keys": ["results", "paging"],
          "rate_limit": {
            "limit": 100,
            "window": "10s",
            "header": "X-RateLimit-Remaining"
          }
        },
        {
          "action": "get",
          "method": "GET",
          "path": "/crm/v3/objects/deals/{id}",
          "params": {
            "path": {
              "id": { "type": "string", "required": true }
            },
            "query": {
              "properties": { "type": "string", "required": false }
            }
          },
          "script": "scripts/deals-get.sh",
          "confidence": 0.95
        }
        // ... more endpoints
      ]
    },
    "contacts": {
      // ... similar structure
    }
  },
  "graphql": null,  // or GraphQL operations if detected
  "websockets": null,  // or WebSocket connection info
  "notes": [
    "Captured during authenticated session on app.hubspot.com",
    "Deal properties observed: dealname, amount, closedate, pipeline, dealstage",
    "Pagination uses cursor-based paging via 'after' parameter"
  ]
}
```

### 5.6 Skill Generator Script

```python
#!/usr/bin/env python3
"""
skill-gen.py — Generate OpenClaw skill from captured API traffic.

Usage:
    python3 skill-gen.py --domain hubspot.com --capture-dir /data/workspace/.api-captures/hubspot.com

Reads the latest capture from the capture directory, runs the classification
pipeline, and generates a complete skill in /data/shared/api-skills/{domain}/
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse, parse_qs

# Import our modules (same directory)
sys.path.insert(0, os.path.dirname(__file__))
from noise_filter import filter_noise
from api_classifier import cluster_endpoints, detect_crud, score_confidence
from auth_extractor import detect_auth_method, extract_auth_config

SHARED_SKILLS_DIR = "/data/shared/api-skills"
CREDENTIALS_DIR = "/data/workspace/credentials/api-auth"

def main():
    parser = argparse.ArgumentParser(description="Generate API skill from captures")
    parser.add_argument("--domain", required=True, help="Domain name")
    parser.add_argument("--capture-dir", required=True, help="Path to capture directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill")
    args = parser.parse_args()

    domain = args.domain
    capture_dir = Path(args.capture_dir)

    # Find the latest capture
    captures = sorted(capture_dir.glob("*/capture.jsonl"), reverse=True)
    if not captures:
        print(f"No captures found in {capture_dir}", file=sys.stderr)
        sys.exit(1)

    latest_capture = captures[0]
    print(f"Processing: {latest_capture}", file=sys.stderr)

    # Load captured requests
    requests = []
    with open(latest_capture) as f:
        for line in f:
            if line.strip():
                requests.append(json.loads(line))

    print(f"Loaded {len(requests)} raw requests", file=sys.stderr)

    # Step 1: Filter noise
    filtered = filter_noise(requests)
    print(f"After noise filter: {len(filtered)} requests", file=sys.stderr)

    if not filtered:
        print("No API requests found after filtering.", file=sys.stderr)
        sys.exit(0)

    # Step 2: Detect auth method
    auth_config = detect_auth_method(filtered)
    print(f"Auth method: {auth_config['type']}", file=sys.stderr)

    # Step 3: Cluster endpoints
    clusters = cluster_endpoints(filtered)
    print(f"Found {len(clusters)} resource clusters", file=sys.stderr)

    # Step 4: Detect CRUD for each cluster
    for name, endpoints in clusters.items():
        clusters[name] = {
            "endpoints": endpoints,
            "crud": detect_crud(name, endpoints),
            "confidence": score_confidence(endpoints),
        }

    # Step 5: Determine base URL
    base_url = extract_base_url(filtered)

    # Step 6: Generate skill
    skill_dir = Path(SHARED_SKILLS_DIR) / domain
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)

    # Generate endpoints.json
    endpoints_json = generate_endpoints_json(domain, base_url, auth_config, clusters)
    with open(skill_dir / "endpoints.json", "w") as f:
        json.dump(endpoints_json, f, indent=2)

    # Generate individual scripts
    for resource_name, cluster_data in clusters.items():
        for action, action_endpoints in cluster_data["crud"].items():
            if action == "other":
                continue
            script_name = f"{resource_name}-{action}.sh"
            script_content = generate_script(
                domain, base_url, resource_name, action,
                action_endpoints[0],  # Use first example
                auth_config
            )
            script_path = skill_dir / "scripts" / script_name
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)

    # Generate api.sh dispatcher
    dispatcher = generate_dispatcher(domain, clusters)
    with open(skill_dir / "api.sh", "w") as f:
        f.write(dispatcher)
    os.chmod(skill_dir / "api.sh", 0o755)

    # Generate SKILL.md
    skill_md = generate_skill_md(domain, base_url, auth_config, clusters, endpoints_json)
    with open(skill_dir / "SKILL.md", "w") as f:
        f.write(skill_md)

    # Generate .meta.json
    meta = {
        "domain": domain,
        "version": get_next_version(skill_dir),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "captured_by": os.environ.get("AGENT_NAME", "unknown"),
        "capture_file": str(latest_capture),
        "total_endpoints": sum(
            len(c["crud"]) - (1 if "other" in c["crud"] else 0)
            for c in clusters.values()
        ),
        "avg_confidence": sum(c["confidence"] for c in clusters.values()) / len(clusters),
        "last_verified": datetime.utcnow().isoformat() + "Z",
        "health_status": "unknown",
        "history": [],
    }
    meta_path = skill_dir / ".meta.json"
    if meta_path.exists():
        existing = json.loads(meta_path.read_text())
        meta["history"] = existing.get("history", [])
        meta["history"].append({
            "version": existing.get("version", 0),
            "generated_at": existing.get("generated_at"),
            "captured_by": existing.get("captured_by"),
        })
        # Keep only last 10 history entries
        meta["history"] = meta["history"][-10:]
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    # Generate auth config (references, NOT actual tokens)
    auth_config_file = skill_dir / ".auth" / "auth-config.json"
    auth_config_file.parent.mkdir(exist_ok=True)
    with open(auth_config_file, "w") as f:
        json.dump({
            "type": auth_config["type"],
            "credential_file": f"{CREDENTIALS_DIR}/{domain}.env",
            "env_var": auth_config.get("env_var", f"{domain_to_var(domain)}_AUTH_TOKEN"),
            "header": auth_config.get("header", "Authorization"),
            "template": auth_config.get("template", "Bearer {token}"),
            "setup_instructions": f"echo '{auth_config.get('env_var', 'AUTH_TOKEN')}=YOUR_TOKEN' > {CREDENTIALS_DIR}/{domain}.env",
        }, f, indent=2)

    # Update global registry
    update_registry(domain, meta, endpoints_json)

    # Store initial credentials if we captured them
    store_initial_credentials(domain, auth_config)

    print(f"\n✅ Skill generated: {skill_dir}", file=sys.stderr)
    print(f"   Resources: {', '.join(clusters.keys())}", file=sys.stderr)
    print(f"   Confidence: {meta['avg_confidence']:.0%}", file=sys.stderr)

def get_next_version(skill_dir):
    meta_path = skill_dir / ".meta.json"
    if meta_path.exists():
        existing = json.loads(meta_path.read_text())
        return existing.get("version", 0) + 1
    return 1

def domain_to_var(domain):
    return domain.upper().replace(".", "_").replace("-", "_")

def extract_base_url(requests):
    """Determine the base URL from captured requests."""
    urls = [r['url'] for r in requests]
    parsed = [urlparse(u) for u in urls]
    # Find most common scheme + host
    hosts = defaultdict(int)
    for p in parsed:
        hosts[f"{p.scheme}://{p.netloc}"] += 1
    return max(hosts, key=hosts.get)

def update_registry(domain, meta, endpoints_json):
    """Update the global skill registry."""
    registry_path = Path(SHARED_SKILLS_DIR) / "_registry.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
    else:
        registry = {"skills": {}, "updated_at": None}
    
    registry["skills"][domain] = {
        "version": meta["version"],
        "generated_at": meta["generated_at"],
        "captured_by": meta["captured_by"],
        "avg_confidence": meta["avg_confidence"],
        "resources": list(endpoints_json.get("resources", {}).keys()),
        "auth_type": endpoints_json.get("auth", {}).get("type", "unknown"),
        "endpoint_count": meta["total_endpoints"],
    }
    registry["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)

def store_initial_credentials(domain, auth_config):
    """Store captured credentials locally (NOT in shared directory)."""
    cred_dir = Path(CREDENTIALS_DIR)
    cred_dir.mkdir(parents=True, exist_ok=True)
    cred_file = cred_dir / f"{domain}.env"
    
    if cred_file.exists():
        return  # Don't overwrite existing credentials
    
    token = auth_config.get("captured_token")
    if token:
        env_var = auth_config.get("env_var", f"{domain_to_var(domain)}_AUTH_TOKEN")
        with open(cred_file, "w") as f:
            f.write(f"# Auto-captured credentials for {domain}\n")
            f.write(f"# Captured: {datetime.utcnow().isoformat()}Z\n")
            f.write(f"# WARNING: Token may expire. Re-capture if API returns 401.\n")
            f.write(f'{env_var}="{token}"\n')
        os.chmod(cred_file, 0o600)  # Owner read/write only

# Template generation functions would be defined here
# (generate_endpoints_json, generate_script, generate_dispatcher, generate_skill_md)
# Using the templates defined in sections 5.2, 5.3, 5.4, 5.5 above.

if __name__ == "__main__":
    main()
```

---

## 6. Fleet Distribution via Syncthing

### 6.1 Shared Folder Structure

```
/data/shared/api-skills/            ← Syncthing shared folder
├── _registry.json                  ← Global index (auto-updated)
├── _blocklist.json                 ← Sites to never capture
├── _config.json                    ← Fleet-wide settings
│
├── hubspot.com/                    ← One folder per domain
│   ├── SKILL.md                   ← ✅ Synced (skill definition)
│   ├── api.sh                     ← ✅ Synced (dispatcher)
│   ├── endpoints.json             ← ✅ Synced (endpoint catalog)
│   ├── .meta.json                 ← ✅ Synced (versioning)
│   ├── .auth/
│   │   └── auth-config.json       ← ✅ Synced (auth METHOD, not tokens)
│   └── scripts/
│       ├── deals-list.sh          ← ✅ Synced
│       └── ...
│
├── notion.so/
│   └── ...
│
└── twitter.com/
    └── ...

/data/workspace/credentials/api-auth/  ← LOCAL ONLY (NOT synced)
├── hubspot.com.env                    ← ❌ Never synced
├── notion.so.env                      ← ❌ Never synced
└── twitter.com.env                    ← ❌ Never synced
```

**Critical distinction:** Skills (scripts, schemas, documentation) are shared. Credentials (tokens, cookies, API keys) are **never** shared. Each agent stores its own credentials locally.

### 6.2 Conflict Resolution

**Problem:** Two agents (Molty and Raphael) both visit hubspot.com at the same time and generate skills simultaneously. Syncthing will detect a conflict.

**Resolution strategy: Version-based merge with last-writer-wins per resource.**

```jsonc
// .meta.json includes a vector clock for conflict detection
{
  "domain": "hubspot.com",
  "version": 3,
  "vector_clock": {
    "molty": 2,     // Molty has contributed 2 versions
    "raphael": 1    // Raphael has contributed 1 version
  },
  "generated_at": "2026-02-05T14:30:00Z",
  "captured_by": "molty",
  // ...
}
```

**Conflict resolution algorithm:**

1. When Syncthing detects a conflict (e.g., `endpoints.json.sync-conflict-...`), the self-heal script is triggered
2. Read both versions' `.meta.json` files
3. **Higher version wins overall** — the agent with more capture sessions has more data
4. **Per-resource merge:** If version A has 5 resources and version B has 3 different ones, merge to get all 8
5. **Per-endpoint: higher confidence wins** — if both captured the same endpoint, keep the one with higher confidence score
6. Write merged result, increment version, update vector clock
7. Delete the conflict file

**Practical simplification:** In Phase 1, use **last-writer-wins** (highest `generated_at` timestamp). The merge algorithm is Phase 3.

### 6.3 _registry.json (Global Index)

```jsonc
{
  "updated_at": "2026-02-05T14:30:00Z",
  "skills": {
    "hubspot.com": {
      "version": 3,
      "generated_at": "2026-02-05T14:30:00Z",
      "captured_by": "molty",
      "avg_confidence": 0.92,
      "resources": ["deals", "contacts", "companies", "tickets"],
      "auth_type": "bearer",
      "endpoint_count": 12,
      "health_status": "healthy",       // healthy, degraded, broken, unknown
      "last_health_check": "2026-02-05T15:00:00Z"
    },
    "notion.so": {
      "version": 1,
      "generated_at": "2026-02-04T09:15:00Z",
      "captured_by": "raphael",
      "avg_confidence": 0.88,
      "resources": ["pages", "databases", "blocks"],
      "auth_type": "bearer",
      "endpoint_count": 8,
      "health_status": "healthy",
      "last_health_check": "2026-02-05T14:00:00Z"
    }
  },
  "stats": {
    "total_skills": 2,
    "total_endpoints": 20,
    "fleet_agents": ["molty", "raphael"],
    "captures_today": 3
  }
}
```

### 6.4 _blocklist.json

```jsonc
{
  "description": "Sites that should NEVER be auto-captured",
  "updated_at": "2026-02-05T14:00:00Z",
  "domains": [
    // Banking & Financial
    "*.bank.com",
    "*.banking.*",
    "paypal.com",
    "stripe.com/dashboard",  // Stripe API is OK via official key, not capture
    
    // Health & Medical
    "*.health.*",
    "patient*.*",
    
    // Government
    "*.gov",
    "*.gov.*",
    
    // Auth providers (capture redirect flows, not admin panels)
    "accounts.google.com",
    "login.microsoftonline.com",
    "auth0.com/authorize",
    
    // OpenClaw itself (avoid recursion)
    "*.openclaw.ai",
    "*.railway.app"  // Our own infra
  ],
  "patterns": [
    // URL patterns to skip even on allowed domains
    "/admin/",
    "/settings/security",
    "/billing/",
    "/payment/",
    "/password/"
  ]
}
```

### 6.5 How New Agents Get Existing Skills

When a new agent (e.g., Leonardo 🔵) joins the fleet:

1. **Syncthing auto-syncs** — As soon as Syncthing connects, `/data/shared/api-skills/` is populated with all existing skills
2. **OpenClaw config** — The agent's `openclaw.json` includes `extraDirs: ["/data/shared/api-skills"]`
3. **Skills become available immediately** — OpenClaw loads skills at session start
4. **Credentials need setup** — The new agent needs its own tokens/cookies for authenticated APIs. The `.auth/auth-config.json` tells it exactly what to set up
5. **First use triggers auth check** — When the new agent tries an API skill and gets 401, the self-heal flow kicks in: browser → login → capture tokens → save to local credentials

### 6.6 Syncthing Configuration

```json
// Syncthing folder config for api-skills
{
  "id": "api-skills",
  "label": "API Skills (Fleet Shared)",
  "path": "/data/shared/api-skills",
  "type": "sendreceive",
  "fsWatcherEnabled": true,
  "fsWatcherDelayS": 5,
  "ignorePerms": false,
  "ignoreDelete": false,
  "maxConflicts": 10,
  "order": "newestFirst",
  "versioning": {
    "type": "simple",
    "params": {
      "keep": "5"
    }
  },
  // Ignore patterns (don't sync credentials or temp files)
  "ignore": [
    "*.env",
    "*.secret",
    "*.tmp",
    ".api-captures/",
    "credentials/"
  ]
}
```

---

## 7. Smart Fallback & Self-Healing

### 7.1 Decision Tree

```
Agent needs data from {domain}
        │
        ▼
┌───────────────────┐
│ Check _blocklist   │──YES──▶ Use browser directly (no capture)
│ Is domain blocked? │
└───────┬───────────┘
        │ NO
        ▼
┌───────────────────┐
│ Check _registry    │──NO──▶ ┌──────────────┐
│ Skill exists?      │        │ Use browser   │
└───────┬───────────┘        │ + CDP capture │
        │ YES                 │ + generate    │
        ▼                     │   skill       │
┌───────────────────┐        └──────────────┘
│ Check .meta.json   │
│ Health = healthy?  │──NO──▶ ┌──────────────┐
│ Age < 24h?         │        │ Try API first │
└───────┬───────────┘        │ If fail:      │
        │ YES                 │ browser +     │
        ▼                     │ re-capture    │
┌───────────────────┐        └──────────────┘
│ Check credentials  │
│ Exist locally?     │──NO──▶ ┌──────────────┐
└───────┬───────────┘        │ Prompt for    │
        │ YES                 │ credentials   │
        ▼                     │ OR browser    │
┌───────────────────┐        │ login flow    │
│ Execute API call   │        └──────────────┘
│ via skill script   │
└───────┬───────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Response?                              │
├───────────────────────────────────────┤
│ 2xx SUCCESS    → Return data          │
│ 401/403 AUTH   → Refresh token, retry │
│ 404 GONE       → Re-capture skill     │
│ 429 RATE LIMIT → Wait + retry         │
│ 5xx ERROR      → Fallback to browser  │
│ Timeout        → Fallback to browser  │
└───────────────────────────────────────┘
```

### 7.2 Skill Router Script

```bash
#!/usr/bin/env bash
# skill-router.sh — Smart routing: API skill vs browser
#
# Usage: skill-router.sh <url> <intent>
# Example: skill-router.sh "https://app.hubspot.com/deals" "list all deals"
#
# Exit codes:
#   0 = success (data on stdout)
#   1 = permanent failure
#   2 = auth needed (human intervention required)

set -euo pipefail

URL="$1"
INTENT="${2:-browse}"
DOMAIN=$(echo "$URL" | sed 's|https\?://||' | sed 's|/.*||' | sed 's|^www\.||')
SKILLS_DIR="/data/shared/api-skills"
CAPTURES_DIR="/data/workspace/.api-captures"
REGISTRY="$SKILLS_DIR/_registry.json"
BLOCKLIST="$SKILLS_DIR/_blocklist.json"

# --- Check blocklist ---
if [[ -f "$BLOCKLIST" ]]; then
  if jq -r '.domains[]' "$BLOCKLIST" 2>/dev/null | grep -qiF "$DOMAIN"; then
    echo "BLOCKED: $DOMAIN is in the blocklist. Using browser only." >&2
    exit 10  # Signal to caller: use browser, don't capture
  fi
fi

# --- Check if skill exists ---
SKILL_DIR="$SKILLS_DIR/$DOMAIN"
if [[ -d "$SKILL_DIR" && -f "$SKILL_DIR/endpoints.json" ]]; then
  echo "Found existing skill for $DOMAIN" >&2
  
  # Check health
  META="$SKILL_DIR/.meta.json"
  HEALTH=$(jq -r '.health_status // "unknown"' "$META" 2>/dev/null || echo "unknown")
  
  if [[ "$HEALTH" == "broken" ]]; then
    echo "Skill is marked broken. Falling back to browser + re-capture." >&2
    exec bash "$(dirname "$0")/browser-capture.sh" "$URL" "$DOMAIN"
  fi
  
  # Try the API skill
  echo "Attempting API skill..." >&2
  RESULT=$(bash "$SKILL_DIR/api.sh" "$@" 2>/tmp/skill-error.log) && {
    echo "$RESULT"
    
    # Update health status
    jq '.health_status = "healthy" | .last_verified = now | todate' "$META" > "$META.tmp" \
      && mv "$META.tmp" "$META" 2>/dev/null || true
    
    exit 0
  }
  
  EXIT_CODE=$?
  ERROR=$(cat /tmp/skill-error.log 2>/dev/null || echo "unknown")
  
  case $EXIT_CODE in
    2)  # Auth expired
      echo "Auth expired for $DOMAIN. Attempting re-auth..." >&2
      # Try browser login to get new tokens
      bash "$(dirname "$0")/browser-reauth.sh" "$DOMAIN" && {
        # Retry with new credentials
        RESULT=$(bash "$SKILL_DIR/api.sh" "$@" 2>/dev/null) && {
          echo "$RESULT"
          exit 0
        }
      }
      echo "Re-auth failed. Manual intervention needed." >&2
      exit 2
      ;;
    3)  # Rate limited
      echo "Rate limited on $DOMAIN. Waiting and retrying..." >&2
      sleep 10
      RESULT=$(bash "$SKILL_DIR/api.sh" "$@" 2>/dev/null) && {
        echo "$RESULT"
        exit 0
      }
      echo "Still rate limited. Falling back to browser." >&2
      ;;
    4)  # Endpoint gone (404)
      echo "Endpoint may have changed. Re-capturing..." >&2
      # Mark as degraded
      jq '.health_status = "degraded"' "$META" > "$META.tmp" && mv "$META.tmp" "$META"
      ;;
    *)
      echo "API skill failed (exit $EXIT_CODE): $ERROR" >&2
      ;;
  esac
  
  # Fall through to browser + re-capture
  echo "Falling back to browser with re-capture..." >&2
fi

# --- No skill exists (or skill failed) → Browser + Capture ---
echo "No working skill for $DOMAIN. Using browser with API capture..." >&2
exec bash "$(dirname "$0")/browser-capture.sh" "$URL" "$DOMAIN"
```

### 7.3 Token/Cookie Expiry Detection

```python
def check_token_expiry(domain):
    """Proactively check if stored tokens are about to expire."""
    cred_file = f"/data/workspace/credentials/api-auth/{domain}.env"
    auth_config_file = f"/data/shared/api-skills/{domain}/.auth/auth-config.json"
    
    if not os.path.exists(cred_file) or not os.path.exists(auth_config_file):
        return {"status": "missing", "action": "browser_login"}
    
    with open(auth_config_file) as f:
        auth_config = json.load(f)
    
    # Load token
    token = None
    with open(cred_file) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                _, token = line.strip().split('=', 1)
                token = token.strip('"').strip("'")
                break
    
    if not token:
        return {"status": "missing", "action": "browser_login"}
    
    # Check if JWT (decode without verification to check exp)
    if token.count('.') == 2:
        try:
            import base64
            payload = token.split('.')[1]
            # Add padding
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            exp = decoded.get('exp')
            if exp:
                exp_time = datetime.fromtimestamp(exp)
                now = datetime.utcnow()
                if exp_time < now:
                    return {"status": "expired", "action": "refresh_or_reauth",
                            "expired_at": exp_time.isoformat()}
                elif (exp_time - now).total_seconds() < 3600:  # < 1 hour
                    return {"status": "expiring_soon", "action": "proactive_refresh",
                            "expires_at": exp_time.isoformat()}
                else:
                    return {"status": "valid", "expires_at": exp_time.isoformat()}
        except Exception:
            pass  # Not a JWT, can't check expiry
    
    # For non-JWT tokens, try a lightweight API call
    return {"status": "unknown", "action": "health_check"}
```

### 7.4 Self-Heal Cron Job

Run every 6 hours to proactively check skill health:

```bash
#!/usr/bin/env bash
# self-heal.sh — Proactive health check for all API skills
# Run via cron or heartbeat

SKILLS_DIR="/data/shared/api-skills"
REGISTRY="$SKILLS_DIR/_registry.json"
DEGRADED=()
BROKEN=()

for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -f "$skill_dir/api.sh" ]] || continue
  domain=$(basename "$skill_dir")
  
  echo "Checking $domain..." >&2
  
  # Run health check
  if bash "$skill_dir/api.sh" --health >/dev/null 2>&1; then
    # Update meta
    jq '.health_status = "healthy" | .last_verified = (now | todate)' \
      "$skill_dir/.meta.json" > "$skill_dir/.meta.json.tmp" \
      && mv "$skill_dir/.meta.json.tmp" "$skill_dir/.meta.json"
    echo "  ✅ $domain: healthy" >&2
  else
    EXIT=$?
    if [[ $EXIT -eq 2 ]]; then
      DEGRADED+=("$domain (auth expired)")
      jq '.health_status = "degraded"' "$skill_dir/.meta.json" > "$skill_dir/.meta.json.tmp" \
        && mv "$skill_dir/.meta.json.tmp" "$skill_dir/.meta.json"
      echo "  ⚠️  $domain: auth expired" >&2
    else
      BROKEN+=("$domain (error: $EXIT)")
      jq '.health_status = "broken"' "$skill_dir/.meta.json" > "$skill_dir/.meta.json.tmp" \
        && mv "$skill_dir/.meta.json.tmp" "$skill_dir/.meta.json"
      echo "  ❌ $domain: broken" >&2
    fi
  fi
done

# Report to coordinator if any issues
if [[ ${#DEGRADED[@]} -gt 0 || ${#BROKEN[@]} -gt 0 ]]; then
  echo "=== SKILL HEALTH REPORT ==="
  echo "Degraded: ${DEGRADED[*]:-none}"
  echo "Broken: ${BROKEN[*]:-none}"
  
  # TODO: Send webhook to Molty's command-center channel
  # curl -X POST "$MOLTY_WEBHOOK" -d "{\"text\": \"API Skill Alert: ...\"}"
fi
```

### 7.5 Rate Limiting Awareness

Skills detect rate limit info from response headers and implement backoff:

```bash
# Built into each generated script
handle_rate_limit() {
  local response_headers="$1"
  local retry_after=$(echo "$response_headers" | grep -i 'retry-after:' | awk '{print $2}')
  local remaining=$(echo "$response_headers" | grep -i 'x-ratelimit-remaining:' | awk '{print $2}')
  
  if [[ -n "$retry_after" ]]; then
    echo "Rate limited. Waiting ${retry_after}s..." >&2
    sleep "$retry_after"
  elif [[ -n "$remaining" && "$remaining" -le 5 ]]; then
    echo "Rate limit approaching ($remaining remaining). Slowing down..." >&2
    sleep 2
  fi
}
```

---

## 8. Sub-Agent Integration

### 8.1 How Sub-Agents Discover Skills

Sub-agents have `exec` access but no `browser` access. They discover API skills through:

1. **Direct file listing:**
   ```bash
   exec ls /data/shared/api-skills/
   exec cat /data/shared/api-skills/_registry.json
   ```

2. **Skill search script:**
   ```bash
   exec /data/workspace/scripts/api-capture/skill-search.sh "hubspot deals"
   # Returns: /data/shared/api-skills/hubspot.com/scripts/deals-list.sh
   ```

3. **OpenClaw skill loading:** If `extraDirs` is configured, sub-agents see `api-hubspot-com` as a regular skill and can read its SKILL.md for instructions.

### 8.2 How Sub-Agents Call Skills

```bash
# List HubSpot deals
exec /data/shared/api-skills/hubspot.com/api.sh deals list --limit 10

# Get a specific deal
exec /data/shared/api-skills/hubspot.com/scripts/deals-get.sh --id 12345

# Search contacts
exec /data/shared/api-skills/hubspot.com/api.sh contacts search --query "john"

# Raw output (for piping)
exec /data/shared/api-skills/hubspot.com/api.sh deals list --raw | jq '.results[0].properties'
```

### 8.3 Escalation: No Skill Available

When a sub-agent needs data from a site that hasn't been captured:

```
Sub-Agent: "I need data from crunchbase.com but there's no API skill."
         │
         ▼
┌──────────────────────────┐
│ Check _registry.json     │
│ crunchbase.com exists?   │──YES──▶ Use it
└───────────┬──────────────┘
            │ NO
            ▼
┌──────────────────────────┐
│ Write escalation request │
│ to /data/shared/          │
│ api-skill-requests/       │
│ crunchbase.com.json       │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Parent agent (with        │
│ browser) picks up request │
│ via heartbeat/polling     │
│ → Browser + Capture       │
│ → Generate skill          │
│ → Skill appears via sync  │
└──────────────────────────┘
```

**Escalation request format:**

```jsonc
// /data/shared/api-skill-requests/crunchbase.com.json
{
  "domain": "crunchbase.com",
  "requested_by": "raphael-sub-1",
  "requested_at": "2026-02-05T14:30:00Z",
  "url": "https://www.crunchbase.com/organization/example",
  "intent": "Get company funding data",
  "priority": "normal",  // normal, urgent
  "status": "pending"    // pending, in_progress, completed, failed
}
```

### 8.4 Sandboxing Considerations

- Sub-agents run in a restricted context (no browser, limited tool access)
- Generated scripts use only `curl`, `jq`, `bash` — all available in sandboxed environments
- Credentials are loaded from files (the sub-agent needs read access to `/data/workspace/credentials/`)
- Output is JSON on stdout, errors on stderr — clean for piping
- Exit codes are standardized (0=success, 1=error, 2=auth, 3=rate limit, 4=endpoint gone)

---

## 9. Security Considerations

### 9.1 Credential Storage

**Cardinal rule: Credentials NEVER appear in shared files.**

```
SHARED (Syncthing):                    LOCAL ONLY:
├── api-skills/hubspot.com/            ├── credentials/api-auth/
│   ├── SKILL.md          ← no tokens │   ├── hubspot.com.env   ← tokens here
│   ├── api.sh            ← no tokens │   ├── notion.so.env
│   ├── endpoints.json    ← no tokens │   └── ...
│   └── .auth/                         │
│       └── auth-config.json ← method │
│           only, no values            │
```

The `.auth/auth-config.json` contains:
- Auth **type** (bearer, cookie, api_key) — ✅ shared
- Auth **header name** (Authorization, X-Api-Key) — ✅ shared
- Auth **template** ("Bearer {token}") — ✅ shared
- Auth **env var name** (HUBSPOT_BEARER_TOKEN) — ✅ shared
- Auth **actual token value** — ❌ **NEVER** shared

### 9.2 Credential Rotation

When a token expires:
1. Self-heal detects 401 response
2. Checks for refresh token flow (if OAuth)
3. If refresh available: auto-refresh and update local credential file
4. If no refresh: mark skill as "degraded" and alert coordinator
5. Human or browser-capable agent logs in again to get new token
6. New token saved to local credential store

### 9.3 Sites That Should NOT Be Auto-Captured

The `_blocklist.json` (Section 6.4) prevents capture of sensitive sites. Additionally:

**Capture but don't share (local-only skills):**
- Internal company tools with PII
- HR/payroll systems
- Medical/health portals
- Legal document systems

**Implementation:** Add a `"share": false` flag in `.meta.json` to keep a skill local:
```jsonc
{
  "domain": "internal-hr.company.com",
  "share": false,  // Stays in /data/workspace/skills/, NOT shared
  // ...
}
```

### 9.4 Data Sanitization Before Sharing

Before writing to `/data/shared/api-skills/`:

1. **Strip response bodies** from endpoints.json (only keep schema, not actual data)
2. **Redact PII** from sample responses (emails, names, phone numbers)
3. **Remove cookies** from any captured headers
4. **Sanitize URLs** (remove query params that contain tokens)
5. **Check for accidental secrets** in SKILL.md (regex scan for patterns like `Bearer xxx`, API keys)

```python
SENSITIVE_PATTERNS = [
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    r'[A-Za-z0-9]{32,}',  # Long opaque tokens
    r'sk-[A-Za-z0-9]{32,}',  # OpenAI-style keys
    r'ghp_[A-Za-z0-9]{36}',  # GitHub PATs
    r'pat-[a-z]{3}-[A-Za-z0-9-]+',  # HubSpot PATs
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Emails
]

def sanitize_for_sharing(content):
    """Remove sensitive data before sharing."""
    for pattern in SENSITIVE_PATTERNS:
        content = re.sub(pattern, '[REDACTED]', content)
    return content
```

### 9.5 Privacy Implications

- **Skill metadata reveals browsing patterns** — which sites agents visit, when, how often
- **Endpoint schemas reveal data structures** — could hint at internal company data models
- **Mitigation:** All sharing is within our own fleet (Syncthing is P2P, no cloud). The risk is between our own agents, which is acceptable
- **If fleet grows beyond trusted agents:** Implement skill-level access control via a permissions field in `.meta.json`

---

## 10. Edge Cases

### 10.1 Heavy Client-Side JS Processing

**Problem:** Some sites do significant data transformation in JavaScript before displaying results. The raw API response may be incomplete or require client-side joins.

**Solution:**
- Capture ALL API calls (including multiple sequential calls that build a page)
- In `endpoints.json`, note "depends_on" relationships between calls
- Generate composite scripts that make multiple API calls and merge results
- Mark these as `"composite": true` with lower confidence

### 10.2 GraphQL APIs

**Problem:** Single endpoint (`/graphql`), all variation is in the request body.

**Solution:** (Detailed in Section 4.7)
- Detect GraphQL queries in POST bodies
- Extract operation names and variables
- Generate one script per operation (not per endpoint)
- Variable substitution via command-line args
- Include the full query string in the script (it's the "schema")

**Generated script example:**
```bash
#!/usr/bin/env bash
# GraphQL: GetDeals query
QUERY='query GetDeals($first: Int, $after: String) {
  deals(first: $first, after: $after) {
    edges { node { id name amount } }
    pageInfo { hasNextPage endCursor }
  }
}'

VARIABLES=$(jq -nc --argjson first "${1:-10}" --arg after "${2:-}" \
  '{first: $first, after: (if $after == "" then null else $after end)}')

source /data/workspace/credentials/api-auth/${DOMAIN}.env
curl -s -X POST "$BASE_URL/graphql" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg q "$QUERY" --argjson v "$VARIABLES" '{query: $q, variables: $v}')"
```

### 10.3 Anti-Bot Measures (Cloudflare, CAPTCHAs)

**Problem:** Some API calls require cookies/headers set by Cloudflare JS challenges.

**Solutions:**
1. **cf_clearance cookie:** Capture the Cloudflare clearance cookie during browser session. Include it in the credential store. Note: these expire frequently (typically 15-30 minutes).
2. **Fallback-first:** For Cloudflare-protected sites, always prefer browser. Don't generate API skills unless the underlying API has its own auth (not Cloudflare).
3. **Detection:** If API calls consistently return 403 with Cloudflare challenge HTML, mark the skill as `"requires_browser_session": true` and don't share it.

### 10.4 WebSocket-Only Real-Time Apps

**Problem:** Some apps (Slack, Discord, live dashboards) use WebSockets for all data.

**Solution:**
- Capture WebSocket handshake URL and protocol
- Record message patterns (JSON schemas for sent/received messages)
- Generate skills that document the WS protocol but don't produce curl scripts
- Instead, generate Node.js one-liners for WS connections:
  ```bash
  node -e "const ws=new(require('ws'))('$WS_URL',{headers:{Authorization:'Bearer $TOKEN'}});
           ws.on('message',d=>console.log(d));ws.on('open',()=>ws.send('$MESSAGE'));"
  ```
- Mark these as `"type": "websocket"` with specific handling instructions in SKILL.md

### 10.5 Browser Fingerprinting

**Problem:** Some sites check TLS fingerprints, canvas fingerprints, or other browser-specific signals.

**Solution:**
- API skills bypass this entirely (we're calling the API, not the website)
- For sites where the API itself checks fingerprints: mark as `"browser_only": true`
- Use `curl --ciphers` to approximate TLS fingerprints if needed
- Last resort: always use browser for these sites

### 10.6 Rate-Limited APIs

**Solution:**
- Extract rate limit headers during capture (X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After)
- Record in `endpoints.json` under `rate_limit` field
- Generated scripts implement backoff (Section 7.5)
- Skill router queues requests when approaching limits
- Fleet-wide: don't have multiple agents hammering the same API

### 10.7 Paginated Responses

**Solution:**
- Detect pagination patterns from captured traffic:
  - Offset-based: `?offset=0&limit=50`, `?offset=50&limit=50`
  - Cursor-based: `?after=abc123`
  - Page-based: `?page=1&per_page=50`
- Record pagination pattern in `endpoints.json`
- Generate `--all` flag in list scripts that auto-paginates:
  ```bash
  # In deals-list.sh
  if [[ "$ALL" == true ]]; then
    OFFSET=0
    while true; do
      RESULT=$(fetch_page "$OFFSET" "$LIMIT")
      echo "$RESULT" | jq -c '.results[]'
      NEXT=$(echo "$RESULT" | jq -r '.paging.next.after // empty')
      [[ -z "$NEXT" ]] && break
      OFFSET="$NEXT"
      sleep 0.5  # Be polite
    done
  fi
  ```

### 10.8 File Uploads/Downloads

**Solution:**
- **Downloads:** Detect binary Content-Types (application/pdf, image/*, etc.) and generate scripts with `curl -o` output
- **Uploads:** Capture multipart/form-data requests. Generate scripts using `curl -F` syntax
- Mark these endpoints as `"type": "file_transfer"` in endpoints.json
- Include file path as a parameter in generated scripts

### 10.9 OAuth Redirect Flows

**Problem:** OAuth requires a multi-step browser redirect dance.

**Solution:**
1. During capture, detect the full OAuth flow:
   - Initial redirect to auth provider
   - User consent page
   - Callback with auth code
   - Code → token exchange
2. Record the token endpoint and required parameters
3. Generate a separate `auth-refresh.sh` script that can exchange refresh tokens
4. For initial auth: always require browser (can't automate user consent)
5. Store both access_token and refresh_token in credential file:
   ```bash
   # hubspot.com.env
   HUBSPOT_ACCESS_TOKEN="xxx"
   HUBSPOT_REFRESH_TOKEN="yyy"
   HUBSPOT_TOKEN_EXPIRY="2026-02-05T16:30:00Z"
   HUBSPOT_CLIENT_ID="zzz"
   HUBSPOT_TOKEN_URL="https://api.hubapi.com/oauth/v1/token"
   ```

---

## 11. Implementation Roadmap

### Phase 1: MVP — Capture & Generate (Est: 20-30 hours)

**Goal:** Single agent can browse a site, capture API traffic, and generate a working skill.

**Components:**
1. CDP Network Capture (Node.js) — 8h
   - `cdp-capture.js`: Attach to CDP, capture Network events
   - Basic noise filter (hardcoded patterns)
   - JSONL output format
2. Skill Generator (Python) — 10h
   - `skill-gen.py`: Read captures, cluster endpoints, generate files
   - Basic URL normalization
   - Simple CRUD detection
   - Shell script templates
   - SKILL.md generation
   - endpoints.json output
3. Credential Handling — 4h
   - Auth detection (Bearer, API key, Cookie)
   - Local credential store (`/data/workspace/credentials/api-auth/`)
   - Credential loading in generated scripts
4. Manual Integration — 3h
   - Bash wrapper to run capture alongside browser
   - Basic skill-router.sh (check skill exists → use or fallback)
   - README/documentation

**Testing:** Manually capture 3 sites (HubSpot, Notion, a public API). Verify generated scripts work.

**Success metric:** Generated skill executes successfully and returns correct data in <500ms.

**Assigned to:** Molty 🦎 (has browser access, coordinates infrastructure)

### Phase 2: Fleet Distribution (Est: 10-15 hours)

**Goal:** Skills auto-share across agents via Syncthing. Any agent can use skills captured by another.

**Components:**
1. Syncthing Folder Setup — 2h
   - Configure `/data/shared/api-skills/` on all agents
   - Set up ignore patterns (credentials, temp files)
2. Global Registry — 3h
   - `_registry.json` management
   - `_blocklist.json`
   - Skill search script for sub-agents
3. OpenClaw Integration — 3h
   - `extraDirs` configuration
   - Skill naming convention (api-{domain})
   - Test skill loading across agents
4. Conflict Resolution — 4h
   - Basic last-writer-wins
   - .meta.json version tracking
   - Conflict detection script

**Testing:** Molty captures HubSpot → verify Raphael can use the skill. Both capture same site → verify conflict resolution.

**Success metric:** Skill captured on Agent A is usable on Agent B within 60 seconds.

**Assigned to:** Molty 🦎 (Syncthing admin) + Raphael 🔴 (testing)

### Phase 3: Self-Healing & Smart Routing (Est: 15-20 hours)

**Goal:** System automatically detects failures, refreshes tokens, and re-captures when needed.

**Components:**
1. Smart Skill Router — 5h
   - Full decision tree (Section 7.1)
   - Automatic fallback browser → re-capture
   - Retry logic with exponential backoff
2. Token Expiry Detection — 4h
   - JWT decode for expiry check
   - Proactive refresh flow
   - OAuth refresh_token support
3. Health Check System — 4h
   - `self-heal.sh` cron job
   - Per-endpoint health tracking
   - Degradation detection (response schema changes)
4. Alerting — 3h
   - Webhook to Molty's command center
   - Discord notifications for broken skills
   - Weekly health report

**Testing:** Expire a token → verify system detects and handles it. Change an API response → verify schema change detection.

**Success metric:** System recovers from auth failure within 5 minutes without human intervention.

**Assigned to:** Molty 🦎 (coordination) + Donatello 🟣 (when available, for research on edge cases)

### Phase 4: Sub-Agent Integration (Est: 8-12 hours)

**Goal:** Sub-agents can discover and use API skills, and escalate requests for uncaptured sites.

**Components:**
1. Skill Discovery API — 3h
   - `skill-search.sh` script
   - Natural language to skill matching
   - Registry querying
2. Escalation System — 4h
   - Request queue (`/data/shared/api-skill-requests/`)
   - Parent agent polling for new requests
   - Status tracking
3. Documentation — 2h
   - Sub-agent usage guide
   - Error handling guide
   - Examples for common patterns

**Testing:** Sub-agent asks for HubSpot data → uses existing skill. Sub-agent asks for unknown site → escalation works.

**Success metric:** Sub-agent can retrieve data from captured site without browser access.

**Assigned to:** Raphael 🔴 (has sub-agents, can test directly)

### Phase 5: Advanced Features (Est: 20-30 hours)

**Goal:** Handle edge cases, improve accuracy, add GraphQL support.

**Components:**
1. GraphQL Support — 8h
2. Pagination Auto-Detection — 4h
3. WebSocket Skill Generation — 6h
4. Advanced Conflict Resolution (vector clocks, per-resource merge) — 5h
5. Composite API Calls (multi-request workflows) — 6h
6. Performance Dashboard — 3h

**Assigned to:** Donatello 🟣 (research/technical depth)

### Phase Summary

| Phase | Description | Hours | Dependencies | Agent |
|-------|-------------|-------|--------------|-------|
| 1 | MVP: Capture & Generate | 20-30h | None | Molty 🦎 |
| 2 | Fleet Distribution | 10-15h | Phase 1 | Molty 🦎 + Raphael 🔴 |
| 3 | Self-Healing | 15-20h | Phase 1, 2 | Molty 🦎 |
| 4 | Sub-Agent Integration | 8-12h | Phase 1, 2 | Raphael 🔴 |
| 5 | Advanced Features | 20-30h | Phase 1-3 | Donatello 🟣 |
| **Total** | | **73-107h** | | |

### Testing Strategy

1. **Unit tests per component:** Each script has a `--test` flag that runs against mock data
2. **Integration tests:** End-to-end capture → generate → use for 5+ real sites
3. **Fleet tests:** Cross-agent skill sharing and conflict scenarios
4. **Chaos tests:** Token expiry, API changes, rate limits, network failures
5. **Regression tests:** Periodically re-capture known sites and compare with existing skills

### Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| API call latency | <500ms (vs 10-45s browser) | Timing in scripts |
| Skill generation success | >80% of captures produce working skills | Registry stats |
| Fleet sync latency | <60s for new skill to reach all agents | Syncthing metrics |
| Self-healing rate | >90% of failures auto-recovered | Health check logs |
| Sub-agent adoption | >50% of data requests use API skills | Usage logs |
| Sites captured | 20+ within first month | Registry count |

---

## 12. Example Walkthrough: HubSpot

Let's trace the complete flow from Molty browsing HubSpot to Raphael's sub-agent using the generated skill.

### Step 1: Molty Browses HubSpot

Molty (via main session with browser access) is asked: *"Show me all open deals in HubSpot."*

Molty checks: Does `/data/shared/api-skills/hubspot.com/` exist? → **No.**

Molty uses the browser tool to visit `https://app.hubspot.com/contacts/deals`:

```
[Molty] Using browser to visit https://app.hubspot.com/contacts/deals
        (No API skill exists yet — capturing traffic...)
```

### Step 2: CDP Capture Runs Alongside

While the browser loads HubSpot, `cdp-capture.js` is attached to the same CDP session:

```bash
$ node /data/workspace/scripts/api-capture/cdp-capture.js \
    "ws://127.0.0.1:9222/devtools/page/ABC123" \
    "hubspot.com" \
    "/data/workspace/.api-captures"
```

The capture observes ~150 network requests. After noise filtering, 12 remain:

```
[cdp-capture] Connected to ws://127.0.0.1:9222/devtools/page/ABC123
[cdp-capture] Monitoring hubspot.com
[cdp-capture] 150 total requests observed
[cdp-capture] 138 filtered as noise (analytics, CDN, tracking)
[cdp-capture] 12 API requests captured to .api-captures/hubspot.com/2026-02-05T14-30-00Z/capture.jsonl
```

**Sample captured requests:**
```
GET  https://api.hubapi.com/crm/v3/objects/deals?limit=50&properties=dealname,amount,closedate,dealstage,pipeline
GET  https://api.hubapi.com/crm/v3/objects/deals/12345?properties=dealname,amount
GET  https://api.hubapi.com/crm/v3/objects/contacts?limit=20
POST https://api.hubapi.com/crm/v3/objects/deals/search  {"filterGroups":[...],"sorts":[...]}
GET  https://api.hubapi.com/crm/v3/pipelines/deals
GET  https://api.hubapi.com/crm/v3/properties/deals
POST https://api.hubapi.com/collector/graphql  (HubSpot internal GraphQL for UI components)
```

### Step 3: Skill Generation

After the browser session completes:

```bash
$ python3 /data/workspace/scripts/api-capture/skill-gen.py \
    --domain hubspot.com \
    --capture-dir /data/workspace/.api-captures/hubspot.com
```

Output:
```
Processing: .api-captures/hubspot.com/2026-02-05T14-30-00Z/capture.jsonl
Loaded 12 raw requests
After noise filter: 12 requests
Auth method: bearer (Authorization: Bearer pat-na1-...)
Found 4 resource clusters: deals, contacts, pipelines, properties
Generating scripts...

✅ Skill generated: /data/shared/api-skills/hubspot.com/
   Resources: deals, contacts, pipelines, properties
   Confidence: 93%
```

### Step 4: Generated Files

**`/data/shared/api-skills/hubspot.com/SKILL.md`:**
```markdown
---
name: api-hubspot-com
description: Auto-captured API skill for hubspot.com. Direct API access to deals, contacts, pipelines, properties.
metadata: {"openclaw":{"requires":{"bins":["curl","jq"]}}}
---

# HubSpot API Skill (Auto-Captured)

**Generated:** 2026-02-05T14:31:00Z
**Captured by:** molty
**Confidence:** 93%

## Quick Start

Use `{baseDir}/api.sh` to interact with HubSpot's CRM API directly.

### Available Actions

#### Deals
- **List:** `exec {baseDir}/scripts/deals-list.sh [--limit N] [--offset N]`
- **Get:** `exec {baseDir}/scripts/deals-get.sh --id {ID}`
- **Search:** `exec {baseDir}/scripts/deals-search.sh --query '{"filterGroups":[...]}'`

#### Contacts
- **List:** `exec {baseDir}/scripts/contacts-list.sh [--limit N]`

#### Pipelines
- **List:** `exec {baseDir}/scripts/pipelines-list.sh`

#### Properties
- **List:** `exec {baseDir}/scripts/properties-list.sh`

### Dispatcher
```bash
exec {baseDir}/api.sh deals list --limit 10
exec {baseDir}/api.sh deals get --id 12345
exec {baseDir}/api.sh contacts list --limit 20
```

## Authentication

This API requires **Bearer token** authentication.
Credentials loaded from `/data/workspace/credentials/api-auth/hubspot.com.env`.

```bash
echo 'HUBSPOT_COM_AUTH_TOKEN="pat-na1-your-token"' > /data/workspace/credentials/api-auth/hubspot.com.env
```
```

**`/data/shared/api-skills/hubspot.com/scripts/deals-list.sh`:**
```bash
#!/usr/bin/env bash
# Auto-generated API script for: GET /crm/v3/objects/deals
# Domain: hubspot.com
# Resource: deals | Action: list | Confidence: 0.97
# Generated: 2026-02-05T14:31:00Z | Captured by: molty

set -euo pipefail

BASE_URL="https://api.hubapi.com"
ENDPOINT="/crm/v3/objects/deals"
METHOD="GET"
CRED_FILE="/data/workspace/credentials/api-auth/hubspot.com.env"

if [[ -f "$CRED_FILE" ]]; then
  source "$CRED_FILE"
else
  echo "ERROR: No credentials at $CRED_FILE" >&2
  echo "Run: echo 'HUBSPOT_COM_AUTH_TOKEN=\"your-token\"' > $CRED_FILE" >&2
  exit 1
fi

LIMIT="50"
OFFSET=""
PROPERTIES="dealname,amount,closedate,dealstage,pipeline"
RAW=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --offset) OFFSET="$2"; shift 2 ;;
    --properties) PROPERTIES="$2"; shift 2 ;;
    --raw) RAW=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    --help) head -20 "$0" | grep '^#' | sed 's/^# \?//'; exit 0 ;;
    *) echo "Unknown: $1" >&2; exit 1 ;;
  esac
done

URL="${BASE_URL}${ENDPOINT}?limit=${LIMIT}"
[[ -n "$PROPERTIES" ]] && URL="${URL}&properties=${PROPERTIES}"
[[ -n "$OFFSET" ]] && URL="${URL}&after=${OFFSET}"

CURL_CMD=(curl -s -w "\n%{http_code}" -X GET
  -H "Authorization: Bearer ${HUBSPOT_COM_AUTH_TOKEN}"
  -H "Accept: application/json"
  "$URL")

if [[ "$DRY_RUN" == true ]]; then
  echo "${CURL_CMD[@]}"
  exit 0
fi

RESPONSE=$("${CURL_CMD[@]}" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
  if [[ "$RAW" == true ]]; then echo "$BODY"; else echo "$BODY" | jq '.'; fi
elif [[ "$HTTP_CODE" == "401" || "$HTTP_CODE" == "403" ]]; then
  echo "AUTH_EXPIRED" >&2; exit 2
elif [[ "$HTTP_CODE" == "429" ]]; then
  echo "RATE_LIMITED" >&2; exit 3
else
  echo "API_ERROR:$HTTP_CODE" >&2; echo "$BODY" >&2; exit 1
fi
```

**`/data/workspace/credentials/api-auth/hubspot.com.env`** (LOCAL ONLY — not synced):
```bash
# Auto-captured credentials for hubspot.com
# Captured: 2026-02-05T14:31:00Z
# WARNING: Token may expire. Re-capture if API returns 401.
HUBSPOT_COM_AUTH_TOKEN="pat-na1-abcdef1234567890"
```

### Step 5: Syncthing Distributes the Skill

Within seconds, Syncthing syncs `/data/shared/api-skills/hubspot.com/` to all connected agents:

```
Molty → Syncthing → Raphael
                  → Leonardo (when online)
                  → Donatello (when online)
```

Raphael receives:
- `SKILL.md`, `api.sh`, `endpoints.json`, `.meta.json`, scripts/
- But NOT the credentials file (that's local to Molty)

### Step 6: Raphael's Sub-Agent Uses the Skill

Later, Raphael's sub-agent needs HubSpot deal data:

```
[Raphael Sub-Agent] Task: "Get the latest deals from HubSpot"

1. Check registry:
   $ cat /data/shared/api-skills/_registry.json | jq '.skills["hubspot.com"]'
   → Found! Version 1, confidence 93%, healthy

2. But no credentials yet:
   $ cat /data/workspace/credentials/api-auth/hubspot.com.env
   → File not found

3. Escalate to parent (Raphael):
   "I found a HubSpot API skill but need credentials. 
    Please set up: echo 'HUBSPOT_COM_AUTH_TOKEN=your-token' > /data/workspace/credentials/api-auth/hubspot.com.env"

4. After Raphael provides credentials:
   $ exec /data/shared/api-skills/hubspot.com/api.sh deals list --limit 5
```

**Response (200ms instead of 30s):**
```json
{
  "results": [
    {
      "id": "12345",
      "properties": {
        "dealname": "Acme Corp Series A",
        "amount": "5000000",
        "closedate": "2026-03-15",
        "dealstage": "qualifiedtobuy",
        "pipeline": "default"
      }
    },
    {
      "id": "12346",
      "properties": {
        "dealname": "TechStart Seed Round",
        "amount": "1500000",
        "closedate": "2026-02-28",
        "dealstage": "presentationscheduled",
        "pipeline": "default"
      }
    }
  ],
  "paging": {
    "next": {
      "after": "12347",
      "link": "..."
    }
  }
}
```

### Step 7: Self-Healing (Two Weeks Later)

HubSpot rotates their internal API version. The skill starts getting 404s:

```
[Self-Heal] Health check for hubspot.com:
  ❌ deals-list: 404 Not Found
  ❌ deals-get: 404 Not Found
  ✅ contacts-list: 200 OK
  ✅ pipelines-list: 200 OK
  
  Result: 2/4 endpoints broken. Marking as "degraded".
  
  Action: Scheduling re-capture via Molty's browser...
```

Molty automatically browses HubSpot again, the CDP capture detects the new API paths (`/crm/v4/` instead of `/crm/v3/`), regenerates the skill with version 2, and syncs to the fleet.

```
[Skill Gen] Re-captured hubspot.com
  Version: 1 → 2
  Changed: /crm/v3/ → /crm/v4/ (2 endpoints updated)
  Confidence: 91%
  Syncing to fleet...
```

---

## Appendix A: File-Level Dependency Graph

```
cdp-capture.js ──→ capture.jsonl ──→ noise-filter.py ──→ api-classifier.py
                                                              │
                                                              ├→ auth-extractor.py
                                                              │
                                                              └→ skill-gen.py ──→ SKILL.md
                                                                                   api.sh
                                                                                   endpoints.json
                                                                                   scripts/*.sh
                                                                                   .meta.json
                                                                                   .auth/auth-config.json
```

## Appendix B: Exit Code Convention

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Return data |
| 1 | General error | Log and alert |
| 2 | Auth failure (401/403) | Refresh token or re-auth |
| 3 | Rate limited (429) | Wait and retry |
| 4 | Endpoint gone (404) | Re-capture skill |
| 10 | Domain blocklisted | Use browser only, no capture |

## Appendix C: Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `AGENT_NAME` | All scripts | Name of the current agent (molty, raphael, etc.) |
| `SKILLS_DIR` | skill-router.sh | Override shared skills path (default: `/data/shared/api-skills`) |
| `CAPTURES_DIR` | cdp-capture.js | Override capture storage path |
| `CDP_PORT` | cdp-capture.js | Chrome DevTools port (default: 9222) |
| `SKILL_CONFIDENCE_THRESHOLD` | skill-gen.py | Min confidence to include endpoint (default: 0.6) |
| `MAX_CAPTURE_SIZE_MB` | cdp-capture.js | Max capture file size (default: 50) |
| `HEALTH_CHECK_INTERVAL` | self-heal.sh | Seconds between health checks (default: 21600 = 6h) |

---

*This specification is a living document. Update it as implementation reveals new insights or requirements change.*

*— Molty 🦎, Systems Architect, TMNT Squad*
