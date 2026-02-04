#!/usr/bin/env python3
"""
Create a new Agent Skill from template.

Usage:
    python create.py my-skill-name
    python create.py my-skill-name --author "Your Name" --description "What it does"
    python create.py my-skill-name --output ~/my-skills/  # Create inside your skills repo

Workflow:
    1. First time: python init.py my-skills --public
    2. Create skills: python create.py new-skill -o ~/my-skills/
    3. Publish: python publish.py ~/my-skills/new-skill
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


def validate_skill_name(name: str) -> bool:
    """Validate skill name follows agentskills conventions."""
    if not name or len(name) > 64:
        return False
    # Lowercase letters, numbers, hyphens. Must start with letter.
    if not re.match(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$', name):
        return False
    return True


def get_template_path() -> Path:
    """Get path to template directory."""
    return Path(__file__).parent.parent / "references" / "template"


def substitute_placeholders(content: str, replacements: dict) -> str:
    """Replace placeholders in content."""
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    return content


def create_skill(name: str, output_dir: Path, author: str = "", description: str = "") -> Path:
    """Create a new skill from template."""
    template = get_template_path()
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")

    skill_dir = output_dir / name
    if skill_dir.exists():
        raise FileExistsError(f"Directory already exists: {skill_dir}")

    # Copy template
    shutil.copytree(template, skill_dir)

    # Prepare replacements
    title_name = name.replace("-", " ").title()
    replacements = {
        "my-skill": name,
        "My Skill": title_name,
        "[you]": author if author else "[you]",
    }

    if description:
        replacements["[What it does]. Use when [specific situation]. [Key capability or output]."] = description
        replacements["[One sentence summary.]"] = description

    # Process SKILL.md
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text()
    content = substitute_placeholders(content, replacements)
    skill_md.write_text(content)

    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Create a new Agent Skill")
    parser.add_argument("name", help="Skill name (lowercase, hyphens only)")
    parser.add_argument("--output", "-o", default=".", help="Output directory (default: current)")
    parser.add_argument("--author", "-a", default="", help="Author name")
    parser.add_argument("--description", "-d", default="", help="Short description")
    args = parser.parse_args()

    if not validate_skill_name(args.name):
        print(f"Error: Invalid skill name '{args.name}'", file=sys.stderr)
        print("Name must be 1-64 chars, lowercase letters/numbers/hyphens, start with letter")
        sys.exit(1)

    output_dir = Path(args.output).expanduser().resolve()

    try:
        skill_dir = create_skill(args.name, output_dir, args.author, args.description)
        print(f"Created skill: {skill_dir}")
        print()
        print("Next steps:")
        print(f"  1. cd {skill_dir}")
        print("  2. Edit SKILL.md with your instructions")
        print("  3. Add your code to scripts/")
        print(f"  4. Publish: python {Path(__file__).parent}/publish.py {skill_dir}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
