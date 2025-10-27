#!/bin/bash
# github_operation.sh - Delegate GitHub operations to Copilot CLI
# Specialized script for issue management, PR operations, and repo queries

set -euo pipefail

# Source the main delegation script functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delegate_copilot.sh" 2>/dev/null || true

# GitHub operation templates
github_create_issue() {
    local title="$1"
    local body="$2"
    local labels="${3:-}"

    local prompt="Create a GitHub issue with the following details:
Title: $title
Body: $body"

    if [ -n "$labels" ]; then
        prompt="$prompt
Labels: $labels"
    fi

    prompt="$prompt

Use the gh CLI to create the issue and return the issue URL and number in JSON format:
{
  \"issue_number\": <number>,
  \"issue_url\": \"<url>\",
  \"status\": \"created\"
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/github_issue_$(date +%s).json}"
}

github_list_issues() {
    local repo="${1:-.}"  # Default to current repo
    local state="${2:-open}"  # Default to open issues
    local limit="${3:-10}"  # Default to 10 issues

    local prompt="List GitHub issues for repository: $repo
State: $state
Limit: $limit

Use the gh CLI and return results in JSON format:
{
  \"issues\": [
    {
      \"number\": <number>,
      \"title\": \"<title>\",
      \"state\": \"<state>\",
      \"labels\": [\"<label1>\", \"<label2>\"],
      \"url\": \"<url>\"
    }
  ]
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/github_issues_$(date +%s).json}"
}

github_create_pr() {
    local title="$1"
    local body="$2"
    local base="${3:-main}"
    local head="${4:-$(git branch --show-current)}"

    local prompt="Create a GitHub pull request:
Title: $title
Body: $body
Base branch: $base
Head branch: $head

Use the gh CLI and return the PR URL and number in JSON format:
{
  \"pr_number\": <number>,
  \"pr_url\": \"<url>\",
  \"status\": \"created\"
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/github_pr_$(date +%s).json}"
}

github_query_repo() {
    local query="$1"

    local prompt="Query GitHub repository information: $query

Use the gh CLI or gh api commands to gather information and return results in JSON format.
Provide clear, structured data that answers the query."

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/github_query_$(date +%s).json}"
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    cat <<EOF
GitHub Operations Delegation Script

Usage:
    $0 create-issue "title" "body" ["labels"]
    $0 list-issues [repo] [state] [limit]
    $0 create-pr "title" "body" [base] [head]
    $0 query "query description"

Examples:
    # Create an issue
    $0 create-issue "Fix login bug" "Users can't login with OAuth" "bug,priority-high"

    # List open issues
    $0 list-issues . open 20

    # Create a PR
    $0 create-pr "Add feature X" "Implements feature X as per issue #123" main feature/x

    # Query repo
    $0 query "Show the last 5 commits and their authors"

EOF
    exit 0
fi

# Parse operation
OPERATION="$1"
shift

case "$OPERATION" in
    create-issue)
        github_create_issue "$@"
        ;;
    list-issues)
        github_list_issues "$@"
        ;;
    create-pr)
        github_create_pr "$@"
        ;;
    query)
        github_query_repo "$@"
        ;;
    *)
        echo "Unknown operation: $OPERATION"
        exit 1
        ;;
esac
