#!/bin/bash
# delegate_copilot.sh - Universal GitHub Copilot delegation script
# Preserves Claude Code session limits by offloading tasks to Copilot CLI

set -euo pipefail

# Configuration
RESULTS_DIR="${COPILOT_RESULTS_DIR:-./copilot-results}"
TIMEOUT="${COPILOT_TIMEOUT:-60}"  # Default 60 second timeout

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure results directory exists
mkdir -p "$RESULTS_DIR"

# Function to show usage
usage() {
    cat <<EOF
${BLUE}Copilot Delegation Script${NC}

Usage: $0 [OPTIONS] <task-description>

Delegates tasks to GitHub Copilot CLI to preserve Claude Code session limits.

OPTIONS:
    -t, --task-file FILE    Read task from JSON file
    -o, --output FILE       Output file (default: auto-generated)
    -T, --timeout SECONDS   Timeout in seconds (default: 60)
    -h, --help              Show this help message

EXAMPLES:
    # Delegate GitHub issue creation
    $0 "Create a GitHub issue for bug XYZ"

    # Delegate research task
    $0 "Research best React state management libraries for 2025"

    # Use task file
    $0 --task-file tasks/github-pr.json

BENEFITS:
    - Preserves Claude Code session limits (Pro: 10-40 prompts/5h)
    - Faster execution (Copilot avg 12.7s)
    - Offloads heavy research/GitHub ops to fresh context
    - Returns compressed results only

EOF
    exit 0
}

# Function to log with timestamp
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)  echo -e "${BLUE}[INFO]${NC} [$timestamp] $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} [$timestamp] $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} [$timestamp] $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} [$timestamp] $message" ;;
    esac
}

# Function to generate output filename
generate_output_file() {
    local task_hash=$(echo "$1" | md5 | cut -c1-8)
    local timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${RESULTS_DIR}/copilot_${timestamp}_${task_hash}.json"
}

# Function to delegate to Copilot
delegate_to_copilot() {
    local prompt="$1"
    local output_file="$2"

    log INFO "Delegating to Copilot CLI..."
    log INFO "Task: ${prompt:0:80}..."

    # Create temporary file for raw output
    local raw_output=$(mktemp)

    # Execute Copilot with timeout (if timeout command available)
    local start_time=$(date +%s.%N)

    # Check if timeout command exists (gtimeout on macOS via coreutils, timeout on Linux)
    local timeout_cmd=""
    if command -v gtimeout &> /dev/null; then
        timeout_cmd="gtimeout $TIMEOUT"
    elif command -v timeout &> /dev/null; then
        timeout_cmd="timeout $TIMEOUT"
    fi

    if [ -n "$timeout_cmd" ]; then
        eval "$timeout_cmd copilot -p \"$prompt\" --allow-all-tools" > "$raw_output" 2>&1
        local exit_code=$?
    else
        # No timeout available, run without it
        copilot -p "$prompt" --allow-all-tools > "$raw_output" 2>&1
        local exit_code=$?
    fi

    if [ $exit_code -eq 0 ]; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)

        # Extract JSON from markdown if present
        if grep -q '```json' "$raw_output"; then
            # Extract JSON from markdown code fence
            sed -n '/```json/,/```/p' "$raw_output" | sed '1d;$d' > "$output_file"
        else
            # Copy as-is (might already be JSON or plain text)
            cat "$raw_output" > "$output_file"
        fi

        # Add metadata wrapper
        local char_count=$(wc -c < "$output_file")
        local token_estimate=$((char_count / 4))

        # Create final output with metadata
        cat > "${output_file}.meta" <<EOF
{
  "status": "success",
  "duration_seconds": $duration,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "tokens_estimate": $token_estimate,
  "characters": $char_count,
  "cli": "copilot",
  "result_file": "$output_file"
}
EOF

        log SUCCESS "Delegation completed in ${duration}s (~${token_estimate} tokens)"
        log INFO "Result saved to: $output_file"
        log INFO "Metadata saved to: ${output_file}.meta"

        # Show preview of result
        echo ""
        echo -e "${BLUE}═══ Result Preview ═══${NC}"
        head -20 "$output_file"
        if [ $(wc -l < "$output_file") -gt 20 ]; then
            echo "..."
            echo -e "${YELLOW}(truncated, see full result in $output_file)${NC}"
        fi
        echo -e "${BLUE}═══════════════════════${NC}"
        echo ""

        # Cleanup
        rm -f "$raw_output"
        return 0
    else
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)

        log ERROR "Copilot delegation failed or timed out after ${duration}s"

        # Save error information
        cat > "$output_file" <<EOF
{
  "error": "Delegation failed or timed out",
  "duration_seconds": $duration,
  "timeout_seconds": $TIMEOUT,
  "output": $(jq -Rs . < "$raw_output")
}
EOF

        # Cleanup
        rm -f "$raw_output"
        return 1
    fi
}

# Parse command line arguments
TASK=""
TASK_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--task-file)
            TASK_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -T|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            TASK="$1"
            shift
            ;;
    esac
done

# Determine task source
if [ -n "$TASK_FILE" ]; then
    if [ ! -f "$TASK_FILE" ]; then
        log ERROR "Task file not found: $TASK_FILE"
        exit 1
    fi

    # Read task from JSON file
    TASK=$(jq -r '.prompt' "$TASK_FILE" 2>/dev/null || cat "$TASK_FILE")

    if [ -z "$TASK" ]; then
        log ERROR "Could not extract task from file: $TASK_FILE"
        exit 1
    fi

    log INFO "Loaded task from: $TASK_FILE"
elif [ -z "$TASK" ]; then
    log ERROR "No task specified. Use -t/--task-file or provide task as argument."
    echo ""
    usage
fi

# Generate output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE=$(generate_output_file "$TASK")
fi

# Delegate to Copilot
delegate_to_copilot "$TASK" "$OUTPUT_FILE"

exit $?
