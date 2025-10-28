#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
SessionEnd Extractor - Extract completed work to structured files

Runs when session ends (user quits, closes tab, session timeout).
Scans full conversation transcript and extracts:
  - Design proposals → .plans/[topic]/design.md
  - Task breakdowns → .plans/[topic]/tasks/task-*.md
  - Decisions → decisions.yaml (append)
  - Research → decisions.yaml (append)

Zero conversation overhead - runs after session ends.

Leverages extraction-optimized output style for reliable parsing.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml


def extract_designs(transcript: list[dict]) -> list[dict]:
    """
    Find all design proposals in conversation.

    Detection patterns (from extraction-optimized style):
    - **Type:** Design
    - ## Architecture
    - ## Task Breakdown
    - Multiple YAML blocks
    """
    designs = []

    for i, entry in enumerate(transcript):
        if entry.get("type") != "assistant":
            continue

        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            # Handle both old format (string) and new format (list)
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                # Extract text from content blocks
                text = " ".join(
                    block.get("text", "")
                    for block in content
                    if block.get("type") == "text"
                )
            else:
                continue
        else:
            continue

        # Detect extraction-optimized design patterns
        patterns = [
            r"\*\*Type:\*\* Design",
            r"## Architecture",
            r"## Task Breakdown",
            r"```yaml\n.*?architecture:",
            r"```yaml\n.*?tasks:",
            r"\*\*Status:\*\* (Complete|Draft)",
            r"\*\*Estimated Tokens:\*\*",
        ]

        pattern_count = sum(
            len(re.findall(p, text, re.IGNORECASE | re.DOTALL)) for p in patterns
        )

        # Require at least 3 patterns for design detection
        if pattern_count >= 3:
            designs.append(
                {
                    "index": i,
                    "timestamp": entry.get("timestamp", ""),
                    "content": text,
                    "pattern_count": pattern_count,
                }
            )

    return designs


def extract_plans(transcript: list[dict]) -> list[dict]:
    """
    Find all parallel development plans in conversation.

    Detection patterns (from extraction-optimized style):
    - **Type:** Plan
    - ## Plan Structure
    - YAML block with metadata: and tasks:
    - ## Task Details
    """
    plans = []

    for i, entry in enumerate(transcript):
        if entry.get("type") != "assistant":
            continue

        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            # Handle both old format (string) and new format (list)
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                # Extract text from content blocks
                text = " ".join(
                    block.get("text", "")
                    for block in content
                    if block.get("type") == "text"
                )
            else:
                continue
        else:
            continue

        # Detect extraction-optimized plan patterns
        patterns = [
            r"\*\*Type:\*\* Plan",
            r"## Plan Structure",
            r"## Task Details",
            r"```yaml\n.*?metadata:",
            r"```yaml\n.*?tasks:",
            r"\*\*Status:\*\* (Ready|Draft)",
        ]

        pattern_count = sum(
            len(re.findall(p, text, re.IGNORECASE | re.DOTALL)) for p in patterns
        )

        # Require at least 3 patterns for plan detection
        if pattern_count >= 3:
            plans.append(
                {
                    "index": i,
                    "timestamp": entry.get("timestamp", ""),
                    "content": text,
                    "pattern_count": pattern_count,
                }
            )

    return plans


def extract_yaml_blocks(content: str) -> list[dict]:
    """
    Extract YAML blocks from markdown content.

    Expects: ```yaml\n...\n```
    """
    yaml_blocks = re.findall(r"```yaml\n(.*?)```", content, re.DOTALL)
    parsed = []

    for block in yaml_blocks:
        try:
            data = yaml.safe_load(block)
            if data:  # Skip empty blocks
                parsed.append(data)
        except yaml.YAMLError as e:
            print(f"DEBUG: Failed to parse YAML block: {e}", file=sys.stderr)
            continue

    return parsed


def extract_title(content: str) -> Optional[str]:
    """
    Extract title from markdown.

    Pattern: # [Title] at start of content
    """
    match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def extract_metadata(content: str) -> dict:
    """
    Extract metadata from extraction-optimized format.

    Patterns:
    - **Type:** Design
    - **Status:** Complete
    - **Estimated Tokens:** 45000
    """
    metadata = {}

    type_match = re.search(r"\*\*Type:\*\*\s+(.+?)(?:\n|\|)", content)
    if type_match:
        metadata["type"] = type_match.group(1).strip()

    status_match = re.search(r"\*\*Status:\*\*\s+(.+?)(?:\n|\|)", content)
    if status_match:
        metadata["status"] = status_match.group(1).strip()

    tokens_match = re.search(r"\*\*Estimated Tokens:\*\*\s+([\d,]+)", content)
    if tokens_match:
        tokens_str = tokens_match.group(1).replace(",", "")
        metadata["estimated_tokens"] = int(tokens_str)

    return metadata


