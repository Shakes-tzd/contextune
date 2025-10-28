#!/bin/bash
# Helper: Regenerate PLAN_FULL.md from modular task files

PLAN_DIR=$(dirname "$0")/..
PLAN_FILE="$PLAN_DIR/plan.yaml"
OUTPUT_FILE="$PLAN_DIR/PLAN_FULL.md"

cd "$PLAN_DIR"

if [ ! -f "plan.yaml" ]; then
  echo "❌ Error: plan.yaml not found"
  exit 1
fi

echo "📝 Generating PLAN_FULL.md from modular task files..."

# Extract metadata
PLAN_NAME=$(grep "name:" plan.yaml | head -1 | sed 's/.*name: *"\(.*\)".*/\1/')
CREATED=$(grep "created:" plan.yaml | head -1 | sed 's/.*created: *"\(.*\)".*/\1/')
STATUS=$(grep "status:" plan.yaml | head -1 | sed 's/.*status: *"\(.*\)".*/\1/')

# Start output
cat > PLAN_FULL.md <<EOF
# Development Plan: $PLAN_NAME

**Created:** $CREATED
**Status:** $STATUS

---

EOF

# Add overview
echo "## 📋 Overview" >> PLAN_FULL.md
echo "" >> PLAN_FULL.md
grep -A 10 "overview:" plan.yaml | tail -n +2 | sed '/^$/d' | sed 's/^  //' >> PLAN_FULL.md
echo "" >> PLAN_FULL.md
echo "---" >> PLAN_FULL.md
echo "" >> PLAN_FULL.md

# Append each task
TASK_COUNT=0
for TASK_FILE in tasks/*.md; do
  if [ -f "$TASK_FILE" ]; then
    echo "  ✅ Adding $TASK_FILE"
    cat "$TASK_FILE" >> PLAN_FULL.md
    echo "" >> PLAN_FULL.md
    echo "---" >> PLAN_FULL.md
    echo "" >> PLAN_FULL.md
    ((TASK_COUNT++))
  fi
done

echo ""
echo "✅ Generated PLAN_FULL.md with $TASK_COUNT tasks"
