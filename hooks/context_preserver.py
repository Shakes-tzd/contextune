#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Automated Context Preservation Hook (PreCompact)

Automatically extracts working context from conversation transcript
before compaction and writes to scratch_pad.md for next session.

Eliminates manual copying of Claude's last message.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# High-value patterns indicating working context worth preserving
HIGH_VALUE_PATTERNS = [
    r'## Architecture',
    r'## Implementation',
    r'## Task \d+:',
    r'## Solution:',
    r'```yaml',
    r'```python',
    r'decision-sync\.py',
    r'decision-link\.py',
    r'Option \d+:',
    r'Let me design',
    r'Enhanced schema:',
    r'Auto-population',
    r'file_path.*\.md',
    r'task-\d+\.md',
    r'Updated plan:',
    r'### \d+\.',  # Numbered sections
]

def extract_last_claude_message(transcript_path: str) -> Optional[str]:
    """
    Extract the last message from Claude in the conversation.

    Args:
        transcript_path: Path to conversation transcript file

    Returns:
        Last Claude message content or None if not found
    """
    try:
        with open(transcript_path, 'r') as f:
            content = f.read()

        # Claude Code transcript format - try JSON lines first
        lines = content.strip().split('\n')
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('role') == 'assistant':
                    return entry.get('content', '')
            except json.JSONDecodeError:
                continue

        # Fallback: look for last message with "assistant:" prefix
        assistant_messages = re.findall(r'assistant:\s*(.*?)(?=\nuser:|$)', content, re.DOTALL)
        if assistant_messages:
            return assistant_messages[-1].strip()

        return None

    except Exception as e:
        print(f"DEBUG: Failed to read transcript: {e}", file=sys.stderr)
        return None

def detect_working_context(message: str) -> int:
    """
    Count high-value patterns in message to determine if it contains
    working context worth preserving.

    Args:
        message: Claude's message content

    Returns:
        Number of high-value patterns detected
    """
    if not message:
        return 0

    count = 0
    for pattern in HIGH_VALUE_PATTERNS:
        matches = re.findall(pattern, message, re.IGNORECASE)
        count += len(matches)

    return count

def extract_structured_content(message: str) -> dict:
    """
    Extract structured content sections from message.

    Args:
        message: Claude's message content

    Returns:
        Dict with extracted sections (yaml_blocks, code_blocks, sections)
    """
    result = {
        'yaml_blocks': [],
        'code_blocks': [],
        'sections': [],
        'full_message': message
    }

    # Extract YAML blocks
    yaml_blocks = re.findall(r'```yaml\n(.*?)```', message, re.DOTALL)
    result['yaml_blocks'] = yaml_blocks

    # Extract code blocks
    code_blocks = re.findall(r'```(?:python|bash|javascript)\n(.*?)```', message, re.DOTALL)
    result['code_blocks'] = code_blocks

    # Extract major sections (## headings)
    sections = re.findall(r'##\s+(.+?)(?=\n##|\Z)', message, re.DOTALL)
    result['sections'] = sections

    return result

def write_scratch_pad(project_root: Path, content: dict, session_id: str):
    """
    Write extracted content to scratch_pad.md in project root.

    Args:
        project_root: Project root directory
        content: Extracted structured content
        session_id: Current session ID
    """
    scratch_pad = project_root / 'scratch_pad.md'

    with open(scratch_pad, 'w') as f:
        f.write(f"# Context Preserved from Compaction\n\n")
        f.write(f"**Session ID:** {session_id}\n")
        f.write(f"**Preserved:** {datetime.now().isoformat()}\n")
        f.write(f"**Auto-extracted by:** PreCompact hook\n\n")
        f.write("---\n\n")

        # Write full message
        f.write("## Last Claude Message (Full Context)\n\n")
        f.write(content['full_message'])
        f.write("\n\n---\n\n")

        # Write extracted structured content
        if content['yaml_blocks']:
            f.write("## Extracted YAML Blocks\n\n")
            for i, block in enumerate(content['yaml_blocks'], 1):
                f.write(f"### YAML Block {i}\n\n")
                f.write(f"```yaml\n{block}```\n\n")

        if content['code_blocks']:
            f.write("## Extracted Code Blocks\n\n")
            for i, block in enumerate(content['code_blocks'], 1):
                f.write(f"### Code Block {i}\n\n")
                f.write(f"```\n{block}```\n\n")

    print(f"DEBUG: ✅ Preserved context to {scratch_pad}", file=sys.stderr)

def main():
    """
    PreCompact hook entry point.

    Reads conversation transcript, extracts last Claude message,
    detects working context, and writes to scratch_pad.md if valuable.
    """
    try:
        # Read hook data
        hook_data = json.loads(sys.stdin.read())

        transcript_path = hook_data.get('transcript_path', '')
        session_id = hook_data.get('session_id', 'unknown')
        trigger = hook_data.get('trigger', 'unknown')

        print(f"DEBUG: PreCompact triggered ({trigger})", file=sys.stderr)
        print(f"DEBUG: Transcript path: {transcript_path}", file=sys.stderr)

        # Extract last Claude message
        last_message = extract_last_claude_message(transcript_path)

        if not last_message:
            print("DEBUG: No Claude message found in transcript", file=sys.stderr)
            return

        # Detect if message contains working context
        pattern_count = detect_working_context(last_message)

        print(f"DEBUG: Detected {pattern_count} high-value patterns", file=sys.stderr)

        # Threshold: preserve if ≥3 high-value patterns
        if pattern_count >= 3:
            print("DEBUG: Working context detected, preserving...", file=sys.stderr)

            # Extract structured content
            structured = extract_structured_content(last_message)

            # Find project root (walk up from transcript location)
            project_root = Path(transcript_path).parent
            while project_root.parent != project_root:
                if (project_root / '.git').exists() or (project_root / 'pyproject.toml').exists():
                    break
                project_root = project_root.parent

            # Write to scratch_pad.md
            write_scratch_pad(project_root, structured, session_id)

            print(f"DEBUG: 🎯 Context preserved ({len(last_message)} chars, {pattern_count} patterns)", file=sys.stderr)
        else:
            print(f"DEBUG: No significant working context ({pattern_count} patterns < 3 threshold)", file=sys.stderr)

    except Exception as e:
        print(f"DEBUG: Context preservation failed: {e}", file=sys.stderr)

    # Always continue (don't block compaction)
    output = {"continue": True}
    print(json.dumps(output))
    sys.exit(0)

if __name__ == '__main__':
    main()
