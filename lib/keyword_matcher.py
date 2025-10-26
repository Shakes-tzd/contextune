#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Keyword-based intent matcher for SuperClaude command detection.

This module provides fast, regex-based matching of user input to SuperClaude
commands using keyword patterns. Designed for <1ms latency per query.

Performance target: <1ms per query
Method: Compiled regex patterns with early termination
Confidence: Fixed at 0.85 for all keyword matches
"""

import re
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


@dataclass
class IntentMatch:
    """Result of intent matching operation."""

    command: str          # e.g., "/ctx:design"
    confidence: float     # 0.0-1.0
    method: str          # "keyword"
    latency_ms: float    # Actual execution time
    matched_patterns: List[str]  # Patterns that matched


class KeywordMatcher:
    """
    Fast keyword-based intent matcher using compiled regex patterns.

    Matches user input against predefined keyword patterns for each
    SuperClaude command. Returns the first match found with confidence 0.85.

    Example:
        >>> matcher = KeywordMatcher()
        >>> result = matcher.match("design a caching system")
        >>> result.command
        '/ctx:design'
        >>> result.confidence
        0.85
    """

    # Command patterns: (command, compiled_regex, pattern_description, confidence)
    COMMAND_PATTERNS: List[Tuple[str, re.Pattern, str, float]] = []

    def __init__(self):
        """Initialize the keyword matcher with compiled regex patterns."""
        if not KeywordMatcher.COMMAND_PATTERNS:
            KeywordMatcher._compile_patterns()

    @staticmethod
    def _compile_patterns():
        """Load and compile regex patterns from intent_mappings.json."""
        import json
        import os

        # Find the JSON file (relative to this script or absolute)
        json_path = os.path.join(os.path.dirname(__file__), '../data/intent_mappings.json')
        if not os.path.exists(json_path):
            json_path = 'data/intent_mappings.json'  # Fallback

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Load patterns from JSON
            for command, config in data.get('commands', {}).items():
                # Get regex patterns if they exist
                if 'patterns' in config:
                    for pattern_entry in config['patterns']:
                        # Support both [pattern, confidence] and plain string patterns
                        if isinstance(pattern_entry, list):
                            pattern_str, confidence = pattern_entry
                        else:
                            pattern_str = pattern_entry
                            confidence = 0.85  # Default confidence

                        compiled = re.compile(pattern_str, re.IGNORECASE)
                        KeywordMatcher.COMMAND_PATTERNS.append(
                            (command, compiled, pattern_str, confidence)
                        )

                # Also load keywords and convert to simple patterns
                if 'keywords' in config:
                    for keyword in config['keywords']:
                        # Convert keyword to word boundary pattern
                        # e.g., "design" -> r'\bdesign\b'
                        pattern_str = r'\b' + re.escape(keyword) + r'\b'
                        confidence = 0.85  # Default confidence for keywords

                        compiled = re.compile(pattern_str, re.IGNORECASE)
                        KeywordMatcher.COMMAND_PATTERNS.append(
                            (command, compiled, keyword, confidence)
                        )

            # Load skill patterns and keywords (separate section)
            for skill, config in data.get('skills', {}).items():
                if 'patterns' in config:
                    for pattern_entry in config['patterns']:
                        # Support both [pattern, confidence] and plain string patterns
                        if isinstance(pattern_entry, list):
                            pattern_str, confidence = pattern_entry
                        else:
                            pattern_str = pattern_entry
                            confidence = 0.85  # Default confidence

                        compiled = re.compile(pattern_str, re.IGNORECASE)
                        KeywordMatcher.COMMAND_PATTERNS.append(
                            (skill, compiled, pattern_str, confidence)
                        )

                # Also load skill keywords
                if 'keywords' in config:
                    for keyword in config['keywords']:
                        pattern_str = r'\b' + re.escape(keyword) + r'\b'
                        confidence = 0.85

                        compiled = re.compile(pattern_str, re.IGNORECASE)
                        KeywordMatcher.COMMAND_PATTERNS.append(
                            (skill, compiled, keyword, confidence)
                        )

        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Fallback: use minimal built-in patterns
            print(f"Warning: Could not load patterns from JSON: {e}", file=sys.stderr)
            print("Using fallback patterns", file=sys.stderr)

            # Minimal fallback patterns
            fallback = {
                '/ctx:design': [r'\bdesign\b', r'\barchitect\b'],
                '/ctx:research': [r'\bresearch\b', r'\binvestigate\b'],
            }

            for command, pattern_list in fallback.items():
                for pattern_str in pattern_list:
                    compiled = re.compile(pattern_str, re.IGNORECASE)
                    KeywordMatcher.COMMAND_PATTERNS.append(
                        (command, compiled, pattern_str, 0.85)
                    )

    def match(self, text: str) -> Optional[IntentMatch]:
        """
        Match input text against command patterns.

        Args:
            text: User input text to match against patterns

        Returns:
            IntentMatch if a pattern matches, None otherwise

        Performance:
            Uses early termination - returns on first match
            Target latency: <1ms per query
        """
        start_time = time.perf_counter()

        if not text or not isinstance(text, str):
            return None

        # Check each pattern until first match
        for command, pattern, pattern_str, confidence in self.COMMAND_PATTERNS:
            if pattern.search(text):
                latency_ms = (time.perf_counter() - start_time) * 1000
                return IntentMatch(
                    command=command,
                    confidence=confidence,
                    method="keyword",
                    latency_ms=latency_ms,
                    matched_patterns=[pattern_str]
                )

        # No match found
        return None


# =============================================================================
# Unit Tests
# =============================================================================

if __name__ == '__main__':
    import sys

    def test_basic_matches():
        """Test basic keyword matching for each command."""
        matcher = KeywordMatcher()

        test_cases = [
            ("design the architecture", "/ctx:design"),
            ("architect the API", "/ctx:design"),
            ("research best libraries", "/ctx:research"),
            ("investigate options", "/ctx:research"),
            ("plan parallel development", "/ctx:plan"),
            ("create parallel plan", "/ctx:plan"),
            ("execute parallel tasks", "/ctx:execute"),
            ("run in parallel", "/ctx:execute"),
            ("check parallel status", "/ctx:status"),
            ("cleanup worktrees", "/ctx:cleanup"),
        ]

        passed = 0
        failed = 0

        for text, expected_command in test_cases:
            result = matcher.match(text)
            if result and result.command == expected_command:
                passed += 1
                print(f"✓ '{text}' -> {expected_command}")
            else:
                failed += 1
                actual = result.command if result else "None"
                print(f"✗ '{text}' -> expected {expected_command}, got {actual}")

        return passed, failed

    def test_case_insensitivity():
        """Test case-insensitive matching."""
        matcher = KeywordMatcher()

        test_cases = [
            "ANALYZE the code",
            "Analyze The Code",
            "analyze the code",
        ]

        passed = 0
        failed = 0

        for text in test_cases:
            result = matcher.match(text)
            if result and result.command == "/ctx:design":
                passed += 1
                print(f"✓ Case insensitive: '{text}'")
            else:
                failed += 1
                print(f"✗ Case insensitive failed: '{text}'")

        return passed, failed

    def test_no_match():
        """Test cases that should not match."""
        matcher = KeywordMatcher()

        test_cases = [
            "hello world",
            "random text",
            "nothing relevant here",
            "",
        ]

        passed = 0
        failed = 0

        for text in test_cases:
            result = matcher.match(text)
            if result is None:
                passed += 1
                print(f"✓ No match (as expected): '{text}'")
            else:
                failed += 1
                print(f"✗ Unexpected match: '{text}' -> {result.command}")

        return passed, failed

    def test_confidence_and_method():
        """Test that confidence and method are set correctly."""
        matcher = KeywordMatcher()
        result = matcher.match("analyze the code")

        passed = 0
        failed = 0

        if result:
            if result.confidence == 0.85:
                passed += 1
                print(f"✓ Confidence correct: {result.confidence}")
            else:
                failed += 1
                print(f"✗ Confidence incorrect: {result.confidence}")

            if result.method == "keyword":
                passed += 1
                print(f"✓ Method correct: {result.method}")
            else:
                failed += 1
                print(f"✗ Method incorrect: {result.method}")

            if result.matched_patterns:
                passed += 1
                print(f"✓ Matched patterns: {result.matched_patterns}")
            else:
                failed += 1
                print(f"✗ No matched patterns")
        else:
            failed += 3
            print("✗ No match returned")

        return passed, failed

    def test_performance():
        """Test that matching is fast (<1ms per query)."""
        matcher = KeywordMatcher()

        test_queries = [
            "analyze the code",
            "run tests",
            "fix the bug",
            "implement feature",
            "explain this",
            "random text that won't match",
        ]

        # Warmup
        for query in test_queries:
            matcher.match(query)

        # Measure
        latencies = []
        for query in test_queries * 100:  # 600 queries
            result = matcher.match(query)
            if result:
                latencies.append(result.latency_ms)
            else:
                # Measure manually for non-matches
                start = time.perf_counter()
                matcher.match(query)
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        print(f"\nPerformance Benchmark:")
        print(f"  Queries: {len(latencies)}")
        print(f"  Avg latency: {avg_latency:.4f}ms")
        print(f"  Max latency: {max_latency:.4f}ms")

        passed = 0
        failed = 0

        if avg_latency < 1.0:
            passed += 1
            print(f"✓ Average latency under 1ms")
        else:
            failed += 1
            print(f"✗ Average latency over 1ms")

        if max_latency < 2.0:  # Allow some variance
            passed += 1
            print(f"✓ Max latency reasonable")
        else:
            failed += 1
            print(f"✗ Max latency too high")

        return passed, failed

    def test_compound_phrases():
        """Test matching in compound phrases."""
        matcher = KeywordMatcher()

        test_cases = [
            ("can you design the API architecture", "/ctx:design"),
            ("please research best state libraries", "/ctx:research"),
            ("let's create a parallel development plan", "/ctx:plan"),
            ("I want to execute these tasks in parallel", "/ctx:execute"),
        ]

        passed = 0
        failed = 0

        for text, expected_command in test_cases:
            result = matcher.match(text)
            if result and result.command == expected_command:
                passed += 1
                print(f"✓ Compound phrase: '{text}'")
            else:
                failed += 1
                actual = result.command if result else "None"
                print(f"✗ Compound phrase: '{text}' -> expected {expected_command}, got {actual}")

        return passed, failed

    # Run all tests
    print("=" * 70)
    print("Keyword Matcher Unit Tests")
    print("=" * 70)

    total_passed = 0
    total_failed = 0

    print("\n--- Basic Matches ---")
    p, f = test_basic_matches()
    total_passed += p
    total_failed += f

    print("\n--- Case Insensitivity ---")
    p, f = test_case_insensitivity()
    total_passed += p
    total_failed += f

    print("\n--- No Match Cases ---")
    p, f = test_no_match()
    total_passed += p
    total_failed += f

    print("\n--- Confidence and Method ---")
    p, f = test_confidence_and_method()
    total_passed += p
    total_failed += f

    print("\n--- Compound Phrases ---")
    p, f = test_compound_phrases()
    total_passed += p
    total_failed += f

    print("\n--- Performance ---")
    p, f = test_performance()
    total_passed += p
    total_failed += f

    print("\n" + "=" * 70)
    print(f"Total: {total_passed} passed, {total_failed} failed")
    print("=" * 70)

    sys.exit(0 if total_failed == 0 else 1)
