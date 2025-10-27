#!/bin/bash
# feature-execute.sh - Execute feature implementation
# Usage: ./scripts/feature-execute.sh FEATURE_ID

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FEATURES_FILE="$PROJECT_ROOT/features.yaml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Feature ID required${NC}"
    echo "Usage: $0 FEATURE_ID"
    echo ""
    echo "Available features:"
    yq '.features[] | select(.status == "planned") | .id' "$FEATURES_FILE"
    exit 1
fi

FEATURE_ID=$1

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Execute Feature: $FEATURE_ID${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Check if yq is available
if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: yq is not installed${NC}"
    echo "Install with: brew install yq"
    exit 1
fi

# Validate feature exists
if ! yq ".features[] | select(.id == \"$FEATURE_ID\")" "$FEATURES_FILE" >/dev/null 2>&1; then
    echo -e "${RED}Error: Feature $FEATURE_ID not found${NC}"
    exit 1
fi

# Get feature details
NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")
PRIORITY=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .priority" "$FEATURES_FILE")
PHASE=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .phase" "$FEATURES_FILE")
HOURS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .effort.estimate_hours" "$FEATURES_FILE")
COMPLEXITY=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .effort.complexity" "$FEATURES_FILE")
RISK=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .effort.risk" "$FEATURES_FILE")

echo -e "${BLUE}Feature Details:${NC}"
echo -e "  Name: ${GREEN}$NAME${NC}"
echo -e "  Status: ${YELLOW}$STATUS${NC}"
echo -e "  Priority: $PRIORITY"
echo -e "  Phase: $PHASE"
echo -e "  Estimated effort: ${HOURS}h"
echo -e "  Complexity: $COMPLEXITY"
echo -e "  Risk: $RISK"
echo ""

# Check status
if [ "$STATUS" == "completed" ]; then
    echo -e "${GREEN}✓ Feature already completed${NC}"
    exit 0
fi

if [ "$STATUS" == "blocked" ]; then
    echo -e "${RED}✗ Feature is blocked${NC}"
    exit 1
fi

if [ "$STATUS" != "planned" ] && [ "$STATUS" != "in_progress" ]; then
    echo -e "${YELLOW}⚠ Feature status is '$STATUS'${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check dependencies
DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null || echo "")

if [ -n "$DEPS" ]; then
    echo -e "${BLUE}Checking dependencies...${NC}"
    DEPS_MET=true

    for dep in $DEPS; do
        DEP_STATUS=$(yq ".features[] | select(.id == \"$dep\") | .status" "$FEATURES_FILE")
        DEP_NAME=$(yq ".features[] | select(.id == \"$dep\") | .name" "$FEATURES_FILE")

        if [ "$DEP_STATUS" != "completed" ]; then
            echo -e "  ${RED}✗ $dep: $DEP_NAME (status: $DEP_STATUS)${NC}"
            DEPS_MET=false
        else
            echo -e "  ${GREEN}✓ $dep: $DEP_NAME${NC}"
        fi
    done

    if [ "$DEPS_MET" = false ]; then
        echo ""
        echo -e "${RED}Error: Dependencies not met${NC}"
        echo "Complete dependent features first, then try again"
        exit 1
    fi

    echo ""
fi

# Show implementation plan
echo -e "${BLUE}Implementation Plan:${NC}"
echo ""

echo -e "${BLUE}Files to modify:${NC}"
yq ".features[] | select(.id == \"$FEATURE_ID\") | .implementation.files[]" "$FEATURES_FILE" | while read -r file; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${YELLOW}+${NC} $file (will create)"
    fi
done

echo ""
echo -e "${BLUE}Changes required:${NC}"
yq ".features[] | select(.id == \"$FEATURE_ID\") | .implementation.changes[]" "$FEATURES_FILE" | while read -r change; do
    echo -e "  • $change"
done

echo ""
echo -e "${BLUE}Testing required:${NC}"
yq ".features[] | select(.id == \"$FEATURE_ID\") | .testing[]" "$FEATURES_FILE" | while read -r test; do
    echo -e "  • $test"
done

echo ""

# Ask for confirmation
read -p "Create worktree for this feature? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Create worktree
WORKTREE="worktrees/$FEATURE_ID"
BRANCH="feature/$FEATURE_ID"

echo ""
echo -e "${BLUE}Creating worktree...${NC}"

if [ -d "$PROJECT_ROOT/$WORKTREE" ]; then
    echo -e "${YELLOW}⚠ Worktree already exists: $WORKTREE${NC}"

    # Check if it's registered with git
    if git -C "$PROJECT_ROOT" worktree list | grep -q "$WORKTREE"; then
        echo -e "${GREEN}✓ Registered with git${NC}"
    else
        echo -e "${RED}✗ Directory exists but not registered${NC}"
        echo -e "${YELLOW}Remove manually: rm -rf $WORKTREE${NC}"
        exit 1
    fi
else
    # Create worktree
    cd "$PROJECT_ROOT"

    if git show-ref --verify --quiet refs/heads/$BRANCH; then
        echo -e "${YELLOW}⚠ Branch $BRANCH already exists${NC}"
        git worktree add "$WORKTREE" "$BRANCH"
    else
        git worktree add "$WORKTREE" -b "$BRANCH"
    fi

    echo -e "${GREEN}✓ Created worktree: $WORKTREE${NC}"
fi

# Update feature status to in_progress
echo ""
echo -e "${BLUE}Updating feature status...${NC}"

# Use a temp file to avoid yq issues with in-place editing
TEMP_FILE=$(mktemp)
yq "(.features[] | select(.id == \"$FEATURE_ID\") | .status) = \"in_progress\"" "$FEATURES_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$FEATURES_FILE"

echo -e "${GREEN}✓ Status updated to: in_progress${NC}"

# Commit status change
cd "$PROJECT_ROOT"
git add "$FEATURES_FILE"
git commit -m "chore($FEATURE_ID): start implementation

Starting work on: $NAME
Estimated effort: ${HOURS}h
Phase: $PHASE
"

echo -e "${GREEN}✓ Committed status change${NC}"

# Show next steps
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Ready to implement $FEATURE_ID${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. ${BLUE}cd $WORKTREE${NC}"
echo -e "  2. Make changes to files listed above"
echo -e "  3. Run tests"
echo -e "  4. Commit changes"
echo -e "  5. Push branch: ${BLUE}git push -u origin $BRANCH${NC}"
echo -e "  6. Create PR"
echo -e "  7. Mark feature as completed: ${BLUE}./scripts/feature-complete.sh $FEATURE_ID${NC}"
echo ""

echo -e "${GRAY}Worktree: $PROJECT_ROOT/$WORKTREE${NC}"
echo -e "${GRAY}Branch: $BRANCH${NC}"
echo ""

# Open editor with implementation guide (optional)
IMPL_GUIDE="$PROJECT_ROOT/PLUGIN_IMPROVEMENTS.md"
if [ -f "$IMPL_GUIDE" ]; then
    read -p "Open implementation guide? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Try to detect editor
        if [ -n "${EDITOR:-}" ]; then
            $EDITOR "$IMPL_GUIDE"
        elif command -v code &> /dev/null; then
            code "$IMPL_GUIDE"
        elif command -v vim &> /dev/null; then
            vim "$IMPL_GUIDE"
        else
            echo "Open: $IMPL_GUIDE"
        fi
    fi
fi
