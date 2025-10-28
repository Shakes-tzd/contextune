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
sys.path.insert(0, str(Path(__file__).parent.parent / 'hooks'))

from session_end_extractor import (
    extract_designs,
    extract_decisions,
    extract_yaml_blocks,
    extract_title,
    extract_metadata,
    sanitize_topic,
    write_design_files
)

def create_mock_transcript(assistant_messages: list[str]) -> list[dict]:
    """Create mock transcript entries."""
    transcript = []

    for i, content in enumerate(assistant_messages):
        transcript.append({
            'type': 'user',
            'message': {'role': 'user', 'content': f'User message {i}'},
            'timestamp': f'2025-10-27T{i:02d}:00:00.000Z'
        })

        transcript.append({
            'type': 'assistant',
            'message': {
                'role': 'assistant',
                'content': [{'type': 'text', 'text': content}]
            },
            'timestamp': f'2025-10-27T{i:02d}:00:30.000Z'
        })

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
    assert designs[0]['pattern_count'] >= 3
    assert 'JWT Authentication' in designs[0]['content']

def test_extract_designs_ignores_conversational_content():
    """Test that conversational responses are not detected as designs."""

    conversational = "I've updated the file successfully. Let me know if you need anything else."

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
    assert 'architecture' in yaml_blocks[0]
    assert 'tasks' in yaml_blocks[1]

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

    assert metadata['type'] == 'Design'
    assert metadata['status'] == 'Complete'
    assert metadata['estimated_tokens'] == 45000

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

    designs = [{'content': design_content, 'pattern_count': 5, 'timestamp': '2025-10-27'}]

    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        result = write_design_files(project_root, designs, 'test-session')

        assert result == 1

        # Check design.md exists
        design_file = project_root / '.plans' / 'test-feature' / 'design.md'
        assert design_file.exists()

        # Check task file exists
        task_file = project_root / '.plans' / 'test-feature' / 'tasks' / 'task-1.md'
        assert task_file.exists()

        # Verify task file content
        task_content = task_file.read_text()
        assert 'task-1' in task_content
        assert 'Implement test' in task_content
        assert '- [ ] Test passes' in task_content

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
    assert 'PostgreSQL' in decisions[0]['content']

def test_empty_transcript():
    """Test handling of empty transcript."""

    transcript = []
    designs = extract_designs(transcript)
    decisions = extract_decisions(transcript)

    assert len(designs) == 0
    assert len(decisions) == 0

if __name__ == '__main__':
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])
