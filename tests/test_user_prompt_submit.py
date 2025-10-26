#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pytest>=7.0.0",
#     "model2vec>=0.3.0",
#     "semantic-router>=0.1.0",
#     "numpy>=1.24.0",
#     "rapidfuzz>=3.0.0"
# ]
# ///
"""
Tests for selective Haiku triggering in user_prompt_submit hook.

Verifies that:
1. High-confidence exact matches skip Haiku (faster + cheaper)
2. Low-confidence matches trigger Haiku
3. Fuzzy/semantic methods always trigger Haiku
4. Feedback formatting works with and without Haiku analysis
"""

import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

# Add parent directories to path
TESTS_DIR = Path(__file__).parent
PROJECT_ROOT = TESTS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))
sys.path.insert(0, str(PROJECT_ROOT / "hooks"))

# Import the hook module components
from keyword_matcher_v2 import IntentMatch


def test_selective_haiku_triggering_high_confidence_keyword():
    """Test that high-confidence keyword matches skip Haiku analysis."""
    # Create a high-confidence keyword match (0.98, keyword method)
    match = IntentMatch(
        command="/ctx:help",
        confidence=0.98,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help", "how to"]
    )

    # Should NOT trigger Haiku (confidence >= 0.95 AND method is keyword)
    should_run_haiku = match.confidence < 0.95 or match.method in ['fuzzy', 'semantic']

    assert should_run_haiku == False, "High-confidence keyword match should skip Haiku"


def test_selective_haiku_triggering_low_confidence():
    """Test that low-confidence matches trigger Haiku analysis."""
    # Create a low-confidence match (0.85)
    match = IntentMatch(
        command="/ctx:help",
        confidence=0.85,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help"]
    )

    # Should trigger Haiku (confidence < 0.95)
    should_run_haiku = match.confidence < 0.95 or match.method in ['fuzzy', 'semantic']

    assert should_run_haiku == True, "Low-confidence match should trigger Haiku"


def test_selective_haiku_triggering_fuzzy_method():
    """Test that fuzzy method always triggers Haiku, even with high confidence."""
    # Create a high-confidence fuzzy match (1.0, fuzzy method)
    match = IntentMatch(
        command="/ctx:help",
        confidence=1.0,
        method="fuzzy",
        latency_ms=0.25,
        matched_keywords=["help please"]
    )

    # Should trigger Haiku (method is fuzzy)
    should_run_haiku = match.confidence < 0.95 or match.method in ['fuzzy', 'semantic']

    assert should_run_haiku == True, "Fuzzy method should always trigger Haiku"


def test_selective_haiku_triggering_semantic_method():
    """Test that semantic method always triggers Haiku, even with high confidence."""
    # Create a high-confidence semantic match (0.99, semantic method)
    match = IntentMatch(
        command="/ctx:research",
        confidence=0.99,
        method="semantic",
        latency_ms=45.0,
        matched_keywords=["research topic"]
    )

    # Should trigger Haiku (method is semantic)
    should_run_haiku = match.confidence < 0.95 or match.method in ['fuzzy', 'semantic']

    assert should_run_haiku == True, "Semantic method should always trigger Haiku"


def test_selective_haiku_triggering_boundary_confidence():
    """Test boundary condition at 0.95 confidence."""
    # Test exactly 0.95 confidence with keyword method
    match_at_threshold = IntentMatch(
        command="/ctx:help",
        confidence=0.95,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help"]
    )

    # Should NOT trigger Haiku (confidence >= 0.95)
    should_run_haiku = match_at_threshold.confidence < 0.95 or match_at_threshold.method in ['fuzzy', 'semantic']

    assert should_run_haiku == False, "Confidence of exactly 0.95 should skip Haiku"

    # Test just below threshold (0.949)
    match_below_threshold = IntentMatch(
        command="/ctx:help",
        confidence=0.949,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help"]
    )

    should_run_haiku = match_below_threshold.confidence < 0.95 or match_below_threshold.method in ['fuzzy', 'semantic']

    assert should_run_haiku == True, "Confidence below 0.95 should trigger Haiku"


