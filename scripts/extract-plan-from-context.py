#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Extract Plan from Conversation Transcript

Reads conversation transcript (JSONL) and extracts plans to modular files.

Can work in two modes:
1. As a hook - receives hook_data with transcript_path via stdin
2. As a CLI - receives transcript path as argument

Usage as hook:
  echo '{"transcript_path": "/path/to/transcript.jsonl"}' | uv run scripts/extract-plan-from-context.py

Usage as CLI:
  uv run scripts/extract-plan-from-context.py /path/to/transcript.jsonl

Usage with plan text (fallback):
  uv run scripts/extract-plan-from-context.py <<'PLAN'
  # Implementation Plan: ...
  PLAN
"""

import re
import sys
import yaml
import json
from pathlib import Path


def find_plan_in_transcript(transcript_path: str) -> str | None:
    """
    Read transcript JSONL file and find plan in conversation.

    Returns: Plan content as string, or None if not found
    """
    try:
        with open(transcript_path, 'r') as f:
            transcript = [json.loads(line) for line in f if line.strip()]

        print(f"DEBUG: Loaded {len(transcript)} conversation entries", file=sys.stderr)

        # Search for plan in assistant messages
        for entry in reversed(transcript):  # Start from most recent
            if entry.get("type") != "assistant":
                continue

            message = entry.get("message", {})
            if isinstance(message, dict):
                content = message.get("content", [])

                # Handle both formats
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = " ".join(
                        block.get("text", "")
                        for block in content
                        if block.get("type") == "text"
                    )
                else:
                    continue
            else:
                continue

            # Check for plan markers
            if "**Type:** Plan" in text and "## Plan Structure" in text:
                print(f"DEBUG: Found plan in conversation!", file=sys.stderr)
                return text

        print(f"DEBUG: No plan found in transcript", file=sys.stderr)
        return None

    except Exception as e:
        print(f"DEBUG: Error reading transcript: {e}", file=sys.stderr)
        return None


def extract_plan_yaml(content: str) -> dict | None:
    """Extract YAML block from ## Plan Structure section."""
    pattern = r'## Plan Structure\s*```yaml\s*\n(.*?)```'
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if not match:
        print("❌ Error: Could not find ## Plan Structure section", file=sys.stderr)
        return None

    yaml_text = match.group(1)

    try:
        plan_data = yaml.safe_load(yaml_text)
        return plan_data
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML in Plan Structure: {e}", file=sys.stderr)
        return None


def extract_tasks(content: str) -> list[dict]:
    """Extract all task sections from ## Task Details."""
    # Pattern: ### Task N: Name\n...```yaml\n...```\n...content
    pattern = r'### Task (\d+):\s*(.+?)\n(.*?)(?=###|## References|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    tasks = []
    for task_num, task_name, task_content in matches:
        # Extract YAML frontmatter from task content
        yaml_pattern = r'```yaml\s*\n(.*?)```'
        yaml_match = re.search(yaml_pattern, task_content, re.DOTALL)

        if not yaml_match:
            print(f"⚠️  Warning: No YAML frontmatter for task-{task_num}", file=sys.stderr)
            continue

        try:
            task_yaml = yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError as e:
            print(f"⚠️  Warning: Invalid YAML in task-{task_num}: {e}", file=sys.stderr)
            continue

        # Get remaining content after YAML block
        yaml_end = yaml_match.end()
        remaining_content = task_content[yaml_end:].strip()

        tasks.append({
            'num': task_num,
            'name': task_name.strip(),
            'yaml': task_yaml,
            'content': remaining_content
        })

    return tasks


