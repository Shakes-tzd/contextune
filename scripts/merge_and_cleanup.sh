#!/bin/bash
# Deterministic Merge and Cleanup Workflow
#
# Merges branch and cleans up (local + remote).
# Cost: ~$0.002 (545 tokens)
# Duration: 500-1500ms
#
# Usage: merge_and_cleanup.sh <branch> [into_branch] [remote]

set -e

BRANCH=$1
INTO_BRANCH=${2:-master}

# Auto-detect remote if not specified
if [ -z "$3" ]; then
    REMOTE=$(git remote | head -1)
    if [ -z "$REMOTE" ]; then
        echo "Error: No git remotes configured" >&2
        exit 1
    fi
else
    REMOTE=$3
fi

if [ -z "$BRANCH" ]; then
    echo "Usage: merge_and_cleanup.sh <branch> [into_branch] [remote]" >&2
    echo "Example: merge_and_cleanup.sh 'feature-x' 'main'" >&2
    echo "Remote auto-detected from: git remote (currently: $REMOTE)" >&2
    exit 1
fi

# Ensure we're on target branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$INTO_BRANCH" ]; then
    git checkout $INTO_BRANCH
fi

# Merge
git merge --no-ff $BRANCH -m "Merge branch '$BRANCH' into $INTO_BRANCH"

# Delete local branch
git branch -d $BRANCH

# Delete remote branch (auto-detected remote)
git push $REMOTE --delete $BRANCH 2>/dev/null || echo "ℹ️  Remote branch already deleted"

echo "✅ Merged $BRANCH into $INTO_BRANCH and cleaned up (remote: $REMOTE)"
