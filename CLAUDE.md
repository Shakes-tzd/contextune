# Contextune Development Guide

## Project Overview

Contextune is a Claude Code plugin that provides natural language to slash command mapping. It uses a 3-tier detection cascade (keyword → Model2Vec → Semantic Router) to detect user intent and suggest appropriate slash commands.

**Core Technology:**
- Python 3.10+ with UV for dependency management
- Claude Code plugin architecture (hooks system)
- Machine learning: Model2Vec embeddings + Semantic Router
- Documentation: MkDocs with mkdocstrings

## Critical Development Rules

### Package Management - UV Only

**ALWAYS use UV for Python operations:**
```bash
# Run scripts
uv run script.py

# Run with dependencies
uv run --with pytest pytest

# Add dependencies
uv add package-name

# Add dev dependencies  
uv add --dev package-name

# Sync environment
uv sync

# Run module
uv run -m pytest
```

**NEVER use:**
- `pip install` - use `uv add`
- `python script.py` - use `uv run script.py`
- `poetry` or `conda` - UV only

### UV Script Format (PEP 723)

All standalone scripts MUST use inline script metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "model2vec>=0.3.0",
#     "numpy>=1.24.0"
# ]
# ///

# Script code here
```

**Why:** UV automatically creates ephemeral venvs with correct dependencies. This is how Claude Code hooks work.

## Project Structure

```
contextune/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata (name, version, hooks)
├── hooks/
│   ├── hooks.json               # Hook registrations for Claude Code
│   └── user_prompt_submit.py   # Main intent detection hook
├── lib/
│   ├── keyword_matcher.py       # Tier 1: Regex-based (0.02ms)
│   ├── model2vec_matcher.py     # Tier 2: Embeddings (0.2ms)
│   ├── semantic_router_matcher.py # Tier 3: LLM-based (50ms)
│   └── unified_detector.py      # Coordinates all 3 tiers
├── data/
│   ├── intent_mappings.json     # Base command → pattern mappings
│   └── user_patterns.json       # User customizations (auto-generated)
├── commands/
│   ├── contextune-config.md     # /contextune:config command
│   └── contextune-stats.md      # /contextune:stats command
├── tests/
│   ├── test_keyword.py
│   ├── test_model2vec.py
│   ├── test_semantic_router.py
│   └── test_unified.py
├── docs/
│   ├── index.md                 # MkDocs landing page
│   ├── installation.md
│   ├── usage.md
│   ├── architecture.md
│   └── api/                     # Auto-generated API docs
├── pyproject.toml               # UV + MkDocs configuration
├── CLAUDE.md                    # This file
├── README.md                    # GitHub landing page
└── LICENSE                      # MIT
```

## Development Workflow

### 1. Adding Dependencies

```bash
# Core dependencies
uv add model2vec
uv add semantic-router
uv add numpy

# Dev dependencies
uv add --dev pytest
uv add --dev mkdocs
uv add --dev mkdocs-material
uv add --dev mkdocstrings[python]
uv add --dev ruff
uv add --dev mypy
```

### 2. Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_keyword.py

# Run with coverage
uv run pytest --cov=lib --cov-report=html

# Run with verbose output
uv run pytest -v
```

### 3. Testing Individual Matchers

Each matcher has built-in tests:

```bash
# Test keyword matcher
uv run lib/keyword_matcher.py

# Test Model2Vec matcher
uv run lib/model2vec_matcher.py

# Test semantic router matcher
uv run lib/semantic_router_matcher.py
```

### 4. Testing the Hook

Simulate Claude Code calling the hook:

```bash
# Test with sample prompt
echo '{"prompt":"analyze my code please"}' | uv run hooks/user_prompt_submit.py

# Expected output (JSON):
# {"continue": true, "feedback": "<contextune_detection>...", "suppressOutput": false}
```

### 5. Local Plugin Installation

```bash
# Install plugin locally for testing
# In Claude Code:
/plugin install contextune@local

# Verify installation
/plugin list

# Test with natural language
# Just type: "can you review my code"
# Contextune should detect and suggest /sc:analyze
```

### 6. Documentation Development

