#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rapidfuzz>=3.0.0",
#     "pyyaml>=6.0",
# ]
# ///

"""
RapidFuzz-based keyword matcher with auto-loading from markdown files.

Eliminates JSON maintenance - keywords live in markdown frontmatter!
Uses fuzzy matching for typo tolerance and natural variations.
"""

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import yaml
from rapidfuzz import fuzz, process


@dataclass
class IntentMatch:
    """Result of intent matching operation."""
    command: str  # e.g., "/ctx:design" or "skill:ctx:worktree" or "agent:worktree-manager"
    confidence: float  # 0.0-1.0
    method: str  # "fuzzy"
    latency_ms: float
    matched_keywords: List[str]  # Keywords that matched


class KeywordMatcherV2:
    """
    Fuzzy keyword matcher using RapidFuzz.

    Loads keywords from:
    1. Markdown frontmatter (commands/*.md, skills/*/SKILL.md, agents/*.md)
    2. Generated intent_mappings.json (fallback)

    Uses fuzzy string matching for typo tolerance.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize matcher by loading keywords from markdown files."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.keyword_index: Dict[str, List[str]] = {}
        self.load_keywords()

    def load_keywords(self):
        """Load keywords from markdown frontmatter or JSON."""
        try:
            # Try loading from generated JSON first (faster)
            json_path = self.base_dir / 'data' / 'intent_mappings.json'
            if json_path.exists():
                self.load_from_json(json_path)
                print(f"✅ Loaded {len(self.keyword_index)} items from JSON", file=sys.stderr)
                return
        except Exception as e:
            print(f"Warning: Could not load JSON: {e}", file=sys.stderr)

        # Fall back to parsing markdown files directly
        try:
            self.load_from_markdown()
            print(f"✅ Loaded {len(self.keyword_index)} items from markdown", file=sys.stderr)
        except Exception as e:
            print(f"Error: Could not load from markdown: {e}", file=sys.stderr)
            # Use minimal fallback
            self.keyword_index = {
                '/ctx:design': ['design', 'architect', 'architecture'],
                '/ctx:research': ['research', 'investigate'],
            }

    def load_from_json(self, json_path: Path):
        """Load keywords from generated JSON file."""
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Load commands
        for cmd, config in data.get('commands', {}).items():
            keywords = config.get('keywords', [])
            if keywords:
                self.keyword_index[cmd] = keywords

        # Load skills
        for skill, config in data.get('skills', {}).items():
            keywords = config.get('keywords', [])
            if keywords:
                self.keyword_index[skill] = keywords

        # Load agents
        for agent, config in data.get('agents', {}).items():
            keywords = config.get('keywords', [])
            if keywords:
                self.keyword_index[agent] = keywords

    def load_from_markdown(self):
        """Load keywords directly from markdown frontmatter."""
        # Parse commands
        commands_dir = self.base_dir / 'commands'
        if commands_dir.exists():
            for md_file in commands_dir.glob('*.md'):
                self._parse_markdown_file(md_file)

        # Parse skills
        skills_dir = self.base_dir / 'skills'
        if skills_dir.exists():
            for skill_file in skills_dir.glob('*/SKILL.md'):
                self._parse_markdown_file(skill_file)

        # Parse agents
        agents_dir = self.base_dir / 'agents'
        if agents_dir.exists():
            for agent_file in agents_dir.glob('*.md'):
                self._parse_markdown_file(agent_file)

    def _parse_markdown_file(self, filepath: Path):
        """Extract frontmatter from markdown and add to index."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                return

            frontmatter = yaml.safe_load(match.group(1)) or {}
            name = frontmatter.get('name')
            keywords = frontmatter.get('keywords', [])

            if name and keywords:
                # Normalize name
                if not name.startswith(('/','skill:','agent:')):
                    if 'agent' in str(filepath):
                        name = f"agent:{name}"
                    elif 'skill' in str(filepath):
                        name = f"skill:{name}"
                    else:
                        name = f"/{name}"

                self.keyword_index[name] = keywords

        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    def _is_help_with_action(self, text: str) -> bool:
        """
        Check if 'help' appears with action verbs (e.g., 'help me', 'help you').

        These are NOT requests for help documentation, but requests for assistance.
        Returns True if this is a help-with-action pattern (should NOT match /ctx:help).
        """
        # Patterns that indicate "help with action" not "help documentation"
        action_patterns = [
            r'\bhelp\s+(me|us|you|them)\b',  # "help me research"
            r'\b(can|could|would|will)\s+you\s+help\b',  # "can you help"
            r'\bhelp\s+\w+\s+(with|to|for)\b',  # "help implement with"
        ]

        text_lower = text.lower()
        for pattern in action_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def match(self, text: str) -> Optional[IntentMatch]:
        """
        Fuzzy match input text against all keywords with context-aware filtering.

        Uses RapidFuzz for typo tolerance. Returns best match above threshold.

        Special handling for /ctx:help to avoid false positives when "help"
        appears with action verbs like "help me research".

        Args:
            text: User's natural language query

        Returns:
            IntentMatch if confidence >= 0.70, None otherwise
        """
        start_time = time.perf_counter()

        if not text or not text.strip():
            return None

        text = text.strip().lower()
        best_match = None
        best_score = 0.0
        matched_keywords = []

        # Try each command/skill/agent
        for command, keywords in self.keyword_index.items():
            for keyword in keywords:
                # Fuzzy match using partial_ratio (better for keywords in longer text)
                # This checks if keyword appears as a substring with fuzzy matching
                score = fuzz.partial_ratio(keyword.lower(), text) / 100.0

                # Context-aware filtering for /ctx:help
                if command == '/ctx:help' and self._is_help_with_action(text):
                    # Skip this match - user wants help WITH something, not help docs
                    continue

                if score > best_score:
                    best_score = score
                    best_match = command
                    matched_keywords = [keyword]

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Return if confidence above threshold
        if best_match and best_score >= 0.70:
            return IntentMatch(
                command=best_match,
                confidence=best_score,
                method='fuzzy',
                latency_ms=latency_ms,
                matched_keywords=matched_keywords
            )

        return None

    def match_all(self, text: str, threshold: float = 0.70) -> List[IntentMatch]:
        """Return all matches above threshold with context-aware filtering, sorted by confidence."""
        start_time = time.perf_counter()

        if not text or not text.strip():
            return []

        text = text.strip().lower()
        matches = []

        for command, keywords in self.keyword_index.items():
            # Skip /ctx:help if this is a help-with-action pattern
            if command == '/ctx:help' and self._is_help_with_action(text):
                continue

            best_keyword_score = 0.0
            best_keyword = ""

            for keyword in keywords:
                score = fuzz.partial_ratio(keyword.lower(), text) / 100.0
                if score > best_keyword_score:
                    best_keyword_score = score
                    best_keyword = keyword

            if best_keyword_score >= threshold:
                latency_ms = (time.perf_counter() - start_time) * 1000
                matches.append(IntentMatch(
                    command=command,
                    confidence=best_keyword_score,
                    method='fuzzy',
                    latency_ms=latency_ms,
                    matched_keywords=[best_keyword]
                ))

        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches


# Self-test
if __name__ == '__main__':
    matcher = KeywordMatcherV2()

    test_cases = [
        "design a caching system",
        "desing the API",  # typo
        "architect the solution",
        "research best libraries",
        "my worktree is stuck",
        "worktree locked error",
    ]

    print("\n🧪 Testing fuzzy keyword matching:\n")
    for text in test_cases:
        result = matcher.match(text)
        if result:
            print(f"✅ '{text}'")
            print(f"   → {result.command} ({result.confidence:.0%} confidence)")
            print(f"   → Matched: {result.matched_keywords}")
        else:
            print(f"❌ '{text}' → No match")
        print()
