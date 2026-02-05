# WHOOP Health Data Integration Spec (OpenClaw / Molty)

**Owner (foundation):** Molty 🦎  
**Future owner:** April 📰 (planned)  
**User:** Guillermo (Hong Kong, **HKT UTC+8**)  
**Primary delivery:** Telegram + Morning Briefing at **07:30 HKT**  
**Doc updated:** 2026-02-05

---

## 0) Goals & non-goals

### Goals
- Pull Guillermo’s WHOOP daily metrics (Sleep / Recovery / Strain / Workouts) reliably via the **official WHOOP Developer API**.
- Generate:
  - **Daily health digest** (Telegram)
  - **Compact Morning Briefing section** (07:30 HKT)
  - **Weekly trend summary** (Sunday)
  - **Alerts** for key thresholds (recovery, sleep, HRV)
- Build a maintainable skill + script foundation usable by future agents (April).

### Non-goals (initial scope)
- Real-time streaming metrics (WHOOP official API does **not** expose continuous HR time-series data).
- Fully public multi-user app distribution (app approval + scaling concerns are Phase 4+).

---

## 1) Part 1 — WHOOP API research (official + community)

### 1.1 Official WHOOP Developer Platform
**Docs:** https://developer.whoop.com/  
**API reference:** https://developer.whoop.com/api/

#### Access requirements
- You must have an active WHOOP membership to develop on the platform. WHOOP explicitly states there is **no sandbox**.
- You create an “App” in the **WHOOP Developer Dashboard**: https://developer-dashboard.whoop.com/
  - Requires creating a **Team** first.
  - You can create up to **5 apps** per account (can request more via WHOOP support/typeform).

#### Dev vs Launch
- Apps can be used immediately for development with a limit of **10 WHOOP members**.
- To launch to all WHOOP members, you must submit the app for approval.
  - Source: https://developer.whoop.com/docs/developing/app-approval/

### 1.2 Authentication
WHOOP uses **OAuth 2.0 Authorization Code** flow.

- Authorization URL: `https://api.prod.whoop.com/oauth/oauth2/auth`
- Token URL (exchange code + refresh): `https://api.prod.whoop.com/oauth/oauth2/token`
- Tokens are short-lived; `expires_in` is returned.
- Refresh tokens are available when requesting the `offline` scope.

OAuth docs: https://developer.whoop.com/docs/developing/oauth/

**Important operational note (WHOOP guidance):** refresh tokens regularly (WHOOP support FAQ suggests **every hour**).

### 1.3 OAuth scopes (from API docs)
From https://developer.whoop.com/api/ (Authentication → OAuth scopes):
- `read:recovery`
- `read:cycles`
- `read:workout`
- `read:sleep`
- `read:profile`
- `read:body_measurement`

Plus the **`offline`** scope (documented in OAuth guide) to obtain refresh tokens.

**Recommended for this integration:**
- `offline read:recovery read:cycles read:workout read:sleep`
- (Optional) `read:profile read:body_measurement`

