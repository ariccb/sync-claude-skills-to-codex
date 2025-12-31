#!/usr/bin/env python3
"""List available skills with YAML frontmatter parsing.

Usage:
    list-skills              # Human-readable list from ~/.codex/skills
    list-skills --json       # JSON output
    list-skills /path/to/dir # Custom skills directory

No external dependencies - parses simple YAML frontmatter manually.
"""
# /// script
# requires-python = ">=3.9"
# ///

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md content (no pyyaml needed)."""
    if not content.startswith("---"):
        return {}
    try:
        end = content.index("---", 3)
        frontmatter = content[3:end].strip()

        result = {}
        current_key = None
        current_value = []

        for line in frontmatter.split("\n"):
            # Check for key: value pattern
            match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)$", line)
            if match:
                # Save previous key if exists
                if current_key:
                    result[current_key] = "\n".join(current_value).strip()

                current_key = match.group(1)
                value = match.group(2).strip()

                # Handle quoted strings
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                # Handle multiline indicator
                elif value in (">", "|", ">-", "|-"):
                    value = ""

                current_value = [value] if value else []
            elif current_key and line.startswith("  "):
                # Continuation of multiline value
                current_value.append(line.strip())

        # Save last key
        if current_key:
            result[current_key] = " ".join(current_value).strip()

        return result
    except (ValueError, Exception):
        return {}


def list_skills(skills_dir: Path) -> list[dict]:
    """Walk skills directory and extract metadata."""
    skills = []
    for skill_md in skills_dir.rglob("SKILL.md"):
        try:
            meta = parse_frontmatter(skill_md.read_text())
        except Exception:
            continue

        if meta.get("name"):
            desc = meta.get("description", "")
            if not isinstance(desc, str):
                desc = str(desc)
            skills.append(
                {
                    "name": meta["name"],
                    "description": desc,
                    "allowed_tools": meta.get("allowed-tools", ""),
                    "path": str(skill_md.parent),
                }
            )
    return sorted(skills, key=lambda s: s["name"])


def main():
    # Parse arguments
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = [a for a in sys.argv[1:] if a.startswith("-")]

    # Determine skills directory
    if args:
        skills_path = Path(args[0])
    else:
        skills_path = Path.home() / ".codex" / "skills"

    if not skills_path.exists():
        print(f"Skills directory not found: {skills_path}", file=sys.stderr)
        sys.exit(1)

    skills = list_skills(skills_path)

    if "--json" in flags:
        print(json.dumps(skills, indent=2))
    else:
        if not skills:
            print("No skills found.")
            return

        print(f"Found {len(skills)} skill(s) in {skills_path}:\n")
        for s in skills:
            desc = s["description"][:70] + "..." if len(s["description"]) > 70 else s["description"]
            print(f"  {s['name']}")
            print(f"    {desc}")
            print()


if __name__ == "__main__":
    main()
