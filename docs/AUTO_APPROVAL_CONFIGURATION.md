# Auto-Approval Configuration for Parallel Agents

**Purpose:** Configure Claude Code to auto-approve git and GitHub CLI commands so parallel agents can work autonomously without approval bottlenecks.

**Problem:** When spawning multiple Haiku agents in parallel, each agent needs to run git/gh commands (create issues, worktrees, commits, pushes). Without auto-approval, you must approve each command individually, negating the parallelism benefits.

**Solution:** Pre-approve safe git/gh commands using Claude Code's IAM permission system.

---

## Quick Setup (Recommended)

### Step 1: Access Permissions UI

In Claude Code, run:
```
/permissions
```

This opens the permission configuration interface.

### Step 2: Add Allow Rules for Git Commands

Add these allow rules for git operations in worktrees:

```
Bash(git worktree:*)
Bash(git add:*)
Bash(git commit:*)
Bash(git push:*)
Bash(git status)
Bash(git diff:*)
Bash(git log:*)
Bash(git checkout:*)
Bash(git branch:*)
Bash(git remote:*)
```

### Step 3: Add Allow Rules for GitHub CLI

Add these allow rules for GitHub operations:

```
Bash(gh issue create:*)
Bash(gh issue comment:*)
Bash(gh issue close:*)
Bash(gh issue view:*)
Bash(gh issue list:*)
Bash(gh pr create:*)
Bash(gh auth status)
Bash(gh label create:*)
```

### Step 4: Add Project-Specific Rules

For Contextune parallel execution, add:

```
Bash(mkdir -p .parallel/*)
Bash(uv run:*)
Bash(npm install)
Bash(npm run test:*)
Bash(pytest:*)
```

---

## How It Works

**IAM Permission System:**

Claude Code has three rule types:
1. **Allow rules** - Auto-approve without prompts
2. **Ask rules** - Prompt for confirmation (overrides allow)
3. **Deny rules** - Block completely (highest precedence)

**Bash Command Matching:**

Uses **prefix matching** (not regex):
- `Bash(git worktree:*)` matches `git worktree add`, `git worktree list`, etc.
- `Bash(git add:*)` matches `git add .`, `git add file.js`, etc.
- `Bash(git status)` matches exactly `git status`

**Important:** The `:*` syntax means "this command followed by anything"

---

## Permission Modes

You can also set a global permission mode in settings:

### Option A: Accept Edits Mode (Recommended for Development)

In your Claude Code settings, set:
```json
{
  "defaultMode": "acceptEdits"
}
```

**What it does:**
- Auto-approves file edits during session
- Still asks for Bash commands (good for safety)
- Session expires when you close Claude Code

**Best for:** Active development with controlled git operations

### Option B: Bypass Permissions Mode (Use with Caution!)

```json
{
  "defaultMode": "bypassPermissions"
}
```

**What it does:**
- Skips ALL approval prompts
- No safety checks

**⚠️ WARNING:** Only use in safe, isolated environments (VMs, containers)

**Best for:** CI/CD pipelines, testing environments

---

## Advanced: PreToolUse Hook Auto-Approval

For more fine-grained control, create a PreToolUse hook that auto-approves based on logic:

### 1. Create Hook Script

Create `hooks/auto_approve_git.py`:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import sys
import json
import re

