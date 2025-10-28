"""
Decision-Link: Link decisions.yaml entries to observability_db.py sessions.

This module enables full context traceability by linking decisions to observability
sessions based on timestamp matching. The result is a complete chain:
  conversation → session → detections → performance metrics

Features:
- Match timestamps between decisions.yaml and observability DB sessions
- Link session_id from conversations to sessions table
- Add observability_link fields for traceability
- Dry-run mode for safe testing
- Rich progress reporting with detailed output
"""

import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class DecisionLinker:
    """Links decisions.yaml entries to observability DB sessions."""

    def __init__(self, db_path: str, decisions_path: str, dry_run: bool = False):
        """Initialize the linker with database and decisions file paths.

        Args:
            db_path: Path to observability.db
            decisions_path: Path to decisions.yaml
            dry_run: If True, don't write changes to decisions.yaml
        """
        self.db_path = Path(db_path)
        self.decisions_path = Path(decisions_path)
        self.dry_run = dry_run
        self.console = Console()

        # Validate paths
        if not self.db_path.exists():
            self.console.print(f"[red]Error: Database not found: {self.db_path}[/red]")
            sys.exit(1)

        if not self.decisions_path.exists():
            self.console.print(
                f"[red]Error: Decisions file not found: {self.decisions_path}[/red]"
            )
            sys.exit(1)

    def load_decisions(self) -> dict[str, Any]:
        """Load decisions.yaml file.

        Returns:
            Parsed YAML content as dictionary
        """
        try:
            with open(self.decisions_path) as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            self.console.print(f"[red]Error parsing YAML: {e}[/red]")
            sys.exit(1)

    def save_decisions(self, data: dict[str, Any]) -> None:
        """Save decisions to decisions.yaml file.

        Args:
            data: Decisions dictionary to save
        """
        if self.dry_run:
            self.console.print("[yellow]Dry-run: Skipping file write[/yellow]")
            return

        try:
            with open(self.decisions_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            self.console.print(
                f"[green]Saved decisions to {self.decisions_path}[/green]"
            )
        except (OSError, yaml.YAMLError) as e:
            self.console.print(f"[red]Error saving YAML: {e}[/red]")
            sys.exit(1)

    def query_sessions(self) -> list[dict[str, Any]]:
        """Query observability DB for all sessions.

        Returns:
            List of session records with session_id and start_time
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT session_id, start_time, end_time, total_detections
                    FROM sessions
                    ORDER BY start_time DESC
                    """
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.console.print(f"[red]Database error: {e}[/red]")
            return []

    def query_detections_for_session(
        self, session_id: str
    ) -> list[dict[str, Any]]:
        """Query detections for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            List of detection records for the session
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, command, confidence, method, timestamp
                    FROM detection_history
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (session_id,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.console.print(f"[red]Database error: {e}[/red]")
            return []

    def find_matching_session(
        self, timestamp_ms: int, tolerance_ms: int = 5000
    ) -> dict[str, Any] | None:
        """Find session matching a given timestamp.

        Matches based on whether timestamp falls within session duration.
        Uses tolerance for fuzzy matching (default 5 seconds).

        Args:
            timestamp_ms: Timestamp in milliseconds
            tolerance_ms: Tolerance window in milliseconds

        Returns:
            Session record if found, None otherwise
        """
        sessions = self.query_sessions()

        # Convert timestamp to seconds (DB uses seconds)
        timestamp_sec = timestamp_ms / 1000

        for session in sessions:
            start_time = session["start_time"]
            end_time = session.get("end_time")

            # Check if timestamp is within session bounds (with tolerance)
            if start_time - tolerance_ms / 1000 <= timestamp_sec <= (
                end_time or time.time()
            ) + tolerance_ms / 1000:
                return session

        return None

    def parse_timestamp(self, timestamp_str: str) -> int | None:
        """Parse timestamp string to milliseconds.

        Supports ISO 8601 format: "2025-10-27T15:00:00Z"

        Args:
            timestamp_str: Timestamp string

        Returns:
            Timestamp in milliseconds, or None if parsing fails
        """
        try:
            # Try ISO 8601 format
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except (ValueError, AttributeError):
            return None

    def link_decisions(self) -> dict[str, Any]:
        """Link decisions to observability sessions.

        Returns:
            Updated decisions dictionary with observability_link fields
        """
        decisions = self.load_decisions()

        if "decisions" not in decisions or not decisions["decisions"].get("entries"):
            self.console.print("[yellow]No decision entries to link[/yellow]")
            return decisions

        entries = decisions["decisions"]["entries"]
        linked_count = 0
        skipped_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                f"Linking {len(entries)} decision entries...", total=len(entries)
            )

            for entry in entries:
                progress.update(task, advance=1)

                # Get timestamp from entry
                if "created_at" not in entry:
                    progress.console.print(
                        "  [yellow]Skipped: No created_at timestamp[/yellow]"
                    )
                    skipped_count += 1
                    continue

                timestamp_ms = self.parse_timestamp(entry["created_at"])
                if timestamp_ms is None:
                    progress.console.print(
                        "  [yellow]Skipped: Could not parse timestamp[/yellow]"
                    )
                    skipped_count += 1
                    continue

                # Find matching session
                matching_session = self.find_matching_session(timestamp_ms)
                if matching_session is None:
                    progress.console.print(
                        f"  [yellow]No session found for {entry.get('id', 'unknown')}[/yellow]"
                    )
                    skipped_count += 1
                    continue

                # Add observability link
                session_id = matching_session["session_id"]
                detections = self.query_detections_for_session(session_id)

                entry["observability_link"] = {
                    "session_id": session_id,
                    "timestamp": matching_session["start_time"],
                    "detection_count": len(detections),
                    "linked_at": datetime.utcnow().isoformat() + "Z",
                }

                if detections:
                    entry["observability_link"]["first_detection"] = {
                        "command": detections[0]["command"],
                        "confidence": detections[0]["confidence"],
                        "method": detections[0]["method"],
                    }

                linked_count += 1

        # Display summary
        self.console.print()
        summary_table = Table(title="Decision Linking Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="green")
        summary_table.add_row("Total entries", str(len(entries)))
        summary_table.add_row("Successfully linked", str(linked_count))
        summary_table.add_row("Skipped", str(skipped_count))
        self.console.print(summary_table)

        return decisions

    def run(self) -> None:
        """Execute the linking process."""
        self.console.print("[bold blue]Decision-Link: Observability DB Linking[/bold blue]")
        self.console.print(f"Database: {self.db_path}")
        self.console.print(f"Decisions: {self.decisions_path}")

        if self.dry_run:
            self.console.print("[yellow]Mode: DRY-RUN (no changes will be written)[/yellow]")

        self.console.print()

        # Link decisions
        updated_decisions = self.link_decisions()

        # Save results
        if not self.dry_run:
            self.save_decisions(updated_decisions)
            self.console.print("[green]Successfully updated decisions.yaml[/green]")
        else:
            self.console.print("[yellow]Dry-run complete (no files modified)[/yellow]")

        self.console.print("[bold green]Complete![/bold green]")
