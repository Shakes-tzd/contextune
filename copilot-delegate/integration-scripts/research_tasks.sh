#!/bin/bash
# research_tasks.sh - Pre-implementation research for all tasks
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
RESEARCH_DIR=${2:-research}

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Pre-Implementation Research (Copilot)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Validate inputs
if [ ! -f "$PLAN_FILE" ]; then
  echo -e "${RED}Error: Plan file not found: $PLAN_FILE${NC}"
  exit 1
fi

# Create research directory
mkdir -p "$RESEARCH_DIR"

# Check if yq is available
if ! command -v yq &> /dev/null; then
  echo -e "${YELLOW}Warning: yq not found, using grep fallback (limited)${NC}"
  USE_YQ=false
else
  USE_YQ=true
fi

echo -e "${BLUE}Parsing plan file:${NC} $PLAN_FILE"
echo ""

# Extract tasks
if [ "$USE_YQ" = true ]; then
  TASK_COUNT=$(yq '.tasks | length' "$PLAN_FILE")
  echo -e "Found ${GREEN}$TASK_COUNT${NC} tasks to research"
  echo ""

  # Process each task
  TASK_INDEX=0
  while [ $TASK_INDEX -lt $TASK_COUNT ]; do
    TASK_ID=$(yq ".tasks[$TASK_INDEX].id" "$PLAN_FILE")
    TASK_TITLE=$(yq ".tasks[$TASK_INDEX].title" "$PLAN_FILE")
    TASK_DESC=$(yq ".tasks[$TASK_INDEX].description" "$PLAN_FILE")

    # Extract technologies/libraries mentioned
    TECH_KEYWORDS=$(echo "$TASK_TITLE $TASK_DESC" | grep -oiE '(react|vue|angular|typescript|python|node|express|fastapi|django|auth|database|api|graphql|rest|websocket)' | sort -u | tr '\n' ',' || echo "general")

    echo -e "${BLUE}Task $((TASK_INDEX+1))/$TASK_COUNT:${NC} $TASK_ID - $TASK_TITLE"
    echo -e "  Technologies: ${YELLOW}$TECH_KEYWORDS${NC}"

    # Build research prompt
    RESEARCH_PROMPT="Research best practices and current approaches for implementing this task:

Task: $TASK_TITLE
Description: $TASK_DESC
Technologies: $TECH_KEYWORDS

Provide comprehensive research including:
1. **Current Best Practices (2025)** - What are the recommended approaches?
2. **Recommended Libraries** - Which libraries/packages should be used? Include versions.
3. **Common Patterns** - What design patterns apply?
4. **Pitfalls to Avoid** - What common mistakes should be avoided?
5. **Code Examples** - Brief examples of key patterns
6. **Testing Approach** - How should this be tested?

Return as structured JSON:
{
  \"task_id\": \"$TASK_ID\",
  \"best_practices\": [\"practice 1\", \"practice 2\", ...],
  \"recommended_libraries\": [
    {\"name\": \"lib-name\", \"version\": \"1.2.3\", \"purpose\": \"...\"}
  ],
  \"patterns\": [\"pattern 1\", \"pattern 2\", ...],
  \"pitfalls\": [\"pitfall 1\", \"pitfall 2\", ...],
  \"examples\": [
    {\"concept\": \"...\", \"code\": \"...\"}
  ],
  \"testing_approach\": \"...\"
}"

    # Create temp task file
    TEMP_TASK=$(mktemp)
    cat > "$TEMP_TASK" <<EOF
{
  \"prompt\": $(echo "$RESEARCH_PROMPT" | jq -Rs .)
}
EOF

    # Delegate to Copilot
    RESEARCH_OUTPUT="$RESEARCH_DIR/$TASK_ID.json"
    "$COPILOT_DELEGATE_DIR/scripts/delegate_copilot.sh" \
      --task-file "$TEMP_TASK" \
      --output "$RESEARCH_OUTPUT" > /dev/null 2>&1

    # Clean up
    rm -f "$TEMP_TASK"

    if [ -f "$RESEARCH_OUTPUT" ]; then
      echo -e "  ${GREEN}✅ Research completed${NC}"
    else
      echo -e "  ${RED}✗ Research failed${NC}"
    fi

    echo ""
    TASK_INDEX=$((TASK_INDEX+1))
  done
else
  # Fallback without yq
  echo -e "${YELLOW}Limited research support without yq${NC}"
  echo -e "${YELLOW}Install yq for full research capabilities:${NC}"
  echo -e "  brew install yq"
  echo ""
fi

# Create research summary
SUMMARY_FILE="$RESEARCH_DIR/summary.md"

echo -e "${BLUE}Creating research summary...${NC}"

cat > "$SUMMARY_FILE" <<EOF
# Pre-Implementation Research Summary

Generated: $(date +"%Y-%m-%d %H:%M:%S")
Plan: $PLAN_FILE

## Tasks Researched

EOF

# Add each task's summary
for research_file in "$RESEARCH_DIR"/*.json; do
  if [ "$research_file" != "$RESEARCH_DIR/summary.md" ] && [ -f "$research_file" ]; then
    TASK_ID=$(basename "$research_file" .json)

    echo "### $TASK_ID" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    # Extract key points
    if command -v jq &> /dev/null; then
      echo "**Best Practices:**" >> "$SUMMARY_FILE"
      jq -r '.best_practices[]? | "- \(.)"' "$research_file" >> "$SUMMARY_FILE" 2>/dev/null || echo "- (See full research file)" >> "$SUMMARY_FILE"
      echo "" >> "$SUMMARY_FILE"

      echo "**Recommended Libraries:**" >> "$SUMMARY_FILE"
      jq -r '.recommended_libraries[]? | "- \(.name) (\(.version)) - \(.purpose)"' "$research_file" >> "$SUMMARY_FILE" 2>/dev/null || echo "- (See full research file)" >> "$SUMMARY_FILE"
      echo "" >> "$SUMMARY_FILE"

      echo "**Key Pitfalls:**" >> "$SUMMARY_FILE"
      jq -r '.pitfalls[]? | "- \(.)"' "$research_file" >> "$SUMMARY_FILE" 2>/dev/null || echo "- (See full research file)" >> "$SUMMARY_FILE"
      echo "" >> "$SUMMARY_FILE"
    else
      echo "*(Install jq for detailed summary)*" >> "$SUMMARY_FILE"
      echo "" >> "$SUMMARY_FILE"
    fi

    echo "Full research: \`$research_file\`" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
  fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Research Phase Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Research files:${NC}"
ls -1 "$RESEARCH_DIR"/*.json 2>/dev/null | while read file; do
  echo -e "  📄 $(basename "$file")"
done

echo ""
echo -e "${BLUE}Summary:${NC} $SUMMARY_FILE"
echo ""

echo -e "${GREEN}✓ Ready to implement with research-backed approach!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Review research summary: ${YELLOW}cat $SUMMARY_FILE${NC}"
echo -e "  2. Share research files with Haiku agents"
echo -e "  3. Agents will implement using current best practices"
echo ""