def write_plan_files(plan_data: dict, tasks: list[dict], output_dir: str = ".parallel/plans"):
    """Write extracted plan to modular files."""
    plans_dir = Path(output_dir)
    plans_dir.mkdir(parents=True, exist_ok=True)

    # Write plan.yaml
    plan_file = plans_dir / "plan.yaml"
    with open(plan_file, 'w') as f:
        yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created {plan_file}", file=sys.stderr)

    # Write task files
    tasks_dir = plans_dir / "tasks"
    tasks_dir.mkdir(exist_ok=True)

    for task in tasks:
        task_id = task['yaml'].get('id', f"task-{task['num']}")
        task_file = tasks_dir / f"{task_id}.md"

        with open(task_file, 'w') as f:
            # Write YAML frontmatter
            f.write("---\n")
            yaml.dump(task['yaml'], f, default_flow_style=False, sort_keys=False)
            f.write("---\n\n")

            # Write task name
            f.write(f"# {task['name']}\n\n")

            # Write task content
            f.write(task['content'])
            f.write("\n")

        print(f"✅ Created {task_file}", file=sys.stderr)

    # Create helper directories
    (plans_dir / "templates").mkdir(exist_ok=True)
    (plans_dir / "scripts").mkdir(exist_ok=True)

    return len(tasks)


def main():
    """Main extraction entry point."""
    content = None

    # Mode detection
    if len(sys.argv) > 1:
        # Mode 1: CLI mode - transcript path as argument
        transcript_path = sys.argv[1]
        print(f"🔍 Reading transcript from: {transcript_path}", file=sys.stderr)
        content = find_plan_in_transcript(transcript_path)

        if not content:
            print("❌ Error: No plan found in transcript", file=sys.stderr)
            sys.exit(1)

    elif not sys.stdin.isatty():
        # Mode 2: Stdin mode - could be hook_data or plan text
        stdin_data = sys.stdin.read()

        if not stdin_data.strip():
            print("❌ Error: No data provided via stdin", file=sys.stderr)
            sys.exit(1)

        # Try to parse as JSON (hook mode)
        try:
            hook_data = json.loads(stdin_data)
            transcript_path = hook_data.get("transcript_path")

            if transcript_path:
                print(f"🔍 Hook mode: Reading transcript from: {transcript_path}", file=sys.stderr)
                content = find_plan_in_transcript(transcript_path)
            else:
                # JSON but no transcript_path - treat as plan text
                content = stdin_data

        except json.JSONDecodeError:
            # Not JSON - treat as plan text directly
            content = stdin_data

    else:
        print("❌ Error: No input provided", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  As hook:  echo '{\"transcript_path\": \"...\"}' | uv run extract-plan-from-context.py", file=sys.stderr)
        print("  As CLI:   uv run extract-plan-from-context.py /path/to/transcript.jsonl", file=sys.stderr)
        print("  As pipe:  cat plan.txt | uv run extract-plan-from-context.py", file=sys.stderr)
        sys.exit(1)

    if not content:
        print("❌ Error: Could not get plan content", file=sys.stderr)
        sys.exit(1)

    # Validate plan markers
    if "**Type:** Plan" not in content:
        print("❌ Error: Content doesn't appear to be an extraction-optimized plan", file=sys.stderr)
        print("Missing marker: **Type:** Plan", file=sys.stderr)
        sys.exit(1)

    print("🔍 Extracting plan from content...", file=sys.stderr)

    # Extract plan YAML
    plan_data = extract_plan_yaml(content)
    if not plan_data:
        sys.exit(1)

    print(f"✅ Parsed plan structure", file=sys.stderr)

    # Extract tasks
    tasks = extract_tasks(content)
    if not tasks:
        print("❌ Error: No tasks found in content", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Parsed {len(tasks)} tasks", file=sys.stderr)

    # Write files
    task_count = write_plan_files(plan_data, tasks)

    print(f"\n✅ Extraction complete!", file=sys.stderr)
    print(f"Created:", file=sys.stderr)
    print(f"  - .parallel/plans/plan.yaml", file=sys.stderr)
    print(f"  - {task_count} task files in .parallel/plans/tasks/", file=sys.stderr)
    print(f"  - Helper directories (templates, scripts)", file=sys.stderr)
    print(f"\n📖 Review: cat .parallel/plans/plan.yaml", file=sys.stderr)
    print(f"🚀 Execute: /ctx:execute", file=sys.stderr)


if __name__ == "__main__":
    main()
