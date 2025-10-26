#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "model2vec>=0.3.0",
#     "semantic-router>=0.1.0",
#     "numpy>=1.24.0",
#     "rapidfuzz>=3.0.0"
# ]
# ///
"""
Contextune UserPromptSubmit Hook

Detects slash commands from natural language prompts using 3-tier cascade:
1. Keyword matching (0.02ms, 60% coverage)
2. Model2Vec embeddings (0.2ms, 30% coverage)
3. Semantic Router (50ms, 10% coverage)

Uses Claude Code headless mode for interactive prompt analysis and suggestions.

Hook Protocol:
- Input: JSON via stdin with {"prompt": "...", "session_id": "..."}
- Output: JSON via stdout with {"continue": true, "feedback": "..."}
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add lib directory to Python path
PLUGIN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

# Import matchers (now using RapidFuzz-based keyword matcher v2!)
from keyword_matcher_v2 import KeywordMatcherV2 as KeywordMatcher, IntentMatch
from model2vec_matcher import Model2VecMatcher
from semantic_router_matcher import SemanticRouterMatcher
from observability_db import ObservabilityDB


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


class ClaudeCodeHaikuEngineer:
    """
    Uses Claude Code headless mode to analyze prompts and provide interactive suggestions.

    Benefits:
    - No separate API key needed (uses existing Claude Code auth)
    - Integrated billing with Claude Code
    - Fast Haiku model for cost optimization
    - Interactive blocking mode for user feedback
    """

    def __init__(self):
        self._claude_available = None

    def is_available(self) -> bool:
        """Check if Claude Code CLI is available."""
        if self._claude_available is None:
            try:
                result = subprocess.run(
                    ["claude", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                self._claude_available = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._claude_available = False

        return self._claude_available

    def analyze_and_enhance(
        self,
        prompt: str,
        detected_command: str,
        confidence: float,
        available_commands: List[str],
        timeout: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze prompt using Claude Code headless mode and suggest enhancements.

        Args:
            prompt: User's original prompt
            detected_command: Command detected by cascade
            confidence: Detection confidence (0-1)
            available_commands: List of all available commands
            timeout: Timeout in seconds

        Returns:
            Dict with analysis results or None if unavailable/failed
        """
        if not self.is_available():
            return None

        # Build analysis prompt for Haiku
        analysis_prompt = f"""You are a prompt enhancement assistant for Contextune, a Claude Code plugin.

USER'S PROMPT: "{prompt}"

DETECTED COMMAND: {detected_command}
DETECTION CONFIDENCE: {confidence:.0%}

AVAILABLE ALTERNATIVES:
{chr(10).join(f"- {cmd}" for cmd in available_commands[:10])}

TASK: Analyze the user's prompt and provide:
1. Whether the detected command is the best match (true/false)
2. Alternative commands if better matches exist
3. A brief, helpful suggestion for the user

RESPONSE FORMAT (JSON):
{{
  "is_best_match": true/false,
  "alternatives": ["command1", "command2"],
  "suggestion": "Brief suggestion text"
}}

Be concise. Focus on actionability."""

        try:
            # Call Claude Code headless with Haiku model
            cmd = [
                "claude",
                "--model", "claude-haiku-4-5",
                "-p", analysis_prompt,
                "--output-format", "json",
                "--allowedTools", ""  # No tools needed for this analysis
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                print(f"DEBUG: Claude Code error: {result.stderr}", file=sys.stderr)
                return None

            # Parse Claude's response - it's nested in a wrapper object
            claude_response = json.loads(result.stdout)

            # Extract the actual result (may be nested in "result" field)
            if "result" in claude_response:
                result_text = claude_response["result"]
                # Result may contain JSON in markdown code blocks
                if "```json" in result_text:
                    # Extract JSON from markdown code block
                    json_start = result_text.find("```json") + 7
                    json_end = result_text.find("```", json_start)
                    result_text = result_text[json_start:json_end].strip()

                # Parse the extracted JSON
                analysis = json.loads(result_text)
                return analysis
            else:
                # If no "result" field, assume the whole response is the analysis
                return claude_response

        except subprocess.TimeoutExpired:
            print(f"DEBUG: Claude Code timeout after {timeout}s", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to parse Claude response: {e}", file=sys.stderr)
            print(f"DEBUG: Raw output: {result.stdout[:200]}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"DEBUG: Haiku engineer error: {e}", file=sys.stderr)
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
    """Write detection data to observability DB for status line to read."""
    try:
        db = ObservabilityDB(".contextune/observability.db")
        db.set_detection(
            command=match.command,
            confidence=match.confidence,
            method=match.method,
            prompt_preview=prompt[:60] + ("..." if len(prompt) > 60 else ""),
            latency_ms=match.latency_ms
        )

        # Also log matcher performance
        db.log_matcher_performance(match.method, match.latency_ms, success=True)

        print(f"DEBUG: Wrote detection to observability DB: {match.command} ({match.confidence:.0%} {match.method})", file=sys.stderr)
    except Exception as e:
        # Don't fail hook if observability write fails
        print(f"DEBUG: Failed to write to observability DB: {e}", file=sys.stderr)
        # Also log the error
        try:
            db = ObservabilityDB(".contextune/observability.db")
            db.log_error("user_prompt_submit", type(e).__name__, str(e))
        except:
            pass


def clear_detection_statusline():
    """Clear status line detection (no match found)."""
    try:
        db = ObservabilityDB(".contextune/observability.db")
        db.clear_detection()
        print(f"DEBUG: Cleared detection from observability DB", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Failed to clear detection from observability DB: {e}", file=sys.stderr)


def get_detection_count() -> int:
    """Get total number of detections for progressive tips."""
    try:
        db = ObservabilityDB(".contextune/observability.db")
        stats = db.get_stats()
        return stats.get("detections", {}).get("total", 0)
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
    # Contextune commands
    "/ctx:design": "design system architecture with structured workflow",
    "/ctx:research": "get fast answers using 3 parallel agents",
    "/ctx:plan": "create parallel development plans",
    "/ctx:execute": "run tasks in parallel worktrees",
    "/ctx:status": "monitor parallel task progress",
    "/ctx:cleanup": "clean up completed worktrees",
    "/ctx:help": "see example-first command guide",
    "/ctx:configure": "enable persistent status bar display",
    "/ctx:stats": "see your time & cost savings",
    "/ctx:verify": "verify and execute detected command with confirmation",

    # Skill-only detections (no commands)
    "skill:ctx:performance": "analyze and optimize parallel workflow performance",
    "skill:ctx:parallel-expert": "get guidance on parallelizing tasks effectively",
    "skill:ctx:help": "discover Contextune features and capabilities",
    "skill:ctx:worktree": "troubleshoot git worktree issues and conflicts",
}

# Skill mapping for reliable Claude execution
# Maps slash commands AND skill detections to skill names
# Skills are auto-discovered by Claude Code from: contextune/skills/*/SKILL.md
SKILL_MAPPING = {
    # Commands with skills
    "/ctx:design": "ctx:architect",    # Plugin skill: skills/software-architect
    "/ctx:research": "ctx:researcher", # Plugin skill: skills/researcher

    # Skills without commands (direct skill suggestions)
    "skill:ctx:performance": "ctx:performance",
    "skill:ctx:parallel-expert": "ctx:parallel-expert",
    "skill:ctx:help": "ctx:help",
    "skill:ctx:worktree": "ctx:worktree",

    # Note: /ctx:plan and /ctx:execute are commands, not skills
    # They execute workflows directly rather than providing guidance
}

def create_skill_augmented_prompt(match: IntentMatch, original_prompt: str) -> str:
    """
    Augment prompt with skill suggestion for more reliable execution.

    Evidence: Skills are invoked more reliably than slash commands because
    they use Claude's native Skill tool (structured, type-safe) vs text expansion.

    Args:
        match: Detected command and confidence
        original_prompt: User's original prompt text

    Returns:
        Augmented prompt that guides Claude to use skill or command
    """
    if match.command in SKILL_MAPPING:
        skill_name = SKILL_MAPPING[match.command]
        # Strong directive: "You can use your X skill"
        return f"{original_prompt}. You can use your {skill_name} skill to help with this task."
    else:
        # For commands without skills, use directive language
        action = COMMAND_ACTIONS.get(match.command, "complete this request")
        return f"{original_prompt}. Please use the {match.command} command to {action}."


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
        if match.command.startswith("/ctx:"):
            return "Want parallel workflows? Type `/ctx:plan` to work on multiple tasks simultaneously"
        return f"Blazing fast: {match.latency_ms:.2f}ms detection. Type `/ctx:stats` to see all metrics"

    # Power users (21+) - occasional celebration
    else:
        if detection_count % 10 == 0:  # Every 10th detection
            return f"🎉 {detection_count} detections! Type `/ctx:stats` to see your time & cost savings"
        return None  # No tip for most interactions


def load_available_commands() -> List[str]:
    """Load list of all available commands for Claude Code."""
    # Return all commands from COMMAND_ACTIONS
    return [cmd for cmd in COMMAND_ACTIONS.keys() if cmd.startswith("/")]


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


def format_interactive_suggestion(
    match: IntentMatch,
    analysis: Optional[Dict[str, Any]],
    detection_count: int = 0
) -> str:
    """
    Format interactive suggestion with Haiku analysis.

    Args:
        match: Detected command match
        analysis: Haiku analysis results (optional)
        detection_count: Total detections for contextual tips

    Returns:
        Formatted suggestion message
    """
    # Get action description
    action = COMMAND_ACTIONS.get(match.command, "execute this command")
    confidence_pct = int(match.confidence * 100)

    # Base detection message
    base_msg = f"🎯 Detected: `{match.command}` ({confidence_pct}% via {match.method})"

    # Add latency if fast
    if match.latency_ms < 1.0:
        base_msg += f"\n⚡ Detection speed: {match.latency_ms:.2f}ms"

    # Add Haiku analysis if available
    if analysis:
        if not analysis.get("is_best_match", True):
            alternatives = analysis.get("alternatives", [])
            if alternatives:
                base_msg += f"\n\n💡 Better alternatives:"
                for alt in alternatives[:3]:
                    alt_action = COMMAND_ACTIONS.get(alt, "execute this command")
                    base_msg += f"\n  • `{alt}` - {alt_action}"

        suggestion = analysis.get("suggestion")
        if suggestion:
            base_msg += f"\n\n💬 Suggestion: {suggestion}"
    else:
        # Fallback without analysis
        base_msg += f"\n\n📝 Action: Type `{match.command}` to {action}"

    # Get contextual tip
    tip = get_contextual_tip(match, detection_count)
    if tip:
        base_msg += f"\n\n💡 Tip: {tip}"

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

        print(f"DEBUG: Command detected (detection #{detection_count + 1})", file=sys.stderr)

        # Initialize Haiku engineer for interactive analysis
        engineer = ClaudeCodeHaikuEngineer()
        haiku_analysis = None

        # Try to get Haiku analysis for better suggestions
        if engineer.is_available():
            print(f"DEBUG: Running Haiku analysis...", file=sys.stderr)
            available_commands = load_available_commands()
            haiku_analysis = engineer.analyze_and_enhance(
                prompt=prompt,
                detected_command=match.command,
                confidence=match.confidence,
                available_commands=available_commands,
                timeout=30
            )
            if haiku_analysis:
                print(f"DEBUG: Haiku analysis: {json.dumps(haiku_analysis)}", file=sys.stderr)
            else:
                print(f"DEBUG: Haiku analysis failed or timed out", file=sys.stderr)
        else:
            print(f"DEBUG: Claude Code CLI not available, skipping Haiku analysis", file=sys.stderr)

        # AUGMENT MODE: Modify prompt with skill/command suggestion for reliability
        print(f"DEBUG: Augmenting prompt for Claude", file=sys.stderr)

        # Create augmented prompt with skill suggestion
        augmented_prompt = create_skill_augmented_prompt(match, prompt)

        # Format feedback with Haiku analysis (if available)
        feedback_msg = format_interactive_suggestion(match, haiku_analysis, detection_count)

        response = {
            "continue": True,
            "modifiedPrompt": augmented_prompt,  # KEY: Augmented prompt for reliable execution
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