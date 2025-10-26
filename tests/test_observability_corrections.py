#!/usr/bin/env python3
"""
Tests for Haiku correction logging in ObservabilityDB.

Tests cover:
- Table creation and schema validation
- log_correction() method functionality
- Cost calculation accuracy
- Index usage and query performance
- Correction acceptance rate queries
- Cost analysis aggregations
"""

import sqlite3
import sys
import tempfile
import time
from pathlib import Path

import pytest

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from observability_db import ObservabilityDB


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_observability.db"
        db = ObservabilityDB(str(db_path))
        yield db
        # Cleanup happens automatically with tempdir


def test_model_corrections_table_exists(temp_db):
    """Test that model_corrections table is created."""
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='model_corrections'
        """)
        assert cursor.fetchone() is not None, "model_corrections table should exist"


def test_model_corrections_schema(temp_db):
    """Test that model_corrections table has correct schema."""
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("PRAGMA table_info(model_corrections)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        # Check all required columns exist with correct types
        expected_columns = {
            "id": "INTEGER",
            "original_command": "TEXT",
            "corrected_command": "TEXT",
            "original_confidence": "REAL",
            "correction_accepted": "BOOLEAN",
            "model_name": "TEXT",
            "reasoning": "TEXT",
            "prompt_tokens": "INTEGER",
            "completion_tokens": "INTEGER",
            "total_cost_usd": "REAL",
            "latency_ms": "REAL",
            "timestamp": "REAL",
            "session_id": "TEXT",
            "prompt_preview": "TEXT",
        }

        for col_name, col_type in expected_columns.items():
            assert col_name in columns, f"Column {col_name} should exist"
            assert columns[col_name] == col_type, (
                f"Column {col_name} should be {col_type}"
            )


def test_model_corrections_indexes(temp_db):
    """Test that required indexes are created."""
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='model_corrections'
        """)
        indexes = [row[0] for row in cursor.fetchall()]

        required_indexes = [
            "idx_corrections_timestamp",
            "idx_corrections_accepted",
            "idx_corrections_command",
        ]

        for idx in required_indexes:
            assert idx in indexes, f"Index {idx} should exist"


def test_log_correction_basic(temp_db):
    """Test basic correction logging."""
    temp_db.log_correction(
        original_command="/ctx:research",
        corrected_command="/ctx:design",
        original_confidence=0.85,
        correction_accepted=True,
        prompt_tokens=150,
        completion_tokens=50,
        latency_ms=245.0,
    )

    # Verify insertion
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT * FROM model_corrections")
        row = cursor.fetchone()

        assert row is not None, "Correction should be logged"
        assert row[1] == "/ctx:research", "Original command should match"
        assert row[2] == "/ctx:design", "Corrected command should match"
        assert row[3] == 0.85, "Confidence should match"
        assert row[4] == 1, "Correction accepted should be True (1)"


def test_log_correction_cost_calculation(temp_db):
    """Test cost calculation accuracy for Haiku 4.5."""
    # Haiku 4.5 pricing:
    # Input: $0.25 per million tokens
    # Output: $1.25 per million tokens

    prompt_tokens = 1000
    completion_tokens = 500

    temp_db.log_correction(
        original_command="/ctx:research",
        corrected_command="/ctx:design",
        original_confidence=0.85,
        correction_accepted=True,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=245.0,
    )

    # Calculate expected cost
    expected_input_cost = (prompt_tokens * 0.25) / 1_000_000
    expected_output_cost = (completion_tokens * 1.25) / 1_000_000
    expected_total_cost = expected_input_cost + expected_output_cost

    # Verify cost in database
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT total_cost_usd FROM model_corrections")
        actual_cost = cursor.fetchone()[0]

        assert abs(actual_cost - expected_total_cost) < 1e-10, (
            f"Cost should be {expected_total_cost}, got {actual_cost}"
        )


def test_log_correction_with_reasoning(temp_db):
    """Test logging correction with reasoning."""
    reasoning = (
        "User asked for system design, not research. /ctx:design is better match."
    )

    temp_db.log_correction(
        original_command="/ctx:research",
        corrected_command="/ctx:design",
        original_confidence=0.85,
        correction_accepted=True,
        reasoning=reasoning,
        prompt_tokens=150,
        completion_tokens=50,
        latency_ms=245.0,
    )

    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT reasoning FROM model_corrections")
        stored_reasoning = cursor.fetchone()[0]

        assert stored_reasoning == reasoning, "Reasoning should be stored correctly"


