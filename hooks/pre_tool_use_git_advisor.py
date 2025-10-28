#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
PreToolUse Git Workflow Advisor

Intercepts Bash tool calls and detects git multi-tool workflows.
Provides non-blocking feedback suggesting script usage instead.

Layer 3 defense: Last line of defense against inefficient git workflows.

Hook Protocol:
- Input: JSON via stdin with tool invocation data
- Output: JSON via stdout with feedback
- IMPORTANT: Never blocks (always {"continue": true})
"""

import json
import re
import sys


def detect_git_workflow_in_bash(command: str) -> tuple[bool, str | None, str | None]:
    """
    Detect git multi-tool workflows in Bash commands.

    Returns: (is_workflow, workflow_type, script_recommendation)
    """
    # Normalize command
    cmd = command.strip()

    # Pattern 1: git add && git commit
    if re.search(r'git\s+add.*&&.*git\s+commit', cmd, re.IGNORECASE):
        return True, "commit_workflow", "./scripts/commit_and_push.sh"

    # Pattern 2: git commit && git push
    if re.search(r'git\s+commit.*&&.*git\s+push', cmd, re.IGNORECASE):
        return True, "commit_push_workflow", "./scripts/commit_and_push.sh"

    # Pattern 3: git add && git commit && git push
    if re.search(r'git\s+add.*&&.*git\s+commit.*&&.*git\s+push', cmd, re.IGNORECASE):
        return True, "full_workflow", "./scripts/commit_and_push.sh"

    # Pattern 4: Sequential git commands with ; or newlines
    git_commands = re.findall(r'git\s+\w+', cmd, re.IGNORECASE)
    if len(git_commands) >= 2:
        # Multiple git commands in one call
        return True, "multi_command", "./scripts/commit_and_push.sh"

    # Pattern 5: git checkout && git pull && git merge
    if re.search(r'git\s+checkout.*&&.*git\s+(pull|merge)', cmd, re.IGNORECASE):
        return True, "merge_workflow", "./scripts/merge_and_cleanup.sh"

    return False, None, None


def calculate_token_waste(workflow_type: str) -> tuple[int, int, float]:
    """
    Calculate token waste for multi-tool approach vs script.

    Returns: (multi_tool_tokens, script_tokens, savings_percent)
    """
    # Conservative estimates
    multi_tool_tokens = {
        "commit_workflow": 8000,
        "commit_push_workflow": 15000,
        "full_workflow": 25000,
        "multi_command": 12000,
        "merge_workflow": 18000,
    }

    script_tokens = 545  # Average for script-based approach

    tokens_wasted = multi_tool_tokens.get(workflow_type, 10000)
    savings_percent = ((tokens_wasted - script_tokens) / tokens_wasted) * 100

    return tokens_wasted, script_tokens, savings_percent


def main():
    """PreToolUse hook entry point."""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        # DEBUG logging
        print(f"DEBUG: PreToolUse triggered for tool: {tool_name}", file=sys.stderr)

        # Only intercept Bash tool calls
        if tool_name != "Bash":
            # Not a Bash call, continue without feedback
            response = {"continue": True}
            print(json.dumps(response))
            return

        # Get the bash command
        command = tool_input.get("command", "")
        print(f"DEBUG: Bash command: {command[:100]}...", file=sys.stderr)

        # Detect git workflows
        is_workflow, workflow_type, script_recommendation = detect_git_workflow_in_bash(command)

        if not is_workflow:
            # Not a git workflow, continue
            response = {"continue": True}
            print(json.dumps(response))
            return

        # Git workflow detected! Provide non-blocking feedback
        print(f"DEBUG: Git workflow detected: {workflow_type}", file=sys.stderr)

        # Calculate token waste
        multi_tokens, script_tokens, savings = calculate_token_waste(workflow_type)

        # Build feedback message
        feedback = f"""🚨 Git Workflow Inefficiency Detected

**Detected:** Multi-tool git workflow in Bash command
**Type:** {workflow_type.replace('_', ' ').title()}

**Current approach:**
```bash
{command[:200]}{"..." if len(command) > 200 else ""}
```

**Cost:** ~{multi_tokens:,} tokens (~${multi_tokens * 0.003 / 1000:.3f})

---

💡 **Recommended:** Use deterministic script instead

**Script:** `{script_recommendation}`

**Benefits:**
- ✅ {savings:.0f}% token reduction
- ✅ Cost: ~{script_tokens} tokens (~${script_tokens * 0.003 / 1000:.3f})
- ✅ Savings: ~{multi_tokens - script_tokens:,} tokens per invocation
- ✅ Deterministic, tested workflow
- ✅ Auto-detects remote
- ✅ Proper error handling

**Example usage:**
```bash
# Instead of multiple git commands:
{script_recommendation} "." "feat: add feature

Detailed commit message here.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

**Slash Command:** Use `/ctx:git-commit` for guided workflow

**See:** UNIFIED_DRY_STRATEGY.md for git workflow guidelines

---

⚠️ **Note:** Continuing with your original command, but **consider using the script** for future efficiency.
"""

        # Log the detection
        print(f"DEBUG: Providing feedback for {workflow_type}", file=sys.stderr)
        print(f"DEBUG: Token waste: {multi_tokens - script_tokens:,} tokens ({savings:.0f}% reduction)", file=sys.stderr)

        # IMPORTANT: Never block, always continue
        response = {
            "continue": True,
            "feedback": feedback,
            "suppressOutput": False  # Show feedback to user
        }

        print(json.dumps(response))

    except Exception as e:
        # Never fail the hook - always continue
        print(f"DEBUG: PreToolUse error: {e}", file=sys.stderr)
        response = {"continue": True}
        print(json.dumps(response))


if __name__ == "__main__":
    main()
