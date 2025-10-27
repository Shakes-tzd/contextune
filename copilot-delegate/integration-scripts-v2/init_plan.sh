#!/bin/bash
# init_plan.sh - Initialize .parallel/plan.yaml for parallel execution
# Version 2: plan.yaml as source of truth (no GitHub issues required)

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT=${1:-.}
PLAN_DIR="$PROJECT_ROOT/.parallel"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Initialize Parallel Execution Plan${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Create .parallel directory
mkdir -p "$PLAN_DIR"/{status,research,scripts}

# Detect project details
PROJECT_NAME=$(basename "$(cd "$PROJECT_ROOT" && pwd)")
CURRENT_DATE=$(date +"%Y-%m-%d")

echo -e "${BLUE}Creating plan.yaml template...${NC}"

# Create plan.yaml template
cat > "$PLAN_DIR/plan.yaml" <<EOF
# Parallel Execution Plan
# Generated: $CURRENT_DATE
# Edit this file to define your parallel tasks

project:
  name: "$PROJECT_NAME"
  description: "Add project description here"
  created: "$CURRENT_DATE"

parallel_config:
  max_concurrent: 4                # Max parallel agents
  auto_research: true              # Use Copilot for pre-implementation research
  github_integration: false        # Create GitHub issues? (optional)
  status_tracking: "inline"        # "inline" (in plan.yaml) or "files" (.parallel/status/)

tasks:
  # Example task 1
  - id: "task-1"
    title: "Implement feature X"
    description: |
      Detailed description of what needs to be implemented.
      Be specific about requirements and expected behavior.

    priority: "high"               # high, medium, low
    complexity: 7                  # 1-10 scale
    estimated_hours: 8

    files:                         # Files to create/modify
      - "src/feature-x.ts"
      - "tests/feature-x.test.ts"

    dependencies: []               # Task IDs this depends on (e.g., ["task-2"])

    implementation_steps:
      - "Step 1: Setup structure"
      - "Step 2: Implement core logic"
      - "Step 3: Add error handling"
      - "Step 4: Write tests"
      - "Step 5: Add documentation"

    success_criteria:
      - "All tests passing"
      - "Code follows project patterns"
      - "Documentation complete"

    research_keywords:             # For Copilot research (if auto_research: true)
      - "relevant technology"
      - "best practices"

    # Execution tracking (updated automatically)
    status: "pending"              # pending, in_progress, completed, blocked
    assigned_to: null
    started_at: null
    completed_at: null
    worktree: null
    branch: null
    github_issue: null             # If github_integration: true

    # Results (updated by agents)
    commits: 0
    files_changed: []
    tests_added: 0
    tests_passing: false

  # Example task 2
  - id: "task-2"
    title: "Implement feature Y"
    description: "Another feature to implement in parallel"

    priority: "medium"
    complexity: 5
    estimated_hours: 6

    files:
      - "src/feature-y.ts"
      - "tests/feature-y.test.ts"

    dependencies: ["task-1"]       # Depends on task-1 completing first

    implementation_steps:
      - "Step 1: ..."
      - "Step 2: ..."

    success_criteria:
      - "Criteria 1"
      - "Criteria 2"

    research_keywords:
      - "keyword1"
      - "keyword2"

    status: "pending"
    assigned_to: null
    started_at: null
    completed_at: null
    worktree: null
    branch: null
    github_issue: null
    commits: 0
    files_changed: []
    tests_added: 0
    tests_passing: false

# Add more tasks as needed...
EOF

echo -e "${GREEN}✓ Created: $PLAN_DIR/plan.yaml${NC}"
echo ""

# Create helper scripts
cat > "$PLAN_DIR/scripts/status.sh" <<'EOF'
#!/bin/bash
# Quick status check
yq '.tasks[] | "\(.id): \(.status) - \(.title)"' .parallel/plan.yaml
EOF
chmod +x "$PLAN_DIR/scripts/status.sh"

cat > "$PLAN_DIR/scripts/update.sh" <<'EOF'
#!/bin/bash
# Update task status
# Usage: ./update.sh task-1 completed
TASK_ID=$1
NEW_STATUS=$2
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"$NEW_STATUS\"" .parallel/plan.yaml
EOF
chmod +x "$PLAN_DIR/scripts/update.sh"

echo -e "${GREEN}✓ Created helper scripts${NC}"
echo ""

# Update .gitignore
GITIGNORE="$PROJECT_ROOT/.gitignore"

if [ ! -f "$GITIGNORE" ]; then
  touch "$GITIGNORE"
fi

# Remove old .parallel entry if exists
sed -i.bak '/^\.parallel\/$/d' "$GITIGNORE" 2>/dev/null || true

# Add worktrees to gitignore
if ! grep -q "^worktrees/$" "$GITIGNORE" 2>/dev/null; then
  echo "worktrees/" >> "$GITIGNORE"
  echo -e "${GREEN}✓ Added worktrees/ to .gitignore${NC}"
fi

# Add research cache to gitignore
if ! grep -q "^\.parallel/research/$" "$GITIGNORE" 2>/dev/null; then
  echo ".parallel/research/" >> "$GITIGNORE"
  echo -e "${GREEN}✓ Added .parallel/research/ to .gitignore${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Parallel execution plan initialized!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Edit .parallel/plan.yaml - define your tasks"
echo -e "  2. Commit to git: ${BLUE}git add .parallel/ && git commit -m 'feat: add parallel plan'${NC}"
echo -e "  3. Run research: ${BLUE}./research_from_plan.sh${NC}"
echo -e "  4. Setup worktrees: ${BLUE}./setup_worktrees_from_plan.sh${NC}"
echo -e "  5. Spawn agents: ${BLUE}./spawn_agents_from_plan.sh${NC}"
echo ""

echo -e "${YELLOW}Quick commands:${NC}"
echo -e "  Status: ${BLUE}./parallel/scripts/status.sh${NC}"
echo -e "  Validate: ${BLUE}yq .parallel/plan.yaml${NC}"
echo ""
