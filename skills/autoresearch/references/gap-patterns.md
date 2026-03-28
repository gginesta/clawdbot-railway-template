# Common Gap Patterns + Fixes

## Pattern 1: Trigger Miss (description too narrow)

**Symptom**: Test cases using synonyms or slightly different phrasing don't trigger the skill.

**Example**: Skill description says "Use when creating a new skill" but misses "author a skill", "write a skill", "build a skill".

**Fix**: Expand the description with more trigger phrases. Add noun variants, verb synonyms, and common phrasings from real user requests.

```yaml
# Before
description: Use when creating a new skill.

# After
description: Create, build, author, or improve OpenClaw skills. Use when: creating a new skill from scratch, writing a SKILL.md, authoring a skill, building a skill package, or improving an existing skill.
```

---

## Pattern 2: Trigger Over-Fire (description too broad)

**Symptom**: Adversarial test cases (off-topic prompts) incorrectly trigger the skill.

**Example**: A `pdf-editor` skill triggers when user asks about "editing files" (which could be code files).

**Fix**: Add "NOT for" clauses to description. Narrow scope with specific nouns.

```yaml
description: Edit and process PDF documents. NOT for: code files, Word docs, images, or general file editing.
```

---

## Pattern 3: Workflow Gap (missing step)

**Symptom**: Agent follows the skill but gets stuck at a decision point not addressed.

**Example**: `railway-deploy` skill explains how to push code but doesn't address what to do if the build fails.

**Fix**: Add a section for the missing scenario. Keep it concise — pseudocode or a checklist is fine.

```markdown
## If Build Fails

1. Run `railway logs` to get the error
2. Check for missing env vars: `railway variables`
3. If dependency issue: check `package.json` / `requirements.txt`
4. Fix and re-push
```

---

## Pattern 4: Missing Reference

**Symptom**: Agent has to rediscover the same schema/API/format every run, wasting tokens and risking errors.

**Example**: A `notion` skill that doesn't include the block type schema, so agent guesses wrong block types.

**Fix**: Create `references/{topic}.md` with the schema/API docs. Add a pointer from SKILL.md.

```markdown
## API Reference
See `references/block-types.md` for the complete Notion block schema.
```

---

## Pattern 5: Over-Specification (forced approach)

**Symptom**: Skill demands a specific method even when the situation calls for flexibility.

**Example**: `email` skill always mandates Gmail API even when the context clearly involves SMTP or another provider.

**Fix**: Make the approach conditional. Add a "choosing between X and Y" section.

```markdown
## Choosing an Approach

| Situation | Approach |
|-----------|----------|
| Gmail account configured | Use Gmail API via `gog` |
| SMTP credentials available | Use SMTP directly |
| Multiple providers | Check `~/.config/email/` for active config |
```

---

## Pattern 6: Under-Specification on Fragile Steps

**Symptom**: A critical, error-prone step is described vaguely, leading to inconsistent execution.

**Example**: "Update the config file" without specifying which keys, format, or validation step.

**Fix**: Add a concrete example or a script. Don't leave fragile steps to interpretation.

```markdown
## Updating the Config

Edit `/data/workspace/credentials/config.json`:
```json
{
  "key": "value",    // required
  "timeout": 30      // seconds
}
```
Validate: `python3 scripts/validate_config.py`
```

---

## Pattern 7: Context Bloat

**Symptom**: Skill is long but low-density. Conciseness score suffers.

**Common culprits**:
- Long "About" sections explaining concepts Codex already knows
- Repeating the same rule in multiple places
- Step-by-step instructions for trivial operations (e.g., "run `ls` to list files")

**Fix**: Ruthlessly trim. Move detailed docs to `references/`. Delete anything Codex knows from pre-training.

Rule of thumb: if the instruction is in every Python tutorial, delete it.

---

## Quick Fix Matrix

| Gap Type | Where to Fix | Effort |
|----------|-------------|--------|
| Trigger miss | `description:` in frontmatter | Low |
| Trigger over-fire | `description:` — add NOT clauses | Low |
| Workflow gap | SKILL.md body — new section | Medium |
| Missing reference | New `references/{topic}.md` | Medium |
| Over-specification | SKILL.md — add conditional table | Low |
| Under-specification | SKILL.md — add example / script | Medium–High |
| Context bloat | SKILL.md — delete/move to references | Low |
