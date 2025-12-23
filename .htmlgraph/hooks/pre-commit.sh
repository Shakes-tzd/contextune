#!/bin/bash
#
# HtmlGraph Pre-Commit Hook
# Reminds developers to create/start features for non-trivial work
#
# To disable: git config htmlgraph.precommit false
# To bypass once: git commit --no-verify

# Check if hook is disabled via config
if [ "$(git config --type=bool htmlgraph.precommit)" = "false" ]; then
    exit 0
fi

# Check if HtmlGraph is initialized
if [ ! -d ".htmlgraph" ]; then
    # Not an HtmlGraph project, skip silently
    exit 0
fi

# Fast check for in-progress features using grep (avoids Python startup)
# This is 10-100x faster than calling the CLI
ACTIVE_COUNT=$(find .htmlgraph/features -name "*.html" -exec grep -l 'data-status="in-progress"' {} \; 2>/dev/null | wc -l | tr -d ' ')

# If we have active features and htmlgraph CLI is available, get details
if [ "$ACTIVE_COUNT" -gt 0 ] && command -v htmlgraph &> /dev/null; then
    ACTIVE_FEATURES=$(htmlgraph feature list --status in-progress 2>/dev/null)
else
    ACTIVE_FEATURES=""
fi

# Redirect output to stderr (standard for git hooks)
exec 1>&2

if [ "$ACTIVE_COUNT" -gt 0 ]; then
    # Active features exist - show them
    echo ""
    echo "✓ HtmlGraph: $ACTIVE_COUNT active feature(s)"
    echo ""
    echo "$ACTIVE_FEATURES"
    echo ""
else
    # No active features - show reminder
    echo ""
    echo "⚠️  HtmlGraph Feature Reminder"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "No active features found. Did you forget to start one?"
    echo ""
    echo "For non-trivial work, consider:"
    echo "  1. Create feature: (use Python API or dashboard)"
    echo "  2. Start feature: htmlgraph feature start <feature-id>"
    echo ""
    echo "Quick decision:"
    echo "  • >30 min work? → Create feature"
    echo "  • 3+ files? → Create feature"
    echo "  • Needs tests? → Create feature"
    echo "  • Simple fix? → Direct commit OK"
    echo ""
    echo "To disable this reminder: git config htmlgraph.precommit false"
    echo "To bypass once: git commit --no-verify"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Proceeding with commit..."
    echo ""
fi

# Always exit 0 (allow commit)
exit 0
