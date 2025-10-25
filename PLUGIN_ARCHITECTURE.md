# Contextune Plugin Architecture

This document explains the correct directory structure for the Contextune plugin and how it provides globally available slash commands.

## Directory Structure

```
contextune/                          # Plugin root (what gets distributed)
├── .claude-plugin/                  # ✅ Plugin metadata
│   └── plugin.json                  # Plugin configuration (name, version, hooks)
│
├── commands/                        # ✅ GLOBAL commands (available in ALL projects)
│   ├── contextune-config.md        # /contextune:config
│   ├── contextune-config.py
│   ├── contextune-stats.md         # /contextune:stats
│   ├── contextune-stats.py
│   ├── contextune-verify.md        # /contextune:verify
│   ├── contextune-parallel-plan.md       # /contextune:parallel:plan
│   ├── contextune-parallel-execute.md    # /contextune:parallel:execute
│   ├── contextune-parallel-status.md     # /contextune:parallel:status
│   └── contextune-parallel-cleanup.md    # /contextune:parallel:cleanup
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
- **Naming**: Use `contextune:command-name` pattern for namespacing
- **Frontmatter**: Must include `name`, `description`, and optionally `executable`

### `.claude/` (Project-Level Configuration)
- **Purpose**: Development-only project configuration for Contextune itself
- **Location**: Root of Contextune project
- **Distributed**: ❌ NO - this is for Contextune development only
- **Content**: Local settings, project-specific commands (none currently)
- **Note**: This directory exists because Contextune is both a plugin AND a development project

## What Gets Distributed

When users install Contextune via `/plugin install contextune`, they get:

```
~/.claude/plugins/contextune/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── contextune-config.md        # Globally available
│   ├── contextune-stats.md         # Globally available
│   ├── contextune-verify.md        # Globally available
│   ├── contextune-parallel-plan.md       # Globally available
│   ├── contextune-parallel-execute.md    # Globally available
│   ├── contextune-parallel-status.md     # Globally available
│   └── contextune-parallel-cleanup.md    # Globally available
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
contextune/
├── .claude/commands/parallel/      # ❌ Project-level (only in Contextune dev)
│   ├── plan.md                     # Would NOT be globally available
│   ├── execute.md
│   ├── status.md
│   └── cleanup.md
├── commands/
│   └── contextune-parallel-*.md    # Would be globally available
```

Users would get ONLY `commands/contextune-parallel-*.md` globally. The `.claude/commands/parallel/` files would stay in the Contextune development project only.

### After This Fix (CORRECT ✅)
```
contextune/
├── commands/                        # ✅ Plugin-level (global to ALL projects)
│   ├── contextune-parallel-plan.md       # Globally available
│   ├── contextune-parallel-execute.md    # Globally available
│   ├── contextune-parallel-status.md     # Globally available
│   └── contextune-parallel-cleanup.md    # Globally available
```

Users get ALL parallel commands globally when they install Contextune.

## Command Frontmatter Requirements

All plugin commands must have:

```yaml
---
name: contextune:command-name     # Required: Full command name with namespace
description: Brief description    # Required: Shows in /help
executable: true                  # Optional: true for markdown commands
                                  # OR: path/to/script.py for Python scripts
---
```

**Examples:**

**Markdown Command (Imperative Instructions)**:
```yaml
---
name: contextune:parallel:plan
description: Document a development plan for parallel execution
executable: true
---
```

**Python Script Command**:
```yaml
---
name: contextune:config
description: Configure Contextune intent detection settings
executable: commands/contextune-config.py
---
```

## How It Works

1. **User installs plugin**:
   ```bash
   /plugin install contextune
   ```

2. **Plugin is copied to**:
   ```
   ~/.claude/plugins/contextune/
   ```

3. **Commands become globally available**:
   - `/contextune:config`
   - `/contextune:stats`
   - `/contextune:verify`
   - `/contextune:parallel:plan`
   - `/contextune:parallel:execute`
   - `/contextune:parallel:status`
   - `/contextune:parallel:cleanup`

4. **Works in ALL projects**:
   - Users can use these commands in any project
   - No need to add project-level commands
   - No need to configure anything

5. **Natural language triggers**:
   - Contextune hook detects intent
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
   ls commands/contextune-*.md
   ```

3. **Check frontmatter has `name` field**:
   ```bash
   head -5 commands/contextune-parallel-plan.md
   ```

4. **Verify NO commands in `.claude/commands/`**:
   ```bash
   ls .claude/commands/  # Should be empty or contain dev-only commands
   ```

## Testing Locally

To test the plugin locally before publishing:

1. **Install from local directory**:
   ```bash
   /plugin install contextune@local
   ```

2. **Verify commands are available**:
   ```bash
   /help
   # Should show contextune:* commands
   ```

3. **Test a command**:
   ```bash
   /contextune:parallel:plan
   ```

4. **Test natural language**:
   ```
   "plan parallel development for feature X, Y, Z"
   # Contextune hook should detect and route to /contextune:parallel:plan
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
         "name": "contextune",
         "path": "."
       }
     ]
   }
   ```

2. **Users install via**:
   ```bash
   /plugin install contextune@your-marketplace-name
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
- ✅ Contextune parallel commands are now globally available
- ✅ No project-level duplication needed
- ✅ Users get everything by just installing the plugin
