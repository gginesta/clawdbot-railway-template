#!/usr/bin/env node
/**
 * cdp-capture.js
 *
 * Phase 1 (MVP) CDP Network Capture for Unbrowse DIY.
 *
 * Connects to a running Chromium/Brave remote debugging instance and captures
 * API-like network traffic as JSONL (one request/response pair per line).
 *
 * Requirements implemented:
 * - Connect to CDP via WebSocket (discovers a page target via http://127.0.0.1:<port>/json/list)
 * - Listen for Network.requestWillBeSent, Network.responseReceived, Network.loadingFinished
 * - Capture URL, method, headers, request body, response body, status, timing, initiator
 * - Filter noise (analytics/ads/pixels/CDN/static assets/favicon/service-workers)
 * - Only keep API-like requests (XHR/Fetch w/ JSON responses OR content-type application/json)
 * - Output JSONL to /data/workspace/data/captures/{domain}-{timestamp}.jsonl
 * - Graceful shutdown on Ctrl+C
 * - Uses ws module from /openclaw/node_modules/ws
 */

/* eslint-disable no-console */

const fs = require('fs');
const path = require('path');
const { URL } = require('url');

// ws is available in OpenClaw at /openclaw/node_modules/ws
let WebSocket;
try {
  WebSocket = require('/openclaw/node_modules/ws');
} catch (e) {
  // Fallback in case node resolution already has ws.
  WebSocket = require('ws');
}

function usage(exitCode = 0) {
  const msg = `\
Usage:
  node cdp-capture.js [--port 18800] [--domain example.com] [--output /data/workspace/data/captures/]

Options:
  --port        Remote debugging port (default: 18800)
  --domain      Domain to match a page target (e.g., hubspot.com). Also used for output filename.
  --output      Output directory for captures (default: /data/workspace/data/captures/)
  --ws          (Optional) Explicit WebSocket debugger URL. Skips target discovery.
  --help        Show this help

Notes:
  - Brave must be started with remote debugging enabled, e.g.:
      /usr/bin/brave-browser --remote-debugging-port=18800
  - This script discovers a PAGE target matching --domain via:
      http://127.0.0.1:<port>/json/list
`;
  console.error(msg);
  process.exit(exitCode);
}

function parseArgs(argv) {
  const args = { port: 18800, domain: '', output: '/data/workspace/data/captures/', ws: '' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') usage(0);
    if (a === '--port') { args.port = Number(argv[++i]); continue; }
    if (a === '--domain') { args.domain = String(argv[++i] || ''); continue; }
    if (a === '--output') { args.output = String(argv[++i] || ''); continue; }
    if (a === '--ws') { args.ws = String(argv[++i] || ''); continue; }
    console.error(`Unknown arg: ${a}`);
    usage(2);
  }
  if (!Number.isFinite(args.port) || args.port <= 0) {
    console.error('Invalid --port');
    process.exit(2);
  }
  return args;
}