```bash
# Build docs locally
uv run mkdocs build

# Serve docs with live reload
uv run mkdocs serve
# Visit http://localhost:8000

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

## Code Quality Standards

### Linting with Ruff

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Type Checking with mypy

```bash
# Type check all files
uv run mypy lib/

# Strict mode
uv run mypy --strict lib/keyword_matcher.py
```

### Pre-commit Checks

Before committing, always run:

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Run tests
uv run pytest

# Type check
uv run mypy lib/
```

## Plugin Development Patterns

### Hook Contract

**Input (stdin JSON):**
```json
{
  "prompt": "user's natural language input",
  "session_id": "unique-session-id",
  "timestamp": "2025-10-14T10:30:00Z"
}
```

**Output (stdout JSON):**
```json
{
  "continue": true,
  "feedback": "Message shown to Claude",
  "suppressOutput": false
}
```

**Exit codes:**
- `0`: Success, continue normal flow
- `1`: Error (logs to stderr, continues anyway)
- `2`: Block action (for PreToolUse hooks only)

### Adding New Commands

1. Create markdown file in `commands/`:

```markdown
---
name: contextune:mycommand
description: Brief description
---

# Command Name

Full documentation here.

## Usage
\```
/contextune:mycommand [args]
\```
```

2. Add to `.claude-plugin/plugin.json` if needed
3. Test: `/contextune:mycommand`

### Adding New Matchers

1. Create `lib/my_matcher.py`:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["your-deps"]
# ///

from dataclasses import dataclass
from typing import Optional

@dataclass
class IntentMatch:
    command: str
    confidence: float
    method: str
    latency_ms: float
    matched_patterns: list[str]

class MyMatcher:
    def is_available(self) -> bool:
        """Check if dependencies are available."""
        pass
    
    def match(self, text: str) -> Optional[IntentMatch]:
        """Match text to command."""
        pass

if __name__ == "__main__":
    # Self-test code
    pass
```

2. Integrate in `lib/unified_detector.py`
3. Add tests in `tests/test_my_matcher.py`

## Documentation Standards

### Docstring Format (Google Style)

```python
def match(self, text: str) -> Optional[IntentMatch]:
    """
    Match natural language text to a slash command.
    
    Uses a 3-tier cascade: keyword → Model2Vec → Semantic Router.
    Falls through to next tier if no match found.
    
    Args:
        text: User's natural language query (e.g., "analyze my code")
        
    Returns:
        IntentMatch if command detected with confidence >= 0.7,
        None otherwise.
        
    Example:
        >>> detector = UnifiedDetector()
        >>> result = detector.match("review my code")
        >>> print(result.command)
        '/sc:analyze'
        
    Note:
        First call may be slow (~50ms) as models load lazily.
        Subsequent calls are fast (<2ms with keyword match).
    """
    pass
```

### MkDocs Configuration

MkDocs is configured in `pyproject.toml` under `[tool.mkdocs]`.

**Key features:**
- Material theme with dark mode
- Auto-generated API docs via mkdocstrings
- Code highlighting with Pygments
- Search enabled
- GitHub integration

**Adding docs pages:**

1. Create markdown file in `docs/`
2. Add to navigation in `mkdocs.yml` (auto-generated from pyproject.toml)
3. Build: `uv run mkdocs build`

## Performance Requirements

### Latency Targets

- **Keyword matching:** <0.1ms (P95)
- **Model2Vec matching:** <1ms (P95)
- **Semantic Router matching:** <100ms (P95)
- **Total hook execution:** <2ms (P95) for keyword path

**Why these matter:** Hooks run on EVERY user prompt. Slow hooks = bad UX.

### Testing Performance

```python
import time

def benchmark_matcher(matcher, queries, iterations=100):
    """Benchmark matcher performance."""
    latencies = []
    
    for _ in range(iterations):
        for query in queries:
            start = time.perf_counter()
            result = matcher.match(query)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
    
    print(f"P50: {sorted(latencies)[len(latencies)//2]:.2f}ms")
    print(f"P95: {sorted(latencies)[int(len(latencies)*0.95)]:.2f}ms")
    print(f"P99: {sorted(latencies)[int(len(latencies)*0.99)]:.2f}ms")
