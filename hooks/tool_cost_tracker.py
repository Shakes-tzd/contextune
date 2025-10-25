#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "logfire>=0.1.0",
# ]
# ///

"""
PostToolUse hook to track actual costs vs. estimates.
Compares routing decisions with actual token usage.
"""

import json
import sys
from pathlib import Path

import logfire

sys.path.insert(0, str(Path(__file__).parent))
from utils.logfire_config import configure_logfire_for_hooks

configure_logfire_for_hooks("PostToolUse-CostTracking")


def main():
    try:
        with logfire.span("hook.PostToolUse.CostTracking"):
            hook_data = json.load(sys.stdin)

            # Extract actual usage
            tool_name = hook_data.get("tool", {}).get("name", "")
            tool_result = hook_data.get("tool_result", {})

            # Parse actual token usage from result
            actual_tokens = estimate_tokens_from_result(tool_result)

            # Log actual vs estimated
            logfire.info(
                "Actual tool usage",
                tool_name=tool_name,
                actual_tokens=actual_tokens,
                result_size_bytes=len(str(tool_result)),
            )

            logfire.metric(
                "routing.actual_tokens", value=actual_tokens, tags={"tool": tool_name}
            )

            print(json.dumps({"continue": True}))

    except Exception as e:
        logfire.error("Cost tracking error", error=str(e))
        print(json.dumps({"continue": True}))


def estimate_tokens_from_result(result: dict) -> int:
    """Estimate tokens from tool result."""
    result_str = json.dumps(result)
    return len(result_str) // 4


if __name__ == "__main__":
    main()
