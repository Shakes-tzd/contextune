#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0",
#     "typer>=0.9.0",
#     "readchar>=4.0"
# ]
# ///
"""
Interactive Plan Viewer - Browse decisions.yaml with arrow key navigation

Features:
- Arrow key navigation (↑/↓)
- Enter to view full plan
- Rich TUI with syntax highlighting
- Filter and search

Usage:
    plan-viewer.py              # Interactive mode with arrow keys
    plan-viewer.py view PLAN_ID # View specific plan
    plan-viewer.py search TOPIC # Search by topic
"""

import typer
from pathlib import Path
from typing import Optional, List
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich import box
from rich.text import Text
import readchar

app = typer.Typer(help="Interactive plan viewer for decisions.yaml")
console = Console()


def load_decisions(path: Path = Path("decisions.yaml")) -> dict:
    """Load decisions.yaml file."""
    if not path.exists():
        console.print(f"[red]Error: {path} not found[/red]")
        raise typer.Exit(1)

    with open(path) as f:
        return yaml.safe_load(f)


def get_all_entries(data: dict) -> List[dict]:
    """Get all entries (research, plans, decisions) with type info."""
    entries = []

    # Research entries
    for entry in data.get('research', {}).get('entries', []):
        entries.append({
            **entry,
            'entry_type': 'research',
            'display_title': entry.get('topic', 'Unknown')
        })

    # Plan entries
    for entry in data.get('plans', {}).get('entries', []):
        entries.append({
            **entry,
            'entry_type': 'plan',
            'display_title': entry.get('title', 'Unknown')
        })

    # Decision entries
    for entry in data.get('decisions', {}).get('entries', []):
        entries.append({
            **entry,
            'entry_type': 'decision',
            'display_title': entry.get('title', 'Unknown')
        })

    return entries


def render_list(entries: List[dict], selected_idx: int) -> Table:
    """Render plan list with selection highlighting."""
    table = Table(title="📋 Contextune Plans & Decisions", box=box.ROUNDED, show_header=True)
    table.add_column("", width=2)  # Selection marker
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Status", style="green", width=10)

    for i, entry in enumerate(entries):
        marker = "→" if i == selected_idx else " "
        entry_id = entry['id']
        title = entry['display_title'][:50]
        etype = entry['entry_type']
        status = entry.get('status', 'unknown')

        style = "bold yellow" if i == selected_idx else ""

        table.add_row(marker, entry_id, title, etype, status, style=style)

    return table


def render_detail(entry: dict) -> Panel:
    """Render full plan detail."""
    # Header
    header_text = f"""[bold]{entry['display_title']}[/bold]

[cyan]ID:[/cyan] {entry['id']}
[cyan]Type:[/cyan] {entry['entry_type']}
[cyan]Status:[/cyan] {entry.get('status', 'unknown')}
[cyan]Created:[/cyan] {entry.get('created_at', 'unknown')[:10]}
"""

    # Content
    content_parts = [header_text, "\n" + "─" * 70 + "\n"]

    if 'summary' in entry:
        # Render summary as Markdown
        content_parts.append(entry['summary'][:2000])  # Limit for readability

    # Conversation link
    if 'conversation_link' in entry:
        link = entry['conversation_link']
        content_parts.append(f"\n\n[dim]Session: {link.get('session_id', 'unknown')[:40]}[/dim]")

    full_content = "\n".join(content_parts)

    return Panel(
        full_content,
        title=f"📄 {entry['id']}",
        border_style="blue",
        subtitle="[dim]Press 'q' to go back[/dim]"
    )


@app.command()
def interactive():
    """Interactive mode with arrow key navigation."""

    data = load_decisions()
    entries = get_all_entries(data)

    if not entries:
        console.print("[yellow]No entries found in decisions.yaml[/yellow]")
        return

    selected_idx = 0
    mode = "list"  # "list" or "detail"
    current_entry = None

    console.clear()
    console.print("\n[bold cyan]📋 Interactive Plan Viewer[/bold cyan]")
    console.print("[dim]Arrow keys: Navigate | Enter: View | q: Quit[/dim]\n")

    with Live(render_list(entries, selected_idx), console=console, refresh_per_second=10) as live:
        while True:
            if mode == "list":
                # List mode
                live.update(render_list(entries, selected_idx))

                key = readchar.readkey()

                if key == readchar.key.UP:
                    selected_idx = max(0, selected_idx - 1)
                elif key == readchar.key.DOWN:
                    selected_idx = min(len(entries) - 1, selected_idx + 1)
                elif key == readchar.key.ENTER or key == '\n' or key == '\r':
                    # Switch to detail mode
                    current_entry = entries[selected_idx]
                    mode = "detail"
                    live.update(render_detail(current_entry))
                elif key.lower() == 'q':
                    break

            elif mode == "detail":
                # Detail mode
                key = readchar.readkey()

                if key.lower() == 'q' or key == readchar.key.ESC:
                    # Back to list
                    mode = "list"
                    live.update(render_list(entries, selected_idx))

    console.print("\n[dim]Goodbye![/dim]\n")


