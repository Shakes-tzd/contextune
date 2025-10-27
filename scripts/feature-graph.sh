#!/bin/bash
# feature-graph.sh - Generate dependency graph visualization
# Usage: ./scripts/feature-graph.sh [--format FORMAT]

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

# Parse arguments
FORMAT="text"  # text, dot, mermaid

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--format text|dot|mermaid]"
            exit 1
            ;;
    esac
done

# Check if yq is available
if ! command -v yq &> /dev/null; then
    echo -e "${RED}Error: yq is not installed${NC}"
    echo "Install with: brew install yq"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Feature Dependency Graph${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

if [ "$FORMAT" == "text" ]; then
    # Text format (ASCII art)

    echo -e "${BLUE}Legend:${NC}"
    echo -e "  ${GREEN}✓${NC} Completed"
    echo -e "  ${BLUE}→${NC} In Progress"
    echo -e "  ${YELLOW}○${NC} Planned"
    echo -e "  ${RED}✗${NC} Blocked"
    echo ""

    echo -e "${BLUE}Dependency Tree:${NC}"
    echo ""

    # Show each feature
    yq '.features[] | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
        NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
        STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")
        PHASE=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .phase" "$FEATURES_FILE")
        DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null || echo "")
        BLOCKS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .blocks[]" "$FEATURES_FILE" 2>/dev/null || echo "")

        # Status symbol
        STATUS_SYMBOL="○"
        STATUS_COLOR=$YELLOW
        case $STATUS in
            "completed")
                STATUS_SYMBOL="✓"
                STATUS_COLOR=$GREEN
                ;;
            "in_progress")
                STATUS_SYMBOL="→"
                STATUS_COLOR=$BLUE
                ;;
            "blocked")
                STATUS_SYMBOL="✗"
                STATUS_COLOR=$RED
                ;;
        esac

        echo -e "${STATUS_COLOR}${STATUS_SYMBOL} ${FEATURE_ID}${NC}: ${NAME} ${GRAY}[Phase ${PHASE}]${NC}"

        # Show dependencies (what this feature needs)
        if [ -n "$DEPS" ]; then
            for dep in $DEPS; do
                DEP_STATUS=$(yq ".features[] | select(.id == \"$dep\") | .status" "$FEATURES_FILE")
                DEP_SYMBOL="○"
                case $DEP_STATUS in
                    "completed") DEP_SYMBOL="✓" ;;
                    "in_progress") DEP_SYMBOL="→" ;;
                    "blocked") DEP_SYMBOL="✗" ;;
                esac
                echo -e "   ${GRAY}├─ depends on:${NC} $dep ${GRAY}[$DEP_SYMBOL]${NC}"
            done
        fi

        # Show what features this blocks
        if [ -n "$BLOCKS" ]; then
            for blocked in $BLOCKS; do
                BLOCKED_STATUS=$(yq ".features[] | select(.id == \"$blocked\") | .status" "$FEATURES_FILE")
                BLOCKED_SYMBOL="○"
                case $BLOCKED_STATUS in
                    "completed") BLOCKED_SYMBOL="✓" ;;
                    "in_progress") BLOCKED_SYMBOL="→" ;;
                    "blocked") BLOCKED_SYMBOL="✗" ;;
                esac
                echo -e "   ${GRAY}└─ blocks:${NC} $blocked ${GRAY}[$BLOCKED_SYMBOL]${NC}"
            done
        fi

        # Show if independent
        if [ -z "$DEPS" ] && [ -z "$BLOCKS" ]; then
            echo -e "   ${GRAY}└─ independent (can execute in parallel)${NC}"
        fi

        echo ""
    done

    echo -e "${BLUE}Phase Grouping:${NC}"
    echo ""

    for phase in 0 1 2 3 4; do
        PHASE_FEATURES=$(yq ".features[] | select(.phase == $phase) | .id" "$FEATURES_FILE" 2>/dev/null || echo "")

        if [ -n "$PHASE_FEATURES" ]; then
            echo -e "${BLUE}Phase $phase:${NC}"

            for feat in $PHASE_FEATURES; do
                STATUS=$(yq ".features[] | select(.id == \"$feat\") | .status" "$FEATURES_FILE")
                STATUS_SYMBOL="○"
                case $STATUS in
                    "completed") STATUS_SYMBOL="✓" ;;
                    "in_progress") STATUS_SYMBOL="→" ;;
                    "blocked") STATUS_SYMBOL="✗" ;;
                esac
                echo -e "  $STATUS_SYMBOL $feat"
            done

            echo ""
        fi
    done

    echo -e "${BLUE}Parallel Execution Groups:${NC}"
    echo ""

    echo -e "${GREEN}Can execute in parallel (Phase 1):${NC}"
    yq '.features[] | select(.phase == 1 and (.dependencies | length) == 0 and .status == "planned") | .id' "$FEATURES_FILE" | while read -r feat; do
        echo -e "  • $feat"
    done

    echo ""
    echo -e "${YELLOW}Sequential (Phase 2 - depends on Phase 1):${NC}"
    yq '.features[] | select(.phase == 2 and (.dependencies | length) > 0) | .id' "$FEATURES_FILE" | while read -r feat; do
        DEPS=$(yq ".features[] | select(.id == \"$feat\") | .dependencies[]" "$FEATURES_FILE" | tr '\n' ',' | sed 's/,$//')
        echo -e "  • $feat (needs: $DEPS)"
    done

