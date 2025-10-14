#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "model2vec>=0.3.0",
#     "numpy>=1.24.0"
# ]
# ///
"""
Model2Vec-based semantic intent matcher for SuperClaude command detection.

Uses minishlab/potion-base-2M (8MB) for ultra-fast semantic matching (1-3ms per query).
Matches natural language queries to SuperClaude commands using cosine similarity.
"""

import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import sys


@dataclass
class IntentMatch:
    """Result of intent matching operation."""
    command: str
    confidence: float  # Cosine similarity score
    method: str  # "model2vec"
    latency_ms: float
    matched_patterns: List[str]


class Model2VecMatcher:
    """
    Semantic intent matcher using Model2Vec embeddings.

    Features:
    - Lazy model loading (only on first use)
    - Pre-computed intent embeddings (cached)
    - Cosine similarity matching
    - 1-3ms query latency (after model load)
    - Graceful fallback if dependencies unavailable
    """

    # Intent patterns for each command
    INTENT_PATTERNS = {
        "/sc:analyze": [
            "analyze this code",
            "review the codebase",
            "check code quality",
            "audit for issues",
            "examine the code structure",
            "inspect code patterns",
        ],
        "/sc:test": [
            "run tests",
            "check coverage",
            "write unit tests",
            "test this code",
            "execute test suite",
            "verify functionality",
        ],
        "/sc:troubleshoot": [
            "fix this bug",
            "debug the issue",
            "help me solve this error",
            "diagnose the problem",
            "resolve this issue",
            "why is this broken",
        ],
        "/sc:implement": [
            "build this feature",
            "create a component",
            "implement this",
            "develop functionality",
            "code this up",
            "make this feature",
        ],
        "/sc:explain": [
            "explain this code",
            "what does this do",
            "document this",
            "help me understand",
            "describe how this works",
            "clarify this code",
        ],
        "/sc:improve": [
            "optimize this",
            "make it faster",
            "refactor this code",
            "enhance performance",
            "clean up this code",
            "improve efficiency",
        ],
        "/sc:git": [
            "commit changes",
            "create a branch",
            "git operations",
            "version control",
            "push to remote",
            "manage commits",
        ],
        "/sc:build": [
            "compile the project",
            "build the application",
            "package for deployment",
            "run build process",
            "bundle assets",
            "prepare for production",
        ],
        "/sc:design": [
            "design the architecture",
            "plan the system",
            "create API design",
            "design components",
            "structure the application",
            "architect the solution",
        ],
    }

    # Confidence threshold for matching
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(self, model_name: str = "minishlab/potion-base-2M"):
        """
        Initialize matcher with lazy loading.

        Args:
            model_name: Model2Vec model identifier
        """
        self.model_name = model_name
        self._model = None
        self._intent_embeddings: Optional[Dict[str, List[Tuple[str, any]]]] = None
        self._model_load_attempted = False

    def is_available(self) -> bool:
        """
        Check if model2vec is installed and model can be loaded.

        Returns:
            True if model2vec is available, False otherwise
        """
        try:
            import model2vec
            return True
        except ImportError:
            return False

    def _load_model(self) -> bool:
        """
        Lazy load the Model2Vec model.

        Returns:
            True if model loaded successfully, False otherwise
        """
        if self._model is not None:
            return True

        if self._model_load_attempted:
            return False

        self._model_load_attempted = True

        try:
            from model2vec import StaticModel
            import numpy as np

            # Load model (downloads on first use, ~8MB)
            self._model = StaticModel.from_pretrained(self.model_name)
            self._precompute_intent_embeddings()
            return True

        except Exception as e:
            print(f"Warning: Failed to load Model2Vec model: {e}", file=sys.stderr)
            return False

    def _precompute_intent_embeddings(self):
        """Pre-compute embeddings for all intent patterns."""
        if self._model is None:
            return

        self._intent_embeddings = {}

        for command, patterns in self.INTENT_PATTERNS.items():
            embeddings = []
            for pattern in patterns:
                embedding = self._model.encode([pattern])[0]
                embeddings.append((pattern, embedding))
            self._intent_embeddings[command] = embeddings

    def _cosine_similarity(self, vec1, vec2) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        import numpy as np

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def match(self, text: str) -> Optional[IntentMatch]:
        """
        Match natural language text to a SuperClaude command.

        Args:
            text: User query text

        Returns:
            IntentMatch if confidence >= threshold, None otherwise
        """
        start_time = time.perf_counter()

        # Ensure model is loaded
        if not self._load_model():
            return None

        if not text or not text.strip():
            return None

        # Encode query
        try:
            query_embedding = self._model.encode([text.strip()])[0]
        except Exception as e:
            print(f"Warning: Failed to encode query: {e}", file=sys.stderr)
            return None

        # Find best match across all commands
        best_command = None
        best_confidence = 0.0
        best_pattern = None

        for command, pattern_embeddings in self._intent_embeddings.items():
            for pattern, pattern_embedding in pattern_embeddings:
                similarity = self._cosine_similarity(query_embedding, pattern_embedding)

                if similarity > best_confidence:
                    best_confidence = similarity
                    best_command = command
                    best_pattern = pattern

        # Calculate latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Return match if above threshold
        if best_confidence >= self.CONFIDENCE_THRESHOLD and best_command:
            return IntentMatch(
                command=best_command,
                confidence=best_confidence,
                method="model2vec",
                latency_ms=latency_ms,
                matched_patterns=[best_pattern] if best_pattern else [],
            )

        return None

    def batch_match(self, texts: List[str]) -> List[Optional[IntentMatch]]:
        """
        Match multiple queries in batch (more efficient).

        Args:
            texts: List of user query texts

        Returns:
            List of IntentMatch results (None for no match)
        """
        if not self._load_model():
            return [None] * len(texts)

        results = []
        for text in texts:
            results.append(self.match(text))

        return results


def main():
    """Demo and basic testing."""
    print("Model2Vec Intent Matcher Demo")
    print("=" * 50)

    matcher = Model2VecMatcher()

    # Check availability
    if not matcher.is_available():
        print("ERROR: model2vec not available")
        print("Install with: uv pip install model2vec>=0.3.0")
        sys.exit(1)

    print(f"Model2Vec is available")
    print(f"Model: {matcher.model_name}")
    print()

    # Test queries
    test_queries = [
        "can you analyze my code for issues?",
        "help me debug this error",
        "write tests for this function",
        "explain what this code does",
        "make this code faster",
        "implement a new feature",
        "commit my changes",
        "compile the project",
        "design the API",
        "random unrelated text",
    ]

    print("Testing queries:")
    print("-" * 50)

    for query in test_queries:
        result = matcher.match(query)
        if result:
            print(f"Query: '{query}'")
            print(f"  → Command: {result.command}")
            print(f"  → Confidence: {result.confidence:.3f}")
            print(f"  → Latency: {result.latency_ms:.2f}ms")
            print(f"  → Matched: {result.matched_patterns[0] if result.matched_patterns else 'N/A'}")
        else:
            print(f"Query: '{query}'")
            print(f"  → No match found")
        print()


if __name__ == "__main__":
    main()