def sanitize_topic(title: str) -> str:
    """Convert title to filesystem-safe slug."""
    # Remove special chars, convert to lowercase, replace spaces with hyphens
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug[:50]  # Limit length


def write_design_files(project_root: Path, designs: list[dict], session_id: str) -> int:
    """
    Write extracted designs to .plans/ directory.

    Returns: Number of designs written
    """
    if not designs:
        return 0

    # Use most comprehensive design (highest pattern count)
    best_design = max(designs, key=lambda d: d["pattern_count"])
    content = best_design["content"]

    # Extract metadata
    title = extract_title(content) or "untitled-design"
    metadata = extract_metadata(content)
    topic_slug = sanitize_topic(title)

    # Create .plans directory structure
    plans_dir = project_root / ".plans" / topic_slug
    plans_dir.mkdir(parents=True, exist_ok=True)

    # Write design.md
    design_file = plans_dir / "design.md"
    with open(design_file, "w") as f:
        f.write(content)

    print(f"DEBUG: ✅ Wrote design to {design_file}", file=sys.stderr)

    # Extract and write task files
    task_count = write_task_files(plans_dir, content)

    return 1


def write_task_files(plans_dir: Path, content: str) -> int:
    """
    Extract tasks from YAML blocks and write individual task files.

    Returns: Number of task files written
    """
    yaml_blocks = extract_yaml_blocks(content)
    task_count = 0

    for yaml_data in yaml_blocks:
        if "tasks" in yaml_data:
            tasks_dir = plans_dir / "tasks"
            tasks_dir.mkdir(exist_ok=True)

            tasks_list = yaml_data["tasks"]
            if not isinstance(tasks_list, list):
                continue

            for task in tasks_list:
                if not isinstance(task, dict):
                    continue

                task_id = task.get("id", f"task-{task_count + 1}")
                task_file = tasks_dir / f"{task_id}.md"

                with open(task_file, "w") as f:
                    # Write YAML frontmatter
                    f.write("---\n")
                    yaml.dump(task, f, default_flow_style=False, sort_keys=False)
                    f.write("---\n\n")

                    # Write task details
                    title = task.get("title", "Untitled Task")
                    f.write(f"# {task_id}: {title}\n\n")

                    f.write("## Description\n\n")
                    f.write(task.get("description", "(To be filled in)\n\n"))

                    # Files section
                    files_created = task.get("files_created", [])
                    files_modified = task.get("files_modified", [])

                    if files_created or files_modified:
                        f.write("## Files\n\n")

                        if files_created:
                            f.write("**Created:**\n")
                            for file_info in files_created:
                                if isinstance(file_info, dict):
                                    path = file_info.get("path", "")
                                    purpose = file_info.get("purpose", "")
                                    f.write(f"- `{path}` - {purpose}\n")

                        if files_modified:
                            f.write("\n**Modified:**\n")
                            for file_info in files_modified:
                                if isinstance(file_info, dict):
                                    path = file_info.get("path", "")
                                    changes = file_info.get("changes", "")
                                    f.write(f"- `{path}` - {changes}\n")

                    # Validation section
                    validation = task.get("validation", [])
                    if validation:
                        f.write("\n## Validation Checklist\n\n")
                        for item in validation:
                            f.write(f"- [ ] {item}\n")

                task_count += 1

    if task_count:
        print(f"DEBUG: ✅ Wrote {task_count} task files", file=sys.stderr)

    return task_count


