#!/usr/bin/env python3
"""
Publish a skill to your skills monorepo.

Usage:
    python publish.py ./my-skill
    python publish.py ./my-skill --message "Add image processing skill"

Requires:
- gh CLI (https://cli.github.com) authenticated via `gh auth login`
- Skill must be inside a git repo initialized with init.py

For first-time setup, run: python init.py my-skills --public
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(args: list, cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{result.stderr}")
    return result


def find_git_root(start_path: Path) -> Path | None:
    """Find the git repository root from a starting path."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def get_repo_url(git_root: Path) -> str | None:
    """Get the GitHub URL of the repository."""
    try:
        result = run_command(["git", "remote", "get-url", "origin"], cwd=git_root, check=False)
        if result.returncode == 0:
            url = result.stdout.strip()
            # Convert SSH to HTTPS format for display
            if url.startswith("git@github.com:"):
                url = url.replace("git@github.com:", "https://github.com/")
            if url.endswith(".git"):
                url = url[:-4]
            return url
    except Exception:
        pass
    return None


def has_agentskills_topic(git_root: Path) -> bool:
    """Check if the repo has the agentskills topic."""
    try:
        result = run_command(["gh", "repo", "view", "--json", "repositoryTopics"], cwd=git_root, check=False)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            topics = [t.get("name", "") for t in data.get("repositoryTopics", [])]
            return "agentskills" in topics
    except Exception:
        pass
    return False


def parse_skill_metadata(skill_dir: Path) -> dict:
    """Extract metadata from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    content = skill_md.read_text()
    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    metadata = {}
    for line in content[3:end].strip().split("\n"):
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata


def publish_skill(skill_dir: Path, message: str = None) -> str:
    """Publish a skill by committing and pushing to the monorepo."""
    skill_dir = skill_dir.resolve()

    # Find git root
    git_root = find_git_root(skill_dir)
    if not git_root:
        raise RuntimeError(
            "Not inside a git repository.\n"
            "First initialize a skills repo: python init.py my-skills"
        )

    # Check for agentskills topic
    if not has_agentskills_topic(git_root):
        print("Warning: Repo doesn't have 'agentskills' topic. Adding it now...", file=sys.stderr)
        run_command(["gh", "repo", "edit", "--add-topic", "agentskills"], cwd=git_root, check=False)

    # Get skill metadata
    metadata = parse_skill_metadata(skill_dir)
    skill_name = metadata.get("name") or skill_dir.name

    # Get relative path for commit message
    try:
        rel_path = skill_dir.relative_to(git_root)
    except ValueError:
        rel_path = skill_dir.name

    # Stage the skill directory
    run_command(["git", "add", str(skill_dir)], cwd=git_root)

    # Check if there are changes to commit
    status = run_command(["git", "status", "--porcelain", str(skill_dir)], cwd=git_root)
    if not status.stdout.strip():
        print("No changes to publish.")
        repo_url = get_repo_url(git_root)
        return repo_url or str(git_root)

    # Commit
    commit_msg = message or f"Add skill: {skill_name}"
    run_command(["git", "commit", "-m", commit_msg], cwd=git_root)

    # Push
    run_command(["git", "push"], cwd=git_root)

    repo_url = get_repo_url(git_root)
    return repo_url or str(git_root)


def main():
    parser = argparse.ArgumentParser(description="Publish a skill to your skills monorepo")
    parser.add_argument("skill_dir", help="Path to skill directory")
    parser.add_argument("--message", "-m", help="Custom commit message")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.exists():
        print(f"Error: Directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if not (skill_dir / "SKILL.md").exists():
        print(f"Error: No SKILL.md found in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        url = publish_skill(skill_dir, args.message)
        print(f"Published to: {url}")
        print()
        print("Your skill is now discoverable via find-skill!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