### 1.4 Rate limits
WHOOP rate limiting policy (official): https://developer.whoop.com/docs/developing/rate-limiting/
- **100 requests / minute**
- **10,000 requests / day**
- Rate limit headers are returned (e.g. `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).
- HTTP 429 on limit exceeded.

For our use-case (1 user, daily polling) this is extremely generous.

### 1.5 Webhooks (optional but supported)
WHOOP supports webhooks for near-real-time updates:
- Event types: `workout.updated/deleted`, `sleep.updated/deleted`, `recovery.updated/deleted`
- v2 webhooks use UUID identifiers (v1 webhooks are no longer published).
- Signature validation:
  - Headers: `X-WHOOP-Signature`, `X-WHOOP-Signature-Timestamp`
  - Compute: `base64(HMAC_SHA256(timestamp + raw_body, client_secret))`

Docs: https://developer.whoop.com/docs/developing/webhooks/

**Design note:** Webhooks are great for “send alert as soon as sleep is processed”, but they require a public HTTPS endpoint + robust signature validation + retries. For Phase 1–3, scheduled polling is simpler.

### 1.6 Key endpoints & data models (v2)
WHOOP’s core data model centers around a **Physiological Cycle** (not strictly a calendar day).

Primary data objects we care about:
- **Cycle**: strain + energy + avg/max HR over the cycle
- **Sleep**: per sleep (incl. naps) with stage durations and quality metrics
- **Recovery**: recovery score + HRV + RHR + (WHOOP 4.0) SpO2 + skin temp
- **Workout**: workout details with strain, HR stats, energy, time-in-zones

Official data model examples:
- Cycle example: https://developer.whoop.com/docs/developing/user-data/cycle/
- Sleep example: https://developer.whoop.com/docs/developing/user-data/sleep/
- Recovery details: https://developer.whoop.com/docs/developing/user-data/recovery/
- Workout example: https://developer.whoop.com/docs/developing/user-data/workout/

**Fields we will use (high-signal subset):**

**Cycle (score):**
- `strain` (float)
- `kilojoule` (float) → convert to kcal if desired
- `average_heart_rate` (int)
- `max_heart_rate` (int)

**Sleep (score):**
- Stage summary (all millis):
  - `total_in_bed_time_milli`
  - `total_awake_time_milli`
  - `total_light_sleep_time_milli`
  - `total_slow_wave_sleep_time_milli` (deep)
  - `total_rem_sleep_time_milli`
  - `disturbance_count`
- Quality/score:
  - `sleep_performance_percentage` (acts as “sleep score”)
  - `sleep_efficiency_percentage`
  - `sleep_consistency_percentage`
  - `respiratory_rate`

**Recovery (score):**
- `recovery_score` (0–100)
- `hrv_rmssd_milli`
- `resting_heart_rate`
- `spo2_percentage` (WHOOP 4.0)
- `skin_temp_celsius` (WHOOP 4.0)

**Workout (score):**
- `sport_name` (+ `sport_id`)
- `start`, `end`
- `strain`
- `average_heart_rate`, `max_heart_rate`
- `kilojoule` (energy)
- `distance_meter` (if available)
- `zone_durations` (millis in HR zones 0–5)

### 1.7 Official vs unofficial community options

#### Recommended: Official API (OAuth)
- Supported, documented, stable-ish.
- Works without sharing WHOOP email/password with Molty.

#### Unofficial / reverse-engineered APIs (fallback only)
These typically automate login with WHOOP credentials and call private endpoints (e.g. `https://api-7.whoop.com`) and may break, violate ToS, or require handling MFA.

Notable projects:
- **whoopy (PyPI)** — “unofficial Python client for the WHOOP API” (supports OAuth; includes auto token refresh patterns):
  - https://pypi.org/project/whoopy/
- **hedgertronic/whoop** — Python tools (historically used username/password auth):
  - https://github.com/hedgertronic/whoop
- **ianm199/unofficialWhoopAPI** — wrapper around SwaggerHub reverse-engineered API; supports heart-rate by tick but limited to 8-day windows (per README):
  - https://github.com/ianm199/unofficialWhoopAPI/
- **colinmacon/WhoopAPI-Wrapper** — reverse-engineered API wrapper using `api-7.whoop.com`:
  - https://github.com/colinmacon/WhoopAPI-Wrapper

**Policy recommendation:** Use the official API for production. Consider unofficial APIs only if WHOOP blocks access or key metrics are missing.

---

## 2) Part 2 — Integration design

### 2.1 What to fetch daily (and where it comes from)

#### Sleep (last main sleep)
**Endpoint sources:**
- Prefer: get latest sleep(s) in a time window via Sleep collection, then pick latest `nap=false`.
- Or: derive from Cycle via `GET /v2/cycle/{cycleId}/sleep` once cycle is identified.

**Metrics to compute / report:**
- Sleep “score”: `sleep_performance_percentage`
- Total sleep time (TST): `light + slow_wave + rem` (millis)
- In bed: `total_in_bed_time_milli`
- Awake time: `total_awake_time_milli`
- Stage breakdown: deep (slow_wave), REM, light (millis)
- Efficiency: `sleep_efficiency_percentage`
- Disturbances: `disturbance_count`

#### Recovery (for that sleep/cycle)
**Endpoint sources:**
- `GET /v2/recovery` (collection) filtered by time window
- Or: `GET /v2/recovery/{cycleId}` ("getRecoveryForCycle") once cycle is known

**Metrics:**
- Recovery score: `recovery_score`
- HRV: `hrv_rmssd_milli` (rmssd)
- Resting heart rate: `resting_heart_rate`
- SpO2: `spo2_percentage`

#### Strain (day/cycle)
**Endpoint:** `GET /v2/cycle` (collection) + `GET /v2/cycle/{cycleId}`

**Metrics:**
- Daily strain: `cycle.score.strain`
- Energy: `cycle.score.kilojoule` (convert to kcal for display)
- Avg / max HR across the cycle: `average_heart_rate`, `max_heart_rate`

**Note on “active vs resting calories”:** official Cycle data provides `kilojoule` but does not explicitly separate active vs resting in the v2 examples. We will report total energy and optionally estimate splits only if WHOOP exposes additional fields (verify during implementation).

#### Workouts (in the cycle window)
**Endpoint:** `GET /v2/activity/workout` (collection)

**Metrics per workout:**
- Type: `sport_name`
- Duration: `end - start`
- Strain: `score.strain`
- HR: `avg`, `max`
- Energy: `kilojoule` (convert)
- (Optional) HR zone durations from `zone_durations`

### 2.2 Daily timing logic (Cycle vs Calendar Day)
WHOOP data is cycle-based; a “day” often corresponds to the cycle that contains the main sleep.

**Morning Briefing target:** 07:30 HKT.

**Selection algorithm (robust & simple):**
1. Define `briefing_time_local = today 07:30 HKT`.
2. Query sleeps in the window `[briefing_time_local - 36h, briefing_time_local]`.
3. Choose the most recent sleep with `nap=false` and `score_state == "SCORED"`.
4. Use that sleep’s `cycle_id` as the anchor for:
   - Cycle strain/energy
   - Recovery
   - Workouts filtered by `[cycle.start, cycle.end]`

**Edge cases & fallback:**
- If the latest main sleep is still `PENDING_SCORE` at 07:30, fall back to the previous scored sleep, and include a note (“last night’s sleep still processing”).
- If user slept past 07:30, morning briefing will show the previous sleep; optionally send a follow-up digest when sleep is scored (Phase 4 with webhooks).

### 2.3 Internal normalized data model (what Molty stores)
Store one daily snapshot keyed by **local date** (HKT) and referenced WHOOP IDs.

Suggested file per day:
- `data/whoop/daily/YYYY-MM-DD.json`

Schema (example):
```json
{
  "date_local": "2026-02-06",
  "timezone": "Asia/Hong_Kong",
  "cycle": {
    "id": 12345,
    "start": "2026-02-05T18:00:00Z",
    "end": "2026-02-06T10:00:00Z",
    "strain": 12.4,
    "kilojoule": 9800.2,
    "kcal": 2342,
    "avg_hr": 71,
    "max_hr": 156
  },
  "sleep": {
    "id": "...uuid...",
    "start": "...",
    "end": "...",
    "performance_pct": 94,
    "efficiency_pct": 89.2,
    "consistency_pct": 82,
    "respiratory_rate": 15.8,
    "disturbances": 8,
    "tst_min": 454,
    "in_bed_min": 512,
    "awake_min": 58,
    "stages_min": {"deep": 72, "rem": 105, "light": 277}
  },
  "recovery": {
    "score_pct": 82,
    "hrv_rmssd_ms": 68.3,
    "rhr_bpm": 52,
    "spo2_pct": 97.0,
    "skin_temp_c": 33.7
  },
  "workouts": [
    {
      "id": "...uuid...",
      "sport_name": "running",
      "start": "...",
      "end": "...",
      "duration_min": 32,
      "strain": 6.2,
      "avg_hr": 142,
      "max_hr": 171,
      "kilojoule": 1600,
      "kcal": 382
    }
  ]
}
```

### 2.4 Smart insights (templates vs AI)

**Recommendation: hybrid approach**
- Use deterministic computations + templates for:
  - Threshold alerts
  - Deltas vs baseline (7-day avg)
  - “Green/Yellow/Red” labels
- Optionally let the LLM generate a short narrative *only* from computed facts.

This avoids hallucinations and keeps output consistent.

#### Suggested insight rules (v1)
- **Recovery color bands** (WHOOP convention-like):
  - Red: `< 33%`
  - Yellow: `33–66%`
  - Green: `> 66%`
- **Sleep low:** total sleep `< 6h`
- **HRV drop:** today HRV < (7-day average − 1.0σ) OR < 0.8×(7-day avg)
- **Strain suggestion:**
  - Green recovery + sleep >= 7h → “good day for intensity”
  - Red recovery → “prioritize active recovery / low strain”

### 2.5 Delivery formats

#### A) Standalone daily Telegram digest
Structure (human-friendly):
- Date + anchor sleep window
- Recovery (score, HRV, RHR, SpO2)
- Sleep (TST, score, efficiency, stages, disturbances)
- Strain (day strain, energy)
- Workouts list (top 1–3)
- 1–3 bullet insights + recommended training intensity

#### B) Morning Briefing compact section
Max 3–5 lines:
- “WHOOP: Recovery X% (color), Sleep YhZm (score), Strain A.B, Workouts: N”
- One suggestion sentence.

#### C) Weekly trend summary (Sunday)
Compute from stored daily snapshots (preferred) or fetch last 7 days:
- Averages: recovery, HRV, RHR, sleep time, strain
- Best/worst day highlights
- Trend arrows vs previous week
- 1–2 concrete recommendations

#### D) Alerts
Send ASAP when digest is generated (Phase 2), later via webhooks (Phase 4).
- Recovery < 33% (red)
- Sleep < 6h
- HRV significant drop

---

## 3) Part 2 — Skill & code structure

### 3.1 Proposed repo layout
```
skills/
  whoop/
    SKILL.md
scripts/
  whoop.py                 # main CLI wrapper
  whoop_refresh.py         # (optional) standalone refresh job
  whoop_digest.py          # (optional) formatting utilities
credentials/
  whoop-oauth.json         # refresh/access token store (chmod 600)
  whoop.env                # CLIENT_ID/CLIENT_SECRET/REDIRECT_URI (chmod 600)
data/
  whoop/
    daily/
      YYYY-MM-DD.json
```

### 3.2 `credentials/whoop-oauth.json`
Store per-user tokens and expiry:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_at": 1770300000,
  "scope": "offline read:sleep read:recovery read:workout read:cycles",
  "token_type": "bearer"
}
```

### 3.3 Token refresh strategy
WHOOP docs emphasize that:
- Access tokens are short-lived (`expires_in`).
- Refresh token rotation: after refresh, **both** access and refresh tokens update; old refresh token is invalidated.
- Avoid concurrent refresh calls (race condition).

**Implementation rules:**
- Before any API call: if `now > expires_at - 120s`, refresh.
- File lock around refresh (simple `fcntl` lock in Python) to prevent concurrent refresh.
- On HTTP 401: attempt one refresh + retry.

### 3.4 API wrapper approach
Prefer Python for:
- timezones (zoneinfo)
- JSON transformations
- storing snapshots

`scripts/whoop.py` commands:
- `whoop.py auth-url` → prints authorization URL to open
- `whoop.py exchange-code --redirected-url "..."` → extracts `code` and exchanges for tokens
- `whoop.py refresh` → refresh tokens
- `whoop.py fetch-daily --at "2026-02-06T07:30:00+08:00"` → produces normalized daily JSON to stdout + writes snapshot
- `whoop.py format-telegram --date 2026-02-06` → prints message text

---

## 4) Message templates (Telegram + Briefing)

### 4.1 Daily digest (Telegram) — example
```
WHOOP — Thu 2026-02-06 (HKT)

