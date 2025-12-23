#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "htmlgraph>=0.7.0",
# ]
# ///
"""Auto-tracking hook: Create HtmlGraph track from /ctx:plan execution.

This hook runs after /ctx:plan completes and automatically:
1. Detects plan creation by checking for .parallel/plans/plan.yaml
2. Parses plan metadata
3. Creates HtmlGraph track
4. Stores track_id back in plan.yaml

Enables zero-friction integration: just run /ctx:plan and get automatic tracking.
"""

import json
import sys
from pathlib import Path
from typing import Any

import yaml


def log(message: str, data: dict[str, Any] | None = None) -> None:
    """Log to stderr for debugging."""
    log_entry = {"hook": "contextune_plan_tracker", "message": message}
    if data:
        log_entry["data"] = data
    print(json.dumps(log_entry), file=sys.stderr)


def find_recent_plan() -> Path | None:
    """Find most recently created plan.yaml.

    Returns:
        Path to plan.yaml if found, None otherwise
    """
    plans_dir = Path(".parallel/plans")
    if not plans_dir.exists():
        return None

    # Look for plan.yaml files
    plan_files = list(plans_dir.glob("*/plan.yaml"))
    if not plan_files:
        # Also check root level
        root_plan = plans_dir / "plan.yaml"
        if root_plan.exists():
            return root_plan
        return None

    # Return most recent
    return max(plan_files, key=lambda p: p.stat().st_mtime)


def create_track_from_plan(plan_path: Path) -> str | None:
    """Create HtmlGraph track from plan.

    Args:
        plan_path: Path to plan.yaml

    Returns:
        Track ID if created, None if failed
    """
    try:
        # Check if HtmlGraph is available
        try:
            from htmlgraph import SDK
            from htmlgraph.models import Step
        except ImportError:
            log("HtmlGraph not available, skipping track creation")
            return None

        # Load plan
        with open(plan_path) as f:
            plan_data = yaml.safe_load(f)

        if not plan_data:
            log("Empty plan file", {"path": str(plan_path)})
            return None

        # Extract metadata
        metadata = plan_data.get("metadata", {})
        overview = plan_data.get("overview", "")
        tasks = plan_data.get("tasks", [])

        # Check if track already exists
        if "htmlgraph_track_id" in metadata:
            existing_track_id = metadata["htmlgraph_track_id"]
            log("Track already exists", {"track_id": existing_track_id})
            return existing_track_id

        # Initialize SDK
        sdk = SDK(agent="contextune-auto-tracker")

        # Create track using TrackBuilder
        plan_title = metadata.get("title", "Untitled Plan")

        track = sdk.tracks.builder() \
            .title(plan_title) \
            .description(overview or f"Auto-created from {plan_path.parent.name}") \
            .priority("high") \
            .create()

        log("Created HtmlGraph track", {
            "track_id": track.id,
            "title": plan_title,
            "tasks": len(tasks)
        })

        # Store track_id in plan metadata
        metadata["htmlgraph_track_id"] = track.id
        metadata["auto_tracked"] = True
        plan_data["metadata"] = metadata

        # Write back to plan.yaml
        with open(plan_path, 'w') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)

        log("Updated plan with track_id", {"plan_path": str(plan_path)})

        return track.id

    except Exception as e:
        log("Error creating track", {"error": str(e), "type": type(e).__name__})
        return None


def main() -> None:
    """Hook entry point."""
    try:
        # Read hook input (PostToolUse format)
        input_data = json.loads(sys.stdin.read())

        # Check if this was a plan creation command
        # We detect this by looking for recent plan.yaml files
        plan_path = find_recent_plan()

        if not plan_path:
            # No recent plan found, nothing to track
            log("No recent plan found, skipping")
            print(json.dumps({"continue": True}))
            sys.exit(0)

        # Check if plan was created very recently (within last 60 seconds)
        import time
        age_seconds = time.time() - plan_path.stat().st_mtime

        if age_seconds > 60:
            # Plan is too old, probably not from this command
            log("Plan too old, skipping", {"age_seconds": age_seconds})
            print(json.dumps({"continue": True}))
            sys.exit(0)

        # Create track
        track_id = create_track_from_plan(plan_path)

        if track_id:
            # Provide feedback to user via additionalContext
            feedback = {
                "continue": True,
                "additionalContext": (
                    f"\n\n🔗 **HtmlGraph Integration**\n"
                    f"Created track `{track_id}` for this plan.\n"
                    f"All tasks will be auto-linked when you run `/ctx:execute`.\n"
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
