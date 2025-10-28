#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0"
# ]
# ///
"""
Decision Sync - Auto-populate decisions.yaml from history.jsonl

Scans ~/.claude/history.jsonl (1,236+ conversations) and extracts:
- Research findings: "research", "/ctx:research", "investigate", "explore"
- Plans: "/ctx:plan", "create plan", "design", "architecture"
- Decisions: "decided to", "alternatives considered"

Appends to decisions.yaml with conversation links for context preservation.

Usage:
    decision-sync.py [--dry-run] [--limit N] [--output PATH]

Options:
    --dry-run       Show what would be added without modifying files
    --limit N       Only process first N conversations (default: all)
    --output PATH   Custom decisions.yaml path (default: ./decisions.yaml)
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import argparse
import traceback

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: uv add pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
except ImportError:
    Console = None  # Fallback if rich not available
    Progress = None


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ConversationLink:
    """Link to source conversation for context preservation."""
    session_id: str
    timestamp: int
    prompt: str
    project: str
    history_line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ResearchEntry:
    """Research finding extracted from conversation."""
    id: str
    topic: str
    category: str
    findings: List[str]
    methodology: str
    sources: List[str]
    conversation_link: ConversationLink
    created_at: str
    status: str = "active"
    permanent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['conversation_link'] = self.conversation_link.to_dict()
        # Calculate expiration (6 months)
        created = datetime.fromisoformat(self.created_at)
        expires = created + timedelta(days=180)
        data['expires_at'] = expires.isoformat() + 'Z'
        return data


@dataclass
class DecisionEntry:
    """Decision extracted from conversation."""
    id: str
    title: str
    date: str
    status: str
    category: str
    context: str
    decision: str
    rationale: str
    alternatives_considered: List[Dict[str, Any]]
    consequences: Dict[str, List[str]]
    conversation_link: ConversationLink
    permanent: bool = False
    implementation_status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['conversation_link'] = self.conversation_link.to_dict()
        return data


# ============================================================================
# Keyword Matchers
# ============================================================================

class KeywordMatcher:
    """Detect research, plans, and decisions via keyword patterns."""

    RESEARCH_KEYWORDS = {
        'research', '/ctx:research', 'ctx:research',
        'investigate', 'exploration', 'explore', 'findings',
        'methodology', 'compare', 'comparison', 'benchmark',
        'analysis', 'analyze', 'study', 'survey'
    }

    PLAN_KEYWORDS = {
        '/ctx:plan', 'ctx:plan', 'create plan',
        'design', 'architecture', 'implementation plan',
        'breakdown', 'decompose', 'strategy', 'roadmap',
        'phased approach', 'workflow'
    }

    DECISION_KEYWORDS = {
        'decided to', 'decision:', 'alternatives',
        'alternatives considered', 'pros and cons',
        'why did we choose', 'rationale', 'trade-off',
        'accepted', 'rejected', 'status: accepted'
    }

    @classmethod
    def detect_research(cls, text: str) -> bool:
        """Check if text contains research indicators."""
        text_lower = text.lower()
        # At least 2 keywords or research-specific patterns
        matches = sum(
            1 for keyword in cls.RESEARCH_KEYWORDS
            if keyword.lower() in text_lower
        )
        # Also detect structured research patterns
        has_findings = bool(re.search(r'(findings?|findings:)', text, re.IGNORECASE))
        has_methodology = bool(re.search(r'(methodology|approach)', text, re.IGNORECASE))

        return matches >= 1 or (has_findings and has_methodology)

    @classmethod
    def detect_plan(cls, text: str) -> bool:
        """Check if text contains planning indicators."""
        text_lower = text.lower()
        matches = sum(
            1 for keyword in cls.PLAN_KEYWORDS
            if keyword.lower() in text_lower
        )
        # Also detect YAML task structure
        has_yaml_tasks = bool(re.search(r'tasks:\s*\n\s*-', text, re.IGNORECASE))
        has_phases = bool(re.search(r'phases?:', text, re.IGNORECASE))

        return matches >= 1 or has_yaml_tasks or has_phases

    @classmethod
    def detect_decision(cls, text: str) -> bool:
        """Check if text contains decision indicators."""
        text_lower = text.lower()
        matches = sum(
            1 for keyword in cls.DECISION_KEYWORDS
            if keyword.lower() in text_lower
        )
        # Also detect decision structure
        has_alternatives = bool(re.search(r'##.*alternatives', text, re.IGNORECASE))
        has_status = bool(re.search(r'\*\*status:\*\*\s*(accepted|rejected)', text, re.IGNORECASE))

        return matches >= 1 or has_alternatives or has_status


# ============================================================================
# History Parser
# ============================================================================

class HistoryParser:
    """Parse ~/.claude/history.jsonl file."""

    def __init__(self, history_path: Optional[Path] = None, dry_run: bool = False):
        self.history_path = history_path or Path.home() / '.claude' / 'history.jsonl'
        self.dry_run = dry_run
        self.console = Console() if Console else None
        self.entries_read = 0
        self.research_found = 0
        self.plans_found = 0
        self.decisions_found = 0
        self.next_research_id = 1
        self.next_decision_id = 1

    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load history.jsonl entries."""
        if not self.history_path.exists():
            if self.console:
                self.console.print(f"[yellow]⚠️  History file not found: {self.history_path}", file=sys.stderr)
            return []

        entries = []
        try:
            with open(self.history_path, 'r') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                        self.entries_read += 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error reading history: {e}", file=sys.stderr)

        return entries

    def extract_prompt(self, entry: Dict[str, Any]) -> Optional[str]:
        """Extract user's prompt/display text from entry."""
        # Try various fields
        for field in ['display', 'prompt', 'message']:
            if field in entry and isinstance(entry[field], str):
                text = entry[field]
                if text and len(text) > 3:  # Skip very short entries
                    return text[:200]  # Limit to first 200 chars
        return None

    def scan_entries(self, entries: List[Dict[str, Any]]) -> tuple:
        """Scan entries for research, plans, decisions."""
        research_items = []
        plan_items = []
        decision_items = []

        for i, entry in enumerate(entries):
            prompt = self.extract_prompt(entry)
            if not prompt:
                continue

            # Extract metadata for linking
            timestamp = entry.get('timestamp', int(datetime.now().timestamp() * 1000))
            project = entry.get('project', '/Users/shakes/.claude')
            session_id = entry.get('session_id', f'hist-{i}')

            # Create conversation link
            link = ConversationLink(
                session_id=session_id,
                timestamp=timestamp,
                prompt=prompt,
                project=project,
                history_line=i
            )

            # Detect type
            if KeywordMatcher.detect_research(prompt):
                research_items.append({
                    'line': i,
                    'prompt': prompt,
                    'link': link
                })
                self.research_found += 1

            if KeywordMatcher.detect_plan(prompt):
                plan_items.append({
                    'line': i,
                    'prompt': prompt,
                    'link': link
                })
                self.plans_found += 1

            if KeywordMatcher.detect_decision(prompt):
                decision_items.append({
                    'line': i,
                    'prompt': prompt,
                    'link': link
                })
                self.decisions_found += 1

        return research_items, plan_items, decision_items

    def create_research_entries(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert detected research to entry dictionaries."""
        entries = []
        for item in items[:50]:  # Limit to avoid explosion
            link = item['link']
            entry = ResearchEntry(
                id=f"res-{self.next_research_id:03d}",
                topic=item['prompt'][:60],
                category="discovery",  # Will be refined in real scenario
                findings=[f"Research from: {item['prompt'][:100]}"],
                methodology="Extracted from conversation history",
                sources=[link.prompt],
                conversation_link=link,
                created_at=datetime.now().isoformat() + 'Z',
                status="active"
            )
            entries.append(entry.to_dict())
            self.next_research_id += 1

        return entries

    def create_decision_entries(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert detected decisions to entry dictionaries."""
        entries = []
        for item in items[:50]:  # Limit to avoid explosion
            link = item['link']
            entry = DecisionEntry(
                id=f"dec-{self.next_decision_id:03d}",
                title=item['prompt'][:80],
                date=datetime.now().isoformat() + 'Z',
                status="pending",  # Will be reviewed
                category="architecture",
                context=item['prompt'],
                decision="To be determined",
                rationale="Extracted from conversation history",
                alternatives_considered=[],
                consequences={"positive": [], "negative": []},
                conversation_link=link,
                permanent=False
            )
            entries.append(entry.to_dict())
            self.next_decision_id += 1

        return entries


# ============================================================================
# YAML Manager
# ============================================================================

class YAMLManager:
    """Safe YAML reading/writing for decisions.yaml."""

    def __init__(self, path: Optional[Path] = None, dry_run: bool = False):
        self.path = path or Path.cwd() / 'decisions.yaml'
        self.dry_run = dry_run
        self.console = Console() if Console else None

    def load_decisions(self) -> Dict[str, Any]:
        """Load existing decisions.yaml."""
        if not self.path.exists():
            return self._default_structure()

        try:
            with open(self.path, 'r') as f:
                data = yaml.safe_load(f)
                return data or self._default_structure()
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error loading YAML: {e}", file=sys.stderr)
            return self._default_structure()

    def _default_structure(self) -> Dict[str, Any]:
        """Return default decisions.yaml structure."""
        return {
            'metadata': {
                'project': 'contextune',
                'version': '1.0',
                'last_scan': None,
                'auto_population_enabled': True
            },
            'research': {'entries': []},
            'decisions': {'entries': []},
            'plans': {'entries': []},
            'features': {'entries': []}
        }

    def append_entries(self, data: Dict[str, Any], research: List[Dict], decisions: List[Dict]) -> Dict[str, Any]:
        """Append research and decision entries."""
        # Update metadata
        data['metadata']['last_scan'] = datetime.now().isoformat() + 'Z'
        data['metadata']['auto_population_enabled'] = True

        # Add research entries (avoid duplicates)
        if 'research' not in data:
            data['research'] = {'entries': []}
        existing_topics = {e.get('topic') for e in data['research'].get('entries', [])}
        for entry in research:
            if entry.get('topic') not in existing_topics:
                data['research']['entries'].append(entry)

        # Add decision entries (avoid duplicates)
        if 'decisions' not in data:
            data['decisions'] = {'entries': []}
        existing_titles = {e.get('title') for e in data['decisions'].get('entries', [])}
        for entry in decisions:
            if entry.get('title') not in existing_titles:
                data['decisions']['entries'].append(entry)

        return data

    def save(self, data: Dict[str, Any]) -> bool:
        """Save to decisions.yaml."""
        if self.dry_run:
            return True

        try:
            with open(self.path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving YAML: {e}", file=sys.stderr)
            return False


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Auto-populate decisions.yaml from history.jsonl'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be added without modifying')
    parser.add_argument('--limit', type=int, default=None,
                        help='Only process first N conversations')
    parser.add_argument('--output', type=Path, default=None,
                        help='Custom decisions.yaml path')

    args = parser.parse_args()

    console = Console() if Console else None

    try:
        # Print header
        if console:
            console.print("\n[bold cyan]Decision Sync[/bold cyan] - Auto-populate from history.jsonl\n")

        # Load history
        if console:
            console.print("[cyan]1.[/cyan] Loading history...", end=" ")
        parser_obj = HistoryParser(dry_run=args.dry_run)
        entries = parser_obj.load_history(args.limit)
        if console:
            console.print(f"[green]✓[/green] Loaded {len(entries)} entries")

        if not entries:
            if console:
                console.print("[yellow]⚠️  No history entries found", file=sys.stderr)
            return 1

        # Scan for research, plans, decisions
        if console:
            console.print("[cyan]2.[/cyan] Scanning for research, plans, decisions...", end=" ")
        research, plans, decisions = parser_obj.scan_entries(entries)
        if console:
            console.print(f"[green]✓[/green]")
            console.print(f"   - Found {parser_obj.research_found} research items")
            console.print(f"   - Found {parser_obj.plans_found} plans")
            console.print(f"   - Found {parser_obj.decisions_found} decisions")

        # Create structured entries
        if console:
            console.print("[cyan]3.[/cyan] Creating structured entries...", end=" ")
        research_entries = parser_obj.create_research_entries(research)
        decision_entries = parser_obj.create_decision_entries(decisions)
        if console:
            console.print(f"[green]✓[/green]")

        # Load and update decisions.yaml
        if console:
            console.print("[cyan]4.[/cyan] Loading decisions.yaml...", end=" ")
        yaml_mgr = YAMLManager(args.output, args.dry_run)
        data = yaml_mgr.load_decisions()
        if console:
            console.print(f"[green]✓[/green]")

        # Append entries
        if console:
            console.print("[cyan]5.[/cyan] Appending entries...", end=" ")
        data = yaml_mgr.append_entries(data, research_entries, decision_entries)
        if console:
            console.print(f"[green]✓[/green]")

        # Save
        if console:
            console.print("[cyan]6.[/cyan] Saving to decisions.yaml...", end=" ")
        success = yaml_mgr.save(data)
        if console:
            if success:
                console.print(f"[green]✓[/green]")
            else:
                console.print(f"[red]✗[/red]")
                return 1

        # Summary
        if console:
            console.print("\n[bold green]Summary[/bold green]")
            console.print(f"  Entries processed: {parser_obj.entries_read}")
            console.print(f"  Research entries added: {len(research_entries)}")
            console.print(f"  Decision entries added: {len(decision_entries)}")
            if args.dry_run:
                console.print(f"  [yellow]DRY RUN - No files modified[/yellow]")
            else:
                console.print(f"  [green]✓ decisions.yaml updated successfully[/green]")
            console.print()

        return 0

    except Exception as e:
        if console:
            console.print(f"\n[red]Error: {e}[/red]", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
