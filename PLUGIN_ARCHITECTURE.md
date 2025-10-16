# SlashSense Plugin Architecture

This document explains the correct directory structure for the SlashSense plugin and how it provides globally available slash commands.

## Directory Structure

```
slashsense/                          # Plugin root (what gets distributed)
├── .claude-plugin/                  # ✅ Plugin metadata
│   └── plugin.json                  # Plugin configuration (name, version, hooks)
│
├── commands/                        # ✅ GLOBAL commands (available in ALL projects)
│   ├── slashsense-config.md        # /slashsense:config
│   ├── slashsense-config.py
│   ├── slashsense-stats.md         # /slashsense:stats
│   ├── slashsense-stats.py
│   ├── slashsense-verify.md        # /slashsense:verify
│   ├── slashsense-parallel-plan.md       # /slashsense:parallel:plan
│   ├── slashsense-parallel-execute.md    # /slashsense:parallel:execute
│   ├── slashsense-parallel-status.md     # /slashsense:parallel:status
│   └── slashsense-parallel-cleanup.md    # /slashsense:parallel:cleanup
│
├── hooks/                           # ✅ Plugin hooks
│   ├── hooks.json                   # Hook registrations
│   └── user_prompt_submit.py       # Intent detection hook
│
├── lib/                             # ✅ Plugin libraries
│   ├── keyword_matcher.py
│   ├── model2vec_matcher.py
│   ├── semantic_router_matcher.py
│   └── unified_detector.py
│
├── data/                            # ✅ Plugin data
│   └── intent_mappings.json
│
├── .claude/                         # ⚠️  DEV-ONLY (not distributed with plugin)
│   ├── commands/                    # Empty - project-level commands for development
│   └── settings.local.json          # Local development settings
│
├── docs/                            # ✅ Documentation
├── tests/                           # ✅ Tests
├── pyproject.toml                   # ✅ Python dependencies
├── README.md                        # ✅ Plugin documentation
└── LICENSE                          # ✅ MIT license
```

## Key Distinctions

### `.claude-plugin/` (Plugin Metadata)
- **Purpose**: Contains `plugin.json` with plugin metadata
- **Location**: Root of plugin directory
- **Distributed**: ✅ YES - included when plugin is installed
- **Content**: Plugin name, version, description, hooks configuration

### `commands/` (Plugin Commands)
- **Purpose**: GLOBAL slash commands available in ALL projects
- **Location**: Root of plugin directory (NOT inside `.claude-plugin/`)
- **Distributed**: ✅ YES - these become globally available
- **Naming**: Use `slashsense:command-name` pattern for namespacing
- **Frontmatter**: Must include `name`, `description`, and optionally `executable`

### `.claude/` (Project-Level Configuration)
- **Purpose**: Development-only project configuration for SlashSense itself
- **Location**: Root of SlashSense project
- **Distributed**: ❌ NO - this is for SlashSense development only
- **Content**: Local settings, project-specific commands (none currently)
- **Note**: This directory exists because SlashSense is both a plugin AND a development project

## What Gets Distributed

When users install SlashSense via `/plugin install slashsense`, they get:

```
~/.claude/plugins/slashsense/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── slashsense-config.md        # Globally available
│   ├── slashsense-stats.md         # Globally available
│   ├── slashsense-verify.md        # Globally available
│   ├── slashsense-parallel-plan.md       # Globally available
│   ├── slashsense-parallel-execute.md    # Globally available
│   ├── slashsense-parallel-status.md     # Globally available
│   └── slashsense-parallel-cleanup.md    # Globally available
├── hooks/
├── lib/
├── data/
└── ...
```

**They do NOT get**:
- `.claude/` directory (project-level, dev-only)
- `.git/` directory
- `tests/` directory (optional)

## Command Availability

### Before This Fix (WRONG ❌)
```
slashsense/
├── .claude/commands/parallel/      # ❌ Project-level (only in SlashSense dev)
│   ├── plan.md                     # Would NOT be globally available
│   ├── execute.md
│   ├── status.md
│   └── cleanup.md
├── commands/
│   └── slashsense-parallel-*.md    # Would be globally available
```

Users would get ONLY `commands/slashsense-parallel-*.md` globally. The `.claude/commands/parallel/` files would stay in the SlashSense development project only.

