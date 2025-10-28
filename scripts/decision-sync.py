#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0"
# ]
# ///
"""
Decision Sync - Auto-populate decisions.yaml from conversation transcripts

Scans ~/.claude/projects/ for conversation transcripts and extracts:
- Research findings from extraction-optimized format
- Plans and designs
- Architectural decisions

Uses same extraction patterns as SessionEnd hook for consistency.

Usage:
    decision-sync.py [--dry-run] [--limit N] [--project PATH]

Options:
    --dry-run       Show what would be added without modifying files
    --limit N       Only process first N conversations (default: all)
    --project PATH  Specific project to scan (default: scan all projects)
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import argparse

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: uv add pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

# Hybrid import: Try shared module, fallback to embedded copy
try:
    # Try importing from shared lib (DRY when it works)
    sys.path.insert(0, str(Path(__file__).parent.parent / 'lib'))
    from extraction_patterns import (
        extract_designs,
        extract_decisions,
        extract_assistant_text,
        extract_research,
        extract_title
    )
except ImportError:
    # Fallback: Embedded copy (reliability when imports fail)
    def extract_assistant_text(entry):
        """Extract text from assistant message."""
        if entry.get('type') != 'assistant':
            return None
        message = entry.get('message', {})
        if not isinstance(message, dict):
            return None
        content = message.get('content', [])
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return ' '.join(b.get('text', '') for b in content if b.get('type') == 'text')
        return None

    def extract_title(content):
        """Extract title from markdown."""
        match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
        return match.group(1).strip() if match else None

    def extract_designs(transcript):
        """Find design proposals."""
        designs = []
        for i, entry in enumerate(transcript):
            text = extract_assistant_text(entry)
            if not text:
                continue
            patterns = [r"\*\*Type:\*\* Design", r"## Architecture", r"## Task Breakdown"]
            if sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns) >= 3:
                designs.append({'index': i, 'timestamp': entry.get('timestamp', ''), 'content': text, 'pattern_count': 3})
        return designs

    def extract_decisions(transcript):
        """Find decisions."""
        decisions = []
        for entry in transcript:
            text = extract_assistant_text(entry)
            if not text:
                continue
            if sum(len(re.findall(p, text, re.IGNORECASE)) for p in [r"## Decision:", r"### Alternatives"]) >= 2:
                decisions.append({'timestamp': entry.get('timestamp', ''), 'content': text})
        return decisions

    def extract_research(transcript):
        """Find research."""
        research = []
        for entry in transcript:
            text = extract_assistant_text(entry)
            if not text:
                continue
            match = re.search(r'## Research:\s*(.+?)$', text, re.MULTILINE)
            if match:
                research.append({'topic': match.group(1).strip(), 'findings': [text[:200]], 'timestamp': entry.get('timestamp', '')})
        return research

def find_conversation_transcripts(project_filter: Optional[str] = None) -> List[Path]:
    """
    Find all conversation transcript files.

    Args:
        project_filter: Optional path to specific project (e.g. /Users/user/project)

    Returns:
        List of transcript file paths
    """
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        return []

    transcripts = []

    if project_filter:
        # Convert project path to transcript directory name
        # /Users/shakes/DevProjects/contextune → -Users-shakes-DevProjects-contextune
        project_path = Path(project_filter).resolve()
        normalized = str(project_path).replace('/', '-')
        transcript_dir = projects_dir / normalized

        if transcript_dir.exists():
            transcripts.extend(transcript_dir.glob("*.jsonl"))
        else:
            # Try all subdirs that contain the project name
            project_name = project_path.name
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir() and project_name.lower() in project_dir.name.lower():
                    transcripts.extend(project_dir.glob("*.jsonl"))
    else:
        # Scan all projects
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                transcripts.extend(project_dir.glob("*.jsonl"))

    return transcripts

def read_transcript(transcript_path: Path) -> List[dict]:
    """Read conversation transcript JSONL file."""
    try:
        with open(transcript_path, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        if console:
            console.print(f"[yellow]Warning: Failed to read {transcript_path.name}: {e}[/yellow]")
        return []

# extract_research imported from lib or fallback above

def populate_from_transcripts(
    decisions_path: Path,
    transcripts: List[Path],
    dry_run: bool = False,
    limit: Optional[int] = None
) -> Dict[str, int]:
    """
    Populate decisions.yaml from conversation transcripts.

    Args:
        decisions_path: Path to decisions.yaml
        transcripts: List of transcript files to scan
        dry_run: If True, don't modify files
        limit: Max conversations to process

    Returns:
        Dict with counts of extracted items
    """
    stats = {
        'transcripts_scanned': 0,
        'research_found': 0,
        'plans_found': 0,
        'decisions_found': 0
    }

    all_research = []
    all_plans = []
    all_decisions = []

    if console:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        )
    else:
        progress = None

    with progress or DummyProgress():
        task = progress.add_task("Scanning transcripts...", total=len(transcripts)) if progress else None

        for i, transcript_path in enumerate(transcripts):
            if limit and i >= limit:
                break

            transcript = read_transcript(transcript_path)
            if not transcript:
                continue

            stats['transcripts_scanned'] += 1

            # Extract using SessionEnd hook patterns
            if extract_designs:
                designs = extract_designs(transcript)
                stats['plans_found'] += len(designs)
                all_plans.extend([{
                    'content': d['content'],
                    'timestamp': d['timestamp'],
                    'session': transcript_path.stem
                } for d in designs])

            if extract_decisions:
                decisions = extract_decisions(transcript)
                stats['decisions_found'] += len(decisions)
                all_decisions.extend([{
                    'content': d['content'],
                    'timestamp': d['timestamp'],
                    'session': transcript_path.stem
                } for d in decisions])

            # Extract research
            research = extract_research(transcript)
            stats['research_found'] += len(research)
            all_research.extend([{
                **r,
                'session': transcript_path.stem
            } for r in research])

            if progress:
                progress.update(task, advance=1)

    if console:
        console.print(f"\n[green]✅ Scanned {stats['transcripts_scanned']} transcripts[/green]")
        console.print(f"   Research: {stats['research_found']}")
        console.print(f"   Plans: {stats['plans_found']}")
        console.print(f"   Decisions: {stats['decisions_found']}")

    if not dry_run and (all_research or all_plans or all_decisions):
        # Load or create decisions.yaml
        if decisions_path.exists():
            with open(decisions_path) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {
                'metadata': {
                    'project': 'contextune',
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'last_scan': None,
                    'auto_population_enabled': True
                },
                'research': {'entries': []},
                'plans': {'entries': []},
                'decisions': {'entries': []},
                'features': {'entries': []}
            }

        # Append research entries
        if all_research:
            for i, research in enumerate(all_research[:50], 1):
                entry = {
                    'id': f'res-{i:03d}',
                    'topic': research['topic'],
                    'findings': research['findings'],
                    'category': 'research',
                    'conversation_link': {
                        'session_id': research['session'],
                        'timestamp': research['timestamp']
                    },
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                data['research']['entries'].append(entry)

        # Append plan entries (NEW!)
        if all_plans:
            for i, plan in enumerate(all_plans[:20], 1):  # Limit to 20
                title = extract_title(plan['content']) or f"Plan {i}"
                entry = {
                    'id': f'plan-{i:03d}',
                    'title': title,
                    'summary': plan['content'][:500] + '...',  # First 500 chars
                    'conversation_link': {
                        'session_id': plan['session'],
                        'timestamp': plan['timestamp']
                    },
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                data['plans']['entries'].append(entry)

        # Append decision entries (NEW!)
        if all_decisions:
            for i, decision in enumerate(all_decisions[:20], 1):
                title = extract_title(decision['content']) or f"Decision {i}"
                entry = {
                    'id': f'dec-{i:03d}',
                    'title': title,
                    'summary': decision['content'][:500] + '...',
                    'conversation_link': {
                        'session_id': decision['session'],
                        'timestamp': decision['timestamp']
                    },
                    'created_at': datetime.now().isoformat(),
                    'status': 'accepted'
                }
                data['decisions']['entries'].append(entry)

        # Update metadata
        data['metadata']['last_scan'] = datetime.now().isoformat()

        # Save
        with open(decisions_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        if console:
            console.print(f"\n[green]✅ Updated {decisions_path}[/green]")

    return stats

class DummyProgress:
    """Fallback if Rich not available."""
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def add_task(self, *args, **kwargs): return None
    def update(self, *args, **kwargs): pass

def main():
    parser = argparse.ArgumentParser(description="Auto-populate decisions.yaml from conversation transcripts")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be added")
    parser.add_argument('--limit', type=int, help="Process only first N conversations")
    parser.add_argument('--output', type=Path, default=Path('decisions.yaml'), help="decisions.yaml path")
    parser.add_argument('--project', type=str, help="Specific project path to scan")

    args = parser.parse_args()

    if console:
        console.print("\n[bold]🔍 Decision Sync - Scanning Conversation Transcripts[/bold]\n")

    # Find transcripts
    transcripts = find_conversation_transcripts(args.project)

    if not transcripts:
        if console:
            console.print("[yellow]No conversation transcripts found in ~/.claude/projects/[/yellow]")
        else:
            print("No transcripts found")
        return

    if console:
        console.print(f"Found {len(transcripts)} conversation transcripts\n")

    if args.limit:
        transcripts = transcripts[:args.limit]
        if console:
            console.print(f"[yellow]Limiting to first {args.limit} transcripts[/yellow]\n")

    # Populate from transcripts
    stats = populate_from_transcripts(
        args.output,
        transcripts,
        dry_run=args.dry_run,
        limit=args.limit
    )

    # Summary
    if console:
        table = Table(title="\nExtraction Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Transcripts Scanned", str(stats['transcripts_scanned']))
        table.add_row("Research Found", str(stats['research_found']))
        table.add_row("Plans Found", str(stats['plans_found']))
        table.add_row("Decisions Found", str(stats['decisions_found']))

        console.print(table)

        if args.dry_run:
            console.print("\n[yellow]🔒 Dry run - no files modified[/yellow]")
        else:
            console.print(f"\n[green]✅ decisions.yaml updated at {args.output}[/green]")

if __name__ == '__main__':
    main()