def write_plan_files(project_root: Path, plans: list[dict], session_id: str) -> int:
    """
    Write extracted plans to .parallel/plans/ directory.

    Returns: Number of plans written
    """
    if not plans:
        return 0

    # Use most comprehensive plan (highest pattern count)
    best_plan = max(plans, key=lambda p: p["pattern_count"])
    content = best_plan["content"]

    # Extract plan YAML from ## Plan Structure section
    plan_yaml_match = re.search(
        r"## Plan Structure\s*```yaml\n(.*?)```", content, re.DOTALL | re.IGNORECASE
    )
    if not plan_yaml_match:
        print("DEBUG: Could not find Plan Structure YAML block", file=sys.stderr)
        return 0

    try:
        plan_data = yaml.safe_load(plan_yaml_match.group(1))
    except yaml.YAMLError as e:
        print(f"DEBUG: Failed to parse plan YAML: {e}", file=sys.stderr)
        return 0

    # Extract plan name for directory
    plan_name = plan_data.get("metadata", {}).get("name", "untitled-plan")
    plan_slug = sanitize_topic(plan_name)

    # Create .parallel/plans directory
    plans_dir = project_root / ".parallel" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    # Write plan.yaml
    plan_file = plans_dir / "plan.yaml"
    with open(plan_file, "w") as f:
        yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)

    print(f"DEBUG: ✅ Wrote plan to {plan_file}", file=sys.stderr)

    # Extract and write task files from ## Task Details sections
    task_pattern = r"### Task (\d+):\s*(.+?)\n.*?```yaml\n(.*?)```\n(.*?)(?=###|---|\Z)"
    task_matches = re.findall(task_pattern, content, re.DOTALL)

    if task_matches:
        tasks_dir = plans_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        for task_num, task_name, task_yaml_str, task_content in task_matches:
            try:
                task_yaml = yaml.safe_load(task_yaml_str)
            except yaml.YAMLError as e:
                print(
                    f"DEBUG: Failed to parse task-{task_num} YAML: {e}", file=sys.stderr
                )
                continue

            task_id = task_yaml.get("id", f"task-{task_num}")
            task_file = tasks_dir / f"{task_id}.md"

            with open(task_file, "w") as f:
                # Write YAML frontmatter
                f.write("---\n")
                yaml.dump(task_yaml, f, default_flow_style=False, sort_keys=False)
                f.write("---\n\n")

                # Write task name
                f.write(f"# {task_name.strip()}\n\n")

                # Write task content
                f.write(task_content.strip())
                f.write("\n")

        print(
            f"DEBUG: ✅ Wrote {len(task_matches)} task files", file=sys.stderr
        )

    # Create helper scripts (templates)
    scripts_dir = plans_dir / "scripts"
    templates_dir = plans_dir / "templates"
    scripts_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)

    # Helper scripts content would go here (add_task.sh, generate_full.sh)
    # For now, just create the directories

    return 1


def extract_decisions(transcript: list[dict]) -> list[dict]:
    """
    Find architectural decisions in conversation.

    Detection patterns:
    - ## Decision:
    - **Status:** Accepted|Proposed|Rejected
    - ### Alternatives Considered
    """
    decisions = []

    for entry in transcript:
        if entry.get("type") != "assistant":
            continue

        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
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

        decision_patterns = [
            r"## Decision:",
            r"\*\*Status:\*\* (Accepted|Proposed|Rejected)",
            r"### Alternatives Considered",
            r"### Context",
            r"### Consequences",
        ]

        if sum(len(re.findall(p, text, re.IGNORECASE)) for p in decision_patterns) >= 3:
            decisions.append({"timestamp": entry.get("timestamp", ""), "content": text})

    return decisions


