#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "htmlgraph>=0.7.0",
# ]
# ///
"""Auto-tracking hook: Create HtmlGraph features from /ctx:execute tasks.

This hook runs when /ctx:execute starts and automatically:
1. Reads plan.yaml to get track_id and tasks
2. Creates HtmlGraph feature for each task
3. Links features to track
4. Starts first feature automatically

Enables zero-friction execution: run /ctx:execute and get automatic feature tracking.
"""

import json
import sys
from pathlib import Path
from typing import Any

import yaml


def log(message: str, data: dict[str, Any] | None = None) -> None:
    """Log to stderr for debugging."""
    log_entry = {"hook": "contextune_execute_tracker", "message": message}
    if data:
        log_entry["data"] = data
    print(json.dumps(log_entry), file=sys.stderr)


def get_plan_path() -> Path | None:
    """Get path to current plan.yaml.

    Returns:
        Path to plan.yaml if found, None otherwise
    """
    # Check standard location
    plan_path = Path(".parallel/plans/plan.yaml")
    if plan_path.exists():
        return plan_path

    # Check for subdirectories with plan.yaml
    plans_dir = Path(".parallel/plans")
    if plans_dir.exists():
        plan_files = list(plans_dir.glob("*/plan.yaml"))
        if plan_files:
            # Return most recent
            return max(plan_files, key=lambda p: p.stat().st_mtime)

    return None


def create_features_from_tasks(plan_path: Path) -> list[str]:
    """Create HtmlGraph features for each task in plan.

    Args:
        plan_path: Path to plan.yaml

    Returns:
        List of created feature IDs
    """
    feature_ids: list[str] = []

    try:
        # Check if HtmlGraph is available
        try:
            from htmlgraph import SDK
        except ImportError:
            log("HtmlGraph not available, skipping feature creation")
            return []

        # Load plan
        with open(plan_path) as f:
            plan_data = yaml.safe_load(f)

        if not plan_data:
            log("Empty plan file", {"path": str(plan_path)})
            return []

        # Get track_id
        metadata = plan_data.get("metadata", {})
        track_id = metadata.get("htmlgraph_track_id")

        if not track_id:
            log("No track_id in plan, cannot link features")
            return []

        # Get tasks
        tasks = plan_data.get("tasks", [])
        if not tasks:
            log("No tasks in plan")
            return []

        # Initialize SDK
        sdk = SDK(agent="contextune-auto-tracker")

        # Create feature for each task
        for task in tasks:
            task_id = task.get("id", "unknown")
            task_title = task.get("title", f"Task {task_id}")
            task_type = task.get("type", "implement")
            priority = task.get("priority", "medium")
            dependencies = task.get("dependencies", [])

            # Check if feature already exists
            task_file_path = plan_path.parent / task.get("file", f"tasks/{task_id}.md")

            # Read task file to get steps
            steps = []
            if task_file_path.exists():
                with open(task_file_path) as tf:
                    content = tf.read()
                    # Extract steps from task file
                    # Look for numbered lists or step sections
                    import re
                    step_pattern = r'^\d+\.\s+\*\*(.+?)\*\*'
                    for match in re.finditer(step_pattern, content, re.MULTILINE):
                        steps.append(match.group(1))

            # Create feature
            try:
                feature = sdk.features.create(task_title) \
                    .set_track(track_id) \
                    .set_priority(priority)

                if steps:
                    feature = feature.add_steps(steps)

                feature = feature.save()

                feature_ids.append(feature.id)

                log("Created feature", {
                    "feature_id": feature.id,
                    "task_id": task_id,
                    "title": task_title,
                    "track_id": track_id,
                    "steps": len(steps)
                })

            except Exception as e:
                log("Error creating feature", {
                    "task_id": task_id,
                    "error": str(e)
                })

        # Auto-start first feature if configured
        if feature_ids:
            try:
                from lib.contextune_integration import get_config

                config = get_config()
                if config.htmlgraph.tracking.auto_start_features:
                    first_feature = feature_ids[0]
                    with sdk.features.edit(first_feature) as f:
                        f.status = "in-progress"

                    log("Auto-started first feature", {"feature_id": first_feature})

            except Exception as e:
                log("Error auto-starting feature", {"error": str(e)})

        return feature_ids

    except Exception as e:
        log("Error creating features", {"error": str(e), "type": type(e).__name__})
        return []


def main() -> None:
    """Hook entry point."""
    try:
        # Read hook input (PostToolUse format)
        input_data = json.loads(sys.stdin.read())

        # Get plan path
        plan_path = get_plan_path()

        if not plan_path:
            log("No plan found, skipping feature creation")
            print(json.dumps({"continue": True}))
            sys.exit(0)

        # Create features
        feature_ids = create_features_from_tasks(plan_path)

        if feature_ids:
            # Provide feedback to user
            feedback = {
                "continue": True,
                "additionalContext": (
                    f"\n\n🎯 **HtmlGraph Integration**\n"
                    f"Created {len(feature_ids)} features for this execution:\n"
                    + "\n".join(f"  - `{fid}`" for fid in feature_ids[:5])
                    + (f"\n  - ... and {len(feature_ids) - 5} more" if len(feature_ids) > 5 else "")
                    + f"\n\nFirst feature auto-started. View progress: `htmlgraph serve`\n"
                )
            }
        else:
            feedback = {"continue": True}

        print(json.dumps(feedback))
        sys.exit(0)

    except Exception as e:
        log("Hook error", {"error": str(e), "type": type(e).__name__})
        # Never block on errors
        print(json.dumps({"continue": True}))
        sys.exit(0)


if __name__ == "__main__":
    main()
