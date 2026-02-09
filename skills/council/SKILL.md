---
name: council
description: Send an idea to the Council for multi-perspective feedback. Spawns sub-agents with expert personas to stress-test ideas, plans, and decisions. Auto-discovers personas from agents/ folder.
version: 1.0.0
author: Molty (TMNT Squad)
credits: Inspired by Council of the Wise (jeffaf) on ClawhHub. Adapted for TMNT squad with custom personas.
---

# Council

Get multi-perspective feedback on ideas from a panel of expert personas. Perfect for stress-testing business plans, architecture decisions, content strategies, or major choices.

## Usage

Triggered by natural language:
- "Send this to the council: [idea/plan]"
- "Council: [topic]"
- "Get the council's feedback on [thing]"
- "Stress-test this idea: [description]"

## How It Works

1. Receive idea/topic from user
2. Auto-discover agent personas from `{skill_folder}/agents/*.md`
3. Send loading message: `🏛️ *The Council convenes...* (2-5 minutes)`
4. Spawn a sub-agent (5-minute timeout) with all personas
5. Return consolidated multi-perspective feedback

## Council Members

Default personas in `agents/` folder:

| Persona | Emoji | Focus |
|---------|-------|-------|
| Strategist | 🎯 | Business strategy, market positioning, competitive advantage |
| Engineer | 🛠️ | Technical feasibility, implementation, scalability |
| Devil's Advocate | 👹 | Challenges assumptions, finds weaknesses, worst-case scenarios |
| Investor | 💰 | ROI, unit economics, risk/reward, financial viability |
| User | 👤 | UX, adoption barriers, end-user perspective |

### Adding Custom Personas

Add any `.md` file to the `agents/` folder:

```bash
# Example: add a legal perspective
cat > agents/Legal.md << 'EOF'
# Legal Advisor ⚖️

You analyze legal implications, regulatory risks, and compliance requirements.
Focus on: IP protection, liability, data privacy, contractual risks.
Challenge: "What could go wrong legally? What regulations apply?"
EOF
```

The council auto-discovers all `.md` files in `agents/`. No config changes needed.

## Sub-Agent Task Template

When spawning the council sub-agent, use this prompt structure:

```
Analyze this from multiple expert perspectives.

**The Idea:**
[user's idea here]

**Personas to embody:**
[list discovered .md files with their content]

**For each perspective:**
1. Key insights (2-3 bullets)
2. Concerns or red flags
3. Specific recommendations

**Format:**
Start with a ⚖️ Synthesis section (TL;DR — combined recommendation + key decisions needed).
Note where personas DISAGREE — that's where the real insight is.
Then individual perspective sections.
Keep each perspective focused and in-character.
```

## Output Format

```markdown
## 🏛️ Council — [Topic]

### ⚖️ Synthesis
[combined recommendation + disagreements + key decisions]

---

### 🎯 Strategist
[market/competitive analysis]

### 🛠️ Engineer  
[technical feasibility + implementation]

### 👹 Devil's Advocate
[challenges + risks + worst-case]

### 💰 Investor
[ROI + financial analysis]

### 👤 User
[UX + adoption + end-user view]
```

## Configuration

- **Timeout:** 5 minutes (sub-agent spawn)
- **Model:** Uses session default (recommend Sonnet+ for quality)
- **Agents:** Auto-discovered from `agents/` folder
- **No external API calls** — runs entirely via local sub-agent spawn

## Security

- ✅ No external API calls or network requests
- ✅ No credentials required
- ✅ All analysis runs locally via sessions_spawn
- ✅ Agent personas are just markdown files (no code execution)
- ✅ Sub-agent inherits session security context
