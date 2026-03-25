# Fleet Update SOP — OpenClaw Version Updates

*Last updated: molty | 2026-03-25 | Created after botched update where I claimed done but hadn't done it*

---

## When to Use

Every time we update the OpenClaw version across the fleet. No exceptions, no shortcuts.

---

## Prerequisites

- **Railway API token:** `1d318b62-a713-4fd6-80cf-c54c0934f5d8`
- **Template repo:** `gginesta/clawdbot-railway-template`
- **GitHub PAT:** `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`

---

## Step 1: Find the Latest Version

```bash
git ls-remote --tags https://github.com/openclaw/openclaw.git | grep -v '\^{}' | awk '{print $2}' | sed 's|refs/tags/||' | sort -V | tail -5
```

Pick the latest stable (no `-beta`). Write it down: `TARGET=vX.X.X`

---

## Step 2: Verify Current State (DO NOT SKIP)

Check what every agent is **actually running**, not what MEMORY.md says:

```bash
for proj in "3f47a8ad-232e-4074-8a2a-1af45ab3c047:3daf200b-6fdb-4ead-a850-b7d33301f3b0:f55df1f4-35ed-4ae7-9300-ec74ee9035be:Molty" \
  "d1b3e2b7-10f9-444f-829d-e77975554175:fc8720f0-cd59-48b1-93a2-c8b53e7faa90:88c2c024-7471-4483-81f5-786f5c95c49b:Raphael" \
  "56793cec-6283-4af0-ae1f-ac10ec622e58:02713288-b633-4f01-8bfe-e8ef9a739605:ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9:Leonardo" \
  "2501cb81-c58d-495c-9e39-642e30826d07:ea026a0b-79e0-433d-907e-5cc4f75385e2:3393e01a-9fd9-4ca8-976e-b649fc75a947:April"; do
  pid=$(echo $proj | cut -d: -f1)
  sid=$(echo $proj | cut -d: -f2)
  eid=$(echo $proj | cut -d: -f3)
  name=$(echo $proj | cut -d: -f4)
  ref=$(curl -s -X POST https://backboard.railway.app/graphql/v2 \
    -H "Authorization: Bearer 1d318b62-a713-4fd6-80cf-c54c0934f5d8" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"{ variables(projectId: \\\"$pid\\\", serviceId: \\\"$sid\\\", environmentId: \\\"$eid\\\") }\"}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin)['data']['variables']; print(d.get('OPENCLAW_GIT_REF','NOT SET'))" 2>/dev/null)
  echo "$name: $ref"
done
```

**Print the table. Confirm all need updating.**

---

## Step 3: Update Env Vars on All 4 Services

The `OPENCLAW_GIT_REF` env var overrides the Dockerfile ARG. Must update both.

```bash
TARGET="vX.X.X"
for proj in "3f47a8ad-232e-4074-8a2a-1af45ab3c047:3daf200b-6fdb-4ead-a850-b7d33301f3b0:f55df1f4-35ed-4ae7-9300-ec74ee9035be:Molty" \
  "d1b3e2b7-10f9-444f-829d-e77975554175:fc8720f0-cd59-48b1-93a2-c8b53e7faa90:88c2c024-7471-4483-81f5-786f5c95c49b:Raphael" \
  "56793cec-6283-4af0-ae1f-ac10ec622e58:02713288-b633-4f01-8bfe-e8ef9a739605:ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9:Leonardo" \
  "2501cb81-c58d-495c-9e39-642e30826d07:ea026a0b-79e0-433d-907e-5cc4f75385e2:3393e01a-9fd9-4ca8-976e-b649fc75a947:April"; do
  pid=$(echo $proj | cut -d: -f1)
  sid=$(echo $proj | cut -d: -f2)
  eid=$(echo $proj | cut -d: -f3)
  name=$(echo $proj | cut -d: -f4)
  result=$(curl -s -X POST https://backboard.railway.app/graphql/v2 \
    -H "Authorization: Bearer 1d318b62-a713-4fd6-80cf-c54c0934f5d8" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"mutation { variableUpsert(input: { projectId: \\\"$pid\\\", serviceId: \\\"$sid\\\", environmentId: \\\"$eid\\\", name: \\\"OPENCLAW_GIT_REF\\\", value: \\\"$TARGET\\\" }) }\"}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if d.get('data',{}).get('variableUpsert') else '❌ '+str(d))" 2>/dev/null)
  echo "$name: $result"
done
```

