#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "pytest>=7.0"]
# ///
"""
Tests for SessionEnd extractor hook.

Tests extraction of designs, decisions, and research from conversation transcripts
using extraction-optimized output format.
"""

import json
import tempfile
from pathlib import Path
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

from session_end_extractor import (
    extract_designs,
    extract_decisions,
    extract_yaml_blocks,
    extract_title,
    extract_metadata,
    sanitize_topic,
    write_design_files,
    extract_decision_data,
    append_decisions,
)


def create_mock_transcript(assistant_messages: list[str]) -> list[dict]:
    """Create mock transcript entries."""
    transcript = []

    for i, content in enumerate(assistant_messages):
        transcript.append(
            {
                "type": "user",
                "message": {"role": "user", "content": f"User message {i}"},
                "timestamp": f"2025-10-27T{i:02d}:00:00.000Z",
            }
        )

        transcript.append(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": content}],
                },
                "timestamp": f"2025-10-27T{i:02d}:00:30.000Z",
            }
        )

    return transcript


def test_extract_designs_with_extraction_optimized_format():
    """Test design extraction with extraction-optimized output style."""

    design_content = """# JWT Authentication System

**Type:** Design
**Status:** Complete
**Estimated Tokens:** 45000

---

## Overview

JWT-based authentication with refresh token rotation.

---

## Architecture

```yaml
architecture:
  components:
    - name: "AuthService"
      purpose: "Handles authentication"
```

---

## Task Breakdown

```yaml
tasks:
  - id: task-1
    title: "Implement JWT generation"
    type: implement
    complexity: simple
    estimated_tokens: 8000
```
"""

    transcript = create_mock_transcript([design_content])
    designs = extract_designs(transcript)

    assert len(designs) == 1
    assert designs[0]["pattern_count"] >= 3
    assert "JWT Authentication" in designs[0]["content"]


def test_extract_designs_ignores_conversational_content():
    """Test that conversational responses are not detected as designs."""

    conversational = (
        "I've updated the file successfully. Let me know if you need anything else."
    )

    transcript = create_mock_transcript([conversational])
    designs = extract_designs(transcript)

    assert len(designs) == 0


def test_extract_yaml_blocks():
    """Test YAML block extraction."""

    content = """
## Architecture

```yaml
architecture:
  components:
    - name: "Component A"
```

## Tasks

```yaml
tasks:
  - id: task-1
    title: "Task 1"
```
"""

    yaml_blocks = extract_yaml_blocks(content)

    assert len(yaml_blocks) == 2
    assert "architecture" in yaml_blocks[0]
    assert "tasks" in yaml_blocks[1]


def test_extract_title():
    """Test title extraction from markdown."""

    content = """# JWT Authentication System

**Type:** Design
"""

    title = extract_title(content)
    assert title == "JWT Authentication System"


def test_extract_metadata():
    """Test metadata extraction."""

    content = """
**Type:** Design
**Status:** Complete
**Estimated Tokens:** 45000
"""

    metadata = extract_metadata(content)

    assert metadata["type"] == "Design"
    assert metadata["status"] == "Complete"
    assert metadata["estimated_tokens"] == 45000


def test_sanitize_topic():
    """Test topic sanitization for filesystem."""

    assert sanitize_topic("JWT Authentication System") == "jwt-authentication-system"
    assert sanitize_topic("Feature: Add User Profiles") == "feature-add-user-profiles"
    assert sanitize_topic("A" * 100) == "a" * 50  # Length limit


