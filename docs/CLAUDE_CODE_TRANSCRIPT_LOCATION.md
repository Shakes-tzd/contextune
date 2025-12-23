# Claude Code Transcript Location

## Summary

Claude Code stores conversation transcripts in JSONL format (JSON Lines - one JSON object per line) at specific locations.

## Locations

### Global History (All Projects)
```bash
~/.claude/history.jsonl
```

This file contains the history of all sessions across all projects.

### Project-Specific Conversations
```bash
~/.claude/projects/-<FULL_PROJECT_PATH>/<session-id>.jsonl
```

**Where:**
- `<FULL_PROJECT_PATH>` = The full absolute path with `/` replaced by `-` and a leading `-`
- `<session-id>` = A UUID for each conversation session

**Example:**

If your project is at: `/Users/shakes/DevProjects/contextune`

Then transcripts are stored at:
```bash
~/.claude/projects/-Users-shakes-DevProjects-contextune/1cc2a1f2-b6c9-4b5e-a684-f82ff9cc7b3a.jsonl
~/.claude/projects/-Users-shakes-DevProjects-contextune/661ecfd0-05c0-46f5-aef7-cde0aef26dc9.jsonl
# ... etc (one file per session)
```

## Path Conversion Formula

To convert a project path to the transcript directory name:

```bash
# Input:  /Users/shakes/DevProjects/contextune
# Output: -Users-shakes-DevProjects-contextune

# Bash conversion:
ESCAPED_PATH=$(pwd | sed 's/\//-/g')
TRANSCRIPT_DIR="$HOME/.claude/projects/$ESCAPED_PATH"
```

## File Format

Each line in the JSONL file is a JSON object representing a conversation turn:

```json
{
  "display": "user's prompt text",
  "pastedContents": {},
  "timestamp": 1759771380131,
  "project": "/Users/shakes/.claude"
}
```

Or for assistant responses:

```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "text",
        "text": "assistant response..."
      }
    ]
  },
  "timestamp": 1759771380132
}
```

## Usage in Scripts

### Get Most Recent Transcript

```bash
#!/bin/bash
# Get most recent transcript for current project

ESCAPED_PATH=$(pwd | sed 's/\//-/g')
TRANSCRIPT_DIR="$HOME/.claude/projects/$ESCAPED_PATH"

if [ ! -d "$TRANSCRIPT_DIR" ]; then
    echo "Error: Not in a Claude Code project" >&2
    exit 1
fi

LATEST=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    echo "Error: No transcripts found" >&2
    exit 1
fi

echo "$LATEST"
```

### Extract User Prompts

```bash
# Using jq to extract all user prompts
cat "$TRANSCRIPT_DIR"/*.jsonl | jq -r 'select(.display) | .display'
```

### Extract Assistant Responses

```bash
# Extract assistant responses
cat "$TRANSCRIPT_DIR"/*.jsonl | jq -r '
  select(.type == "assistant") |
  .message.content[] |
  select(.type == "text") |
  .text
'
```

## Related Scripts

- **scripts/extract-current-plan.sh** - Extracts plans from current session transcript
- **scripts/extract-plan-from-context.py** - Parses transcript and extracts plan structure

## References

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- Bug fix: scripts/extract-current-plan.sh:11-13 (fixed 2025-12-23)
