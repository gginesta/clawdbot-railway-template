# @Molton_Sanchez — Account Status

## Current Status: READ-ONLY
- Account created recently, Twitter bot detection blocks posting
- Can read, search, and research via Bird CLI
- Retry posting periodically to check if restriction lifted

## Account Details
- **Handle:** @Molton_Sanchez
- **Display Name:** Molty Moltensson
- **User ID:** 2017943260631588864
- **CLI:** `bird` (npm global)
- **Credentials:** `/data/workspace/credentials/twitter.env`

## Commands
```bash
export AUTH_TOKEN="..." CT0="..."
bird whoami          # Check auth
bird search "query"  # Search
bird read <url>      # Read tweet
bird thread <url>    # Read thread
bird tweet "text"    # Post (when enabled)
bird reply <id> "text"  # Reply (when enabled)
```

## When Posting Enabled
- ALWAYS get Guillermo's approval first
- Draft → Review → Approve → Post
- No exceptions
