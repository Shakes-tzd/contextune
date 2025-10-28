#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
PostToolUse hook to track actual costs vs. estimates.

Compares routing decisions with actual token usage to:
1. Validate routing decisions
2. Track cumulative costs
3. Calculate actual Haiku vs Sonnet savings
4. Feed data to weekly review
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.observability_db import ObservabilityDB


class CostTracker:
    """
    Track actual tool costs and compare with routing estimates.

    Cost model (per 1K tokens):
    - Sonnet input: $0.003
    - Sonnet output: $0.015
    - Haiku input: $0.00025
    - Haiku output: $0.00125
    """

    SONNET_INPUT_COST = 0.003
    SONNET_OUTPUT_COST = 0.015
    HAIKU_INPUT_COST = 0.00025
    HAIKU_OUTPUT_COST = 0.00125

    def __init__(self):
        self.db = ObservabilityDB()

    def track_tool_usage(
        self,
        tool_name: str,
        tool_params: dict[str, Any],
        result: Any,
        model_used: str = "sonnet",  # "sonnet" or "haiku"
    ) -> dict[str, Any]:
        """
        Track actual tool usage and calculate costs.

        Args:
            tool_name: Name of tool used
            tool_params: Tool parameters
            result: Tool result/output
            model_used: Which model executed the tool

        Returns:
            Cost analysis dictionary
        """

        # Estimate tokens from result
        estimated_tokens = self._estimate_tokens(tool_name, result)

        # Calculate actual cost
        if model_used == "sonnet":
            input_cost = (estimated_tokens / 1000) * self.SONNET_INPUT_COST
            output_cost = (estimated_tokens / 1000) * self.SONNET_OUTPUT_COST
            total_cost = input_cost + output_cost
        else:  # haiku
            input_cost = (estimated_tokens / 1000) * self.HAIKU_INPUT_COST
            output_cost = (estimated_tokens / 1000) * self.HAIKU_OUTPUT_COST
            total_cost = input_cost + output_cost

        # Calculate potential savings if wrong model used
        if model_used == "sonnet":
            haiku_cost = (estimated_tokens / 1000) * (
                self.HAIKU_INPUT_COST + self.HAIKU_OUTPUT_COST
            )
            potential_savings = total_cost - haiku_cost
        else:
            potential_savings = 0.0  # Already using cheapest model

        cost_analysis = {
            "tool": tool_name,
            "model": model_used,
            "estimated_tokens": estimated_tokens,
            "actual_cost": total_cost,
            "potential_savings": potential_savings,
            "efficiency": "optimal" if potential_savings <= 0 else "suboptimal",
        }

        return cost_analysis

    def _estimate_tokens(self, tool_name: str, result: Any) -> int:
        """
        Estimate tokens from tool result.

        Rough heuristics:
        - Read: ~2 tokens per line
        - Bash: ~0.5 tokens per char
        - Grep: ~1 token per match
        - Other: ~100 tokens baseline
        """

        if isinstance(result, dict):
            result_str = json.dumps(result)
        else:
            result_str = str(result)

        # Tool-specific heuristics
        if tool_name == "Read":
            line_count = result_str.count("\n")
            return line_count * 2
        elif tool_name == "Bash":
            return len(result_str) // 2
        elif tool_name == "Grep":
            match_count = result_str.count("\n")
            return match_count * 1
        else:
            # Generic: ~4 chars per token
            return len(result_str) // 4

    def log_cost_metrics(self, cost_analysis: dict[str, Any]):
        """Log cost metrics to observability database."""

        self.db.log_performance_metric(
            component="cost_tracker",
            operation="tool_cost",
            latency_ms=0.0,
            metadata={
                "tool": cost_analysis["tool"],
                "model": cost_analysis["model"],
                "tokens": cost_analysis["estimated_tokens"],
                "cost": cost_analysis["actual_cost"],
                "savings": cost_analysis["potential_savings"],
                "efficiency": cost_analysis["efficiency"],
            },
        )


def main():
    """Main entry point for PostToolUse hook."""
    try:
        # Read hook input from stdin
        hook_data: dict[str, Any] = json.load(sys.stdin)

        tool: dict[str, Any] = hook_data.get("tool", {})
        tool_name: str = tool.get("name", "")
        tool_params: dict[str, Any] = tool.get("parameters", {})
        result: Any = hook_data.get("result", {})

        # Detect which model was used
        # Heuristic: If result is very large but fast, likely Haiku
        # For now, assume Sonnet (can be enhanced with actual detection)
        model_used = "sonnet"

        # Track cost
        tracker = CostTracker()
        cost_analysis = tracker.track_tool_usage(
            tool_name, tool_params, result, model_used
        )

        # Log to database
        tracker.log_cost_metrics(cost_analysis)

        # Generate feedback if significant savings possible
        if cost_analysis["potential_savings"] > 0.01:  # $0.01 threshold
            feedback = f"""
💰 **Cost Optimization Opportunity**

Tool: `{tool_name}`
Current cost: ${cost_analysis["actual_cost"]:.4f}
Potential savings: ${cost_analysis["potential_savings"]:.4f}

This operation could be delegated to Haiku for cost efficiency.
            """.strip()

            output = {"continue": True, "additionalContext": feedback}
        else:
            output = {"continue": True}

        print(json.dumps(output))

    except Exception as e:
        # Log error but don't block
        try:
            db = ObservabilityDB()
            db.log_error(
                component="cost_tracker",
                message=str(e),
                error_type=type(e).__name__,
            )
        except Exception:
            pass

        # Always continue
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
