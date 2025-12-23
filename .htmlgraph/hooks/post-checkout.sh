#!/bin/bash
#
# HtmlGraph Post-Checkout Hook
# Logs branch switches / checkouts for continuity tracking
#

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

if [ ! -d ".htmlgraph" ]; then
  exit 0
fi

OLD_HEAD="$1"
NEW_HEAD="$2"
FLAG="$3"

if ! command -v htmlgraph &> /dev/null; then
  if command -v python3 &> /dev/null; then
    python3 -m htmlgraph.git_events checkout "$OLD_HEAD" "$NEW_HEAD" "$FLAG" &> /dev/null &
  fi
  exit 0
fi

htmlgraph git-event checkout "$OLD_HEAD" "$NEW_HEAD" "$FLAG" &> /dev/null &
exit 0
