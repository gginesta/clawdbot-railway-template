# 🧠 Memory Vault

A durable, structured memory system for capturing and searching personal knowledge — including AI conversation history.

Based on [Nat Eliason's memory architecture](https://x.com/nateliason) and adapted for personal use with Obsidian + qmd.

## Architecture

```
memory-vault/
├── knowledge/          # Layer 1: Knowledge Graph (PARA)
│   ├── projects/       # Active projects with deadlines
│   ├── areas/          # Ongoing responsibilities (health, finance, etc.)
│   ├── resources/      # Reference material (topics, tools, concepts)
│   └── archives/       # Completed or inactive items
├── daily/              # Layer 2: Daily Notes (episodic memory)
│   └── YYYY/MM/        # Organized by year/month
├── tacit/              # Layer 3: Tacit Knowledge
│   └── preferences.md  # User patterns, preferences, quirks
├── ai-history/         # AI Conversation Archives
│   ├── chatgpt/        # ChatGPT exports
│   ├── claude/         # Claude exports
│   └── grok/           # Grok exports
└── templates/          # Reusable templates
```

## The Three Layers

### Layer 1: Knowledge Graph (PARA)

Organized using the PARA method:
- **Projects**: Active work with a deadline or end goal
- **Areas**: Ongoing responsibilities you maintain
- **Resources**: Topics, tools, or reference material
- **Archives**: Completed or inactive items

Each entity has:
- `summary.md` — Human-readable overview
- `items.json` — Atomic facts with metadata

### Layer 2: Daily Notes

Dated markdown files that serve as:
- Timeline of events and activities
- Episodic memory ("what happened when")
- Quick capture for later processing

Format: `daily/YYYY/MM/YYYY-MM-DD.md`

### Layer 3: Tacit Knowledge

A single file (`tacit/preferences.md`) capturing:
- Personal patterns and habits
- Preferences and quirks
- Communication style
- Things AI assistants should know about you

## Atomic Facts Schema

Facts in `items.json` follow this structure:

```json
{
  "id": "fact-uuid",
  "content": "The actual fact or piece of information",
  "source": "Where this came from (URL, conversation, observation)",
  "createdAt": "2026-02-01T12:00:00Z",
  "lastAccessed": "2026-02-01T12:00:00Z",
  "accessCount": 1,
  "status": "active",
  "tags": ["tag1", "tag2"],
  "supersedes": null,
  "supersededBy": null
}
```

### Status Values
- `active` — Current, valid information
- `superseded` — Replaced by newer information (never delete!)

### Memory Decay Tiers
- **Hot**: Accessed in last 7 days
- **Warm**: Accessed in last 30 days
- **Cold**: Older than 30 days (candidates for archival)

## Usage with Obsidian

1. Clone this repo to your machine
2. Open the folder as an Obsidian vault
3. Use daily notes plugin for Layer 2
4. Link between notes using `[[wikilinks]]`
5. Commit and push when you want to backup

### Recommended Obsidian Plugins
- **Daily Notes** — Auto-create daily note files
- **Calendar** — Visual calendar for daily notes
- **Dataview** — Query your notes like a database
- **Git** — Auto-commit and sync

## Usage with qmd (AI Search)

[qmd](https://github.com/tobi/qmd) provides hybrid search (BM25 + vector):

```bash
# Install qmd (requires Bun)
bun install -g qmd

# Index your vault
qmd index /path/to/memory-vault

# Search
qmd search "what did I learn about X?"
```

## Importing AI History

### ChatGPT
1. Go to Settings → Data Controls → Export Data
2. Download and extract the ZIP
3. Copy `conversations.json` to `ai-history/chatgpt/`
4. Run the processing script (see `templates/import-chatgpt.md`)

### Claude
1. Go to Settings → Export Conversations
2. Download the export
3. Copy to `ai-history/claude/`

### Grok
1. Export from X/Grok settings
2. Copy to `ai-history/grok/`

## Key Principles

1. **Never delete, only supersede** — Old information might be useful for "what did I believe at time X?"
2. **Atomic facts** — One fact per entry, easy to update or supersede
3. **Source everything** — Always note where information came from
4. **Access tracking** — Know what you actually use vs. what sits cold

## Quick Start

1. Start with `tacit/preferences.md` — teach the system about yourself
2. Create your first daily note in `daily/YYYY/MM/`
3. Add a project or area to `knowledge/`
4. Export and import your AI history
5. Search with qmd or Obsidian

---

*Built for humans who want AI to actually remember them.*
