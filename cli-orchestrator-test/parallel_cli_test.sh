#!/bin/bash

# Parallel CLI Test Script
# Tests Claude Code, Gemini CLI, Codex CLI, and GitHub Copilot in parallel
# Measures execution time, captures outputs, and compares results

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESULTS_DIR="results"
LOGS_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Test prompt - something that requires actual thinking and code understanding
TEST_PROMPT="Analyze this simple Python function and identify any potential bugs or improvements:

def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

Provide your analysis in JSON format with keys: 'bugs', 'improvements', 'risk_level', and 'explanation'."

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Parallel CLI Orchestration Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Test Timestamp:${NC} $TIMESTAMP"
echo -e "${YELLOW}Test Prompt:${NC}"
echo "$TEST_PROMPT"
echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""

# Function to test a single CLI
test_cli() {
    local cli_name=$1
    local cli_command=$2
    local result_file="${RESULTS_DIR}/${cli_name}_${TIMESTAMP}.json"
    local log_file="${LOGS_DIR}/${cli_name}_${TIMESTAMP}.log"
    local time_file="${RESULTS_DIR}/${cli_name}_${TIMESTAMP}.time"

    echo -e "${YELLOW}[${cli_name}]${NC} Starting test..." | tee -a "$log_file"

    # Record start time
    local start_time=$(date +%s.%N)

    # Execute CLI command
    if eval "$cli_command" > "$result_file" 2>> "$log_file"; then
        # Record end time
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)
        echo "$duration" > "$time_file"

        # Calculate token estimate (rough estimate: 1 token ≈ 4 characters)
        local char_count=$(wc -c < "$result_file")
        local token_estimate=$((char_count / 4))

        echo -e "${GREEN}[${cli_name}]${NC} ✓ Completed in ${duration}s (~${token_estimate} tokens)" | tee -a "$log_file"
        return 0
    else
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc)
        echo "$duration" > "$time_file"

        echo -e "${RED}[${cli_name}]${NC} ✗ Failed after ${duration}s" | tee -a "$log_file"
        echo '{"error": "CLI execution failed"}' > "$result_file"
        return 1
    fi
}

# Export function and variables for parallel execution
export -f test_cli
export TEST_PROMPT RESULTS_DIR LOGS_DIR TIMESTAMP RED GREEN YELLOW BLUE NC

# Start parallel tests
echo -e "${BLUE}Starting parallel CLI tests...${NC}"
echo ""

# Array to store background process IDs
declare -a PIDS

# Test 1: Claude Code
(test_cli "claude" "claude -p \"$TEST_PROMPT\" --output-format json") &
PIDS+=($!)

# Test 2: Gemini CLI
(test_cli "gemini" "gemini -p \"$TEST_PROMPT\" --output-format json") &
PIDS+=($!)

# Test 3: Codex CLI
(test_cli "codex" "codex -p \"$TEST_PROMPT\" --output-format json") &
PIDS+=($!)

# Test 4: GitHub Copilot
(test_cli "copilot" "copilot -p \"$TEST_PROMPT\" --allow-all-tools") &
PIDS+=($!)

# Wait for all background processes
echo -e "${YELLOW}Waiting for all CLIs to complete...${NC}"
echo ""

for pid in "${PIDS[@]}"; do
    wait "$pid" || true
done

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo ""

# Generate comparison report
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Test Results Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Create results table
printf "%-15s %-15s %-15s %-15s\n" "CLI" "Time (s)" "Tokens (est)" "Status"
printf "%-15s %-15s %-15s %-15s\n" "───────────────" "───────────────" "───────────────" "───────────────"

for cli in claude gemini codex copilot; do
    time_file="${RESULTS_DIR}/${cli}_${TIMESTAMP}.time"
    result_file="${RESULTS_DIR}/${cli}_${TIMESTAMP}.json"

    if [ -f "$time_file" ]; then
        duration=$(cat "$time_file")
        char_count=$(wc -c < "$result_file" 2>/dev/null || echo "0")
        token_estimate=$((char_count / 4))

        # Check if result contains error
        if grep -q '"error"' "$result_file" 2>/dev/null; then
            status="${RED}✗ Failed${NC}"
        else
            status="${GREEN}✓ Success${NC}"
        fi

        printf "%-15s %-15s %-15s " "$cli" "$duration" "$token_estimate"
        echo -e "$status"
    else
        printf "%-15s %-15s %-15s %s\n" "$cli" "N/A" "N/A" "${RED}✗ No data${NC}"
    fi
done

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""

# Show fastest CLI
echo -e "${YELLOW}Performance Rankings:${NC}"
echo ""

# Sort by time
{
    for cli in claude gemini codex copilot; do
        time_file="${RESULTS_DIR}/${cli}_${TIMESTAMP}.time"
        if [ -f "$time_file" ]; then
            duration=$(cat "$time_file")
            echo "$duration $cli"
        fi
    done
} | sort -n | awk '{print NR". "$2" - "$1"s"}'

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo ""

# Quality analysis
echo -e "${YELLOW}Response Quality Analysis:${NC}"
echo ""

for cli in claude gemini codex copilot; do
    result_file="${RESULTS_DIR}/${cli}_${TIMESTAMP}.json"

    if [ -f "$result_file" ] && [ -s "$result_file" ]; then
        echo -e "${BLUE}[${cli}]${NC}"

        # Check if valid JSON
        if jq empty "$result_file" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Valid JSON response"

            # Check for expected keys
            if jq -e '.bugs' "$result_file" >/dev/null 2>&1; then
                echo -e "  ${GREEN}✓${NC} Contains 'bugs' field"
            else
                echo -e "  ${YELLOW}⚠${NC} Missing 'bugs' field"
            fi

            if jq -e '.improvements' "$result_file" >/dev/null 2>&1; then
                echo -e "  ${GREEN}✓${NC} Contains 'improvements' field"
            else
                echo -e "  ${YELLOW}⚠${NC} Missing 'improvements' field"
            fi

            if jq -e '.risk_level' "$result_file" >/dev/null 2>&1; then
                echo -e "  ${GREEN}✓${NC} Contains 'risk_level' field"
            else
                echo -e "  ${YELLOW}⚠${NC} Missing 'risk_level' field"
            fi

            # Show response size
            response_size=$(jq -r 'if type == "object" then . | tostring | length else . | length end' "$result_file" 2>/dev/null || echo "0")
            echo -e "  Response size: ${response_size} characters"
        else
            echo -e "  ${RED}✗${NC} Invalid JSON response"
            echo -e "  First 200 chars: $(head -c 200 "$result_file")"
        fi
        echo ""
    else
        echo -e "${BLUE}[${cli}]${NC}"
        echo -e "  ${RED}✗${NC} No response or empty file"
        echo ""
    fi
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Test complete!${NC}"
echo -e "Results saved in: ${YELLOW}${RESULTS_DIR}/${NC}"
echo -e "Logs saved in: ${YELLOW}${LOGS_DIR}/${NC}"
echo ""
echo -e "To view individual responses:"
echo -e "  ${YELLOW}cat ${RESULTS_DIR}/claude_${TIMESTAMP}.json${NC}"
echo -e "  ${YELLOW}cat ${RESULTS_DIR}/gemini_${TIMESTAMP}.json${NC}"
echo -e "  ${YELLOW}cat ${RESULTS_DIR}/codex_${TIMESTAMP}.json${NC}"
echo -e "  ${YELLOW}cat ${RESULTS_DIR}/copilot_${TIMESTAMP}.json${NC}"
echo ""
