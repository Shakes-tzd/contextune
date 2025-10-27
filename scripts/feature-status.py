#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Feature Status - Show feature improvement status and recommendations.

Usage:
    uv run scripts/feature-status.py [OPTIONS]

Options:
    --phase N              Show only Phase N features
    --priority LEVEL       Show priority level (critical, high, medium, low)
    --status STATUS        Show status (planned, in_progress, completed, blocked)
    --independent          Show independent features only
"""

import sys
from pathlib import Path
from typing import Optional

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def load_features() -> dict:
    """Load features.yaml."""
    features_file = Path(__file__).parent.parent / "features.yaml"

    if not features_file.exists():
        console.print("[red]Error: features.yaml not found[/red]")
        sys.exit(1)

    with open(features_file) as f:
        return yaml.safe_load(f)


def parse_args():
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Show feature improvement status and recommendations"
    )
    parser.add_argument("--phase", type=int, help="Filter by phase")
    parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        help="Filter by priority",
    )
    parser.add_argument(
        "--status",
        choices=["planned", "in_progress", "completed", "blocked", "research"],
        help="Filter by status",
    )
    parser.add_argument(
        "--independent", action="store_true", help="Show only independent features"
    )

    return parser.parse_args()


def get_priority_symbol(priority: str) -> str:
    """Get emoji for priority level."""
    symbols = {
        "critical": "🔥",
        "high": "⭐",
        "medium": "○",
        "low": "·",
    }
    return symbols.get(priority, "○")


def get_status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        "completed": "green",
        "in_progress": "blue",
        "planned": "yellow",
        "blocked": "red",
        "research": "dim",
    }
    return colors.get(status, "white")


def show_summary(data: dict):
    """Show summary statistics."""
    console.print(
        Panel.fit(
            "[bold blue]Contextune Feature Status[/bold blue]",
            border_style="blue",
        )
    )
    console.print()

    summary = data["summary"]

    # Overall stats
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  Total features: [green]{summary['total_features']}[/green]")
    console.print()

    # By status
    console.print(f"[bold]By Status:[/bold]")
    for status, count in summary["by_status"].items():
        color = get_status_color(status)
        console.print(f"  {status}: [{color}]{count}[/{color}]")
    console.print()

    # By priority
    console.print(f"[bold]By Priority:[/bold]")
    for priority, count in summary["by_priority"].items():
        symbol = get_priority_symbol(priority)
        console.print(f"  {symbol} {priority}: {count}")
    console.print()

    # By phase
    console.print(f"[bold]By Phase:[/bold]")
    for phase, count in summary["by_phase"].items():
        console.print(f"  {phase}: {count}")
    console.print()


def show_features(data: dict, args):
    """Show feature list with optional filtering."""
    features = data["features"]

    # Apply filters
    if args.phase is not None:
        features = [f for f in features if f.get("phase") == args.phase]

    if args.priority:
        features = [f for f in features if f.get("priority") == args.priority]

    if args.status:
        features = [f for f in features if f.get("status") == args.status]

    if args.independent:
        features = [f for f in features if not f.get("dependencies")]

    if not features:
        console.print("[yellow]No features match the filters[/yellow]")
        return

    console.print(f"[bold]Features:[/bold]")
    console.print()

    for feature in features:
        feature_id = feature["id"]
        name = feature["name"]
        status = feature["status"]
        priority = feature["priority"]
        phase = feature.get("phase", 0)
        tokens = feature["effort"]["estimated_tokens"]
        cost_haiku = feature["effort"].get("cost_haiku", "N/A")
        deps = feature.get("dependencies", [])

        # Status color and symbol
        status_color = get_status_color(status)
        priority_symbol = get_priority_symbol(priority)

        # Feature header
        console.print(
            f"{priority_symbol} [bold]{feature_id}[/bold]: {name}",
            style=status_color,
        )

        # Details - Display tokens with cost
        tokens_display = f"{tokens:,}" if tokens > 0 else "0"
        console.print(
            f"   Status: [{status_color}]{status}[/{status_color}] | "
            f"Priority: {priority} | Phase: {phase} | "
            f"Tokens: {tokens_display} ({cost_haiku} Haiku)"
        )

        # Dependencies
        if deps:
            deps_str = ", ".join([f"[yellow]{d}[/yellow]" for d in deps])
            console.print(f"   Dependencies: {deps_str}")

        console.print()


def show_execution_recommendations(data: dict):
    """Show execution recommendations."""
    features = data["features"]

    console.print("[bold]Execution Recommendations:[/bold]")
    console.print()

    # Ready to execute (no dependencies)
    ready = [
        f
        for f in features
        if f["status"] == "planned" and not f.get("dependencies")
    ]

    if ready:
        console.print("[bold green]Ready to execute (no dependencies):[/bold green]")
        for feature in ready:
            phase = feature.get("phase", 0)
            console.print(
                f"  • {feature['id']}: {feature['name']} (Phase {phase})"
            )
        console.print()

    # Blocked (has dependencies)
    blocked = [
        f
        for f in features
        if f["status"] == "planned" and f.get("dependencies")
    ]

    if blocked:
        console.print("[bold yellow]Blocked (waiting on dependencies):[/bold yellow]")
        for feature in blocked:
            deps = ", ".join(feature.get("dependencies", []))
            console.print(f"  • {feature['id']}: {feature['name']} (needs: {deps})")
        console.print()

    # Commands
    console.print("[dim]Commands:[/dim]")
    console.print("  [dim]uv run scripts/feature-status.py --phase 1[/dim]")
    console.print("  [dim]uv run scripts/feature-execute.py feat-001[/dim]")
    console.print("  [dim]uv run scripts/feature-graph.py[/dim]")
    console.print()


def main():
    """Main entry point."""
    args = parse_args()
    data = load_features()

    show_summary(data)
    show_features(data, args)
    show_execution_recommendations(data)


if __name__ == "__main__":
    main()
