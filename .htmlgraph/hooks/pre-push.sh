#!/bin/bash
#
# HtmlGraph Pre-Push Hook
# Logs pushes for continuity tracking / team boundary events
#

set +e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

if [ ! -d ".htmlgraph" ]; then
  exit 0
fi

REMOTE_NAME="$1"
REMOTE_URL="$2"
UPDATES="$(cat)"

if ! command -v htmlgraph &> /dev/null; then
  if command -v python3 &> /dev/null; then
    printf "%s" "$UPDATES" | python3 -m htmlgraph.git_events push "$REMOTE_NAME" "$REMOTE_URL" &> /dev/null &
  fi
  exit 0
fi

printf "%s" "$UPDATES" | htmlgraph git-event push "$REMOTE_NAME" "$REMOTE_URL" &> /dev/null &
exit 0
