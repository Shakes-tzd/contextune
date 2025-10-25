#!/usr/bin/env bash
# Setup worktrees for parallel task execution
# Creates worktrees and branches for all tasks in plan.yaml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(cd "$PLAN_DIR/../../.." && pwd)"

PLAN_FILE="$PLAN_DIR/plan.yaml"
WORKTREE_BASE="$PROJECT_ROOT/worktrees"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Setting up worktrees for parallel execution${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if plan.yaml exists
if [ ! -f "$PLAN_FILE" ]; then
  echo -e "${RED}Error: plan.yaml not found at $PLAN_FILE${NC}"
  exit 1
fi

# Check if yq is available
if ! command -v yq &> /dev/null; then
  echo -e "${YELLOW}Warning: yq not found, using grep fallback${NC}"
  USE_YQ=false
else
  USE_YQ=true
fi

# Extract task IDs from plan.yaml
if [ "$USE_YQ" = true ]; then
  TASK_IDS=$(yq '.tasks[].id' "$PLAN_FILE")
else
  # Fallback: grep for "id:" in tasks section
  TASK_IDS=$(grep -A 100 "^tasks:" "$PLAN_FILE" | grep "^\s*id:" | sed 's/.*id:\s*"\?\([^"]*\)"\?.*/\1/')
fi

# Count tasks
TASK_COUNT=$(echo "$TASK_IDS" | wc -l | tr -d ' ')
echo -e "Found ${GREEN}$TASK_COUNT${NC} tasks in plan"
echo ""

# Create worktrees directory if it doesn't exist
mkdir -p "$WORKTREE_BASE"

# Function to setup a single worktree
setup_worktree() {
  local task_id=$1
  local branch_name="feature/$task_id"
  local worktree_path="$WORKTREE_BASE/$task_id"
  
  # Check if worktree already exists
  if [ -d "$worktree_path" ]; then
    echo -e "${YELLOW}⚠️  Worktree already exists: $task_id${NC}"
    return 0
  fi
  
  # Check if branch already exists
  if git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/$branch_name; then
    echo -e "${YELLOW}⚠️  Branch already exists: $branch_name (using existing)${NC}"
    git -C "$PROJECT_ROOT" worktree add "$worktree_path" "$branch_name" 2>/dev/null || true
  else
    # Create new worktree and branch
    git -C "$PROJECT_ROOT" worktree add "$worktree_path" -b "$branch_name" 2>&1 | grep -v "Preparing worktree" || true
  fi
  
  if [ -d "$worktree_path" ]; then
    echo -e "${GREEN}✅ Created worktree: $task_id${NC}"
  else
    echo -e "${RED}❌ Failed to create worktree: $task_id${NC}"
  fi
}

# Export function for parallel execution
export -f setup_worktree
export WORKTREE_BASE PROJECT_ROOT GREEN YELLOW RED NC

# Setup worktrees in parallel
echo -e "${BLUE}Creating worktrees in parallel...${NC}"
echo ""

# Use xargs for parallel execution (macOS compatible)
echo "$TASK_IDS" | xargs -P 10 -I {} bash -c 'setup_worktree "$@"' _ {}

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Worktree setup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Summary
echo -e "${BLUE}Summary:${NC}"
git -C "$PROJECT_ROOT" worktree list | grep "worktrees/" | wc -l | xargs -I {} echo -e "  Active worktrees: ${GREEN}{}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Spawn agents for each task"
echo -e "  2. Agents will work in their respective worktrees"
echo -e "  3. Run create_prs.sh when tasks are complete"
