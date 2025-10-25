#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Contextune Observability Dashboard

Beautiful, real-time dashboard showing:
- Detection statistics
- Performance metrics (P50/P95/P99)
- Matcher efficiency
- Recent errors
- System health
"""

import sys
from pathlib import Path

# Add lib directory to path
PLUGIN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

from observability_db import ObservabilityDB
import json
from datetime import datetime


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.0f}s ago"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m ago"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h ago"
    else:
        return f"{seconds/86400:.1f}d ago"


def render_dashboard():
    """Render comprehensive observability dashboard."""
    db = ObservabilityDB(".contextune/observability.db")
    stats = db.get_stats()

    print("=" * 70)
    print("🎯 CONTEXTUNE OBSERVABILITY DASHBOARD".center(70))
    print("=" * 70)
    print()

    # === DETECTION STATISTICS ===
    det_stats = stats["detections"]
    print("📊 DETECTION STATISTICS")
    print("-" * 70)
    print(f"  Total Detections:  {det_stats['total']}")
    print()

    if det_stats["by_method"]:
        print("  By Detection Method:")
        for method, count in sorted(det_stats["by_method"].items(), key=lambda x: x[1], reverse=True):
            pct = (count / det_stats['total'] * 100) if det_stats['total'] > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"    {method:15s} {count:4d} ({pct:5.1f}%) {bar}")
    print()

    if det_stats["by_command"]:
        print("  Top Commands:")
        for cmd, count in list(det_stats["by_command"].items())[:5]:
            pct = (count / det_stats['total'] * 100) if det_stats['total'] > 0 else 0
            print(f"    {cmd:20s} {count:4d} ({pct:5.1f}%)")
    print()

    # === MATCHER PERFORMANCE ===
    matcher_stats = stats["matchers"]
    if matcher_stats:
        print("⚡ MATCHER PERFORMANCE")
        print("-" * 70)
        print(f"  {'Method':<15s} {'Avg Latency':>12s} {'Success Rate':>12s}")
        print(f"  {'-'*15} {'-'*12} {'-'*12}")

        # Sort by latency
        for method in ["keyword", "model2vec", "semantic"]:
            if method in matcher_stats:
                m = matcher_stats[method]
                latency = m["avg_latency_ms"]
                success = m["success_rate"]

                # Color code latency
                if latency < 1:
                    latency_str = f"✓ {latency:.3f}ms"
                elif latency < 10:
                    latency_str = f"→ {latency:.2f}ms"
                else:
                    latency_str = f"⚠ {latency:.1f}ms"

                print(f"  {method:<15s} {latency_str:>12s} {success:>11.1f}%")
        print()

    # === PERFORMANCE METRICS ===
    perf_stats = stats["performance"]
    if perf_stats:
        print("📈 SYSTEM PERFORMANCE")
        print("-" * 70)
        print(f"  {'Component':<20s} {'P50':>8s} {'P95':>8s} {'P99':>8s} {'Count':>8s}")
        print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for component, metrics in perf_stats.items():
            p50 = metrics["p50"]
            p95 = metrics["p95"]
            p99 = metrics["p99"]
            count = metrics["count"]

            print(f"  {component:<20s} {p50:>7.2f}ms {p95:>7.2f}ms {p99:>7.2f}ms {count:>8d}")
        print()

    # === RECENT DETECTIONS ===
    recent = db.get_recent_detections(5)
    if recent:
        print("🔍 RECENT DETECTIONS (Last 5)")
        print("-" * 70)
        for d in recent:
            timestamp = datetime.fromtimestamp(d["timestamp"])
            time_ago = format_duration(datetime.now().timestamp() - d["timestamp"])
            prompt = d.get("prompt_preview", "")[:40]
            latency = d.get("latency_ms", 0)

            print(f"  {timestamp.strftime('%H:%M:%S')} ({time_ago})")
            print(f"    → {d['command']} ({d['confidence']*100:.0f}% {d['method']}, {latency:.3f}ms)")
            if prompt:
                print(f"    Prompt: \"{prompt}\"")
            print()

    # === ERROR TRACKING ===
    error_stats = stats["errors"]
    if error_stats["total"] > 0:
        print("❌ ERROR TRACKING")
        print("-" * 70)
        print(f"  Total Errors: {error_stats['total']}")
        print()

        if error_stats["by_component"]:
            print("  By Component:")
            for component, count in sorted(error_stats["by_component"].items(), key=lambda x: x[1], reverse=True):
                print(f"    {component:20s} {count:4d}")
            print()

        # Recent errors
        recent_errors = db.get_error_summary(24)
        if recent_errors:
            print("  Recent Errors (Last 24h):")
            for err in recent_errors[:3]:
                timestamp = datetime.fromtimestamp(err["timestamp"])
                time_ago = format_duration(datetime.now().timestamp() - err["timestamp"])
                print(f"    [{timestamp.strftime('%H:%M:%S')}] {err['component']}")
                print(f"      {err['error_type']}: {err['message']}")
                print(f"      ({time_ago})")
                print()

    # === SYSTEM HEALTH ===
    print("🏥 SYSTEM HEALTH")
    print("-" * 70)

    # Calculate health score
    health_score = 100

    # Deduct for errors
    if error_stats["total"] > 0:
        error_penalty = min(30, error_stats["total"] * 5)
        health_score -= error_penalty

    # Deduct for slow performance
    if perf_stats:
        for component, metrics in perf_stats.items():
            if metrics["p95"] > 100:  # > 100ms is slow
                health_score -= 10

    # Health indicator
    if health_score >= 90:
        health_icon = "✅"
        health_status = "Excellent"
    elif health_score >= 70:
        health_icon = "✓"
        health_status = "Good"
    elif health_score >= 50:
        health_icon = "⚠"
        health_status = "Fair"
    else:
        health_icon = "❌"
        health_status = "Poor"

    print(f"  Overall Health: {health_icon} {health_score}/100 ({health_status})")
    print()

    # === RECOMMENDATIONS ===
    recommendations = []

    if matcher_stats.get("semantic", {}).get("success_rate", 0) < 50:
        recommendations.append("⚠ Semantic router has low success rate - check Cohere API key")

    if error_stats["total"] > 10:
        recommendations.append("⚠ High error count - review error logs")

    if perf_stats.get("hook", {}).get("p95", 0) > 50:
        recommendations.append("⚠ Hook P95 latency >50ms - may impact UX")

    if det_stats["total"] < 10:
        recommendations.append("💡 Try natural language queries like 'research best React libraries'")

    if recommendations:
        print("💡 RECOMMENDATIONS")
        print("-" * 70)
        for rec in recommendations:
            print(f"  {rec}")
        print()

    print("=" * 70)
    print()
    print("💡 Commands:")
    print("  /ctx:help       Full command reference")
    print("  /ctx:research   Fast parallel research")
    print("  /ctx:plan       Create parallel development plan")
    print()


if __name__ == "__main__":
    try:
        render_dashboard()
    except FileNotFoundError:
        print("⚠ No observability data yet. Use Contextune first to collect metrics!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error rendering dashboard: {e}", file=sys.stderr)
        sys.exit(1)
