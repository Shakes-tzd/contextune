#!/usr/bin/env bash
# Create Pull Requests for completed tasks
# Uses task files as PR descriptions (zero transformation)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(cd "$PLAN_DIR/../../.." && pwd)"

TASKS_DIR="$PLAN_DIR/tasks"
BASE_BRANCH="${BASE_BRANCH:-main}"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Creating Pull Requests for completed tasks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
  echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
  echo "Install it: https://cli.github.com/"
  exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
  echo -e "${RED}Error: Not authenticated with GitHub${NC}"
  echo "Run: gh auth login"
  exit 1
fi

# Find all completed tasks
COMPLETED_TASKS=()
for task_file in "$TASKS_DIR"/task-*.md; do
  if [ -f "$task_file" ]; then
    # Check status in YAML frontmatter
    status=$(grep "^status:" "$task_file" | head -1 | sed 's/status:\s*//')
    
    if [ "$status" = "completed" ]; then
      task_id=$(basename "$task_file" .md)
      COMPLETED_TASKS+=("$task_id")
    fi
  fi
done

# Count completed tasks
COMPLETED_COUNT=${#COMPLETED_TASKS[@]}

if [ $COMPLETED_COUNT -eq 0 ]; then
  echo -e "${YELLOW}No completed tasks found${NC}"
  echo "Tasks must have 'status: completed' in their YAML frontmatter"
  exit 0
fi

echo -e "Found ${GREEN}$COMPLETED_COUNT${NC} completed tasks"
echo ""

# Function to create PR for a single task
create_pr() {
  local task_id=$1
  local task_file="$TASKS_DIR/$task_id.md"
  local branch_name="feature/$task_id"
  
  # Extract title (first # heading, skip YAML frontmatter)
  local title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
  
  # Extract labels from YAML frontmatter
  local labels=$(awk '/^labels:/,/^[a-z]/ {if ($0 ~ /^\s*-/) print $2}' "$task_file" | tr '\n' ',' | sed 's/,$//')
  
  echo -e "${BLUE}Creating PR for: $title${NC}"
  
  # Check if PR already exists
  existing_pr=$(gh pr list --head "$branch_name" --json number --jq '.[0].number' 2>/dev/null || echo "")
  
  if [ -n "$existing_pr" ]; then
    echo -e "${YELLOW}⚠️  PR already exists: #$existing_pr${NC}"
    echo ""
    return 0
  fi
  
  # Check if branch exists and has commits
  if ! git -C "$PROJECT_ROOT" show-ref --verify --quiet refs/heads/$branch_name; then
    echo -e "${RED}❌ Branch not found: $branch_name${NC}"
    echo ""
    return 1
  fi
  
  # Check if branch has commits ahead of base
  commits_ahead=$(git -C "$PROJECT_ROOT" rev-list --count $BASE_BRANCH..$branch_name 2>/dev/null || echo "0")
  
  if [ "$commits_ahead" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No commits in branch: $branch_name${NC}"
    echo ""
    return 0
  fi
  
  # Create PR with task file as body
  if [ -n "$labels" ]; then
    pr_url=$(gh pr create \
      --repo "$(git -C "$PROJECT_ROOT" remote get-url origin | sed 's/.*://;s/.git$//')" \
      --base "$BASE_BRANCH" \
      --head "$branch_name" \
      --title "$title" \
      --body-file "$task_file" \
      --label "$labels" 2>&1)
  else
    pr_url=$(gh pr create \
      --repo "$(git -C "$PROJECT_ROOT" remote get-url origin | sed 's/.*://;s/.git$//')" \
      --base "$BASE_BRANCH" \
      --head "$branch_name" \
      --title "$title" \
      --body-file "$task_file" 2>&1)
  fi
  
  if [[ "$pr_url" == *"http"* ]]; then
    pr_number=$(echo "$pr_url" | grep -oE '[0-9]+$')
    echo -e "${GREEN}✅ Created PR #$pr_number: $title${NC}"
    echo -e "   ${BLUE}$pr_url${NC}"
  else
    echo -e "${RED}❌ Failed to create PR: $pr_url${NC}"
  fi
  
  echo ""
}

# Create PRs sequentially (to avoid rate limits)
echo -e "${BLUE}Creating PRs...${NC}"
echo ""

for task_id in "${COMPLETED_TASKS[@]}"; do
  create_pr "$task_id"
done

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ PR creation complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Summary
echo -e "${BLUE}Summary:${NC}"
echo -e "  Completed tasks: ${GREEN}$COMPLETED_COUNT${NC}"
gh pr list --head "feature/task-*" --json number | jq '. | length' | xargs -I {} echo -e "  PRs created: ${GREEN}{}${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Review PRs: gh pr list"
echo -e "  2. Merge PRs: gh pr merge <number>"
echo -e "  3. Cleanup: ./scripts/cleanup_worktrees.sh"
