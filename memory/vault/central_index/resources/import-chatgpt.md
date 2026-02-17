# Importing ChatGPT History

## Step 1: Export from ChatGPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile picture → **Settings**
3. Go to **Data Controls**
4. Click **Export Data**
5. Wait for email (usually 5-30 minutes)
6. Download the ZIP file

## Step 2: Extract

```bash
cd ai-history/chatgpt/raw/
unzip ~/Downloads/chatgpt-export-*.zip
```

You'll get:
- `conversations.json` — All your chats
- `user.json` — Account info
- `model_comparisons.json` — If you did any A/B tests
- Various other files

## Step 3: Process (Manual)

For now, manual processing:

1. Open `conversations.json` in a text editor or JSON viewer
2. Find conversations worth preserving
3. Create markdown summaries in `processed/`

### Conversation Summary Format

```markdown
# Chat: [Topic]

**Date**: YYYY-MM-DD
**Model**: GPT-4 / GPT-3.5
**ID**: conversation-uuid

## Summary

What this conversation was about.

## Key Takeaways

- Fact 1
- Fact 2

## Notable Exchanges

> **Me**: Question I asked
> **ChatGPT**: Key part of response

## Tags

#topic1 #topic2
```

## Step 4: Process (Automated — Future)

TODO: Create a script that:
1. Parses `conversations.json`
2. Groups by date/topic
3. Extracts key exchanges
4. Generates markdown files
5. Identifies facts for `items.json`

## Tips

- Focus on conversations where you learned something
- Skip small talk and one-off questions
- Look for decisions you made based on AI advice
- Note any incorrect information you later discovered
