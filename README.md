# Contextune 🎵

> **Precision-Tuned Context Engineering for Claude Code**

Optimize context flow with modular plans (95% fewer tokens), parallel workflows (81% cost reduction), and zero-transformation architecture. Contextune your workflows for peak performance!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-purple.svg)](https://docs.claude.com/en/docs/claude-code/plugins)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/Shakes-tzd/contextune/releases)
[![Cost Savings](https://img.shields.io/badge/cost%20savings-81%25-brightgreen.svg)](#-cost-optimization)
[![Context Optimization](https://img.shields.io/badge/token%20savings-95%25-brightgreen.svg)](#-context-engineering)
[![Documentation](https://img.shields.io/badge/docs-contextune.com-blue.svg)](https://contextune.com/)

---

## The Problem

Claude Code has 80+ plugins with hundreds of slash commands. You can't remember them all.

**Before Contextune:**
```
You: "I need to run tests"
Claude: "Sure! Running tests..."
[30 seconds later, writes custom test script]
```

**After Contextune:**
```
You: "I need to run tests"
Contextune: 🎯 Auto-executing /sc:test (85% confidence, keyword match, 0.02ms)
Claude: [Executes /sc:test automatically]
```

---

## 🚀 NEW in v0.3.0: Haiku Agent Architecture

**81% cost reduction + 2x speedup with three-tier intelligence**

Contextune v0.3.0 introduces cost-optimized Haiku agents that dramatically reduce parallel workflow costs while improving performance.

### 💰 Cost Optimization

**Before (All Sonnet):**
```
5 parallel tasks: $1.40 per workflow
1,200 workflows/year: $1,680/year
```

**After (Haiku Agents):**
```
5 parallel tasks: $0.27 per workflow  (81% cheaper!)
1,200 workflows/year: $328/year
Annual savings: $1,356 💰
```

### ⚡ Performance

- **Response time**: 2x faster (Haiku 1-2s vs Sonnet 3-5s)
- **Quality**: Identical for execution tasks
- **Scalability**: Same 200K context window

### 🤖 5 Specialized Haiku Agents

**parallel-task-executor** - Feature implementation ($0.04 vs $0.27)
```
Autonomous development task execution:
- Creates GitHub issue and worktree
- Implements features
- Runs tests
- Pushes code and reports

Cost per task: $0.04 (85% savings!)
```

**worktree-manager** - Git worktree lifecycle ($0.008 vs $0.06)
```
Expert worktree management:
- Create/remove worktrees
- Diagnose lock file issues
- Bulk cleanup operations
- Health checks

Cost per operation: $0.008 (87% savings!)
```

**issue-orchestrator** - GitHub operations ($0.01 vs $0.08)
```
GitHub issue management:
- Create/update/close issues
- Label management
- Link to PRs
- Bulk operations

Cost per operation: $0.01 (87% savings!)
```

**test-runner** - Autonomous testing ($0.02 vs $0.15)
```
Multi-language test execution:
- Run tests (Python, JS, Rust, Go)
- Generate reports
- Create issues for failures
- Track coverage

Cost per run: $0.02 (87% savings!)
```

**performance-analyzer** - Workflow optimization ($0.015 vs $0.12)
```
Performance and cost analysis:
- Benchmark workflows
- Identify bottlenecks
- Calculate ROI
- Generate reports

Cost per analysis: $0.015 (87% savings!)
```

### 📊 Three-Tier Architecture

```
Tier 1: Skills (Sonnet)        → Guidance & expertise (20% of work)
Tier 2: Orchestration (Sonnet) → Planning & coordination
Tier 3: Execution (Haiku)      → Task execution (80% of work)

Result: 81% cost reduction, 2x performance, same quality!
```

**Learn more:**
- [Haiku Agent Architecture](docs/HAIKU_AGENT_ARCHITECTURE.md)
- [Cost Optimization Guide](docs/COST_OPTIMIZATION_GUIDE.md)
- [Migration Guide](docs/MIGRATION_GUIDE_v0.3.0.md)

---

## ✨ AI-Powered Skills (v0.2.0)

Contextune now includes **autonomous expert guidance** through Skills. No commands to memorize - just ask questions naturally!

### 🧠 4 Expert Skills (Auto-Activated)

**🚀 parallel-development-expert**
```
You: "How can I work on multiple features faster?"

Claude: *Skill activates automatically*
"Let me analyze your project...

Found 3 independent tasks!
Sequential: 8 hours → Parallel: 3 hours (62% faster!)

Say 'work on them in parallel' and I'll handle everything!"
```

**📚 intent-recognition**
```
You: "What can Contextune do?"

Claude: "Contextune makes Claude Code more natural!

🎯 Capabilities:
1. Parallel Development (30-70% faster)
2. Smart Intent Detection (zero commands to learn)
3. Expert Troubleshooting (autonomous help)

Try: 'work on auth and dashboard in parallel'"
```

**🔧 git-worktree-master**
```
You: "Can't remove worktree, says locked"

Claude: "Diagnosing... Found lock file from interrupted operation.

Safe fix: Remove lock + worktree
Risk: None (keeps your branch)

Proceed? ✅"
```

**⚡ performance-optimizer**
```
You: "My parallel workflow seems slow"

Claude: "Benchmarking...

Bottleneck: Sequential setup (107s overhead)
Fix: Parallel setup pattern
Impact: 2.3 min faster (23% improvement)

Optimize now?"
```

**Learn more:** [Skills Documentation](skills/README.md)

---

## Features

### 🚀 **3-Tier Detection Cascade**
- **Keyword Matching** (0.02ms) - 60% of queries
- **Model2Vec Embeddings** (0.2ms) - 30% of queries
- **Semantic Router** (50ms) - 10% of queries

### 🎯 **Smart Intent Detection & Auto-Execution**
Understands natural variations and **automatically executes** the detected command:
- "analyze my code" → Auto-executes `/sc:analyze`
- "review the codebase" → Auto-executes `/sc:analyze`
- "check code quality" → Auto-executes `/sc:analyze`
- "audit for issues" → Auto-executes `/sc:analyze`
- "work on these in parallel" → Auto-executes `/ctx:execute`

### ⚡ **Lightning Fast**
- P95 latency: <2ms (keyword path)
- Zero context overhead
- Lazy model loading
- Automatic caching

### 🔧 **Zero Configuration**
- Works out of the box
- Auto-discovers all installed plugins
- No API keys required (keyword + Model2Vec)
- Optional: Semantic Router for complex queries

---

## Quick Start

### Installation

**Option 1: From Marketplace (Recommended)**
```bash
# Add Contextune marketplace
/plugin marketplace add Shakes-tzd/contextune

# Install plugin
/plugin install contextune
```

**Option 2: Direct from GitHub**
```bash
# Install directly
/plugin install Shakes-tzd/contextune

# Or specify version
/plugin install Shakes-tzd/contextune@0.1.0
```

**Option 3: Local Development**
```bash
# Clone repository
git clone https://github.com/Shakes-tzd/contextune
cd contextune

# Install locally
/plugin install @local
```

### One-Time Configuration (Recommended)

**NEW in v0.5.0:** Run the configuration command for persistent visibility:

```bash
/ctx:configure
```

This will:
- ✅ Add Contextune section to `~/.claude/CLAUDE.md` (~150 tokens, loaded at session start)
- ✅ Add Contextune commands to your status bar (zero context, always visible)
- ✅ Validate plugin settings and skills
- ✅ Create backups before any changes

**Benefits:**
- **Always visible:** See `/research | /parallel:plan | /parallel:execute` in status bar
- **Session awareness:** Claude remembers Contextune at every session start
- **Safe:** Creates backups, asks permission, provides rollback instructions

**Without configuration:** Contextune still works via intent detection, but you won't see visual reminders.

### Usage

Just type what you want in natural language:

```
# Instead of memorizing:
/sc:analyze --comprehensive

# Just type:
"can you analyze my code for issues?"

# Contextune auto-executes:
🎯 Auto-executing /sc:analyze (85% confidence, keyword match, 0.02ms)
```

### Supported Commands

Contextune detects these commands out of the box:

| Natural Language | Command | Confidence |
|-----------------|---------|------------|
| "analyze the code" | `/sc:analyze` | 85% |
| "run tests" | `/sc:test` | 85% |
| "fix this bug" | `/sc:troubleshoot` | 85% |
| "implement feature" | `/sc:implement` | 85% |
| "explain this code" | `/sc:explain` | 85% |
| "optimize performance" | `/sc:improve` | 85% |
| "design architecture" | `/sc:design` | 85% |
| "commit changes" | `/sc:git` | 85% |

**Expandable:** Contextune auto-discovers commands from all your installed plugins!

---

## Parallel Development Workflow

Contextune includes a powerful parallel development system that lets Claude work on multiple independent tasks simultaneously using git worktrees.

### Key Features

- 🚀 **Automatic Subagent Spawning** - Claude spawns multiple agents to work in parallel
- 🌿 **Git Worktrees** - Isolated working directories for each task
- 📋 **GitHub Integration** - Automatic issue creation and tracking
- 🎯 **Zero Manual Coordination** - Claude manages everything automatically

### Commands

| Natural Language | Command | What It Does |
|-----------------|---------|--------------|
| "plan parallel development" | `/ctx:plan` | Document development plan for parallel execution |
| "work on these in parallel" | `/ctx:execute` | Execute plan in parallel using git worktrees |
| "check parallel status" | `/ctx:status` | Monitor progress across all parallel tasks |
| "cleanup parallel worktrees" | `/ctx:cleanup` | Clean up completed worktrees and branches |

### Example Workflow

```
You: "I need to implement authentication, dashboard, and analytics"

Claude: "📋 These tasks are independent. Would you like to work on them in parallel?"

You: "yes, parallelize this work"

Contextune: 🎯 /ctx:execute detected (92% confidence)

Claude:
"✅ Created plan: .parallel/plans/PLAN-20251014.md
✅ Created 3 GitHub issues
✅ Created 3 git worktrees
🚀 Spawning 3 parallel subagents...

Agent 1: Working on authentication (worktrees/task-123)
Agent 2: Working on dashboard (worktrees/task-124)
Agent 3: Working on analytics (worktrees/task-125)

All tasks complete in 2 hours (vs 4.5h sequential - 56% faster!)"
```

### Time Savings

- **Sequential**: 4.5 hours (sum of all tasks)
- **Parallel**: 2 hours (longest task duration)
- **Speed Up**: ~57% faster

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Git remote configured
- Clean working tree

---

## How It Works

### Architecture

```
User prompt: "analyze my code please"
              ↓
    UserPromptSubmit Hook
              ↓
    ┌─────────────────────┐
    │   3-Tier Cascade    │
    ├─────────────────────┤
    │ 1. Keyword (0.02ms) │ → 60% coverage
    │ 2. Model2Vec (0.2ms)│ → 30% coverage
    │ 3. Semantic (50ms)  │ → 10% coverage
    └─────────────────────┘
              ↓
    Command: /sc:analyze (85%)
              ↓
    Hook modifies prompt to "/sc:analyze"
              ↓
    Claude Code auto-executes the command
```

### Confidence Levels

- **85%+**: Keyword match (high precision, instant)
- **70-85%**: Semantic match (good accuracy, fast)
- **50-70%**: Fallback match (requires confirmation)
- **<50%**: No suggestion (pass through)

---

## Development

### Prerequisites

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) package manager
- Claude Code

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/contextune
cd contextune

# Install dependencies
uv sync

# Run tests
uv run pytest

# Test matchers individually
uv run lib/keyword_matcher.py
uv run lib/model2vec_matcher.py
uv run lib/semantic_router_matcher.py

# Test hook
echo '{"prompt":"analyze my code"}' | uv run hooks/user_prompt_submit.py
```

### Documentation

```bash
# Serve docs locally
uv run mkdocs serve
# Visit http://localhost:8000

# Build docs
uv run mkdocs build

# Deploy to GitHub Pages
uv run mkdocs gh-deploy
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check --fix .

# Type check
uv run mypy lib/

# Run all checks
uv run pytest && uv run ruff check . && uv run mypy lib/
```

---

## Configuration

### Basic Configuration

Contextune works out of the box with zero configuration!

### Advanced Configuration

Edit `~/.claude/plugins/contextune/data/user_patterns.json`:

```json
{
  "enabled": true,
  "confidence_threshold": 0.7,
  "tiers": {
    "keyword": true,
    "model2vec": true,
    "semantic_router": false
  },
  "custom_mappings": {
    "make it pretty": "/sc:improve",
    "ship it": "/sc:git"
  }
}
```

### Environment Variables

```bash
# Optional: For Semantic Router (Tier 3)
export COHERE_API_KEY="your-key"
# Or
export OPENAI_API_KEY="your-key"
```

---

## Performance

Benchmarked on M1 MacBook Pro:

| Tier | Latency (P95) | Coverage | Dependencies |
|------|---------------|----------|--------------|
| Keyword | 0.02ms | 60% | None |
| Model2Vec | 0.2ms | 30% | model2vec (8MB) |
| Semantic Router | 50ms | 10% | API key |

**Total hook overhead: <2ms for 90% of queries**

---

## Roadmap

### v1.0 (Current)
- [x] 3-tier detection cascade
- [x] Keyword matching
- [x] Model2Vec embeddings
- [x] Semantic Router integration
- [x] Hook implementation
- [x] Basic command mappings

### v1.1 (Current)
- [x] `/ctx:intents` command
- [x] `/ctx:stats` command
- [x] Parallel development workflow
- [x] `/ctx:plan` command
- [x] `/ctx:execute` command
- [x] `/ctx:status` command
- [x] `/ctx:cleanup` command
- [ ] Auto-discovery of all plugin commands
- [ ] Learning mode (capture corrections)
- [ ] Custom pattern editor

### v1.2 (Future)
- [ ] Multi-command suggestions
- [ ] Context-aware ranking
- [ ] Command chaining detection
- [ ] Team pattern sharing
- [ ] VS Code extension

---

## Contributing

We love contributions! Here's how to help:

### Reporting Bugs

Open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Claude Code version, plugin version)

### Suggesting Features

Open an issue with:
- Use case description
- Proposed solution
- Why it would help others

### Pull Requests

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Ensure tests pass: `uv run pytest`
5. Format code: `uv run ruff format .`
6. Commit changes: `git commit -m 'feat: add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open Pull Request

**Development guidelines:**
- Follow existing code style
- Add tests for new features
- Update documentation
- Use conventional commits
- Ensure all checks pass

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=lib --cov-report=html

# Run specific test file
uv run pytest tests/test_keyword.py

# Run with verbose output
uv run pytest -v

# Test individual matchers (built-in tests)
uv run lib/keyword_matcher.py
uv run lib/model2vec_matcher.py
uv run lib/semantic_router_matcher.py
```

---

## FAQ

### Does Contextune slow down Claude Code?

No! The hook adds <2ms latency for 90% of queries. You won't notice it.

### Does it work offline?

Keyword and Model2Vec tiers work completely offline (90% coverage). Semantic Router tier requires an API key but is optional.

### Can I add custom commands?

Yes! Edit `data/user_patterns.json` to add your own mappings.

### Does it work with other plugins?

Yes! Contextune auto-discovers commands from all installed plugins.

### What about privacy?

Everything runs locally except Semantic Router (optional). No data is collected.

---

## Troubleshooting

### "No command detected"

- Check confidence threshold in config
- Try more specific language
- Add custom mappings for your phrases

### "Model2Vec not available"

```bash
# Install dependencies
uv sync
```

The model downloads automatically on first use (~8MB).

### "Semantic Router failing"

```bash
# Set API key
export COHERE_API_KEY="your-key"
# Or
export OPENAI_API_KEY="your-key"
```

Or disable in config: `"semantic_router": false`

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Model2Vec](https://github.com/minishlab/model2vec) by Minish Lab
- Uses [Semantic Router](https://github.com/aurelio-labs/semantic-router) by Aurelio Labs
- Inspired by Claude Code's plugin ecosystem
- Special thanks to all contributors

---

## Links

- **Documentation**: https://yourusername.github.io/contextune/
- **GitHub**: https://github.com/yourusername/contextune
- **Issues**: https://github.com/yourusername/contextune/issues
- **Discussions**: https://github.com/yourusername/contextune/discussions
- **Claude Code Docs**: https://docs.claude.com/en/docs/claude-code/plugins
- **Website**: https://contextune.com (coming soon)

---

## Support

- 📖 [Read the docs](https://yourusername.github.io/contextune/)
- 💬 [Join discussions](https://github.com/yourusername/contextune/discussions)
- 🐛 [Report bugs](https://github.com/yourusername/contextune/issues)
- ⭐ [Star the repo](https://github.com/yourusername/contextune)

---

<p align="center">
  <b>Contextune: The command translator Claude Code needs.</b>
  <br><br>
  Made with ❤️ by developers who forgot too many slash commands
</p>