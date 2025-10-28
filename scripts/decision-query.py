#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Decision Query - Selective context loading from decisions.yaml

Load specific decisions instead of entire file to minimize context tokens.

Usage:
    uv run scripts/decision-query.py [OPTIONS]

Options:
    --topic TOPIC              Filter by topic (authentication, architecture, etc.)
    --tags TAGS                Filter by tags (comma-separated)
    --category CATEGORY        Filter by category (architecture, process, tooling, performance)
    --status STATUS            Filter by status (accepted, rejected, pending, revisiting)
    --since DAYS               Show entries from last N days (e.g., 30d)
    --impact LEVEL             Filter by impact (high, medium, low)
    --include-expired          Include expired research entries (default: skip)
    --format FORMAT            Output format (text, json, yaml) - default: text
    --estimate-tokens          Show token count estimation for results
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

console = Console()


def load_decisions() -> dict:
    """Load decisions.yaml from project root."""
    # Try multiple paths to find decisions.yaml
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir.parent / "decisions.yaml",  # ../decisions.yaml (normal run)
        script_dir.parent.parent
        / "decisions.yaml",  # ../../decisions.yaml (from worktree/scripts/)
        script_dir.parent.parent.parent
        / "decisions.yaml",  # ../../../decisions.yaml (edge case)
    ]

    decisions_file = None
    for path in possible_paths:
        if path.exists():
            decisions_file = path
            break

    if not decisions_file:
        console.print(
            f"[red]Error: decisions.yaml not found. Searched: {possible_paths}[/red]"
        )
        sys.exit(1)

    with open(decisions_file) as f:
        return yaml.safe_load(f) or {}


def estimate_tokens(entry: dict[str, Any]) -> int:
    """Estimate token count for a decision entry.

    Rough estimation:
    - Title/ID: ~20 tokens
    - Context/Description: ~100 tokens per 500 chars
    - Decision: ~100 tokens per 500 chars
    - Alternatives: ~50 tokens per alternative
    - Consequences: ~50 tokens
    """
    tokens = 20

    # Context/Description
    if "context" in entry:
        tokens += len(str(entry["context"])) // 5

    # Decision
    if "decision" in entry:
        tokens += len(str(entry["decision"])) // 5

    # Rationale
    if "rationale" in entry:
        tokens += len(str(entry["rationale"])) // 5

    # Alternatives
    if "alternatives_considered" in entry:
        tokens += len(entry["alternatives_considered"]) * 50

    # Consequences
    if "consequences" in entry:
        tokens += 50

    return max(tokens, 100)  # Minimum 100 tokens per entry


def is_expired(entry: dict[str, Any]) -> bool:
    """Check if entry has expired based on expires_at field."""
    if entry.get("permanent"):
        return False

    if "expires_at" not in entry:
        return False

    try:
        expires_at = datetime.fromisoformat(entry["expires_at"].replace("Z", "+00:00"))
        return datetime.now(expires_at.tzinfo) > expires_at
    except (ValueError, TypeError):
        return False


def filter_entries(
    entries: list[dict[str, Any]],
    topic: str | None = None,
    tags: list[str] | None = None,
    category: str | None = None,
    status: str | None = None,
    since_days: int | None = None,
    impact: str | None = None,
    include_expired: bool = False,
) -> list[dict[str, Any]]:
    """Filter entries based on query criteria."""
    if not entries:
        return []

    results = []

    for entry in entries:
        # Skip expired entries unless requested
        if is_expired(entry) and not include_expired:
            continue

        # Topic filter (search in title, context, decision)
        if topic:
            topic_lower = topic.lower()
            searchable = " ".join(
                [
                    str(entry.get("title", "")),
                    str(entry.get("context", "")),
                    str(entry.get("decision", "")),
                    str(entry.get("topic", "")),
                ]
            ).lower()
            if topic_lower not in searchable:
                continue

        # Tags filter
        if tags:
            entry_tags = set(entry.get("tags", []))
            if not entry_tags or not any(tag in entry_tags for tag in tags):
                continue

        # Category filter
        if category and entry.get("category") != category:
            continue

        # Status filter
        if status and entry.get("status") != status:
            continue

        # Impact filter
        if impact and entry.get("impact") != impact:
            continue

        # Since filter (created_at or timestamp)
        if since_days:
            cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)
            try:
                created = entry.get("created_at", entry.get("date"))
                if created:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    if created_dt < cutoff:
                        continue
            except (ValueError, TypeError):
                pass

        results.append(entry)

    return results


