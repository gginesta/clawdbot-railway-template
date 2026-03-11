# April Deployment Retrospective
<!-- Last updated: molty | 2026-03-11 | Post-deployment audit -->

## Summary

| Metric | Value |
|--------|-------|
| First deploy attempt | 16:02 HKT (08:02 UTC) |
| First SUCCESS status | 22:22 HKT (14:22 UTC) |
| Fully operational | ~22:30 HKT (estimated) |
| **Total elapsed** | **~6.5 hours** |
| Deploy attempts | 10 (8 failed/removed, 1 success, ongoing) |
| Post-deploy issues | 7+ |

## What Should Have Taken 30-60 Minutes

With a proper checklist, April deployment should have been:
- 15 min: Railway service + Discord bot setup
- 10 min: Config from template + secrets
- 10 min: Syncthing to hub (Molty)
- 10 min: Test cross-agent comms
- 5 min: Security audit
- **Total: ~50 minutes**

Instead: **6.5 hours** with ongoing issues.

## Timeline of Issues

### Phase 1: Initial Deployment (16:02 - 17:00 HKT)
| Time | Issue | Root Cause |
|------|-------|------------|
| 16:02 | Deploy FAILED | Unknown (early attempts) |
| 16:02 | Deploy FAILED | Unknown |
| Multiple | REMOVED deployments | Config iterations |

### Phase 2: Getting to SUCCESS (17:00 - 22:22 HKT)
| Time | Issue | Root Cause |
|------|-------|------------|
| ~20:38 | 6 more REMOVED deploys | Config/build issues |
| 22:22 | First SUCCESS | Finally working build |

### Phase 3: Post-Deploy Issues (22:22 - 22:30+ HKT)
| Time | Issue | Root Cause | Fix |
|------|-------|------------|-----|
| 20:30 | Syncthing wrong topology | Added to desktop, not hub | Moved to Molty hub |
| 20:48 | Molty not seeing #april-private | Channel not in Molty config | Added channel config |
| 21:17 | @mentions not routing | allowBots: true (wrong) | Changed to "mentions" |
| 21:56 | Still not replying | SIGUSR1 doesn't reload Discord | Full restart needed |
| 21:59 | Security audit findings | dangerouslyDisableDeviceAuth, perms | Fixed in config |
| 22:18 | April broke her config | allowBots in wrong location | Guillermo fixing |
| 22:20 | Gateway down | Invalid config structure | Manual config fix |

## What We Didn't Have (and needed)

### 1. Config Template
- Should have copied from Molty/Raphael/Leonardo
- April started from scratch → config errors

### 2. Pre-flight Checklist
- No systematic verification before "go live"
- Issues discovered reactively, not proactively

### 3. Syncthing Topology Documentation
- Hub-and-spoke wasn't documented
- Added agent directly to desktop (wrong)

### 4. Discord Config Reference
- `allowBots` placement not documented
- April put it in guild config (invalid)

### 5. Security Baseline
- No pre-deploy security check
- Dangerous flags discovered by April's own audit

### 6. Cross-Agent Comm Test
- No verification that bot-to-bot works
- Discovered broken 2+ hours after deploy

## Lessons Learned → Regressions Added

| REG | Lesson |
|-----|--------|
| REG-027 | `allowBots: "mentions"` not `true` |
| REG-028 | Hub-and-spoke Syncthing (via Molty) |
| REG-029 | Credentials dirs must be 700 |
| REG-030 | Full restart for Discord config changes |
| REG-031 | Document channel ownership |
| REG-032 | allowBots is top-level Discord config |

## Documentation Created

1. `/data/workspace/docs/AGENT-DEPLOYMENT-CHECKLIST.md` — Step-by-step for Donatello/Michelangelo
2. REGRESSIONS.md updated with REG-027 through REG-032
3. This retrospective

## For Donatello & Michelangelo

**Before deploying:**
1. Read `AGENT-DEPLOYMENT-CHECKLIST.md`
2. Copy config from working agent (Molty recommended)
3. Use the checklist — don't improvise
4. Run security audit BEFORE announcing "live"
5. Test cross-agent @mentions BEFORE closing deploy

**Target time: 60 minutes max** (not 6 hours)

## Owner Actions

- [ ] Guillermo: Fix April's config (in progress)
- [ ] Molty: Verify April online after fix
- [ ] Molty: Add "agent preflight" cron before future deploys
- [ ] Molty: Template config file in `/data/workspace/templates/agent-config-template.json`

---

*This deployment was a learning experience. The documentation exists now. Donatello and Michelangelo should take 1 hour, not 6.*