elif [ "$FORMAT" == "dot" ]; then
    # Graphviz DOT format
    echo "digraph feature_dependencies {"
    echo "  rankdir=LR;"
    echo "  node [shape=box, style=rounded];"
    echo ""

    # Define nodes
    yq '.features[] | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
        NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE" | sed 's/"/\\"/g')
        STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")

        COLOR="yellow"
        case $STATUS in
            "completed") COLOR="green" ;;
            "in_progress") COLOR="blue" ;;
            "blocked") COLOR="red" ;;
        esac

        echo "  \"$FEATURE_ID\" [label=\"$FEATURE_ID\\n$NAME\", fillcolor=$COLOR, style=filled];"
    done

    echo ""

    # Define edges (dependencies)
    yq '.features[] | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
        DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null || echo "")

        if [ -n "$DEPS" ]; then
            for dep in $DEPS; do
                echo "  \"$dep\" -> \"$FEATURE_ID\" [label=\"depends on\"];"
            done
        fi
    done

    echo "}"
    echo ""
    echo "// Generate image with: dot -Tpng feature-graph.dot -o feature-graph.png"

elif [ "$FORMAT" == "mermaid" ]; then
    # Mermaid format (for GitHub, GitLab, etc.)
    echo "```mermaid"
    echo "graph LR"
    echo ""

    # Define nodes
    yq '.features[] | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
        NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE" | sed 's/"/\\"/g')
        STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")

        STYLE=""
        case $STATUS in
            "completed") STYLE=":::completed" ;;
            "in_progress") STYLE=":::in_progress" ;;
            "blocked") STYLE=":::blocked" ;;
            *) STYLE=":::planned" ;;
        esac

        echo "  $FEATURE_ID[\"$NAME\"]$STYLE"
    done

    echo ""

    # Define edges
    yq '.features[] | .id' "$FEATURES_FILE" | while read -r FEATURE_ID; do
        DEPS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .dependencies[]" "$FEATURES_FILE" 2>/dev/null || echo "")

        if [ -n "$DEPS" ]; then
            for dep in $DEPS; do
                echo "  $dep --> $FEATURE_ID"
            done
        fi
    done

    echo ""
    echo "  classDef completed fill:#90EE90,stroke:#006400"
    echo "  classDef in_progress fill:#87CEEB,stroke:#00008B"
    echo "  classDef blocked fill:#FFB6C1,stroke:#8B0000"
    echo "  classDef planned fill:#FFFFE0,stroke:#DAA520"
    echo "```"

else
    echo -e "${RED}Error: Unknown format: $FORMAT${NC}"
    echo "Supported formats: text, dot, mermaid"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

if [ "$FORMAT" == "text" ]; then
    echo -e "${GRAY}Commands:${NC}"
    echo -e "  ${GRAY}./scripts/feature-graph.sh --format dot > graph.dot${NC}"
    echo -e "  ${GRAY}dot -Tpng graph.dot -o graph.png${NC}"
    echo -e "  ${GRAY}./scripts/feature-graph.sh --format mermaid > GRAPH.md${NC}"
    echo ""
fi
