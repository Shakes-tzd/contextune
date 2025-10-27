#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0.0",
# ]
# ///
"""
Feature Graph - Generate dependency graph visualization.

Usage:
    uv run scripts/feature-graph.py [--format FORMAT]

Formats:
    text (default) - ASCII visualization
    mermaid        - Mermaid diagram
    dot            - Graphviz DOT format
"""

import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel

console = Console()


def load_features() -> dict:
    """Load features.yaml."""
    features_file = Path(__file__).parent.parent / "features.yaml"

    if not features_file.exists():
        console.print("[red]Error: features.yaml not found[/red]")
        sys.exit(1)

    with open(features_file) as f:
        return yaml.safe_load(f)


def get_status_symbol(status: str) -> str:
    """Get symbol for status."""
    symbols = {
        "completed": "✓",
        "in_progress": "→",
        "planned": "○",
        "blocked": "✗",
        "research": "?",
    }
    return symbols.get(status, "○")


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


def text_format(data: dict):
    """Generate text format (ASCII art)."""
    console.print(
        Panel.fit(
            "[bold blue]Feature Dependency Graph[/bold blue]",
            border_style="blue",
        )
    )
    console.print()

    console.print("[bold]Legend:[/bold]")
    console.print("  [green]✓[/green] Completed")
    console.print("  [blue]→[/blue] In Progress")
    console.print("  [yellow]○[/yellow] Planned")
    console.print("  [red]✗[/red] Blocked")
    console.print()

    console.print("[bold]Dependency Tree:[/bold]")
    console.print()

    features = data["features"]

    for feature in features:
        feature_id = feature["id"]
        name = feature["name"]
        status = feature["status"]
        phase = feature.get("phase", 0)
        deps = feature.get("dependencies", [])
        blocks = feature.get("blocks", [])

        # Status symbol and color
        symbol = get_status_symbol(status)
        color = get_status_color(status)

        console.print(
            f"{symbol} [bold]{feature_id}[/bold]: {name} [dim][Phase {phase}][/dim]",
            style=color,
        )

        # Show dependencies (what this needs)
        if deps:
            for dep_id in deps:
                dep = next((f for f in features if f["id"] == dep_id), None)
                if dep:
                    dep_symbol = get_status_symbol(dep["status"])
                    console.print(
                        f"   [dim]├─ depends on:[/dim] {dep_id} [dim][{dep_symbol}][/dim]"
                    )

        # Show what this blocks
        if blocks:
            for blocked_id in blocks:
                blocked = next((f for f in features if f["id"] == blocked_id), None)
                if blocked:
                    blocked_symbol = get_status_symbol(blocked["status"])
                    console.print(
                        f"   [dim]└─ blocks:[/dim] {blocked_id} [dim][{blocked_symbol}][/dim]"
                    )

        # Show if independent
        if not deps and not blocks:
            console.print("   [dim]└─ independent (can execute in parallel)[/dim]")

        console.print()

    # Show phase grouping
    console.print("[bold]Phase Grouping:[/bold]")
    console.print()

    for phase in range(0, 5):
        phase_features = [f for f in features if f.get("phase") == phase]

        if phase_features:
            console.print(f"[bold blue]Phase {phase}:[/bold blue]")

            for feat in phase_features:
                symbol = get_status_symbol(feat["status"])
                console.print(f"  {symbol} {feat['id']}")

            console.print()

    # Show parallel execution groups
    console.print("[bold]Parallel Execution Groups:[/bold]")
    console.print()

    console.print("[bold green]Can execute in parallel (Phase 1):[/bold green]")
    phase1_independent = [
        f
        for f in features
        if f.get("phase") == 1
        and not f.get("dependencies")
        and f["status"] == "planned"
    ]

    if phase1_independent:
        for feat in phase1_independent:
            console.print(f"  • {feat['id']}")
    else:
        console.print("  [dim]None[/dim]")

    console.print()
    console.print("[bold yellow]Sequential (Phase 2 - depends on Phase 1):[/bold yellow]")
    phase2_dependent = [
        f
        for f in features
        if f.get("phase") == 2 and f.get("dependencies")
    ]

    if phase2_dependent:
        for feat in phase2_dependent:
            deps = ", ".join(feat.get("dependencies", []))
            console.print(f"  • {feat['id']} (needs: {deps})")
    else:
        console.print("  [dim]None[/dim]")


def mermaid_format(data: dict):
    """Generate Mermaid diagram format."""
    console.print("```mermaid")
    console.print("graph LR")
    console.print()

    features = data["features"]

    # Define nodes
    for feature in features:
        feature_id = feature["id"]
        name = feature["name"].replace('"', '\\"')
        status = feature["status"]

        style = {
            "completed": ":::completed",
            "in_progress": ":::in_progress",
            "blocked": ":::blocked",
        }.get(status, ":::planned")

        console.print(f"  {feature_id}[\"{name}\"]{style}")

    console.print()

    # Define edges (dependencies)
    for feature in features:
        feature_id = feature["id"]
        deps = feature.get("dependencies", [])

        if deps:
            for dep_id in deps:
                console.print(f"  {dep_id} --> {feature_id}")

    console.print()

    # Define styles
    console.print("  classDef completed fill:#90EE90,stroke:#006400")
    console.print("  classDef in_progress fill:#87CEEB,stroke:#00008B")
    console.print("  classDef blocked fill:#FFB6C1,stroke:#8B0000")
    console.print("  classDef planned fill:#FFFFE0,stroke:#DAA520")
    console.print("```")


def dot_format(data: dict):
    """Generate Graphviz DOT format."""
    console.print("digraph feature_dependencies {")
    console.print("  rankdir=LR;")
    console.print("  node [shape=box, style=rounded];")
    console.print()

    features = data["features"]

    # Define nodes
    for feature in features:
        feature_id = feature["id"]
        name = feature["name"].replace('"', '\\"')
        status = feature["status"]

        color = {
            "completed": "green",
            "in_progress": "blue",
            "blocked": "red",
        }.get(status, "yellow")

        console.print(
            f'  "{feature_id}" [label="{feature_id}\\n{name}", fillcolor={color}, style=filled];'
        )

    console.print()

    # Define edges
    for feature in features:
        feature_id = feature["id"]
        deps = feature.get("dependencies", [])

        if deps:
            for dep_id in deps:
                console.print(f'  "{dep_id}" -> "{feature_id}" [label="depends on"];')

    console.print("}")
    console.print()
    console.print("// Generate image with: dot -Tpng feature-graph.dot -o feature-graph.png")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate dependency graph")
    parser.add_argument(
        "--format",
        choices=["text", "mermaid", "dot"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()
    data = load_features()

    if args.format == "text":
        text_format(data)
    elif args.format == "mermaid":
        mermaid_format(data)
    elif args.format == "dot":
        dot_format(data)

    if args.format == "text":
        console.print()
        console.print("[dim]Commands:[/dim]")
        console.print(
            "  [dim]uv run scripts/feature-graph.py --format dot > graph.dot[/dim]"
        )
        console.print("  [dim]dot -Tpng graph.dot -o graph.png[/dim]")
        console.print(
            "  [dim]uv run scripts/feature-graph.py --format mermaid > GRAPH.md[/dim]"
        )
        console.print()


if __name__ == "__main__":
    main()