**All 4 must show ✅. If any fails, stop and debug.**

---

## Step 4: Update Dockerfile Default & Push

```bash
cd /tmp && rm -rf clawdbot-railway-template
git clone https://gginesta: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@github.com/gginesta/clawdbot-railway-template.git
cd clawdbot-railway-template
sed -i "s/OPENCLAW_GIT_REF=v[0-9a-z.\-]*/OPENCLAW_GIT_REF=$TARGET/" Dockerfile
grep "OPENCLAW_GIT_REF" Dockerfile  # VERIFY before committing
git config user.email "molty@tmnt.ai" && git config user.name "Molty"
git add Dockerfile && git commit -m "chore: update openclaw to $TARGET"
git push origin main
```

This push triggers rebuilds on all 4 Railway services.

---

## Step 5: Wait for Builds & Verify (DO NOT SKIP)

Wait ~5-8 minutes, then check:

```bash
for entry in "3daf200b-6fdb-4ead-a850-b7d33301f3b0:f55df1f4-35ed-4ae7-9300-ec74ee9035be:Molty" \
  "fc8720f0-cd59-48b1-93a2-c8b53e7faa90:88c2c024-7471-4483-81f5-786f5c95c49b:Raphael" \
  "02713288-b633-4f01-8bfe-e8ef9a739605:ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9:Leonardo" \
  "ea026a0b-79e0-433d-907e-5cc4f75385e2:3393e01a-9fd9-4ca8-976e-b649fc75a947:April"; do
  sid=$(echo $entry | cut -d: -f1)
  eid=$(echo $entry | cut -d: -f2)
  name=$(echo $entry | cut -d: -f3)
  status=$(curl -s -X POST https://backboard.railway.app/graphql/v2 \
    -H "Authorization: Bearer 1d318b62-a713-4fd6-80cf-c54c0934f5d8" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"{ deployments(first: 1, input: { serviceId: \\\"$sid\\\", environmentId: \\\"$eid\\\" }) { edges { node { status } } } }\"}" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['deployments']['edges'][0]['node']['status'])" 2>/dev/null)
  echo "$name: $status"
done
```

**All 4 must show `SUCCESS`. If any shows `FAILED`, check logs before reporting.**

---

## Step 6: Update MEMORY.md

Only after Step 5 passes. Update the Fleet section:

```
**Version:** vX.X.X (deployed YYYY-MM-DD, all 4 agents ✅)
```

---

## Agent Reference Table

| Agent | Project ID | Service ID | Environment ID |
|-------|-----------|------------|----------------|
| Molty 🦎 | `3f47a8ad-232e-4074-8a2a-1af45ab3c047` | `3daf200b-6fdb-4ead-a850-b7d33301f3b0` | `f55df1f4-35ed-4ae7-9300-ec74ee9035be` |
| Raphael 🔴 | `d1b3e2b7-10f9-444f-829d-e77975554175` | `fc8720f0-cd59-48b1-93a2-c8b53e7faa90` | `88c2c024-7471-4483-81f5-786f5c95c49b` |
| Leonardo 🔵 | `56793cec-6283-4af0-ae1f-ac10ec622e58` | `02713288-b633-4f01-8bfe-e8ef9a739605` | `ffa245c6-0eac-40aa-bcf3-9edd7cdd8de9` |
| April 🌸 | `2501cb81-c58d-495c-9e39-642e30826d07` | `ea026a0b-79e0-433d-907e-5cc4f75385e2` | `3393e01a-9fd9-4ca8-976e-b649fc75a947` |

---

## Rules

1. **Never claim "fleet updated" without running Step 5.** This is how the Mar 25 incident happened.
2. **Env vars override Dockerfile ARG.** Both must be updated.
3. **Verify actual state, not MEMORY.md.** MEMORY.md can be stale.
4. **All 4 or nothing.** Don't leave agents on different versions.
5. **REG-033 applies:** No fleet updates without Guillermo's explicit approval in the same session.
