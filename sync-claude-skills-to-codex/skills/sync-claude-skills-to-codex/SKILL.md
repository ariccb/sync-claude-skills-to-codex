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

Run all steps as a single bash script to avoid shell compatibility issues:

```bash
bash -c '
CODEX_SKILLS="$HOME/.codex/skills"
CLAUDE_PLUGINS="$HOME/.claude/plugins/cache"
CLAUDE_PERSONAL="$HOME/.claude/skills"

# Step 1: Ensure directories exist
mkdir -p "$CODEX_SKILLS" "$HOME/bin"

# Step 2: Sync plugin skills
echo "=== Syncing Claude plugin skills ==="
if [ -d "$CLAUDE_PLUGINS" ]; then
    find "$CLAUDE_PLUGINS" -name "SKILL.md" -path "*/skills/*" 2>/dev/null | while read skill_file; do
        skill_dir=$(dirname "$skill_file")
        skill_name=$(basename "$skill_dir")

        # Skip hidden directories (POSIX compatible)
        case "$skill_name" in .*) continue ;; esac

        # Skip if manual (non-symlink) skill exists
        if [ -e "$CODEX_SKILLS/$skill_name" ] && [ ! -L "$CODEX_SKILLS/$skill_name" ]; then
            echo "SKIP: $skill_name (manual skill exists)"
            continue
        fi

        ln -sfn "$skill_dir" "$CODEX_SKILLS/$skill_name"
        echo "SYNC: $skill_name"
    done
fi

# Step 3: Sync personal skills
echo ""
echo "=== Syncing Claude personal skills ==="
if [ -d "$CLAUDE_PERSONAL" ]; then
    for skill_dir in "$CLAUDE_PERSONAL"/*/; do
        [ -f "${skill_dir}SKILL.md" ] || continue
        skill_name=$(basename "$skill_dir")

        # Skip hidden directories (POSIX compatible)
        case "$skill_name" in .*) continue ;; esac

        if [ -e "$CODEX_SKILLS/$skill_name" ] && [ ! -L "$CODEX_SKILLS/$skill_name" ]; then
            echo "SKIP: $skill_name (manual skill exists)"
            continue
        fi

        ln -sfn "${skill_dir%/}" "$CODEX_SKILLS/$skill_name"
        echo "SYNC: $skill_name"
    done
fi

# Step 4: Report results
echo ""
echo "=== Sync Complete ==="
echo "Skills in: $CODEX_SKILLS/"
ls -la "$CODEX_SKILLS/" | grep -E "^l|^d" | grep -v "^\." | head -20
'
```

### Step 5: Install list-skills enumerator (optional)

If list-skills is not already installed, copy it from the skill directory:

```bash
# Find the skill directory (works whether installed as plugin or personal skill)
SKILL_DIR=$(find ~/.claude -name "list-skills.py" -path "*sync-claude-skills-to-codex*" 2>/dev/null | head -1 | xargs dirname)
if [ -n "$SKILL_DIR" ] && [ ! -f "$HOME/bin/list-skills" ]; then
    cp "$SKILL_DIR/list-skills.py" "$HOME/bin/list-skills"
    chmod +x "$HOME/bin/list-skills"
    echo "INSTALLED: ~/bin/list-skills"
fi
```

### Verify installation

```bash
# List all synced skills
ls -la ~/.codex/skills/

# If list-skills is installed
list-skills
```

## Output

After running, both Claude Code and Codex will have access to the same skills via:
- Claude Code: Original skill locations (plugins + `~/.claude/skills/`)
- Codex CLI: Symlinks in `~/.codex/skills/`

## Notes

- **Re-run after plugin updates**: When plugins update versions, symlinks may break. Re-run this skill to fix.
- **Manual skills preserved**: If you have manually created skills in `~/.codex/skills/`, they won't be overwritten.
- **Excludes project skills**: Only syncs global skills, not project-level `.claude/skills/` folders.
