# AskUserQuestion Integration for UserPromptSubmit Hook

**Question:** Can the UserPromptSubmit hook use AskUserQuestion to verify Haiku suggestions?

**Answer:** Yes! But indirectly - the hook instructs Claude to use AskUserQuestion.

---

## Architecture

### Hook → Claude → Tool Flow

```
┌────────────────────────────────────────────────────────┐
│ 1. User types natural language prompt                  │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ 2. UserPromptSubmit hook runs                          │
│    - Detects intent (keyword/Model2Vec/Semantic)       │
│    - Runs Haiku analysis (if confidence < 95%)         │
│    - Gets alternative suggestions                       │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ 3. Hook returns with additionalContext                 │
│    - Contains instruction for Claude to use            │
│      AskUserQuestion tool                              │
│    - Provides question text and options                │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ 4. Claude reads additionalContext                      │
│    - Sees instruction to use AskUserQuestion           │
│    - Calls AskUserQuestion tool with options           │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ 5. User sees native question UI                        │
│    - Interactive selection (not text in conversation)  │
│    - Multiple options with descriptions                │
│    - Better UX than feedback field                     │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ 6. Claude executes selected command                    │
│    - Uses SlashCommand tool OR                         │
│    - Uses Skill tool (depending on selection)          │
└────────────────────────────────────────────────────────┘
```

---

## Implementation

### Current Code (Auto-Execute)

```python
# hooks/user_prompt_submit.py (CURRENT - line ~684)

response = {
    "continue": True,
    "modifiedPrompt": f"[Contextune detected your intent and is using {best_command}]\n\n{augmented_prompt}",
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": f"\n\n{interactive_msg}\n\n[Contextune auto-executing: `{best_command}`]",
    },
}
```

**Problem:** Auto-executes without asking user.

---

### New Code (Ask User via AskUserQuestion)

```python
# hooks/user_prompt_submit.py (NEW - with AskUserQuestion)

def create_ask_user_question_instruction(
    match: IntentMatch,
    haiku_analysis: dict | None,
    prompt: str
) -> dict:
    """
    Create additionalContext that instructs Claude to use AskUserQuestion.

    Returns hook response with directive for Claude to ask user.
    """

    # Build options from Haiku analysis
    options = []

    # Option 1: Original detection
    options.append({
        "command": match.command,
        "description": f"Original detection ({match.confidence:.0%} via {match.method})",
        "confidence": match.confidence
    })

    # Option 2-4: Haiku alternatives
    if haiku_analysis and haiku_analysis.get("alternatives"):
        for alt in haiku_analysis["alternatives"][:3]:  # Max 3 alternatives
            options.append({
                "command": alt,
                "description": f"Haiku suggests this is better for: {prompt[:50]}...",
                "confidence": 0.85  # Haiku suggestions are high confidence
            })

    # Option 5: None (user wants to rephrase)
    options.append({
        "command": "none",
        "description": "None of these - let me rephrase my request",
        "confidence": 1.0
    })

    # Create instruction for Claude
    instruction = f"""
SYSTEM DIRECTIVE - SlashSense Intent Detection:

Detected intent: {match.command} (confidence: {match.confidence:.0%}, method: {match.method})

{f'Haiku analysis suggests alternatives: {haiku_analysis.get("suggestion", "")}' if haiku_analysis else ''}

ACTION REQUIRED: Use the AskUserQuestion tool to present these options to the user:

Question: "SlashSense detected your intent. Which command would you like to use?"
Header: "SlashSense"
Options:
{chr(10).join(f'  {i+1}. {opt["command"]}: {opt["description"]}' for i, opt in enumerate(options))}

After user selects:
- If they select a command: Use SlashCommand tool to execute it
- If they select "none": Acknowledge and wait for rephrased request

This provides better UX than showing text suggestions in the conversation.
"""

    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": instruction,
        }
    }


# In main() function (replace lines ~684-691):

# INTERACTIVE MODE: Ask user via AskUserQuestion
if haiku_analysis and not haiku_analysis.get("is_best_match", True):
    # Low confidence or Haiku suggests alternatives - ASK USER
    print("DEBUG: Using interactive mode - asking user via AskUserQuestion", file=sys.stderr)

    response = create_ask_user_question_instruction(match, haiku_analysis, prompt)

else:
    # High confidence - AUTO-EXECUTE
    print("DEBUG: Using auto-execute mode (high confidence)", file=sys.stderr)

    response = {
        "continue": True,
        "modifiedPrompt": f"[Contextune detected your intent and is using {best_command}]\n\n{augmented_prompt}",
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"\n\n{interactive_msg}\n\n[Contextune auto-executing: `{best_command}`]",
        },
    }

print(f"DEBUG: Response: {json.dumps(response)}", file=sys.stderr)
print(json.dumps(response))
```

---

## Configuration

Add settings to control behavior:

```json
// .claude/plugins/marketplaces/Contextune/config.json

{
  "interactive_questions": {
    "enabled": true,
    "auto_execute_threshold": 0.95,
    "ask_user_threshold": 0.70,
    "below_threshold_behavior": "show_suggestion"  // or "silent"
  }
}
```

