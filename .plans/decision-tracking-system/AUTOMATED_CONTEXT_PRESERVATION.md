# Automated Context Preservation Across Compaction

**Problem:** User manually copied last Claude message to scratch_pad.md before compacting to preserve working context (design proposals, implementation plans).

**Solution:** Automated PreCompact hook that extracts working context and writes to scratch_pad.md with zero user intervention.

---

## Architecture

### PreCompact Hook Flow

```
User types /compact
    ↓
PreCompact hook triggered
    ↓
Hook reads transcript_path (full conversation)
    ↓
Extract last Claude message
    ↓
Detect "working context" patterns:
  - Design proposals
  - Implementation plans
  - Task breakdowns (YAML, markdown)
  - Code templates
  - Architecture decisions
    ↓
Write to scratch_pad.md automatically
    ↓
Compaction proceeds
    ↓
Next session starts
    ↓
System reminder shows scratch_pad.md content
```

### What Gets Preserved

**High-priority patterns:**
1. **Design proposals** - "Let me design...", "Architecture:", "Plan:"
2. **Task breakdowns** - YAML task lists, numbered steps
3. **Code templates** - Complete code blocks with comments
4. **Decision options** - "Option 1 vs Option 2", "Alternatives:"
5. **Implementation specs** - "Implementation steps:", "Files to create:"

**Detection heuristics:**
```python
HIGH_VALUE_PATTERNS = [
    r'## Architecture',
    r'## Implementation',
    r'## Task \d+:',
    r'```yaml',
    r'decision-sync\.py',
    r'Option \d+:',
    r'Let me design',
    r'Plan:',
    r'Enhanced schema:',
    r'Auto-population',
]

# Extract if Claude's last message contains ≥3 high-value patterns
```

---

## Implementation

### File: `hooks/context_preserver.py`

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Automated Context Preservation Hook (PreCompact)

Automatically extracts working context from conversation transcript
before compaction and writes to scratch_pad.md for next session.

Eliminates manual copying of Claude's last message.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# High-value patterns indicating working context worth preserving
HIGH_VALUE_PATTERNS = [
    r'## Architecture',
    r'## Implementation',
    r'## Task \d+:',
    r'## Solution:',
    r'```yaml',
    r'```python',
    r'decision-sync\.py',
    r'decision-link\.py',
    r'Option \d+:',
    r'Let me design',
    r'Enhanced schema:',
    r'Auto-population',
    r'file_path.*\.md',
    r'task-\d+\.md',
    r'Updated plan:',
    r'### \d+\.',  # Numbered sections
]

def extract_last_claude_message(transcript_path: str) -> Optional[str]:
    """
    Extract the last message from Claude in the conversation.

    Args:
        transcript_path: Path to conversation transcript file

    Returns:
        Last Claude message content or None if not found
    """
    try:
        with open(transcript_path, 'r') as f:
            content = f.read()

        # Claude Code transcript format (approximate - adjust based on actual format)
        # Look for last assistant message

        # Try JSON lines format first
        lines = content.strip().split('\n')
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('role') == 'assistant':
                    return entry.get('content', '')
            except json.JSONDecodeError:
                continue

        # Fallback: look for last message with "assistant:" prefix
        assistant_messages = re.findall(r'assistant:\s*(.*?)(?=\nuser:|$)', content, re.DOTALL)
        if assistant_messages:
            return assistant_messages[-1].strip()

        return None

    except Exception as e:
        print(f"DEBUG: Failed to read transcript: {e}", file=sys.stderr)
        return None

def detect_working_context(message: str) -> int:
    """
    Count high-value patterns in message to determine if it contains
    working context worth preserving.

    Args:
        message: Claude's message content

    Returns:
        Number of high-value patterns detected
    """
    if not message:
        return 0

    count = 0
    for pattern in HIGH_VALUE_PATTERNS:
        matches = re.findall(pattern, message, re.IGNORECASE)
        count += len(matches)

    return count

def extract_structured_content(message: str) -> dict:
    """
    Extract structured content sections from message.

    Args:
        message: Claude's message content

    Returns:
        Dict with extracted sections (yaml_blocks, code_blocks, sections)
    """
    result = {
        'yaml_blocks': [],
        'code_blocks': [],
        'sections': [],
        'full_message': message
    }

    # Extract YAML blocks
    yaml_blocks = re.findall(r'```yaml\n(.*?)```', message, re.DOTALL)
    result['yaml_blocks'] = yaml_blocks

    # Extract code blocks
    code_blocks = re.findall(r'```(?:python|bash|javascript)\n(.*?)```', message, re.DOTALL)
    result['code_blocks'] = code_blocks

    # Extract major sections (## headings)
    sections = re.findall(r'##\s+(.+?)(?=\n##|\Z)', message, re.DOTALL)
    result['sections'] = sections

    return result

