---
name: ctx:git-commit
description: Deterministic commit and push workflow using scripts (DRY compliant)
keywords:
  - commit
  - push
  - git commit
  - commit and push
  - save changes
executable: true
---

# Git Commit - Deterministic Commit and Push Workflow

You are executing a deterministic git commit and push workflow.

**Cost:** ~$0.002 (545 tokens) vs ~$0.037-0.086 (8K-25K tokens) for multi-tool approach
**Savings:** 93-97% token reduction

---

## Workflow

### Step 1: Determine What to Commit

Check git status to understand what files changed:

```bash
git status --short
```

**Analyze the output:**
- `M` = Modified files
- `A` = Added files
- `D` = Deleted files
- `??` = Untracked files

### Step 2: Stage and Commit

**Use the plugin's commit script (works from any project):**

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "<files>" "<message>" "<branch>" "<remote>"
```

> **Note:** `${CLAUDE_PLUGIN_ROOT}` is automatically set by Claude Code to the plugin's installation directory (e.g., `~/.claude/plugins/contextune@Contextune/`). This ensures the script is always accessible regardless of which project you're working in.

**Parameters:**
- `<files>` - Files to commit (use `.` for all changes, or specific files)
- `<message>` - Commit message (follows conventional commits format)
- `<branch>` - Branch name (default: `master`, optional)
- `<remote>` - Remote name (auto-detected if not specified, optional)

**Example 1: Commit all changes**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "." "feat: add new feature

Detailed description of changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Example 2: Commit specific files**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "src/feature.ts tests/feature.test.ts" "feat: implement feature X"
```

**Example 3: Specify branch and remote**
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "." "fix: resolve bug" "develop" "origin"
```

---

## Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tooling changes

**Examples:**

```bash
# Feature
"feat: add user authentication

Implemented JWT-based authentication with refresh tokens.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Bug fix
"fix: resolve memory leak in WebSocket handler

Fixed issue where connections were not properly cleaned up.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Documentation
"docs: update API documentation

Added examples for new endpoints.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## What the Script Does

The `commit_and_push.sh` script handles:

1. ✅ `git add <files>` - Stage specified files
2. ✅ Check for changes - Skip if nothing to commit
3. ✅ `git commit -m "<message>"` - Commit with message
4. ✅ Auto-detect remote - Use first remote if not specified
5. ✅ `git push <remote> <branch>` - Push to remote
6. ✅ Error handling - Clear error messages

**Script output:**
```
✅ Committed and pushed to origin/master
```

---

## Error Handling

**If script fails:**

1. **No changes to commit:**
   ```
   ℹ️  No changes to commit
   ```
   - Expected when files are already committed

2. **No git remotes:**
   ```
   Error: No git remotes configured
   ```
   - Add remote: `git remote add origin <url>`

3. **Permission denied:**
   ```
   Error: Permission denied
   ```
   - Check SSH keys or credentials

4. **Merge conflicts:**
   ```
   Error: Merge conflict detected
   ```
   - Pull latest changes first: `git pull <remote> <branch>`
   - Resolve conflicts manually

---

## Script Location

The commit script is part of the Contextune plugin and is automatically accessible via:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh"
```

**Where `CLAUDE_PLUGIN_ROOT` resolves to:**
- `~/.claude/plugins/contextune@Contextune/` (typical installation)
- Set automatically by Claude Code when executing plugin commands

**Fallback (if env var not set):**
```bash
git add <files> && git commit -m "<message>" && git push
```

## Why Minimize Tool Calls?

### Token Efficiency

**Multi-tool approach (what NOT to do):**
```
Tool 1: git status
Tool 2: git add .
Tool 3: git status --short
Tool 4: git diff --cached
Tool 5: git commit -m "message"
Tool 6: git log -1
Tool 7: git push origin master
Tool 8: git status

Cost: ~8K-25K tokens ($0.037-0.086)
```

**Efficient approach (correct):**
```
Tool 1: git add . && git commit -m "message" && git push

Cost: ~545 tokens ($0.002)
Savings: 93-97% reduction
```

### Reliability

- ✅ **Deterministic** - Same input → same output
- ✅ **Tested** - Script handles edge cases
- ✅ **Fast** - Single command, 100-500ms execution
- ✅ **Error recovery** - Clear error messages

### Compliance

- ✅ Follows UNIFIED_DRY_STRATEGY.md
- ✅ Uses scripts for workflows (not multi-tool)
- ✅ Automatic remote detection
- ✅ Proper error handling

---

## Integration with Contextune

This command is available via:

1. **Explicit command:** `/ctx:git-commit`
2. **Natural language:** Contextune detects and routes automatically:
   - "commit and push"
   - "save changes"
   - "commit these files"

3. **PreToolUse hook:** Intercepts manual git commands and suggests script

---

## Related Commands

- `/ctx:git-pr` - Create pull request using script
- `/ctx:git-merge` - Merge branches using script
- `/ctx:cleanup` - Cleanup worktrees and branches

---

## Advanced Usage

### Multiple File Patterns

```bash
# Commit specific directories
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "src/ tests/" "feat: implement feature"

# Commit specific file types
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "*.ts *.tsx" "refactor: update types"
```

### Multiline Commit Messages

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh" "." "feat: add authentication

Implemented features:
- JWT token generation
- Refresh token rotation
- User session management

Breaking changes:
- Auth API endpoints changed from /api/v1 to /api/v2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Notes

- **Always use `${CLAUDE_PLUGIN_ROOT}`** - This resolves to the plugin's installation directory
- Script works from ANY project directory (not just Contextune)
- Script auto-updates when plugin is updated
- Single git commands (like `git status`) are always OK without script
- Follow conventional commit format for consistency
- Include co-authorship footer for Claude-assisted commits

---

## See Also

- `UNIFIED_DRY_STRATEGY.md` - DRY strategy for git operations
- `${CLAUDE_PLUGIN_ROOT}/scripts/commit_and_push.sh` - Script source code
- `${CLAUDE_PLUGIN_ROOT}/scripts/smart_execute.sh` - Error recovery wrapper
- `${CLAUDE_PLUGIN_ROOT}/scripts/create_pr.sh` - Create pull request script
- `${CLAUDE_PLUGIN_ROOT}/scripts/merge_and_cleanup.sh` - Merge and cleanup script