def format_entry_text(entry: dict[str, Any], show_tokens: bool = False) -> str:
    """Format entry for text output."""
    lines = []

    # Header
    title = entry.get("title", "Unknown")
    entry_id = entry.get("id", "no-id")
    lines.append(f"[bold]{title}[/bold] [dim]({entry_id})[/dim]")

    # Metadata
    metadata = []
    if "date" in entry:
        date = entry["date"][:10] if isinstance(entry["date"], str) else entry["date"]
        metadata.append(f"Date: {date}")
    if "category" in entry:
        metadata.append(f"Category: {entry['category']}")
    if "status" in entry:
        status = entry["status"]
        status_color = {
            "accepted": "green",
            "rejected": "red",
            "pending": "yellow",
            "revisiting": "blue",
        }.get(status, "white")
        metadata.append(f"Status: [{status_color}]{status}[/{status_color}]")
    if "impact" in entry:
        metadata.append(f"Impact: {entry['impact']}")

    if metadata:
        lines.append("   " + " | ".join(metadata))

    # Context
    if "context" in entry:
        context = entry["context"]
        if len(context) > 200:
            context = context[:200] + "..."
        lines.append(f"   Context: {context}")

    # Decision
    if "decision" in entry:
        decision = entry["decision"]
        if len(decision) > 200:
            decision = decision[:200] + "..."
        lines.append(f"   Decision: {decision}")

    # Token count
    if show_tokens:
        tokens = estimate_tokens(entry)
        lines.append(f"   Tokens: {tokens:,}")

    # Expiration warning
    if is_expired(entry):
        lines.append("   [red]EXPIRED[/red]")
    elif "expires_at" in entry:
        try:
            expires = datetime.fromisoformat(entry["expires_at"].replace("Z", "+00:00"))
            days_left = (expires - datetime.now(expires.tzinfo)).days
            if days_left <= 30:
                lines.append(f"   [yellow]Expires in {days_left} days[/yellow]")
        except (ValueError, TypeError):
            pass

    return "\n".join(lines)


def show_text_output(results: list[dict[str, Any]], show_tokens: bool = False):
    """Display results in formatted text output."""
    if not results:
        console.print("[yellow]No matching decisions found[/yellow]")
        return

    console.print(f"\n[bold]Found {len(results)} matching decision(s)[/bold]\n")

    total_tokens = 0
    for i, entry in enumerate(results, 1):
        console.print(format_entry_text(entry, show_tokens))
        if show_tokens:
            total_tokens += estimate_tokens(entry)

        if i < len(results):
            console.print()

    if show_tokens:
        console.print()
        console.print(f"[bold]Total estimated tokens: {total_tokens:,}[/bold]")
        reduction = (1 - total_tokens / 10000) * 100
        console.print(f"[green]Context reduction: {reduction:.1f}%[/green]")


def show_json_output(results: list[dict[str, Any]]):
    """Display results in JSON format."""
    console.print(json.dumps(results, indent=2, default=str))


def show_yaml_output(results: list[dict[str, Any]]):
    """Display results in YAML format."""
    console.print(yaml.dump(results, default_flow_style=False))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Query decisions.yaml for selective context loading"
    )
    parser.add_argument(
        "--topic",
        help="Filter by topic (e.g., authentication, architecture)",
        type=str,
    )
    parser.add_argument(
        "--tags",
        help="Filter by tags (comma-separated)",
        type=str,
    )
    parser.add_argument(
        "--category",
        choices=["architecture", "process", "tooling", "performance"],
        help="Filter by category",
    )
    parser.add_argument(
        "--status",
        choices=["accepted", "rejected", "pending", "revisiting"],
        help="Filter by status",
    )
    parser.add_argument(
        "--since",
        type=str,
        help="Show entries from last N days (e.g., 30d)",
    )
    parser.add_argument(
        "--impact",
        choices=["high", "medium", "low"],
        help="Filter by impact level",
    )
    parser.add_argument(
        "--include-expired",
        action="store_true",
        help="Include expired research entries",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--estimate-tokens",
        action="store_true",
        help="Show token count estimation",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Load decisions
    data = load_decisions()

    # Collect all entries from all sections
    all_entries = []

    # Add research entries
    if "research" in data and "entries" in data["research"]:
        research_entries = data["research"]["entries"] or []
        for entry in research_entries:
            entry["_type"] = "research"
        all_entries.extend(research_entries)

    # Add plan entries
    if "plans" in data and "entries" in data["plans"]:
        plan_entries = data["plans"]["entries"] or []
        for entry in plan_entries:
            entry["_type"] = "plan"
        all_entries.extend(plan_entries)

    # Add decision entries
    if "decisions" in data and "entries" in data["decisions"]:
        decision_entries = data["decisions"]["entries"] or []
        for entry in decision_entries:
            entry["_type"] = "decision"
        all_entries.extend(decision_entries)

    # Add feature entries
    if "features" in data and "entries" in data["features"]:
        feature_entries = data["features"]["entries"] or []
        for entry in feature_entries:
            entry["_type"] = "feature"
        all_entries.extend(feature_entries)

    # Parse since argument
    since_days = None
    if args.since:
        try:
            since_days = int(args.since.rstrip("d"))
        except ValueError:
            console.print(f"[red]Invalid --since value: {args.since}[/red]")
            sys.exit(1)

    # Parse tags argument
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]

    # Filter entries
    results = filter_entries(
        all_entries,
        topic=args.topic,
        tags=tags,
        category=args.category,
        status=args.status,
        since_days=since_days,
        impact=args.impact,
        include_expired=args.include_expired,
    )

    # Display results
    if args.format == "json":
        show_json_output(results)
    elif args.format == "yaml":
        show_yaml_output(results)
    else:
        show_text_output(results, args.estimate_tokens)


if __name__ == "__main__":
    main()
