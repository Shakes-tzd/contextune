#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "semantic-router>=0.1.0"
# ]
# ///

"""
Semantic Router-based intent matcher for SuperClaude command detection.

Provides fast, semantic matching of user queries to SuperClaude commands using
embeddings-based routing with Cohere or OpenAI encoders.

Target performance: 50-100ms per query
"""

import os
import time
from dataclasses import dataclass
from typing import List, Optional

from semantic_router import Route, SemanticRouter
from semantic_router.encoders import CohereEncoder, OpenAIEncoder


@dataclass
class IntentMatch:
    """Result of semantic intent matching."""
    command: str
    confidence: float
    method: str  # "semantic_router"
    latency_ms: float
    matched_patterns: List[str]


class SemanticRouterMatcher:
    """
    Semantic Router-based intent matcher for SuperClaude commands.

    Uses embeddings-based semantic routing to match user queries to commands
    with high accuracy and low latency. Supports both Cohere and OpenAI encoders.
    """

    def __init__(self):
        """Initialize matcher with lazy loading."""
        self._router: Optional[SemanticRouter] = None
        self._encoder_type: Optional[str] = None
        self._routes: List[Route] = self._define_routes()

    def _define_routes(self) -> List[Route]:
        """
        Define semantic routes for SuperClaude commands.

        Each route contains example utterances that represent the command's intent.
        """
        return [
            Route(
                name="/sc:analyze",
                utterances=[
                    "analyze this code",
                    "review the code quality",
                    "check for code issues",
                    "what are the problems with this code",
                    "audit this codebase",
                    "assess code quality",
                    "inspect the architecture",
                    "evaluate the code structure",
                    "find security vulnerabilities",
                    "check for performance issues",
                    "review this implementation",
                    "what's wrong with this code"
                ]
            ),
            Route(
                name="/sc:test",
                utterances=[
                    "run the tests",
                    "execute test suite",
                    "check test coverage",
                    "run unit tests",
                    "test this code",
                    "verify with tests",
                    "check if tests pass",
                    "measure code coverage",
                    "run integration tests",
                    "execute all tests",
                    "validate with test cases",
                    "generate test report"
                ]
            ),
            Route(
                name="/sc:troubleshoot",
                utterances=[
                    "fix this bug",
                    "debug this issue",
                    "why isn't this working",
                    "solve this problem",
                    "troubleshoot the error",
                    "diagnose this issue",
                    "find the bug",
                    "repair this code",
                    "resolve this error",
                    "figure out what's broken",
                    "investigate this failure",
                    "why is this failing"
                ]
            ),
            Route(
                name="/sc:implement",
                utterances=[
                    "build a new feature",
                    "implement this functionality",
                    "create a new component",
                    "develop this feature",
                    "add this capability",
                    "build this from scratch",
                    "implement the requirements",
                    "develop this module",
                    "create this feature",
                    "build the functionality",
                    "add this feature",
                    "write the implementation"
                ]
            ),
            Route(
                name="/sc:explain",
                utterances=[
                    "explain this code",
                    "what does this do",
                    "help me understand this",
                    "document this code",
                    "describe how this works",
                    "clarify this implementation",
                    "break down this code",
                    "walk me through this",
                    "explain the logic",
                    "what's happening here",
                    "help me understand the flow",
                    "describe the architecture"
                ]
            ),
            Route(
                name="/sc:improve",
                utterances=[
                    "optimize this code",
                    "refactor this implementation",
                    "improve performance",
                    "make this code better",
                    "enhance this code",
                    "clean up this code",
                    "improve code quality",
                    "optimize for speed",
                    "refactor for maintainability",
                    "enhance the performance",
                    "make this more efficient",
                    "improve the design"
                ]
            )
        ]

    def _get_encoder(self):
        """
        Get appropriate encoder based on available API keys.

        Tries Cohere first, then OpenAI. Returns None if no keys available.
        """
        cohere_key = os.environ.get("COHERE_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if cohere_key:
            self._encoder_type = "cohere"
            return CohereEncoder(cohere_api_key=cohere_key)
        elif openai_key:
            self._encoder_type = "openai"
            return OpenAIEncoder(openai_api_key=openai_key)
        else:
            return None

    def _build_router(self) -> bool:
        """
        Build the router with lazy initialization.

        Returns:
            True if router was built successfully, False otherwise.
        """
        if self._router is not None:
            return True

        try:
            encoder = self._get_encoder()
            if encoder is None:
                return False

            self._router = SemanticRouter(
                encoder=encoder,
                routes=self._routes
            )
            return True
        except Exception:
            # Gracefully handle encoder initialization errors
            return False

    def is_available(self) -> bool:
        """
        Check if semantic router is available.

        Returns:
            True if API key is available and router can be built.
        """
        if self._router is not None:
            return True

        cohere_key = os.environ.get("COHERE_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        return cohere_key is not None or openai_key is not None

    def match(self, text: str) -> Optional[IntentMatch]:
        """
        Match user query to SuperClaude command using semantic routing.

        Args:
            text: User query text to match.

        Returns:
            IntentMatch object if successful match found, None otherwise.
        """
        # Lazy build router on first use
        if not self._build_router():
            return None

        start_time = time.perf_counter()

        try:
            # Route the query
            route_choice = self._router(text)

            # Calculate latency
            latency_ms = (time.perf_counter() - start_time) * 1000

            # semantic-router returns RouteChoice with name field
            if route_choice is None or route_choice.name is None:
                return None

            route_name = route_choice.name

            # Get matched route for patterns
            matched_route = next(
                (route for route in self._routes if route.name == route_name),
                None
            )

            # Extract sample patterns from the matched route
            matched_patterns = (
                matched_route.utterances[:3] if matched_route else []
            )

            # Use similarity_score if available, otherwise default confidence
            confidence = route_choice.similarity_score if route_choice.similarity_score else 0.85

            return IntentMatch(
                command=route_name,
                confidence=confidence,
                method="semantic_router",
                latency_ms=latency_ms,
                matched_patterns=matched_patterns
            )

        except Exception:
            # Gracefully handle API errors or routing failures
            return None


# Example usage and testing
if __name__ == "__main__":
    matcher = SemanticRouterMatcher()

    if not matcher.is_available():
        print("No API key available. Set COHERE_API_KEY or OPENAI_API_KEY.")
        exit(1)

    # Test queries
    test_queries = [
        "Can you review this code for me?",
        "Run all the tests please",
        "This function is broken, help me fix it",
        "Build a login system",
        "What does this function do?",
        "Make this code faster"
    ]

    print("Testing Semantic Router Matcher\n" + "=" * 50)

    for query in test_queries:
        result = matcher.match(query)

        if result:
            print(f"\nQuery: {query}")
            print(f"Command: {result.command}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Latency: {result.latency_ms:.2f}ms")
            print(f"Matched patterns: {result.matched_patterns[:2]}")
        else:
            print(f"\nQuery: {query}")
            print("No match found")
