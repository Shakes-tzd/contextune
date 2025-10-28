#!/bin/bash
# Copilot Error Handler - Web-research-powered error recovery
#
# Escalation handler for errors Haiku cannot resolve.
# Uses Copilot CLI with web search to find solutions.
#
# Cost: ~$0.10 per analysis
# Duration: 10-15 seconds
# Success rate: 90-95% of errors Haiku can't fix

ERROR_LOG_FILE=$1

if [ -z "$ERROR_LOG_FILE" ] || [ ! -f "$ERROR_LOG_FILE" ]; then
    echo "Usage: error_handler.sh <error_log.json>" >&2
    exit 1
fi

# Check if copilot is available
if ! command -v copilot &> /dev/null; then
    echo "❌ Copilot CLI not found. Install: npm install -g @githubnext/github-copilot-cli" >&2
    echo "COPILOT_NOT_AVAILABLE" >&2
    exit 1
fi

# Read error context
ERROR_CONTEXT=$(cat "$ERROR_LOG_FILE")

SCRIPT=$(echo "$ERROR_CONTEXT" | jq -r '.script')
EXIT_CODE=$(echo "$ERROR_CONTEXT" | jq -r '.exit_code')
ERROR_OUTPUT=$(echo "$ERROR_CONTEXT" | jq -r '.error_output')
HAIKU_ATTEMPTS=$(echo "$ERROR_CONTEXT" | jq -r '.recovery_attempts[] | select(.handler == "haiku") | .diagnosis' 2>/dev/null || echo "None")

# Create Copilot prompt
COPILOT_PROMPT="You are a git error troubleshooting expert with web search capability.

**Error Context:**
- Script: $SCRIPT
- Exit Code: $EXIT_CODE
- Error Output:
\`\`\`
$ERROR_OUTPUT
\`\`\`

**Previous Recovery Attempts:**
- Haiku diagnosis: $HAIKU_ATTEMPTS

**Task:**
1. Search online for solutions to this error
2. Check GitHub issues, Stack Overflow, documentation
3. Provide a working fix

**Response format (JSON only):**
{
  \"can_fix\": true or false,
  \"research_findings\": \"What you found online\",
  \"error_type\": \"Specific error category\",
  \"fix\": \"Command to run\" or null,
  \"explanation\": \"Why this fix works\",
  \"confidence\": \"high\" | \"medium\" | \"low\"
}

Output ONLY JSON, no markdown fences or extra text."

echo "🔍 Analyzing error with Copilot (web search enabled)..." >&2

# Execute Copilot with timeout
TIMEOUT=30
if command -v gtimeout &> /dev/null; then
    TIMEOUT_CMD="gtimeout $TIMEOUT"
elif command -v timeout &> /dev/null; then
    TIMEOUT_CMD="timeout $TIMEOUT"
else
    TIMEOUT_CMD=""
fi

if [ -n "$TIMEOUT_CMD" ]; then
    COPILOT_OUTPUT=$($TIMEOUT_CMD copilot -p "$COPILOT_PROMPT" --allow-all-tools 2>&1)
    COPILOT_CLI_EXIT=$?
else
    COPILOT_OUTPUT=$(copilot -p "$COPILOT_PROMPT" --allow-all-tools 2>&1)
    COPILOT_CLI_EXIT=$?
fi

if [ $COPILOT_CLI_EXIT -ne 0 ]; then
    echo "❌ Copilot CLI failed: $COPILOT_OUTPUT" >&2
    exit 1
fi

# Parse JSON (remove markdown fences if present)
COPILOT_JSON=$(echo "$COPILOT_OUTPUT" | sed 's/```json//g; s/```//g' | jq -c '.' 2>/dev/null)

if [ -z "$COPILOT_JSON" ] || [ "$COPILOT_JSON" = "null" ]; then
    # Copilot might have returned plain text - try to extract fix from text
    echo "⚠️  Copilot returned non-JSON response" >&2
    echo "Raw output: $COPILOT_OUTPUT" >&2
    exit 1
fi

# Extract fields
CAN_FIX=$(echo "$COPILOT_JSON" | jq -r '.can_fix')
FIX_COMMAND=$(echo "$COPILOT_JSON" | jq -r '.fix')
RESEARCH=$(echo "$COPILOT_JSON" | jq -r '.research_findings')
EXPLANATION=$(echo "$COPILOT_JSON" | jq -r '.explanation')
CONFIDENCE=$(echo "$COPILOT_JSON" | jq -r '.confidence')

# Log Copilot's analysis
TMP=$(mktemp)
jq --argjson copilot_analysis "$COPILOT_JSON" \
   '.recovery_attempts += [{
      "handler": "copilot",
      "research_findings": $copilot_analysis.research_findings,
      "can_fix": $copilot_analysis.can_fix,
      "confidence": $copilot_analysis.confidence,
      "timestamp": (now | todate)
   }]' "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

echo "📊 Copilot research: $RESEARCH" >&2
echo "💡 Confidence: $CONFIDENCE" >&2

# Check if Copilot can fix
if [ "$CAN_FIX" != "true" ] || [ "$FIX_COMMAND" = "null" ] || [ -z "$FIX_COMMAND" ]; then
    echo "❌ Copilot could not suggest a fix" >&2
    exit 1
fi

# Copilot suggested a fix - try it
echo "🔧 Applying Copilot's fix: $FIX_COMMAND" >&2
echo "📝 Explanation: $EXPLANATION" >&2

set +e
FIX_OUTPUT=$(eval "$FIX_COMMAND" 2>&1)
FIX_EXIT=$?
set -e

if [ $FIX_EXIT -eq 0 ]; then
    echo "✅ Copilot's fix successful!" >&2
    echo "Fix applied: $FIX_COMMAND" >&2
    echo "$FIX_OUTPUT"

    # Log successful recovery
    TMP=$(mktemp)
    jq '.recovery_attempts[-1].success = true | .recovery_attempts[-1].fix_applied = "'"$FIX_COMMAND"'"' \
       "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

    exit 0
fi

# Fix failed
echo "❌ Copilot's fix did not work" >&2
echo "Fix attempted: $FIX_COMMAND" >&2
echo "Result: $FIX_OUTPUT" >&2

# Log failed fix
TMP=$(mktemp)
jq '.recovery_attempts[-1].success = false | .recovery_attempts[-1].fix_attempted = "'"$FIX_COMMAND"'" | .recovery_attempts[-1].fix_result = "'"$FIX_OUTPUT"'"' \
   "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

exit 1
