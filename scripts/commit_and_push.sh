#!/bin/bash
# Deterministic Commit and Push Workflow
#
# Simple, fast, deterministic git workflow.
# Cost: ~$0.002 (545 tokens)
# Duration: 100-500ms
#
# Usage: commit_and_push.sh <files> <message> [branch]

set -e

FILES=${1:-.}
MESSAGE=$2
BRANCH=${3:-master}

if [ -z "$MESSAGE" ]; then
    echo "Usage: commit_and_push.sh <files> <message> [branch]" >&2
    echo "Example: commit_and_push.sh '.' 'feat: add feature' 'main'" >&2
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

# Push
git push origin $BRANCH

echo "✅ Committed and pushed to origin/$BRANCH"