Recovery: 82% (GREEN)
• HRV: 68 ms (RMSSD)
• RHR: 52 bpm | SpO₂: 97%

Sleep: 7h 34m (Score 94%)
• Efficiency: 89% | Disturbances: 8
• Stages: Deep 1:12 • REM 1:45 • Light 4:37

Strain (cycle): 12.4
• Energy: 9,800 kJ (~2,342 kcal)

Workouts: 2
• Strength Trainer — 45m | Strain 8.1 | HR 118/162 | ~430 kcal
• Run — 32m | Strain 6.2 | HR 142/171 | ~382 kcal

Insights
• Recovery is strong → good day for intensity if schedule allows.
• Sleep efficiency is slightly low vs your 7-day avg → consider winding down 20–30m earlier.
```

### 4.2 Morning Briefing section — example
```
WHOOP: Recovery 82% (Green) | Sleep 7h34 (94%) | Strain 12.4 | Workouts 2
Suggestion: Solid readiness — plan a harder session today if you want.
```

### 4.3 Alerts — examples

**Recovery red:**
```
WHOOP ALERT (HKT): Recovery 29% (RED).
Recommendation: keep strain low, prioritize sleep + hydration; consider active recovery only.
```

**Sleep low:**
```
WHOOP ALERT (HKT): Sleep 5h42 (< 6h).
Recommendation: protect bedtime tonight; keep training intensity moderate.
```

**HRV drop:**
```
WHOOP ALERT (HKT): HRV 42 ms (↓ 25% vs 7-day avg).
Recommendation: you may be under-recovered — consider reducing intensity today.
```

### 4.4 Weekly trend summary — example
```
WHOOP — Weekly Summary (Sun)

