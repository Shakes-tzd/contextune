#!/bin/bash
# Extract Plan from Current Session
#
# Finds the current session's transcript and extracts plan to .parallel/plans/
#
# Usage: ./scripts/extract-current-plan.sh

set -e

# Find most recent transcript file
# Claude Code stores transcripts at: ~/.claude/projects/-<FULL_PATH_WITH_SLASHES_AS_DASHES>/<session-id>.jsonl
ESCAPED_PATH=$(pwd | sed 's/\//-/g')
TRANSCRIPT_DIR="$HOME/.claude/projects/$ESCAPED_PATH"

if [ ! -d "$TRANSCRIPT_DIR" ]; then
    echo "❌ Error: Transcript directory not found: $TRANSCRIPT_DIR" >&2
    echo "Are you in a Claude Code project directory?" >&2
    exit 1
fi

# Get most recent transcript file
TRANSCRIPT_FILE=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | head -1)

if [ -z "$TRANSCRIPT_FILE" ]; then
    echo "❌ Error: No transcript files found in $TRANSCRIPT_DIR" >&2
    exit 1
fi

echo "🔍 Found transcript: $TRANSCRIPT_FILE" >&2
echo "🔍 Extracting plan..." >&2

# Run extraction script with transcript path
uv run "$(dirname "$0")/extract-plan-from-context.py" "$TRANSCRIPT_FILE"