function nowStamp() {
  // 2026-02-05T14-22-00Z
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function safeJsonParse(s) {
  try { return JSON.parse(s); } catch { return null; }
}

function looksLikeJsonContentType(ct) {
  if (!ct) return false;
  const v = String(ct).toLowerCase();
  return v.includes('application/json') || v.includes('+json') || v.includes('application/graphql-response');
}

function isStaticAsset(urlStr) {
  const lower = String(urlStr).toLowerCase();
  if (lower.startsWith('data:') || lower.startsWith('blob:')) return true;
  const exts = [
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.otf', '.map', '.pdf', '.zip'
  ];
  for (const ext of exts) {
    if (lower.split('?')[0].endsWith(ext)) return true;
  }
  if (lower.includes('/favicon.ico')) return true;
  return false;
}

function isAnalyticsOrAds(urlStr) {
  const lower = String(urlStr).toLowerCase();
  const needles = [
    'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
    'mixpanel.com', 'segment.com', 'api.segment.io', 'cdn.segment.com',
    'hotjar.com', 'intercom.io', 'sentry.io', 'datadoghq.com',
    'newrelic.com', 'facebook.com/tr', 'connect.facebook.net',
    'optimizely.com', 'snap.licdn.com', 'adsystem', '/pixel', 'pixel.'
  ];
  return needles.some(n => lower.includes(n));
}

function isServiceWorkerish(rec) {
  const u = (rec && rec.url) ? rec.url.toLowerCase() : '';
  if (u.includes('service-worker') || u.includes('serviceworker') || u.endsWith('/sw.js')) return true;
  const initiatorType = rec && rec.initiator && rec.initiator.type;
  if (initiatorType && String(initiatorType).toLowerCase().includes('service')) return true;
  return false;
}

function shouldKeep(rec) {
  if (!rec || !rec.url) return false;
  if (rec.method === 'OPTIONS') return false; // preflights are noise for MVP

  if (isStaticAsset(rec.url)) return false;
  if (isAnalyticsOrAds(rec.url)) return false;
  if (isServiceWorkerish(rec)) return false;

  // Keep only API-like traffic:
  //   - XHR/Fetch with JSON responses, OR
  //   - any request with JSON response content-type
  const type = (rec.resourceType || '').toLowerCase();
  const isXhrFetch = (type === 'xhr' || type === 'fetch');

  const ct = (rec.responseHeaders && (rec.responseHeaders['content-type'] || rec.responseHeaders['Content-Type'])) || rec.mimeType;
  const bodyLooksJson = (typeof rec.responseBody === 'string' && safeJsonParse(rec.responseBody) != null);
  const isJson = looksLikeJsonContentType(ct)
    || (rec.mimeType && String(rec.mimeType).toLowerCase().includes('json'))
    || bodyLooksJson;

  if (!isJson) return false;
  // If the response is JSON, we keep it. (XHR/Fetch is preferred, but JSON content-type wins.)
  return true;
}

function headerMap(headers) {
  // CDP sometimes sends headers as object with mixed casing.
  if (!headers || typeof headers !== 'object') return {};
  const out = {};
  for (const [k, v] of Object.entries(headers)) {
    if (v === undefined) continue;
    out[k] = String(v);
  }
  return out;
}

async function fetchJson(url) {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return await res.json();
}

async function discoverWebSocketUrl(port, domain) {
  const listUrl = `http://127.0.0.1:${port}/json/list`;
  let targets;
  try {
    targets = await fetchJson(listUrl);
  } catch (e) {
    throw new Error(`Failed to query ${listUrl}. Is Brave running with --remote-debugging-port=${port}? (${e.message})`);
  }

  if (!Array.isArray(targets) || targets.length === 0) {
    throw new Error(`No CDP targets found at ${listUrl}. Open a tab first.`);
  }

  const domainLower = String(domain || '').toLowerCase();
  const candidates = targets
    .filter(t => t && t.type === 'page' && typeof t.webSocketDebuggerUrl === 'string')
    .filter(t => {
      const u = String(t.url || '').toLowerCase();
      if (!u || u.startsWith('chrome://') || u.startsWith('brave://') || u.startsWith('devtools://')) return false;
      if (!domainLower) return true;
      return u.includes(domainLower);
    });

  const target = candidates[0] || targets.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
  if (!target) {
    throw new Error(`No suitable PAGE target found. Try opening a normal tab or pass --ws explicitly.`);
  }
  return { wsUrl: target.webSocketDebuggerUrl, targetUrl: target.url, targetTitle: target.title };
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
    this.onEvent = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.wsUrl);
      this.ws = ws;

      ws.on('open', () => resolve());
      ws.on('error', (err) => reject(err));
      ws.on('message', (data) => {
        let msg;
        try { msg = JSON.parse(String(data)); } catch { return; }

        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message || 'CDP error'));
          else resolve(msg.result);
          return;
        }

        if (msg.method && this.onEvent) {
          this.onEvent(msg.method, msg.params || {});
        }
      });
      ws.on('close', () => {
        // reject any pending
        for (const { reject } of this.pending.values()) {
          reject(new Error('CDP socket closed'));
        }
        this.pending.clear();
      });
    });
  }

  send(method, params = {}, timeoutMs = 5000) {
    const id = this.nextId++;
    const payload = { id, method, params };

    return new Promise((resolve, reject) => {
      const t = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP timeout for ${method}`));
      }, timeoutMs);

      this.pending.set(id, {
        resolve: (r) => { clearTimeout(t); resolve(r); },
        reject: (e) => { clearTimeout(t); reject(e); }
      });

      try {
        this.ws.send(JSON.stringify(payload));
      } catch (e) {
        clearTimeout(t);
        this.pending.delete(id);
        reject(e);
      }
    });
  }

  close() {
    try { this.ws && this.ws.close(); } catch {}
  }
}

async function main() {
  const args = parseArgs(process.argv);
  ensureDir(args.output);

  const stamp = nowStamp();
  const safeDomain = (args.domain || 'capture').replace(/[^a-zA-Z0-9.-]+/g, '_');
  const outFile = path.join(args.output, `${safeDomain}-${stamp}.jsonl`);

  let wsInfo;
  if (args.ws) {
    wsInfo = { wsUrl: args.ws, targetUrl: '(explicit)', targetTitle: '(explicit)' };
  } else {
    wsInfo = await discoverWebSocketUrl(args.port, args.domain);
  }

  const out = fs.createWriteStream(outFile, { flags: 'a' });
  let written = 0;
  const inflight = new Map(); // requestId -> record

  const cdp = new CdpClient(wsInfo.wsUrl);
  await cdp.connect();

  // Enable network
  await cdp.send('Network.enable', {});
  // Some sites rely on extra info; harmless if unsupported.
  try { await cdp.send('Network.setCacheDisabled', { cacheDisabled: true }); } catch {}

  let shuttingDown = false;
  function shutdown(reason) {
    if (shuttingDown) return;
    shuttingDown = true;
    console.error(`\n[cdp-capture] Shutting down (${reason}). Wrote ${written} records to ${outFile}`);
    try { cdp.close(); } catch {}
    try { out.end(); } catch {}
    setTimeout(() => process.exit(0), 200);
  }
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));

  cdp.onEvent = async (method, params) => {
    try {
      if (method === 'Network.requestWillBeSent') {
        const { requestId, request, initiator, type, documentURL, wallTime, timestamp } = params;
        if (!requestId || !request) return;

        const rec = inflight.get(requestId) || {};
        rec.requestId = requestId;
        rec.url = request.url;
        rec.method = request.method;
        rec.requestHeaders = headerMap(request.headers);
        if (request.postData) rec.requestBody = request.postData;
        rec.initiator = initiator || null;
        rec.resourceType = type || null;
        rec.documentURL = documentURL || null;
        rec.wallTime = wallTime || null;
        rec.startTimestamp = timestamp || null;
        inflight.set(requestId, rec);
      }

      if (method === 'Network.responseReceived') {
        const { requestId, response, timestamp, type } = params;
        if (!requestId || !response) return;
        const rec = inflight.get(requestId) || { requestId };

        rec.responseUrl = response.url;
        rec.status = response.status;
        rec.statusText = response.statusText;
        rec.responseHeaders = headerMap(response.headers);
        rec.mimeType = response.mimeType;
        rec.responseRemoteIPAddress = response.remoteIPAddress || null;
        rec.responseRemotePort = response.remotePort || null;
        rec.protocol = response.protocol || null;
        rec.responseTimestamp = timestamp || null;
        rec.responseTiming = response.timing || null;
        rec.resourceType = rec.resourceType || type || null;
        inflight.set(requestId, rec);
      }

      if (method === 'Network.loadingFinished') {
        const { requestId, encodedDataLength, timestamp } = params;
        if (!requestId) return;
        const rec = inflight.get(requestId);
        if (!rec) return;

        rec.encodedDataLength = encodedDataLength;
        rec.endTimestamp = timestamp || null;

        // Request body (best-effort)
        if (rec.requestBody == null && rec.method && rec.method !== 'GET' && rec.method !== 'HEAD') {
          try {
            const r = await cdp.send('Network.getRequestPostData', { requestId }, 1500);
            if (r && typeof r.postData === 'string') rec.requestBody = r.postData;
          } catch {}
        }

        // Response body (best-effort)
        try {
          const bodyRes = await cdp.send('Network.getResponseBody', { requestId }, 5000);
          if (bodyRes && typeof bodyRes.body === 'string') {
            let bodyText = bodyRes.body;
            if (bodyRes.base64Encoded) {
              try { bodyText = Buffer.from(bodyRes.body, 'base64').toString('utf8'); } catch {}
            }

            // Guardrail: avoid gigantic blobs (still keep something).
            const max = 2 * 1024 * 1024; // 2MB
            if (bodyText.length > max) {
              rec.responseBody = bodyText.slice(0, max);
              rec.responseBodyTruncated = true;
              rec.responseBodyBytes = bodyText.length;
            } else {
              rec.responseBody = bodyText;
              rec.responseBodyTruncated = false;
              rec.responseBodyBytes = bodyText.length;
            }

            // Convenience flags
            const ct = (rec.responseHeaders && (rec.responseHeaders['content-type'] || rec.responseHeaders['Content-Type'])) || rec.mimeType;
            rec.responseIsJson = looksLikeJsonContentType(ct) || (safeJsonParse(bodyText) != null);
          }
        } catch {
          // Some responses cannot be retrieved (e.g., redirects, opaque, cached).
        }

        // Apply filters and write
        if (shouldKeep(rec)) {
          const lineObj = {
            version: 1,
            capturedAt: new Date().toISOString(),
            target: {
              wsUrl: wsInfo.wsUrl,
              pageUrl: wsInfo.targetUrl,
              pageTitle: wsInfo.targetTitle
            },
            request: {
              id: rec.requestId,
              url: rec.url,
              method: rec.method,
              headers: rec.requestHeaders,
              body: rec.requestBody ?? null,
              documentURL: rec.documentURL,
              initiator: rec.initiator,
              resourceType: rec.resourceType
            },
            response: {
              url: rec.responseUrl || null,
              status: rec.status ?? null,
              statusText: rec.statusText ?? null,
              headers: rec.responseHeaders || {},
              mimeType: rec.mimeType || null,
              protocol: rec.protocol || null,
              remoteIPAddress: rec.responseRemoteIPAddress || null,
              remotePort: rec.responseRemotePort || null,
              body: rec.responseBody ?? null,
              bodyTruncated: !!rec.responseBodyTruncated,
              bodyBytes: rec.responseBodyBytes ?? null,
              isJson: !!rec.responseIsJson
            },
            timing: {
              wallTime: rec.wallTime ?? null,
              startTimestamp: rec.startTimestamp ?? null,
              responseTimestamp: rec.responseTimestamp ?? null,
              endTimestamp: rec.endTimestamp ?? null,
              responseTiming: rec.responseTiming ?? null,
              encodedDataLength: rec.encodedDataLength ?? null
            }
          };
          out.write(JSON.stringify(lineObj) + '\n');
          written++;
        }

        inflight.delete(requestId);
      }
    } catch (e) {
      // Don't crash the capture session because of one bad event.
      console.error(`[cdp-capture] Event handler error: ${e.message}`);
    }
  };

  console.error(`[cdp-capture] Connected to: ${wsInfo.wsUrl}`);
  console.error(`[cdp-capture] Target page: ${wsInfo.targetTitle} :: ${wsInfo.targetUrl}`);
  console.error(`[cdp-capture] Writing JSONL to: ${outFile}`);
  console.error('[cdp-capture] Browse normally; API-like XHR/Fetch JSON responses will be recorded. Ctrl+C to stop.');

  // Keep process alive
  setInterval(() => {}, 1000);
}

main().catch((e) => {
  console.error(`[cdp-capture] Fatal: ${e.message}`);
  process.exit(1);
});
