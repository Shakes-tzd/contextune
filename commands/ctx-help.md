---
name: ctx:help
description: Example-first command reference and quick start guide
keywords:
  - help
  - examples
  - quick start
  - how to use
  - show examples
  - command reference
  - getting started
---

# Contextune Help - Quick Start Guide

**Just type naturally—Contextune detects your intent automatically!**

---

## ✨ Try These Examples (Copy & Paste)

### 🔍 Fast Research (1-2 min, ~$0.07)
```
research best React state management library for 2025
```
→ Spawns 3 parallel agents (web + codebase + deps)
→ Returns comparison table + recommendation
→ 67% faster than sequential research

### ⚡ Parallel Development (30-70% faster)
```
work on authentication, dashboard, and API in parallel
```
→ Creates development plan with task breakdown
→ Sets up git worktrees for parallel execution
→ Spawns agents to work simultaneously

### 💡 Feature Discovery
```
what can Contextune do?
```
→ Activates intent-recognition skill
→ Shows all capabilities with examples
→ Guides you to the right commands

---

## 📚 Most Used Commands

### `/ctx:research <query>`
Fast technical research using 3 parallel Haiku agents.

**Examples:**
```bash
/ctx:research best database for user authentication
/ctx:research should I use REST or GraphQL
/ctx:research latest TypeScript testing frameworks
```

