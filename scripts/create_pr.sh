#!/bin/bash
# Deterministic Create Pull Request Workflow
#
# Creates a PR using gh CLI with standard template.
# Cost: ~$0.002 (545 tokens)
# Duration: 500-1000ms
#
# Usage: create_pr.sh <title> <body> [base] [head]

set -e

TITLE=$1
BODY=$2
BASE=${3:-master}
HEAD=${4:-$(git branch --show-current)}

if [ -z "$TITLE" ] || [ -z "$BODY" ]; then
    echo "Usage: create_pr.sh <title> <body> [base] [head]" >&2
    echo "Example: create_pr.sh 'Add feature' 'Implements X' 'main' 'feature-branch'" >&2
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found. Install: brew install gh" >&2
    exit 1
fi

# Create PR
gh pr create \
    --title "$TITLE" \
    --body "$BODY" \
    --base "$BASE" \
    --head "$HEAD"

echo "✅ Pull request created: $TITLE"
