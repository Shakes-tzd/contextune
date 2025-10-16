#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "model2vec>=0.3.0",
#     "semantic-router>=0.1.0",
#     "numpy>=1.24.0"
# ]
# ///
"""
SlashSense UserPromptSubmit Hook

Detects slash commands from natural language prompts using 3-tier cascade:
1. Keyword matching (0.02ms, 60% coverage)
2. Model2Vec embeddings (0.2ms, 30% coverage)  
3. Semantic Router (50ms, 10% coverage)

Hook Protocol:
- Input: JSON via stdin with {"prompt": "...", "session_id": "..."}
- Output: JSON via stdout with {"continue": true, "feedback": "..."}
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add lib directory to Python path
PLUGIN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

# Import your existing matchers (unchanged!)
from keyword_matcher import KeywordMatcher, IntentMatch
from model2vec_matcher import Model2VecMatcher
from semantic_router_matcher import SemanticRouterMatcher


class SlashSenseDetector:
    """
    3-tier intent detection cascade.
    
    Uses your existing matchers in order of speed:
    1. KeywordMatcher (always fast)
    2. Model2VecMatcher (if available)
    3. SemanticRouterMatcher (if API key available)
    """
    
    def __init__(self):
        self._keyword = None
        self._model2vec = None
        self._semantic = None
        
    def _get_keyword(self):
        if self._keyword is None:
            self._keyword = KeywordMatcher()
        return self._keyword
    
    def _get_model2vec(self):
        if self._model2vec is None:
            m = Model2VecMatcher()
            self._model2vec = m if m.is_available() else None
        return self._model2vec
    
    def _get_semantic(self):
        if self._semantic is None:
            m = SemanticRouterMatcher()
            self._semantic = m if m.is_available() else None
        return self._semantic
    
    def detect(self, text: str) -> Optional[IntentMatch]:
        """Detect intent using 3-tier cascade."""
        
        # Tier 1: Keyword (always available)
        result = self._get_keyword().match(text)
        if result:
            return result
        
        # Tier 2: Model2Vec
        m2v = self._get_model2vec()
        if m2v:
            result = m2v.match(text)
            if result:
                return result
        
        # Tier 3: Semantic Router
        sem = self._get_semantic()
        if sem:
            result = sem.match(text)
            if result:
                return result
        
        return None


def should_process(prompt: str) -> bool:
    """Check if prompt needs intent detection."""
    if not prompt or not prompt.strip():
        return False
    
    # Skip if already a command
    if prompt.strip().startswith("/"):
        return False
    
    # Skip if too short
    if len(prompt.strip().split()) < 3:
        return False
    
    return True


def format_suggestion(match: IntentMatch) -> str:
    """Format detection result as Claude-friendly suggestion."""
    
    confidence_label = "HIGH" if match.confidence >= 0.85 else "MEDIUM"
    
    return f"""
<slashsense_detection>
🎯 **Command Detected**: `{match.command}`

**Confidence**: {match.confidence:.0%} ({confidence_label})
**Method**: {match.method}
**Latency**: {match.latency_ms:.2f}ms

