#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///

"""
SlashSense Statistics Command

Displays detection performance metrics and statistics.
Currently uses mock/example data for demonstration.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

# Mock statistics data for demonstration
MOCK_STATS = {
    "total_detections": 1247,
    "tier_performance": {
        "keyword": {
            "detections": 892,
            "avg_latency_ms": 0.05,
            "accuracy": 0.98
        },
        "model2vec": {
            "detections": 245,
            "avg_latency_ms": 0.18,
            "accuracy": 0.94
        },
        "semantic_router": {
            "detections": 110,
            "avg_latency_ms": 47.3,
            "accuracy": 0.89
        }
    },
    "top_commands": [
        {"command": "/sc:analyze", "count": 324},
        {"command": "/sc:implement", "count": 218},
        {"command": "/sc:test", "count": 187},
        {"command": "/sc:git", "count": 156},
        {"command": "/sc:improve", "count": 134}
    ],
    "confidence_distribution": {
        "0.7-0.8": 243,
        "0.8-0.9": 456,
        "0.9-1.0": 548
    }
}


def display_overview():
    """Display overview statistics."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SlashSense Detection Statistics[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    stats_table = Table(show_header=False, box=None, padding=(0, 2))
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green bold")

    stats_table.add_row("Total Detections", f"{MOCK_STATS['total_detections']:,}")
    stats_table.add_row("Keyword Matches", f"{MOCK_STATS['tier_performance']['keyword']['detections']:,}")
    stats_table.add_row("Model2Vec Matches", f"{MOCK_STATS['tier_performance']['model2vec']['detections']:,}")
    stats_table.add_row("Semantic Router Matches", f"{MOCK_STATS['tier_performance']['semantic_router']['detections']:,}")

    console.print(Panel(stats_table, title="[bold]Overview[/bold]", border_style="blue"))
    console.print()


def display_tier_performance():
    """Display tier-by-tier performance metrics."""
    tier_table = Table(show_header=True, box=None, padding=(0, 2))
    tier_table.add_column("Tier", style="cyan bold")
    tier_table.add_column("Detections", justify="right", style="green")
    tier_table.add_column("Avg Latency", justify="right", style="yellow")
    tier_table.add_column("Accuracy", justify="right", style="magenta")
    tier_table.add_column("Performance", justify="left")

    for tier_name, tier_data in MOCK_STATS["tier_performance"].items():
        # Create performance bar
        accuracy_pct = int(tier_data["accuracy"] * 100)
        bar = "█" * (accuracy_pct // 5) + "░" * (20 - (accuracy_pct // 5))

        tier_table.add_row(
            tier_name.capitalize(),
            f"{tier_data['detections']:,}",
            f"{tier_data['avg_latency_ms']:.2f}ms",
            f"{accuracy_pct}%",
            f"[green]{bar}[/green]"
        )

    console.print(Panel(tier_table, title="[bold]Tier Performance[/bold]", border_style="blue"))
    console.print()


def display_top_commands():
    """Display most frequently detected commands."""
    cmd_table = Table(show_header=True, box=None, padding=(0, 2))
    cmd_table.add_column("Rank", style="cyan", justify="right")
    cmd_table.add_column("Command", style="green bold")
    cmd_table.add_column("Count", justify="right", style="yellow")
    cmd_table.add_column("Percentage", justify="right", style="magenta")

    total = MOCK_STATS["total_detections"]

    for idx, cmd_data in enumerate(MOCK_STATS["top_commands"], 1):
        percentage = (cmd_data["count"] / total) * 100
        cmd_table.add_row(
            f"#{idx}",
            cmd_data["command"],
            f"{cmd_data['count']:,}",
            f"{percentage:.1f}%"
        )

    console.print(Panel(cmd_table, title="[bold]Top 5 Commands[/bold]", border_style="blue"))
    console.print()


def display_confidence_distribution():
    """Display confidence score distribution."""
    console.print(Panel.fit(
        "[bold]Confidence Score Distribution[/bold]",
        border_style="blue"
    ))
    console.print()

    total = sum(MOCK_STATS["confidence_distribution"].values())

    for range_label, count in MOCK_STATS["confidence_distribution"].items():
        percentage = (count / total) * 100
        bar_length = int(percentage / 2)  # Scale to fit in terminal
        bar = "█" * bar_length

        console.print(f"  [cyan]{range_label}[/cyan]: [green]{bar}[/green] {count:,} ({percentage:.1f}%)")

    console.print()


def display_recommendations():
    """Display performance recommendations."""
    recommendations = []

    # Check tier usage
    keyword_pct = (MOCK_STATS['tier_performance']['keyword']['detections'] /
                   MOCK_STATS['total_detections']) * 100

    if keyword_pct < 60:
        recommendations.append(
            "[yellow]Consider adding more keyword patterns to improve fast-path performance[/yellow]"
        )

    semantic_count = MOCK_STATS['tier_performance']['semantic_router']['detections']
    if semantic_count > 200:
        recommendations.append(
            "[yellow]High semantic router usage detected. Consider promoting common patterns to Model2Vec tier[/yellow]"
        )

    if recommendations:
        console.print(Panel(
            "\n".join(f"• {rec}" for rec in recommendations),
            title="[bold]Recommendations[/bold]",
            border_style="yellow"
        ))
        console.print()


def main():
    """Main entry point for slashsense:stats command."""
    try:
        display_overview()
        display_tier_performance()
        display_top_commands()
        display_confidence_distribution()
        display_recommendations()

        console.print("[dim]Note: These are example statistics. Real-time tracking coming soon![/dim]")
        console.print()

        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Statistics display cancelled.[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