@app.command(name="list")
def list_plans(
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Filter by topic"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    entry_type: Optional[str] = typer.Option(None, "--type", help="Filter by type (research/plan/decision)"),
    sort_by: str = typer.Option("date", "--sort", help="Sort by: date, title, id")
):
    """List all plans in a formatted table."""

    data = load_decisions()
    entries = get_all_entries(data)

    # Apply filters
    if topic:
        entries = [e for e in entries if topic.lower() in e['display_title'].lower()]

    if status:
        entries = [e for e in entries if e.get('status') == status]

    if entry_type:
        entries = [e for e in entries if e['entry_type'] == entry_type]

    # Sort
    if sort_by == 'date':
        entries.sort(key=lambda e: e.get('created_at', ''), reverse=True)
    elif sort_by == 'title':
        entries.sort(key=lambda e: e['display_title'])
    elif sort_by == 'id':
        entries.sort(key=lambda e: e['id'])

    # Render table
    table = Table(title="📋 Contextune Plans & Decisions", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")

    for entry in entries:
        entry_id = entry['id']
        title = entry['display_title'][:50]
        etype = entry['entry_type']
        status = entry.get('status', 'unknown')

        table.add_row(entry_id, title, etype, status)

    console.print()
    console.print(table)
    console.print(f"\n[dim]Total: {len(entries)} entries[/dim]")
    console.print(f"[dim]Tip: Run 'plan-viewer.py' for interactive mode with arrow keys[/dim]")
    console.print()


@app.command()
def view(
    plan_id: str = typer.Argument(..., help="Plan ID to view (e.g., plan-012)")
):
    """View detailed plan content."""

    data = load_decisions()
    entries = get_all_entries(data)

    # Find entry
    entry = next((e for e in entries if e['id'] == plan_id), None)

    if not entry:
        console.print(f"[red]Error: Plan {plan_id} not found[/red]")
        raise typer.Exit(1)

    # Render detail
    console.print()
    console.print(render_detail(entry))
    console.print()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term"),
    show_content: bool = typer.Option(False, "--content", "-c", help="Show content snippets")
):
    """Search plans by topic/title."""

    data = load_decisions()
    entries = get_all_entries(data)

    # Search
    matches = [e for e in entries if query.lower() in e['display_title'].lower() or
               (query.lower() in e.get('summary', '').lower())]

    if not matches:
        console.print(f"[yellow]No results for '{query}'[/yellow]")
        return

    console.print(f"\n[green]Found {len(matches)} result(s) for '{query}'[/green]\n")

    for entry in matches:
        console.print(f"[cyan]{entry['id']}[/cyan]: {entry['display_title']}")
        if show_content and 'summary' in entry:
            console.print(f"  [dim]{entry['summary'][:200]}...[/dim]")
        console.print()


@app.command()
def stats():
    """Show statistics about decisions.yaml."""

    data = load_decisions()

    research_count = len(data.get('research', {}).get('entries', []))
    plan_count = len(data.get('plans', {}).get('entries', []))
    decision_count = len(data.get('decisions', {}).get('entries', []))
    feature_count = len(data.get('features', {}).get('entries', []))

    table = Table(title="📊 decisions.yaml Statistics", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green", justify="right")

    table.add_row("Research Entries", str(research_count))
    table.add_row("Plans", str(plan_count))
    table.add_row("Decisions", str(decision_count))
    table.add_row("Features", str(feature_count))
    table.add_row("Total", str(research_count + plan_count + decision_count + feature_count))

    console.print()
    console.print(table)

    metadata = data.get('metadata', {})
    console.print()
    console.print(f"[dim]Last scan: {metadata.get('last_scan', 'Never')[:19]}[/dim]")
    console.print(f"[dim]Version: {metadata.get('version', 'unknown')}[/dim]")
    console.print()


if __name__ == "__main__":
    # If no command specified, run interactive mode
    import sys
    if len(sys.argv) == 1:
        interactive()
    else:
        app()