**Logic:**
- **Confidence >= 0.95:** Auto-execute (no question)
- **0.70 <= Confidence < 0.95:** Ask user via AskUserQuestion
- **Confidence < 0.70:** Show text suggestion (current behavior)

---

## Complete Implementation

```python
# hooks/user_prompt_submit.py

import json
import os
from pathlib import Path

# Load config
def load_config() -> dict:
    """Load plugin configuration."""
    config_path = Path.home() / ".claude" / "plugins" / "marketplaces" / "Contextune" / "config.json"

    default_config = {
        "interactive_questions": {
            "enabled": True,
            "auto_execute_threshold": 0.95,
            "ask_user_threshold": 0.70,
            "below_threshold_behavior": "show_suggestion"
        }
    }

    if config_path.exists():
        with open(config_path) as f:
            user_config = json.load(f)
            # Merge with defaults
            return {**default_config, **user_config}

    return default_config


def should_ask_user(match: IntentMatch, haiku_analysis: dict | None, config: dict) -> bool:
    """Determine if we should ask user via AskUserQuestion."""

    if not config["interactive_questions"]["enabled"]:
        return False

    confidence = match.confidence
    auto_threshold = config["interactive_questions"]["auto_execute_threshold"]
    ask_threshold = config["interactive_questions"]["ask_user_threshold"]

    # High confidence: auto-execute
    if confidence >= auto_threshold:
        return False

    # Medium confidence: ask user
    if confidence >= ask_threshold:
        return True

    # Low confidence: just show suggestion (don't ask)
    return False


def create_ask_user_question_instruction(
    match: IntentMatch,
    haiku_analysis: dict | None,
    prompt: str
) -> dict:
    """
    Create additionalContext that instructs Claude to use AskUserQuestion.
    """

    # Build options
    options = []

    # Add original detection
    action = COMMAND_ACTIONS.get(match.command, "execute this command")
    options.append({
        "label": match.command,
        "description": f"{action} (detected: {match.confidence:.0%} {match.method})"
    })

    # Add Haiku alternatives
    if haiku_analysis and haiku_analysis.get("alternatives"):
        for alt_cmd in haiku_analysis["alternatives"][:2]:  # Max 2 alternatives
            alt_action = COMMAND_ACTIONS.get(alt_cmd, "execute command")
            options.append({
                "label": alt_cmd,
                "description": f"{alt_action} (Haiku suggestion)"
            })

    # Add "none" option
    options.append({
        "label": "None",
        "description": "None of these - let me rephrase my request"
    })

    # Create instruction with exact JSON structure Claude should use
    instruction = f"""
SYSTEM DIRECTIVE - SlashSense Intent Detection:

The user's prompt was: "{prompt[:100]}{'...' if len(prompt) > 100 else ''}"

SlashSense detected: {match.command} ({match.confidence:.0%} via {match.method})
{f'Haiku analysis: {haiku_analysis.get("suggestion", "")}' if haiku_analysis else ''}

YOU MUST use the AskUserQuestion tool RIGHT NOW to present options to the user.

Use this exact structure:

{{
  "questions": [{{
    "question": "SlashSense detected your intent. Which command would you like to use?",
    "header": "SlashSense",
    "multiSelect": false,
    "options": {json.dumps(options, indent=6)}
  }}]
}}

After user responds:
- If they select a slash command: Use SlashCommand tool to execute it
- If they select "None": Say "No problem! Please rephrase your request."

DO NOT respond to the user's original prompt until after they've selected an option.
"""

    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": instruction,
        }
    }


# In main() function (replace decision logic):

# Load configuration
config = load_config()

# Determine behavior based on confidence and config
if should_ask_user(match, haiku_analysis, config):
    # INTERACTIVE MODE: Ask user via AskUserQuestion
    print(
        f"DEBUG: Asking user (confidence={match.confidence:.2f}, threshold={config['interactive_questions']['ask_user_threshold']})",
        file=sys.stderr
    )

    response = create_ask_user_question_instruction(match, haiku_analysis, prompt)

elif match.confidence >= config["interactive_questions"]["auto_execute_threshold"]:
    # AUTO-EXECUTE MODE: High confidence
    print(
        f"DEBUG: Auto-executing (confidence={match.confidence:.2f} >= {config['interactive_questions']['auto_execute_threshold']})",
        file=sys.stderr
    )

    response = {
        "continue": True,
        "modifiedPrompt": f"[Contextune detected your intent and is using {best_command}]\n\n{augmented_prompt}",
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"\n\n{interactive_msg}\n\n[Contextune auto-executing: `{best_command}`]",
        },
    }

else:
    # SUGGESTION MODE: Low confidence, just show suggestion
    print(
        f"DEBUG: Showing suggestion only (confidence={match.confidence:.2f} < {config['interactive_questions']['ask_user_threshold']})",
        file=sys.stderr
    )

    response = {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"\n\n{interactive_msg}\n\nType `{match.command}` to execute, or rephrase your request.",
        },
    }

print(f"DEBUG: Response: {json.dumps(response)}", file=sys.stderr)
print(json.dumps(response))
```

