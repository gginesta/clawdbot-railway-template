# Fleet Updates — Process Reference
*Last updated: 2026-03-14*

---

## How Railway Deployments Work

**Source repo:** `gginesta/clawdbot-railway-template` (main branch)
**Dockerfile:** Builds OpenClaw from source using `OPENCLAW_GIT_REF`
**Auto-deploy:** Railway watches the repo — any push to main triggers rebuild

All agents (Molty, Raphael, Leonardo, April) use this same template.

---

## To Update OpenClaw Version

### Step 1: Update the source repo

```bash
# Clone the template repo
cd /tmp && rm -rf clawdbot-railway-template
git clone https://gginesta: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@github.com/gginesta/clawdbot-railway-template.git
cd clawdbot-railway-template

# Check current version
grep "OPENCLAW_GIT_REF" Dockerfile

# Update to new version
sed -i 's/OPENCLAW_GIT_REF=v[0-9.]*[0-9]/OPENCLAW_GIT_REF=vX.X.X/g' Dockerfile

# Commit and push
git config user.email "molty@tmnt.ai"
git config user.name "Molty"
git add Dockerfile
git commit -m "chore: update openclaw to vX.X.X"
git push origin main
```

### Step 2: Railway auto-deploys

Railway watches the repo. Push triggers rebuild for **all services using this template**.

Build time: ~5-8 minutes (builds from source).

### Step 3: Verify

```bash
# Check deployment status
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer 1d318b62-a713-4fd6-80cf-c54c0934f5d8" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ service(id: \"SERVICE_ID\") { deployments(first: 1) { edges { node { status createdAt } } } } }"}'

# After deploy, check version
openclaw --version
```

---

## Service IDs

| Agent | Project ID | Service ID |
|-------|------------|------------|
| Molty | 3f47a8ad-232e-4074-8a2a-1af45ab3c047 | 3daf200b-6fdb-4ead-a850-b7d33301f3b0 |
| Raphael | (check Railway) | fc8720f0-cd59-48b1-93a2-c8b53e7faa90 |
| Leonardo | (check Railway) | 02713288-b633-4f01-8bfe-e8ef9a739605 |
| April | 2501cb81-c58d-495c-9e39-642e30826d07 | ea026a0b-79e0-433d-907e-5cc4f75385e2 |

---

## Manual Redeploy (without version change)

If you just need to restart without changing version:

```bash
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer 1d318b62-a713-4fd6-80cf-c54c0934f5d8" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { serviceInstanceRedeploy(serviceId: \"SERVICE_ID\", environmentId: \"ENV_ID\") }"}'
```

---

## Environment IDs

| Agent | Environment ID (production) |
|-------|----------------------------|
| Molty | f55df1f4-35ed-4ae7-9300-ec74ee9035be |
| April | 3393e01a-9fd9-4ca8-976e-b649fc75a947 |

---

## What NOT to do

❌ `openclaw update` — Doesn't work on Railway (git repo is dirty/read-only)
❌ Edit `/data/workspace/Dockerfile` — That's local, not what Railway uses
❌ `gateway update.run` — Same issue, skips due to dirty repo

---

## Checking for Updates

```bash
# Check current vs latest
openclaw update status

# Or fetch from Twitter/GitHub
curl -s "https://api.fxtwitter.com/openclaw/status/TWEET_ID" | python3 -c "..."
```

---

## After Update Checklist

1. ✅ Verify version: `openclaw --version`
2. ✅ Check gateway health: `openclaw gateway status`
3. ✅ Test key features from release notes
4. ✅ Update TOOLS.md if new credentials/config needed
5. ✅ Update other agents if needed (same repo = auto-updated)
