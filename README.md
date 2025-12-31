# sync-claude-skills-to-codex

Sync Claude Code skills to Codex CLI via symlinks. Share your skill library between both AI coding assistants.

## What it does

- Creates symlinks from `~/.codex/skills/` to your Claude Code skills
- Syncs both plugin skills (`~/.claude/plugins/cache/`) and personal skills (`~/.claude/skills/`)
- Includes `list-skills` enumerator for skill discovery
- Handles plugin version changes (re-run after updates)

## Installation

### From GitHub (recommended)

```bash
# Step 1: Add the marketplace
/plugin marketplace add ariccb/sync-claude-skills-to-codex

# Step 2: Install the plugin
/plugin install sync-claude-skills-to-codex@ariccb-ai-tools
```

### Manual installation

Clone and copy the skill to your personal skills directory:

```bash
git clone https://github.com/ariccb/sync-claude-skills-to-codex.git
mkdir -p ~/.claude/skills
cp -r sync-claude-skills-to-codex/sync-claude-skills-to-codex/skills/sync-claude-skills-to-codex ~/.claude/skills/
```

## Usage

In Claude Code or Codex, run:

```
/sync-claude-skills-to-codex
```

The skill will:
1. Find all Claude Code skills (plugins + personal)
2. Create symlinks in `~/.codex/skills/`
3. Install `list-skills` enumerator in `~/bin/`

### Options

- `/sync-claude-skills-to-codex` — Run full sync
- `/sync-claude-skills-to-codex list` — List current skills without syncing
- `/sync-claude-skills-to-codex --dry-run` — Show what would be synced

### List skills

After installation, use the enumerator:

```bash
list-skills           # Human-readable list
list-skills --json    # JSON output for tooling
```

## Why symlinks?

Both Claude Code and Codex use identical `SKILL.md` formats (YAML frontmatter + markdown). Symlinks mean:
- Changes to source skills instantly reflect in both tools
- No disk space duplication
- Single source of truth

## Re-running after plugin updates

When Claude Code plugins update versions, symlinks may break. Just re-run:

```
/sync-claude-skills-to-codex
```

## License

MIT
