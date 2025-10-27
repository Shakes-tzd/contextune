#!/bin/bash
# research_task.sh - Delegate research tasks to Copilot CLI
# Preserves Claude Code sessions by offloading web research, library comparisons, etc.

set -euo pipefail

# Source the main delegation script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delegate_copilot.sh" 2>/dev/null || true

# Research task templates
research_library() {
    local library_name="$1"
    local use_case="${2:-general}"

    local prompt="Research the following library: $library_name
Use case: $use_case

Provide comprehensive information including:
1. What it does
2. Current version and maintenance status
3. Pros and cons
4. Best use cases
5. Alternatives to consider
6. Community adoption (GitHub stars, npm downloads, etc.)
7. Recommendation for the use case

Return results in JSON format:
{
  \"library\": \"$library_name\",
  \"version\": \"<latest-version>\",
  \"description\": \"<description>\",
  \"pros\": [\"<pro1>\", \"<pro2>\"],
  \"cons\": [\"<con1>\", \"<con2>\"],
  \"use_cases\": [\"<use-case1>\", \"<use-case2>\"],
  \"alternatives\": [\"<alt1>\", \"<alt2>\"],
  \"stats\": {
    \"github_stars\": <number>,
    \"npm_downloads\": \"<weekly-downloads>\"
  },
  \"recommendation\": \"<recommendation>\"
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/research_library_$(date +%s).json}"
}

research_compare() {
    local options="$1"  # Comma-separated list
    local criteria="${2:-features,performance,ease-of-use}"

    local prompt="Compare the following options: $options

Comparison criteria: $criteria

For each option, evaluate based on the criteria and provide a clear recommendation.

Return results in JSON format:
{
  \"options\": [
    {
      \"name\": \"<option-name>\",
      \"scores\": {
        \"<criterion1>\": <score-1-10>,
        \"<criterion2>\": <score-1-10>
      },
      \"summary\": \"<summary>\"
    }
  ],
  \"recommendation\": {
    \"choice\": \"<recommended-option>\",
    \"reasoning\": \"<why>\"
  }
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/research_compare_$(date +%s).json}"
}

research_best_practices() {
    local topic="$1"
    local year="${2:-2025}"

    local prompt="Research current best practices for: $topic
Year: $year

Provide up-to-date best practices including:
1. Industry standards
2. Common patterns
3. What to avoid
4. Tools and libraries recommended
5. Examples

Return results in JSON format:
{
  \"topic\": \"$topic\",
  \"year\": $year,
  \"best_practices\": [
    {
      \"category\": \"<category>\",
      \"practice\": \"<practice>\",
      \"reasoning\": \"<why>\"
    }
  ],
  \"anti_patterns\": [\"<anti-pattern1>\", \"<anti-pattern2>\"],
  \"recommended_tools\": [\"<tool1>\", \"<tool2>\"],
  \"examples\": [\"<example1>\", \"<example2>\"]
}"

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/research_best_practices_$(date +%s).json}"
}

research_documentation() {
    local tool_or_api="$1"
    local specific_feature="${2:-}"

    local prompt="Look up current documentation for: $tool_or_api"

    if [ -n "$specific_feature" ]; then
        prompt="$prompt
Specific feature: $specific_feature"
    fi

    prompt="$prompt

Find the most recent official documentation and provide:
1. API/usage examples
2. Key concepts
3. Common patterns
4. Gotchas and important notes
5. Links to official docs

Return results in JSON format with examples and references."

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/research_docs_$(date +%s).json}"
}

research_general() {
    local question="$1"

    local prompt="Research and answer the following question comprehensively:
$question

Provide:
1. Direct answer
2. Supporting details
3. Sources/references
4. Related considerations
5. Recommendations if applicable

Return results in structured JSON format that is easy to parse and understand."

    delegate_to_copilot "$prompt" "${OUTPUT_FILE:-./copilot-results/research_general_$(date +%s).json}"
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    cat <<EOF
Research Task Delegation Script

Preserves Claude Code session limits by delegating research to Copilot CLI.

Usage:
    $0 library <library-name> [use-case]
    $0 compare "option1,option2,option3" [criteria]
    $0 best-practices <topic> [year]
    $0 documentation <tool-or-api> [specific-feature]
    $0 general <question>

Examples:
    # Research a library
    $0 library "zustand" "React state management"

    # Compare options
    $0 compare "zustand,jotai,recoil" "bundle-size,DX,performance"

    # Best practices
    $0 best-practices "React performance optimization" 2025

    # Look up documentation
    $0 documentation "Next.js App Router" "server components"

    # General research
    $0 general "What are the security implications of using localStorage for JWT tokens?"

Benefits:
    - Preserves Claude Code sessions (research is expensive)
    - Access to web search (Copilot has web access)
    - Fast results (~12-15 seconds)
    - Returns compressed findings only

EOF
    exit 0
fi

# Parse research type
RESEARCH_TYPE="$1"
shift

case "$RESEARCH_TYPE" in
    library)
        research_library "$@"
        ;;
    compare)
        research_compare "$@"
        ;;
    best-practices)
        research_best_practices "$@"
        ;;
    documentation|docs)
        research_documentation "$@"
        ;;
    general)
        research_general "$@"
        ;;
    *)
        echo "Unknown research type: $RESEARCH_TYPE"
        exit 1
        ;;
esac
