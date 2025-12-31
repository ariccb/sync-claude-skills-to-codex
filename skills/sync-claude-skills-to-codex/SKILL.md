---
name: sync-claude-skills-to-codex
description: Sync Claude Code skills (plugins + personal) to Codex CLI via symlinks. Creates ~/bin/list-skills enumerator for skill discovery. Run after installing new Claude plugins.
---

# Sync Claude Skills to Codex

Synchronize Claude Code skills to Codex CLI so both tools share the same skill library.

**What it does:**
- Creates symlinks from `~/.codex/skills/` to Claude skill sources
- Syncs both plugin skills (`~/.claude/plugins/cache/`) and personal skills (`~/.claude/skills/`)
- Installs `list-skills` enumerator in `~/bin/` for skill discovery
- Handles version changes (re-run after plugin updates)

## Input

Arguments: #$ARGUMENTS

Options:
- `/sync-claude-skills-to-codex` — Run full sync
- `/sync-claude-skills-to-codex list` — Just list current skills (doesn't sync)
- `/sync-claude-skills-to-codex --dry-run` — Show what would be synced

## Workflow

### Step 1: Ensure directories exist

```bash
mkdir -p "$HOME/.codex/skills" "$HOME/bin"
```

### Step 2: Sync plugin skills

Find all SKILL.md files in Claude plugin cache and create symlinks:

```bash
CODEX_SKILLS="$HOME/.codex/skills"
CLAUDE_PLUGINS="$HOME/.claude/plugins/cache"

find "$CLAUDE_PLUGINS" -name "SKILL.md" -path "*/skills/*" 2>/dev/null | while read skill_file; do
    skill_dir=$(dirname "$skill_file")
    skill_name=$(basename "$skill_dir")

    # Skip hidden directories
    [[ "$skill_name" == .* ]] && continue

    # Skip if manual (non-symlink) skill exists
    if [ -e "$CODEX_SKILLS/$skill_name" ] && [ ! -L "$CODEX_SKILLS/$skill_name" ]; then
        echo "SKIP: $skill_name (manual skill exists)"
        continue
    fi

    ln -sfn "$skill_dir" "$CODEX_SKILLS/$skill_name"
    echo "SYNC: $skill_name -> $skill_dir"
done
```

### Step 3: Sync personal skills

```bash
CLAUDE_PERSONAL="$HOME/.claude/skills"

if [ -d "$CLAUDE_PERSONAL" ]; then
    for skill_dir in "$CLAUDE_PERSONAL"/*/; do
        [ -f "$skill_dir/SKILL.md" ] || continue
        skill_name=$(basename "$skill_dir")
        [[ "$skill_name" == .* ]] && continue

        if [ -e "$CODEX_SKILLS/$skill_name" ] && [ ! -L "$CODEX_SKILLS/$skill_name" ]; then
            echo "SKIP: $skill_name (manual skill exists)"
            continue
        fi

        ln -sfn "$skill_dir" "$CODEX_SKILLS/$skill_name"
        echo "SYNC: $skill_name -> $skill_dir"
    done
fi
```

### Step 4: Install list-skills enumerator

Create `~/bin/list-skills` if it doesn't exist. See [list-skills.py](list-skills.py) for the full script.

```bash
if [ ! -f "$HOME/bin/list-skills" ]; then
    # Copy list-skills.py to ~/bin/list-skills and make executable
    cp "$(dirname "$0")/list-skills.py" "$HOME/bin/list-skills"
    chmod +x "$HOME/bin/list-skills"
    echo "INSTALLED: ~/bin/list-skills"
fi
```

### Step 5: Report results

```bash
echo ""
echo "=== Sync Complete ==="
echo "Skills available in: ~/.codex/skills/"
echo "Run 'list-skills' to see all skills"
echo "Run 'list-skills --json' for machine-readable output"
```

## Output

After running, both Claude Code and Codex will have access to the same skills via:
- Claude Code: Original skill locations (plugins + `~/.claude/skills/`)
- Codex CLI: Symlinks in `~/.codex/skills/`

## Notes

- **Re-run after plugin updates**: When plugins update versions, symlinks may break. Re-run this skill to fix.
- **Manual skills preserved**: If you have manually created skills in `~/.codex/skills/`, they won't be overwritten.
- **Excludes project skills**: Only syncs global skills, not project-level `.claude/skills/` folders.
