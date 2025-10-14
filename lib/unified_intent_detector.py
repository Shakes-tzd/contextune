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
Unified intent detector - 3-tier cascade.

Tier 1: Keyword matching (0.02ms)
Tier 2: Model2Vec embeddings (0.2ms)
Tier 3: Semantic Router (50ms)
"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Import your existing matchers
from keyword_matcher import KeywordMatcher, IntentMatch
from model2vec_matcher import Model2VecMatcher
from semantic_router_matcher import SemanticRouterMatcher


@dataclass
class DetectionResult:
    """Unified detection result."""
    command: str
    confidence: float
    method: str
    latency_ms: float


class UnifiedIntentDetector:
    """
    3-tier intent detection cascade.
    
    Tries matchers in order of speed:
    1. Keyword (fastest, 60% coverage)
    2. Model2Vec (fast, 30% coverage)
    3. Semantic Router (accurate, 10% coverage)
    """
    
    def __init__(self):
        """Initialize matchers with lazy loading."""
        self._keyword_matcher = None
        self._model2vec_matcher = None
        self._semantic_router_matcher = None
    
    def _get_keyword_matcher(self) -> KeywordMatcher:
        """Lazy load keyword matcher."""
        if self._keyword_matcher is None:
            self._keyword_matcher = KeywordMatcher()
        return self._keyword_matcher
    
    def _get_model2vec_matcher(self) -> Optional[Model2VecMatcher]:
        """Lazy load model2vec matcher."""
        if self._model2vec_matcher is None:
            matcher = Model2VecMatcher()
            if matcher.is_available():
                self._model2vec_matcher = matcher
            else:
                return None
        return self._model2vec_matcher
    
    def _get_semantic_router_matcher(self) -> Optional[SemanticRouterMatcher]:
        """Lazy load semantic router matcher."""
        if self._semantic_router_matcher is None:
            matcher = SemanticRouterMatcher()
            if matcher.is_available():
                self._semantic_router_matcher = matcher
            else:
                return None
        return self._semantic_router_matcher
    
    def detect(self, text: str) -> Optional[DetectionResult]:
        """
        Detect intent using 3-tier cascade.
        
        Args:
            text: User prompt text
            
        Returns:
            DetectionResult if match found, None otherwise
        """
        if not text or not text.strip():
            return None
        
        # Tier 1: Keyword matching (always available, fastest)
        keyword_result = self._get_keyword_matcher().match(text)
        if keyword_result:
            return DetectionResult(
                command=keyword_result.command,
                confidence=keyword_result.confidence,
                method="keyword",
                latency_ms=keyword_result.latency_ms
            )
        
        # Tier 2: Model2Vec (fast semantic matching)
        model2vec_matcher = self._get_model2vec_matcher()
        if model2vec_matcher:
            model2vec_result = model2vec_matcher.match(text)
            if model2vec_result:
                return DetectionResult(
                    command=model2vec_result.command,
                    confidence=model2vec_result.confidence,
                    method="model2vec",
                    latency_ms=model2vec_result.latency_ms
                )
        
        # Tier 3: Semantic Router (most accurate, slowest)
        semantic_router_matcher = self._get_semantic_router_matcher()
        if semantic_router_matcher:
            semantic_result = semantic_router_matcher.match(text)
            if semantic_result:
                return DetectionResult(
                    command=semantic_result.command,
                    confidence=semantic_result.confidence,
                    method="semantic_router",
                    latency_ms=semantic_result.latency_ms
                )
        
        # No match found
        return None


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: uv run unified_intent_detector.py 'your query here'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    detector = UnifiedIntentDetector()
    result = detector.detect(query)
    
    if result:
        print(f"Command: {result.command}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Method: {result.method}")
        print(f"Latency: {result.latency_ms:.2f}ms")
    else:
        print("No command detected")