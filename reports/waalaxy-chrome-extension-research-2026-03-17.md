# Research: Waalaxy + Chrome Extension Remote Gateway Access
**Date:** 2026-03-17 | **Author:** Molty 🦎 | **Task:** jn7aww7z6bepw61f0rbyjh343n82a148

## Summary
Two viable approaches for fleet agents (primarily Raphael) to interact with Waalaxy for LinkedIn automation.

## How Waalaxy Works
- **Chrome Extension** (required): Installed on user's Chrome browser. Opens a LinkedIn tab in background to perform actions.
- **Waalaxy Cloud** (mandatory on paid plans): Continues actions even when Chrome is closed / computer off. Actions queue in the cloud.
- **Result**: Once campaigns are configured, Waalaxy Cloud runs them without needing active browser control.

## Approach 1: OpenClaw Chrome Relay (Best for Setup/Monitoring)
**How it works:**
1. Guillermo installs Waalaxy Chrome extension on his browser
2. Installs OpenClaw node host on his PC (`openclaw node run`)
3. When Chrome is open + OpenClaw relay attached (click toolbar icon), Raphael/Molty can control it remotely
4. Agent navigates to Waalaxy (app.waalaxy.com), sets up campaigns, imports prospects

**Limitations:**
- Requires Guillermo's Chrome to be open (not for 3am unattended use)
- Waalaxy itself keeps LinkedIn tab open — needs to be running to trigger new imports
- Good for: setting up sequences, checking campaign stats, importing new prospects

**Ref:** OpenClaw docs — `profile="chrome"` relay mode; node host on macOS/Windows

## Approach 2: Waalaxy Cloud API / Dashboard Automation
**How it works:**
- Waalaxy Cloud handles autonomous sending once campaigns are queued
- Raphael can monitor campaign status via `app.waalaxy.com` dashboard (with Chrome relay)
- For bulk prospect imports: needs LinkedIn session + Waalaxy extension active

## Recommended Setup for Raphael (Sales Lead)
1. **Guillermo**: Install Waalaxy Chrome extension on his PC browser, authenticate with LinkedIn
2. **Guillermo**: Install OpenClaw node host (`openclaw node run`) — connects his PC to our VPS Gateway
3. **Raphael**: Use `browser(profile="chrome")` to access Waalaxy dashboard via the relay
4. **Campaigns**: Set up outreach sequences once → Waalaxy Cloud handles sending unattended

## Blocker
- Needs Guillermo's PC to have OpenClaw node host installed (not yet confirmed)
- Waalaxy subscription required (confirm Raphael has/needs one)
- LinkedIn account for the automation (confirm which account — Guillermo's or a dedicated one)

## Decision Needed from Guillermo
1. Do you have Waalaxy installed? Which LinkedIn account?
2. Are you willing to install OpenClaw node host on your PC?
3. Should this be Raphael's tool (Brinc outreach) or general fleet access?

## Files
- This report: `/data/workspace/reports/waalaxy-chrome-extension-research-2026-03-17.md`
