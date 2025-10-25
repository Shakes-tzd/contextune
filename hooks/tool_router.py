#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "logfire>=0.1.0",
# ]
# ///

"""
Intelligent Tool Router for Claude Code.

Routes tool calls to optimal execution strategy:
- Direct Sonnet execution for small operations
- Haiku filtering for large operations
- Parallel Haiku tasks for multi-file operations

Tracks costs, performance, and decision quality via Logfire.
"""

import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import logfire

# Import shared Logfire configuration
sys.path.insert(0, str(Path(__file__).parent))
try:
    from utils.logfire_config import configure_logfire_for_hooks

    configure_logfire_for_hooks("PreToolUse-IntelligentRouter")
except ImportError:
    logfire.configure(
        token=os.getenv("LOGFIRE_TOKEN"),
        send_to_logfire=True if os.getenv("LOGFIRE_TOKEN") else False,
        console=False,
    )


class RoutingDecision(Enum):
    """Possible routing decisions."""

    DIRECT = "direct"  # Execute directly with main Sonnet
    DELEGATE_HAIKU = "delegate"  # Delegate to single Haiku subagent
    PARALLEL_HAIKU = "parallel"  # Use parallel Haiku subagents
    BLOCK_OPTIMIZE = "block"  # Block and suggest optimization


@dataclass
class CostEstimate:
    """Cost estimation for different execution strategies."""

    direct_sonnet_cost: float
    haiku_filtered_cost: float
    savings: float
    savings_percent: float


@dataclass
class RoutingMetrics:
    """Metrics for routing decision."""

    estimated_tokens: int
    file_size_bytes: int | None
    operation_type: str
    context_window_usage: float
    parallelization_possible: bool
    compression_ratio: float | None


