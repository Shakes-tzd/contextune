#!/bin/bash
# feature-complete.sh - Mark feature as completed
# Usage: ./scripts/feature-complete.sh FEATURE_ID

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FEATURES_FILE="$PROJECT_ROOT/features.yaml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Feature ID required${NC}"
    echo "Usage: $0 FEATURE_ID"
    exit 1
fi

FEATURE_ID=$1

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Complete Feature: $FEATURE_ID${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Validate feature exists
if ! yq ".features[] | select(.id == \"$FEATURE_ID\")" "$FEATURES_FILE" >/dev/null 2>&1; then
    echo -e "${RED}Error: Feature $FEATURE_ID not found${NC}"
    exit 1
fi

# Get feature details
NAME=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .name" "$FEATURES_FILE")
STATUS=$(yq ".features[] | select(.id == \"$FEATURE_ID\") | .status" "$FEATURES_FILE")

echo -e "${BLUE}Feature:${NC} $NAME"
echo -e "${BLUE}Current status:${NC} $STATUS"
echo ""

# Check if already completed
if [ "$STATUS" == "completed" ]; then
    echo -e "${GREEN}✓ Feature already marked as completed${NC}"
    exit 0
fi

# Ask for confirmation
read -p "Mark this feature as completed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Update status
TEMP_FILE=$(mktemp)
yq "(.features[] | select(.id == \"$FEATURE_ID\") | .status) = \"completed\"" "$FEATURES_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$FEATURES_FILE"

echo -e "${GREEN}✓ Status updated to: completed${NC}"

# Commit status change
cd "$PROJECT_ROOT"
git add "$FEATURES_FILE"
git commit -m "chore($FEATURE_ID): mark as completed

Completed: $NAME

✅ Feature implementation complete
"

echo -e "${GREEN}✓ Committed status change${NC}"

# Check what features are now unblocked
UNBLOCKED=$(yq ".features[] | select(.dependencies[] == \"$FEATURE_ID\" and .status == \"planned\") | .id" "$FEATURES_FILE" 2>/dev/null || echo "")

if [ -n "$UNBLOCKED" ]; then
    echo ""
    echo -e "${BLUE}Features now unblocked:${NC}"
    for feat in $UNBLOCKED; do
        FEAT_NAME=$(yq ".features[] | select(.id == \"$feat\") | .name" "$FEATURES_FILE")
        echo -e "  ${GREEN}✓${NC} $feat: $FEAT_NAME"
    done

    echo ""
    echo -e "${YELLOW}You can now execute:${NC}"
    for feat in $UNBLOCKED; do
        echo -e "  ${BLUE}./scripts/feature-execute.sh $feat${NC}"
    done
fi

# Show completion stats
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Feature $FEATURE_ID completed!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

COMPLETED_COUNT=$(yq '.features[] | select(.status == "completed") | .id' "$FEATURES_FILE" | wc -l | tr -d ' ')
TOTAL_COUNT=$(yq '.features | length' "$FEATURES_FILE")
COMPLETION_PCT=$(awk "BEGIN {printf \"%.0f\", ($COMPLETED_COUNT/$TOTAL_COUNT)*100}")

echo -e "${BLUE}Overall Progress:${NC}"
echo -e "  Completed: ${GREEN}$COMPLETED_COUNT${NC} / $TOTAL_COUNT (${GREEN}$COMPLETION_PCT%${NC})"
echo ""

echo -e "${GRAY}Next steps:${NC}"
echo -e "  ${GRAY}./scripts/feature-status.sh${NC}         # View all features"
echo -e "  ${GRAY}./scripts/feature-graph.sh${NC}          # View dependency graph"
echo ""
