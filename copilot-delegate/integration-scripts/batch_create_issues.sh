#!/bin/bash
# batch_create_issues.sh - Create GitHub issues for all tasks in plan.yaml
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
PLAN_FILE=${1:-plan.yaml}
OUTPUT_FILE=${2:-issue-mapping.json}

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Batch GitHub Issue Creation (Copilot)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Validate inputs
if [ ! -f "$PLAN_FILE" ]; then
  echo -e "${RED}Error: Plan file not found: $PLAN_FILE${NC}"
  exit 1
fi

# Check if yq is available for parsing YAML
if ! command -v yq &> /dev/null; then
  echo -e "${YELLOW}Warning: yq not found, using grep fallback${NC}"
  USE_YQ=false
else
  USE_YQ=true
fi

echo -e "${BLUE}Parsing plan file:${NC} $PLAN_FILE"
echo ""

# Extract tasks from plan.yaml
if [ "$USE_YQ" = true ]; then
  TASK_COUNT=$(yq '.tasks | length' "$PLAN_FILE")
  echo -e "Found ${GREEN}$TASK_COUNT${NC} tasks"
  echo ""

  # Build tasks array
  TASKS_JSON=$(yq -o=json '.tasks[]' "$PLAN_FILE" | jq -s '.')
else
  # Fallback: parse with grep (basic support)
  echo -e "${YELLOW}Using grep fallback (limited support)${NC}"
  TASK_COUNT=$(grep -c "^\s*-\s*id:" "$PLAN_FILE" || echo "0")
  echo -e "Found ${GREEN}$TASK_COUNT${NC} tasks"
  echo ""

  # Can't build full JSON without yq, just extract IDs
  TASK_IDS=$(grep "^\s*id:" "$PLAN_FILE" | sed 's/.*id:\s*"\?\([^"]*\)"\?.*/\1/')
fi

# Build Copilot prompt for batch issue creation
if [ "$USE_YQ" = true ]; then
  # Build rich prompt with full task details
  PROMPT="Create GitHub issues for the following parallel execution tasks:

$(echo "$TASKS_JSON" | jq -r '.[] | "
Task ID: \(.id)
Title: \(.title)
Description: \(.description)
Labels: parallel-execution,task-\(.id)
Files: \(.files | join(\", \"))
---"')

Use the gh CLI to create all issues. For each issue, run:

\`\`\`bash
gh issue create --title \"<title>\" --body \"<body>\" --label \"<labels>\"
\`\`\`

Return results as JSON array:
\`\`\`json
[
  {
    \"task_id\": \"task-1\",
    \"issue_number\": 101,
    \"issue_url\": \"https://github.com/owner/repo/issues/101\",
    \"title\": \"Task title\",
    \"status\": \"created\"
  },
  ...
]
\`\`\`

Create all issues now and return the JSON array."
else
  # Fallback: simpler prompt with just IDs
  PROMPT="Create GitHub issues for the following task IDs: $TASK_IDS

For each task ID, create a GitHub issue with:
- Title: \"Implement task <id>\"
- Body: \"Parallel execution task. See plan.yaml for details.\"
- Labels: parallel-execution,task-<id>

Use the gh CLI and return results as JSON array with task_id, issue_number, and issue_url for each."
fi

# Save prompt to temporary file
TEMP_TASK=$(mktemp)
cat > "$TEMP_TASK" <<EOF
{
  "prompt": $(echo "$PROMPT" | jq -Rs .)
}
EOF

echo -e "${BLUE}Delegating to Copilot CLI...${NC}"
echo ""

# Delegate to Copilot
"$COPILOT_DELEGATE_DIR/scripts/delegate_copilot.sh" --task-file "$TEMP_TASK" --output "$OUTPUT_FILE"

# Clean up
rm -f "$TEMP_TASK"

# Validate output
if [ ! -f "$OUTPUT_FILE" ]; then
  echo -e "${RED}Error: Output file not created${NC}"
  exit 1
fi

# Parse and validate results
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Batch Issue Creation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Display results
echo -e "${BLUE}Issues Created:${NC}"
jq -r '.[] | "  ✅ Task \(.task_id): Issue #\(.issue_number) - \(.issue_url)"' "$OUTPUT_FILE"

echo ""
echo -e "${BLUE}Issue Mapping saved to:${NC} $OUTPUT_FILE"
echo ""

# Create environment export script
ENV_EXPORT_FILE="${OUTPUT_FILE%.json}.env"
echo -e "${BLUE}Creating environment export:${NC} $ENV_EXPORT_FILE"

cat > "$ENV_EXPORT_FILE" <<'EOF'
# Auto-generated issue number mapping
# Source this file before spawning Haiku agents
EOF

jq -r '.[] | "export ISSUE_NUM_\(.task_id | gsub("-"; "_"))=\(.issue_number)"' "$OUTPUT_FILE" >> "$ENV_EXPORT_FILE"

echo ""
echo -e "${GREEN}✓ Ready for parallel execution!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Source the environment file: ${YELLOW}source $ENV_EXPORT_FILE${NC}"
echo -e "  2. Setup worktrees: ${YELLOW}./setup_worktrees.sh${NC}"
echo -e "  3. Spawn Haiku agents with pre-created issue numbers"
echo ""
