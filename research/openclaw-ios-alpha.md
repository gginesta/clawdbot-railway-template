# OpenClaw iOS Alpha + Phone Control Plugins — Research Report
*Feb 9, 2026 | Commits: 6aedc54, 730f86d*

## What's New

Two major additions in the latest OpenClaw update:

### 1. iOS Alpha Node App (`6aedc54`)
A native Swift iOS app that turns an iPhone into an OpenClaw "node" — a paired device that the gateway can control remotely.

**Available iOS services (from source):**
| Service | Capability |
|---------|-----------|
| `PhotoLibraryService` | Camera snap, photo access |
| `ScreenController` | Screen recording/capture |
| `CalendarService` | Read/write calendar events |
| `ContactsService` | Read/write contacts |
| `RemindersService` | Read/write reminders |
| `MotionService` | Device motion/accelerometer |
| `DeviceStatusService` | Battery, network status |
| `NetworkStatusService` | WiFi/cellular status |

### 2. Gateway Phone Control Plugin (`730f86d`)
A security layer that controls which phone commands are allowed. Uses an **arm/disarm** model:

**Command groups:**
- `camera` → `camera.snap`, `camera.clip`
- `screen` → `screen.record`
- `writes` → `calendar.add`, `contacts.add`, `reminders.add`
- `all` → all of the above

**Key security feature:** Commands are DENIED by default. You must explicitly "arm" a group with optional auto-expiry (e.g., `arm camera 5m`). This prevents accidental or unauthorized access.

### 3. Device Pairing Plugin (`extensions/device-pair/`)
Handles secure pairing between iOS app and gateway:
- Telegram-based pairing flow: `/pair` → get setup code → paste in iOS app → `/pair approve`
- Setup code = base64 JSON with gateway WebSocket URL + short-lived token
- State stored in `~/.openclaw/devices/` (pending.json, paired.json)

## How to Pair Guillermo's iPhone

1. **Enable the plugins** — add `device-pair` and `phone-control` to OpenClaw config
2. **In Telegram:** Send `/pair` to Molty-bot → receive setup code
3. **On iPhone:** Install OpenClaw iOS app (TestFlight/alpha) → Settings → Gateway → paste setup code
4. **In Telegram:** `/pair approve` to confirm
5. **Arm specific capabilities:** e.g., "arm camera 10m" to enable camera for 10 minutes

## Practical Use Cases

| Use Case | Command | Example |
|----------|---------|---------|
| **Whiteboard capture** | `camera.snap` | "Take a photo of my whiteboard" |
| **Video clip** | `camera.clip` | "Record 30 seconds of what you see" |
| **Screenshot** | `screen.record` | "Screenshot my phone" |
| **Calendar integration** | `calendar.add` | "Add a meeting to my phone calendar" |
| **Contact lookup** | `contacts` | "Find Alfred Cheung's number" |
| **Reminder creation** | `reminders.add` | "Add a reminder on my phone" |
| **Device status** | device status | "What's my phone battery at?" |

## Security Considerations

- ✅ **Arm/disarm model** — commands denied by default, must be explicitly enabled
- ✅ **Auto-expiry** — armed state can auto-expire (e.g., 5m, 1h)
- ✅ **Pairing approval** — requires explicit `/pair approve` from owner
- ✅ **Setup codes expire** — short-lived tokens for pairing
- ⚠️ **Alpha status** — may have bugs, security not fully audited
- ⚠️ **Network exposure** — iPhone must reach Railway gateway (needs public WebSocket URL or Tailscale)

## Production Readiness

**Status: ALPHA — experimental, not production-ready**

- The iOS app is in `apps/ios/` (Swift, native)
- Author: Mariano Belinky (core OpenClaw contributor)
- Has E2E test scripts (`scripts/dev/ios-node-e2e.ts`)
- Has Telegram pairing test (`scripts/dev/test-device-pair-telegram.ts`)
- No App Store release yet — likely TestFlight only

## Action Items for This Week

1. **Check if plugins are auto-enabled** — look for `device-pair` and `phone-control` in our config
2. **Don't deploy yet** — alpha status means wait for at least one more release
3. **Prepare for when it's ready:**
   - Ensure our Railway gateway has a stable WebSocket URL (we have this via the public domain)
   - Ask Guillermo if he wants to try the alpha when available
4. **Monitor the OpenClaw changelog** for iOS app updates moving to beta

## Relevance to TMNT Fleet

Medium-term opportunity. Once stable:
- Guillermo could pair his iPhone → Molty can check his calendar, add reminders, take photos on command
- Could enable "take a photo of this document" workflows
- Calendar integration could replace our current Google Calendar API approach with native phone calendar
- The arm/disarm security model is well-designed and aligns with our safety-first approach
