#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=7.0.0"]
# ///
"""
Comprehensive tests for keyword matcher with context-aware pattern matching.

Tests verify that the /ctx:help command correctly rejects "help [pronoun] [action]"
patterns while detecting genuine help requests.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.keyword_matcher import KeywordMatcher


class TestContextAwareHelpMatching:
    """Test context-aware /ctx:help pattern matching."""

    def setup_method(self):
        """Create a fresh matcher for each test."""
        self.matcher = KeywordMatcher()

    def test_false_positive_help_me_research(self):
        """Reject: 'help me research X' should NOT match /ctx:help."""
        result = self.matcher.match("help me research the best state library")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me research'"

    def test_false_positive_help_me_implement(self):
        """Reject: 'help me implement X' should NOT match /ctx:help."""
        result = self.matcher.match("help me implement a new feature")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me implement'"

    def test_false_positive_help_me_build(self):
        """Reject: 'help me build X' should NOT match /ctx:help."""
        result = self.matcher.match("can you help me build this component")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me build'"

    def test_false_positive_help_me_create(self):
        """Reject: 'help me create X' should NOT match /ctx:help."""
        result = self.matcher.match("help me create a new API endpoint")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me create'"

    def test_false_positive_help_me_design(self):
        """Reject: 'help me design X' should NOT match /ctx:help."""
        result = self.matcher.match("help me design the authentication system")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me design'"

    def test_false_positive_help_me_analyze(self):
        """Reject: 'help me analyze X' should NOT match /ctx:help."""
        result = self.matcher.match("help me analyze this codebase")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me analyze'"

    def test_false_positive_help_me_fix(self):
        """Reject: 'help me fix X' should NOT match /ctx:help."""
        result = self.matcher.match("help me fix this bug")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help me fix'"

    def test_false_positive_help_you_with(self):
        """Reject: 'help you with X' should NOT match /ctx:help."""
        result = self.matcher.match("I can help you with that task")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help you with'"

    def test_false_positive_help_us_build(self):
        """Reject: 'help us build X' should NOT match /ctx:help."""
        result = self.matcher.match("help us build a better product")
        assert result is None or result.command != "/ctx:help", \
            "Should not detect /ctx:help for 'help us build'"


class TestTruePositiveHelpMatching:
    """Test that genuine help requests are correctly detected."""

    def setup_method(self):
        """Create a fresh matcher for each test."""
        self.matcher = KeywordMatcher()

    def test_true_positive_show_help(self):
        """Match: 'show help' should match /ctx:help with high confidence."""
        result = self.matcher.match("show help")
        assert result is not None, "Should detect /ctx:help for 'show help'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95, f"Expected confidence 0.95, got {result.confidence}"

    def test_true_positive_what_is_help(self):
        """Match: 'what is help' should match /ctx:help with high confidence."""
        result = self.matcher.match("what is help")
        assert result is not None, "Should detect /ctx:help for 'what is help'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_list_help(self):
        """Match: 'list help' should match /ctx:help with high confidence."""
        result = self.matcher.match("list help")
        assert result is not None, "Should detect /ctx:help for 'list help'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_command(self):
        """Match: 'help command' should match /ctx:help with high confidence."""
        result = self.matcher.match("help command")
        assert result is not None, "Should detect /ctx:help for 'help command'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_reference(self):
        """Match: 'help reference' should match /ctx:help with high confidence."""
        result = self.matcher.match("show me the help reference")
        assert result is not None, "Should detect /ctx:help for 'help reference'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_guide(self):
        """Match: 'help guide' should match /ctx:help with high confidence."""
        result = self.matcher.match("where is the help guide")
        assert result is not None, "Should detect /ctx:help for 'help guide'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_menu(self):
        """Match: 'help menu' should match /ctx:help with high confidence."""
        result = self.matcher.match("help menu")
        assert result is not None, "Should detect /ctx:help for 'help menu'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_documentation(self):
        """Match: 'help documentation' should match /ctx:help with high confidence."""
        result = self.matcher.match("help documentation")
        assert result is not None, "Should detect /ctx:help for 'help documentation'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_help_docs(self):
        """Match: 'help docs' should match /ctx:help with high confidence."""
        result = self.matcher.match("help docs")
        assert result is not None, "Should detect /ctx:help for 'help docs'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.95

    def test_true_positive_need_help(self):
        """Match: 'need help' (standalone) should match /ctx:help."""
        result = self.matcher.match("I need help")
        assert result is not None, "Should detect /ctx:help for 'need help'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.85

    def test_true_positive_want_help(self):
        """Match: 'want help' (standalone) should match /ctx:help."""
        result = self.matcher.match("I want help")
        assert result is not None, "Should detect /ctx:help for 'want help'"
        assert result.command == "/ctx:help"
        assert result.confidence == 0.85


class TestConfidenceScoring:
    """Test that confidence scores are correctly assigned based on pattern tier."""

    def setup_method(self):
        """Create a fresh matcher for each test."""
        self.matcher = KeywordMatcher()

    def test_high_confidence_explicit_patterns(self):
        """High confidence (0.95): Explicit help commands."""
        high_confidence_queries = [
            "show help",
            "what is help",
            "help command",
            "help reference",
        ]

        for query in high_confidence_queries:
            result = self.matcher.match(query)
            assert result is not None, f"Should match: {query}"
            if result.command == "/ctx:help":
                assert result.confidence == 0.95, \
                    f"Expected 0.95 for '{query}', got {result.confidence}"

    def test_medium_confidence_filtered_standalone(self):
        """Medium confidence (0.85): Filtered standalone help."""
        medium_confidence_queries = [
            "I need help",
            "I want help",
        ]

        for query in medium_confidence_queries:
            result = self.matcher.match(query)
            assert result is not None, f"Should match: {query}"
            if result.command == "/ctx:help":
                assert result.confidence == 0.85, \
                    f"Expected 0.85 for '{query}', got {result.confidence}"

    def test_low_confidence_negative_lookahead(self):
        """Low confidence (0.70): General help with negative lookahead."""
        # These should match with low confidence (if they match at all)
        # The negative lookahead should prevent most action-based phrases
        low_confidence_queries = [
            "help with configuration",  # Should match (not an action verb)
        ]

        for query in low_confidence_queries:
            result = self.matcher.match(query)
            if result and result.command == "/ctx:help":
                assert result.confidence == 0.70, \
                    f"Expected 0.70 for '{query}', got {result.confidence}"


class TestPerformance:
    """Test that performance targets are maintained (<2ms P95)."""

    def setup_method(self):
        """Create a fresh matcher for each test."""
        self.matcher = KeywordMatcher()

    def test_latency_under_2ms(self):
        """Verify P95 latency is under 2ms."""
        test_queries = [
            "show help",
            "help me research",
            "help command",
            "help me implement feature",
            "I need help",
            "random text that won't match help",
        ]

        latencies = []

        # Warmup
        for query in test_queries * 10:
            self.matcher.match(query)

        # Measure
        for query in test_queries * 100:  # 600 queries
            result = self.matcher.match(query)
            if result:
                latencies.append(result.latency_ms)

        if latencies:
            latencies.sort()
            p95_latency = latencies[int(len(latencies) * 0.95)]
            assert p95_latency < 2.0, \
                f"P95 latency {p95_latency:.2f}ms exceeds 2ms target"


class TestCaseInsensitivity:
    """Test that patterns are case-insensitive."""

    def setup_method(self):
        """Create a fresh matcher for each test."""
        self.matcher = KeywordMatcher()

    def test_case_variations(self):
        """Test various case combinations."""
        variations = [
            "SHOW HELP",
            "Show Help",
            "show help",
            "ShOw HeLp",
            "HELP COMMAND",
            "help command",
        ]

        for query in variations:
            result = self.matcher.match(query)
            assert result is not None, f"Should match case-insensitive: {query}"
            assert result.command == "/ctx:help"


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))
