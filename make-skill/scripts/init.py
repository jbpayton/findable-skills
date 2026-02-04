#!/usr/bin/env python3
"""
Initialize a skills monorepo on GitHub.

Usage:
    python init.py my-skills
    python init.py my-skills --public
    python init.py my-skills --description "My collection of Agent Skills"

Requires: gh CLI (https://cli.github.com) authenticated via `gh auth login`
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_gh_cli() -> bool:
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_command(args: list, cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command."""
    result = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{result.stderr}")
    return result


def get_github_username() -> str:
    """Get the authenticated GitHub username."""
    result = run_command(["gh", "api", "user", "--jq", ".login"])
    return result.stdout.strip()


def init_skills_repo(name: str, output_dir: Path, public: bool = False, description: str = None) -> tuple[Path, str]:
    """Initialize a new skills monorepo."""
    repo_dir = output_dir / name

    if repo_dir.exists():
        raise FileExistsError(f"Directory already exists: {repo_dir}")

    # Create directory
    repo_dir.mkdir(parents=True)

    # Create README
    desc = description or "A collection of Agent Skills"
    readme_content = f"""# {name}

{desc}

## Skills

Skills in this repository:

<!-- Add your skills here as you create them -->

## Usage

Find skills:
```bash
python find-skill/scripts/find.py "your query"
```

## About

This is a skills monorepo using the [agentskills.io](https://agentskills.io) specification.
"""
    (repo_dir / "README.md").write_text(readme_content)

    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
    (repo_dir / ".gitignore").write_text(gitignore_content)

    # Initialize git
    run_command(["git", "init"], cwd=repo_dir)
    run_command(["git", "add", "."], cwd=repo_dir)
    run_command(["git", "commit", "-m", "Initialize skills repository"], cwd=repo_dir)

    # Create GitHub repo
    visibility = "--public" if public else "--private"
    create_args = ["gh", "repo", "create", name, visibility, "--source", str(repo_dir), "--push"]
    if description:
        create_args.extend(["--description", description])

    run_command(create_args, cwd=repo_dir)

    # Add agentskills topic
    username = get_github_username()
    run_command(["gh", "repo", "edit", f"{username}/{name}", "--add-topic", "agentskills"])

    return repo_dir, f"https://github.com/{username}/{name}"


def main():
    parser = argparse.ArgumentParser(description="Initialize a skills monorepo")
    parser.add_argument("name", help="Repository name (e.g., 'my-skills')")
    parser.add_argument("--output", "-o", default=".", help="Parent directory (default: current)")
    parser.add_argument("--public", action="store_true", help="Make repo public (default: private)")
    parser.add_argument("--description", "-d", help="Repository description")
    args = parser.parse_args()

    if not check_gh_cli():
        print("Error: gh CLI not found or not authenticated", file=sys.stderr)
        print()
        print("Install gh CLI: https://cli.github.com")
        print("Then run: gh auth login")
        sys.exit(1)

    output_dir = Path(args.output).expanduser().resolve()

    try:
        repo_dir, url = init_skills_repo(
            args.name,
            output_dir,
            args.public,
            args.description
        )
        print(f"Created skills repo: {url}")
        print(f"Local path: {repo_dir}")
        print()
        print("Next steps:")
        print(f"  cd {repo_dir}")
        print(f"  python path/to/make-skill/scripts/create.py my-first-skill")
        print(f"  python path/to/make-skill/scripts/publish.py my-first-skill")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
