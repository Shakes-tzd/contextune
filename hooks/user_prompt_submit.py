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
Contextune UserPromptSubmit Hook

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
from datetime import datetime

# Add lib directory to Python path
PLUGIN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

# Import your existing matchers (unchanged!)
from keyword_matcher import KeywordMatcher, IntentMatch
from model2vec_matcher import Model2VecMatcher
from semantic_router_matcher import SemanticRouterMatcher


class ContextuneDetector:
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


def write_detection_for_statusline(match: IntentMatch, prompt: str):
    """Write detection data to file for status line to read."""
    try:
        # Create .contextune directory in current working directory
        contextune_dir = Path(".contextune")
        contextune_dir.mkdir(exist_ok=True)

        detection_file = contextune_dir / "last_detection"

        # Write detection with timestamp
        detection_data = {
            "command": match.command,
            "confidence": round(match.confidence, 2),
            "method": match.method,
            "latency_ms": round(match.latency_ms, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_preview": prompt[:60] + ("..." if len(prompt) > 60 else "")
        }

        with open(detection_file, "w") as f:
            json.dump(detection_data, f, indent=2)

        print(f"DEBUG: Wrote detection to {detection_file}", file=sys.stderr)
    except Exception as e:
        # Don't fail hook if statusline write fails
        print(f"DEBUG: Failed to write statusline file: {e}", file=sys.stderr)


def clear_detection_statusline():
    """Clear status line detection (no match found)."""
    try:
        detection_file = Path(".contextune/last_detection")
        if detection_file.exists():
            detection_file.unlink()
            print(f"DEBUG: Cleared detection file", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Failed to clear statusline file: {e}", file=sys.stderr)


def get_detection_count() -> int:
    """Get total number of detections for progressive tips."""
    try:
        stats_file = Path.home() / ".claude" / "plugins" / "contextune" / "data" / "detection_stats.json"
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)
                return stats.get("total_detections", 0)
    except:
        pass
    return 0


def increment_detection_count():
    """Increment detection counter for progressive disclosure."""
    try:
        data_dir = Path.home() / ".claude" / "plugins" / "contextune" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        stats_file = data_dir / "detection_stats.json"

        stats = {"total_detections": 0, "by_method": {}, "by_command": {}}
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)

        stats["total_detections"] = stats.get("total_detections", 0) + 1

        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
    except:
        pass  # Don't fail hook if stats tracking fails


# Command action descriptions for directive feedback
COMMAND_ACTIONS = {
    # SuperClaude commands
    "/sc:analyze": "analyze code quality, security & performance",
    "/sc:test": "run tests with comprehensive reports",
    "/sc:implement": "implement features with expert guidance",
    "/sc:improve": "optimize code quality & performance",
    "/sc:troubleshoot": "diagnose and fix issues",
    "/sc:explain": "get clear code explanations",
    "/sc:design": "design system architecture",
    "/sc:git": "commit with smart messages",
    "/sc:build": "build and package your project",
    "/sc:cleanup": "clean up code and remove dead code",

    # Contextune commands
    "/ctx:research": "get fast answers using 3 parallel agents",
    "/ctx:plan": "create parallel development plans",
    "/ctx:execute": "run tasks in parallel worktrees",
    "/ctx:status": "monitor parallel task progress",
    "/ctx:cleanup": "clean up completed worktrees",
    "/ctx:help": "see example-first command guide",
    "/ctx:configure": "enable persistent status bar display",
    "/ctx:stats": "see your time & cost savings",
}


def get_contextual_tip(match: IntentMatch, detection_count: int) -> str:
    """Generate directive contextual tip based on usage patterns."""

    # First-time users (1-3 detections)
    if detection_count <= 3:
        return "New user? Type `/ctx:help` to see all commands with examples"

    # Early users (4-10 detections) - promote status bar
    elif detection_count <= 10:
        return "Enable persistent detection: Type `/ctx:configure` to set up status bar"

    # Experienced users (11-20) - promote advanced features
    elif detection_count <= 20:
        if match.command.startswith("/sc:"):
            return "Want parallel workflows? Type `/ctx:plan` to work on multiple tasks simultaneously"
        return f"Blazing fast: {match.latency_ms:.2f}ms detection. Type `/ctx:stats` to see all metrics"

    # Power users (21+) - occasional celebration
    else:
        if detection_count % 10 == 0:  # Every 10th detection
            return f"🎉 {detection_count} detections! Type `/ctx:stats` to see your time & cost savings"
        return None  # No tip for most interactions


def format_suggestion(match: IntentMatch, detection_count: int = 0) -> str:
    """Format detection with directive, actionable phrasing."""

    # Get action description
    action = COMMAND_ACTIONS.get(match.command, "execute this command")

    # Build directive message
    confidence_pct = int(match.confidence * 100)

    # Primary directive message
    base_msg = f"💡 Type `{match.command}` to {action} ({confidence_pct}% {match.method}"

    # Add latency if fast (show performance)
    if match.latency_ms < 1.0:
        base_msg += f", {match.latency_ms:.2f}ms"

    base_msg += ")"

    # Get contextual tip
    tip = get_contextual_tip(match, detection_count)

    if tip:
        return f"{base_msg}\n💡 {tip}"

    return base_msg


def main():
    """Hook entry point."""

    try:
        # Read hook event from stdin
        event_json = sys.stdin.read()
        event = json.loads(event_json)

        prompt = event.get("prompt", "")

        # DEBUG: Log what we received
        print(f"DEBUG: Contextune hook triggered with prompt: '{prompt}'", file=sys.stderr)

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
        detector = ContextuneDetector()

        # Detect intent
        match = detector.detect(prompt)

        print(f"DEBUG: Detection result: {match}", file=sys.stderr)

        if match is None or match.confidence < 0.7:
            print(f"DEBUG: No match or low confidence, passing through", file=sys.stderr)
            # Clear status line detection (no match)
            clear_detection_statusline()
            # No match or low confidence - pass through
            response = {
                "continue": True,
                "suppressOutput": True
            }
            print(json.dumps(response))
            return

        # Write detection for status line
        write_detection_for_statusline(match, prompt)

        # Get current detection count for progressive tips
        detection_count = get_detection_count()

        # Increment counter
        increment_detection_count()

        # SUGGEST MODE: Add context, let Claude decide
        print(f"DEBUG: Suggesting command to Claude (detection #{detection_count + 1})", file=sys.stderr)

        # Format feedback with contextual tips
        feedback_msg = format_suggestion(match, detection_count)

        response = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"\n\n[Contextune detected: `{match.command}` with {match.confidence:.0%} confidence via {match.method}]"
            },
            "feedback": feedback_msg
        }

        print(f"DEBUG: Response: {json.dumps(response)}", file=sys.stderr)
        print(json.dumps(response))

    except Exception as e:
        # Log error but don't block Claude
        import traceback
        print(f"Contextune error: {e}", file=sys.stderr)
        print(f"DEBUG: Traceback: {traceback.format_exc()}", file=sys.stderr)
        response = {
            "continue": True,
            "suppressOutput": True
        }
        print(json.dumps(response))


if __name__ == "__main__":
    main()