7-day averages:
• Recovery: 71% (↑6 vs prior week)
• Sleep: 7h02 (↓18m)
• HRV: 61 ms (↓4)
• Strain: 11.3 (↑0.8)

Notes:
• Best recovery day: Wed (86%). Lowest: Sat (34%).
• Sleep is trending slightly down — consider a consistent lights-out window.
```

---

## 5) What Guillermo needs to provide

### Required (official API path)
1. **Create a WHOOP Developer App** (Developer Dashboard)
   - Provide Molty with:
     - `CLIENT_ID`
     - `CLIENT_SECRET`
     - `REDIRECT_URI` (can be a local URI if doing manual copy/paste of redirected URL)
2. Confirm which scopes to request (recommended list in §1.3).
3. Preference questions (to tailor insights):
   - Primary goal: performance / fat loss / general health / stress management?
   - Training style: heavy lifting? endurance? mixed?
   - Which metrics matter most: recovery vs sleep vs strain?

### Not required (and not recommended)
- WHOOP email/password should **not** be required if using the official OAuth flow.

---

## 6) Implementation roadmap (with effort estimates)

### Phase 1 — API access + auth setup (0.5–1.5 days)
- Create WHOOP app in dashboard
- Implement OAuth helper commands:
  - Generate auth URL
  - Exchange code
  - Store tokens safely
  - Refresh flow
- Smoke test: profile + last sleep/recovery

**Risks:** redirect URI handling (manual copy/paste); token rotation concurrency.

### Phase 2 — Daily fetch script + Telegram digest (1–2 days)
- Implement daily fetch + normalization:
  - choose anchor sleep
  - pull cycle, recovery, workouts
  - write `data/whoop/daily/YYYY-MM-DD.json`
- Implement formatting + send via Telegram pipeline
- Add basic alerts (recovery <33, sleep <6h, HRV drop)

### Phase 3 — Morning Briefing integration (0.5–1 day)
- Produce compact briefing snippet
- Ensure briefing uses HKT and stable selection logic
- Add “data not ready” fallbacks

### Phase 4 — Trends + smarter alerts + (optional) webhooks (2–4 days)
- Weekly summary w/ trends vs prior week
- Baseline computations (7/14/30-day)
- More robust HRV anomaly detection
- Optional: webhook endpoint + signature validation + “sleep processed” immediate follow-up

---

## 7) Notes for April (future owner)
- Prefer snapshot-driven analytics to reduce API calls and avoid “cycle vs calendar” confusion.
- Keep insight generation grounded in computed fields; never infer medical advice.
- If adding webhooks: validate signatures and process asynchronously; keep reconciliation polling.

---

## 8) Open questions / validation checklist (do during Phase 1)
- Confirm exact base paths for endpoints in production:
  - Many examples reference `/v2/...` and tutorial references `/developer/v1/...`.
  - Validate with one `curl` request after OAuth.
- Confirm whether Cycle energy (`kilojoule`) represents total day energy and whether any endpoint exposes “active vs resting”.
- Confirm whether Recovery always links to the main sleep via `sleep_id`.

