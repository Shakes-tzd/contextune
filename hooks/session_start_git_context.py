#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0"
# ]
# ///
"""
SessionStart Git Context Injector

Injects differential git context at session start:
- Commits since last session
- Files changed since last session
- Current git status
- Branch information

Token Overhead: ~1-2K tokens (differential only, not full history)
Blocking: No
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


def load_last_session() -> Optional[dict]:
    """Load last session metadata from cache."""
    try:
        cache_dir = Path.home() / ".claude" / "plugins" / "contextune" / ".cache"
        last_session_file = cache_dir / "last_session.yaml"

        if not last_session_file.exists():
            return None

        with open(last_session_file, 'r') as f:
            return yaml.safe_load(f)

    except Exception as error:
        print(f"DEBUG: Failed to load last session: {error}", file=sys.stderr)
        return None


def get_commits_since_last_session(last_commit: str, limit: int = 10) -> list[str]:
    """Get commits since last session."""
    try:
        cmd = f"git log --oneline {last_commit}..HEAD -n {limit}"
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0:
            return []

        commits = [line for line in result.stdout.strip().split('\n') if line]
        return commits

    except Exception as error:
        print(f"DEBUG: Failed to get commits: {error}", file=sys.stderr)
        return []


def get_files_changed(last_commit: str) -> list[dict]:
    """Get files changed since last session."""
    try:
        cmd = f"git diff --name-status {last_commit}..HEAD"
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0:
            return []

        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) >= 2:
                status = parts[0]
                file = parts[1]

                # Decode status
                if status == 'A':
                    change_type = 'added'
                elif status == 'D':
                    change_type = 'deleted'
                elif status == 'M':
                    change_type = 'modified'
                elif status.startswith('R'):
                    change_type = 'renamed'
                else:
                    change_type = 'modified'

                changes.append({'file': file, 'type': change_type, 'status': status})

        return changes

    except Exception as error:
        print(f"DEBUG: Failed to get file changes: {error}", file=sys.stderr)
        return []


def get_diff_stats(last_commit: str) -> str:
    """Get diff statistics."""
    try:
        cmd = f"git diff --shortstat {last_commit}..HEAD"
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.stdout.strip() if result.returncode == 0 else 'Unable to calculate diff stats'

    except Exception:
        return 'Unable to calculate diff stats'


def get_current_status() -> dict:
    """Get current git status."""
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            timeout=1
        )

        if result.returncode != 0:
            return {'clean': True, 'uncommitted': 0}

        lines = [line for line in result.stdout.strip().split('\n') if line]

        if not lines:
            return {'clean': True, 'uncommitted': 0}

        return {
            'clean': False,
            'uncommitted': len(lines),
            'files': lines[:5]
        }

    except Exception:
        return {'clean': True, 'uncommitted': 0}


def get_time_since(timestamp: str) -> str:
    """Calculate time since last session."""
    try:
        last_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(last_time.tzinfo) if last_time.tzinfo else datetime.now()
        diff = now - last_time

        minutes = int(diff.total_seconds() / 60)
        hours = minutes // 60
        days = hours // 24

        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        return 'just now'

    except Exception:
        return 'recently'


def generate_context_summary(last_session: dict) -> str:
    """Generate context summary."""
    commits = get_commits_since_last_session(last_session['last_commit'])
    files_changed = get_files_changed(last_session['last_commit'])
    diff_stats = get_diff_stats(last_session['last_commit'])
    current_status = get_current_status()
    time_since = get_time_since(last_session['ended_at'])

    # Build summary
    summary = f"📋 Git Context Since Last Session ({time_since})\n\n"

    # Commit activity
    if commits:
        summary += "**Git Activity:**\n"
        summary += f"- {len(commits)} new commit{'s' if len(commits) > 1 else ''}\n"
        summary += f"- {diff_stats}\n"
        summary += f"- Branch: {last_session['branch']}\n\n"

        summary += "**Recent Commits:**\n"
        for commit in commits[:5]:
            summary += f"  {commit}\n"

        if len(commits) > 5:
            summary += f"  ... and {len(commits) - 5} more\n"
        summary += '\n'
    else:
        summary += "**Git Activity:** No commits since last session\n\n"

    # File changes
    if files_changed:
        summary += f"**Files Changed ({len(files_changed)} total):**\n"

        by_type = {'added': [], 'modified': [], 'deleted': [], 'renamed': []}
        for change in files_changed:
            by_type.setdefault(change['type'], []).append(change['file'])

        if by_type['added']:
            summary += f"  Added ({len(by_type['added'])}):\n"
            for f in by_type['added'][:3]:
                summary += f"    - {f}\n"
            if len(by_type['added']) > 3:
                summary += f"    ... and {len(by_type['added']) - 3} more\n"

        if by_type['modified']:
            summary += f"  Modified ({len(by_type['modified'])}):\n"
            for f in by_type['modified'][:3]:
                summary += f"    - {f}\n"
            if len(by_type['modified']) > 3:
                summary += f"    ... and {len(by_type['modified']) - 3} more\n"

        if by_type['deleted']:
            summary += f"  Deleted ({len(by_type['deleted'])}):\n"
            for f in by_type['deleted'][:3]:
                summary += f"    - {f}\n"

        summary += '\n'

    # Current working directory status
    if not current_status['clean']:
        summary += "**Current Status:**\n"
        summary += f"- {current_status['uncommitted']} uncommitted change{'s' if current_status['uncommitted'] > 1 else ''}\n"

        if current_status.get('files'):
            summary += "\n**Uncommitted:**\n"
            for file in current_status['files']:
                summary += f"  {file}\n"
        summary += '\n'
    else:
        summary += "**Current Status:** Working directory clean ✅\n\n"

    # Last session context
    if last_session.get('files_worked_on'):
        summary += "**Last Session Work:**\n"
        file_count = last_session.get('file_count', len(last_session['files_worked_on']))
        summary += f"- Worked on {file_count} file{'s' if file_count > 1 else ''}\n"

        if len(last_session['files_worked_on']) <= 5:
            for f in last_session['files_worked_on']:
                summary += f"  - {f}\n"
        else:
            for f in last_session['files_worked_on'][:3]:
                summary += f"  - {f}\n"
            summary += f"  ... and {len(last_session['files_worked_on']) - 3} more\n"
        summary += '\n'

    summary += "---\n\n"
    summary += "**Ready to continue!** Git is synced and tracking all changes.\n"

    return summary


def main():
    """Main hook entry point."""
    try:
        # Read stdin
        hook_data = json.load(sys.stdin)

        print("DEBUG: SessionStart git context injector triggered", file=sys.stderr)

        # Load last session
        last_session = load_last_session()

        if not last_session:
            print("DEBUG: No previous session found, skipping git context", file=sys.stderr)
            # First session or cache cleared
            response = {'continue': True}
            print(json.dumps(response))
            return

        print(f"DEBUG: Last session: {last_session.get('session_id')}", file=sys.stderr)
        print(f"DEBUG: Last commit: {last_session.get('last_commit')}", file=sys.stderr)

        # Generate context summary
        summary = generate_context_summary(last_session)

        print(f"DEBUG: Generated context summary ({len(summary)} chars)", file=sys.stderr)

        # Inject context
        response = {
            'continue': True,
            'additionalContext': summary,
            'suppressOutput': False
        }

        print(json.dumps(response))

    except Exception as error:
        print(f"DEBUG: SessionStart error: {error}", file=sys.stderr)
        # Never block - always continue
        response = {'continue': True}
        print(json.dumps(response))


if __name__ == '__main__':
    main()
