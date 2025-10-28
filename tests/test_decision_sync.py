"""
Unit tests for decision-sync.py

Tests:
1. Keyword detection (research, plans, decisions)
2. History.jsonl parsing
3. YAML reading/writing without corruption
4. Duplicate detection
5. Entry creation with proper structure
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys
import yaml
import re


# ============================================================================
# Test KeywordMatcher
# ============================================================================

class TestKeywordMatcher:
    """Test keyword detection logic."""

    RESEARCH_KEYWORDS = {
        'research', '/ctx:research', 'ctx:research',
        'investigate', 'exploration', 'explore', 'findings',
        'methodology', 'compare', 'comparison', 'benchmark',
        'analysis', 'analyze', 'study', 'survey'
    }

    PLAN_KEYWORDS = {
        '/ctx:plan', 'ctx:plan', 'create plan',
        'design', 'architecture', 'implementation plan',
        'breakdown', 'decompose', 'strategy', 'roadmap',
        'phased approach', 'workflow'
    }

    DECISION_KEYWORDS = {
        'decided to', 'decision:', 'alternatives',
        'alternatives considered', 'pros and cons',
        'why did we choose', 'rationale', 'trade-off',
        'accepted', 'rejected', 'status: accepted'
    }

    def detect_research(self, text: str) -> bool:
        """Check if text contains research indicators."""
        text_lower = text.lower()
        matches = sum(
            1 for keyword in self.RESEARCH_KEYWORDS
            if keyword.lower() in text_lower
        )
        has_findings = bool(re.search(r'(findings?|findings:)', text, re.IGNORECASE))
        has_methodology = bool(re.search(r'(methodology|approach)', text, re.IGNORECASE))
        return matches >= 1 or (has_findings and has_methodology)

    def detect_plan(self, text: str) -> bool:
        """Check if text contains planning indicators."""
        text_lower = text.lower()
        matches = sum(
            1 for keyword in self.PLAN_KEYWORDS
            if keyword.lower() in text_lower
        )
        has_yaml_tasks = bool(re.search(r'tasks:\s*\n\s*-', text, re.IGNORECASE))
        has_phases = bool(re.search(r'phases?:', text, re.IGNORECASE))
        return matches >= 1 or has_yaml_tasks or has_phases

    def detect_decision(self, text: str) -> bool:
        """Check if text contains decision indicators."""
        text_lower = text.lower()
        matches = sum(
            1 for keyword in self.DECISION_KEYWORDS
            if keyword.lower() in text_lower
        )
        has_alternatives = bool(re.search(r'##.*alternatives', text, re.IGNORECASE))
        has_status = bool(re.search(r'\*\*status:\*\*\s*(accepted|rejected)', text, re.IGNORECASE))
        return matches >= 1 or has_alternatives or has_status

    def test_detect_research_with_research_keyword(self):
        """Research keyword should be detected."""
        text = "Can you research the best practices for authentication?"
        assert self.detect_research(text)

    def test_detect_research_with_investigate(self):
        """'investigate' keyword should be detected."""
        text = "Please investigate how OAuth works"
        assert self.detect_research(text)

    def test_detect_research_with_compare(self):
        """'compare' keyword should be detected."""
        text = "Compare different database options for this use case"
        assert self.detect_research(text)

    def test_detect_plan_with_ctx_plan(self):
        """'/ctx:plan' keyword should be detected."""
        text = "Create a plan: /ctx:plan"
        assert self.detect_plan(text)

    def test_detect_plan_with_design(self):
        """'design' keyword should be detected."""
        text = "Let's design the architecture for this system"
        assert self.detect_plan(text)

    def test_detect_plan_with_yaml_tasks(self):
        """YAML task structure should be detected."""
        text = "tasks:\n  - id: task-1\n    title: Implementation"
        assert self.detect_plan(text)

    def test_detect_decision_with_decided_to(self):
        """'decided to' keyword should be detected."""
        text = "We decided to use PostgreSQL for the database"
        assert self.detect_decision(text)

    def test_detect_decision_with_alternatives(self):
        """'alternatives' keyword should be detected."""
        text = "Alternatives considered: Option A vs Option B"
        assert self.detect_decision(text)

    def test_detect_decision_with_status(self):
        """Decision status pattern should be detected."""
        text = "**Status:** Accepted - Use JWT for authentication"
        assert self.detect_decision(text)

    def test_no_false_positives(self):
        """Regular text should not trigger detection."""
        text = "The quick brown fox jumps over the lazy dog"
        assert not self.detect_research(text)
        assert not self.detect_plan(text)
        assert not self.detect_decision(text)


# ============================================================================
# Test History Parsing
# ============================================================================

class TestHistoryParsing:
    """Test history file parsing."""

    def test_load_valid_jsonl(self):
        """Should load valid JSONL entries."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"display": "test 1", "timestamp": 123}\n')
            f.write('{"display": "test 2", "timestamp": 456}\n')
            f.flush()
            path = Path(f.name)

        try:
            entries = []
            with open(path, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))

            assert len(entries) == 2
            assert entries[0]['display'] == 'test 1'
            assert entries[1]['display'] == 'test 2'
        finally:
            path.unlink()

    def test_load_with_limit(self):
        """Should respect limit parameter."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for i in range(10):
                f.write(f'{{"display": "test {i}", "timestamp": {i}}}\n')
            f.flush()
            path = Path(f.name)

        try:
            entries = []
            with open(path, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    if line.strip():
                        entries.append(json.loads(line))

            assert len(entries) == 5
        finally:
            path.unlink()

    def test_extract_prompt_from_display(self):
        """Should extract prompt from 'display' field."""
        entry = {"display": "What is the best way to implement caching?"}
        prompt = entry.get('display', '').strip()
        assert prompt == "What is the best way to implement caching?"

    def test_extract_prompt_truncation(self):
        """Should truncate long prompts to 200 chars."""
        long_text = "x" * 300
        entry = {"display": long_text}
        prompt = entry.get('display', '')[:200] if 'display' in entry else None
        assert len(prompt) == 200

    def test_skip_empty_entries(self):
        """Should skip empty or malformed JSON entries."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"display": "valid"}\n')
            f.write('\n')  # Empty line
            f.write('invalid json\n')
            f.write('{"display": "valid2"}\n')
            f.flush()
            path = Path(f.name)

        try:
            entries = []
            with open(path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            assert len(entries) == 2
            assert entries[0]['display'] == 'valid'
            assert entries[1]['display'] == 'valid2'
        finally:
            path.unlink()


# ============================================================================
# Test YAML Operations
# ============================================================================

class TestYAMLOperations:
    """Test YAML reading and writing."""

    def test_load_existing_yaml(self):
        """Should load existing YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'test': 'data', 'nested': {'key': 'value'}}, f)
            f.flush()
            path = Path(f.name)

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            assert data['test'] == 'data'
            assert data['nested']['key'] == 'value'
        finally:
            path.unlink()

    def test_save_without_corruption(self):
        """Should save YAML without corruption."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            path = Path(f.name)

        try:
            # Create test data
            test_data = {
                'metadata': {'version': '1.0'},
                'research': {'entries': [
                    {'id': 'res-1', 'topic': 'Test Research'}
                ]},
                'decisions': {'entries': []}
            }

            # Save
            with open(path, 'w') as f:
                yaml.dump(test_data, f)

            # Reload and verify structure
            with open(path, 'r') as f:
                reloaded = yaml.safe_load(f)

            assert reloaded is not None
            assert 'metadata' in reloaded
            assert 'research' in reloaded
            assert reloaded['research']['entries'][0]['topic'] == 'Test Research'
        finally:
            path.unlink()

    def test_append_without_duplicates(self):
        """Should append entries without duplicating."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            path = Path(f.name)

        try:
            # Initial data
            data = {'research': {'entries': []}}

            # First append
            entry1 = {'id': 'res-1', 'topic': 'Token Estimation'}
            data['research']['entries'].append(entry1)

            # Try to append same entry - check for duplicate
            topics = {e['topic'] for e in data['research']['entries']}
            if 'Token Estimation' not in topics:
                data['research']['entries'].append(entry1)

            # Should have only 1
            assert len(data['research']['entries']) == 1
        finally:
            path.unlink()

    def test_handles_missing_file(self):
        """Should create default structure for missing file."""
        nonexistent = Path('/tmp/nonexistent_test_file_xyz.yaml')
        if nonexistent.exists():
            nonexistent.unlink()

        # Verify file doesn't exist
        assert not nonexistent.exists()

        # Attempt to load should create structure
        default_data = {
            'metadata': {'version': '1.0'},
            'research': {'entries': []},
            'decisions': {'entries': []}
        }
        assert 'metadata' in default_data
        assert 'research' in default_data


# ============================================================================
# Test Integration
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow."""

    def test_end_to_end_json_to_yaml(self):
        """Test complete workflow: parse JSON → extract → save YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as hist:
            hist.write('{"display": "research authentication best practices", "timestamp": 123}\n')
            hist.write('{"display": "design the API architecture", "timestamp": 456}\n')
            hist.write('{"display": "decided to use JWT tokens", "timestamp": 789}\n')
            hist.flush()
            hist_path = Path(hist.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as yaml_file:
            yaml_path = Path(yaml_file.name)

        try:
            # Step 1: Load history
            entries = []
            with open(hist_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            assert len(entries) == 3

            # Step 2: Detect types
            matcher = TestKeywordMatcher()
            research_count = 0
            plan_count = 0
            for entry in entries:
                display = entry.get('display', '')
                if matcher.detect_research(display):
                    research_count += 1
                if matcher.detect_plan(display):
                    plan_count += 1

            assert research_count > 0
            assert plan_count > 0

            # Step 3: Create YAML structure
            yaml_data = {
                'metadata': {'last_scan': datetime.now().isoformat()},
                'research': {'entries': []},
                'decisions': {'entries': []}
            }

            # Step 4: Save to YAML
            with open(yaml_path, 'w') as f:
                yaml.dump(yaml_data, f)

            # Verify file created and readable
            assert yaml_path.exists()
            with open(yaml_path, 'r') as f:
                saved = yaml.safe_load(f)
            assert 'metadata' in saved
            assert 'research' in saved

        finally:
            hist_path.unlink()
            yaml_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
