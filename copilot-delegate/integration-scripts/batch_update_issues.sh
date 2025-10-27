#!/bin/bash
# batch_update_issues.sh - Update/close GitHub issues for completed tasks
# Part of copilot-delegate integration with parallel execution

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPILOT_DELEGATE_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
WORKTREE_BASE=${1:-worktrees}
ISSUE_MAPPING=${2:-issue-mapping.json}

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Batch GitHub Issue Updates (Copilot)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Validate inputs
if [ ! -d "$WORKTREE_BASE" ]; then
  echo -e "${RED}Error: Worktree base directory not found: $WORKTREE_BASE${NC}"
  exit 1
fi

if [ ! -f "$ISSUE_MAPPING" ]; then
  echo -e "${RED}Error: Issue mapping file not found: $ISSUE_MAPPING${NC}"
  echo -e "${YELLOW}Run batch_create_issues.sh first${NC}"
  exit 1
fi

echo -e "${BLUE}Scanning worktrees for status updates...${NC}"
echo ""

# Build updates array
UPDATES_JSON="[]"

# Scan each worktree for .task-status files
for worktree in "$WORKTREE_BASE"/*; do
  if [ ! -d "$worktree" ]; then
    continue
  fi

  TASK_ID=$(basename "$worktree")
  STATUS_FILE="$worktree/.task-status"

  if [ ! -f "$STATUS_FILE" ]; then
    echo -e "${YELLOW}⚠ No status file for $TASK_ID (still in progress?)${NC}"
    continue
  fi

  echo -e "${BLUE}Processing:${NC} $TASK_ID"

  # Read status file
  source "$STATUS_FILE"

  # Get issue number from mapping
  ISSUE_NUM=$(jq -r ".[] | select(.task_id == \"$TASK_ID\") | .issue_number" "$ISSUE_MAPPING")

  if [ -z "$ISSUE_NUM" ] || [ "$ISSUE_NUM" == "null" ]; then
    echo -e "  ${RED}✗ Issue number not found in mapping${NC}"
    continue
  fi

  # Build update based on status
  if [ "$status" == "completed" ]; then
    # Completed task - close issue
    UPDATE_BODY="✅ **Task Completed Successfully**

**Summary:** $summary

**Files Changed:**
${files_changed/,/
}

**Test Results:** $([ "$tests_passing" == "yes" ] && echo "✅ All tests passing" || echo "⚠️ Tests need attention")

**Commits:** $commits commit(s)

Ready for review and merge!

🤖 Completed by Haiku Agent (parallel-task-executor)
**Cost**: ~\$0.04 (85% cheaper than Sonnet!)"

    UPDATE_JSON=$(jq -n \
      --arg issue "$ISSUE_NUM" \
      --arg body "$UPDATE_BODY" \
      '{
        issue: ($issue | tonumber),
        action: "close",
        comment: $body
      }')

    echo -e "  ${GREEN}✓ Will close issue #$ISSUE_NUM${NC}"

  elif [ "$status" == "blocked" ]; then
    # Blocked task - add warning comment
    UPDATE_BODY="⚠️ **Task Blocked**

**Issue:** $summary

**Details:**
$(cat "$worktree/.task-error" 2>/dev/null || echo "See worktree for details")

**Need:** Human intervention required

🤖 Reported by Haiku Agent"

    UPDATE_JSON=$(jq -n \
      --arg issue "$ISSUE_NUM" \
      --arg body "$UPDATE_BODY" \
      '{
        issue: ($issue | tonumber),
        action: "comment",
        body: $body
      }')

    echo -e "  ${YELLOW}⚠ Will comment on issue #$ISSUE_NUM (blocked)${NC}"

  elif [ "$status" == "in_progress" ]; then
    # In progress - update with progress
    UPDATE_BODY="🔄 **Task In Progress**

**Current Stage:** $summary

**Files Modified:** ${files_changed:-None yet}

**Commits:** ${commits:-0} so far

🤖 Progress update from Haiku Agent"

    UPDATE_JSON=$(jq -n \
      --arg issue "$ISSUE_NUM" \
      --arg body "$UPDATE_BODY" \
      '{
        issue: ($issue | tonumber),
        action: "comment",
        body: $body
      }')

    echo -e "  ${BLUE}ℹ Will update issue #$ISSUE_NUM (in progress)${NC}"

  else
    echo -e "  ${YELLOW}⚠ Unknown status: $status${NC}"
    continue
  fi

  # Add to updates array
  UPDATES_JSON=$(echo "$UPDATES_JSON" | jq ". += [$UPDATE_JSON]")
  echo ""
done

# Check if we have any updates
UPDATE_COUNT=$(echo "$UPDATES_JSON" | jq 'length')

if [ "$UPDATE_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}No updates to process${NC}"
  exit 0
fi

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}Found $UPDATE_COUNT issue update(s)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Build Copilot prompt for batch updates
COPILOT_PROMPT="Update GitHub issues with the following changes:

$(echo "$UPDATES_JSON" | jq -r '.[] | "
Issue #\(.issue): \(.action)
\(.comment // .body)
---"')

For each update, use the gh CLI:

For comments:
\`\`\`bash
gh issue comment <issue-number> --body \"<body>\"
\`\`\`

For closing:
\`\`\`bash
gh issue close <issue-number> --comment \"<comment>\"
\`\`\`

Execute all updates and return a JSON array:
\`\`\`json
[
  {
    \"issue\": 101,
    \"action\": \"closed\" or \"commented\",
    \"status\": \"success\" or \"error\",
    \"message\": \"Optional error message if failed\"
  },
  ...
]
\`\`\`"

# Create temp task file
TEMP_TASK=$(mktemp)
cat > "$TEMP_TASK" <<EOF
{
  "prompt": $(echo "$COPILOT_PROMPT" | jq -Rs .)
}
EOF

echo -e "${BLUE}Delegating to Copilot CLI...${NC}"
echo ""

# Delegate to Copilot
OUTPUT_FILE="batch-update-results.json"
"$COPILOT_DELEGATE_DIR/scripts/delegate_copilot.sh" \
  --task-file "$TEMP_TASK" \
  --output "$OUTPUT_FILE"

# Clean up
rm -f "$TEMP_TASK"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Batch Issue Update Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Display results
if [ -f "$OUTPUT_FILE" ] && command -v jq &> /dev/null; then
  echo -e "${BLUE}Results:${NC}"
  jq -r '.[] | if .status == "success" then "  ✅ Issue #\(.issue): \(.action)" else "  ✗ Issue #\(.issue): \(.message)" end' "$OUTPUT_FILE" 2>/dev/null || echo "  (See $OUTPUT_FILE for details)"
  echo ""
fi

echo -e "${GREEN}✓ Issue updates synchronized!${NC}"
echo ""
