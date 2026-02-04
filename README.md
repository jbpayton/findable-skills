# skillstash

**Agent Skills that teach agents to find and create findable Agent Skills.**

Two skills:

- **find-skill** — search for Agent Skills locally and on GitHub
- **make-skill** — learn how to create Agent Skills

That's it.

---

## Why This Exists

### The Problem (2022-2024)

Agents needed capabilities they didn't have. The solutions were heavy:

**LangChain Tools** required decorators, schemas, framework lock-in:
```python
@tool
def my_tool(input: str) -> str:
    """Description for the LLM."""
    return do_thing(input)
```

**LLM Auto Forge** (and similar projects) tried to let agents create tools dynamically, but had to hack around LangChain's assumptions—tools registered at init, static tool lists, framework ceremony.

**Custom solutions** everywhere. Everyone rebuilding the same plumbing.

### The Insight

An agent doesn't need a framework. It needs:
1. A file that explains what something does
2. Code that does it

That's a skill. The agent reads the explanation, runs the code. No SDK, no registration, no ceremony.

### The Shift (2024-2025)

[Agent Skills](https://agentskills.io) emerged as an open format:

```
my-skill/
  SKILL.md      # Frontmatter + instructions
  scripts/      # Code
```

Adopted by Claude, Copilot, others. The format problem is solved.

But discovery wasn't. How does Agent A find a skill that Agent B made?

### The Solution

Don't build a registry. Don't build a platform. Just:

1. Put skills on GitHub with topic `agentskills`
2. Search GitHub + local folders
3. Done

These two skills do exactly that.

---

## What Happened to the Old Approaches

### LangChain Tool Registration
Still works, still useful for structured integrations. But for "agent needs a capability it doesn't have"? Overkill. A skill is simpler.

### LLM Auto Forge
The vision was right: agents dynamically creating and discovering tools. The implementation was constrained by LangChain's architecture. 

With the skills format, you don't need:
- Custom `ToolRegistry` classes
- `SelfModifiableAgentExecutor` hacks  
- Framework-specific tool wrappers
- Vector stores for tool discovery (agents can just read descriptions)

The agent reads a SKILL.md. That's the interface.

### MCP (Model Context Protocol)
Solves a different problem—structured tool/resource access via servers. Skills are simpler: just files. Both can coexist. Use MCP when you need persistent connections and structured schemas. Use skills when you need "here's how to do X."

---

## How It Works Now

### Making a Skill Discoverable

Option A: Push to GitHub with topic `agentskills`

Option B: Keep it in a local folder

Option C: Put it anywhere with a URL (gist, pastebin, raw file host)

### Finding a Skill

```bash
python find-skill/scripts/find.py "detect silence in audio"
```

Searches your local `~/skills/` folder, then GitHub repos tagged `agentskills`.

Returns names, descriptions, locations. You decide whether to use them.

### Creating a Skill

Read `make-skill/SKILL.md`. It explains the format and walks through creating one.

Or just copy `make-skill/references/template/` and modify.

---

## The Ecosystem

There's no central registry. Skills live:
- In GitHub repos (searchable via topics)
- In local folders (searchable via find-skill)
- In monorepos (find-skill looks inside)
- Anywhere with a URL

Lineage is tracked via `metadata.parent` in the SKILL.md frontmatter—optional, honor system.

Trust is your problem. Sandbox what you don't trust. Read code before running it.

---

## What You Don't Need Anymore

| Old Way | Why It's Unnecessary |
|---------|---------------------|
| Tool decorator schemas | Agent reads SKILL.md |
| Framework-specific wrappers | It's just files |
| Custom tool registries | GitHub topics + local folders |
| Vector stores for tool search | Agent reads descriptions directly |
| Embedding-based discovery | GitHub search + agent judgment |
| Central package manager | Skills live anywhere |

---

## Installation

### Option A: Clone (Standalone Use)

```bash
git clone https://github.com/jbpayton/skillstash
cd skillstash

# Find skills
python find-skill/scripts/find.py "convert pdf to text"
```

### Option B: Submodule (Add to Your Project)

```bash
# Add to your existing project
git submodule add https://github.com/jbpayton/skillstash .skills/skillstash

# Find skills from your project root
python .skills/skillstash/find-skill/scripts/find.py "send email"
```

### Option C: System-Wide Config

For use across multiple projects, create a global config directory:

```bash
mkdir -p ~/.agent-skills
```

Put your `.env` and any shared config there. The scripts search for `.env` in this order:
1. Current working directory
2. `~/.agent-skills/.env`
3. The skillstash project root
4. The script directory

---

## Getting Started

```bash
# Find skills
python find-skill/scripts/find.py "convert pdf to text"

# Make a skill
# Read make-skill/SKILL.md, then copy the template
```

### GitHub Token Setup (Required for Publishing)

To publish skills and make them discoverable, you need a GitHub Personal Access Token:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. Generate new token with the **`repo`** scope
3. Create a `.env` file in the project root:

```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

The `repo` scope allows the scripts to:
- Create your skills monorepo
- Push skill code
- Add the `agentskills` topic (required for discoverability)

### Configure Your Skills Repo

Edit `find-skill/scripts/config.json` to add your personal skills repo:

```json
{
  "local_paths": ["~/skills/"],
  "github": {
    "enabled": true,
    "topic": "agentskills",
    "repos": ["your-username/your-skills-monorepo"]
  }
}
```

This ensures your skills are always found first, even before the topic search indexes them.

---

## Structure

```
skillstash/
  README.md           # You're reading it
  .env                # Your GitHub token (create this, gitignored)
  skills/             # Your local skills (gitignored)

  find-skill/         # Search for skills
    SKILL.md
    scripts/
      find.py
      config.json     # Configure your repos here

  make-skill/         # Create skills
    SKILL.md
    scripts/
      init.py         # Create a skills monorepo
      create.py       # Create a skill from template
      publish.py      # Publish a skill to GitHub
    references/
      format.md       # The agentskills.io format explained
      discovery.md    # How to make skills findable
      template/       # Copy this to start
```

---

## License

Public domain (Unlicense). Copy it, use it, forget where you got it.

---

## The Point

Three years ago, letting agents dynamically find and create tools required hacking frameworks.

Now it's just files. An agent reads instructions and runs code. Discovery is search. Creation is writing a SKILL.md.

These two skills help with that.