def should_auto_approve(tool_name: str, params: dict) -> bool:
    """
    Determine if a tool call should be auto-approved.
    """

    if tool_name == "Bash":
        command = params.get("command", "")

        # Auto-approve safe git operations
        safe_git_patterns = [
            r"^git worktree (add|list|remove|prune)",
            r"^git (add|status|diff|log|branch|remote)",
            r"^git commit -m",
            r"^git push origin feature/",
            r"^git checkout -b feature/",
        ]

        for pattern in safe_git_patterns:
            if re.match(pattern, command):
                return True

        # Auto-approve GitHub CLI operations
        safe_gh_patterns = [
            r"^gh issue (create|comment|close|view|list)",
            r"^gh pr (create|view|list)",
            r"^gh label create",
            r"^gh auth status",
        ]

        for pattern in safe_gh_patterns:
            if re.match(pattern, command):
                return True

        # Auto-approve worktree operations
        if command.startswith("cd /Users/") and "/worktrees/" in command:
            return True

        # Auto-approve project-specific commands
        if command.startswith("uv run"):
            return True
        if command in ["npm install", "npm run test"]:
            return True

    # Auto-approve Read operations in worktrees
    if tool_name == "Read":
        file_path = params.get("file_path", "")
        if "/worktrees/" in file_path:
            return True

    # Auto-approve Write/Edit in worktrees
    if tool_name in ["Write", "Edit"]:
        file_path = params.get("file_path", "")
        if "/worktrees/" in file_path:
            return True

    return False

