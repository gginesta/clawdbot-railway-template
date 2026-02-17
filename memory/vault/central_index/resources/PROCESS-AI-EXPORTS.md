# Task: Process AI Conversation Exports for Memory Vault

## Context
I'm building a personal knowledge system called Memory Vault using Obsidian. It uses:
- **PARA method** for organization (Projects, Areas, Resources, Archives)
- **Three-layer architecture**: Knowledge Graph (PARA), Daily Notes, Tacit Knowledge
- **Atomic facts** stored as JSON for structured retrieval

## Your Job
Process my AI conversation exports (ChatGPT, Claude, Grok) and extract valuable knowledge into the Memory Vault format.

## Input Files
Look in the current directory for:
- ChatGPT export: `*.zip` containing `conversations.json`
- Claude export: `*.zip` containing conversation JSON files  
- Grok export: `*.zip` containing conversation data

Extract the zips first if needed.

## What to Extract
For each meaningful conversation, identify:

1. **Decisions made** - Choices, conclusions, "we decided to..."
2. **Lessons learned** - Insights, realizations, "I learned that..."
3. **Useful techniques** - How-tos, workflows, prompts that worked well
4. **Project context** - What projects were discussed, key milestones
5. **Preferences expressed** - My opinions, likes/dislikes, style preferences
6. **People & relationships** - Names mentioned, who does what
7. **Technical knowledge** - Code snippets, configurations, solutions worth keeping
8. **Ideas & plans** - Future intentions, things to try, brainstorms

**Skip:**
- Casual chitchat with no substance
- Failed attempts that led nowhere
- Repetitive troubleshooting that was resolved
- Test messages, typos, corrections

---

## Output Structure

Create files in these locations:

### 1. Processed Summaries (per source)
`ai-history/[source]/processed/summary-YYYY-MM.md`

Use this template:
```md
# [Source] Conversations Summary - [Month Year]

## Overview
[2-3 sentence summary of what this period covered]

## Key Themes
- Theme 1
- Theme 2

## Notable Conversations

### [Topic/Title]
**Date:** YYYY-MM-DD
**Summary:** [2-3 sentences]
**Key Takeaways:**
- Point 1
- Point 2

**Relevant to:** [[Project Name]] or Area/Resource

---
[Repeat for each notable conversation]

## Decisions Made
| Date | Decision | Context | Related To |
|------|----------|---------|------------|
| | | | |

## Lessons Learned
- Lesson 1: [description]
- Lesson 2: [description]
```

### 2. Atomic Facts (JSON)
`ai-history/[source]/processed/items-YYYY-MM.json`

Schema:
```json
{
  "items": [
    {
      "id": "uuid-here",
      "type": "decision|lesson|preference|fact|technique|idea",
      "content": "The actual insight or fact",
      "context": "Where this came from / why it matters",
      "source": "chatgpt|claude|grok",
      "sourceDate": "YYYY-MM-DD",
      "confidence": "high|medium|low",
      "tags": ["tag1", "tag2"],
      "relatedTo": ["project-name", "area-name"],
      "extractedAt": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

### 3. PARA Additions
If you identify content that belongs in the knowledge base:

**Projects** (`knowledge/projects/[name]/`):
- Active work with clear end goals
- Create `summary.md` and `items.json` if new project identified

**Areas** (`knowledge/areas/[name].md`):
- Ongoing responsibilities (health, finances, relationships, skills)
- No end date, just maintained

**Resources** (`knowledge/resources/[name].md`):
- Reference material, guides, collected knowledge on a topic
- Useful for future reference

**Archives** (`knowledge/archives/`):
- Completed projects, outdated info

### 4. Tacit Knowledge
`tacit/preferences.md` - Append any discovered preferences:
```md
## [Category]
- Preference: [what I prefer]
- Evidence: [conversation where this was expressed]
```

`tacit/patterns.md` - Recurring behaviors or approaches:
```md
## [Pattern Name]
- Description: [what I tend to do]
- Examples: [when this showed up]
```

---

## Processing Instructions

1. **Start with ChatGPT** (likely largest, most history)
2. **Then Claude** (recent, probably technical)
3. **Then Grok** (likely smallest)

For each source:
1. Extract and read the conversation data
2. Scan for high-value conversations (skip trivial ones)
3. Extract insights into the formats above
4. Create the output files

## Quality Guidelines

- **Be selective** - Only extract genuinely useful knowledge, not everything
- **Preserve context** - Include enough background to understand later
- **Link relationships** - Note which project/area things relate to
- **Date everything** - Temporal context matters
- **Use my voice** - Summaries should sound like my notes, not formal documentation

---

## My Projects (for PARA categorization)

| Project | Lead | Type | Description |
|---------|------|------|-------------|
| Master/Molty | Molty 🦎 | Meta | AI assistant setup, OpenClaw configuration |
| Personal/April | April 📰 | Personal | Fitness, family, admin, personal research |
| Brinc | Raphael 🔴 | Corporate | Corporate work |
| Cerebro | Leonardo 🔵 | Venture | Venture project |
| Tinker Labs | Donatello 🟣 | Research | Research and incubation |
| Mana Capital | Michelangelo 🟠 | Investment | Investment/PE |

---

## Output Location
Save all outputs to: `./processed-exports/`

Create this folder structure:
```
processed-exports/
├── ai-history/
│   ├── chatgpt/
│   │   └── processed/
│   ├── claude/
│   │   └── processed/
│   └── grok/
│       └── processed/
├── knowledge/
│   ├── projects/
│   ├── areas/
│   └── resources/
└── tacit/
```

I'll review and move files to my Memory Vault after.

---

## Begin
Start by:
1. Listing what export files you find in this directory
2. Checking file sizes to plan approach
3. Processing them one by one
4. Give me a progress update after each source is complete

If any file is very large (>50MB JSON), process it in chunks by date range.
