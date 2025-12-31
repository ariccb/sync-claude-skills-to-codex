---
name: sync-claude-skills-to-codex
description: Sync Claude Code skills (plugins + personal) to Codex CLI by copying folders. Creates ~/bin/list-skills enumerator for skill discovery. Run after installing new Claude plugins.
---

# Sync Claude Skills to Codex

Synchronize Claude Code skills to Codex CLI so both tools share the same skill library.

**What it does:**
- Copies skill folders from Claude sources to `~/.codex/skills/`
- Syncs both plugin skills (`~/.claude/plugins/cache/`) and personal skills (`~/.claude/skills/`)
- Installs `list-skills` enumerator in `~/bin/` for skill discovery
- Uses a `.synced-from-claude` marker to track managed skills (safe to update on re-runs)
- Preserves manually created skills in `~/.codex/skills/`

## Input

Arguments: #$ARGUMENTS

Options:
- `/sync-claude-skills-to-codex` — Run full sync (respects marker files)
- `/sync-claude-skills-to-codex --force` — Force sync ALL skills, overwriting existing ones
- `/sync-claude-skills-to-codex list` — Just list current skills (doesn't sync)
- `/sync-claude-skills-to-codex --dry-run` — Show what would be synced

## How the Marker File Works

The `.synced-from-claude` marker file is a provenance tracking mechanism:

1. **On first sync**: When a skill is copied to `~/.codex/skills/`, a `.synced-from-claude` file is created inside the skill folder containing the source path.

2. **On subsequent syncs**:
   - If the marker file EXISTS → skill is "managed" → safe to overwrite with fresh copy
   - If the marker file is MISSING → skill is "manual" → skip to preserve user customizations

3. **Why this matters**: If you manually create or customize a skill in `~/.codex/skills/`, it won't have the marker file, so the sync won't accidentally overwrite your work.

4. **Force flag**: Use `--force` to ignore marker file checks and sync everything. This will overwrite ALL skills including manual ones.

## Workflow

First, check if `--force` flag is present in arguments:

```bash
# Set FORCE_SYNC based on arguments
FORCE_SYNC=false
case "#$ARGUMENTS" in
  *--force*) FORCE_SYNC=true ;;
esac
echo "Force sync: $FORCE_SYNC"
```

Run all steps as a single bash script to avoid shell compatibility issues:

```bash
bash -c '
CODEX_SKILLS="$HOME/.codex/skills"
CLAUDE_PLUGINS="$HOME/.claude/plugins/cache"
CLAUDE_PERSONAL="$HOME/.claude/skills"
MARKER_FILE=".synced-from-claude"
FORCE_SYNC="'"$FORCE_SYNC"'"

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

        target_dir="$CODEX_SKILLS/$skill_name"

        # Handle symlinks first (migration from old version) - always replace
        if [ -L "$target_dir" ]; then
            rm "$target_dir"
            echo "MIGRATE: $skill_name (removing old symlink)"
        # Skip if manual (non-synced) directory exists (unless --force)
        elif [ -d "$target_dir" ] && [ ! -f "$target_dir/$MARKER_FILE" ] && [ "$FORCE_SYNC" != "true" ]; then
            echo "SKIP: $skill_name (manual skill exists, use --force to overwrite)"
            continue
        fi

        # Remove existing synced copy and replace with fresh copy
        if [ -d "$target_dir" ]; then
            rm -rf "$target_dir"
        fi

        cp -r "$skill_dir" "$target_dir"
        echo "$skill_dir" > "$target_dir/$MARKER_FILE"
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

        target_dir="$CODEX_SKILLS/$skill_name"

        # Handle symlinks first (migration from old version) - always replace
        if [ -L "$target_dir" ]; then
            rm "$target_dir"
            echo "MIGRATE: $skill_name (removing old symlink)"
        # Skip if manual (non-synced) directory exists (unless --force)
        elif [ -d "$target_dir" ] && [ ! -f "$target_dir/$MARKER_FILE" ] && [ "$FORCE_SYNC" != "true" ]; then
            echo "SKIP: $skill_name (manual skill exists, use --force to overwrite)"
            continue
        fi

        # Remove existing synced copy and replace with fresh copy
        if [ -d "$target_dir" ]; then
            rm -rf "$target_dir"
        fi

        cp -r "${skill_dir%/}" "$target_dir"
        echo "${skill_dir%/}" > "$target_dir/$MARKER_FILE"
        echo "SYNC: $skill_name"
    done
fi

# Step 4: Report results
echo ""
echo "=== Sync Complete ==="
echo "Skills in: $CODEX_SKILLS/"
ls -la "$CODEX_SKILLS/" | head -20
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
- Codex CLI: Copied folders in `~/.codex/skills/`

## Notes

- **Re-run after plugin updates**: When plugins update versions, re-run this skill to get the latest copies.
- **Manual skills preserved**: Skills without a `.synced-from-claude` marker file won't be overwritten (unless `--force` is used).
- **Excludes project skills**: Only syncs global skills, not project-level `.claude/skills/` folders.
- **Migration**: Old symlinks are automatically removed and replaced with real copies on re-run.
- **Force sync**: Use `--force` to overwrite all skills including manual ones. Useful for initial setup or when you want to reset everything to match Claude sources.
