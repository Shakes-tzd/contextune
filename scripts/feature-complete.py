#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Feature Complete - Mark feature as completed.

Usage:
    uv run scripts/feature-complete.py FEATURE_ID
"""

import subprocess
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


def load_features() -> dict:
    """Load features.yaml."""
    features_file = Path(__file__).parent.parent / "features.yaml"

    if not features_file.exists():
        console.print("[red]Error: features.yaml not found[/red]")
        sys.exit(1)

    with open(features_file) as f:
        return yaml.safe_load(f)


def save_features(data: dict):
    """Save features.yaml."""
    features_file = Path(__file__).parent.parent / "features.yaml"

    with open(features_file, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_feature(data: dict, feature_id: str) -> dict | None:
    """Get feature by ID."""
    for feature in data["features"]:
        if feature["id"] == feature_id:
            return feature
    return None


def run_command(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed: {' '.join(cmd)}[/red]")
        console.print(f"[red]{e.stderr}[/red]")
        sys.exit(1)


def update_feature_status(data: dict, feature_id: str):
    """Update feature status to completed."""
    for feature in data["features"]:
        if feature["id"] == feature_id:
            feature["status"] = "completed"
            break

    save_features(data)
    console.print("[green]✓ Status updated to: completed[/green]")


def commit_status_change(feature: dict):
    """Commit status change to git."""
    run_command(["git", "add", "features.yaml"])
    commit_msg = f"""chore({feature['id']}): mark as completed

Completed: {feature['name']}

✅ Feature implementation complete
"""
    run_command(["git", "commit", "-m", commit_msg])
    console.print("[green]✓ Committed status change[/green]")


def get_unblocked_features(data: dict, feature_id: str) -> list[dict]:
    """Get features that are now unblocked."""
    features = data["features"]
    unblocked = []

    for feature in features:
        if (
            feature["status"] == "planned"
            and feature_id in feature.get("dependencies", [])
        ):
            unblocked.append(feature)

    return unblocked


def show_completion_stats(data: dict):
    """Show overall completion statistics."""
    features = data["features"]
    total = len(features)
    completed = sum(1 for f in features if f["status"] == "completed")
    completion_pct = int((completed / total) * 100)

    console.print()
    console.print("[bold]Overall Progress:[/bold]")
    console.print(
        f"  Completed: [green]{completed}[/green] / {total} ([green]{completion_pct}%[/green])"
    )
    console.print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        console.print("[red]Error: Feature ID required[/red]")
        console.print("Usage: uv run scripts/feature-complete.py FEATURE_ID")
        sys.exit(1)

    feature_id = sys.argv[1]
    data = load_features()

    # Get feature
    feature = get_feature(data, feature_id)
    if not feature:
        console.print(f"[red]Error: Feature {feature_id} not found[/red]")
        sys.exit(1)

    # Show header
    console.print(
        Panel.fit(
            f"[bold blue]Complete Feature: {feature_id}[/bold blue]",
            border_style="blue",
        )
    )
    console.print()

    console.print(f"[bold]Feature:[/bold] {feature['name']}")
    console.print(f"[bold]Current status:[/bold] {feature['status']}")
    console.print()

    # Check if already completed
    if feature["status"] == "completed":
        console.print("[green]✓ Feature already marked as completed[/green]")
        sys.exit(0)

    # Ask for confirmation
    if not Confirm.ask("Mark this feature as completed?"):
        console.print("Cancelled")
        sys.exit(0)

    # Update status
    update_feature_status(data, feature_id)

    # Commit status change
    commit_status_change(feature)

    # Check what's unblocked
    unblocked = get_unblocked_features(data, feature_id)

    if unblocked:
        console.print()
        console.print("[bold]Features now unblocked:[/bold]")
        for feat in unblocked:
            console.print(f"  [green]✓[/green] {feat['id']}: {feat['name']}")

        console.print()
        console.print("[yellow]You can now execute:[/yellow]")
        for feat in unblocked:
            console.print(f"  [blue]uv run scripts/feature-execute.py {feat['id']}[/blue]")

    # Show completion stats
    show_completion_stats(data)

    # Show success
    console.print(
        Panel.fit(
            f"[bold green]✅ Feature {feature_id} completed![/bold green]",
            border_style="green",
        )
    )
    console.print()

    console.print("[dim]Next steps:[/dim]")
    console.print("  [dim]uv run scripts/feature-status.py         # View all features[/dim]")
    console.print("  [dim]uv run scripts/feature-graph.py          # View dependency graph[/dim]")
    console.print()


if __name__ == "__main__":
    main()