def test_log_correction_prompt_preview_sanitization(temp_db):
    """Test that prompt preview is limited to 100 chars."""
    long_prompt = "a" * 200

    temp_db.log_correction(
        original_command="/ctx:research",
        corrected_command="/ctx:design",
        original_confidence=0.85,
        correction_accepted=True,
        prompt_tokens=150,
        completion_tokens=50,
        latency_ms=245.0,
        prompt_preview=long_prompt,
    )

    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT prompt_preview FROM model_corrections")
        stored_preview = cursor.fetchone()[0]

        assert len(stored_preview) == 100, (
            "Prompt preview should be limited to 100 chars"
        )


def test_log_correction_no_correction(temp_db):
    """Test logging when Haiku agrees with original detection."""
    temp_db.log_correction(
        original_command="/ctx:research",
        corrected_command="/ctx:research",  # Same as original
        original_confidence=0.95,
        correction_accepted=False,  # No correction needed
        prompt_tokens=150,
        completion_tokens=30,
        latency_ms=200.0,
    )

    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT correction_accepted FROM model_corrections")
        accepted = cursor.fetchone()[0]

        assert accepted == 0, "correction_accepted should be False (0)"


def test_correction_acceptance_rate_query(temp_db):
    """Test query for correction acceptance rate."""
    # Log 10 corrections: 7 accepted, 3 not accepted
    for i in range(7):
        temp_db.log_correction(
            original_command=f"/ctx:cmd{i}",
            corrected_command="/ctx:design",
            original_confidence=0.8,
            correction_accepted=True,
            prompt_tokens=150,
            completion_tokens=50,
            latency_ms=200.0,
        )

    for i in range(3):
        temp_db.log_correction(
            original_command=f"/ctx:cmd{i}",
            corrected_command=f"/ctx:cmd{i}",
            original_confidence=0.9,
            correction_accepted=False,
            prompt_tokens=150,
            completion_tokens=30,
            latency_ms=180.0,
        )

    # Query acceptance rate
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT
                CAST(SUM(correction_accepted) AS FLOAT) / COUNT(*) as acceptance_rate
            FROM model_corrections
        """)
        acceptance_rate = cursor.fetchone()[0]

        assert abs(acceptance_rate - 0.7) < 0.01, (
            f"Acceptance rate should be 0.7, got {acceptance_rate}"
        )


def test_average_cost_per_correction_query(temp_db):
    """Test query for average cost per correction."""
    costs = []
    for i in range(5):
        prompt_tokens = 100 + i * 50
        completion_tokens = 40 + i * 10
        cost = (prompt_tokens * 0.25 + completion_tokens * 1.25) / 1_000_000
        costs.append(cost)

        temp_db.log_correction(
            original_command=f"/ctx:cmd{i}",
            corrected_command="/ctx:design",
            original_confidence=0.8,
            correction_accepted=True,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=200.0,
        )

    expected_avg_cost = sum(costs) / len(costs)

    # Query average cost
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT AVG(total_cost_usd) FROM model_corrections
        """)
        avg_cost = cursor.fetchone()[0]

        assert abs(avg_cost - expected_avg_cost) < 1e-10, (
            f"Average cost should be {expected_avg_cost}, got {avg_cost}"
        )


def test_p95_latency_query(temp_db):
    """Test P95 latency calculation."""
    latencies = [
        100.0,
        150.0,
        200.0,
        250.0,
        300.0,
        350.0,
        400.0,
        450.0,
        500.0,
        550.0,
        600.0,
        650.0,
        700.0,
        750.0,
        800.0,
        850.0,
        900.0,
        950.0,
        1000.0,
        1050.0,
    ]

    for i, latency in enumerate(latencies):
        temp_db.log_correction(
            original_command=f"/ctx:cmd{i}",
            corrected_command="/ctx:design",
            original_confidence=0.8,
            correction_accepted=True,
            prompt_tokens=150,
            completion_tokens=50,
            latency_ms=latency,
        )

    # Query P95 latency
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT latency_ms
            FROM model_corrections
            ORDER BY latency_ms
            LIMIT 1 OFFSET (SELECT CAST(COUNT(*) * 0.95 AS INTEGER) FROM model_corrections)
        """)
        p95_latency = cursor.fetchone()[0]

        # P95 of 20 values should be around the 19th value (index 18)
        expected_p95 = latencies[int(len(latencies) * 0.95)]
        assert abs(p95_latency - expected_p95) < 50, (
            f"P95 latency should be around {expected_p95}, got {p95_latency}"
        )


def test_command_distribution_query(temp_db):
    """Test query for most corrected commands."""
    # Log various corrections
    corrections = {
        "/ctx:research": 10,
        "/ctx:plan": 5,
        "/ctx:execute": 3,
        "/ctx:status": 2,
    }

    for cmd, count in corrections.items():
        for _ in range(count):
            temp_db.log_correction(
                original_command=cmd,
                corrected_command="/ctx:design",
                original_confidence=0.8,
                correction_accepted=True,
                prompt_tokens=150,
                completion_tokens=50,
                latency_ms=200.0,
            )

    # Query most corrected commands
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            SELECT original_command, COUNT(*) as count
            FROM model_corrections
            GROUP BY original_command
            ORDER BY count DESC
            LIMIT 3
        """)
        results = cursor.fetchall()

        assert results[0][0] == "/ctx:research", (
            "Most corrected should be /ctx:research"
        )
        assert results[0][1] == 10, "Count should be 10"
        assert results[1][0] == "/ctx:plan", "Second most should be /ctx:plan"
        assert results[1][1] == 5, "Count should be 5"


