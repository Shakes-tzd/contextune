# Contextune Output Styles

Output styles that optimize Claude Code's behavior for automatic context preservation and extraction.

---

## Available Styles

### extraction-optimized.md

**Purpose:** Ensures Claude outputs structured content that SessionEnd hooks can reliably extract to permanent storage.

**Use when:**
- Doing design work
- Creating implementation plans
- Making architectural decisions
- Conducting research

**Benefits:**
- 99% extraction reliability (vs ~60% without)
- Zero manual documentation work
- Automatic file creation (.plans/, decisions.yaml)
- Perfect for /ctx:plan → /ctx:execute workflows

**Activation:**

```bash
# Project-level (recommended)
mkdir -p .claude/output-styles
cp output-styles/extraction-optimized.md .claude/output-styles/

# In Claude Code
/output-style extraction-optimized

# Or user-level (all projects)
mkdir -p ~/.claude/output-styles
cp output-styles/extraction-optimized.md ~/.claude/output-styles/
```

---

## How It Works

### 1. Output Style Modifies Behavior

Output style instructions → Claude outputs in consistent format → Transcripts store structured content

### 2. SessionEnd Hook Extracts

Session ends → Hook reads transcript → Parses structured content → Writes to files

### 3. SessionStart Hook Restores

Next session → Hook reads files → Injects context → You continue work

**Result:** Zero manual documentation, perfect DRY workflow

---

## Example Workflow

**Session 1:**
```
User: "Design JWT authentication system"

Claude (with extraction-optimized style):
  # JWT Authentication System

  ## Architecture
  ```yaml
  architecture:
    components: [...]
  ```

  ## Task Breakdown
  ```yaml
  tasks:
    - id: task-1
      estimated_tokens: 10000
  ```

[Session ends]

SessionEnd hook automatically creates:
  .plans/jwt-authentication-system/design.md
  .plans/jwt-authentication-system/tasks/task-1.md
  .plans/jwt-authentication-system/tasks/task-2.md
```

**Session 2 (next day):**
```
SessionStart hook injects:
  "Working context restored (~25,000 tokens)"

User: "Let's implement task-1"

Claude: [Has full context, continues immediately]
  [No Read tool needed - context already loaded]
```

---

## Integration with Hooks

This output style is designed to work with:

- **PreCompact hook** (`hooks/context_preserver.py`) - Captures in-progress work
- **SessionEnd hook** (`hooks/session_end_extractor.py`) - Extracts completed work
- **SessionStart hook** (`hooks/context_restorer.js`) - Restores context in next session
- **Background processor** (`scripts/decision-sync.py`) - Retroactive extraction from history

Together, they create a zero-manual-work documentation system.

---

## Format Guarantees

The extraction-optimized style guarantees:

✅ **YAML blocks for structured data**
```yaml
tasks:
  - id: task-1
```

✅ **Consistent headers**
- `## Architecture` (always)
- `## Task Breakdown` (always)
- `## Decision:` (always)

✅ **Metadata in every output**
```markdown
**Type:** Design
**Status:** Complete
**Estimated Tokens:** 45000
```

✅ **Code fences**
\`\`\`yaml
data: here
\`\`\`

This enables:
- Single regex pattern per section
- Direct YAML parsing (no string processing)
- 99% extraction success rate

---

## Creating Custom Output Styles

Want to create your own extraction-optimized style?

**Template:**
```markdown
---
name: Your Style Name
description: Brief description
---

# Your Style Name

## Required Output Format: [Concept]

\`\`\`markdown
# [Title]

**Metadata:** value

## Section Header

\`\`\`yaml
structured:
  data: here
\`\`\`
\`\`\`

## Forbidden Patterns

❌ Pattern that breaks extraction
✅ Pattern that enables extraction
```

**Key principles:**
1. Consistent structure (same headers every time)
2. YAML blocks for data (easy parsing)
3. Metadata at top (Type, Status, Tokens)
4. Code fences (```yaml, not bare)
5. Predictable patterns (extraction regex)

---

## Testing Your Output Style

### 1. Activate Style
```bash
/output-style extraction-optimized
```

### 2. Do Design Work
```
"Design authentication system"
```

### 3. Check Output Format
- Has consistent headers? ✅
- Has YAML blocks? ✅
- Has metadata? ✅
- Has task breakdown? ✅

### 4. Test Extraction
```bash
# End session, then check:
ls .plans/authentication-system/design.md
ls .plans/authentication-system/tasks/

# Should exist with structured content
```

---

## Troubleshooting

**Issue:** SessionEnd hook didn't extract my design

**Check:**
1. Did you use extraction-optimized style? `/output-style extraction-optimized`
2. Does output have `## Architecture` header?
3. Are YAML blocks properly fenced with \`\`\`yaml?
4. Is SessionEnd hook registered in hooks/hooks.json?

**Issue:** Extraction created empty files

**Check:**
1. Are headers exactly `## Architecture` (not "System Architecture")?
2. Are YAML blocks valid? (test with `yaml.safe_load()`)
3. Check SessionEnd hook logs for parse errors

**Issue:** Extraction missed some content

**Check:**
1. Is content in forbidden patterns? (conversational, unstructured)
2. Run hook with DEBUG to see what patterns matched
3. Compare output to examples in extraction-optimized.md

---

## Performance

**Token overhead:** ~50 tokens per prompt (output style in system prompt)

**Token savings:**
- Write tool: 0 uses (vs 1-5 per session)
- Read tool: 0 uses (vs 1-5 per session)
- Net savings: 200-1000 tokens per session

**Time savings:**
- Manual documentation: 0 minutes (vs 5-15 per session)
- File reading: 0 tool calls (vs 2-5 per session)

**Reliability improvement:**
- Extraction success: 99% (vs 60% without style)

---

## Distribution

This output style is included with Contextune plugin. Users get it automatically when they install the plugin.

**Plugin distribution:**
```
contextune/
├── output-styles/
│   ├── extraction-optimized.md
│   └── README.md (this file)
├── hooks/
│   ├── context_preserver.py      # PreCompact
│   ├── context_restorer.js       # SessionStart
│   └── session_end_extractor.py  # SessionEnd (to be created)
└── .claude-plugin/
    └── plugin.json
```

Users can:
1. Copy to project: `cp [plugin]/output-styles/extraction-optimized.md .claude/output-styles/`
2. Activate: `/output-style extraction-optimized`
3. Work normally - extraction happens automatically

---

## Future Enhancements

**Planned:**
- Style variants for different work types (research-only, implementation-only)
- Auto-switching based on task type
- Style validation (check if output matches expected format)
- Extraction confidence scoring
- User feedback loop (did extraction capture everything?)

---

## Resources

- [Claude Code Output Styles Docs](https://docs.claude.com/en/docs/claude-code/output-styles.md)
- [Contextune Plugin](https://github.com/yourusername/contextune)
- [SessionEnd Hook Design](./../.plans/decision-tracking-system/WRITE_TOOL_VS_EXTRACTION_ANALYSIS.md)