def extract_decision_data(
    content: str, timestamp: str, session_id: str
) -> Optional[dict]:
    """
    Extract structured decision data from content.

    Expected format:
    ## Decision: {title}
    **Date:** YYYY-MM-DD
    **Status:** Accepted|Rejected|Pending|Revisiting
    ### Context
    {context}
    ### Alternatives Considered
    #### Option 1: ...
    **Result:** ✅/❌ ...
    ### Consequences
    **Positive:**
    - {benefit}
    **Negative:**
    - {consequence}

    Returns: Structured decision dict, or None if parsing fails
    """
    decision = {}

    # Extract title from "## Decision: {title}"
    title_match = re.search(r"## Decision:\s*(.+?)(?:\n|$)", content)
    if not title_match:
        return None

    decision["title"] = title_match.group(1).strip()

    # Extract date
    date_match = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", content)
    if date_match:
        decision["date"] = f"{date_match.group(1)}T00:00:00Z"
    else:
        decision["date"] = datetime.now().isoformat() + "Z"

    # Extract status
    status_match = re.search(
        r"\*\*Status:\*\*\s*(Accepted|Rejected|Pending|Revisiting)",
        content,
        re.IGNORECASE,
    )
    if status_match:
        status = status_match.group(1).lower()
        decision["status"] = status
    else:
        decision["status"] = "pending"

    # Extract context (between ### Context and ### Alternatives)
    context_match = re.search(
        r"### Context\s*\n(.*?)(?=###|\Z)", content, re.DOTALL | re.IGNORECASE
    )
    if context_match:
        decision["context"] = context_match.group(1).strip()

    # Extract alternatives considered
    alternatives = []
    # Find alternatives section - look for "### Alternatives" header
    alt_match = re.search(r"###\s+Alternatives[^\n]*\n+", content)
    if alt_match:
        alt_start_idx = alt_match.end()  # Position after header and newlines
        # Find next section header (### with exactly 3 hashes, followed by non-hash)
        rest = content[alt_start_idx:]
        next_section = re.search(r"\n###[^#]", rest)

        if next_section:
            alternatives_text = content[
                alt_start_idx : alt_start_idx + next_section.start() + 1
            ]
        else:
            alternatives_text = rest

        # Parse each option: #### Option X: {title}
        option_matches = re.finditer(
            r"#### Option (\d+):\s*(.+?)\n(.*?)(?=####|\Z)",
            alternatives_text,
            re.DOTALL,
        )

        for option_match in option_matches:
            option_title = option_match.group(2).strip()
            option_content = option_match.group(3).strip()

            alt = {"option": option_title}

            # Extract result (✅ Selected, ❌ Rejected)
            result_match = re.search(r"\*\*Result:\*\*\s*(.+?)(?:\n|$)", option_content)
            if result_match:
                result = result_match.group(1).strip()
                if "✅" in result or "selected" in result.lower():
                    alt["result"] = "selected"
                elif "❌" in result or "rejected" in result.lower():
                    alt["result"] = "rejected"
                else:
                    alt["result"] = "considered"

            # Extract pros
            pros_match = re.search(
                r"(?:^|\n)(?:pros|Pros):\s*\n(.*?)(?=(?:^|\n)(?:cons|Cons)|\Z)",
                option_content,
                re.DOTALL | re.MULTILINE,
            )
            if pros_match:
                pros_text = pros_match.group(1)
                pros = [
                    line.strip().lstrip("-").strip()
                    for line in pros_text.split("\n")
                    if line.strip().startswith("-")
                ]
                if pros:
                    alt["pros"] = pros

            # Extract cons
            cons_match = re.search(
                r"(?:^|\n)(?:cons|Cons):\s*\n(.*?)(?=\Z)",
                option_content,
                re.DOTALL | re.MULTILINE,
            )
            if cons_match:
                cons_text = cons_match.group(1)
                cons = [
                    line.strip().lstrip("-").strip()
                    for line in cons_text.split("\n")
                    if line.strip().startswith("-")
                ]
                if cons:
                    alt["cons"] = cons

            alternatives.append(alt)

    if alternatives:
        decision["alternatives_considered"] = alternatives

    # Extract consequences
    consequences = {}
    cons_start_idx = content.lower().find("### consequences")
    if cons_start_idx >= 0:
        # Extract from ### Consequences to end of content
        cons_text = content[cons_start_idx + len("### consequences") :]

        # Extract positive consequences - look for "Positive" (with optional ** before and after colon)
        # Pattern matches: **Positive:** or Positive: or Positive** etc.
        positive_match = re.search(
            r"\*{0,2}[Pp]ositive\*{0,2}\s*:\s*\*{0,2}\s*\n(.*?)(?=\*{0,2}[Nn]egative|\Z)",
            cons_text,
            re.DOTALL | re.IGNORECASE,
        )
        if positive_match:
            positive_text = positive_match.group(1)
            positives = [
                line.strip().lstrip("-").strip()
                for line in positive_text.split("\n")
                if line.strip().startswith("-")
            ]
            if positives:
                consequences["positive"] = positives

        # Extract negative consequences
        negative_match = re.search(
            r"\*{0,2}[Nn]egative\*{0,2}\s*:\s*\*{0,2}\s*\n(.*?)(?=\Z)",
            cons_text,
            re.DOTALL | re.IGNORECASE,
        )
        if negative_match:
            negative_text = negative_match.group(1)
            negatives = [
                line.strip().lstrip("-").strip()
                for line in negative_text.split("\n")
                if line.strip().startswith("-")
            ]
            if negatives:
                consequences["negative"] = negatives

    if consequences:
        decision["consequences"] = consequences

    # Add conversation link
    decision["conversation_link"] = {
        "session_id": session_id,
        "timestamp": int(
            datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp() * 1000
        )
        if timestamp
        else None,
    }

    # Add creation timestamp
    decision["created_at"] = timestamp or datetime.now().isoformat() + "Z"

    return decision


