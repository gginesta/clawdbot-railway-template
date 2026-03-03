# Whoop Integration — Status Report
**Date:** 2026-03-04  
**Authored by:** Molty 🦎  
**Todoist task:** `6fwM6PjWHXP2wQfR`

---

## Summary
Full research complete. Comprehensive spec exists at `/data/workspace/scripts/WHOOP-INTEGRATION-SPEC.md` (created 2026-02-05). All research questions answered against live API docs. Ready to implement Phase 1 when Guillermo provides credentials.

---

## API Confirmed (March 2026)
- **Auth:** OAuth 2.0 Authorization Code flow — CONFIRMED LIVE
  - Auth URL: `https://api.prod.whoop.com/oauth/oauth2/auth`
  - Token URL: `https://api.prod.whoop.com/oauth/oauth2/token`
  - Scopes: `read:recovery read:cycles read:workout read:sleep read:profile read:body_measurement`
  - **`offline` scope** for refresh tokens — required for unattended operation
- **Rate limits:** 100 req/min, 10,000 req/day — very generous for single-user polling
- **Base path:** `https://api.prod.whoop.com/developer/v1/`
- **Webhooks:** v1 deprecated/removed; v2 webhooks use UUIDs — optional Phase 4 feature

## Data Available
| Metric | Source | Key fields |
|--------|--------|-----------|
| Recovery | `/v2/recovery` | `recovery_score`, `hrv_rmssd_milli`, `resting_heart_rate`, `spo2_percentage` |
| Sleep | `/v2/activity/sleep` | `sleep_performance_percentage`, all stage durations (millis), `respiratory_rate` |
| Strain (cycle) | `/v2/cycle` | `strain`, `kilojoule`, `avg_hr`, `max_hr` |
| Workouts | `/v2/activity/workout` | sport, duration, strain, HR, energy, zone durations |
| Body measurements | `/v2/user/measurement/body` | height, weight, max_hr |

## What Guillermo Needs to Do (Phase 1 Gate)
1. **Create a WHOOP Developer App** at https://developer-dashboard.whoop.com
   - Create team → create app → request scopes: `offline read:recovery read:cycles read:workout read:sleep`
   - Add redirect URI (e.g. `https://molty.railway.app/whoop/callback` or `http://localhost:3000/callback` for local)
2. **Share with Molty:**
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - Confirm REDIRECT_URI
3. **Optional:** 3 preference questions for tailored insights:
   - Primary goal (performance / fat loss / general health / stress)?
   - Training style (lifting / endurance / mixed)?
   - Most important metrics (recovery vs sleep vs strain)?

## Implementation Estimate
- **Phase 1** (OAuth + smoke test): 2-4h
- **Phase 2** (daily fetch + Telegram digest): 4-8h
- **Phase 3** (Morning Briefing integration): 1-2h
- **Phase 4** (weekly trends + alerts + webhooks): ongoing

## Blockers
- 🚧 **Blocked on Guillermo** — needs WHOOP Developer App created + Client ID/Secret shared
- No code can proceed until OAuth credentials are in hand

## Next Steps (Molty)
Once Guillermo provides credentials:
1. Store in `/data/workspace/credentials/whoop.env`
2. Run `whoop.py auth-url` → Guillermo opens URL, authorizes, pastes redirected URL
3. Run `whoop.py exchange-code` → tokens stored in `credentials/whoop-oauth.json`
4. Smoke test: hit profile + latest sleep/recovery
5. Build daily fetch + Telegram digest

---
*Full spec: `/data/workspace/scripts/WHOOP-INTEGRATION-SPEC.md`*
