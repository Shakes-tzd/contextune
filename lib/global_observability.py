#!/usr/bin/env python3
"""
Global Observability - Cross-Project Analytics

Aggregates metrics across ALL projects to understand:
- Overall Claude Code usage patterns
- Most used commands across projects
- Time-based activity patterns
- Performance trends
- Project comparisons

Benefits:
- 📊 Holistic view of Claude Code usage
- 🕐 Time-based patterns (peak coding hours)
- 📈 Productivity insights
- 🎯 Command popularity rankings
- 🔍 Cross-project correlations
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class ProjectStats:
    """Statistics for a single project."""
    project_path: Path
    total_detections: int
    commands: Dict[str, int]
    methods: Dict[str, int]
    avg_confidence: float
    last_activity: float
    errors: int


class GlobalObservability:
    """Cross-project analytics for Claude Code usage."""

    def __init__(self, search_root: Path = None):
        """
        Initialize global observability.

        Args:
            search_root: Root directory to search for projects (default: $HOME)
        """
        self.search_root = search_root or Path.home()
        self.databases = self._find_all_databases()

    def _find_all_databases(self) -> List[Path]:
        """Find all observability.db files."""
        # Search common project locations
        search_paths = [
            self.search_root / "projects",
            self.search_root / "code",
            self.search_root / "dev",
            self.search_root / "work",
            self.search_root / "DevProjects",
            self.search_root / "Documents",
            self.search_root / "repos",
            self.search_root,  # Also search home directly
        ]

        databases = []
        for search_path in search_paths:
            if search_path.exists():
                # Find all .contextune/observability.db files
                dbs = list(search_path.glob("**/.contextune/observability.db"))
                databases.extend(dbs)

        # Deduplicate
        return list(set(databases))

    def get_project_stats(self, db_path: Path) -> Optional[ProjectStats]:
        """Get statistics for a single project."""
        try:
            conn = sqlite3.connect(db_path)

            # Total detections
            total = conn.execute("SELECT COUNT(*) FROM detection_history").fetchone()[0]

            if total == 0:
                conn.close()
                return None

            # Commands
            commands = dict(conn.execute("""
                SELECT command, COUNT(*) FROM detection_history
                GROUP BY command
            """).fetchall())

            # Methods
            methods = dict(conn.execute("""
                SELECT method, COUNT(*) FROM detection_history
                GROUP BY method
            """).fetchall())

            # Average confidence
            avg_conf = conn.execute(
                "SELECT AVG(confidence) FROM detection_history"
            ).fetchone()[0]

            # Last activity
            last_activity = conn.execute(
                "SELECT MAX(timestamp) FROM detection_history"
            ).fetchone()[0]

            # Errors
            errors = conn.execute("SELECT COUNT(*) FROM error_logs").fetchone()[0]

            conn.close()

            # Project path (parent of .contextune)
            project_path = db_path.parent.parent

            return ProjectStats(
                project_path=project_path,
                total_detections=total,
                commands=commands,
                methods=methods,
                avg_confidence=avg_conf,
                last_activity=last_activity,
                errors=errors
            )
        except Exception as e:
            print(f"Error reading {db_path}: {e}")
            return None

    def aggregate_stats(self) -> Dict[str, Any]:
        """Aggregate statistics across all projects."""
        # Collect per-project stats
        project_stats = []
        for db_path in self.databases:
            stats = self.get_project_stats(db_path)
            if stats:
                project_stats.append(stats)

        if not project_stats:
            return {
                "total_projects": 0,
                "total_detections": 0,
                "message": "No projects with Contextune data found"
            }

        # Aggregate
        total_detections = sum(p.total_detections for p in project_stats)

        # Combine commands across projects
        all_commands = defaultdict(int)
        for p in project_stats:
            for cmd, count in p.commands.items():
                all_commands[cmd] += count

        # Combine methods
        all_methods = defaultdict(int)
        for p in project_stats:
            for method, count in p.methods.items():
                all_methods[method] += count

        # Average confidence
        avg_confidence = sum(p.avg_confidence for p in project_stats) / len(project_stats)

        # Total errors
        total_errors = sum(p.errors for p in project_stats)

        # Most active project
        most_active = max(project_stats, key=lambda p: p.total_detections)

        # Recently active projects (last 7 days)
        week_ago = time.time() - (7 * 86400)
        recently_active = [
            p for p in project_stats
            if p.last_activity > week_ago
        ]

        # Sort projects by activity
        projects_by_activity = sorted(
            project_stats,
            key=lambda p: p.total_detections,
            reverse=True
        )

        return {
            "total_projects": len(project_stats),
            "total_detections": total_detections,
            "commands": dict(all_commands),
            "methods": dict(all_methods),
            "avg_confidence": avg_confidence,
            "total_errors": total_errors,
            "most_active_project": {
                "name": most_active.project_path.name,
                "path": str(most_active.project_path),
                "detections": most_active.total_detections
            },
            "recently_active_count": len(recently_active),
            "projects": [
                {
                    "name": p.project_path.name,
                    "path": str(p.project_path),
                    "detections": p.total_detections,
                    "last_activity": p.last_activity
                }
                for p in projects_by_activity
            ]
        }

    def get_time_patterns(self) -> Dict[str, Any]:
        """Analyze time-based usage patterns across all projects."""
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)

        for db_path in self.databases:
            try:
                conn = sqlite3.connect(db_path)

                # Get all timestamps
                timestamps = [
                    row[0] for row in conn.execute(
                        "SELECT timestamp FROM detection_history"
                    ).fetchall()
                ]

                for ts in timestamps:
                    dt = datetime.fromtimestamp(ts)
                    hourly_activity[dt.hour] += 1
                    daily_activity[dt.strftime('%Y-%m-%d')] += 1

                conn.close()
            except Exception:
                continue

        # Find peak hours
        if hourly_activity:
            peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
        else:
            peak_hour = (0, 0)

        # Activity last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_activity = {
            date: count
            for date, count in daily_activity.items()
            if date >= thirty_days_ago
        }

        return {
            "hourly_activity": dict(hourly_activity),
            "daily_activity": dict(daily_activity),
            "peak_hour": peak_hour[0],
            "peak_hour_count": peak_hour[1],
            "last_30_days": recent_activity,
            "most_active_day": max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else None
        }

    def get_command_insights(self) -> Dict[str, Any]:
        """Analyze command usage patterns."""
        stats = self.aggregate_stats()

        if stats["total_detections"] == 0:
            return {"message": "No data available"}

        commands = stats["commands"]
        total = stats["total_detections"]

        # Sort by popularity
        popular_commands = sorted(
            commands.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Calculate percentages
        command_breakdown = [
            {
                "command": cmd,
                "count": count,
                "percentage": (count / total * 100)
            }
            for cmd, count in popular_commands
        ]

        # Detect trends (compare last 7 days vs previous 7 days)
        # This requires timestamp analysis per command - simplified here

        return {
            "top_commands": command_breakdown,
            "unique_commands": len(commands),
            "most_popular": popular_commands[0] if popular_commands else None
        }

    def get_performance_overview(self) -> Dict[str, Any]:
        """Aggregate performance metrics across projects."""
        all_latencies = defaultdict(list)

        for db_path in self.databases:
            try:
                conn = sqlite3.connect(db_path)

                # Get matcher latencies
                for method, latency in conn.execute(
                    "SELECT method, latency_ms FROM detection_history WHERE latency_ms IS NOT NULL"
                ).fetchall():
                    all_latencies[method].append(latency)

                conn.close()
            except Exception:
                continue

        # Calculate percentiles
        performance = {}
        for method, latencies in all_latencies.items():
            if latencies:
                latencies.sort()
                n = len(latencies)
                performance[method] = {
                    "count": n,
                    "p50": latencies[int(n * 0.5)],
                    "p95": latencies[int(n * 0.95)],
                    "p99": latencies[int(n * 0.99)],
                    "min": min(latencies),
                    "max": max(latencies),
                    "avg": sum(latencies) / n
                }

        return performance

    def export_summary(self, output_path: Path = None):
        """Export complete summary to JSON."""
        summary = {
            "generated_at": datetime.now().isoformat(),
            "search_root": str(self.search_root),
            "databases_found": len(self.databases),
            "aggregate_stats": self.aggregate_stats(),
            "time_patterns": self.get_time_patterns(),
            "command_insights": self.get_command_insights(),
            "performance": self.get_performance_overview()
        }

        if output_path:
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            return summary
        else:
            return summary


if __name__ == "__main__":
    # Demo usage
    print("="*70)
    print("Contextune Global Analytics".center(70))
    print("="*70)
    print()

    obs = GlobalObservability()

    print(f"📁 Found {len(obs.databases)} projects with Contextune data")
    print()

    # Aggregate stats
    stats = obs.aggregate_stats()

    if stats["total_detections"] == 0:
        print("⚠️  No Contextune data found. Use Contextune in your projects first!")
    else:
        print(f"📊 Total Detections: {stats['total_detections']}")
        print(f"🎯 Active Projects: {stats['total_projects']}")
        print(f"📈 Average Confidence: {stats['avg_confidence']*100:.1f}%")
        print(f"❌ Total Errors: {stats['total_errors']}")
        print()

        print("🏆 Most Active Project:")
        print(f"  {stats['most_active_project']['name']}: {stats['most_active_project']['detections']} detections")
        print()

        print("⚡ Top Commands:")
        for cmd, count in sorted(stats['commands'].items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (count / stats['total_detections'] * 100)
            print(f"  {cmd:20s} {count:4d} ({pct:5.1f}%)")
        print()

        # Time patterns
        time_patterns = obs.get_time_patterns()
        print(f"🕐 Peak Coding Hour: {time_patterns['peak_hour']}:00 ({time_patterns['peak_hour_count']} detections)")
        print()

        # Performance
        perf = obs.get_performance_overview()
        if perf:
            print("⚡ Performance (P50/P95/P99):")
            for method, metrics in perf.items():
                print(f"  {method:15s} {metrics['p50']:.3f}ms / {metrics['p95']:.3f}ms / {metrics['p99']:.3f}ms")
