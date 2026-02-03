# Agent Skills Format Reference

This is a summary of the [agentskills.io specification](https://agentskills.io/specification).

## Directory Structure

Minimum:
```
skill-name/
  SKILL.md
```

Full:
```
skill-name/
  SKILL.md          # Required
  scripts/          # Executable code
  references/       # Additional docs
  assets/           # Static resources
```

## SKILL.md Format

### Frontmatter (Required)

```yaml
---
name: skill-name
description: What it does and when to use it.
---
```

### Frontmatter (Optional Fields)

```yaml
---
name: skill-name
description: What it does and when to use it.
license: MIT
compatibility: Requires Python 3.10+, ffmpeg
metadata:
  author: your-name
  version: "1.0"
---
```

## Field Constraints

### name
- Required
- 1-64 characters
- Lowercase letters, numbers, hyphens only
- No leading/trailing hyphens
- No consecutive hyphens
- Must match folder name

### description
- Required
- 1-1024 characters
- Should describe what AND when

### license
- Optional
- License name or filename

### compatibility
- Optional
- 1-500 characters
- Environment requirements

### metadata
- Optional
- Arbitrary key-value pairs

## Body Content

No format restrictions. Write what helps agents use the skill.

Recommended sections:
- When to use
- Usage examples
- Inputs and outputs
- Edge cases

## Progressive Disclosure

1. **Frontmatter** (~100 tokens) — loaded for all skills at discovery
2. **SKILL.md body** (<5000 tokens recommended) — loaded when skill activated  
3. **References/scripts** — loaded only when needed

Keep SKILL.md under 500 lines. Move details to references/.

## File References

Use relative paths:
```markdown
See [reference guide](references/REFERENCE.md) for details.
Run: scripts/main.py
```

Keep references one level deep.
