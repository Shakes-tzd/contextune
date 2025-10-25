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
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple


@dataclass
class IntentMatch:
    """Result of intent matching operation."""

    command: str          # e.g., "/sc:analyze"
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
        >>> result = matcher.match("analyze the code quality")
        >>> result.command
        '/sc:analyze'
        >>> result.confidence
        0.85
    """

    # Command patterns: (command, compiled_regex, pattern_description)
    COMMAND_PATTERNS: List[Tuple[str, re.Pattern, str]] = []

    def __init__(self):
        """Initialize the keyword matcher with compiled regex patterns."""
        if not KeywordMatcher.COMMAND_PATTERNS:
            KeywordMatcher._compile_patterns()

    @staticmethod
    def _compile_patterns():
        """Compile regex patterns for all commands (called once)."""
        # Define raw patterns for each command
        patterns = {
            '/sc:analyze': [
                r'\banalyze\b',
                r'\breview\b',
                r'\baudit\b',
                r'\binspect\b',
                r'\bexamine\b',
                r'\bcheck\s+(code|quality)\b',
                r'\blook\s+at\b.*\b(code|my)\b',
                r'\bcan\s+you\s+look\b',
                r'\bassess\b',
                r'\bevaluate\b',
                r'\binvestigate\b',
                r'\bfor\s+issues\b',
                r'\bfor\s+problems\b',
                r'\bfind\s+(issues|problems)\b',
            ],
            '/sc:test': [
                r'\btest\b',
                r'\bcoverage\b',
                r'\bunit\s+test\b',
                r'\brun\s+(?:the\s+)?(?:unit\s+)?tests\b',
                r'\bvalidate\b',
            ],
            '/sc:troubleshoot': [
                r'\bdebug\b',
                r'\bfix\b',
                r'\btroubleshoot\b',
                r'\bbug\b',
                r'\berror\b',
                r'\bissue\b(?!s)',  # "issue" but not "issues" alone
                r'\bfix\s+(this|the|my)\b',
                r'\bsolve\b',
                r'\bresolve\b',
            ],
            '/sc:implement': [
                r'\bimplement\b',
                r'\bcreate\b',
                r'\bbuild\b',
                r'\bdevelop\b',
                r'\badd\s+feature\b',
            ],
            '/sc:explain': [
                r'\bexplain\b',
                r'\bdescribe\b',
                r'\bdocument\b',
                r'\bwhat\s+does\b',
                r'\bhow\s+does\b',
            ],
            '/sc:improve': [
                r'\bimprove\b',
                r'\boptimize\b',
                r'\brefactor\b',
                r'\benhance\b',
                r'\bperformance\b',
            ],
            '/sc:design': [
                r'\bdesign\b',
                r'\barchitecture\b',
                r'\bplan\b',
                r'\bstructure\b',
            ],
            '/sc:cleanup': [
                r'\bcleanup\b',
                r'\bremove\b',
                r'\bdelete\b',
                r'\bclean\s+up\s+code\b',
            ],
            '/sc:git': [
                r'\bcommit\b',
                r'\bpush\b',
                r'\bpull\b',
                r'\bmerge\b',
                r'\bgit\b',
            ],
            '/ctx:research': [
                r'\bresearch\b',
                r'\binvestigate\b',
                r'\bfind\s+information\b',
                r'\bcompare\b',
                r'\bwhat\'?s\s+the\s+best\b',
                r'\bwhich\s+(library|framework|tool)\b',
                r'\bwhat\s+should\s+i\s+use\b',
                r'\blook\s+into\b',
                r'\bevaluate\s+options\b',
            ],
        }

        # Compile patterns with case-insensitive flag
        for command, pattern_list in patterns.items():
            for pattern_str in pattern_list:
                compiled = re.compile(pattern_str, re.IGNORECASE)
                KeywordMatcher.COMMAND_PATTERNS.append(
                    (command, compiled, pattern_str)
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
        for command, pattern, pattern_str in self.COMMAND_PATTERNS:
            if pattern.search(text):
                latency_ms = (time.perf_counter() - start_time) * 1000
                return IntentMatch(
                    command=command,
                    confidence=0.85,
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
            ("analyze the code", "/sc:analyze"),
            ("review the implementation", "/sc:analyze"),
            ("run tests", "/sc:test"),
            ("unit test coverage", "/sc:test"),
            ("debug this issue", "/sc:troubleshoot"),
            ("fix the bug", "/sc:troubleshoot"),
            ("implement a new feature", "/sc:implement"),
            ("create this component", "/sc:implement"),
            ("explain how this works", "/sc:explain"),
            ("what does this function do", "/sc:explain"),
            ("improve performance", "/sc:improve"),
            ("optimize the code", "/sc:improve"),
            ("design the architecture", "/sc:design"),
            ("plan the structure", "/sc:design"),
            ("cleanup the code", "/sc:cleanup"),
            ("remove dead code", "/sc:cleanup"),
            ("git commit", "/sc:git"),
            ("push to remote", "/sc:git"),
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
            if result and result.command == "/sc:analyze":
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
            ("can you analyze the code quality", "/sc:analyze"),
            ("please run the unit tests", "/sc:test"),
            ("I need to fix this bug in the code", "/sc:troubleshoot"),
            ("let's implement the new feature together", "/sc:implement"),
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
