# Making Skills Discoverable

Skills can live anywhere. Here's how to make them findable.

## GitHub (Recommended)

### Single-Skill Repo

```
my-skill/          <- repo name
  SKILL.md
  scripts/
    main.py
```

Add topic: `agentskills`

Found via: GitHub topic search

### Monorepo

```
my-tools/          <- repo name
  audio/
    silence-detect/
      SKILL.md
      scripts/
    normalize/
      SKILL.md
      scripts/
  image/
    resize/
      SKILL.md
```

Add topic: `agentskills`

Found via: GitHub code search (finds SKILL.md files inside)

### Gist

Single SKILL.md file with embedded code or file links:

```markdown
---
name: quick-skill
description: Does a thing.
metadata:
  files:
    - https://gist.githubusercontent.com/.../main.py
---

# Quick Skill

Instructions...
```

Found via: GitHub gist search

## Local

Keep skills in a folder:

```
~/skills/
  skill-one/
    SKILL.md
  skill-two/
    SKILL.md
```

Configure find-skill to search `~/skills/`.

Found via: local search only (offline capable)

## Anywhere With a URL

Any raw-fetchable location works:

- Pastebin (dpaste.org, ix.io)
- Raw GitHub URLs
- IPFS gateways
- Self-hosted

For scattered files, use metadata.files:

```yaml
metadata:
  files:
    - https://example.com/main.py
    - https://example.com/utils.py
  hash: abc123  # content hash for verification
```

## Content Hash

If files are co-located (same folder), hash is implicit—computed from contents.

If files are scattered (URLs), include explicit hash in metadata for verification.

Hash format: MD5 or SHA256 of sorted file contents.

## Lineage

If derived from another skill:

```yaml
metadata:
  parent: github.com/user/original-skill
  parent-hash: abc123
```

Optional. Helps track improvements and forks.

## Search Priority

find-skill searches in order:

1. Local paths (fastest, offline)
2. GitHub topic repos
3. GitHub code search

Local matches preferred over remote duplicates.