Would you like me to execute `{match.command}` instead?
</slashsense_detection>
""".strip()


def get_delegation_mode() -> str:
    """
    Get delegation mode from config.

    Returns:
        "auto" - Auto-execute high confidence matches
        "verify" - Delegate to sub-agent for verification
        "suggest" - Add context, let main agent decide
    """
    try:
        from pathlib import Path
        import json

        config_path = Path.home() / ".claude" / "plugins" / "slashsense" / "data" / "user_patterns.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("delegation_mode", "verify")
    except:
        pass

    return "verify"  # Default to safest option


def main():
    """Hook entry point."""

    try:
        # Read hook event from stdin
        event_json = sys.stdin.read()
        event = json.loads(event_json)

        prompt = event.get("prompt", "")

        # DEBUG: Log what we received
        print(f"DEBUG: SlashSense hook triggered with prompt: '{prompt}'", file=sys.stderr)

        # Check if we should process
        if not should_process(prompt):
            print(f"DEBUG: Skipping prompt (should_process=False)", file=sys.stderr)
            # Pass through unchanged
            response = {
                "continue": True,
                "suppressOutput": True
            }
            print(json.dumps(response))
            return

        print(f"DEBUG: Processing prompt (should_process=True)", file=sys.stderr)

        # Initialize detector
        detector = SlashSenseDetector()

        # Detect intent
        match = detector.detect(prompt)

        print(f"DEBUG: Detection result: {match}", file=sys.stderr)

        if match is None or match.confidence < 0.7:
            print(f"DEBUG: No match or low confidence, passing through", file=sys.stderr)
            # No match or low confidence - pass through
            response = {
                "continue": True,
                "suppressOutput": True
            }
            print(json.dumps(response))
            return

        # Get delegation mode from config
        delegation_mode = get_delegation_mode()
        print(f"DEBUG: Delegation mode: {delegation_mode}", file=sys.stderr)

        # DELEGATION MODE: Use sub-agent for verification
        if delegation_mode == "verify":
            print(f"DEBUG: Using sub-agent verification", file=sys.stderr)

            # Instruct main agent to spawn verification sub-agent
            delegation_context = f"""

⚠️ **SLASHSENSE DELEGATION DIRECTIVE** ⚠️

**ACTION REQUIRED**: Immediately spawn a sub-agent using the Task tool to handle user verification.

**Detection Summary**:
- Detected Command: `{match.command}`
- Confidence: {match.confidence:.0%}
- Method: {match.method}
- Latency: {match.latency_ms:.2f}ms
- Original Prompt: "{prompt}"

**Your Task**:
1. Use the Task tool with subagent_type="general-purpose"
2. Give the sub-agent this prompt:

```
You are a SlashSense verification agent. Present these options to the user:

🎯 **SlashSense Detection**

I detected you might want to run a slash command:

**Option 1**: Run `{match.command}` ({match.confidence:.0%} confidence)
**Option 2**: Continue with original: "{prompt[:80]}..."

Which do you prefer? (1, 2, or tell me what you want)

Then execute their choice and report back briefly.
```

3. DO NOT process the user's original prompt yourself
4. Wait for sub-agent results
5. Present sub-agent's findings to user

This preserves your context for the main conversation.
"""

            response = {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": delegation_context
                },
                "feedback": f"🎯 SlashSense: Spawning verification agent ({match.confidence:.0%} confidence)"
            }

        # AUTO MODE: High confidence auto-execute (original behavior)
        elif delegation_mode == "auto":
            print(f"DEBUG: Auto-executing command: {match.command}", file=sys.stderr)
            response = {
                "continue": True,
                "modifiedPrompt": match.command,
                "feedback": f"🎯 SlashSense: Auto-executing `{match.command}` ({match.confidence:.0%} confidence, {match.method} match)"
            }

        # SUGGEST MODE: Add context, let main agent decide
        else:  # "suggest"
            print(f"DEBUG: Suggesting to main agent", file=sys.stderr)
            response = {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"\n\n[SlashSense detected: `{match.command}` with {match.confidence:.0%} confidence via {match.method}]"
                },
                "feedback": f"💡 SlashSense: Suggested `{match.command}` ({match.confidence:.0%} confidence)"
            }

        print(f"DEBUG: Response: {json.dumps(response)}", file=sys.stderr)
        print(json.dumps(response))

    except Exception as e:
        # Log error but don't block Claude
        import traceback
        print(f"SlashSense error: {e}", file=sys.stderr)
        print(f"DEBUG: Traceback: {traceback.format_exc()}", file=sys.stderr)
        response = {
            "continue": True,
            "suppressOutput": True
        }
        print(json.dumps(response))


if __name__ == "__main__":
    main()