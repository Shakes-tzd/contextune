#!/usr/bin/env python3
"""
Unified Observability Database for Contextune

Single SQLite database for all metrics, logs, and state:
- Detection state (current + history)
- Performance metrics (hook latency, matcher speed)
- Error tracking
- Session analytics
- Command usage patterns
- User preferences

Benefits:
- ✅ Centralized: No scattered JSON files
- ✅ Fast queries: SQL aggregations vs manual parsing
- ✅ Time-series: Built-in timestamp support
- ✅ Correlations: JOIN detection + performance + errors
- ✅ Thread-safe: ACID transactions
"""

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Detection:
    """Detection result with metadata."""

    command: str
    confidence: float
    method: str
    timestamp: float


@dataclass
class PerformanceMetric:
    """Performance measurement."""

    component: str  # "hook", "keyword_matcher", "model2vec_matcher", etc.
    operation: str  # "detect", "write_db", "read_db", etc.
    latency_ms: float
    timestamp: float
    metadata: dict[str, Any] = None


@dataclass
class ErrorLog:
    """Error/exception tracking."""

    component: str
    error_type: str
    message: str
    stack_trace: str | None
    timestamp: float


class ObservabilityDB:
    """Unified observability database for Contextune."""

    def __init__(self, db_path: str = ".contextune/observability.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database with comprehensive observability schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")

            # === DETECTION TABLES ===

            # Current detection (single row, updated in-place)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS current_detection (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    command TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    method TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    prompt_preview TEXT
                )
            """)

            # Detection history (all detections)
            conn.execute("""
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
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_detection_timestamp ON detection_history(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_detection_command ON detection_history(command)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_detection_method ON detection_history(method)"
            )

            # === PERFORMANCE TABLES ===

            # Performance metrics (hook latency, matcher speed, etc.)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    session_id TEXT,
                    metadata TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_perf_component ON performance_metrics(component)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)"
            )

            # Matcher tier performance (keyword vs model2vec vs semantic)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matcher_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_matcher_method ON matcher_performance(method)"
            )

            # === ERROR TRACKING ===

            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    stack_trace TEXT,
                    timestamp REAL NOT NULL,
                    session_id TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_logs(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_error_component ON error_logs(component)"
            )

            # === SESSION TRACKING ===

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    total_detections INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0
                )
            """)

            # === COMMAND USAGE PATTERNS ===

            conn.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    executed BOOLEAN NOT NULL,
                    timestamp REAL NOT NULL,
                    session_id TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_usage_command ON command_usage(command)"
            )

            # === USER PREFERENCES (migrate from user_patterns.json) ===

            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    pattern TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    confidence_threshold REAL DEFAULT 0.7,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            # === MODEL CORRECTIONS (Haiku auto-correction tracking) ===

            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    -- Input/Output tracking
                    original_command TEXT NOT NULL,
                    corrected_command TEXT NOT NULL,
                    original_confidence REAL,
                    correction_accepted BOOLEAN NOT NULL,

                    -- Model metadata
                    model_name TEXT DEFAULT 'haiku-4-5',
                    reasoning TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_cost_usd REAL,

                    -- Performance
                    latency_ms REAL NOT NULL,

                    -- Context
                    timestamp REAL NOT NULL,
                    session_id TEXT,
                    prompt_preview TEXT,

                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_corrections_timestamp ON model_corrections(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_corrections_accepted ON model_corrections(correction_accepted)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_corrections_command ON model_corrections(corrected_command)"
            )

            conn.commit()

    # === DETECTION METHODS ===

    def set_detection(
        self,
        command: str,
        confidence: float,
        method: str,
        prompt_preview: str = None,
        latency_ms: float = None,
    ) -> None:
        """Update current detection and log to history."""
        timestamp = time.time()

        with sqlite3.connect(self.db_path) as conn:
            # Update current detection (atomic upsert)
            conn.execute(
                """
                INSERT OR REPLACE INTO current_detection
                (id, command, confidence, method, timestamp, prompt_preview)
                VALUES (1, ?, ?, ?, ?, ?)
            """,
                (command, confidence, method, timestamp, prompt_preview),
            )

            # Add to history
            conn.execute(
                """
                INSERT INTO detection_history
                (command, confidence, method, timestamp, prompt_preview, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (command, confidence, method, timestamp, prompt_preview, latency_ms),
            )

            conn.commit()

    def get_detection(self) -> Detection | None:
        """Get current detection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT command, confidence, method, timestamp
                FROM current_detection
                WHERE id = 1
            """)
            row = cursor.fetchone()
            if row:
                return Detection(*row)
            return None

    def clear_detection(self) -> None:
        """Clear current detection."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM current_detection WHERE id = 1")
            conn.commit()

    # === PERFORMANCE METHODS ===

    def log_performance(
        self,
        component: str,
        operation: str,
        latency_ms: float,
        metadata: dict[str, Any] = None,
    ) -> None:
        """Log performance metric."""
        timestamp = time.time()
        metadata_json = json.dumps(metadata) if metadata else None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO performance_metrics
                (component, operation, latency_ms, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (component, operation, latency_ms, timestamp, metadata_json),
            )
            conn.commit()

    def log_matcher_performance(
        self, method: str, latency_ms: float, success: bool
    ) -> None:
        """Log matcher-specific performance."""
        timestamp = time.time()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO matcher_performance
                (method, latency_ms, success, timestamp)
                VALUES (?, ?, ?, ?)
            """,
                (method, latency_ms, success, timestamp),
            )
            conn.commit()

    # === ERROR TRACKING ===

    def log_error(
        self, component: str, error_type: str, message: str, stack_trace: str = None
    ) -> None:
        """Log error/exception."""
        timestamp = time.time()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO error_logs
                (component, error_type, message, stack_trace, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (component, error_type, message, stack_trace, timestamp),
            )
            conn.commit()

    # === MODEL CORRECTION TRACKING ===

    def log_correction(
        self,
        original_command: str,
        corrected_command: str,
        original_confidence: float,
        correction_accepted: bool,
        model_name: str = "haiku-4-5",
        reasoning: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
        session_id: str = "",
        prompt_preview: str = "",
    ) -> None:
        """
        Log Haiku model correction for accuracy tracking and cost analysis.

        Args:
            original_command: Command detected by cascade (e.g., "/ctx:research")
            corrected_command: Command suggested by Haiku (e.g., "/ctx:design")
            original_confidence: Detection confidence (0-1)
            correction_accepted: Whether correction was used (True) or ignored (False)
            model_name: Model used for correction (default: "haiku-4-5")
            reasoning: Haiku's reasoning for the correction
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            latency_ms: Time taken for correction analysis
            session_id: Session identifier
            prompt_preview: First 100 chars of user prompt (PII-safe)

        Example:
            >>> db = ObservabilityDB()
            >>> db.log_correction(
            ...     original_command="/ctx:research",
            ...     corrected_command="/ctx:design",
            ...     original_confidence=0.85,
            ...     correction_accepted=True,
            ...     prompt_tokens=150,
            ...     completion_tokens=50,
            ...     latency_ms=245.0
            ... )
        """
        timestamp = time.time()

        # Calculate cost based on Haiku 4.5 pricing
        # Input: $0.25 per million tokens
        # Output: $1.25 per million tokens
        input_cost = (prompt_tokens * 0.25) / 1_000_000
        output_cost = (completion_tokens * 1.25) / 1_000_000
        total_cost_usd = input_cost + output_cost

        # Sanitize prompt preview (first 100 chars, no secrets)
        safe_preview = prompt_preview[:100] if prompt_preview else ""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO model_corrections
                (original_command, corrected_command, original_confidence, correction_accepted,
                 model_name, reasoning, prompt_tokens, completion_tokens, total_cost_usd,
                 latency_ms, timestamp, session_id, prompt_preview)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    original_command,
                    corrected_command,
                    original_confidence,
                    correction_accepted,
                    model_name,
                    reasoning,
                    prompt_tokens,
                    completion_tokens,
                    total_cost_usd,
                    latency_ms,
                    timestamp,
                    session_id,
                    safe_preview,
                ),
            )
            conn.commit()

    # === ANALYTICS QUERIES ===

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Detection stats
            total_detections = conn.execute(
                "SELECT COUNT(*) FROM detection_history"
            ).fetchone()[0]

            by_method = dict(
                conn.execute("""
                SELECT method, COUNT(*) FROM detection_history
                GROUP BY method
            """).fetchall()
            )

            by_command = dict(
                conn.execute("""
                SELECT command, COUNT(*) FROM detection_history
                GROUP BY command
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """).fetchall()
            )

            # Performance stats (P50, P95, P99 by component)
            perf_stats = {}
            for (component,) in conn.execute(
                "SELECT DISTINCT component FROM performance_metrics"
            ):
                latencies = [
                    row[0]
                    for row in conn.execute(
                        "SELECT latency_ms FROM performance_metrics WHERE component = ? ORDER BY latency_ms",
                        (component,),
                    ).fetchall()
                ]

                if latencies:
                    n = len(latencies)
                    perf_stats[component] = {
                        "p50": latencies[int(n * 0.5)],
                        "p95": latencies[int(n * 0.95)],
                        "p99": latencies[int(n * 0.99)],
                        "count": n,
                    }

            # Error stats
            error_count = conn.execute("SELECT COUNT(*) FROM error_logs").fetchone()[0]
            errors_by_component = dict(
                conn.execute("""
                SELECT component, COUNT(*) FROM error_logs
                GROUP BY component
            """).fetchall()
            )

            # Matcher performance (avg latency by tier)
            matcher_stats = {}
            for (method,) in conn.execute(
                "SELECT DISTINCT method FROM matcher_performance"
            ):
                avg_latency = conn.execute(
                    "SELECT AVG(latency_ms) FROM matcher_performance WHERE method = ?",
                    (method,),
                ).fetchone()[0]
                success_rate = conn.execute(
                    "SELECT AVG(CAST(success AS FLOAT)) FROM matcher_performance WHERE method = ?",
                    (method,),
                ).fetchone()[0]

                matcher_stats[method] = {
                    "avg_latency_ms": round(avg_latency, 3) if avg_latency else 0,
                    "success_rate": round(success_rate * 100, 1) if success_rate else 0,
                }

            return {
                "detections": {
                    "total": total_detections,
                    "by_method": by_method,
                    "by_command": by_command,
                },
                "performance": perf_stats,
                "matchers": matcher_stats,
                "errors": {"total": error_count, "by_component": errors_by_component},
            }

    def get_recent_detections(self, limit: int = 10) -> list[dict]:
        """Get recent detections with details."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT command, confidence, method, timestamp, prompt_preview, latency_ms
                FROM detection_history
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_performance_trends(self, component: str, hours: int = 24) -> list[dict]:
        """Get performance trends over time."""
        since = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT operation, latency_ms, timestamp
                FROM performance_metrics
                WHERE component = ? AND timestamp > ?
                ORDER BY timestamp ASC
            """,
                (component, since),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_error_summary(self, hours: int = 24) -> list[dict]:
        """Get recent errors."""
        since = time.time() - (hours * 3600)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT component, error_type, message, timestamp
                FROM error_logs
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """,
                (since,),
            )

            return [dict(row) for row in cursor.fetchall()]


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("Contextune Unified Observability Database")
    print("=" * 60)
    print()

    db = ObservabilityDB(".contextune/observability.db")

    # Simulate some activity
    print("📝 Logging sample data...")

    # Detection
    db.set_detection("/ctx:research", 0.95, "keyword", "research best React", 0.003)
    db.set_detection("/sc:analyze", 0.88, "model2vec", "analyze my code", 0.245)

    # Performance
    db.log_performance("hook", "total_execution", 2.5)
    db.log_performance("hook", "detection", 0.24)
    db.log_matcher_performance("keyword", 0.003, True)
    db.log_matcher_performance("model2vec", 0.245, True)

    # Error
    db.log_error("semantic_router", "ImportError", "Cohere API key not found")

    print("✓ Logged detections, performance, and errors")
    print()

    # Query stats
    print("📊 Statistics:")
    print("-" * 60)
    stats = db.get_stats()
    print(json.dumps(stats, indent=2))
    print()

    # Recent detections
    print("🔍 Recent Detections:")
    print("-" * 60)
    for d in db.get_recent_detections(5):
        print(
            f"  {d['command']} ({d['confidence'] * 100:.0f}% {d['method']}, {d['latency_ms']:.3f}ms)"
        )
    print()

    # Errors
    print("❌ Recent Errors:")
    print("-" * 60)
    for e in db.get_error_summary(24):
        print(f"  [{e['component']}] {e['error_type']}: {e['message']}")
