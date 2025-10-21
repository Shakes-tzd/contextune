# Changelog

All notable changes to SlashSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-10-21

**Status: Haiku Agent Architecture Release - 81% Cost Reduction + 2x Speedup**

### Added

**Three-Tier Intelligence Architecture:**
- Tier 1 (Skills): Sonnet for guidance and expertise (20% of work)
- Tier 2 (Orchestration): Sonnet for planning and coordination
- Tier 3 (Execution): Haiku agents for cost-optimized task execution (80% of work)
- **Result**: 81% cost reduction ($1,680/year → $328/year for 1,200 workflows)
- **Result**: 2x performance improvement (Haiku 1-2s vs Sonnet 3-5s response time)

**Haiku Agents (5 Specialized Agents):**
- `parallel-task-executor`: Autonomous feature implementation ($0.04 vs $0.27 Sonnet)
- `worktree-manager`: Git worktree lifecycle management ($0.008 vs $0.06 Sonnet)
- `issue-orchestrator`: GitHub issue management ($0.01 vs $0.08 Sonnet)
- `test-runner`: Autonomous test execution and reporting ($0.02 vs $0.15 Sonnet)
- `performance-analyzer`: Workflow benchmarking and optimization ($0.015 vs $0.12 Sonnet)

**Cost Tracking & Optimization:**
- Real-time cost comparison (Sonnet vs Haiku)
- Cost savings dashboard in workflow reports
- ROI calculator for annual projections
- Cost per task/minute/workflow metrics
- CSV-based cost tracking system

**Enhanced Documentation:**
- `HAIKU_AGENT_ARCHITECTURE.md` - Complete three-tier architecture spec
- `AGENT_INTEGRATION_GUIDE.md` - Integration patterns and best practices
- `COST_OPTIMIZATION_GUIDE.md` - Cost tracking, ROI analysis, optimization strategies
- `MIGRATION_GUIDE_v0.3.0.md` - Upgrade guide from v0.2.0

### Changed
- Updated `slashsense-parallel-execute` to use Haiku agents instead of generic Task tool
- Enhanced `performance-optimizer` skill with cost tracking capabilities
- Updated plugin.json to v0.3.0 with new description and keywords

### Performance
- **Cost**: 81% reduction per workflow (5 tasks: $0.274 vs $1.404)
- **Speed**: 2x faster agent response times
- **Scalability**: Same 200K context window as Sonnet
- **Quality**: Identical quality for execution tasks

### Documentation
- Added agent specifications (5 markdown files, ~90KB total)
- Added integration guides (2 markdown files, ~65KB)
- Updated Skills with cost optimization guidance
- Added cost tracking examples and calculators

## [0.2.0] - 2025-10-21

**Status: AI-Powered Skills Release**

### Added

**AI-Powered Skills (4 Autonomous Skills):**
- `parallel-development-expert`: Autonomous guidance on parallelizing development tasks
- `intent-recognition`: Helps users discover SlashSense capabilities
- `git-worktree-master`: Expert troubleshooting for git worktree issues
- `performance-optimizer`: Analyzes and optimizes parallel workflow performance

**Skills Features:**
- Model-invoked (Claude decides when to activate based on context)
- Autonomous expert guidance without user having to ask
- Integration with parallel development workflows
- Comprehensive documentation and examples

**Enhanced Documentation:**
- `SKILLS_ENHANCEMENT.md` - Technical architecture of Skills system
- `QUICKSTART_SKILLS.md` - 5-minute quick start guide
- `skills/README.md` - Complete user guide for Skills
- Skills-specific documentation (4 markdown files, ~2,244 lines)

**Parallel Setup Optimization:**
- O(1) parallel setup (constant time regardless of task count)
- Each subagent creates own issue and worktree autonomously
- 30-63% faster setup time (5 tasks: 32s saved, 20 tasks: 152s saved)
- `PARALLEL_SETUP_PATTERN.md` documentation

### Changed
- Updated plugin.json to v0.2.0
- Updated README with prominent Skills section
- Enhanced `slashsense-parallel-execute` with parallel setup pattern

### Documentation
- Skills architecture and integration guides
- Parallel setup optimization documentation
- Enhanced user documentation with Skills examples

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
