#!/bin/bash
# setup_worktrees_from_plan.sh - Create worktrees from ctx-plan output
# Version 3: Works with Contextune ctx-plan format (.parallel/plans/)

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PLAN_FILE=${1:-.parallel/plans/plan.yaml}
PLAN_DIR=$(dirname "$PLAN_FILE")
WORKTREE_BASE=worktrees

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Setup Worktrees from ctx-plan${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Validate plan file
if [ ! -f "$PLAN_FILE" ]; then
  echo -e "${RED}Error: Plan file not found: $PLAN_FILE${NC}"
  echo -e "${YELLOW}Create plan first: /ctx:plan${NC}"
  exit 1
fi

# Create worktrees directory
mkdir -p "$WORKTREE_BASE"

# Get task count
TASK_COUNT=$(yq '.tasks | length' "$PLAN_FILE")
echo -e "Found ${GREEN}$TASK_COUNT${NC} tasks"
echo ""

# Check for uncommitted changes in main
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo -e "${YELLOW}⚠ You have uncommitted changes${NC}"
  echo -e "${YELLOW}Commit them before creating worktrees${NC}"
  exit 1
fi

# Process each task
TASK_INDEX=0
CREATED_COUNT=0

while [ $TASK_INDEX -lt $TASK_COUNT ]; do
  # Read task metadata from plan index
  TASK_ID=$(yq ".tasks[$TASK_INDEX].id" "$PLAN_FILE")
  TASK_NAME=$(yq ".tasks[$TASK_INDEX].name" "$PLAN_FILE")
  TASK_FILE_REL=$(yq ".tasks[$TASK_INDEX].file" "$PLAN_FILE")
  TASK_FILE="$PLAN_DIR/$TASK_FILE_REL"

  # Read task status from markdown file
  if [ -f "$TASK_FILE" ]; then
    TASK_STATUS=$(yq -p md '.status' "$TASK_FILE" 2>/dev/null || echo "pending")
  else
    echo -e "${RED}Error: Task file not found: $TASK_FILE${NC}"
    TASK_INDEX=$((TASK_INDEX+1))
    continue
  fi

  WORKTREE_PATH="$WORKTREE_BASE/$TASK_ID"
  BRANCH_NAME="feature/$TASK_ID"

  echo -e "${BLUE}Task $((TASK_INDEX+1))/$TASK_COUNT:${NC} $TASK_ID"
  echo -e "  Name: $TASK_NAME"
  echo -e "  File: $TASK_FILE_REL"

  # Skip if already completed
  if [ "$TASK_STATUS" == "completed" ]; then
    echo -e "  ${YELLOW}⚠ Already completed, skipping${NC}"
    echo ""
    TASK_INDEX=$((TASK_INDEX+1))
    continue
  fi

  # Check if worktree already exists
  if [ -d "$WORKTREE_PATH" ]; then
    echo -e "  ${YELLOW}⚠ Worktree already exists${NC}"

    # Verify it's registered with git
    if git worktree list | grep -q "$WORKTREE_PATH"; then
      echo -e "  ${GREEN}✓ Registered with git${NC}"
    else
      echo -e "  ${RED}✗ Directory exists but not registered${NC}"
      echo -e "  ${YELLOW}Remove manually: rm -rf $WORKTREE_PATH${NC}"
    fi

    echo ""
    TASK_INDEX=$((TASK_INDEX+1))
    continue
  fi

  # Check if branch exists
  if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo -e "  ${YELLOW}⚠ Branch $BRANCH_NAME already exists${NC}"

    # Try to add worktree with existing branch
    if git worktree add "$WORKTREE_PATH" "$BRANCH_NAME" 2>/dev/null; then
      echo -e "  ${GREEN}✓ Created worktree with existing branch${NC}"
    else
      echo -e "  ${RED}✗ Failed to create worktree${NC}"
      echo ""
      TASK_INDEX=$((TASK_INDEX+1))
      continue
    fi
  else
    # Create new worktree and branch
    if git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" 2>&1 | grep -v "Preparing worktree"; then
      echo -e "  ${GREEN}✓ Created worktree and branch${NC}"
    else
      echo -e "  ${RED}✗ Failed to create worktree${NC}"
      echo ""
      TASK_INDEX=$((TASK_INDEX+1))
      continue
    fi
  fi

  # Append worktree info to task markdown file
  echo "" >> "$TASK_FILE"
  echo "---" >> "$TASK_FILE"
  echo "" >> "$TASK_FILE"
  echo "**Worktree:** \`$WORKTREE_PATH\`" >> "$TASK_FILE"
  echo "**Branch:** \`$BRANCH_NAME\`" >> "$TASK_FILE"

  echo -e "  ${GREEN}✓ Updated $TASK_FILE_REL${NC}"

  CREATED_COUNT=$((CREATED_COUNT+1))
  echo ""
  TASK_INDEX=$((TASK_INDEX+1))
done

# Commit task file updates
if [ $CREATED_COUNT -gt 0 ]; then
  git add "$PLAN_DIR/tasks/"
  git commit -m "chore: assign worktrees to $CREATED_COUNT task(s)

Updated task files with worktree and branch assignments.

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

  echo -e "${GREEN}✓ Committed task file updates${NC}"
  echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Worktree Setup Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Summary:${NC}"
echo -e "  Created: ${GREEN}$CREATED_COUNT${NC} worktrees"
echo -e "  Total worktrees: ${GREEN}$(git worktree list | grep -c worktrees/)${NC}"
echo ""

# Show worktree list
echo -e "${BLUE}Active Worktrees:${NC}"
git worktree list | grep worktrees/ | while read path branch rest; do
  TASK_ID=$(basename "$path")
  echo -e "  📁 $path → $branch"
done

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Spawn agents: ${BLUE}/ctx:execute${NC}"
echo -e "  2. Monitor progress: ${BLUE}.parallel/plans/scripts/status.sh${NC}"
echo -e "  3. View worktrees: ${BLUE}git worktree list${NC}"
echo ""
