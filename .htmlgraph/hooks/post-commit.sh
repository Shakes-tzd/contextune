#!/bin/bash
#
# HtmlGraph Post-Commit Hook
# Logs Git commit events for agent-agnostic continuity tracking
#

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

if [ ! -d ".htmlgraph" ]; then
  exit 0
fi

if ! command -v htmlgraph &> /dev/null; then
  if command -v python3 &> /dev/null; then
    python3 -m htmlgraph.git_events commit &> /dev/null &
  fi
  exit 0
fi

htmlgraph git-event commit &> /dev/null &
exit 0
