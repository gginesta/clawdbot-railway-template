# Railway Template Webhook Fix

## Problem
The Railway template's `server.js` applies `express.json()` globally, which consumes POST request bodies before the proxy can forward them. This breaks webhooks.

## The Bug (current code)
```javascript
const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "1mb" }));  // <-- GLOBAL - breaks proxy!
```

## The Fix
Only apply body parsing to `/setup` routes:

```javascript
const app = express();
app.disable("x-powered-by");

// Only parse JSON for /setup routes (not proxied routes)
const setupRouter = express.Router();
setupRouter.use(express.json({ limit: "1mb" }));

// Move all /setup/* routes to use setupRouter
app.use('/setup', setupRouter);

// Proxy handler (no body parsing) - works for webhooks
app.use(async (req, res) => {
  // ... existing proxy code ...
});
```

## Alternative Quick Fix
If restructuring routes is too invasive, add body re-serialization before proxy:

```javascript
app.use(async (req, res) => {
  // ... existing checks ...
  
  // Re-serialize body if it was parsed
  if (req.body && Object.keys(req.body).length > 0) {
    const bodyStr = JSON.stringify(req.body);
    req.headers['content-length'] = Buffer.byteLength(bodyStr);
    // http-proxy will use the original request, so we need to pipe a new body
  }
  
  return proxy.web(req, res, { target: GATEWAY_TARGET });
});
```

## Deployment Steps
1. Fork `gginesta/clawdbot-railway-template` (or original `vignesh07/clawdbot-railway-template`)
2. Apply fix to `src/server.js`
3. Update Railway to deploy from forked repo
4. Redeploy both Molty and Raphael instances

## Time Estimate
- Code fix: 10 minutes
- Test locally: 5 minutes  
- Redeploy: 10 minutes per instance
- **Total: ~35 minutes**
