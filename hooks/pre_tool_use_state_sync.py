#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
PreToolUse State Sync - Git-Powered File State Awareness

Intercepts file operations (Write/Edit/NotebookEdit) and checks if files
changed externally since Claude last read them.

Uses git as source of truth for current state.

**Token Overhead:** ~200-500 tokens (only when files changed externally)
**Blocking:** No (provides feedback, always continues)

Hook Protocol:
- Input: JSON via stdin with tool invocation data
- Output: JSON via stdout with feedback
- IMPORTANT: Never blocks (always {"continue": true})
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_file_git_status(file_path: str) -> tuple[bool, str]:
    """
    Check if file has uncommitted changes or differs from last commit.

    Returns: (has_changes, status_description)
    """
    try:
        # Check git status for this specific file
        result = subprocess.run(
            ["git", "status", "--short", file_path],
            capture_output=True,
            text=True,
            timeout=1,
        )

        status = result.stdout.strip()

        if not status:
            # File unchanged
            return False, "unchanged"

        # Parse git status codes
        # M  = Modified (staged)
        # _M = Modified (unstaged)
        # ?? = Untracked
        # A  = Added
        # D  = Deleted

        if status.startswith("M") or status.startswith(" M"):
            return True, "modified"
        elif status.startswith("??"):
            return True, "untracked"
        elif status.startswith("A"):
            return True, "added"
        elif status.startswith("D"):
            return True, "deleted"
        else:
            return True, status[:2]

    except Exception as e:
        print(f"DEBUG: Failed to check git status: {e}", file=sys.stderr)
        return False, "unknown"


def get_file_diff_summary(file_path: str) -> str:
    """
    Get summary of changes in file since last commit.

    Returns: Diff summary (lines added/removed)
    """
    try:
        # Get diff stat
        result = subprocess.run(
            ["git", "diff", "HEAD", file_path, "--stat"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        diff_stat = result.stdout.strip()

        if not diff_stat:
            return "No changes"

        # Extract line changes from stat
        # Example: "file.py | 10 +++++-----"
        return diff_stat

    except Exception as e:
        print(f"DEBUG: Failed to get diff summary: {e}", file=sys.stderr)
        return "Unknown changes"


def check_file_tracked_in_cache(file_path: str) -> tuple[bool, str | None]:
    """
    Check if Claude has read this file in current session.

    Uses simple cache file to track reads.

    Returns: (was_read, last_read_hash)
    """
    try:
        cache_dir = Path.home() / ".claude" / "plugins" / "contextune" / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / "read_files.json"

        if not cache_file.exists():
            return False, None

        with open(cache_file) as f:
            cache = json.load(f)

        file_info = cache.get(file_path)
        if file_info:
            return True, file_info.get("git_hash")

        return False, None

    except Exception as e:
        print(f"DEBUG: Failed to check read cache: {e}", file=sys.stderr)
        return False, None


def main():
    """PreToolUse hook entry point."""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())

        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        # DEBUG logging
        print(f"DEBUG: PreToolUse state sync for tool: {tool_name}", file=sys.stderr)

        # Only intercept file operation tools
        if tool_name not in ["Write", "Edit", "NotebookEdit"]:
            # Not a file operation, continue without feedback
            response = {"continue": True}
            print(json.dumps(response))
            return

        # Get file path from tool input
        file_path = tool_input.get("file_path")
        if not file_path:
            # No file path, continue
            response = {"continue": True}
            print(json.dumps(response))
            return

        print(f"DEBUG: Checking state for file: {file_path}", file=sys.stderr)

        # Check git status
        has_changes, status = get_file_git_status(file_path)

        if not has_changes:
            # File unchanged, continue without feedback
            response = {"continue": True}
            print(json.dumps(response))
            return

        # File has external changes!
        print(f"DEBUG: File has external changes: {status}", file=sys.stderr)

        # Get diff summary
        diff_summary = get_file_diff_summary(file_path)

        # Build feedback message
        feedback = f"""⚠️ File State Change Detected

**File:** `{file_path}`
**Status:** {status.upper()}
**Git Says:** File has uncommitted changes since last commit

**Diff Summary:**
```
{diff_summary}
```

**Recommendation:**
- ✅ Re-read the file to see current state
- ✅ Use Read tool before {tool_name} to avoid conflicts

**Git Source of Truth:**
The file's current state may differ from what you have in context.
Git tracking shows external modifications.

**Example:**
```bash
# Check current state
git diff {file_path}

# See what changed
git log -1 --oneline -- {file_path}
```

**Note:** Continuing with your {tool_name} operation, but verify file state first!
"""

        # Log the detection
        print(f"DEBUG: Providing state sync feedback for {file_path}", file=sys.stderr)

        # IMPORTANT: Never block, always continue with feedback
        response = {
            "continue": True,
            "feedback": feedback,
            "suppressOutput": False  # Show feedback to Claude
        }

        print(json.dumps(response))

    except Exception as e:
        # Never fail the hook - always continue
        print(f"DEBUG: PreToolUse state sync error: {e}", file=sys.stderr)
        response = {"continue": True}
        print(json.dumps(response))


if __name__ == "__main__":
    main()