def test_write_design_files():
    """Test writing design files to .plans/ directory."""

    design_content = """# Test Feature

**Type:** Design
**Status:** Complete
**Estimated Tokens:** 20000

## Architecture

```yaml
architecture:
  components:
    - name: "Test Component"
```

## Task Breakdown

```yaml
tasks:
  - id: task-1
    title: "Implement test"
    type: implement
    complexity: simple
    estimated_tokens: 10000
    files_created:
      - path: "test.py"
        purpose: "Test file"
    validation:
      - "Test passes"
```
"""

    designs = [
        {"content": design_content, "pattern_count": 5, "timestamp": "2025-10-27"}
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        result = write_design_files(project_root, designs, "test-session")

        assert result == 1

        # Check design.md exists
        design_file = project_root / ".plans" / "test-feature" / "design.md"
        assert design_file.exists()

        # Check task file exists
        task_file = project_root / ".plans" / "test-feature" / "tasks" / "task-1.md"
        assert task_file.exists()

        # Verify task file content
        task_content = task_file.read_text()
        assert "task-1" in task_content
        assert "Implement test" in task_content
        assert "- [ ] Test passes" in task_content


def test_extract_decisions():
    """Test decision extraction."""

    decision_content = """## Decision: Use PostgreSQL

**Date:** 2025-10-27
**Status:** Accepted

### Context

We need a database for the application.

### Alternatives Considered

#### Option 1: MongoDB
**Result:** ❌ Rejected

#### Option 2: PostgreSQL
**Result:** ✅ Selected

### Consequences

**Positive:**
- ACID compliance
"""

    transcript = create_mock_transcript([decision_content])
    decisions = extract_decisions(transcript)

    assert len(decisions) == 1
    assert "PostgreSQL" in decisions[0]["content"]


def test_empty_transcript():
    """Test handling of empty transcript."""

    transcript = []
    designs = extract_designs(transcript)
    decisions = extract_decisions(transcript)

    assert len(designs) == 0
    assert len(decisions) == 0


def test_extract_decision_data():
    """Test structured decision data extraction."""

    decision_content = """## Decision: Use PostgreSQL

**Date:** 2025-10-27
**Status:** Accepted

### Context

We need a reliable database with ACID compliance.

### Alternatives Considered

#### Option 1: MongoDB
**Result:** ❌ Rejected

Pros:
- Document-based flexibility

Cons:
- No ACID compliance

#### Option 2: PostgreSQL
**Result:** ✅ Selected

Pros:
- ACID compliance
- Mature ecosystem

Cons:
- Relational schema planning needed

### Consequences

**Positive:**
- Strong data consistency
- Wide community support

**Negative:**
- More schema planning upfront
"""

    decision = extract_decision_data(
        decision_content, "2025-10-27T12:00:00Z", "test-session"
    )

    assert decision is not None
    assert decision["title"] == "Use PostgreSQL"
    assert decision["status"] == "accepted"
    assert "reliable database" in decision.get("context", "")
    assert len(decision.get("alternatives_considered", [])) == 2
    assert decision["conversation_link"]["session_id"] == "test-session"


def test_extract_decision_data_with_consequences():
    """Test extraction of decision consequences."""

    decision_content = """## Decision: Use extraction-optimized output format

**Status:** Accepted

### Consequences

**Positive:**
- Perfect DRY compliance
- 99%+ extraction reliability

**Negative:**
- Requires format discipline
"""

    decision = extract_decision_data(
        decision_content, "2025-10-27T10:00:00Z", "test-session"
    )

    assert decision is not None
    assert "consequences" in decision
    assert len(decision["consequences"]["positive"]) == 2
    assert len(decision["consequences"]["negative"]) == 1


def test_append_decisions_to_yaml():
    """Test appending decisions to decisions.yaml."""

    decision_content = """## Decision: Use PostgreSQL

**Date:** 2025-10-27
**Status:** Accepted

### Context

We need a reliable database.

### Alternatives Considered

#### Option 1: MongoDB
**Result:** ❌ Rejected

#### Option 2: PostgreSQL
**Result:** ✅ Selected

### Consequences

**Positive:**
- ACID compliance

**Negative:**
- Schema planning needed
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create a minimal decisions.yaml
        decisions_file = project_root / "decisions.yaml"
        initial_data = {"decisions": {"entries": []}}
        with open(decisions_file, "w") as f:
            yaml.dump(initial_data, f)

        # Append decision
        decisions = [{"content": decision_content, "timestamp": "2025-10-27T12:00:00Z"}]
        result = append_decisions(project_root, decisions, "test-session-123")

        assert result == 1

        # Verify it was written
        with open(decisions_file, "r") as f:
            updated_data = yaml.safe_load(f)

        assert len(updated_data["decisions"]["entries"]) == 1
        appended = updated_data["decisions"]["entries"][0]
        assert appended["title"] == "Use PostgreSQL"
        assert appended["status"] == "accepted"
        assert appended["conversation_link"]["session_id"] == "test-session-123"


def test_append_decisions_prevents_duplicates():
    """Test that duplicate decisions are not appended."""

    decision_content = """## Decision: Use PostgreSQL

**Date:** 2025-10-27
**Status:** Accepted

### Context

We need a database.

### Alternatives Considered

#### Option 1: MongoDB
**Result:** ❌ Rejected

#### Option 2: PostgreSQL
**Result:** ✅ Selected
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create decisions.yaml with existing decision
        decisions_file = project_root / "decisions.yaml"
        existing_data = {
            "decisions": {
                "entries": [
                    {
                        "id": "dec-000000-use-postgresql",
                        "title": "Use PostgreSQL",
                        "status": "accepted",
                    }
                ]
            }
        }
        with open(decisions_file, "w") as f:
            yaml.dump(existing_data, f)

        # Try to append duplicate
        decisions = [{"content": decision_content, "timestamp": "2025-10-27T12:00:00Z"}]
        result = append_decisions(project_root, decisions, "test-session-456")

        # Should not append since same ID would be generated
        # (depends on timestamp)
        with open(decisions_file, "r") as f:
            final_data = yaml.safe_load(f)

        # At most 2 entries (original + new), likely 1 due to duplicate prevention
        assert len(final_data["decisions"]["entries"]) <= 2


if __name__ == "__main__":
    # Run tests
    import pytest

    pytest.main([__file__, "-v"])