def append_decisions(project_root: Path, decisions: list[dict], session_id: str) -> int:
    """
    Append extracted decisions to decisions.yaml.

    Returns: Number of decisions appended
    """
    if not decisions:
        return 0

    decisions_file = project_root / "decisions.yaml"
    if not decisions_file.exists():
        print(f"DEBUG: decisions.yaml not found at {decisions_file}", file=sys.stderr)
        return 0

    # Load existing decisions.yaml
    try:
        with open(decisions_file, "r") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"DEBUG: Failed to load decisions.yaml: {e}", file=sys.stderr)
        return 0

    # Ensure 'decisions' section exists
    if "decisions" not in data:
        data["decisions"] = {"entries": []}
    if "entries" not in data["decisions"]:
        data["decisions"]["entries"] = []

    # Extract and append each decision
    appended_count = 0
    existing_entries = data["decisions"].get("entries", [])

    for decision_entry in decisions:
        content = decision_entry.get("content", "")
        timestamp = decision_entry.get("timestamp", "")

        # Parse decision data
        decision_data = extract_decision_data(content, timestamp, session_id)
        if not decision_data:
            continue

        # Generate unique ID based on title and timestamp
        title_slug = sanitize_topic(decision_data["title"])
        timestamp_ms = decision_data["conversation_link"].get("timestamp", 0)
        decision_id = f"dec-{timestamp_ms % 1000000:06d}-{title_slug[:20]}"

        # Check if similar decision already exists
        existing_ids = [e.get("id") for e in existing_entries if isinstance(e, dict)]
        if decision_id in existing_ids:
            print(
                f"DEBUG: Decision {decision_id} already exists, skipping",
                file=sys.stderr,
            )
            continue

        decision_data["id"] = decision_id

        # Append to entries list
        existing_entries.append(decision_data)
        appended_count += 1

    # Update entries
    data["decisions"]["entries"] = existing_entries

    # Write back to decisions.yaml atomically
    try:
        with open(decisions_file, "w") as f:
            yaml.dump(
                data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        print(
            f"DEBUG: ✅ Appended {appended_count} decisions to decisions.yaml",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"DEBUG: Failed to write decisions.yaml: {e}", file=sys.stderr)
        return 0

    return appended_count


def main():
    """
    SessionEnd hook entry point.

    Reads full transcript, extracts completed work, writes structured files.
    """
    try:
        # Read hook data
        hook_data = json.loads(sys.stdin.read())

        transcript_path = hook_data.get("transcript_path", "")
        session_id = hook_data.get("session_id", "unknown")

        print(f"DEBUG: SessionEnd extractor triggered", file=sys.stderr)
        print(f"DEBUG: Session: {session_id}", file=sys.stderr)
        print(f"DEBUG: Transcript: {transcript_path}", file=sys.stderr)

        if not transcript_path or not Path(transcript_path).exists():
            print(f"DEBUG: Transcript not found, skipping extraction", file=sys.stderr)
            output = {"continue": True}
            print(json.dumps(output))
            sys.exit(0)

        # Read full transcript
        with open(transcript_path, "r") as f:
            transcript = [json.loads(line) for line in f if line.strip()]

        print(f"DEBUG: Loaded {len(transcript)} conversation entries", file=sys.stderr)

        # Find project root from first entry's cwd
        project_root = Path.cwd()
        if transcript:
            cwd = transcript[0].get("cwd")
            if cwd:
                project_root = Path(cwd)

        print(f"DEBUG: Project root: {project_root}", file=sys.stderr)

        # Extract components
        designs = extract_designs(transcript)
        plans = extract_plans(transcript)
        decisions_found = extract_decisions(transcript)

        print(f"DEBUG: Found {len(designs)} design proposals", file=sys.stderr)
        print(f"DEBUG: Found {len(plans)} parallel plans", file=sys.stderr)
        print(f"DEBUG: Found {len(decisions_found)} decision points", file=sys.stderr)

        # Write structured files
        designs_written = write_design_files(project_root, designs, session_id)
        plans_written = write_plan_files(project_root, plans, session_id)
        decisions_written = append_decisions(project_root, decisions_found, session_id)

        if designs_written or plans_written or decisions_written:
            print(
                f"DEBUG: ✅ Extracted {designs_written} designs, {plans_written} plans, {decisions_written} decisions",
                file=sys.stderr,
            )
        else:
            print(f"DEBUG: No extractable content found", file=sys.stderr)

    except Exception as e:
        print(f"DEBUG: SessionEnd extraction failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)

    # Always continue (don't block session end)
    output = {"continue": True}
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
