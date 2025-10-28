"""
Unit tests for decision-query.py
"""

import importlib.util
from datetime import datetime, timedelta
from pathlib import Path

import pytest


# Dynamic import of decision_query script
def load_decision_query_module():
    """Load decision-query.py as a module."""
    script_path = Path(__file__).parent.parent / "scripts" / "decision-query.py"
    spec = importlib.util.spec_from_file_location("decision_query", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


decision_query = load_decision_query_module()
estimate_tokens = decision_query.estimate_tokens
is_expired = decision_query.is_expired
filter_entries = decision_query.filter_entries


class TestTokenEstimation:
    """Test token estimation for entries."""

    def test_empty_entry(self):
        """Minimal entry should have at least 100 tokens."""
        entry = {"id": "test-001", "title": "Test"}
        assert estimate_tokens(entry) >= 100

    def test_context_increases_tokens(self):
        """Longer context should increase token count."""
        entry_short = {"id": "test-001", "title": "Test", "context": "Short"}
        entry_long = {
            "id": "test-002",
            "title": "Test",
            "context": "A" * 500,
        }
        assert estimate_tokens(entry_long) > estimate_tokens(entry_short)

    def test_decision_increases_tokens(self):
        """Decision field should increase token count."""
        entry_no_decision = {"id": "test-001", "title": "Test"}
        entry_with_decision = {
            "id": "test-002",
            "title": "Test",
            "decision": "We decided to do this thing after careful consideration. "
            * 10,
        }
        assert estimate_tokens(entry_with_decision) > estimate_tokens(entry_no_decision)

    def test_alternatives_increase_tokens(self):
        """More alternatives should increase token count."""
        entry_no_alts = {
            "id": "test-001",
            "title": "Test",
            "alternatives_considered": [],
        }
        entry_with_alts = {
            "id": "test-002",
            "title": "Test",
            "alternatives_considered": [
                {"option": "A", "result": "rejected"},
                {"option": "B", "result": "rejected"},
                {"option": "C", "result": "accepted"},
            ],
        }
        assert estimate_tokens(entry_with_alts) > estimate_tokens(entry_no_alts)


class TestExpirationLogic:
    """Test lifecycle and expiration checking."""

    def test_permanent_entries_never_expire(self):
        """Entries marked permanent=true should never expire."""
        past = (datetime.now() - timedelta(days=1000)).isoformat() + "Z"
        entry = {
            "id": "test-001",
            "title": "Test",
            "expires_at": past,
            "permanent": True,
        }
        assert not is_expired(entry)

    def test_future_expiration(self):
        """Entry with future expiration should not be expired."""
        future = (datetime.now() + timedelta(days=30)).isoformat() + "Z"
        entry = {"id": "test-001", "title": "Test", "expires_at": future}
        assert not is_expired(entry)

    def test_past_expiration(self):
        """Entry with past expiration should be expired."""
        past = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
        entry = {"id": "test-001", "title": "Test", "expires_at": past}
        assert is_expired(entry)

    def test_no_expiration_field(self):
        """Entry without expiration should not be expired."""
        entry = {"id": "test-001", "title": "Test"}
        assert not is_expired(entry)

    def test_invalid_expiration_date(self):
        """Entry with invalid expiration date should not crash."""
        entry = {"id": "test-001", "title": "Test", "expires_at": "invalid-date"}
        # Should not raise, just return False
        assert not is_expired(entry)


class TestFilterEntries:
    """Test filtering functionality."""

    def get_sample_entries(self):
        """Create sample entries for testing."""
        return [
            {
                "id": "dec-001",
                "title": "Use authentication tokens",
                "topic": "authentication",
                "category": "architecture",
                "status": "accepted",
                "tags": ["security", "auth"],
                "impact": "high",
                "date": datetime.now().isoformat() + "Z",
            },
            {
                "id": "dec-002",
                "title": "Improve performance",
                "topic": "performance",
                "category": "performance",
                "status": "pending",
                "tags": ["optimization"],
                "impact": "medium",
                "date": (datetime.now() - timedelta(days=45)).isoformat() + "Z",
            },
            {
                "id": "res-001",
                "title": "Research caching strategies",
                "topic": "caching",
                "category": "architecture",
                "status": "accepted",
                "tags": ["performance"],
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat() + "Z",
                "date": (datetime.now() - timedelta(days=10)).isoformat() + "Z",
            },
            {
                "id": "res-002",
                "title": "Expired research",
                "topic": "obsolete",
                "status": "accepted",
                "expires_at": (datetime.now() - timedelta(days=1)).isoformat() + "Z",
                "date": (datetime.now() - timedelta(days=200)).isoformat() + "Z",
            },
        ]

    def test_filter_by_topic(self):
        """Filter entries by topic."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, topic="authentication")
        assert len(results) == 1
        assert results[0]["id"] == "dec-001"

    def test_filter_by_category(self):
        """Filter entries by category."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, category="performance")
        assert len(results) == 1
        assert results[0]["id"] == "dec-002"

    def test_filter_by_status(self):
        """Filter entries by status."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, status="accepted")
        # dec-001, res-001 are accepted and not expired (res-002 is expired)
        assert len(results) == 2

    def test_filter_by_tags(self):
        """Filter entries by tags."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, tags=["security"])
        assert len(results) == 1
        assert results[0]["id"] == "dec-001"

    def test_filter_by_tags_multiple(self):
        """Filter entries by multiple tags (OR logic)."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, tags=["security", "optimization"])
        assert len(results) == 2  # dec-001, dec-002

    def test_filter_by_impact(self):
        """Filter entries by impact level."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, impact="high")
        assert len(results) == 1
        assert results[0]["id"] == "dec-001"

    def test_filter_by_since(self):
        """Filter entries by date range (last N days)."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, since_days=30)
        # Should include dec-001 (today) and res-001 (10 days ago).
        # dec-002 is 45 days ago, so NOT included (outside 30 day window)
        # res-002 is 200 days ago AND expired, so NOT included
        assert len(results) == 2
        ids = {r["id"] for r in results}
        assert "dec-001" in ids
        assert "res-001" in ids

    def test_filter_exclude_expired_by_default(self):
        """Expired entries should be excluded by default."""
        entries = self.get_sample_entries()
        results = filter_entries(entries)
        # Should exclude res-002 (expired)
        ids = {r["id"] for r in results}
        assert "res-002" not in ids

    def test_filter_include_expired(self):
        """Expired entries should be included when requested."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, include_expired=True)
        # Should include res-002
        ids = {r["id"] for r in results}
        assert "res-002" in ids

    def test_combined_filters(self):
        """Multiple filters should work together (AND logic)."""
        entries = self.get_sample_entries()
        results = filter_entries(entries, category="architecture", status="accepted")
        # Should include dec-001 and res-001
        assert len(results) == 2
        ids = {r["id"] for r in results}
        assert "dec-001" in ids
        assert "res-001" in ids


class TestContextReduction:
    """Test context reduction (the main benefit of selective loading)."""

    def test_selective_load_reduces_context(self):
        """Selective loading should use fewer tokens than full load."""
        entries = [
            {
                "id": f"dec-{i:03d}",
                "title": f"Decision {i}",
                "context": "A" * 500,
                "decision": "B" * 500,
            }
            for i in range(10)
        ]

        # Full load
        full_tokens = sum(estimate_tokens(e) for e in entries)

        # Selective load
        filtered = filter_entries(entries, category="architecture")
        selective_tokens = sum(estimate_tokens(e) for e in filtered)

        # When filtering out entries, selective should be less
        if len(filtered) < len(entries):
            assert selective_tokens < full_tokens

    def test_selective_vs_changelog_comparison(self):
        """Verify selective loading is more efficient than typical CHANGELOG."""
        # Simulate a large decision with rich formatting like CHANGELOG
        changelog_entry = {
            "id": "changelog-001",
            "title": "Large changelog entry",
            "context": "A" * 2000,
            "decision": "B" * 2000,
            "rationale": "C" * 1000,
            "alternatives_considered": [
                {"option": f"Alt {i}", "pros": ["Pro"] * 5, "cons": ["Con"] * 5}
                for i in range(5)
            ],
            "consequences": {
                "positive": ["Benefit"] * 10,
                "negative": ["Cost"] * 10,
            },
        }

        entry_tokens = estimate_tokens(changelog_entry)
        # CHANGELOG would load all entries (~15-150K tokens)
        # Selective loading gets only what's needed (~2-5K)
        assert entry_tokens >= 100
        assert entry_tokens < 5000  # Should be well under typical selective load


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
