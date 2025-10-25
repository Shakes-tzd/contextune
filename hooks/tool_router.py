#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Intelligent Tool Router for Claude Code.

Routes tool calls to optimal execution strategy:
- Direct Sonnet execution for small operations
- Haiku delegation for large operations
- Parallel Haiku tasks for multi-file operations

Tracks routing decisions via observability database.
"""

import json
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.observability_db import ObservabilityDB


class RoutingDecision(Enum):
    """Routing decision types."""
    SONNET_DIRECT = "sonnet_direct"
    HAIKU_DELEGATE = "haiku_delegate"
    HAIKU_PARALLEL = "haiku_parallel"


@dataclass
class RoutingResult:
    """Result of routing decision."""
    decision: RoutingDecision
    reason: str
    estimated_cost_sonnet: float
    estimated_cost_haiku: float
    savings: float
    metadata: Dict[str, Any]


class IntelligentRouter:
    """
    Routes tool calls based on operation characteristics.

    Thresholds:
    - Read: >1000 lines → Haiku
    - Bash: >5 commands → Haiku
    - Grep: Always fast, keep Sonnet
    - Multi-file: >3 files → Parallel Haiku
    """

    # Cost estimates (per 1K tokens)
    SONNET_INPUT_COST = 0.003  # $3 per million
    SONNET_OUTPUT_COST = 0.015  # $15 per million
    HAIKU_INPUT_COST = 0.00025  # $0.25 per million
    HAIKU_OUTPUT_COST = 0.00125  # $1.25 per million

    # Thresholds
    READ_LINE_THRESHOLD = 1000
    BASH_COMMAND_THRESHOLD = 5
    MULTI_FILE_THRESHOLD = 3

    def __init__(self):
        self.db = ObservabilityDB()

    def route_tool_call(self, tool_name: str, tool_params: Dict[str, Any]) -> RoutingResult:
        """
        Determine optimal routing for a tool call.

        Args:
            tool_name: Name of the tool being called
            tool_params: Parameters for the tool

        Returns:
            RoutingResult with decision and cost analysis
        """

        if tool_name == "Read":
            return self._route_read(tool_params)
        elif tool_name == "Bash":
            return self._route_bash(tool_params)
        elif tool_name == "Grep":
            return self._route_grep(tool_params)
        elif tool_name == "Glob":
            return self._route_glob(tool_params)
        else:
            # Default: Sonnet handles all other tools
            return RoutingResult(
                decision=RoutingDecision.SONNET_DIRECT,
                reason="Tool not eligible for delegation",
                estimated_cost_sonnet=0.0,
                estimated_cost_haiku=0.0,
                savings=0.0,
                metadata={"tool": tool_name}
            )

    def _route_read(self, params: Dict[str, Any]) -> RoutingResult:
        """Route Read operations."""
        file_path = params.get("file_path", "")

        # Try to estimate file size
        try:
            path = Path(file_path)
            if path.exists():
                line_count = len(path.read_text().split("\n"))
            else:
                # Assume medium file
                line_count = 500
        except:
            line_count = 500

        if line_count > self.READ_LINE_THRESHOLD:
            # Large file - delegate to Haiku
            estimated_tokens = line_count * 2  # Rough estimate
            cost_sonnet = (estimated_tokens / 1000) * self.SONNET_INPUT_COST
            cost_haiku = (estimated_tokens / 1000) * self.HAIKU_INPUT_COST
            savings = cost_sonnet - cost_haiku

            return RoutingResult(
                decision=RoutingDecision.HAIKU_DELEGATE,
                reason=f"Large file ({line_count} lines) - delegate to Haiku",
                estimated_cost_sonnet=cost_sonnet,
                estimated_cost_haiku=cost_haiku,
                savings=savings,
                metadata={
                    "file": file_path,
                    "line_count": line_count,
                    "threshold": self.READ_LINE_THRESHOLD
                }
            )
        else:
            # Small file - Sonnet direct
            estimated_tokens = line_count * 2
            cost_sonnet = (estimated_tokens / 1000) * self.SONNET_INPUT_COST

            return RoutingResult(
                decision=RoutingDecision.SONNET_DIRECT,
                reason=f"Small file ({line_count} lines) - Sonnet optimal",
                estimated_cost_sonnet=cost_sonnet,
                estimated_cost_haiku=0.0,
                savings=0.0,
                metadata={
                    "file": file_path,
                    "line_count": line_count
                }
            )

    def _route_bash(self, params: Dict[str, Any]) -> RoutingResult:
        """Route Bash operations."""
        command = params.get("command", "")

        # Count commands (rough heuristic: && or ; separators)
        command_count = command.count("&&") + command.count(";") + 1

        if command_count > self.BASH_COMMAND_THRESHOLD:
            # Multiple commands - delegate to Haiku
            estimated_tokens = len(command) * 0.5  # Rough estimate
            cost_sonnet = (estimated_tokens / 1000) * self.SONNET_INPUT_COST
            cost_haiku = (estimated_tokens / 1000) * self.HAIKU_INPUT_COST
            savings = cost_sonnet - cost_haiku

            return RoutingResult(
                decision=RoutingDecision.HAIKU_DELEGATE,
                reason=f"Complex bash ({command_count} commands) - delegate to Haiku",
                estimated_cost_sonnet=cost_sonnet,
                estimated_cost_haiku=cost_haiku,
                savings=savings,
                metadata={
                    "command_preview": command[:100],
                    "command_count": command_count,
                    "threshold": self.BASH_COMMAND_THRESHOLD
                }
            )
        else:
            # Simple command - Sonnet direct
            return RoutingResult(
                decision=RoutingDecision.SONNET_DIRECT,
                reason=f"Simple bash ({command_count} commands) - Sonnet optimal",
                estimated_cost_sonnet=0.01,
                estimated_cost_haiku=0.0,
                savings=0.0,
                metadata={
                    "command_preview": command[:100],
                    "command_count": command_count
                }
            )

    def _route_grep(self, params: Dict[str, Any]) -> RoutingResult:
        """Route Grep operations - always fast, keep on Sonnet."""
        return RoutingResult(
            decision=RoutingDecision.SONNET_DIRECT,
            reason="Grep is fast - Sonnet optimal",
            estimated_cost_sonnet=0.001,
            estimated_cost_haiku=0.0,
            savings=0.0,
            metadata={"pattern": params.get("pattern", "")}
        )

    def _route_glob(self, params: Dict[str, Any]) -> RoutingResult:
        """Route Glob operations - always fast, keep on Sonnet."""
        return RoutingResult(
            decision=RoutingDecision.SONNET_DIRECT,
            reason="Glob is fast - Sonnet optimal",
            estimated_cost_sonnet=0.001,
            estimated_cost_haiku=0.0,
            savings=0.0,
            metadata={"pattern": params.get("pattern", "")}
        )


def main():
    """Main entry point for PreToolUse hook."""
    try:
        # Read hook input from stdin
        hook_data = json.load(sys.stdin)

        tool = hook_data.get("tool", {})
        tool_name = tool.get("name", "")
        tool_params = tool.get("parameters", {})

        # Route the tool call
        router = IntelligentRouter()
        result = router.route_tool_call(tool_name, tool_params)

        # Log routing decision to observability database
        router.db.log_performance_metric(
            component="tool_router",
            operation="route_decision",
            latency_ms=0.0,  # Routing is near-instant
            metadata={
                "tool": tool_name,
                "decision": result.decision.value,
                "reason": result.reason,
                "estimated_savings": result.savings,
                **result.metadata
            }
        )

        # Generate feedback for Claude
        if result.decision == RoutingDecision.HAIKU_DELEGATE:
            feedback = f"""
⚡ **Routing Suggestion**

Tool: `{tool_name}`
Decision: Delegate to Haiku agent
Reason: {result.reason}
Estimated savings: ${result.savings:.4f}

Consider using the Task tool with subagent_type="general-purpose" for this operation.
            """.strip()

            # Return suggestion (don't block)
            output = {
                "continue": True,
                "additionalContext": feedback
            }
        else:
            # Direct execution - no feedback needed
            output = {"continue": True}

        print(json.dumps(output))

    except Exception as e:
        # Log error but don't block tool execution
        try:
            db = ObservabilityDB()
            db.log_error(
                component="tool_router",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"hook": "PreToolUse"}
            )
        except:
            pass

        # Always allow tool to continue
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