```

## Git Workflow

### Branch Strategy

- `main`: Stable, released versions
- `develop`: Integration branch for features
- `feature/name`: Feature development
- `fix/name`: Bug fixes

### Commit Messages

Use conventional commits:

```bash
feat: add Model2Vec matcher with 0.2ms latency
fix: handle empty prompts in keyword matcher
docs: add architecture overview to MkDocs
test: add comprehensive keyword matcher tests
chore: update dependencies to latest versions
```

### Versioning

Follow semantic versioning (SemVer):

- `1.0.0`: Major release (breaking changes)
- `1.1.0`: Minor release (new features)
- `1.0.1`: Patch release (bug fixes)

Update version in:
1. `.claude-plugin/plugin.json`
2. `pyproject.toml`
3. Create git tag: `git tag v1.0.0`

## Debugging

### Enable Debug Logging

Add to `hooks/user_prompt_submit.py`:

```python
import sys
import json

def debug_log(message: str, data: dict = None):
    """Log to stderr (visible in Claude Code)."""
    log_entry = {"message": message}
    if data:
        log_entry["data"] = data
    print(json.dumps(log_entry), file=sys.stderr)

# Usage
debug_log("Hook triggered", {"prompt": prompt[:50]})
```

### Common Issues

**Issue:** "Module not found: model2vec"
**Fix:** `uv sync` to install dependencies

**Issue:** "Hook not firing"
**Fix:** Check `hooks/hooks.json` is valid JSON

**Issue:** "Model2Vec slow on first run"
**Expected:** Model downloads on first use (~8MB), cached after

**Issue:** "Semantic Router not working"
**Fix:** Set environment variable: `export COHERE_API_KEY=...`

## Release Checklist

Before releasing new version:

- [ ] Run all tests: `uv run pytest`
- [ ] Check types: `uv run mypy lib/`
- [ ] Format code: `uv run ruff format .`
- [ ] Update version in plugin.json and pyproject.toml
- [ ] Update CHANGELOG.md
- [ ] Build docs: `uv run mkdocs build`
- [ ] Test plugin locally: `/plugin install @local`
- [ ] Test with 10+ natural language queries
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push to GitHub: `git push --tags`
- [ ] Deploy docs: `uv run mkdocs gh-deploy`
- [ ] Announce on Discord/Reddit

## Security Considerations

### API Keys

**NEVER commit API keys to git:**

```bash
# Set environment variables
export COHERE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Or use .env file (add to .gitignore!)
echo "COHERE_API_KEY=your-key" > .env
```

### Hook Safety

Hooks run automatically with user's permissions. Be careful:

- ✅ DO: Validate all inputs
- ✅ DO: Handle errors gracefully
- ✅ DO: Use try/except blocks
- ❌ DON'T: Execute arbitrary code
- ❌ DON'T: Make network calls without user consent
- ❌ DON'T: Modify files outside plugin directory

## Resources

### Documentation
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code)
- [UV Documentation](https://docs.astral.sh/uv/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Semantic Router](https://github.com/aurelio-labs/semantic-router)
- [Model2Vec](https://github.com/minishlab/model2vec)

### Community
- [Claude Code Discord](https://discord.gg/anthropic)
- [GitHub Discussions](https://github.com/yourusername/contextune/discussions)

### Examples
- [jeremylongshore/claude-code-plugins](https://github.com/jeremylongshore/claude-code-plugins)
- [wshobson/agents](https://github.com/wshobson/agents)
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)

## Quick Reference

```bash
# Development
uv sync                              # Install dependencies
uv run pytest                        # Run tests
uv run mkdocs serve                  # Preview docs

# Testing
uv run lib/keyword_matcher.py       # Test matcher
echo '{"prompt":"test"}' | uv run hooks/user_prompt_submit.py

# Quality
uv run ruff format .                 # Format code
uv run ruff check --fix .            # Lint & fix
uv run mypy lib/                     # Type check

# Documentation
uv run mkdocs build                  # Build docs
uv run mkdocs gh-deploy              # Deploy to GitHub Pages

# Plugin
/plugin install contextune@local     # Install locally
/plugin uninstall contextune         # Uninstall
```

---

**Remember:** Always use `uv run` for Python commands. Let UV manage dependencies automatically via inline script metadata. This is how Claude Code plugins work!