#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Git Workflow Detector - PreToolUse Hook

Detects when Claude is about to use inefficient multi-tool git workflows
and suggests using optimized scripts instead.

Triggers:
- Multiple git commands in single Bash call
- Sequential git operations (add, commit, push)
- PR/merge workflows

Does NOT block - just provides helpful suggestions.
"""

import json
import sys
import re

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

def format_suggestion(suggestion: dict) -> str:
    """
    Format suggestion message for Claude.

    Args:
        suggestion: Suggestion dict from detect_git_workflow

    Returns:
        Formatted message
    """
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

        if is_workflow and suggestion:
            # Inject suggestion as additional context
            message = format_suggestion(suggestion)

            output = {
                'continue': True,
                'hookSpecificOutput': {
                    'hookEventName': 'PreToolUse',
                    'additionalContext': message
                }
            }

            print(f"DEBUG: Detected git workflow, suggesting {suggestion['script']}", file=sys.stderr)
            print(json.dumps(output))
        else:
            # Not a git workflow, continue normally
            output = {'continue': True}
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
