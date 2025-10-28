#!/bin/bash
# Haiku Error Handler - Fast, cheap error recovery
#
# Uses Claude Haiku in headless mode to analyze script errors.
# Cost: ~$0.001 per analysis
# Duration: 2-5 seconds
# Success rate: 70-80% of git errors

ERROR_LOG_FILE=$1

if [ -z "$ERROR_LOG_FILE" ] || [ ! -f "$ERROR_LOG_FILE" ]; then
    echo "Usage: haiku_error_handler.sh <error_log.json>" >&2
    exit 1
fi

# Read error context
ERROR_CONTEXT=$(cat "$ERROR_LOG_FILE")

# Extract key fields for prompt
SCRIPT=$(echo "$ERROR_CONTEXT" | jq -r '.script')
EXIT_CODE=$(echo "$ERROR_CONTEXT" | jq -r '.exit_code')
ERROR_OUTPUT=$(echo "$ERROR_CONTEXT" | jq -r '.error_output')

# Create Haiku prompt
HAIKU_PROMPT="You are a git error troubleshooter. Analyze this error and provide a fix.

**Script:** $SCRIPT
**Exit Code:** $EXIT_CODE
**Error Output:**
\`\`\`
$ERROR_OUTPUT
\`\`\`

**Task:** Diagnose the issue and suggest a fix.

**Response format (JSON only, no markdown):**
{
  \"can_fix\": true or false,
  \"error_type\": \"auth\" | \"network\" | \"conflict\" | \"diverged\" | \"permission\" | \"syntax\" | \"other\",
  \"diagnosis\": \"Brief explanation of what went wrong\",
  \"fix\": \"Command to run to fix\" or null,
  \"escalate\": true or false
}

**Guidelines:**
- If you can suggest a command to fix the issue, set can_fix=true and provide the fix command
- If the error requires web research or is too complex, set escalate=true
- Common git errors you CAN fix: diverged branches, auth issues, merge conflicts, permissions
- Output ONLY the JSON, no other text"

# Execute Haiku headless
echo "🤖 Analyzing error with Claude Haiku..." >&2

HAIKU_OUTPUT=$(claude --model haiku -p "$HAIKU_PROMPT" 2>&1)
HAIKU_CLI_EXIT=$?

if [ $HAIKU_CLI_EXIT -ne 0 ]; then
    echo "❌ Haiku CLI failed: $HAIKU_OUTPUT" >&2
    echo "HAIKU_CLI_ERROR" >&2
    exit 1
fi

# Parse JSON (remove markdown fences if present)
HAIKU_JSON=$(echo "$HAIKU_OUTPUT" | sed 's/```json//g; s/```//g' | jq -c '.')

if [ -z "$HAIKU_JSON" ] || [ "$HAIKU_JSON" = "null" ]; then
    echo "❌ Failed to parse Haiku response" >&2
    echo "Raw output: $HAIKU_OUTPUT" >&2
    exit 1
fi

# Extract fields
CAN_FIX=$(echo "$HAIKU_JSON" | jq -r '.can_fix')
ESCALATE=$(echo "$HAIKU_JSON" | jq -r '.escalate')
FIX_COMMAND=$(echo "$HAIKU_JSON" | jq -r '.fix')
DIAGNOSIS=$(echo "$HAIKU_JSON" | jq -r '.diagnosis')
ERROR_TYPE=$(echo "$HAIKU_JSON" | jq -r '.error_type')

# Log Haiku's analysis
TMP=$(mktemp)
jq --arg diagnosis "$DIAGNOSIS" \
   --arg error_type "$ERROR_TYPE" \
   --arg can_fix "$CAN_FIX" \
   '.recovery_attempts += [{
      "handler": "haiku",
      "diagnosis": $diagnosis,
      "error_type": $error_type,
      "can_fix": ($can_fix == "true"),
      "timestamp": now | todate
   }]' "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

echo "📊 Haiku diagnosis: $DIAGNOSIS ($ERROR_TYPE)" >&2

# Check if Haiku wants to escalate
if [ "$ESCALATE" = "true" ]; then
    echo "⬆️  Haiku suggests escalation (needs web research)" >&2
    exit 1
fi

# Check if Haiku can fix
if [ "$CAN_FIX" != "true" ] || [ "$FIX_COMMAND" = "null" ] || [ -z "$FIX_COMMAND" ]; then
    echo "❌ Haiku could not suggest a fix" >&2
    exit 1
fi

# Haiku suggested a fix - try it
echo "🔧 Applying Haiku's fix: $FIX_COMMAND" >&2

set +e
FIX_OUTPUT=$(eval "$FIX_COMMAND" 2>&1)
FIX_EXIT=$?
set -e

if [ $FIX_EXIT -eq 0 ]; then
    echo "✅ Haiku's fix successful!" >&2
    echo "Fix applied: $FIX_COMMAND" >&2
    echo "$FIX_OUTPUT"

    # Log successful recovery
    TMP=$(mktemp)
    jq '.recovery_attempts[-1].success = true | .recovery_attempts[-1].fix_applied = "'"$FIX_COMMAND"'"' \
       "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

    exit 0
fi

# Fix failed
echo "❌ Haiku's fix failed" >&2
echo "Fix attempted: $FIX_COMMAND" >&2
echo "Result: $FIX_OUTPUT" >&2

# Log failed fix
TMP=$(mktemp)
jq '.recovery_attempts[-1].success = false | .recovery_attempts[-1].fix_attempted = "'"$FIX_COMMAND"'" | .recovery_attempts[-1].fix_result = "'"$FIX_OUTPUT"'"' \
   "$ERROR_LOG_FILE" > "$TMP" && mv "$TMP" "$ERROR_LOG_FILE"

exit 1