def test_30_day_aggregate_query_performance(temp_db):
    """Test that 30-day aggregate queries run in <10ms."""
    # Insert 100 correction records
    for i in range(100):
        temp_db.log_correction(
            original_command=f"/ctx:cmd{i % 10}",
            corrected_command="/ctx:design",
            original_confidence=0.8,
            correction_accepted=(i % 3 == 0),  # 1/3 acceptance rate
            prompt_tokens=150,
            completion_tokens=50,
            latency_ms=200.0,
        )

    # Time a 30-day aggregate query
    thirty_days_ago = time.time() - (30 * 24 * 3600)

    with sqlite3.connect(temp_db.db_path) as conn:
        start = time.perf_counter()

        conn.execute(
            """
            SELECT
                COUNT(*) as total_corrections,
                CAST(SUM(correction_accepted) AS FLOAT) / COUNT(*) as acceptance_rate,
                AVG(total_cost_usd) as avg_cost,
                AVG(latency_ms) as avg_latency
            FROM model_corrections
            WHERE timestamp > ?
        """,
            (thirty_days_ago,),
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 10, (
            f"30-day aggregate query should run in <10ms, took {elapsed_ms:.2f}ms"
        )


def test_index_usage_verification(temp_db):
    """Test that indexes are used by queries (EXPLAIN QUERY PLAN)."""
    # Insert test data
    for i in range(10):
        temp_db.log_correction(
            original_command=f"/ctx:cmd{i}",
            corrected_command="/ctx:design",
            original_confidence=0.8,
            correction_accepted=True,
            prompt_tokens=150,
            completion_tokens=50,
            latency_ms=200.0,
        )

    # Check that timestamp index is used
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM model_corrections
            WHERE timestamp > 0
        """)
        plan = " ".join(str(row[3]) for row in cursor.fetchall()).lower()

        assert "idx_corrections_timestamp" in plan, (
            "Query should use idx_corrections_timestamp index"
        )

    # Check that correction_accepted index is used
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM model_corrections
            WHERE correction_accepted = 1
        """)
        plan = " ".join(str(row[3]) for row in cursor.fetchall()).lower()

        assert "idx_corrections_accepted" in plan, (
            "Query should use idx_corrections_accepted index"
        )

    # Check that command index is used
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("""
            EXPLAIN QUERY PLAN
            SELECT * FROM model_corrections
            WHERE corrected_command = '/ctx:design'
        """)
        plan = " ".join(str(row[3]) for row in cursor.fetchall()).lower()

        assert "idx_corrections_command" in plan, (
            "Query should use idx_corrections_command index"
        )


def test_concurrent_writes(temp_db):
    """Test WAL mode supports concurrent writes."""
    import threading

    results = []

    def write_correction(thread_id):
        try:
            temp_db.log_correction(
                original_command=f"/ctx:cmd{thread_id}",
                corrected_command="/ctx:design",
                original_confidence=0.8,
                correction_accepted=True,
                prompt_tokens=150,
                completion_tokens=50,
                latency_ms=200.0,
            )
            results.append(True)
        except Exception as e:
            print(f"Thread {thread_id} failed: {e}")
            results.append(False)

    # Launch 10 concurrent writes
    threads = []
    for i in range(10):
        t = threading.Thread(target=write_correction, args=(i,))
        threads.append(t)
        t.start()

    # Wait for all threads
    for t in threads:
        t.join()

    # Verify all writes succeeded
    assert all(results), "All concurrent writes should succeed"

    # Verify all records were inserted
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM model_corrections")
        count = cursor.fetchone()[0]

        assert count == 10, "All 10 corrections should be logged"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
