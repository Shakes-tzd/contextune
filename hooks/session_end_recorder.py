#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
SessionEnd Recorder - Capture Session Metadata for Next Session

Records lightweight session metadata at session end:
- Session ID and timestamp
- Last commit hash (for git diff baseline)
- Current branch
- Files worked on
- Brief summary

**Token Overhead:** ~100 tokens (write only, no injection)
**Blocking:** No

Hook Protocol:
- Input: JSON via stdin with session data
- Output: JSON via stdout
- IMPORTANT: Never blocks (always {"continue": true})
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import yaml


def get_current_commit_hash() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"DEBUG: Failed to get commit hash: {e}", file=sys.stderr)
        return "unknown"


def get_current_branch() -> str:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"DEBUG: Failed to get branch: {e}", file=sys.stderr)
        return "unknown"


def get_files_changed_in_session(start_hash: str) -> list[str]:
    """Get files changed between start_hash and HEAD."""
    try:
        # Get files changed since session start
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{start_hash}..HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        # Also include uncommitted changes
        result2 = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        for line in result2.stdout.split("\n"):
            if line.strip():
                # Extract filename (format: "M  file.py")
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    files.append(parts[1])

        # Deduplicate
        return list(set(files))

    except Exception as e:
        print(f"DEBUG: Failed to get changed files: {e}", file=sys.stderr)
        return []


def main():
    """SessionEnd recorder entry point."""
    try:
        # Read hook data
        hook_data = json.loads(sys.stdin.read())

        session_id = hook_data.get("session_id", "unknown")

        print(f"DEBUG: SessionEnd recorder triggered", file=sys.stderr)
        print(f"DEBUG: Session: {session_id}", file=sys.stderr)

        # Get git state
        commit_hash = get_current_commit_hash()
        branch = get_current_branch()

        # Load previous session data to calculate files worked on
        cache_dir = Path.home() / ".claude" / "plugins" / "contextune" / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        last_session_file = cache_dir / "last_session.yaml"

        # Get session start commit hash (if tracked)
        session_start_hash = commit_hash
        if last_session_file.exists():
            try:
                with open(last_session_file) as f:
                    prev_session = yaml.safe_load(f) or {}
                    session_start_hash = prev_session.get("last_commit", commit_hash)
            except:
                pass

        # Get files changed during this session
        files_worked_on = get_files_changed_in_session(session_start_hash)

        # Create session record
        session_record = {
            "session_id": session_id,
            "ended_at": datetime.now().isoformat() + "Z",
            "last_commit": commit_hash,
            "branch": branch,
            "files_worked_on": files_worked_on[:20],  # Limit to 20 files
            "file_count": len(files_worked_on),
        }

        # Write to cache
        with open(last_session_file, "w") as f:
            yaml.dump(session_record, f, default_flow_style=False)

        print(
            f"DEBUG: ✅ Recorded session metadata ({len(files_worked_on)} files)",
            file=sys.stderr,
        )

    except Exception as e:
        print(f"DEBUG: SessionEnd recorder error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)

    # Always continue (don't block session end)
    response = {"continue": True}
    print(json.dumps(response))


if __name__ == "__main__":
    main()
