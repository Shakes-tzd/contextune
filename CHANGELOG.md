# Changelog

All notable changes to SlashSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.3] - 2025-10-25

**Status: Zero-Context Command Discovery Release**

### Added

**SessionStart Hook for Command Discovery:**
- Added `hooks/session_start.js` - Displays SlashSense commands at session start
- **Zero context overhead** - Uses `feedback` field (0 tokens, UI-only)
- Shows 7 key commands with descriptions
- Includes natural language examples
- Auto-displays on every session start, resume, clear, compact

### Benefits

**Context Optimization:**
- ✅ **0 tokens** vs 150 tokens for CLAUDE.md manual approach
- ✅ Command list visible to user without context cost
- ✅ Auto-updates when plugin changes (no manual editing)
- ✅ Works alongside Skills for comprehensive discovery

**User Experience:**
- ✅ Commands shown at every session start
- ✅ No setup required (works automatically)
- ✅ Reinforces natural language usage patterns
- ✅ Includes quick reference examples

**Architecture:**
- SessionStart hook: 0 tokens (feedback field)
- Skills: Contextual suggestions (when relevant)
- UserPromptSubmit: Intent detection (~20 tokens per match)
- **Total discovery overhead: ~20 tokens vs 150+ for static CLAUDE.md**

### Technical Details

**Hook Implementation:**
- Language: JavaScript (Node.js - guaranteed in Claude Code)
- Execution time: <10ms
- Output format: JSON with `feedback` field
- No `additionalContext` used (zero tokens)
- Registered in `hooks/hooks.json` under SessionStart event

**Comparison:**

| Approach | Token Cost | User Sees | Auto-Updates |
|----------|-----------|-----------|--------------|
| **SessionStart hook** | **0 tokens** ✅ | ✅ Every session | ✅ Yes |
| CLAUDE.md (manual) | 150 tokens ⚠️ | ✅ Always | ❌ Manual |
| Skills only | 0 tokens ✅ | ⚠️ Contextual | ✅ Yes |

**Recommended Stack:**
- SessionStart → Shows commands (0 tokens)
- Skills → Suggest usage (contextual)
- UserPromptSubmit → Detect intent (~20 tokens)

## [0.5.2] - 2025-10-25

**Status: Architecture Cleanup & Plugin Best Practices Release**

### Added

**Skills for Auto-Discovery:**
- `parallel-development-expert` - Proactively suggests parallelization when multiple tasks mentioned
- `intent-recognition` - Helps users discover SlashSense capabilities
- Skills automatically activate based on user context (no manual invocation)
- Zero-config discovery mechanism

### Changed

**Plugin Architecture Improvements:**
- `/ss:configure` - Converted from auto-modification to read-only guide
  - No longer automatically modifies user files (respects plugin boundaries)
  - Provides copy-paste snippets for optional manual customization
  - Explains trade-offs clearly (context cost vs benefits)
- Hook simplified to "suggest" mode only
  - Removed "verify" mode (sub-agent spawning)
  - Removed "auto" mode (auto-execution)
  - Hook now only adds context, Claude decides what to do
  - No user configuration needed (hardcoded behavior)

### Removed

- `/ss:intents` command (unnecessary complexity)
- `commands/slashsense-config.py` (Python dependency removed)
- `delegation_mode` configuration (no longer needed)
- `user_patterns.json` config file (hook has no configurable settings)
- Auto-modification of `~/.claude/CLAUDE.md` (anti-pattern)
- Auto-modification of `~/.claude/statusline.sh` (anti-pattern)

### Benefits

**Architecture:**
- ✅ Plugin is self-contained (no user file modifications)
- ✅ Skills provide automatic discovery (better than CLAUDE.md injection)
- ✅ Hook is simpler and faster (removed branching logic)
- ✅ Zero configuration required (works immediately after install)
- ✅ Follows Claude Code plugin best practices

**User Experience:**
- ✅ No setup needed - Skills activate automatically
- ✅ Claude always in control (intelligent decision-making)
- ✅ Lower context cost (~50 tokens vs 100s-1000s with sub-agents)
- ✅ Cleaner install/uninstall (no orphaned user file modifications)

