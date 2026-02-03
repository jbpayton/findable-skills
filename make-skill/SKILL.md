---
name: make-skill
description: Learn how to create an Agent Skill. Use when you have a capability to share or want to package something reusable.
license: Unlicense
metadata:
  author: community
  version: "0.1"
---

# Make Skill

How to create an Agent Skill that other agents (and humans) can discover and use.

## When to Use

- You've built something useful and want to share it
- You want to package a repeatable workflow
- You're teaching an agent how to do something specific

## Quick Start

1. Copy `references/template/` to your new skill folder
2. Edit the SKILL.md frontmatter (name, description)
3. Replace the example script with your code
4. Push to GitHub with topic `agentskills`

Done. Your skill is now discoverable.

## The Format

A skill is a folder:

```
my-skill/
  SKILL.md          # Required: frontmatter + instructions
  scripts/          # Optional: executable code
  references/       # Optional: additional documentation
  assets/           # Optional: templates, data files
```

### SKILL.md Structure

```markdown
---
name: my-skill
description: What it does. When to use it. Be specific.
license: MIT
metadata:
  author: you
  version: "1.0"
  parent: github.com/original/skill  # if derived from another
---

# My Skill

Instructions for the agent...

## Usage

How to run it...

## Examples

Show inputs and outputs...
```

### Required Fields

| Field | Rules |
|-------|-------|
| `name` | Lowercase, hyphens only, matches folder name, max 64 chars |
| `description` | What it does AND when to use it, max 1024 chars |

### Optional Fields

| Field | Purpose |
|-------|---------|
| `license` | How others can use it |
| `metadata` | Arbitrary key-value pairs (author, version, parent) |
| `compatibility` | Environment requirements |

## Writing Good Instructions

The body of SKILL.md is what agents read. Make it clear:

**Do:**
- Start with when to use this skill
- Give concrete usage examples
- Show expected inputs and outputs
- List requirements and dependencies
- Handle edge cases

**Don't:**
- Assume context the agent won't have
- Write walls of text (keep it scannable)
- Bury the important stuff

## Making It Discoverable

### Option A: GitHub Topic

Add topic `agentskills` to your repository. Done.

### Option B: Monorepo

Keep multiple skills in one repo:

```
my-tools/
  skill-one/
    SKILL.md
  skill-two/
    SKILL.md
```

Tag the repo with `agentskills`. The find-skill searches inside.

### Option C: Local Only

Keep it in `~/skills/` or any folder. Configure find-skill to search there.

### Option D: Anywhere With a URL

Gist, pastebin, raw file host. As long as it's fetchable.

## Tracking Lineage

If your skill improves or derives from another:

```yaml
metadata:
  parent: github.com/user/original-skill
  parent-hash: abc123
```

Optional. Honor system. Helps the ecosystem.

## Reference

See `references/format.md` for the full agentskills.io specification.

See `references/template/` for a working example to copy.
