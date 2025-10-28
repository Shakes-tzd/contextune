#!/bin/bash
# Session Status - Show git state and session context
#
# Usage: ./scripts/session-status.sh [--since-commit HASH]

set -e

CACHE_DIR="$HOME/.claude/plugins/contextune/.cache"
LAST_SESSION_FILE="$CACHE_DIR/last_session.yaml"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Session Status - Git-Powered State Awareness${NC}"
echo ""

# Get current git state
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)

echo -e "${GREEN}Current State:${NC}"
echo "  Branch: $CURRENT_BRANCH"
echo "  Commit: $CURRENT_COMMIT"
echo ""

# Check for uncommitted changes
UNCOMMITTED=$(git status --short | wc -l | tr -d ' ')
if [ "$UNCOMMITTED" -gt 0 ]; then
    echo -e "${YELLOW}Uncommitted Changes: $UNCOMMITTED file(s)${NC}"
    git status --short | head -10
    echo ""
fi

# Load last session info
if [ -f "$LAST_SESSION_FILE" ]; then
    echo -e "${GREEN}Last Session:${NC}"

    # Extract info from YAML (works without yq)
    LAST_COMMIT=$(grep "last_commit:" "$LAST_SESSION_FILE" | awk '{print $2}' | tr -d '"')
    LAST_TIME=$(grep "ended_at:" "$LAST_SESSION_FILE" | cut -d' ' -f2- | tr -d '"')
    LAST_BRANCH=$(grep "branch:" "$LAST_SESSION_FILE" | awk '{print $2}' | tr -d '"')

    echo "  Ended: $LAST_TIME"
    echo "  Commit: $LAST_COMMIT"
    echo "  Branch: $LAST_BRANCH"
    echo ""

    # Calculate what happened since
    if [ -n "$LAST_COMMIT" ] && [ "$LAST_COMMIT" != "$CURRENT_COMMIT" ]; then
        echo -e "${GREEN}Changes Since Last Session:${NC}"

        # Commit count
        COMMIT_COUNT=$(git rev-list --count ${LAST_COMMIT}..HEAD 2>/dev/null || echo "0")
        echo "  Commits: $COMMIT_COUNT"

        # Show recent commits
        if [ "$COMMIT_COUNT" -gt 0 ]; then
            echo ""
            echo "  Recent commits:"
            git log --oneline ${LAST_COMMIT}..HEAD | head -5 | sed 's/^/    /'

            if [ "$COMMIT_COUNT" -gt 5 ]; then
                echo "    ... and $((COMMIT_COUNT - 5)) more"
            fi
            echo ""
        fi

        # File changes
        FILE_CHANGES=$(git diff --name-status ${LAST_COMMIT}..HEAD | wc -l | tr -d ' ')
        echo "  Files changed: $FILE_CHANGES"

        if [ "$FILE_CHANGES" -gt 0 ]; then
            echo ""
            echo "  File summary:"
            git diff --stat ${LAST_COMMIT}..HEAD | tail -1 | sed 's/^/    /'
            echo ""
            echo "  Files by type:"
            git diff --name-status ${LAST_COMMIT}..HEAD | awk '{print "    " $1 " " $2}' | head -10

            if [ "$FILE_CHANGES" -gt 10 ]; then
                echo "    ... and $((FILE_CHANGES - 10)) more"
            fi
        fi
    else
        echo -e "${GREEN}No commits since last session${NC}"
    fi
else
    echo -e "${YELLOW}No previous session tracked${NC}"
    echo "  (This is the first session or cache was cleared)"
fi

echo ""
echo -e "${BLUE}Git Source of Truth:${NC}"
echo "  All file changes tracked by git"
echo "  Use 'git diff' to see detailed changes"
echo "  Use 'git log' to see full history"
echo ""

# Decision tracking status
if [ -f "decisions.yaml" ]; then
    DECISION_COUNT=$(grep -c "^  - id:" decisions.yaml 2>/dev/null || echo "0")
    echo -e "${GREEN}Decision Tracking:${NC}"
    echo "  Active decisions: $DECISION_COUNT"
    echo "  Query: uv run scripts/decision-query.py --topic <topic>"
    echo ""
fi

echo "✅ Ready to continue work!"