### After This Fix (CORRECT ✅)
```
slashsense/
├── commands/                        # ✅ Plugin-level (global to ALL projects)
│   ├── slashsense-parallel-plan.md       # Globally available
│   ├── slashsense-parallel-execute.md    # Globally available
│   ├── slashsense-parallel-status.md     # Globally available
│   └── slashsense-parallel-cleanup.md    # Globally available
```

Users get ALL parallel commands globally when they install SlashSense.

## Command Frontmatter Requirements

All plugin commands must have:

```yaml
---
name: slashsense:command-name     # Required: Full command name with namespace
description: Brief description    # Required: Shows in /help
executable: true                  # Optional: true for markdown commands
                                  # OR: path/to/script.py for Python scripts
---
```

**Examples:**

**Markdown Command (Imperative Instructions)**:
```yaml
---
name: slashsense:parallel:plan
description: Document a development plan for parallel execution
executable: true
---
```

**Python Script Command**:
```yaml
---
name: slashsense:config
description: Configure SlashSense intent detection settings
executable: commands/slashsense-config.py
---
```

## How It Works

1. **User installs plugin**:
   ```bash
   /plugin install slashsense
   ```

2. **Plugin is copied to**:
   ```
   ~/.claude/plugins/slashsense/
   ```

3. **Commands become globally available**:
   - `/slashsense:config`
   - `/slashsense:stats`
   - `/slashsense:verify`
   - `/slashsense:parallel:plan`
   - `/slashsense:parallel:execute`
   - `/slashsense:parallel:status`
   - `/slashsense:parallel:cleanup`

4. **Works in ALL projects**:
   - Users can use these commands in any project
   - No need to add project-level commands
   - No need to configure anything

5. **Natural language triggers**:
   - SlashSense hook detects intent
   - Automatically maps to correct command
   - User never needs to memorize command names

## Verification

To verify the structure is correct:

1. **Check plugin root has `.claude-plugin/`**:
   ```bash
   ls -la .claude-plugin/plugin.json
   ```

2. **Check commands are in `commands/` directory**:
   ```bash
   ls commands/slashsense-*.md
   ```

3. **Check frontmatter has `name` field**:
   ```bash
   head -5 commands/slashsense-parallel-plan.md
   ```

4. **Verify NO commands in `.claude/commands/`**:
   ```bash
   ls .claude/commands/  # Should be empty or contain dev-only commands
   ```

## Testing Locally

To test the plugin locally before publishing:

1. **Install from local directory**:
   ```bash
   /plugin install slashsense@local
   ```

2. **Verify commands are available**:
   ```bash
   /help
   # Should show slashsense:* commands
   ```

3. **Test a command**:
   ```bash
   /slashsense:parallel:plan
   ```

4. **Test natural language**:
   ```
   "plan parallel development for feature X, Y, Z"
   # SlashSense hook should detect and route to /slashsense:parallel:plan
   ```

## Publishing to Marketplace

When publishing to a Claude Code marketplace:

1. **Create marketplace.json**:
   ```json
   {
     "slug": "your-marketplace-name",
     "name": "Your Marketplace",
     "plugins": [
       {
         "name": "slashsense",
         "path": "."
       }
     ]
   }
   ```

2. **Users install via**:
   ```bash
   /plugin install slashsense@your-marketplace-name
   ```

## Common Mistakes to Avoid

❌ **DON'T put commands in `.claude/commands/`** (project-level only)
✅ **DO put commands in `commands/`** (plugin-level, global)

❌ **DON'T use `.claude-plugin/commands/`** (wrong location)
✅ **DO use `commands/` at plugin root** (correct location)

❌ **DON'T forget `name` in frontmatter** (required for command detection)
✅ **DO include `name: plugin-name:command-name`** (proper namespacing)

❌ **DON'T assume `.claude/` gets distributed** (dev-only)
✅ **DO remember only `.claude-plugin/`, `commands/`, `hooks/`, etc. get distributed**

## Summary

- ✅ Commands in `commands/` = **GLOBAL** (available in all projects)
- ❌ Commands in `.claude/commands/` = **LOCAL** (only in this project)
- ✅ `.claude-plugin/` = Plugin metadata (gets distributed)
- ❌ `.claude/` = Project configuration (does NOT get distributed)
- ✅ SlashSense parallel commands are now globally available
- ✅ No project-level duplication needed
- ✅ Users get everything by just installing the plugin