def main():
    try:
        # Read PreToolUse event from stdin
        event = json.loads(sys.stdin.read())

        tool_name = event.get("toolName", "")
        params = event.get("parameters", {})

        # Check if should auto-approve
        if should_auto_approve(tool_name, params):
            result = {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": f"Auto-approved: {tool_name} with safe parameters"
                }
            }
        else:
            # Let normal approval flow proceed
            result = {
                "continue": True
            }

        print(json.dumps(result))
        sys.exit(0)

    except Exception as e:
        # On error, let normal flow proceed
        print(json.dumps({"continue": True}), file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### 2. Register Hook

Update `hooks/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run ${CLAUDE_PLUGIN_ROOT}/hooks/auto_approve_git.py",
            "timeout": 500,
            "description": "Auto-approve safe git/gh operations"
          }
        ]
      }
    ]
  }
}
```

**How it works:**
- Hook intercepts EVERY Bash/Read/Write/Edit call
- Checks if it matches safe patterns
- If yes: Sets `permissionDecision: "allow"` to auto-approve
- If no: Lets normal approval flow proceed
- Runs in 500ms timeout (very fast, no bottleneck)

---

## Recommended Configuration for Contextune

For optimal parallel agent performance:

### Approach 1: IAM Rules (Simplest)

1. Run `/permissions` in Claude Code
2. Add all the allow rules from "Quick Setup" above
3. Set `defaultMode: "acceptEdits"` in settings
4. Done! Agents can work autonomously

**Pros:**
- ✅ Simple configuration
- ✅ No custom scripts needed
- ✅ Easy to review/modify rules

**Cons:**
- ❌ Less flexible (prefix matching only)
- ❌ All-or-nothing per command pattern

### Approach 2: PreToolUse Hook (Most Flexible)

1. Create the `auto_approve_git.py` hook script
2. Register it in `hooks/hooks.json`
3. Customize the patterns in the script
4. Test with: `echo '{"toolName":"Bash","parameters":{"command":"git status"}}' | uv run hooks/auto_approve_git.py`

**Pros:**
- ✅ Full regex power
- ✅ Custom logic (e.g., only approve in worktrees)
- ✅ Easy to extend
- ✅ Can log decisions for audit

**Cons:**
- ❌ Requires Python/UV
- ❌ More complex to debug
- ❌ Slight overhead (500ms timeout)

### Recommended Hybrid Approach

**Use BOTH:**
1. IAM rules for common, safe commands (git, gh basics)
2. PreToolUse hook for complex logic (only approve in worktrees, validate parameters)

This gives you:
- Fast auto-approval for common cases (IAM)
- Fine-grained control for edge cases (hook)
- Safety net (hook can deny even IAM-allowed commands if suspicious)

---

## Testing Your Configuration

### Test 1: Manual Command

In Claude Code, ask:
```
Can you run: git worktree list
```

Expected: Should execute without approval prompt

### Test 2: GitHub Issue Creation

```
Can you create a GitHub issue titled "Test" with body "Testing auto-approval"
```

Expected: Should execute without approval prompt

### Test 3: Parallel Agent Spawn

```
/contextune:parallel:execute
```

Expected: All agents create issues/worktrees without prompts

### Test 4: Check Logs

If using PreToolUse hook, check logs:
```bash
tail -f /tmp/claude-code-hooks.log
```

You should see "Auto-approved: Bash with safe parameters"

---

## Security Considerations

### Safe to Auto-Approve

✅ **Git operations in worktrees:**
- `git worktree add/list/remove/prune`
- `git add`, `git commit`, `git push` to feature branches
- `git status`, `git diff`, `git log` (read-only)

✅ **GitHub CLI read operations:**
- `gh issue list/view`
- `gh pr list/view`
- `gh auth status`

✅ **GitHub CLI create operations (with validation):**
- `gh issue create` (agents create their own issues)
- `gh issue comment` (documenting progress)
- `gh label create` (idempotent, non-destructive)

### DO NOT Auto-Approve (Without Extra Checks)

❌ **Destructive git operations:**
- `git push --force`
- `git reset --hard`
- `git branch -D` (force delete)
- `git clean -fd` (deletes files)

❌ **GitHub CLI destructive operations:**
- `gh repo delete`
- `gh issue delete`
- `gh pr close` (without validation)

❌ **System operations:**
- `rm -rf`
- `sudo` commands
- Network operations outside GitHub

### Worktree Safety

Commands in worktrees are generally safe because:
- ✅ Isolated from main branch
- ✅ Can be deleted without affecting main
- ✅ Feature branches can be abandoned
- ✅ No direct impact on production

But still validate:
- ⚠️ Don't auto-approve `git push origin main` from worktree
- ⚠️ Don't auto-approve destructive file operations
- ⚠️ Check branch names (only feature/*, not main/master)

---

## Troubleshooting

### Issue: "Approval still required despite allow rule"

**Cause:** Ask or Deny rule overrides Allow rule

**Fix:**
1. Run `/permissions`
2. Check for conflicting Ask/Deny rules
3. Remove or modify them
4. Remember: Deny > Ask > Allow in precedence

### Issue: "PreToolUse hook not firing"

**Cause:** Hook not registered or syntax error

**Fix:**
1. Check `hooks/hooks.json` is valid JSON
2. Test hook manually: `echo '{"toolName":"Bash","parameters":{"command":"git status"}}' | uv run hooks/auto_approve_git.py`
3. Check Claude Code console for hook errors
4. Verify `CLAUDE_PLUGIN_ROOT` environment variable

### Issue: "Hook too slow, still prompts"

**Cause:** Hook timeout exceeded (default 500ms)

**Fix:**
1. Increase timeout in hooks.json: `"timeout": 1000`
2. Optimize hook logic (remove expensive operations)
3. Fall back to IAM rules for simple patterns

### Issue: "Agents blocked on permissions despite config"

**Cause:** Agent spawned in different context, doesn't inherit main agent's permissions

**Fix:**
1. Use IAM rules (global across all agents)
2. OR: Pass permission context to agents via environment
3. OR: Configure managed-settings.json (enterprise)

---

## Summary: Fastest Setup

**5-Minute Configuration:**

1. **Run:** `/permissions` in Claude Code

2. **Add these rules:**
   ```
   Bash(git worktree:*)
   Bash(git add:*)
   Bash(git commit:*)
   Bash(git push origin feature/*:*)
   Bash(gh issue:*)
   Bash(gh label create:*)
   ```

3. **Set mode:** `defaultMode: "acceptEdits"` in settings

4. **Test:** `/contextune:parallel:execute`

5. **Verify:** Agents create issues/worktrees without prompts

**Done!** 🚀 Your parallel agents can now work autonomously.

---

## Resources

- [Claude Code IAM Documentation](https://docs.claude.com/en/docs/claude-code/iam.md)
- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks.md)

---

**Last Updated:** 2025-10-26 (v0.8.9)