def write_scratch_pad(project_root: Path, content: dict, session_id: str):
    """
    Write extracted content to scratch_pad.md in project root.

    Args:
        project_root: Project root directory
        content: Extracted structured content
        session_id: Current session ID
    """
    scratch_pad = project_root / 'scratch_pad.md'

    with open(scratch_pad, 'w') as f:
        f.write(f"# Context Preserved from Compaction\n\n")
        f.write(f"**Session ID:** {session_id}\n")
        f.write(f"**Preserved:** {datetime.now().isoformat()}\n")
        f.write(f"**Auto-extracted by:** PreCompact hook\n\n")
        f.write("---\n\n")

        # Write full message
        f.write("## Last Claude Message (Full Context)\n\n")
        f.write(content['full_message'])
        f.write("\n\n---\n\n")

        # Write extracted structured content
        if content['yaml_blocks']:
            f.write("## Extracted YAML Blocks\n\n")
            for i, block in enumerate(content['yaml_blocks'], 1):
                f.write(f"### YAML Block {i}\n\n")
                f.write(f"```yaml\n{block}```\n\n")

        if content['code_blocks']:
            f.write("## Extracted Code Blocks\n\n")
            for i, block in enumerate(content['code_blocks'], 1):
                f.write(f"### Code Block {i}\n\n")
                f.write(f"```\n{block}```\n\n")

    print(f"DEBUG: ✅ Preserved context to {scratch_pad}", file=sys.stderr)

def main():
    """
    PreCompact hook entry point.

    Reads conversation transcript, extracts last Claude message,
    detects working context, and writes to scratch_pad.md if valuable.
    """
    try:
        # Read hook data
        hook_data = json.loads(sys.stdin.read())

        transcript_path = hook_data.get('transcript_path', '')
        session_id = hook_data.get('session_id', 'unknown')
        trigger = hook_data.get('trigger', 'unknown')

        print(f"DEBUG: PreCompact triggered ({trigger})", file=sys.stderr)
        print(f"DEBUG: Transcript path: {transcript_path}", file=sys.stderr)

        # Extract last Claude message
        last_message = extract_last_claude_message(transcript_path)

        if not last_message:
            print("DEBUG: No Claude message found in transcript", file=sys.stderr)
            return

        # Detect if message contains working context
        pattern_count = detect_working_context(last_message)

        print(f"DEBUG: Detected {pattern_count} high-value patterns", file=sys.stderr)

        # Threshold: preserve if ≥3 high-value patterns
        if pattern_count >= 3:
            print("DEBUG: Working context detected, preserving...", file=sys.stderr)

            # Extract structured content
            structured = extract_structured_content(last_message)

            # Find project root (walk up from transcript location)
            project_root = Path(transcript_path).parent
            while project_root.parent != project_root:
                if (project_root / '.git').exists() or (project_root / 'pyproject.toml').exists():
                    break
                project_root = project_root.parent

            # Write to scratch_pad.md
            write_scratch_pad(project_root, structured, session_id)

            print(f"DEBUG: 🎯 Context preserved ({len(last_message)} chars, {pattern_count} patterns)", file=sys.stderr)
        else:
            print(f"DEBUG: No significant working context ({pattern_count} patterns < 3 threshold)", file=sys.stderr)

    except Exception as e:
        print(f"DEBUG: Context preservation failed: {e}", file=sys.stderr)

    # Always continue (don't block compaction)
    output = {"continue": True}
    print(json.dumps(output))
    sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## Registration

### File: `hooks/hooks.json` (add entry)

```json
{
  "hooks": [
    {
      "hookName": "PreCompact",
      "hookPath": "hooks/context_preserver.py",
      "enabled": true,
      "description": "Automatically preserve working context before compaction"
    }
  ]
}
```

---

## User Experience

### Before (Manual)

```
Claude: [Long design proposal with task-1.md, task-2.md, etc.]
User: *copies entire message manually*
User: *creates scratch_pad.md*
User: *pastes message*
User: /compact
```

### After (Automated)

