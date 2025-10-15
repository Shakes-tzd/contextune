# Changelog

All notable changes to SlashSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-15

**Status: Beta Release**

### Added
- 3-tier detection cascade (Keyword → Model2Vec → Semantic Router)
- Keyword matching tier (0.02ms P95 latency, 60% coverage)
- Model2Vec embedding tier (0.2ms P95 latency, 30% coverage)
- Semantic Router tier (50ms P95 latency, 10% coverage)
- UserPromptSubmit hook for intent detection
- 26 command mappings out of the box
- Intent mappings for SuperClaude commands (`/sc:*`)
- Parallel development workflow commands:
  - `/slashsense:parallel:plan` - Document development plans
  - `/slashsense:parallel:execute` - Execute parallel development with git worktrees
  - `/slashsense:parallel:status` - Monitor parallel task progress
  - `/slashsense:parallel:cleanup` - Clean up completed worktrees
- Configuration command: `/slashsense:config`
- Statistics command: `/slashsense:stats`
- Automatic subagent spawning for parallel execution
- GitHub integration (issue creation, labeling, tracking)
- Git worktree management for isolated development
- Custom pattern support via `user_patterns.json`
- Confidence scoring system
- Natural language aliases
- Context-aware keyword detection
- Lazy model loading for performance
- Comprehensive documentation (README, commands, architecture)
- MIT license
- MkDocs documentation site
- Testing suite with pytest
- Code quality tooling (ruff, mypy)
- UV package manager integration
- PEP 723 inline script metadata support

### Documentation
- Complete README with features, installation, usage
- Individual command documentation files
- Architecture documentation
- CLAUDE.md development guide
- PUBLISHING.md marketplace guide
- API documentation with mkdocstrings
- Troubleshooting guide
- Performance benchmarks

### Infrastructure
- GitHub repository setup
- Plugin manifest (plugin.json)
- Marketplace manifest (marketplace.json)
- Hooks configuration (hooks.json)
- Python project configuration (pyproject.toml)
- Git ignore configuration
- Code formatting and linting setup
- Type checking configuration
- Test infrastructure

## [0.0.1] - 2025-10-14

### Added
- Initial project structure
- Basic plugin scaffolding
- Development environment setup

[Unreleased]: https://github.com/Shakes-tzd/slashsense/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Shakes-tzd/slashsense/releases/tag/v0.1.0
[0.0.1]: https://github.com/Shakes-tzd/slashsense/releases/tag/v0.0.1
