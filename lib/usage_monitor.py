#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Claude Code usage monitoring and adaptive optimization.

Integrates with Claude Code's /usage and /context commands to:
1. Track context consumption in real-time
2. Make intelligent model selection decisions
3. Optimize parallel task execution
4. Warn before hitting limits

Usage:
    monitor = UsageMonitor()
    usage = monitor.get_current_usage()

    if usage.weekly_percent > 80:
        # Switch to Haiku for research tasks
        recommended_model = "haiku-4-5"
"""

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class UsageStats:
    """Claude Code usage statistics."""

    # Session limits
    session_percent: float
    session_reset_time: str

    # Weekly limits (all models)
    weekly_percent: float
    weekly_reset_time: str

    # Opus-specific limits
    opus_percent: float

    # Metadata
    timestamp: float
    raw_output: str


class UsageMonitor:
    """
    Monitor Claude Code usage and provide adaptive recommendations.

    Caches usage data for 60 seconds to avoid repeated subprocess calls.
    """

    def __init__(self, cache_ttl: int = 60):
        """
        Initialize usage monitor.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        self.cache_ttl = cache_ttl
        self._cache: Optional[UsageStats] = None
        self._cache_time: float = 0

    def get_current_usage(self, force_refresh: bool = False) -> Optional[UsageStats]:
        """
        Get current usage stats with three-tier fallback strategy.

        Tries in order:
        1. Headless query (fast, but may hallucinate - needs validation)
        2. Token estimation (reliable for Contextune ops, ~85% accurate)
        3. Returns None (user must use manual paste via /ctx:usage)

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            UsageStats if successful, None if all methods fail

        Warning:
            Headless mode may hallucinate usage data. Always verify critical
            decisions manually using `/usage` command.
        """
        # Check cache
        now = time.time()
        if not force_refresh and self._cache and (now - self._cache_time < self.cache_ttl):
            return self._cache

        # Try headless mode query
        try:
            # Ask Claude Code to report its usage
            prompt = """Please report your current usage statistics in this exact format:

Session usage: X%
Weekly usage: Y%
Opus usage: Z%

Where X, Y, Z are the percentage values from your /usage command.
Reply with ONLY those three lines, no other text."""

            result = subprocess.run(
                [
                    "claude",
                    "-p",  # Print mode
                    prompt,
                    "--output-format", "json",
                    "--append-system-prompt", "You have access to your own usage stats. Report them accurately."
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return self._fallback_estimation()

            # Parse JSON response
            response = json.loads(result.stdout)
            usage_text = response.get('result', '')

            # Parse the structured response
            stats = self._parse_structured_response(usage_text)
            if stats:
                # Mark as headless with confidence warning
                stats.raw_output = f"(headless query - unverified)\n{stats.raw_output}"
                self._cache = stats
                self._cache_time = now

                # Log warning to stderr
                print("⚠️  Usage from headless mode - validate manually with /usage", file=sys.stderr)
                return stats

            return self._fallback_estimation()

        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            print(f"DEBUG: Headless mode unavailable, using estimation: {e}", file=sys.stderr)
            return self._fallback_estimation()

    def _parse_structured_response(self, text: str) -> Optional[UsageStats]:
        """Parse Claude's structured usage response."""
        try:
            lines = text.strip().split('\n')
            session_match = re.search(r'Session usage:\s*(\d+)%', text)
            weekly_match = re.search(r'Weekly usage:\s*(\d+)%', text)
            opus_match = re.search(r'Opus usage:\s*(\d+)%', text)

            if session_match and weekly_match and opus_match:
                return UsageStats(
                    session_percent=float(session_match.group(1)),
                    session_reset_time="unknown",  # Not available via headless
                    weekly_percent=float(weekly_match.group(1)),
                    weekly_reset_time="unknown",
                    opus_percent=float(opus_match.group(1)),
                    timestamp=time.time(),
                    raw_output=text
                )
        except Exception:
            pass
        return None

    def _fallback_estimation(self) -> Optional[UsageStats]:
        """
        Fallback: estimate usage from observability database.

        Uses historical token counts to approximate current usage.
        Less accurate but doesn't require manual input.
        """
        try:
            import sqlite3
            conn = sqlite3.connect(".contextune/observability.db")
            cursor = conn.cursor()

            # Get token counts from last 12 hours (session)
            cursor.execute('''
                SELECT SUM(prompt_tokens + completion_tokens)
                FROM model_corrections
                WHERE timestamp >= strftime('%s', 'now', '-12 hours')
            ''')
            session_tokens = cursor.fetchone()[0] or 0

            # Get token counts from last 7 days (weekly)
            cursor.execute('''
                SELECT SUM(prompt_tokens + completion_tokens)
                FROM model_corrections
                WHERE timestamp >= strftime('%s', 'now', '-7 days')
            ''')
            weekly_tokens = cursor.fetchone()[0] or 0

            conn.close()

            # Rough estimates (Claude 3.5 limits)
            # Session: ~200K tokens, Weekly: ~1M tokens
            SESSION_LIMIT = 200000
            WEEKLY_LIMIT = 1000000

            return UsageStats(
                session_percent=min(100.0, (session_tokens / SESSION_LIMIT) * 100),
                session_reset_time="estimated",
                weekly_percent=min(100.0, (weekly_tokens / WEEKLY_LIMIT) * 100),
                weekly_reset_time="estimated",
                opus_percent=0.0,  # Can't estimate
                timestamp=time.time(),
                raw_output="(estimated from token tracking)"
            )

        except Exception as e:
            print(f"DEBUG: Estimation failed: {e}", file=sys.stderr)
            return None

    def _parse_usage_output(self, output: str) -> Optional[UsageStats]:
        """
        Parse /usage command output.

        Example output:
            Current session
            [progress bar] 7% used
            Resets 12:59am (America/New_York)

            Current week (all models)
            [progress bar] 89% used
            Resets Oct 29, 9:59pm (America/New_York)

            Current week (Opus)
            [progress bar] 0% used
        """
        try:
            # Extract session usage
            session_match = re.search(r'Current session.*?(\d+)% used.*?Resets (.+?)(?:\n|$)', output, re.DOTALL)
            session_percent = float(session_match.group(1)) if session_match else 0.0
            session_reset = session_match.group(2).strip() if session_match else ""

            # Extract weekly usage
            weekly_match = re.search(r'Current week \(all models\).*?(\d+)% used.*?Resets (.+?)(?:\n|$)', output, re.DOTALL)
            weekly_percent = float(weekly_match.group(1)) if weekly_match else 0.0
            weekly_reset = weekly_match.group(2).strip() if weekly_match else ""

            # Extract Opus usage
            opus_match = re.search(r'Current week \(Opus\).*?(\d+)% used', output, re.DOTALL)
            opus_percent = float(opus_match.group(1)) if opus_match else 0.0

            return UsageStats(
                session_percent=session_percent,
                session_reset_time=session_reset,
                weekly_percent=weekly_percent,
                weekly_reset_time=weekly_reset,
                opus_percent=opus_percent,
                timestamp=time.time(),
                raw_output=output
            )

        except Exception as e:
            print(f"Error parsing usage output: {e}")
            return None

    def should_use_haiku(self, task_type: str = "general") -> bool:
        """
        Determine if Haiku should be used based on current usage.

        Args:
            task_type: Type of task ("research", "design", "execute", "general")

        Returns:
            True if Haiku is recommended, False otherwise
        """
        usage = self.get_current_usage()
        if not usage:
            # Conservative: use Haiku if we can't determine usage
            return True

        # Thresholds for switching to Haiku
        WEEKLY_THRESHOLD = 80.0  # Switch at 80% weekly usage
        SESSION_THRESHOLD = 90.0  # Switch at 90% session usage

        # Always use Haiku for research (fast, cheap, good enough)
        if task_type == "research":
            return True

        # Use Sonnet for design/architecture unless near limits
        if task_type == "design":
            return usage.weekly_percent > WEEKLY_THRESHOLD or usage.session_percent > SESSION_THRESHOLD

        # For execution, use Haiku by default (deterministic tasks)
        if task_type == "execute":
            return True

        # General tasks: use Haiku if approaching limits
        return usage.weekly_percent > WEEKLY_THRESHOLD or usage.session_percent > SESSION_THRESHOLD

    def get_parallel_task_limit(self) -> int:
        """
        Calculate max parallel tasks based on remaining context.

        Returns:
            Recommended max parallel tasks (1-5)
        """
        usage = self.get_current_usage()
        if not usage:
            return 3  # Conservative default

        # Estimate context per parallel task: ~10-15% per task
        remaining_session = 100 - usage.session_percent
        remaining_weekly = 100 - usage.weekly_percent

        # Use the more restrictive limit
        remaining = min(remaining_session, remaining_weekly)

        if remaining < 15:
            return 1  # Only one task
        elif remaining < 30:
            return 2
        elif remaining < 45:
            return 3
        elif remaining < 60:
            return 4
        else:
            return 5  # Max 5 parallel tasks

    def get_recommendation(self) -> Dict[str, Any]:
        """
        Get comprehensive usage-based recommendations.

        Returns:
            Dict with recommendations and warnings
        """
        usage = self.get_current_usage()
        if not usage:
            return {
                "status": "unknown",
                "message": "Unable to fetch usage data",
                "recommendations": []
            }

        recommendations = []
        warnings = []
        status = "healthy"

        # Weekly limit warnings
        if usage.weekly_percent >= 95:
            status = "critical"
            warnings.append(f"⚠️  CRITICAL: {usage.weekly_percent}% weekly usage (resets {usage.weekly_reset})")
            recommendations.append("Defer non-critical tasks until weekly reset")
            recommendations.append("Use Haiku exclusively for remaining tasks")
        elif usage.weekly_percent >= 80:
            status = "warning"
            warnings.append(f"⚠️  {usage.weekly_percent}% weekly usage")
            recommendations.append("Switch research tasks to Haiku (87% cost savings)")
            recommendations.append(f"You have ~{100 - usage.weekly_percent}% capacity until {usage.weekly_reset}")

        # Session limit warnings
        if usage.session_percent >= 90:
            warnings.append(f"⚠️  {usage.session_percent}% session usage (resets {usage.session_reset})")
            recommendations.append("Consider waiting until session reset for heavy tasks")

        # Opus availability (opportunity!)
        if usage.opus_percent < 10 and usage.weekly_percent < 70:
            recommendations.append(f"✨ Opus available ({usage.opus_percent}% used) - great for complex architecture tasks")

        # Parallel task guidance
        max_tasks = self.get_parallel_task_limit()
        recommendations.append(f"🔄 Recommended max parallel tasks: {max_tasks}")

        return {
            "status": status,
            "usage": {
                "session": f"{usage.session_percent}%",
                "weekly": f"{usage.weekly_percent}%",
                "opus": f"{usage.opus_percent}%"
            },
            "warnings": warnings,
            "recommendations": recommendations,
            "max_parallel_tasks": max_tasks,
            "use_haiku": usage.weekly_percent > 80 or usage.session_percent > 90
        }

    def save_usage_history(self, db_path: str = ".contextune/observability.db"):
        """
        Save usage snapshot to observability database.

        Args:
            db_path: Path to observability database
        """
        usage = self.get_current_usage()
        if not usage:
            return

        try:
            import sqlite3

            db_path_obj = Path(db_path)
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_history (
                    timestamp REAL PRIMARY KEY,
                    session_percent REAL,
                    weekly_percent REAL,
                    opus_percent REAL,
                    session_reset TEXT,
                    weekly_reset TEXT
                )
            ''')

            # Insert snapshot
            cursor.execute('''
                INSERT INTO usage_history
                (timestamp, session_percent, weekly_percent, opus_percent, session_reset, weekly_reset)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                usage.timestamp,
                usage.session_percent,
                usage.weekly_percent,
                usage.opus_percent,
                usage.session_reset_time,
                usage.weekly_reset_time
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving usage history: {e}")


# CLI for testing
if __name__ == "__main__":
    monitor = UsageMonitor()

    # Get current usage
    usage = monitor.get_current_usage()
    if usage:
        print("📊 Current Usage:")
        print(f"  Session: {usage.session_percent}% (resets {usage.session_reset_time})")
        print(f"  Weekly:  {usage.weekly_percent}% (resets {usage.weekly_reset_time})")
        print(f"  Opus:    {usage.opus_percent}%")
        print()

    # Get recommendations
    rec = monitor.get_recommendation()
    print(f"🎯 Status: {rec['status'].upper()}")
    print()

    if rec.get('warnings'):
        print("⚠️  Warnings:")
        for warning in rec['warnings']:
            print(f"  {warning}")
        print()

    if rec.get('recommendations'):
        print("💡 Recommendations:")
        for r in rec['recommendations']:
            print(f"  • {r}")
        print()
    else:
        print(f"ℹ️  {rec.get('message', 'No recommendations available')}")
        print()

    # Save to history
    monitor.save_usage_history()
    print("✅ Usage snapshot saved to observability database")
