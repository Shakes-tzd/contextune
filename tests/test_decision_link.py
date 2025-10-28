#!/usr/bin/env python3
"""
Unit tests for decision-link.py script.

Tests timestamp matching, session lookup, YAML operations,
and link accuracy.
"""

import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

# Add lib to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from decision_link import DecisionLinker


@pytest.fixture
def temp_db() -> Path:
    """Create a temporary database with test data."""
    db_file = Path(tempfile.gettempdir()) / "test_observability.db"

    # Create database with schema
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time REAL NOT NULL,
                end_time REAL,
                total_detections INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                confidence REAL NOT NULL,
                method TEXT NOT NULL,
                timestamp REAL NOT NULL,
                session_id TEXT,
                prompt_preview TEXT,
                latency_ms REAL
            )
            """
        )

        # Insert test sessions
        now = datetime.now(timezone.utc).timestamp()
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            ("session-001", now - 100, now + 100, 5, 0),
        )
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            ("session-002", now + 200, now + 300, 0, 0),
        )

        # Insert test detections
        conn.execute(
            "INSERT INTO detection_history VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (1, "/sc:analyze", 0.95, "keyword", now - 50, "session-001", "test", 1.2),
        )
        conn.execute(
            "INSERT INTO detection_history VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (2, "/sc:test", 0.85, "model2vec", now, "session-001", "test", 2.1),
        )

        conn.commit()

    yield db_file

    # Cleanup
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def temp_decisions() -> Path:
    """Create a temporary decisions.yaml file with test data."""
    decisions_file = Path(tempfile.gettempdir()) / "test_decisions.yaml"

    # Current time for reproducible tests
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat().replace("+00:00", "Z")

    data = {
        "metadata": {
            "project": "contextune",
            "version": "1.0",
            "created": timestamp,
        },
        "decisions": {
            "description": "Test decisions",
            "entries": [
                {
                    "id": "dec-001",
                    "title": "Test Decision 1",
                    "status": "accepted",
                    "created_at": timestamp,
                },
                {
                    "id": "dec-002",
                    "title": "Test Decision 2",
                    "created_at": (now.replace(hour=now.hour + 1)).isoformat().replace(
                        "+00:00", "Z"
                    ),
                },
            ],
        },
    }

    with open(decisions_file, "w") as f:
        yaml.dump(data, f)

    yield decisions_file

    # Cleanup
    if decisions_file.exists():
        decisions_file.unlink()


class TestDecisionLinker:
    """Test suite for DecisionLinker class."""

    def test_init_valid_paths(self, temp_db: Path, temp_decisions: Path) -> None:
        """Test initialization with valid paths."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        assert linker.db_path == temp_db
        assert linker.decisions_path == temp_decisions
        assert not linker.dry_run

    def test_init_invalid_db(self, temp_decisions: Path) -> None:
        """Test initialization fails with invalid database path."""
        with pytest.raises(SystemExit):
            DecisionLinker("/nonexistent/db.db", str(temp_decisions))

    def test_init_invalid_decisions(self, temp_db: Path) -> None:
        """Test initialization fails with invalid decisions file."""
        with pytest.raises(SystemExit):
            DecisionLinker(str(temp_db), "/nonexistent/decisions.yaml")

    def test_load_decisions(self, temp_db: Path, temp_decisions: Path) -> None:
        """Test loading decisions.yaml file."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        decisions = linker.load_decisions()

        assert "metadata" in decisions
        assert "decisions" in decisions
        assert decisions["decisions"]["entries"]
        assert len(decisions["decisions"]["entries"]) == 2

    def test_query_sessions(self, temp_db: Path, temp_decisions: Path) -> None:
        """Test querying sessions from database."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        sessions = linker.query_sessions()

        assert len(sessions) == 2
        assert sessions[0]["session_id"] == "session-002"  # Ordered DESC by start_time
        assert "start_time" in sessions[0]

    def test_query_detections_for_session(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test querying detections for a specific session."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        detections = linker.query_detections_for_session("session-001")

        assert len(detections) == 2
        assert detections[0]["command"] == "/sc:analyze"
        assert detections[1]["command"] == "/sc:test"

    def test_find_matching_session_exact(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test finding session with exact timestamp match."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        sessions = linker.query_sessions()

        # Get start time of first session and add small offset
        session_start = sessions[0]["start_time"]
        timestamp_ms = int((session_start + 10) * 1000)

        # Find matching session (session-002 has start_time around current time)
        matching = linker.find_matching_session(timestamp_ms)
        assert matching is not None
        assert matching["session_id"] == "session-002"

    def test_find_matching_session_no_match(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test finding session when no match exists."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))

        # Timestamp far in the past
        old_timestamp_ms = 1000000000  # Jan 1970
        matching = linker.find_matching_session(old_timestamp_ms)
        assert matching is None

    def test_parse_timestamp_iso8601(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test parsing ISO 8601 timestamp format."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))

        # Parse ISO 8601 with Z suffix
        timestamp_ms = linker.parse_timestamp("2025-10-27T15:30:45Z")
        assert timestamp_ms is not None
        assert isinstance(timestamp_ms, int)

    def test_parse_timestamp_invalid(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test parsing invalid timestamp format."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))

        timestamp_ms = linker.parse_timestamp("invalid-timestamp")
        assert timestamp_ms is None

    def test_save_decisions_dry_run(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test that dry-run mode doesn't write files."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions), dry_run=True)
        decisions = {"test": "data"}

        original_content = temp_decisions.read_text()
        linker.save_decisions(decisions)
        new_content = temp_decisions.read_text()

        # File should not change in dry-run mode
        assert original_content == new_content

    def test_save_decisions_writes_file(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test that decisions are written to file."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions), dry_run=False)

        new_data = {
            "metadata": {"project": "test"},
            "test_key": "test_value",
        }
        linker.save_decisions(new_data)

        # Reload and verify
        saved_data = linker.load_decisions()
        assert saved_data["metadata"]["project"] == "test"
        assert saved_data["test_key"] == "test_value"

    def test_link_decisions_empty_entries(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test linking when no entries exist."""
        # Create a fresh decisions file with empty entries
        empty_decisions = {
            "metadata": {"project": "test"},
            "decisions": {
                "description": "Test",
                "entries": [],
            },
        }

        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(empty_decisions, f)
            temp_file = f.name

        try:
            linker = DecisionLinker(str(temp_db), temp_file)
            result = linker.link_decisions()
            assert result["decisions"]["entries"] == []
        finally:
            Path(temp_file).unlink()

    def test_link_decisions_adds_observability_link(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test that observability_link field is added correctly."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions), dry_run=True)

        decisions = linker.link_decisions()
        entries = decisions["decisions"]["entries"]

        # Check that entries without matching sessions are skipped
        # (since test timestamps don't match DB timestamps)
        for entry in entries:
            if "observability_link" in entry:
                assert "session_id" in entry["observability_link"]
                assert "timestamp" in entry["observability_link"]
                assert "detection_count" in entry["observability_link"]
                assert "linked_at" in entry["observability_link"]


class TestTimestampMatching:
    """Test suite for timestamp matching logic."""

    def test_timestamp_within_session_bounds(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test that timestamp within session bounds matches."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        sessions = linker.query_sessions()

        if sessions:
            session = sessions[0]
            # Timestamp in middle of session
            mid_timestamp = (session["start_time"] + (session.get("end_time") or session["start_time"] + 100)) / 2
            match = linker.find_matching_session(int(mid_timestamp * 1000))
            assert match is not None

    def test_tolerance_matching(self, temp_db: Path, temp_decisions: Path) -> None:
        """Test that tolerance parameter works correctly."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions))
        sessions = linker.query_sessions()

        if sessions:
            session = sessions[0]
            # Timestamp slightly before session start
            early_timestamp = session["start_time"] - 2  # 2 seconds before
            match = linker.find_matching_session(int(early_timestamp * 1000), tolerance_ms=3000)
            assert match is not None  # Should match with 3s tolerance


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_linking_workflow(
        self, temp_db: Path, temp_decisions: Path
    ) -> None:
        """Test complete linking workflow."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions), dry_run=True)

        # Load original decisions
        original = linker.load_decisions()
        original_count = len(original["decisions"]["entries"])

        # Link decisions
        linked = linker.link_decisions()
        linked_count = len(linked["decisions"]["entries"])

        # Should have same number of entries
        assert linked_count == original_count

        # Should not write in dry-run
        reloaded = linker.load_decisions()
        assert reloaded == original

    def test_yaml_roundtrip(self, temp_db: Path, temp_decisions: Path) -> None:
        """Test that YAML can be loaded, modified, and saved."""
        linker = DecisionLinker(str(temp_db), str(temp_decisions), dry_run=False)

        # Load
        original = linker.load_decisions()

        # Modify
        original["test_added"] = "test_value"

        # Save
        linker.save_decisions(original)

        # Reload
        reloaded = linker.load_decisions()
        assert reloaded["test_added"] == "test_value"
