# AI Conversation History

This folder stores exported conversations from AI assistants for search and reference.

## Folder Structure

```
ai-history/
├── chatgpt/           # ChatGPT exports
│   ├── raw/           # Original export files
│   └── processed/     # Cleaned/indexed versions
├── claude/            # Claude exports
│   ├── raw/
│   └── processed/
└── grok/              # Grok exports
    ├── raw/
    └── processed/
```

## Export Instructions

### ChatGPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile → Settings
3. Data Controls → Export Data
4. Wait for email, download ZIP
5. Extract `conversations.json` to `chatgpt/raw/`

### Claude

1. Go to [claude.ai](https://claude.ai)
2. Click your profile → Settings
3. Account → Export Data
4. Download and extract to `claude/raw/`

### Grok

1. Go to X.com
2. Access Grok settings
3. Export conversation history
4. Save to `grok/raw/`

## Processing

After exporting, run the processing scripts to:
1. Convert to searchable markdown
2. Extract key facts
3. Build search index

See `/templates/import-*.md` for processing guides.

## Privacy Note

These files contain your personal conversations. 
- Keep this repo **private**
- Don't commit API keys or passwords mentioned in chats
- Consider sanitizing sensitive info before indexing
