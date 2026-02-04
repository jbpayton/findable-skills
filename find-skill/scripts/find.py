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
import os
import re
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# Global token cache
_github_token: Optional[str] = None

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

def find_env_file() -> Optional[Path]:
    """Find .env file in standard locations."""
    # Search order (first found wins):
    # 1. Current working directory
    # 2. User's home config (~/.agent-skills/.env)
    # 3. Script's project root (when installed as submodule)
    # 4. Script directory (legacy fallback)
    locations = [
        Path.cwd() / ".env",
        Path.home() / ".agent-skills" / ".env",
        Path(__file__).parent.parent.parent / ".env",
        Path(__file__).parent / ".env",
    ]
    for loc in locations:
        if loc.exists():
            return loc
    return None

def load_env_file() -> dict:
    """Load variables from .env file (simple KEY=VALUE format)."""
    env_path = find_env_file()
    if not env_path:
        return {}

    result = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result

def get_github_token() -> Optional[str]:
    """Get GitHub token from .env file or environment variables."""
    global _github_token
    if _github_token is not None:
        return _github_token if _github_token else None

    # Check .env file first
    env_vars = load_env_file()
    token = env_vars.get("GITHUB_TOKEN") or env_vars.get("GH_TOKEN")

    # Fall back to environment variables
    if not token:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    _github_token = token or ""
    return token

def get_github_headers() -> dict:
    """Build headers for GitHub API requests, including auth if available."""
    headers = {
        "User-Agent": "find-skill",
        "Accept": "application/vnd.github.v3+json"
    }
    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

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

def search_configured_repos(query: str, repos: list[str]) -> list[SkillResult]:
    """Search specific configured GitHub repos for skills."""
    results = []
    query_lower = query.lower()

    for repo_name in repos:
        try:
            # Get repo contents (top level)
            url = f"https://api.github.com/repos/{repo_name}/contents"
            req = urllib.request.Request(url, headers=get_github_headers())
            with urllib.request.urlopen(req, timeout=10) as resp:
                contents = json.loads(resp.read().decode())

            # Look for skill directories (dirs containing SKILL.md)
            for item in contents:
                if item.get("type") != "dir":
                    continue

                dir_name = item.get("name", "")
                if dir_name.startswith("."):
                    continue

                # Check if this directory has a SKILL.md
                skill_url = f"https://raw.githubusercontent.com/{repo_name}/HEAD/{dir_name}/SKILL.md"
                content = fetch_url_content(skill_url)
                if not content:
                    continue

                meta = parse_frontmatter(content)
                if not meta:
                    continue

                # Match against query
                searchable = f"{meta.get('name', '')} {meta.get('description', '')}".lower()
                if query_lower in searchable:
                    results.append(SkillResult(
                        name=meta.get("name", dir_name),
                        description=meta.get("description", "")[:300],
                        location=f"https://github.com/{repo_name}/tree/HEAD/{dir_name}",
                        source="github-configured"
                    ))
        except Exception as e:
            print(f"[warn] Failed to search {repo_name}: {e}", file=sys.stderr)

    return results

def search_github_repos(query: str, topic: str) -> list[SkillResult]:
    """Search GitHub repos with agentskills topic."""
    results = []
    try:
        q = urllib.parse.quote(f"{query} topic:{topic}")
        url = f"https://api.github.com/search/repositories?q={q}&per_page=10"
        req = urllib.request.Request(url, headers=get_github_headers())
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
        req = urllib.request.Request(url, headers=get_github_headers())
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

def convert_to_raw_url(github_url: str) -> Optional[str]:
    """Convert GitHub URL to raw content URL for SKILL.md."""
    # Pattern 1: https://github.com/user/repo (repo root)
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/?$", github_url)
    if match:
        user, repo = match.groups()
        return f"https://raw.githubusercontent.com/{user}/{repo}/main/SKILL.md"

    # Pattern 2: https://github.com/user/repo/blob/branch/path/SKILL.md
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", github_url)
    if match:
        user, repo, branch, path = match.groups()
        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"

    return None

def fetch_url_content(url: str) -> Optional[str]:
    """Fetch content from a URL."""
    try:
        req = urllib.request.Request(url, headers=get_github_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        return None

def fetch_skill_content(location: str, source: str) -> Optional[str]:
    """Fetch SKILL.md content from a skill location."""
    if source == "local":
        skill_path = Path(location) / "SKILL.md"
        if skill_path.exists():
            return skill_path.read_text()
        return None

    if source == "github":
        raw_url = convert_to_raw_url(location)
        if raw_url:
            content = fetch_url_content(raw_url)
            if content:
                return content
            # Try master branch if main fails
            if "/main/" in raw_url:
                content = fetch_url_content(raw_url.replace("/main/", "/master/"))
                if content:
                    return content
    return None

def main():
    parser = argparse.ArgumentParser(description="Find Agent Skills")
    parser.add_argument("query", help="What capability do you need?")
    parser.add_argument("--local-only", action="store_true", help="Search only local folders")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fetch", action="store_true", help="Fetch and display SKILL.md content")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results (default: 10)")
    args = parser.parse_args()
    
    config = load_config()
    results = []
    
    results.extend(search_local(args.query, config.get("local_paths", [])))
    
    if not args.local_only and config.get("github", {}).get("enabled", True):
        github_config = config.get("github", {})

        # Search configured repos first (most relevant)
        configured_repos = github_config.get("repos", [])
        if configured_repos:
            results.extend(search_configured_repos(args.query, configured_repos))

        # Then search by topic
        topic = github_config.get("topic", "agentskills")
        results.extend(search_github_repos(args.query, topic))

        # Finally, code search as fallback
        results.extend(search_github_code(args.query))
    
    results = dedupe(results)[:args.limit]
    
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif not results:
        print(f"No skills found for: {args.query}")
        print("Try broader terms, or create the skill yourself.")
    elif args.fetch:
        for i, r in enumerate(results, 1):
            print("=" * 60)
            print(f"[{i}] {r.name} ({r.source})")
            print(f"Location: {r.location}")
            print("=" * 60)
            content = fetch_skill_content(r.location, r.source)
            if content:
                print(content)
            else:
                print("[Could not fetch SKILL.md content]")
            print()
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
