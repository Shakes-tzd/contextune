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

# Import extraction functions from session_end_extractor
sys.path.insert(0, str(Path(__file__).parent.parent / 'hooks'))

try:
    from session_end_extractor import (
        extract_designs,
        extract_decisions,
        extract_assistant_text
    )
except ImportError:
    print("Warning: Could not import from session_end_extractor, using fallback", file=sys.stderr)
    extract_designs = None
    extract_decisions = None
    extract_assistant_text = None

def find_conversation_transcripts(project_filter: Optional[str] = None) -> List[Path]:
    """
    Find all conversation transcript files.

    Args:
        project_filter: Optional path to specific project

    Returns:
        List of transcript file paths
    """
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        return []

    transcripts = []

    if project_filter:
        # Scan specific project only
        project_transcripts = Path(project_filter).parent
        if project_transcripts.exists():
            transcripts.extend(project_transcripts.glob("*.jsonl"))
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

def extract_research_from_transcript(transcript: List[dict]) -> List[dict]:
    """
    Extract research findings from conversation transcript.

    Looks for extraction-optimized format:
    - ## Research: [Topic]
    - ### Key Findings (YAML blocks)
    """
    research_entries = []

    for entry in transcript:
        text = extract_assistant_text(entry) if extract_assistant_text else None
        if not text:
            continue

        # Detect research pattern
        research_match = re.search(r'## Research:\s*(.+?)$', text, re.MULTILINE)
        if not research_match:
            continue

        topic = research_match.group(1).strip()

        # Extract findings YAML block
        findings_yaml = re.search(r'### Key Findings\n\n```yaml\n(.*?)```', text, re.DOTALL)
        findings = []

        if findings_yaml:
            try:
                findings_data = yaml.safe_load(findings_yaml.group(1))
                if isinstance(findings_data, dict) and 'findings' in findings_data:
                    findings = [f.get('finding', '') for f in findings_data['findings']]
            except:
                pass

        # Extract recommendations
        recommendations = re.findall(r'###? Recommendations?\n\n(.+?)(?=\n##|\Z)', text, re.DOTALL)

        research_entries.append({
            'topic': topic,
            'findings': findings if findings else [f"Research from conversation about {topic}"],
            'recommendations': recommendations[0] if recommendations else '',
            'timestamp': entry.get('timestamp', ''),
            'content_snippet': text[:500]
        })

    return research_entries

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
            research = extract_research_from_transcript(transcript)
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

        # Append research entries (with meaningful content!)
        if all_research:
            for i, research in enumerate(all_research[:50], 1):  # Limit to 50
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
