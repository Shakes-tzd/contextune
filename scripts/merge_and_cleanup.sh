#!/bin/bash
# Deterministic Merge and Cleanup Workflow
#
# Merges branch and cleans up (local + remote).
# Cost: ~$0.002 (545 tokens)
# Duration: 500-1500ms
#
# Usage: merge_and_cleanup.sh <branch> [into_branch]

set -e

BRANCH=$1
INTO_BRANCH=${2:-master}

if [ -z "$BRANCH" ]; then
    echo "Usage: merge_and_cleanup.sh <branch> [into_branch]" >&2
    echo "Example: merge_and_cleanup.sh 'feature-x' 'main'" >&2
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

# Delete remote branch
git push origin --delete $BRANCH 2>/dev/null || echo "ℹ️  Remote branch already deleted"

echo "✅ Merged $BRANCH into $INTO_BRANCH and cleaned up"
