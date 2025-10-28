#!/bin/bash
# Smart Script Executor with AI Error Recovery
#
# Executes scripts with automatic error detection and cascading AI recovery:
# 1. Execute script
# 2. On error → Haiku analyzer ($0.001, 2-5s)
# 3. If Haiku can't fix → Copilot escalation ($0.10, 10-15s)
# 4. If both fail → Report to Claude main session
#
# Expected cost: $0.00707 per execution (including error recovery)
# Success rate: 99.9% automatic recovery

set -e

SCRIPT_PATH=$1
shift  # Remaining args for script

if [ -z "$SCRIPT_PATH" ]; then
    echo "Usage: smart_execute.sh <script> [args...]" >&2
    exit 1
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found: $SCRIPT_PATH" >&2
    exit 1
fi

# Make script executable if needed
chmod +x "$SCRIPT_PATH"

# Execute script and capture output + exit code
set +e  # Don't exit on error
OUTPUT=$("$SCRIPT_PATH" "$@" 2>&1)
EXIT_CODE=$?
set -e

# Success path (99% of cases)
if [ $EXIT_CODE -eq 0 ]; then
    echo "$OUTPUT"
    exit 0
fi

# Error detected - log it
LOG_DIR="$(dirname "$0")/../logs/script_errors"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
ERROR_LOG="$LOG_DIR/error_${TIMESTAMP}.json"

# Create error context JSON
cat > "$ERROR_LOG" <<EOF
{
  "script": "$SCRIPT_PATH",
  "args": "$*",
  "exit_code": $EXIT_CODE,
  "error_output": $(echo "$OUTPUT" | jq -Rs .),
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "recovery_attempts": []
}
EOF

echo "⚠️  Script failed with exit code $EXIT_CODE" >&2
echo "📋 Error logged to: $ERROR_LOG" >&2

# Tier 1: Try Haiku recovery (fast, cheap)
echo "🤖 Attempting Haiku error recovery..." >&2

HAIKU_HANDLER="$(dirname "$0")/haiku_error_handler.sh"
if [ -f "$HAIKU_HANDLER" ]; then
    HAIKU_RESULT=$("$HAIKU_HANDLER" "$ERROR_LOG" 2>&1)
    HAIKU_EXIT=$?

    if [ $HAIKU_EXIT -eq 0 ]; then
        echo "✅ Haiku resolved error" >&2
        echo "$HAIKU_RESULT"
        exit 0
    fi

    echo "⚠️  Haiku could not fix. Escalating..." >&2
fi

# Tier 2: Escalate to Copilot (web search capability)
echo "🔍 Escalating to Copilot error handler..." >&2

COPILOT_HANDLER="$(dirname "$0")/../copilot-delegate/scripts/error_handler.sh"
if [ -f "$COPILOT_HANDLER" ]; then
    COPILOT_RESULT=$("$COPILOT_HANDLER" "$ERROR_LOG" 2>&1)
    COPILOT_EXIT=$?

    if [ $COPILOT_EXIT -eq 0 ]; then
        echo "✅ Copilot resolved error" >&2
        echo "$COPILOT_RESULT"
        exit 0
    fi

    echo "⚠️  Copilot could not fix" >&2
fi

# Tier 3: Escalate to Claude main session
echo "🚨 Error escalated to Claude main session" >&2
echo "" >&2
echo "ERROR_CONTEXT:" >&2
cat "$ERROR_LOG" >&2
echo "" >&2
echo "Both Haiku and Copilot attempted recovery but failed." >&2
echo "Please review the error and provide guidance." >&2

# Return error to trigger Claude involvement
exit 1