---

## Testing

### Test 1: High Confidence (Auto-Execute)

```bash
# User prompt: "research testing"
# Detection: /ctx:research (confidence: 0.98, method: keyword)

# Expected: Auto-execute, no question
# Output: [Contextune auto-executing: `/ctx:research`]
```

### Test 2: Medium Confidence (Ask User)

```bash
# User prompt: "can you help me with testing"
# Detection: /ctx:help (confidence: 0.85, method: fuzzy)
# Haiku suggests: /ctx:research might be better

# Expected: AskUserQuestion pops up
# Options:
#   1. /ctx:help: see example-first command guide (detected: 85% fuzzy)
#   2. /ctx:research: get fast answers using 3 parallel agents (Haiku suggestion)
#   3. None: None of these - let me rephrase my request
```

### Test 3: Low Confidence (Suggestion Only)

```bash
# User prompt: "what should I do"
# Detection: /ctx:help (confidence: 0.65, method: semantic)

# Expected: Text suggestion, no question
# Output: 💡 Type `/ctx:help` to see example-first command guide (65% semantic)
```

---

## Benefits

### UX Improvements

**Before (Current):**
- Text suggestion in conversation
- User must manually type command
- Clutters conversation history

**After (With AskUserQuestion):**
- Native UI question dialog
- User clicks to select
- Clean conversation
- Faster interaction

### Cost Optimization

**Selective Questioning:**
- High confidence (95%+): Auto-execute (no overhead)
- Medium confidence (70-95%): Ask user (better UX)
- Low confidence (<70%): Suggestion only (fallback)

**Result:** Only ask when it matters!

### User Control

**Configuration:**
```json
{
  "interactive_questions": {
    "enabled": true,  // Turn on/off globally
    "auto_execute_threshold": 0.95,  // Adjust sensitivity
    "ask_user_threshold": 0.70  // Control when to ask
  }
}
```

---

## Migration Path

### Phase 1: Add Feature (Opt-In)

```json
{
  "interactive_questions": {
    "enabled": false  // Disabled by default
  }
}
```

- Deploy code
- Test with beta users
- Gather feedback

### Phase 2: Enable by Default

```json
{
  "interactive_questions": {
    "enabled": true  // Default on
  }
}
```

- Enable for all users
- Monitor metrics
- Adjust thresholds

### Phase 3: Remove Old Feedback

```python
# Once AskUserQuestion is proven reliable:
# - Remove text-based feedback for medium confidence
# - Only use for low confidence cases
# - Simplify code
```

---

## Comparison to SlashCommand Tool

### AskUserQuestion Approach (Recommended)

**Pros:**
- User gets to choose (better UX)
- Works for any confidence level
- Can present multiple alternatives
- User feels in control

**Cons:**
- Requires user interaction
- Adds one click to workflow

### SlashCommand Auto-Execute (Alternative)

**Pros:**
- Instant execution (no user interaction)
- Faster workflow

**Cons:**
- No user verification
- Could execute wrong command
- User might not understand what happened

### Hybrid Approach (Best)

```
Confidence >= 95%: Auto-execute via SlashCommand
70% <= Confidence < 95%: Ask via AskUserQuestion
Confidence < 70%: Show text suggestion
```

This gives speed + safety + flexibility!

---

## Implementation Checklist

- [ ] Add `config.json` with interactive_questions settings
- [ ] Implement `load_config()` function
- [ ] Implement `should_ask_user()` logic
- [ ] Implement `create_ask_user_question_instruction()`
- [ ] Update main() function with 3-way decision
- [ ] Test all 3 scenarios (high/medium/low confidence)
- [ ] Add logging to observability DB
- [ ] Update documentation
- [ ] Create user guide
- [ ] Beta test with 10 users
- [ ] Gather feedback and adjust thresholds
- [ ] Roll out to all users

---

## Success Metrics

### Quantitative

- **Question response rate:** Target > 90%
- **User satisfaction:** Target > 4.5/5
- **Command execution rate:** Maintain >= 85%
- **Time to execution:** Target < 3 seconds

### Qualitative

- User feedback surveys
- Support ticket reduction
- Feature adoption rate
- Complaint rate (false positives)

---

## Conclusion

**Yes!** The UserPromptSubmit hook can use AskUserQuestion to verify Haiku suggestions by:

1. **Detecting intent** (3-tier cascade)
2. **Running Haiku analysis** (for medium confidence)
3. **Instructing Claude** to use AskUserQuestion (via additionalContext)
4. **Presenting options** to user (native UI)
5. **Executing selection** (via SlashCommand tool)

This approach combines:
- ✅ Speed (auto-execute high confidence)
- ✅ Safety (ask user for medium confidence)
- ✅ Flexibility (show suggestion for low confidence)
- ✅ Great UX (native UI, not text clutter)

**Recommended:** Implement hybrid approach with configurable thresholds.

---

**Next Steps:**
1. Implement configuration system
2. Add `should_ask_user()` logic
3. Test with real prompts
4. Adjust thresholds based on data
5. Roll out gradually (beta → all users)
