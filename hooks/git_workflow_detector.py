#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Git Workflow Detector - PreToolUse Hook with Preference Management

Detects when Claude is about to use inefficient multi-tool git workflows
and suggests using optimized scripts instead.

Features:
- First detection: Uses AskUserQuestion for user choice
- User can set preference: "Always use scripts"
- Subsequent detections: Auto-use based on preference
- Subagents: Always use scripts (no prompting)

Triggers:
- Multiple git commands in single Bash call
- Sequential git operations (add, commit, push)
- PR/merge workflows

Does NOT block - provides suggestions only.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Preference storage
PREFERENCE_FILE = Path.home() / ".claude" / "plugins" / "contextune" / "data" / "git_workflow_preferences.json"

# Script mappings
SCRIPT_SUGGESTIONS = {
    'commit_and_push': {
        'patterns': [
            r'git add.*git commit.*git push',
            r'git commit.*git push',
        ],
        'script': './scripts/commit_and_push.sh',
        'usage': './scripts/commit_and_push.sh "." "message" "branch"',
        'savings': '90-97% tokens, $0.035-0.084 cost reduction'
    },
    'create_pr': {
        'patterns': [
            r'gh pr create',
            r'git push.*gh pr',
        ],
        'script': './scripts/create_pr.sh',
        'usage': './scripts/create_pr.sh "title" "body" "base" "head"',
        'savings': '90-95% tokens, $0.030-0.080 cost reduction'
    },
    'merge_workflow': {
        'patterns': [
            r'git merge.*git push.*git branch -d',
            r'git merge.*git branch.*delete',
        ],
        'script': './scripts/merge_and_cleanup.sh',
        'usage': './scripts/merge_and_cleanup.sh "branch" "into_branch"',
        'savings': '90-95% tokens, $0.030-0.080 cost reduction'
    }
}

def read_preference() -> dict:
    """
    Read user's git workflow preference.

    Returns:
        dict with 'auto_use_scripts' (bool or None) and 'set_at' timestamp
    """
    if not PREFERENCE_FILE.exists():
        return {'auto_use_scripts': None, 'set_at': None}

    try:
        with open(PREFERENCE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {'auto_use_scripts': None, 'set_at': None}

def write_preference(auto_use_scripts: bool):
    """
    Write user's git workflow preference.

    Args:
        auto_use_scripts: Whether to automatically use scripts
    """
    PREFERENCE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'auto_use_scripts': auto_use_scripts,
        'set_at': datetime.now().isoformat()
    }

    with open(PREFERENCE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def detect_git_workflow(command: str) -> tuple[bool, dict]:
    """
    Detect if command contains multi-step git workflow.

    Args:
        command: Bash command to analyze

    Returns:
        (is_workflow: bool, suggestion: dict)
    """
    if 'git ' not in command:
        return False, {}

    # Check each workflow pattern
    for workflow_name, workflow_info in SCRIPT_SUGGESTIONS.items():
        for pattern in workflow_info['patterns']:
            if re.search(pattern, command, re.IGNORECASE):
                return True, {
                    'workflow': workflow_name,
                    'script': workflow_info['script'],
                    'usage': workflow_info['usage'],
                    'savings': workflow_info['savings']
                }

    # Check for multiple git commands (&&, ;, or newlines)
    git_command_count = len(re.findall(r'\bgit\s+\w+', command))
    if git_command_count >= 3:
        return True, {
            'workflow': 'multiple_git_commands',
            'script': './scripts/smart_execute.sh',
            'usage': 'Consider consolidating into a single script',
            'savings': 'Reduces tool call overhead (~90% token reduction)'
        }

    return False, {}

def format_auto_use_message(suggestion: dict) -> str:
    """Format message when auto-using scripts (preference set)."""
    return f"""
✨ AUTO-OPTIMIZATION ACTIVE

Using optimized script: {suggestion['script']}
(Your preference is set to auto-use scripts)

Benefits:
  • {suggestion['savings']}
  • Automatic error recovery (Haiku/Copilot)
  • Minimal session context impact

Change preference: Delete {PREFERENCE_FILE}
""".strip()

def format_ask_user_instruction(suggestion: dict) -> str:
    """Format instruction for Claude to use AskUserQuestion."""
    return f"""
🎯 GIT WORKFLOW OPTIMIZATION DETECTED

Use AskUserQuestion tool with these settings:

Question: "Git workflow optimization available - how would you like to proceed?"

Header: "Optimize"

Options:
1. Use optimized script
   Description: "Use {suggestion['script']} - {suggestion['savings']}, automatic error recovery"

2. Use standard approach
   Description: "Proceed with multiple Bash tool calls (current method)"

3. Always use scripts
   Description: "Set preference to auto-use scripts for all git workflows this session"

Based on user selection:
- Option 1: Execute {suggestion['script']} (one-time)
- Option 2: Continue with Bash as planned
- Option 3: Save preference, then execute {suggestion['script']}

To save preference (Option 3), create file at:
{PREFERENCE_FILE}
With content: {{"auto_use_scripts": true, "set_at": "{datetime.now().isoformat()}"}}
""".strip()

def format_suggestion_only(suggestion: dict) -> str:
    """Format simple suggestion when no preference system available."""
    return f"""
💡 Git Workflow Optimization Available

Detected: Multi-step git operation ({suggestion['workflow']})

Optimized alternative:
  {suggestion['script']}

Usage:
  {suggestion['usage']}

Benefits:
  • {suggestion['savings']}
  • Automatic error recovery (Haiku/Copilot cascade)
  • Minimal session context impact

You can use the optimized script or proceed with current approach.
""".strip()

def main():
    """PreToolUse hook entry point."""

    try:
        hook_data = json.loads(sys.stdin.read())

        tool = hook_data.get('tool', {})
        tool_name = tool.get('name', '')
        tool_params = tool.get('parameters', {})

        # Only check Bash tool
        if tool_name != 'Bash':
            output = {'continue': True}
            print(json.dumps(output))
            sys.exit(0)

        command = tool_params.get('command', '')

        # Detect git workflows
        is_workflow, suggestion = detect_git_workflow(command)

        if not is_workflow or not suggestion:
            # Not a git workflow, continue normally
            output = {'continue': True}
            print(json.dumps(output))
            sys.exit(0)

        # Workflow detected - check preference
        preference = read_preference()
        auto_use = preference.get('auto_use_scripts')

        if auto_use is True:
            # User prefers auto-use - suggest directly
            message = format_auto_use_message(suggestion)
            print(f"DEBUG: Auto-using scripts (preference set)", file=sys.stderr)

        elif auto_use is False:
            # User prefers Bash - don't suggest
            print(f"DEBUG: User prefers Bash approach (preference set)", file=sys.stderr)
            output = {'continue': True}
            print(json.dumps(output))
            sys.exit(0)

        else:
            # No preference - ask user with AskUserQuestion
            message = format_ask_user_instruction(suggestion)
            print(f"DEBUG: First detection, will prompt user via AskUserQuestion", file=sys.stderr)

        # Inject suggestion/instruction
        output = {
            'continue': True,
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'additionalContext': message
            }
        }

        print(json.dumps(output))

    except Exception as e:
        print(f"DEBUG: Git workflow detector error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

        # Always continue (don't block tools)
        output = {'continue': True}
        print(json.dumps(output))

    sys.exit(0)

if __name__ == '__main__':
    main()
