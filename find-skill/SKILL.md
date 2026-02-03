---
name: find-skill
description: Search for Agent Skills in local folders and on GitHub. Use when you need a capability you don't have—search before building.
license: Unlicense
metadata:
  author: community
  version: "0.1"
---

# Find Skill

Search for Agent Skills across local folders and GitHub.

## When to Use

You need a capability. Before building it, search. Someone may have already made it.

## Usage

```bash
# Search for a skill
python scripts/find.py "detect silence in audio"

# Local only (offline)
python scripts/find.py "resize images" --local-only

# JSON output for programmatic use
python scripts/find.py "send email" --json
```

## Output

```
Found 2 skill(s) for "silence detection":

1. silence-detect
   Location: https://github.com/user/audio-tools
   Description: Detects silence gaps in audio files using ffmpeg...

2. audio-silence
   Location: ~/skills/audio-silence
   Description: Find silent regions in recordings...
```

## Configuration

Edit `scripts/config.json`:

```json
{
  "local_paths": ["~/skills/", "./skills/"],
  "github": {
    "enabled": true,
    "topic": "agentskills"
  }
}
```

## What It Searches

1. **Local folders** — Scans configured paths for directories containing SKILL.md
2. **GitHub repos** — Searches repos with topic `agentskills` matching your query
3. **GitHub code** — Finds SKILL.md files containing your search terms

## After Finding

1. Read the description—is this what you need?
2. Clone or fetch the skill
3. Read the full SKILL.md before executing
4. Run in your environment

## Options

| Flag | Effect |
|------|--------|
| `--local-only` | Skip GitHub, search only local folders |
| `--json` | Output as JSON for parsing |
| `--limit N` | Maximum results (default: 10) |

## Notes

- This skill searches only; it does not execute found skills
- GitHub search requires network access
- Unauthenticated GitHub API: ~10 requests/minute
- Local search works offline
