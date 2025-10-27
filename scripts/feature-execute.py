#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Feature Execute - Execute feature implementation by creating worktree.

Usage:
    uv run scripts/feature-execute.py FEATURE_ID
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


def check_dependencies(data: dict, feature: dict) -> tuple[bool, list]:
    """Check if dependencies are met."""
    deps = feature.get("dependencies", [])
    unmet = []

    for dep_id in deps:
        dep = get_feature(data, dep_id)
        if not dep or dep["status"] != "completed":
            unmet.append((dep_id, dep))

    return len(unmet) == 0, unmet


def run_command(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed: {' '.join(cmd)}[/red]")
        console.print(f"[red]{e.stderr}[/red]")
        sys.exit(1)


def create_worktree(feature_id: str) -> tuple[str, str]:
    """Create git worktree for feature."""
    project_root = Path(__file__).parent.parent
    worktree_path = f"worktrees/{feature_id}"
    branch_name = f"feature/{feature_id}"

    # Check if worktree exists
    result = run_command(["git", "worktree", "list"], check=False)
    if worktree_path in result.stdout:
        console.print(f"[yellow]⚠ Worktree already exists: {worktree_path}[/yellow]")
        return worktree_path, branch_name

    # Check if branch exists
    result = run_command(
        ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"], check=False
    )

    if result.returncode == 0:
        # Branch exists, use it
        console.print(f"[yellow]⚠ Branch {branch_name} already exists[/yellow]")
        run_command(["git", "worktree", "add", worktree_path, branch_name])
    else:
        # Create new branch
        run_command(["git", "worktree", "add", worktree_path, "-b", branch_name])

    console.print(f"[green]✓ Created worktree: {worktree_path}[/green]")
    return worktree_path, branch_name


def update_feature_status(data: dict, feature_id: str):
    """Update feature status to in_progress."""
    for feature in data["features"]:
        if feature["id"] == feature_id:
            feature["status"] = "in_progress"
            break

    save_features(data)
    console.print("[green]✓ Status updated to: in_progress[/green]")


def commit_status_change(feature: dict):
    """Commit status change to git."""
    run_command(["git", "add", "features.yaml"])
    commit_msg = f"""chore({feature['id']}): start implementation

Starting work on: {feature['name']}
Estimated effort: {feature['effort']['estimate_hours']}h
Phase: {feature.get('phase', 0)}
"""
    run_command(["git", "commit", "-m", commit_msg])
    console.print("[green]✓ Committed status change[/green]")


def show_feature_details(feature: dict):
    """Show feature details."""
    console.print(
        Panel.fit(
            f"[bold blue]Execute Feature: {feature['id']}[/bold blue]",
            border_style="blue",
        )
    )
    console.print()

    console.print("[bold]Feature Details:[/bold]")
    console.print(f"  Name: [green]{feature['name']}[/green]")
    console.print(f"  Status: [yellow]{feature['status']}[/yellow]")
    console.print(f"  Priority: {feature['priority']}")
    console.print(f"  Phase: {feature.get('phase', 0)}")

    # Token-based effort display
    tokens = feature['effort']['estimated_tokens']
    cost_haiku = feature['effort'].get('cost_haiku', 'N/A')
    cost_sonnet = feature['effort'].get('cost_sonnet', 'N/A')
    tokens_display = f"{tokens:,}" if tokens > 0 else "0"

    console.print(f"  Estimated tokens: [cyan]{tokens_display}[/cyan]")
    console.print(f"  Cost (Haiku): [green]{cost_haiku}[/green] | Cost (Sonnet): [yellow]{cost_sonnet}[/yellow]")
    console.print(f"  Complexity: {feature['effort']['complexity']}")
    console.print(f"  Risk: {feature['effort']['risk']}")
    console.print()


def show_implementation_plan(feature: dict):
    """Show implementation plan."""
    console.print("[bold]Implementation Plan:[/bold]")
    console.print()

    # Show token breakdown
    token_breakdown = feature["effort"].get("token_breakdown", {})
    if token_breakdown:
        console.print("[bold]Token Breakdown:[/bold]")
        context = token_breakdown.get("context", 0)
        reasoning = token_breakdown.get("reasoning", 0)
        output = token_breakdown.get("output", 0)
        total = feature["effort"]["estimated_tokens"]

        console.print(f"  Context:   {context:>6,} tokens  (reading files, docs)")
        console.print(f"  Reasoning: {reasoning:>6,} tokens  (planning, design)")
        console.print(f"  Output:    {output:>6,} tokens  (code, tests, docs)")
        console.print(f"  {'─' * 45}")
        console.print(f"  Total:     {total:>6,} tokens")
        console.print()

    console.print("[bold]Files to modify:[/bold]")
    for file in feature["implementation"]["files"]:
        file_path = Path(__file__).parent.parent / file
        if file_path.exists():
            console.print(f"  [green]✓[/green] {file}")
        else:
            console.print(f"  [yellow]+[/yellow] {file} (will create)")

    console.print()
    console.print("[bold]Changes required:[/bold]")
    for change in feature["implementation"]["changes"]:
        console.print(f"  • {change}")

    console.print()
    console.print("[bold]Testing required:[/bold]")
    for test in feature["testing"]:
        console.print(f"  • {test}")

    console.print()


def show_next_steps(worktree_path: str, branch_name: str, feature_id: str):
    """Show next steps."""
    console.print(
        Panel.fit(
            f"[bold green]✅ Ready to implement {feature_id}[/bold green]",
            border_style="green",
        )
    )
    console.print()

    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. [blue]cd {worktree_path}[/blue]")
    console.print("  2. Make changes to files listed above")
    console.print("  3. Run tests")
    console.print("  4. Commit changes")
    console.print(f"  5. Push branch: [blue]git push -u origin {branch_name}[/blue]")
    console.print("  6. Create PR")
    console.print(
        f"  7. Mark as completed: [blue]uv run scripts/feature-complete.py {feature_id}[/blue]"
    )
    console.print()

    console.print(f"[dim]Worktree: {worktree_path}[/dim]")
    console.print(f"[dim]Branch: {branch_name}[/dim]")
    console.print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        console.print("[red]Error: Feature ID required[/red]")
        console.print("Usage: uv run scripts/feature-execute.py FEATURE_ID")
        console.print()
        console.print("Available features:")
        data = load_features()
        for f in data["features"]:
            if f["status"] == "planned":
                console.print(f"  {f['id']}")
        sys.exit(1)

    feature_id = sys.argv[1]
    data = load_features()

    # Get feature
    feature = get_feature(data, feature_id)
    if not feature:
        console.print(f"[red]Error: Feature {feature_id} not found[/red]")
        sys.exit(1)

    # Show details
    show_feature_details(feature)

    # Check status
    if feature["status"] == "completed":
        console.print("[green]✓ Feature already completed[/green]")
        sys.exit(0)

    if feature["status"] == "blocked":
        console.print("[red]✗ Feature is blocked[/red]")
        sys.exit(1)

    # Check dependencies
    deps_met, unmet = check_dependencies(data, feature)
    if not deps_met:
        console.print("[bold]Checking dependencies...[/bold]")
        for dep_id, dep in unmet:
            dep_name = dep["name"] if dep else "Unknown"
            dep_status = dep["status"] if dep else "not found"
            console.print(f"  [red]✗ {dep_id}: {dep_name} (status: {dep_status})[/red]")

        console.print()
        console.print("[red]Error: Dependencies not met[/red]")
        console.print("Complete dependent features first, then try again")
        sys.exit(1)

    # Show implementation plan
    show_implementation_plan(feature)

    # Ask for confirmation
    if not Confirm.ask("Create worktree for this feature?"):
        console.print("Cancelled")
        sys.exit(0)

    console.print()

    # Create worktree
    console.print("[bold]Creating worktree...[/bold]")
    worktree_path, branch_name = create_worktree(feature_id)

    # Update status
    console.print()
    console.print("[bold]Updating feature status...[/bold]")
    update_feature_status(data, feature_id)

    # Commit status change
    commit_status_change(feature)

    # Show next steps
    console.print()
    show_next_steps(worktree_path, branch_name, feature_id)


if __name__ == "__main__":
    main()
