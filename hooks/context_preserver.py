#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Enhanced Context Preservation Hook (PreCompact) with Checkpoint Pattern

Implements checkpoint pattern for long sessions:
1. Extracts COMPLETED plans to .plans/ (permanent storage)
2. Preserves IN-PROGRESS work to scratch_pad.md (ephemeral transfer)
3. Enables compact-after-plan workflow

Benefits:
- Each plan becomes a checkpoint (permanent)
- Compaction clears old discussion (reduces bloat)
- Working context stays focused on current plan
- Cumulative documentation without context pollution
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import yaml

# Import extraction functions from session_end_extractor
sys.path.insert(0, str(Path(__file__).parent))

# High-value patterns for in-progress work
HIGH_VALUE_PATTERNS = [
    r'## Architecture',
    r'## Implementation',
    r'## Task \d+:',
    r'## Solution:',
    r'```yaml',
    r'```python',
    r'Option \d+:',
    r'Let me design',
    r'Enhanced schema:',
    r'task-\d+\.md',
]

# Plan completion markers
PLAN_COMPLETION_MARKERS = [
    r'\*\*Type:\*\* (Design|Plan|Architecture)',
    r'\*\*Status:\*\* (Complete|Ready)',
    r'## Success Criteria',
    r'## Task Breakdown',
    r'Ready for: /ctx:plan',
    r'Ready for: /ctx:execute',
]

def read_full_transcript(transcript_path: str) -> List[dict]:
    """
    Read full conversation transcript.

    Args:
        transcript_path: Path to transcript JSONL file

    Returns:
        List of conversation entries
    """
    try:
        with open(transcript_path, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"DEBUG: Failed to read transcript: {e}", file=sys.stderr)
        return []

def extract_assistant_text(entry: dict) -> Optional[str]:
    """Extract text from assistant message entry."""
    if entry.get('type') != 'assistant':
        return None

    message = entry.get('message', {})
    if not isinstance(message, dict):
        return None

    content = message.get('content', [])

    # Handle both formats
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return ' '.join(
            block.get('text', '')
            for block in content
            if block.get('type') == 'text'
        )

    return None

def is_completed_plan(text: str) -> int:
    """
    Detect if text contains a COMPLETED plan.

    Returns count of completion markers (≥2 = completed plan)
    """
    if not text:
        return 0

    count = 0
    for pattern in PLAN_COMPLETION_MARKERS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)

    return count

def extract_plans_from_transcript(transcript: List[dict]) -> List[dict]:
    """
    Extract all completed plans from conversation.

    Args:
        transcript: Full conversation transcript

    Returns:
        List of {index, timestamp, content, completion_score} dicts
    """
    plans = []

    for i, entry in enumerate(transcript):
        text = extract_assistant_text(entry)
        if not text:
            continue

        completion_score = is_completed_plan(text)

        # Require ≥2 completion markers for a plan
        if completion_score >= 2:
            plans.append({
                'index': i,
                'timestamp': entry.get('timestamp', ''),
                'content': text,
                'completion_score': completion_score
            })

    return plans

def extract_yaml_blocks(content: str) -> List[dict]:
    """Extract and parse YAML blocks."""
    yaml_blocks = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)
    parsed = []

    for block in yaml_blocks:
        try:
            data = yaml.safe_load(block)
            if data:
                parsed.append(data)
        except yaml.YAMLError:
            continue

    return parsed

def extract_title(content: str) -> Optional[str]:
    """Extract title from markdown (# Title)."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None

def sanitize_topic(title: str) -> str:
    """Convert title to filesystem-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]

def save_plan_to_disk(project_root: Path, plan: dict, session_id: str) -> bool:
    """
    Save completed plan to .plans/ directory.

    Args:
        project_root: Project root directory
        plan: Plan dict with content
        session_id: Current session ID

    Returns:
        bool indicating success
    """
    try:
        content = plan['content']

        # Extract title and create topic slug
        title = extract_title(content) or 'untitled-plan'
        topic_slug = sanitize_topic(title)

        # Create .plans directory
        plans_dir = project_root / '.plans' / topic_slug
        plans_dir.mkdir(parents=True, exist_ok=True)

        # Write design.md
        design_file = plans_dir / 'design.md'
        with open(design_file, 'w') as f:
            f.write(content)

        print(f"DEBUG: ✅ Checkpoint: Saved plan to {design_file}", file=sys.stderr)

        # Extract and save tasks if present
        yaml_blocks = extract_yaml_blocks(content)
        task_count = 0

        for yaml_data in yaml_blocks:
            if 'tasks' in yaml_data and isinstance(yaml_data['tasks'], list):
                tasks_dir = plans_dir / 'tasks'
                tasks_dir.mkdir(exist_ok=True)

                for task in yaml_data['tasks']:
                    if not isinstance(task, dict):
                        continue

                    task_id = task.get('id', f'task-{task_count + 1}')
                    task_file = tasks_dir / f"{task_id}.md"

                    with open(task_file, 'w') as f:
                        # YAML frontmatter
                        f.write('---\n')
                        yaml.dump(task, f, default_flow_style=False, sort_keys=False)
                        f.write('---\n\n')

                        # Task body
                        title = task.get('title', 'Untitled')
                        f.write(f"# {task_id}: {title}\n\n")
                        f.write(task.get('description', '(To be filled in)\n'))

                    task_count += 1

        if task_count:
            print(f"DEBUG: ✅ Checkpoint: Saved {task_count} task files", file=sys.stderr)

        return True

    except Exception as e:
        print(f"DEBUG: Failed to save plan: {e}", file=sys.stderr)
        return False