class IntelligentRouter:
    """Routes tool calls based on runtime analysis."""

    # Configurable thresholds
    SMALL_OPERATION_THRESHOLD = 20_000  # tokens
    MEDIUM_OPERATION_THRESHOLD = 50_000  # tokens
    HAIKU_OVERHEAD = 20_000  # startup cost

    # Context pressure thresholds
    CONTEXT_WARNING = 150_000  # tokens
    CONTEXT_CRITICAL = 180_000  # tokens

    def __init__(self):
        self.session_id = os.getenv("CLAUDE_SESSION_ID", "unknown")
        self.context_usage = self._estimate_context_usage()

    def _estimate_context_usage(self) -> int:
        """Estimate current context window usage."""
        # Check if we have a context tracking file
        context_file = Path(f"/tmp/claude-context-{self.session_id}.txt")
        if context_file.exists():
            try:
                return int(context_file.read_text().strip())
            except:
                pass
        return 0

    def route_read_operation(
        self, file_path: str, description: str
    ) -> tuple[RoutingDecision, dict[str, Any], CostEstimate, RoutingMetrics]:
        """Route a Read tool operation."""

        # Gather metrics
        file_size = self._get_file_size(file_path)
        estimated_tokens = (file_size // 4) if file_size else 10_000

        metrics = RoutingMetrics(
            estimated_tokens=estimated_tokens,
            file_size_bytes=file_size,
            operation_type="read_single_file",
            context_window_usage=self.context_usage / 200_000,
            parallelization_possible=False,
            compression_ratio=None,
        )

        # Cost calculation
        costs = self._calculate_costs(estimated_tokens, compression_ratio=0.1)

        # Decision logic
        decision = self._make_routing_decision(metrics, costs)

        # Build response context
        context = self._build_routing_context(
            decision, metrics, costs, file_path, description
        )

        return decision, context, costs, metrics

    def route_bash_operation(
        self, command: str, description: str
    ) -> tuple[RoutingDecision, dict[str, Any], CostEstimate, RoutingMetrics]:
        """Route a Bash tool operation."""

        # Estimate output size based on command patterns
        estimated_output = self._estimate_bash_output(command)

        metrics = RoutingMetrics(
            estimated_tokens=estimated_output,
            file_size_bytes=None,
            operation_type="bash_command",
            context_window_usage=self.context_usage / 200_000,
            parallelization_possible=self._can_parallelize_command(command),
            compression_ratio=None,
        )

        costs = self._calculate_costs(estimated_output, compression_ratio=0.2)
        decision = self._make_routing_decision(metrics, costs)
        context = self._build_routing_context(
            decision, metrics, costs, command, description
        )

        return decision, context, costs, metrics

    def route_search_operation(
        self, pattern: str, scope: str
    ) -> tuple[RoutingDecision, dict[str, Any], CostEstimate, RoutingMetrics]:
        """Route a Grep/Glob search operation."""

        # Estimate number of files and potential matches
        file_count = self._estimate_file_count(pattern, scope)
        estimated_tokens = file_count * 5_000  # Rough estimate per file

        metrics = RoutingMetrics(
            estimated_tokens=estimated_tokens,
            file_size_bytes=None,
            operation_type="search_multiple_files",
            context_window_usage=self.context_usage / 200_000,
            parallelization_possible=file_count > 5,
            compression_ratio=0.9,  # Searches typically filter heavily
        )

        costs = self._calculate_costs(estimated_tokens, compression_ratio=0.9)
        decision = self._make_routing_decision(metrics, costs)
        context = self._build_routing_context(decision, metrics, costs, pattern, scope)

        return decision, context, costs, metrics

    def _make_routing_decision(
        self, metrics: RoutingMetrics, costs: CostEstimate
    ) -> RoutingDecision:
        """Make routing decision based on metrics and costs."""

        # Context pressure adjustment
        if self.context_usage > self.CONTEXT_CRITICAL:
            # Aggressive filtering when context is critical
            if metrics.estimated_tokens > 30_000:
                return RoutingDecision.DELEGATE_HAIKU
        elif self.context_usage > self.CONTEXT_WARNING:
            # Moderate filtering when context is warning
            if metrics.estimated_tokens > 50_000:
                return RoutingDecision.DELEGATE_HAIKU

        # Standard routing logic
        if metrics.estimated_tokens < self.SMALL_OPERATION_THRESHOLD:
            return RoutingDecision.DIRECT

        if metrics.parallelization_possible and metrics.estimated_tokens > 100_000:
            return RoutingDecision.PARALLEL_HAIKU

        if (
            costs.savings > 0.05
            and metrics.estimated_tokens > self.MEDIUM_OPERATION_THRESHOLD
        ):
            return RoutingDecision.DELEGATE_HAIKU

        return RoutingDecision.DIRECT

    def _calculate_costs(
        self, tokens: int, compression_ratio: float = 0.1
    ) -> CostEstimate:
        """Calculate cost estimates for different strategies."""

        # Direct Sonnet cost
        direct_cost = tokens * 3 / 1_000_000

        # Haiku filtered cost
        haiku_input = self.HAIKU_OVERHEAD + tokens
        haiku_output = tokens * compression_ratio
        haiku_total = (haiku_input * 1 / 1_000_000) + (haiku_output * 5 / 1_000_000)

        # Sonnet processing filtered results
        sonnet_filtered = haiku_output * 3 / 1_000_000

        total_filtered_cost = haiku_total + sonnet_filtered
        savings = direct_cost - total_filtered_cost
        savings_percent = (savings / direct_cost * 100) if direct_cost > 0 else 0

        return CostEstimate(
            direct_sonnet_cost=direct_cost,
            haiku_filtered_cost=total_filtered_cost,
            savings=savings,
            savings_percent=savings_percent,
        )

    def _build_routing_context(
        self,
        decision: RoutingDecision,
        metrics: RoutingMetrics,
        costs: CostEstimate,
        target: str,
        description: str,
    ) -> dict[str, Any]:
        """Build context to return to Claude."""

        if decision == RoutingDecision.DIRECT:
            return {"continue": True}

        # Build recommendation message
        lines = ["⚡ **Intelligent Routing Suggestion**", ""]

        if decision == RoutingDecision.DELEGATE_HAIKU:
            lines.extend(
                [
                    f"**Operation:** {metrics.operation_type}",
                    f"**Estimated tokens:** ~{metrics.estimated_tokens:,}",
                    "**Recommended:** Delegate to Haiku subagent",
                    "",
                    f"💰 **Cost savings:** ${costs.savings:.4f} ({costs.savings_percent:.1f}%)",
                    f"📊 **Context usage:** {metrics.context_window_usage:.1%}",
                    "",
                    "**Suggested Task:**",
                    "```",
                    f"Use a Haiku Task to process: {target}",
                    f"Filter to only: {description}",
                    "Return summary under 2K tokens with key findings.",
                    "```",
                ]
            )

        elif decision == RoutingDecision.PARALLEL_HAIKU:
            lines.extend(
                [
                    f"**Operation:** {metrics.operation_type}",
                    f"**Estimated tokens:** ~{metrics.estimated_tokens:,}",
                    "**Recommended:** Parallel Haiku tasks",
                    "",
                    "⚡ **Speed benefit:** 3-5x faster",
                    "💰 **Similar cost, better throughput**",
                    "",
                    "**Suggested Approach:**",
                    "```",
                    "Launch 3 parallel Haiku Tasks to process:",
                    f"{target}",
                    "Each handles 1/3 of the work, returns filtered results.",
                    "Combine results for final analysis.",
                    "```",
                ]
            )

        return {"additionalContext": "\n".join(lines), "continue": True}

    # Helper methods
    def _get_file_size(self, file_path: str) -> int | None:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except:
            return None

    def _estimate_bash_output(self, command: str) -> int:
        """Estimate bash command output size."""
        large_output_patterns = [
            "git log",
            "docker logs",
            "npm list",
            "find",
            "cat.*\\.log",
            "grep -r",
        ]

        for pattern in large_output_patterns:
            if pattern in command:
                return 100_000

        return 5_000  # Default small output

    def _can_parallelize_command(self, command: str) -> bool:
        """Check if bash command can be parallelized."""
        parallel_patterns = ["find", "grep -r", "git log --all"]
        return any(p in command for p in parallel_patterns)

    def _estimate_file_count(self, pattern: str, scope: str) -> int:
        """Estimate number of files matching pattern."""
        # This is a rough estimate - could be improved with actual glob
        try:
            import glob

            matches = glob.glob(pattern, recursive=True)
            return len(matches)
        except:
            return 10  # Default estimate


def main():
    """Main entry point for intelligent routing hook."""
    exit_code = 0

    try:
        with logfire.span("hook.PreToolUse.IntelligentRouter") as span:
            # Read hook data
            hook_data = json.load(sys.stdin)

            tool_name = hook_data.get("tool", {}).get("name", "")
            tool_input = hook_data.get("tool", {}).get("parameters", {})

            logfire.info(
                "Intelligent routing hook triggered",
                tool_name=tool_name,
                session_id=os.getenv("CLAUDE_SESSION_ID", "unknown"),
            )

            # Initialize router
            router = IntelligentRouter()

            # Route based on tool type
            decision = None
            context = {"continue": True}
            costs = None
            metrics = None

            if tool_name == "Read":
                file_path = tool_input.get("file_path", "")
                description = tool_input.get("description", "")

                with logfire.span("route_read_operation"):
                    decision, context, costs, metrics = router.route_read_operation(
                        file_path, description
                    )

            elif tool_name == "Bash":
                command = tool_input.get("command", "")
                description = tool_input.get("description", "")

                with logfire.span("route_bash_operation"):
                    decision, context, costs, metrics = router.route_bash_operation(
                        command, description
                    )

            elif tool_name in ["Grep", "Glob"]:
                pattern = tool_input.get("pattern", "")
                scope = tool_input.get("scope", "")

                with logfire.span("route_search_operation"):
                    decision, context, costs, metrics = router.route_search_operation(
                        pattern, scope
                    )

            else:
                # Unknown tool, allow it
                logfire.debug("Unknown tool type, allowing", tool_name=tool_name)
                print(json.dumps({"continue": True}))
                return

            # Log detailed metrics
            if decision and metrics and costs:
                logfire.info(
                    "Routing decision made",
                    decision=decision.value,
                    tool_name=tool_name,
                    estimated_tokens=metrics.estimated_tokens,
                    file_size_bytes=metrics.file_size_bytes,
                    operation_type=metrics.operation_type,
                    context_usage_percent=metrics.context_window_usage,
                    parallelization_possible=metrics.parallelization_possible,
                    direct_cost=costs.direct_sonnet_cost,
                    filtered_cost=costs.haiku_filtered_cost,
                    savings_dollars=costs.savings,
                    savings_percent=costs.savings_percent,
                    compression_ratio=metrics.compression_ratio,
                )

                # Track decision for weekly analysis
                logfire.metric(
                    "routing.decision",
                    value=1,
                    tags={
                        "decision": decision.value,
                        "tool": tool_name,
                        "operation": metrics.operation_type,
                    },
                )

                logfire.metric(
                    "routing.cost_savings",
                    value=costs.savings,
                    tags={"decision": decision.value, "tool": tool_name},
                )

            # Return decision to Claude
            print(json.dumps(context))

    except json.JSONDecodeError as e:
        logfire.error("Failed to parse hook data", error=str(e))
        print(json.dumps({"continue": True}))
    except Exception as e:
        logfire.error(
            "Intelligent router error", error=str(e), error_type=type(e).__name__
        )
        print(json.dumps({"continue": True}))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
