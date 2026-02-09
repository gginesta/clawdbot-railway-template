---
name: notion-enhanced
description: Advanced Notion integration with bi-directional sync, database queries, markdown conversion, and page monitoring. Built for multi-agent fleets on Railway.
version: 1.0.0
author: Molty (TMNT Squad)
credits: Patterns inspired by notion-sync (robansuini) on ClawhHub. Custom-built for TMNT fleet architecture.
---

# Notion Enhanced

Advanced Notion API toolkit for agents. Bi-directional markdown↔Notion sync, database queries with filters, property updates, and page change monitoring.

## Setup

Set `NOTION_API_KEY` as an environment variable:

```bash
# From credentials file
source /data/workspace/credentials/notion.env

# Or set directly
export NOTION_API_KEY="ntn_..."
```

Ensure your Notion integration has access to the target pages/databases (Share → Invite integration).

## Scripts

All scripts use Node.js with zero external dependencies (native `https` module only).

### query-database.js — Query Databases with Filters

```bash
node scripts/query-database.js <database-id> [--filter <json>] [--sort <json>] [--limit N]
```

**Examples:**
```bash
# All items (default limit 10)
node scripts/query-database.js abc123

# Filter by status
node scripts/query-database.js abc123 --filter '{"property":"Status","select":{"equals":"Done"}}'

# Multi-select contains
node scripts/query-database.js abc123 --filter '{"property":"Tags","multi_select":{"contains":"AI"}}'

# Sort by date descending
node scripts/query-database.js abc123 --sort '[{"property":"Date","direction":"descending"}]'

# Combined
node scripts/query-database.js abc123 \
  --filter '{"property":"Status","select":{"equals":"In Progress"}}' \
  --sort '[{"property":"Priority","direction":"ascending"}]' \
  --limit 20
```

**Filter patterns:**
- Select: `{"property":"X","select":{"equals":"Value"}}`
- Multi-select: `{"property":"X","multi_select":{"contains":"Tag"}}`
- Checkbox: `{"property":"X","checkbox":{"equals":true}}`
- Date after: `{"property":"X","date":{"after":"2026-01-01"}}`
- Number: `{"property":"X","number":{"greater_than":100}}`

### md-to-notion.js — Push Markdown → Notion

```bash
node scripts/md-to-notion.js <markdown-file> <parent-page-id> <page-title>
```

Converts markdown to Notion blocks and creates a new page. Supports: headings, bold/italic, links, bullet lists, code blocks, dividers.

- Batches 100 blocks per API call (Notion limit)
- 350ms rate limiting between batches
- Returns page URL and ID

### notion-to-md.js — Pull Notion → Markdown

```bash
node scripts/notion-to-md.js <page-id> [output-file]
```

Fetches a Notion page and converts to markdown. Handles pagination for large pages. If output file specified, writes there; otherwise prints to stdout.

### update-properties.js — Update Page Properties

```bash
node scripts/update-properties.js <page-id> <property-name> <value> [--type TYPE]
```

**Supported types:** `select`, `multi_select`, `checkbox`, `number`, `url`, `email`, `date`, `rich_text`

```bash
# Set status
node scripts/update-properties.js <id> Status "Complete" --type select

# Add tags
node scripts/update-properties.js <id> Tags "AI,Research" --type multi_select

# Toggle checkbox
node scripts/update-properties.js <id> Published true --type checkbox
```

### search-notion.js — Search Workspace

```bash
node scripts/search-notion.js <query> [--filter page|database] [--limit N]
```

### watch-page.js — Monitor for Changes

```bash
node scripts/watch-page.js <page-id> [local-markdown-path]
```

Checks if a Notion page has been edited since last check. Compares with local markdown file if provided. Stores state in `memory/notion-watch-state.json`.

Use in cron jobs or heartbeats to detect when Guillermo edits standup pages.

### add-to-database.js — Add Database Entries

```bash
node scripts/add-to-database.js <database-id> --props '<json>'
```

## TMNT Fleet Usage

### Standup Workflow
```bash
# 1. Create standup page from markdown
node scripts/md-to-notion.js standup-draft.md $STANDUP_DB_ID "Daily Standup — Feb 9"

# 2. Monitor for Guillermo's edits
node scripts/watch-page.js $STANDUP_PAGE_ID

# 3. Pull back edited content
node scripts/notion-to-md.js $STANDUP_PAGE_ID standup-reviewed.md
```

### Content Pipeline (Pikachu)
```bash
# Push draft to Notion Content Hub
node scripts/md-to-notion.js draft.md $CONTENT_HUB_ID "Post Title"

# Query pending drafts
node scripts/query-database.js $CONTENT_HUB_ID \
  --filter '{"property":"Status","select":{"equals":"Draft"}}'
```

## Security

- ✅ All API calls go to `api.notion.com` only
- ✅ Credentials via `NOTION_API_KEY` env var (never hardcoded)
- ✅ Zero external dependencies (Node.js `https` module only)
- ✅ No filesystem access outside specified paths
- ✅ Error handling with clear messages
- ✅ Rate limiting built into batch operations

## Credits

Patterns and structure inspired by [notion-sync](https://clawhub.ai) by robansuini (ClawhHub).
Custom-built for TMNT Squad fleet with Railway-specific adaptations (env var auth, no macOS dependencies).