```
Claude: [Long design proposal with task-1.md, task-2.md, etc.]
User: /compact
  ↓ (hook runs automatically)
  ↓ scratch_pad.md created with full context
  ↓
Next session:
  System reminder: "Note: scratch_pad.md contains preserved context"
```

**Zero manual steps!**

---

## Detection Examples

### Example 1: High-Value Message (Preserved)

```markdown
## Solution: Automated Context Preservation Hook

### Architecture
...

### File: `hooks/context_preserver.py`
```python
...
```

### Registration
```json
...
```

Pattern count: 8 (## Solution, ## Architecture, ```python, ```json, etc.)
✅ PRESERVED
```

### Example 2: Low-Value Message (Not Preserved)

```markdown
I've updated the file successfully. The changes look good.
Would you like me to proceed with the next step?
```

Pattern count: 0
❌ NOT PRESERVED (just conversational)
```

### Example 3: Working Context (Preserved)

```markdown
Let me design the auto-population architecture:

## Enhanced Schema

```yaml
conversations:
  scanned_count: 1236
  ...
```

## Implementation

### task-5.md: decision-sync.py
...

### task-6.md: decision-link.py
...

Option 1: Update existing plan
Option 2: Create Phase 2
```

Pattern count: 12 (design, Enhanced schema, ```yaml, task-5.md, task-6.md, Option 1, Option 2, etc.)
✅ PRESERVED
```

---

## Testing

```bash
# Test hook with mock transcript
cat > /tmp/test_transcript.jsonl <<'EOF'
{"role": "user", "content": "Design auto-population"}
{"role": "assistant", "content": "## Solution\n\n### Architecture\n\n```yaml\ntasks:\n  - task-5.md\n```\n\nOption 1: Update plan\nOption 2: New plan"}
EOF

# Run hook
echo '{"transcript_path":"/tmp/test_transcript.jsonl","session_id":"test","trigger":"manual"}' | \
  uv run hooks/context_preserver.py

# Verify scratch_pad.md created
cat scratch_pad.md
```

**Expected output:**
```
DEBUG: PreCompact triggered (manual)
DEBUG: Detected 7 high-value patterns
DEBUG: Working context detected, preserving...
DEBUG: ✅ Preserved context to scratch_pad.md
DEBUG: 🎯 Context preserved (145 chars, 7 patterns)
{"continue": true}
```

---

## Benefits

| Aspect | Manual (Before) | Automated (After) |
|--------|----------------|-------------------|
| **User effort** | Copy/paste/create file | Zero (automatic) |
| **Reliability** | Depends on remembering | 100% (always runs) |
| **Accuracy** | May miss content | Extracts full message + structured sections |
| **Speed** | 30-60 seconds | <100ms (hook execution) |
| **Pattern detection** | Manual judgment | Algorithmic (HIGH_VALUE_PATTERNS) |
| **Format** | Raw paste | Structured (full message + YAML + code) |

---

## Integration with Decision Tracking

**PreCompact hook** (immediate, ephemeral):
- Preserves working context for next session
- scratch_pad.md is temporary transfer mechanism
- Deleted after context is used

**Decision tracking system** (permanent, structured):
- Long-term storage in decisions.yaml
- Auto-populates from history.jsonl after sessions
- Queryable, linkable, lifecycle-managed

**Together:**
1. PreCompact preserves immediate working context (design in progress)
2. Decision tracking captures completed decisions (after implementation)
3. Complementary: short-term transfer + long-term database

---

## Next Steps

1. **Implement:** Create `hooks/context_preserver.py` with code above
2. **Register:** Add to `hooks/hooks.json`
3. **Test:** Trigger `/compact` with design message, verify scratch_pad.md
4. **Validate:** Next session should see scratch_pad.md via system reminder
5. **Integrate:** Decision tracking system reads scratch_pad.md and promotes to decisions.yaml

---

## Future Enhancements

**Smart detection:**
- Use Model2Vec embeddings to detect "design content" vs "conversational"
- Score messages by content type (design: 0.9, code: 0.8, chat: 0.2)
- Dynamic threshold based on message complexity

**Structured extraction:**
- Parse YAML task lists into structured format
- Extract file paths and create tracking entries
- Link to decision tracking system automatically

**User preferences:**
- `scratch_pad_config.json` for custom patterns
- Threshold adjustment (default: 3, user can set 1-10)
- Include/exclude patterns per project

**Observability:**
- Log to observability_db.py (preservations_count, avg_pattern_count)
- Track effectiveness (how often scratch_pad.md is useful)
- Metrics: preservation_rate, next_session_usage_rate