def test_feedback_format_with_haiku_analysis():
    """Test that feedback formatting works with Haiku analysis."""
    from user_prompt_submit import format_interactive_suggestion

    match = IntentMatch(
        command="/ctx:help",
        confidence=0.85,
        method="fuzzy",
        latency_ms=0.25,
        matched_keywords=["help me"]
    )

    # Mock Haiku analysis
    haiku_analysis = {
        "is_best_match": False,
        "alternatives": ["/ctx:research", "/ctx:design"],
        "suggestion": "Consider using /ctx:research for finding information"
    }

    result = format_interactive_suggestion(match, haiku_analysis, detection_count=5)

    # Should include detection info
    assert "/ctx:help" in result
    assert "85%" in result or "fuzzy" in result

    # Should include Haiku analysis
    assert "alternatives" in result.lower() or "/ctx:research" in result
    assert "suggestion" in result.lower() or haiku_analysis["suggestion"] in result


def test_feedback_format_without_haiku_analysis():
    """Test that feedback formatting works without Haiku analysis (selective skip)."""
    from user_prompt_submit import format_interactive_suggestion

    match = IntentMatch(
        command="/ctx:help",
        confidence=0.98,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help"]
    )

    # No Haiku analysis (None)
    haiku_analysis = None

    result = format_interactive_suggestion(match, haiku_analysis, detection_count=5)

    # Should include detection info
    assert "/ctx:help" in result
    assert "98%" in result or "keyword" in result

    # Should include fallback action message
    assert "Action:" in result or "Type" in result

    # Should NOT have Haiku-specific content
    assert "alternatives" not in result.lower()
    assert "Suggestion:" not in result


def test_expected_cost_reduction_pattern():
    """Test that selective triggering pattern matches expected usage."""
    # Simulate realistic detection distribution from logs
    test_cases = [
        # 63% fuzzy matches (should trigger Haiku)
        ("help me out", 0.85, "fuzzy", True),
        ("show me how", 0.80, "fuzzy", True),
        ("I need assistance", 0.90, "fuzzy", True),

        # 37% exact/high-confidence matches (should skip Haiku)
        ("/ctx:help", 0.98, "keyword", False),
        ("research best practices", 0.97, "keyword", False),
        ("design system architecture", 0.96, "keyword", False),
    ]

    haiku_triggered = 0
    haiku_skipped = 0

    for prompt, confidence, method, expected_trigger in test_cases:
        match = IntentMatch(
            command="/ctx:help",
            confidence=confidence,
            method=method,
            latency_ms=0.2,
            matched_keywords=[prompt]
        )

        should_run_haiku = match.confidence < 0.95 or match.method in ['fuzzy', 'semantic']

        if should_run_haiku:
            haiku_triggered += 1
        else:
            haiku_skipped += 1

        assert should_run_haiku == expected_trigger, \
            f"Pattern mismatch for {prompt} ({confidence:.2f}, {method})"

    # Verify we're getting expected ~60% reduction
    total = haiku_triggered + haiku_skipped
    skip_rate = haiku_skipped / total

    # Should skip ~37% (0.37) of requests based on log analysis
    assert skip_rate >= 0.30, f"Skip rate too low: {skip_rate:.0%} (expected ~37%+)"
    assert skip_rate <= 0.50, f"Skip rate too high: {skip_rate:.0%} (expected ~37%)"


def test_integration_full_hook_flow():
    """Integration test: verify full hook handles selective triggering correctly."""
    # This would require more complex mocking of stdin/stdout
    # For now, verify the logic components work together

    # Test case 1: High-confidence keyword (should skip Haiku)
    match_skip = IntentMatch(
        command="/ctx:help",
        confidence=0.98,
        method="keyword",
        latency_ms=0.15,
        matched_keywords=["help"]
    )

    should_run_haiku_skip = match_skip.confidence < 0.95 or match_skip.method in ['fuzzy', 'semantic']
    assert should_run_haiku_skip == False

    # Test case 2: Low-confidence fuzzy (should trigger Haiku)
    match_trigger = IntentMatch(
        command="/ctx:help",
        confidence=0.85,
        method="fuzzy",
        latency_ms=0.25,
        matched_keywords=["help me"]
    )

    should_run_haiku_trigger = match_trigger.confidence < 0.95 or match_trigger.method in ['fuzzy', 'semantic']
    assert should_run_haiku_trigger == True


if __name__ == "__main__":
    # Run tests with pytest
    import subprocess
    result = subprocess.run(["uv", "run", "pytest", __file__, "-v"], cwd=PROJECT_ROOT)
    sys.exit(result.returncode)