**Developer Experience:**
- ✅ Simpler codebase (removed ~150 lines from hook)
- ✅ No Python dependency for config (just Bash/Python for hook logic)
- ✅ Easier to maintain (fewer modes, less complexity)

### Migration Notes

If you previously ran `/ss:configure`:
1. Manually remove SlashSense section from `~/.claude/CLAUDE.md` (optional)
2. Manually remove SlashSense section from `~/.claude/statusline.sh` (optional)
3. Skills now provide discovery automatically (better than static context)

## [0.5.1] - 2025-10-25

**Status: Command Shortening & Research Release**

### Added

**New Command:**
- `/ss:research` - Fast research using 3 parallel Haiku agents (1-2 min, ~$0.07)
  - Agent 1: Web research (latest trends, comparisons)
  - Agent 2: Codebase search (existing patterns, reuse opportunities)
  - Agent 3: Dependency analysis (what's installed, compatibility)
  - Returns comparison table + recommendation + next steps

**Shortened Command Names:**
- All commands shortened from `/slashsense:*` to `/ss:*` for faster typing
- `/ss:configure` - Setup persistent visibility
- `/ss:intents` - Configure intent detection
- `/ss:research` - Quick research (NEW)
- `/ss:plan` - Create parallel development plans
- `/ss:execute` - Execute plans in parallel
- `/ss:status` - Monitor parallel tasks
- `/ss:cleanup` - Clean up worktrees
- `/ss:stats` - View statistics
- `/ss:verify` - Verify detected commands

### Changed
- Updated status bar to show correct command names: `/ss:research | /ss:plan | /ss:execute`
- Updated CLAUDE.md with shortened names and research command
- Updated README and all documentation with new command names
- Plugin description updated to highlight quick research capability

### Benefits
- **Faster typing**: `/ss:*` vs `/slashsense:*` (60% shorter)
- **Quick research**: Answer technical questions in 1-2 min with parallel agents
- **Cost efficient**: Research costs ~$0.07 (3 Haiku agents vs 1 Sonnet ~$0.15)
- **Better UX**: Shorter commands more natural to type

## [0.5.0] - 2025-10-24

**Status: Discovery & Configuration Release - Multi-Layered Visibility**

### Added

**Configuration Command:**
- `/ss:configure` - One-time setup for persistent visibility
- Integrates SlashSense into CLAUDE.md (~150 tokens context at session start)
- Adds SlashSense commands to status bar (zero context, always visible)
- Creates backups before modifications (safe rollback)
- Validates plugin settings and skills
- Comprehensive error handling and rollback instructions

**Architecture Improvements:**
- Multi-layered discovery system (CLAUDE.md + Status Bar + Skills + Hook)
- Documented optimal discovery patterns in `.plans/ARCHITECTURE_IMPROVEMENTS_v0.5.1.md`
- Configuration specification in `.plans/CONFIGURE_COMMAND_SPEC.md`
- Implementation plan for cost optimization features in `.plans/IMPLEMENTATION_PLAN_v0.5.0.md`

**Discovery Enhancements:**
- CLAUDE.md integration for session-start awareness
- Status bar integration for persistent UI visibility
- Comprehensive research on Claude Code plugin architecture
- Context optimization strategies (~350 tokens passive overhead)

### Benefits
- **Visibility**: SlashSense always present through multiple mechanisms
- **Discoverability**: 95%+ users will see and discover features
- **Cost**: Minimal context overhead (~$0.001 per session)
- **User Control**: Requires permission, creates backups, provides rollback

### Documentation
- Complete configure command specification
- Discovery architecture analysis
- Context overhead analysis
- Implementation and testing guides

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
  - `/ss:plan` - Document development plans
  - `/ss:execute` - Execute parallel development with git worktrees
  - `/ss:status` - Monitor parallel task progress
  - `/ss:cleanup` - Clean up completed worktrees
- Configuration command: `/ss:intents`
- Statistics command: `/ss:stats`
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
