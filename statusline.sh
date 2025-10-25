#!/usr/bin/env bash
# Contextune Status Line Integration
# Displays last detected command with confidence

# Check for detection file
DETECTION_FILE=".contextune/last_detection"

if [ ! -f "$DETECTION_FILE" ]; then
    # No detection file - show ready state
    echo "🎯 Contextune: Ready"
    exit 0
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    # Fallback without jq
    echo "🎯 Contextune: Detected (install jq for details)"
    exit 0
fi

# Parse detection JSON
COMMAND=$(jq -r '.command // "unknown"' "$DETECTION_FILE" 2>/dev/null)
CONFIDENCE=$(jq -r '(.confidence * 100 | floor) // 0' "$DETECTION_FILE" 2>/dev/null)
METHOD=$(jq -r '.method // "unknown"' "$DETECTION_FILE" 2>/dev/null)

# Display detection
if [ "$COMMAND" != "unknown" ] && [ "$CONFIDENCE" -gt 0 ]; then
    echo "🎯 $COMMAND ($CONFIDENCE% via $METHOD)"
else
    echo "🎯 Contextune: Ready"
fi
