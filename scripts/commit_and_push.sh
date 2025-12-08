#!/bin/bash
# Deterministic Commit and Push Workflow
#
# Simple, fast, deterministic git workflow.
# Cost: ~$0.002 (545 tokens)
# Duration: 100-500ms
#
# Usage: commit_and_push.sh <files> <message> [branch] [remote]

set -e

FILES=${1:-.}
MESSAGE=$2

# Auto-detect current branch if not specified (supports both main and master)
if [ -z "$3" ]; then
    BRANCH=$(git branch --show-current)
    if [ -z "$BRANCH" ]; then
        echo "Error: Could not detect current branch" >&2
        exit 1
    fi
else
    BRANCH=$3
fi

# Auto-detect remote if not specified
if [ -z "$4" ]; then
    # Get first remote (usually origin, but might be different)
    REMOTE=$(git remote | head -1)
    if [ -z "$REMOTE" ]; then
        echo "Error: No git remotes configured" >&2
        exit 1
    fi
else
    REMOTE=$4
fi

if [ -z "$MESSAGE" ]; then
    echo "Usage: commit_and_push.sh <files> <message> [branch] [remote]" >&2
    echo "Example: commit_and_push.sh '.' 'feat: add feature' 'main'" >&2
    echo "Remote auto-detected from: git remote (currently: $REMOTE)" >&2
    exit 1
fi

# Add files
git add $FILES

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit" >&2
    exit 0
fi

# Commit
git commit -m "$MESSAGE"

# Push with auto-detected remote
git push $REMOTE $BRANCH

echo "✅ Committed and pushed to $REMOTE/$BRANCH"