**What you get:**
- Web research (latest trends, comparisons)
- Codebase analysis (what already exists)
- Dependency check (what's installed vs needed)
- Recommendation with reasoning

**Execution:** Fast parallel | **Cost:** ~$0.07

---

### `/ctx:status`
Monitor progress across all parallel worktrees.

**Shows:**
- Active worktrees and their branches
- Task completion status
- Git commit history per worktree
- Next steps and blockers

**Use when:** Working on parallel tasks and want overview

---

### `/ctx:configure`
Setup guide for persistent status bar integration.

**Enables:**
- Real-time detection display in status bar
- Zero context overhead (file-based)
- See what Contextune detected without cluttering chat

**One-time setup:** Adds statusline script to your config

---

## 🔧 Advanced Workflow Commands

### `/ctx:plan`
Document development plan for parallel execution.

**Creates:**
- Modular YAML plan with task breakdown
- Dependency graph (parallel vs sequential tasks)
- Resource allocation strategy
- Time and cost estimates

**Example:**
```bash
/ctx:plan
# Then describe your features:
# "I need user auth, admin dashboard, and payment integration"
```

**Output:** `.parallel/plans/active/plan.yaml`

---

### `/ctx:execute`
Execute development plan in parallel using git worktrees.

**What happens:**
1. Reads plan from `.parallel/plans/active/plan.yaml`
2. Creates git worktrees for each task
3. Spawns parallel agents to work independently
4. Creates PRs when tasks complete
5. Reports progress and costs

**Prerequisites:**
- Git repository with remote
- GitHub CLI (`gh`) authenticated
- Existing plan (run `/ctx:plan` first)

**Time savings:** 30-70% faster than sequential

---

### `/ctx:cleanup`
Clean up completed worktrees and branches.

**Removes:**
- Merged worktrees
- Completed task branches
- Temporary files

**Safe:** Only cleans up merged/completed work

---

### `/ctx:stats`
View detailed usage statistics and performance metrics.

**Shows:**
- Detection accuracy breakdown
- Cost savings vs manual work
- Performance metrics (latency, throughput)
- Most-used commands

**Validates claims:** See actual 81% cost reduction data

---

## 🎯 Natural Language Detection

You don't need to memorize commands! Just type what you want:

| What You Type | Contextune Detects | Confidence |
|--------------|-------------------|------------|
| "analyze my code" | `/sc:analyze` | 85% (keyword) |
| "run the tests" | `/sc:test` | 85% (keyword) |
| "research best approach" | `/ctx:research` | 92% (keyword) |
| "work in parallel" | `/ctx:execute` | 88% (keyword) |
| "review performance" | `/sc:improve` | 85% (keyword) |
| "explain this code" | `/sc:explain` | 85% (keyword) |

**Detection tiers:**
- **Keyword** (0.02ms) - 60% of queries, instant
- **Model2Vec** (0.2ms) - 30% of queries, fast embeddings
- **Semantic Router** (50ms) - 10% of queries, LLM-based

---

## 🤖 Auto-Activated Skills

These skills activate automatically when you mention certain topics:

### `parallel-development-expert`
**Triggers:** "parallel", "concurrent", "speed up", "work on multiple"

**Does:**
- Analyzes if tasks are parallelizable
- Calculates time savings
- Suggests `/ctx:plan` and `/ctx:execute`
- Guides worktree setup

### `intent-recognition`
**Triggers:** "what can you do", "capabilities", "features", "help"

**Does:**
- Shows Contextune capabilities
- Provides natural language examples
- Explains detection system
- Guides to relevant commands

### `git-worktree-master`
**Triggers:** "worktree stuck", "can't remove", "locked", "worktree error"

**Does:**
- Diagnoses worktree issues
- Suggests safe fixes
- Handles lock file cleanup
- Prevents data loss

### `performance-optimizer`
**Triggers:** "slow", "performance", "optimize", "bottleneck"

**Does:**
- Benchmarks workflow performance
- Identifies bottlenecks
- Calculates speedup potential
- Suggests optimizations

---

## 🚀 Quick Start Workflow

**1. First-Time Setup (Optional, 2 min)**
```bash
/ctx:configure
```
→ Sets up status bar integration for persistent detection display

**2. Fast Research (When You Need to Decide)**
```
research best authentication library for Python
```
→ Get answer in 1-2 min with comparison table

**3. Parallel Development (When You Have Multiple Tasks)**
```
work on user auth, admin panel, and reports in parallel
```
→ Contextune creates plan + worktrees + executes

**4. Monitor Progress**
```bash
/ctx:status
```
→ See what's happening across all parallel tasks

**5. Clean Up When Done**
```bash
/ctx:cleanup
```
→ Remove merged worktrees and branches

---

## 💰 Cost Optimization

Contextune uses **Haiku agents** for 81% cost reduction:

| Operation | Sonnet Cost | Haiku Cost | Savings |
|-----------|-------------|------------|---------|
| Research (3 agents) | $0.36 | $0.07 | 81% |
| Task execution | $0.27 | $0.04 | 85% |
| Worktree management | $0.06 | $0.008 | 87% |

**Annual savings:** ~$1,350 for typical usage (1,200 workflows/year)

Run `/ctx:stats` to see YOUR actual savings!

---

## 🔧 Configuration Files

### Plan Structure
```
.parallel/
├── plans/
│   ├── 20251025-120000/    # Timestamped plan directories
│   │   ├── plan.yaml       # Main plan file
│   │   └── tasks/          # Individual task files
│   └── active -> 20251025-120000/  # Symlink to current plan
└── scripts/
    ├── setup_worktrees.sh  # Worktree creation script
    └── create_prs.sh       # PR creation script
```

### Detection Data
```
.contextune/
└── last_detection         # JSON with latest detection
                          # Read by status bar script
```

---

## 📖 More Resources

- **README:** Full feature list and architecture
- **GitHub:** https://github.com/Shakes-tzd/contextune
- **Issues:** Report bugs or request features

---

## 🆘 Common Questions

**Q: Do I need to memorize slash commands?**
A: No! Just type naturally. Contextune detects intent automatically.

**Q: Does this slow down Claude Code?**
A: No. Hook adds <2ms latency for 90% of queries.

**Q: Does it work offline?**
A: Yes! Keyword + Model2Vec tiers work offline (90% coverage).

**Q: Can I customize detection patterns?**
A: Yes! Edit `~/.claude/plugins/contextune/data/user_patterns.json`

**Q: How do I see detection stats?**
A: Run `/ctx:stats` to see accuracy, performance, and cost metrics.

---

**💡 Tip:** Type "what can Contextune do?" right now to see the intent-recognition skill in action!
