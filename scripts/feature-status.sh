#!/bin/bash
# feature-status.sh - Show feature status and dependencies
# Usage: ./scripts/feature-status.sh [--phase N] [--priority LEVEL] [--status STATUS]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FEATURES_FILE="$PROJECT_ROOT/features.yaml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m'

# Check if yq is available
if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: yq is not installed${NC}"
    echo "Install with: brew install yq"
    exit 1
fi

# Parse arguments
FILTER_PHASE=""
FILTER_PRIORITY=""
FILTER_STATUS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            FILTER_PHASE="$2"
            shift 2
            ;;
        --priority)
            FILTER_PRIORITY="$2"
            shift 2
            ;;
        --status)
            FILTER_STATUS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--phase N] [--priority LEVEL] [--status STATUS]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Contextune Feature Status${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Show summary
echo -e "${BLUE}Summary:${NC}"
echo -e "  Total features: ${GREEN}$(yq '.summary.total_features' "$FEATURES_FILE")${NC}"
echo ""

echo -e "${BLUE}By Status:${NC}"
yq '.summary.by_status | to_entries | .[] | "  \(.key): \(.value)"' "$FEATURES_FILE"
echo ""

echo -e "${BLUE}By Priority:${NC}"
yq '.summary.by_priority | to_entries | .[] | "  \(.key): \(.value)"' "$FEATURES_FILE"
echo ""

echo -e "${BLUE}By Phase:${NC}"
yq '.summary.by_phase | to_entries | .[] | "  \(.key): \(.value)"' "$FEATURES_FILE"
echo ""

# Build query
QUERY='.features[]'

if [ -n "$FILTER_PHASE" ]; then
    QUERY="$QUERY | select(.phase == $FILTER_PHASE)"
fi

if [ -n "$FILTER_PRIORITY" ]; then
    QUERY="$QUERY | select(.priority == \"$FILTER_PRIORITY\")"
fi

if [ -n "$FILTER_STATUS" ]; then
    QUERY="$QUERY | select(.status == \"$FILTER_STATUS\")"
fi

# Show features
echo -e "${BLUE}Features:${NC}"
echo ""

yq -r "$QUERY | .id" "$FEATURES_FILE" | while read -r FEATURE_ID; do
    # Get feature details
    NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
    STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")
    PRIORITY=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .priority" "$FEATURES_FILE")
    PHASE=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .phase" "$FEATURES_FILE")
    HOURS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .effort.estimate_hours" "$FEATURES_FILE")
    DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null || echo "")

    # Color by status
    STATUS_COLOR=$GRAY
    case $STATUS in
        "planned")
            STATUS_COLOR=$YELLOW
            ;;
        "in_progress")
            STATUS_COLOR=$BLUE
            ;;
        "completed")
            STATUS_COLOR=$GREEN
            ;;
        "blocked")
            STATUS_COLOR=$RED
            ;;
    esac

    # Priority symbol
    PRIORITY_SYMBOL=""
    case $PRIORITY in
        "critical")
            PRIORITY_SYMBOL="🔥"
            ;;
        "high")
            PRIORITY_SYMBOL="⭐"
            ;;
        "medium")
            PRIORITY_SYMBOL="○"
            ;;
        "low")
            PRIORITY_SYMBOL="·"
            ;;
    esac

    echo -e "${STATUS_COLOR}${PRIORITY_SYMBOL} ${FEATURE_ID}${NC}: ${NAME}"
    echo -e "   Status: ${STATUS_COLOR}${STATUS}${NC} | Priority: ${PRIORITY} | Phase: ${PHASE} | Effort: ${HOURS}h"

    if [ -n "$DEPS" ]; then
        echo -e "   Dependencies: ${YELLOW}${DEPS}${NC}"
    fi

    echo ""
done

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Show execution recommendations
echo -e "${BLUE}Execution Recommendations:${NC}"
echo ""

echo -e "${GREEN}Ready to execute (no dependencies):${NC}"
yq '.features[] | select(.status == "planned" and (.dependencies | length) == 0) | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
    NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
    PHASE=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .phase" "$FEATURES_FILE")
    echo -e "  • ${FEATURE_ID}: ${NAME} (Phase ${PHASE})"
done

echo ""
echo -e "${YELLOW}Blocked (waiting on dependencies):${NC}"
yq '.features[] | select(.status == "planned" and (.dependencies | length) > 0) | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
    NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
    DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
    echo -e "  • ${FEATURE_ID}: ${NAME} (needs: ${DEPS})"
done

echo ""
echo -e "${GRAY}Commands:${NC}"
echo -e "  ${GRAY}./scripts/feature-status.sh --phase 1${NC}         # Show Phase 1 features"
echo -e "  ${GRAY}./scripts/feature-status.sh --priority critical${NC}  # Show critical features"
echo -e "  ${GRAY}./scripts/feature-execute.sh feat-001${NC}        # Execute a feature"
echo -e "  ${GRAY}./scripts/feature-graph.sh${NC}                   # Show dependency graph"
echo ""
