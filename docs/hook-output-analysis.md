# Hook Output Mechanisms: Context Cost Analysis

## Executive Summary

**Key Finding**: Use `feedback` for UI messages (zero context cost), `additionalContext` for persistent knowledge (token cost).

## Context Cost Breakdown

### 1. `feedback` Field
- **Context Cost**: **ZERO tokens** ✅
- **Behavior**: User-visible message in UI
- **Use Case**: Display information, suggestions, status updates
- **Example Token Cost**: 0 tokens (not added to Claude's context)

```json
{
  "continue": true,
  "feedback": "💡 Contextune: 50 commands available. Type naturally!",
  "suppressOutput": false
}
```

### 2. `additionalContext` Field
- **Context Cost**: **Full token count** ⚠️
- **Behavior**: Added to Claude's conversation context
- **Use Case**: Persistent knowledge, configuration, project state
- **Example Token Cost**: ~100-500 tokens for typical config block

```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "[Contextune config: 50 custom patterns, min confidence 0.7]"
  },
  "suppressOutput": true
}
```

### 3. `suppressOutput` Field
- **Context Cost**: **ZERO tokens** ✅
- **Behavior**: Hide from transcript view (Ctrl-R)
- **Use Case**: Reduce noise in transcript mode
- **Note**: Does NOT affect whether content goes to Claude

```json
{
  "continue": true,
  "feedback": "Internal diagnostic: Hook executed in 2ms",
  "suppressOutput": true  // Hidden from transcript, but not added to context anyway
}
```

## Zero-Context Pattern

**Pattern**: Show information to users WITHOUT consuming context tokens

```json
{
  "continue": true,
  "feedback": "Your user-facing message here (any length, any format)",
  "suppressOutput": false
  // NOTE: NO hookSpecificOutput = zero context cost
}
```

**Use Cases**:
- Command lists at session start
- Status notifications
- UI hints and tips
- Non-critical information

**Performance**: Zero token overhead, instant display

## Context-Injection Pattern

**Pattern**: Add persistent knowledge to Claude's context

```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Persistent knowledge Claude should remember"
  },
  "feedback": "Optional UI message (can be different from context)",
  "suppressOutput": true
}
```

**Use Cases**:
- Project configuration
- Custom patterns/rules
- Session-specific state
- Critical context Claude needs

**Performance**: Costs tokens equal to text length (~4 chars per token)

## Multi-Hook Coordination

### Sequential Hook Execution

When multiple SessionStart hooks are registered:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [
        {"command": "hook1.js"},  // Runs first
        {"command": "hook2.js"}   // Runs second
      ]
    }]
  }
}
```

### Context Combination Rules

1. **Multiple `additionalContext`**: Concatenated in order
2. **Multiple `feedback`**: Only last one shown (currently a bug - may change)
3. **`suppressOutput`**: Each hook controls its own output

**Best Practice**: Use ONE hook for context injection, separate hooks for UI feedback

## Implementation Guide

### Contextune SessionStart Hook (Zero-Context)

```javascript
#!/usr/bin/env node

function main() {
  try {
    // Load commands from commands/ directory
    const commands = getContextuneCommands();

    // Format as user-friendly list
    const message = formatCommandList(commands);

    // ZERO-CONTEXT PATTERN
    const output = {
      continue: true,
      feedback: message,           // User sees this (no context cost)
      suppressOutput: false         // Visible in transcript
      // NO additionalContext = NO TOKENS CONSUMED
    };

    console.log(JSON.stringify(output));
    process.exit(0);

  } catch (err) {
    // Fail silently - don't block session
    console.error('Hook error:', err.message);
    process.exit(0);
  }
}
```

### Performance Comparison

| Pattern | Token Cost | Latency | Use Case |
|---------|-----------|---------|----------|
| Zero-context (feedback only) | 0 tokens | <1ms | Command lists, UI hints |
| Context injection (additionalContext) | ~100-500 tokens | <1ms | Config, persistent state |
| Both (feedback + context) | ~100-500 tokens | <1ms | Show AND remember |

### Example: Contextune Command List

**Zero-Context Approach** (Recommended):
```json
{
  "continue": true,
  "feedback": "💡 Contextune Commands:\n  /contextune:config\n  /contextune:stats\n\nOr type naturally!",
  "suppressOutput": false
}
```
- Token cost: 0
- User sees full list
- Claude doesn't "know" about commands (but will detect them via intent matching)

**Context-Injection Approach** (Only if Claude needs to know):
```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "[Available commands: /contextune:config, /contextune:stats]"
  },
  "feedback": "💡 Contextune loaded",
  "suppressOutput": true
}
```
- Token cost: ~20 tokens
- User sees brief message
- Claude "knows" about commands in context

## Decision Framework

### Use `feedback` (Zero-Context) When:
- ✅ Showing UI information
- ✅ Listing available commands
- ✅ Displaying status/diagnostics
- ✅ Providing hints/tips
- ✅ Non-critical information

### Use `additionalContext` (With Tokens) When:
- ✅ Claude needs persistent knowledge
- ✅ Configuration affects behavior
- ✅ Project state is critical
- ✅ Custom rules/patterns defined
- ✅ Session-specific context required

### Use Both When:
- ✅ User and Claude need different information
- ✅ Showing summary to user, details to Claude
- ✅ UI feedback + context injection

## Known Issues

### Bug: additionalContext Visibility (Issue #9455)

**Expected**: `additionalContext` should be hidden from user, only added to Claude's context

**Actual**: Sometimes shown to user at session start

**Workaround**: Use `suppressOutput: true` to minimize visibility

**Status**: Under investigation by Anthropic

## Recommendations for Contextune

### Session Start: Zero-Context Pattern
```javascript
// Show command list WITHOUT context cost
{
  "continue": true,
  "feedback": "💡 Contextune ready! Type naturally or use:\n  /contextune:config\n  /contextune:stats",
  "suppressOutput": false
}
```

### User Prompt Submit: Context Injection Pattern
```javascript
// Add matched command to Claude's context
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[Contextune detected: /sc:analyze with 95% confidence]"
  },
  "feedback": "💡 Suggested: /sc:analyze",
  "suppressOutput": false
}
```

## Token Cost Examples

### Minimal Context (20 tokens)
```
[Contextune: 10 commands available]
```

### Medium Context (100 tokens)
```
[Contextune Configuration]
- Custom patterns: 5 commands
- Detection: keyword + Model2Vec
- Min confidence: 0.7
```

### Large Context (500 tokens)
```
[Contextune Configuration]

Custom Patterns:
  /sc:analyze: code review, analyze, check quality, review code
  /sc:implement: build feature, create component, add functionality
  ...

Detection Settings:
  - Min confidence: 0.7
  - Enabled tiers: keyword, model2vec, semantic
  - Fallback: ask user if confidence < 0.5

Recent Usage:
  - /sc:analyze: 15 times (95% accuracy)
  - /sc:implement: 8 times (90% accuracy)
```

## Conclusion

**Use `feedback` for UI, `additionalContext` for knowledge.**

For Contextune:
- **SessionStart**: Use zero-context pattern (feedback only)
- **UserPromptSubmit**: Use context injection (detected command)
- **Total cost**: ~20 tokens per matched command (acceptable)

This keeps token usage minimal while providing excellent UX.
