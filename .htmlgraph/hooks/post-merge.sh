#!/bin/bash
#
# HtmlGraph Post-Merge Hook
# Logs successful merges for continuity tracking
#

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

if [ ! -d ".htmlgraph" ]; then
  exit 0
fi

SQUASH_FLAG="$1"

if ! command -v htmlgraph &> /dev/null; then
  if command -v python3 &> /dev/null; then
    python3 -m htmlgraph.git_events merge "$SQUASH_FLAG" &> /dev/null &
  fi
  exit 0
fi

htmlgraph git-event merge "$SQUASH_FLAG" &> /dev/null &
exit 0
