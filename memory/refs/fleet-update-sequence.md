# Fleet Update Sequence — Standing Rule

*How to roll out OpenClaw updates across the TMNT fleet.*

---

## Sequence

| Step | Agent | When | Verify Before Next |
|------|-------|------|-------------------|
| 1 | **Molty** 🦎 | Immediately (canary) | Gateway up, crons running, Discord responds |
| 2 | **Raphael** 🔴 | After overnight run | Discord responds, Brinc channels work |
| 3 | **Leonardo** 🔵 | After overnight run | Discord responds, Cerebro channels work |
| 4 | **April** 🌸 | Next day if no issues | WhatsApp + Discord work |

---

## Process

### Step 1: Update Molty (Canary)
```bash
# Via Railway API
RAILWAY_TOKEN="..."
PROJECT_ID="3f47a8ad-232e-4074-8a2a-1af45ab3c047"
SERVICE_ID="3daf200b-6fdb-4ead-a850-b7d33301f3b0"
ENV_ID="f55df1f4-35ed-4ae7-9300-ec74ee9035be"

# Update version
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { variableUpsert(input: { projectId: \"'$PROJECT_ID'\", environmentId: \"'$ENV_ID'\", serviceId: \"'$SERVICE_ID'\", name: \"OPENCLAW_GIT_REF\", value: \"vX.Y.Z\" }) }"}'

# Trigger redeploy
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { serviceInstanceRedeploy(serviceId: \"'$SERVICE_ID'\", environmentId: \"'$ENV_ID'\") }"}'
```

### Step 2-3: Update Raphael + Leonardo
Same process, different service IDs:
- **Raphael:** Service `...` in Project `ggv-raphael`
- **Leonardo:** Service `...` in Project `Leonardo`

Wait for overnight run to complete first — check Discord #squad-updates for overnight report.

### Step 4: Update April
Same process. Only after 24h of Molty + Raphael + Leonardo running stable.

---

## Verification Checklist

After each agent update:
- [ ] Railway deployment shows SUCCESS
- [ ] Agent responds in Discord (ping in #command-center)
- [ ] Crons fire (check `/cron list`)
- [ ] No error spam in logs
- [ ] Webchat works (if applicable)

---

## Rollback

If an update breaks an agent:
```bash
# Revert to previous version
variableUpsert(..., value: "vPREVIOUS")
serviceInstanceRedeploy(...)
```

---

*Created: 2026-03-13 by Molty*