def extract_last_message_for_scratch_pad(transcript_path: str) -> Optional[str]:
    """Extract last Claude message for scratch_pad."""
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'assistant':
                    message = entry.get('message', {})
                    if isinstance(message, dict):
                        content = message.get('content', [])
                        if isinstance(content, list):
                            text = ' '.join(
                                block.get('text', '')
                                for block in content
                                if block.get('type') == 'text'
                            )
                            return text if text.strip() else None
            except json.JSONDecodeError:
                continue

        return None

    except Exception as e:
        print(f"DEBUG: Failed to extract last message: {e}", file=sys.stderr)
        return None

def write_scratch_pad(project_root: Path, content: str, session_id: str):
    """Write in-progress work to scratch_pad.md."""
    scratch_pad = project_root / 'scratch_pad.md'

    with open(scratch_pad, 'w') as f:
        f.write(f"# In-Progress Context from Compaction\n\n")
        f.write(f"**Session ID:** {session_id}\n")
        f.write(f"**Preserved:** {datetime.now().isoformat()}\n")
        f.write(f"**Auto-extracted by:** PreCompact hook\n\n")
        f.write("---\n\n")
        f.write(content)

    print(f"DEBUG: ✅ Preserved in-progress work to scratch_pad.md", file=sys.stderr)

def main():
    """
    Enhanced PreCompact hook with checkpoint pattern.

    1. Extracts COMPLETED plans to .plans/ (checkpoints)
    2. Preserves IN-PROGRESS work to scratch_pad.md
    3. Enables compact-after-plan workflow
    """
    try:
        hook_data = json.loads(sys.stdin.read())

        transcript_path = hook_data.get('transcript_path', '')
        session_id = hook_data.get('session_id', 'unknown')
        trigger = hook_data.get('trigger', 'unknown')

        print(f"DEBUG: PreCompact checkpoint triggered ({trigger})", file=sys.stderr)

        if not transcript_path or not Path(transcript_path).exists():
            print("DEBUG: Transcript not found", file=sys.stderr)
            output = {"continue": True}
            print(json.dumps(output))
            sys.exit(0)

        # Find project root
        project_root = Path.cwd()
        transcript_dir = Path(transcript_path).parent
        temp_root = transcript_dir
        while temp_root.parent != temp_root:
            if (temp_root / '.git').exists() or (temp_root / 'pyproject.toml').exists():
                project_root = temp_root
                break
            temp_root = temp_root.parent

        print(f"DEBUG: Project root: {project_root}", file=sys.stderr)

        # Step 1: Extract COMPLETED plans (checkpoint pattern)
        print(f"DEBUG: Scanning for completed plans...", file=sys.stderr)
        transcript = read_full_transcript(transcript_path)
        completed_plans = extract_plans_from_transcript(transcript)

        print(f"DEBUG: Found {len(completed_plans)} completed plans", file=sys.stderr)

        plans_saved = 0
        for plan in completed_plans:
            if save_plan_to_disk(project_root, plan, session_id):
                plans_saved += 1

        if plans_saved:
            print(f"DEBUG: 🎯 Checkpoint: {plans_saved} completed plans saved to .plans/", file=sys.stderr)

        # Step 2: Preserve IN-PROGRESS work to scratch_pad.md
        last_message = extract_last_message_for_scratch_pad(transcript_path)

        if last_message:
            # Check if last message is in-progress work (not a completed plan)
            completion_score = is_completed_plan(last_message)

            if completion_score < 2:
                # In-progress work - save to scratch_pad
                pattern_count = len([p for p in HIGH_VALUE_PATTERNS
                                   if re.search(p, last_message, re.IGNORECASE)])

                if pattern_count >= 3:
                    write_scratch_pad(project_root, last_message, session_id)
                    print(f"DEBUG: ✅ Preserved in-progress work ({pattern_count} patterns)", file=sys.stderr)
            else:
                print(f"DEBUG: Last message is completed plan (already extracted)", file=sys.stderr)

        # Summary
        print(f"DEBUG: 📋 Checkpoint Summary:", file=sys.stderr)
        print(f"DEBUG:   Completed plans: {plans_saved} saved to .plans/", file=sys.stderr)
        print(f"DEBUG:   In-progress work: {'saved to scratch_pad.md' if last_message and completion_score < 2 else 'none'}", file=sys.stderr)

    except Exception as e:
        print(f"DEBUG: Checkpoint failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Always continue
    output = {"continue": True}
    print(json.dumps(output))
    sys.exit(0)

if __name__ == '__main__':
    main()
