#!/usr/bin/env python3
"""
Search for Agent Skills locally and on GitHub.

Usage:
    python find.py "your search query"
    python find.py "image resize" --local-only
    python find.py "send email" --json
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class SkillResult:
    name: str
    description: str
    location: str
    source: str

def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        "local_paths": ["~/skills/", "./skills/"],
        "github": {"enabled": True, "topic": "agentskills"}
    }

def parse_frontmatter(content: str) -> Optional[dict]:
    """Extract YAML frontmatter from SKILL.md content."""
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    
    result = {}
    for line in content[3:end].strip().split("\n"):
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result if "name" in result else None

def search_local(query: str, paths: list[str]) -> list[SkillResult]:
    """Search local skill folders."""
    results = []
    query_lower = query.lower()
    
    for path_str in paths:
        base = Path(path_str).expanduser()
        if not base.exists():
            continue
        
        # Search immediate children and one level deeper (for monorepos)
        search_dirs = list(base.iterdir())
        for d in list(search_dirs):
            if d.is_dir():
                search_dirs.extend(d.iterdir())
        
        for item in search_dirs:
            if not item.is_dir():
                continue
            skill_md = item / "SKILL.md"
            if not skill_md.exists():
                continue
            
            meta = parse_frontmatter(skill_md.read_text())
            if not meta:
                continue
            
            searchable = f"{meta.get('name', '')} {meta.get('description', '')}".lower()
            if query_lower in searchable:
                results.append(SkillResult(
                    name=meta.get("name", item.name),
                    description=meta.get("description", "")[:300],
                    location=str(item.absolute()),
                    source="local"
                ))
    return results

def search_github_repos(query: str, topic: str) -> list[SkillResult]:
    """Search GitHub repos with agentskills topic."""
    results = []
    try:
        q = urllib.parse.quote(f"{query} topic:{topic}")
        url = f"https://api.github.com/search/repositories?q={q}&per_page=10"
        req = urllib.request.Request(url, headers={
            "User-Agent": "find-skill",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        
        for repo in data.get("items", []):
            results.append(SkillResult(
                name=repo["name"],
                description=(repo.get("description") or "")[:300],
                location=repo["html_url"],
                source="github"
            ))
    except Exception as e:
        print(f"[warn] GitHub repo search failed: {e}", file=sys.stderr)
    return results

def search_github_code(query: str) -> list[SkillResult]:
    """Search for SKILL.md files on GitHub."""
    results = []
    try:
        q = urllib.parse.quote(f"{query} filename:SKILL.md")
        url = f"https://api.github.com/search/code?q={q}&per_page=10"
        req = urllib.request.Request(url, headers={
            "User-Agent": "find-skill",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        
        for item in data.get("items", []):
            repo = item.get("repository", {})
            path = item.get("path", "")
            skill_name = Path(path).parent.name or repo.get("name", "unknown")
            
            results.append(SkillResult(
                name=skill_name,
                description=f"In {repo.get('full_name', 'unknown')}: {path}",
                location=item.get("html_url", repo.get("html_url", "")),
                source="github"
            ))
    except Exception:
        pass  # Code search often requires auth
    return results

def dedupe(results: list[SkillResult]) -> list[SkillResult]:
    seen = {}
    for r in results:
        key = r.name.lower()
        if key not in seen or r.source == "local":
            seen[key] = r
    return list(seen.values())

def main():
    parser = argparse.ArgumentParser(description="Find Agent Skills")
    parser.add_argument("query", help="What capability do you need?")
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    
    config = load_config()
    results = []
    
    results.extend(search_local(args.query, config.get("local_paths", [])))
    
    if not args.local_only and config.get("github", {}).get("enabled", True):
        topic = config.get("github", {}).get("topic", "agentskills")
        results.extend(search_github_repos(args.query, topic))
        results.extend(search_github_code(args.query))
    
    results = dedupe(results)[:args.limit]
    
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif not results:
        print(f"No skills found for: {args.query}")
        print("Try broader terms, or create the skill yourself.")
    else:
        print(f"Found {len(results)} skill(s) for \"{args.query}\":\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r.name}")
            print(f"   Location: {r.location}")
            desc = r.description[:120] + "..." if len(r.description) > 120 else r.description
            print(f"   Description: {desc}")
            print()

if __name__ == "__main__":
    main()
