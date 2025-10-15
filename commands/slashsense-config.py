#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///

"""
SlashSense Configuration Command

Displays and creates default configuration for SlashSense plugin.
Creates ~/.claude/plugins/slashsense/data/user_patterns.json if missing.
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()

DEFAULT_CONFIG = {
    "enabled": True,
    "confidence_threshold": 0.7,
    "tiers": {
        "keyword": True,
        "model2vec": True,
        "semantic_router": True
    },
    "custom_mappings": {
        "make it pretty": "/sc:improve",
        "ship it": "/sc:git"
    }
}


def get_config_path() -> Path:
    """Get the path to the user configuration file."""
    home = Path.home()
    config_path = home / ".claude" / "plugins" / "slashsense" / "data" / "user_patterns.json"
    return config_path


def ensure_config_exists(config_path: Path) -> dict:
    """
    Ensure configuration file exists, create with defaults if missing.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    try:
        if not config_path.exists():
            # Create parent directories
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write default configuration
            with open(config_path, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)

            console.print(f"[green]Created default configuration at:[/green] {config_path}")
            return DEFAULT_CONFIG
        else:
            # Read existing configuration
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
    except Exception as e:
        console.print(f"[red]Error handling configuration:[/red] {e}", file=sys.stderr)
        return DEFAULT_CONFIG


def display_config(config: dict, config_path: Path):
    """
    Display configuration using Rich formatting.

    Args:
        config: Configuration dictionary
        config_path: Path to configuration file
    """
    # Create main panel
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SlashSense Configuration[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    # Display file location
    console.print(f"[dim]Configuration file:[/dim] {config_path}")
    console.print()

    # Create status table
    status_table = Table(show_header=False, box=None, padding=(0, 2))
    status_table.add_column("Setting", style="cyan")
    status_table.add_column("Value", style="green")

    status_table.add_row("Enabled", "✓ Yes" if config.get("enabled", True) else "✗ No")
    status_table.add_row("Confidence Threshold", str(config.get("confidence_threshold", 0.7)))

    console.print(Panel(status_table, title="[bold]General Settings[/bold]", border_style="blue"))
    console.print()

    # Display tier configuration
    tiers = config.get("tiers", {})
    tier_table = Table(show_header=True, box=None, padding=(0, 2))
    tier_table.add_column("Tier", style="cyan")
    tier_table.add_column("Status", style="green")
    tier_table.add_column("Latency Target", style="yellow")

    tier_table.add_row(
        "Keyword",
        "✓ Enabled" if tiers.get("keyword", True) else "✗ Disabled",
        "<0.1ms"
    )
    tier_table.add_row(
        "Model2Vec",
        "✓ Enabled" if tiers.get("model2vec", True) else "✗ Disabled",
        "<1ms"
    )
    tier_table.add_row(
        "Semantic Router",
        "✓ Enabled" if tiers.get("semantic_router", True) else "✗ Disabled",
        "<100ms"
    )

    console.print(Panel(tier_table, title="[bold]Detection Tiers[/bold]", border_style="blue"))
    console.print()

    # Display custom mappings
    custom_mappings = config.get("custom_mappings", {})
    if custom_mappings:
        mapping_table = Table(show_header=True, box=None, padding=(0, 2))
        mapping_table.add_column("Natural Language", style="cyan")
        mapping_table.add_column("Command", style="green")

        for phrase, command in custom_mappings.items():
            mapping_table.add_row(phrase, command)

        console.print(Panel(mapping_table, title="[bold]Custom Mappings[/bold]", border_style="blue"))
        console.print()

    # Display raw JSON configuration
    json_str = json.dumps(config, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="[bold]Raw Configuration (JSON)[/bold]", border_style="green"))
    console.print()

    # Display help text
    console.print("[dim]To edit configuration, modify:[/dim]")
    console.print(f"[dim]{config_path}[/dim]")
    console.print()


def main():
    """Main entry point for slashsense:config command."""
    try:
        config_path = get_config_path()
        config = ensure_config_exists(config_path)
        display_config(config, config_path)
        return 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Configuration display cancelled.[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
