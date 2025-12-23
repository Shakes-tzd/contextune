#!/bin/bash
# Extract Plan from Current Session
#
# ⚠️  DEPRECATED: /ctx:plan now creates files directly via PlanBuilder
#
# This script remains for backward compatibility with old plans
# created before the direct file creation refactor.
#
# New workflow: /ctx:plan uses PlanBuilder → Files created immediately
# Old workflow: /ctx:plan output → This script → Files extracted (error-prone)
#
# Finds the current session's transcript and extracts plan to .parallel/plans/
#
# Usage: ./scripts/extract-current-plan.sh

set -e

echo "⚠️  DEPRECATED: This extraction script is no longer needed for new plans." >&2
echo "   /ctx:plan now creates files directly using PlanBuilder." >&2
echo "   This script is running for backward compatibility with old plans." >&2
echo "" >&2

# Find most recent transcript file
# Claude Code stores transcripts at: ~/.claude/projects/-<FULL_PATH_WITH_SLASHES_AS_DASHES>/<session-id>.jsonl
ESCAPED_PATH=$(pwd | sed 's/\//-/g')
TRANSCRIPT_DIR="$HOME/.claude/projects/$ESCAPED_PATH"

if [ ! -d "$TRANSCRIPT_DIR" ]; then
    echo "❌ Error: Transcript directory not found: $TRANSCRIPT_DIR" >&2
    echo "Are you in a Claude Code project directory?" >&2
    exit 1
fi

# Get most recent transcript file (exclude subagent transcripts with "agent-" prefix)
# Subagents never contain plans, only main sessions do
TRANSCRIPT_FILE=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | grep -v "/agent-" | head -1)

if [ -z "$TRANSCRIPT_FILE" ]; then
    echo "❌ Error: No transcript files found in $TRANSCRIPT_DIR" >&2
    exit 1
fi

echo "🔍 Found transcript: $TRANSCRIPT_FILE" >&2
echo "🔍 Extracting plan..." >&2

# Run extraction script with transcript path
uv run "$(dirname "$0")/extract-plan-from-context.py" "$TRANSCRIPT_FILE"
