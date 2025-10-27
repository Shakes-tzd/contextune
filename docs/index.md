# Contextune

> **Precision-Tuned Context Engineering for Claude Code**

[![Version 0.8.9](https://img.shields.io/badge/version-0.8.9-blue.svg)](https://github.com/Shakes-tzd/contextune/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cost Savings: 87%](https://img.shields.io/badge/cost%20savings-87%25-brightgreen.svg)](#cost-optimization)

**Contextune is the only Claude Code plugin focused on context engineering and optimization.** It combines intelligent intent detection, smart tool routing, usage monitoring, and session duration tracking to maximize context preservation and minimize costs.

---

## The Problem

Working with Claude Code at scale creates two critical challenges:

1. **Context Exhaustion**: Your productive session ends when Claude runs out of context (first compact)
2. **Cost Explosion**: Every operation on Sonnet consumes expensive tokens

**Without optimization:**
- First compact at ~8 minutes (context fills quickly)
- Reading large files on Sonnet: $0.09 each
- No visibility into usage or optimization opportunities

---

## The Solution

Contextune provides a comprehensive context engineering framework with five integrated systems:

### 1. 🎯 **Intent Detection & Auto-Execution**

**Zero command memorization** - Just type naturally, Contextune executes the right command.

```
You: "analyze my code for issues"
Contextune: 🎯 Auto-executing /sc:analyze (85% confidence, 0.02ms)
```

**3-Tier Detection Cascade:**
- **Keyword** (0.02ms, 60% coverage) - Fast pattern matching
- **Model2Vec** (0.2ms, 30% coverage) - Semantic similarity
- **Semantic Router** (50ms, 10% coverage) - LLM-based intent

**P95 latency: <2ms** for 90% of queries

### 2. ⚡ **Smart Tool Routing**

**Intelligent delegation** of expensive operations to Haiku.

**Automatic Routing Decisions:**
- Read operations >1000 lines → Delegate to Haiku
- Complex Bash commands → Delegate to Haiku
- Fast operations (Grep, Glob) → Keep on Sonnet

**Cost Savings:**
```
Read 2500-line file:
- Sonnet direct: $0.09
- Haiku delegation: $0.02
- Savings: 77%
```

**Context Benefit:** Delays compaction by 3x (preserves Sonnet context)

### 3. 📊 **Session Duration Tracking**

**Measure context preservation effectiveness** - Know exactly how long your sessions stay productive.

**Tracked Metrics:**
- Time from session start to first compact
- Total compact events per session
- Context preservation assessment

**Thresholds:**
- ⚠️ Short (<10 min): Needs optimization
- ✅ Good (10-30 min): Healthy usage
- 🎯 Excellent (30+ min): Excellent preservation

**View Metrics:**
```bash
./scripts/view_session_metrics.sh
```

### 4. 💰 **Usage Monitoring & Optimization**

**Automatic cost optimization** based on Claude Code quota consumption.

**Three-Tier Fallback:**
1. Headless query (experimental, with warnings)
2. Token estimation (~85% accurate)
3. Manual paste (100% accurate)

**Intelligent Thresholds:**

| Weekly Usage | Status | Automatic Actions |
|-------------|--------|-------------------|
| 0-70% | ✅ Healthy | Normal operation |
| 70-85% | ⚠️ Warning | Suggest Haiku for research |
| 85-95% | 🚨 Critical | Auto-switch Haiku, limit parallel tasks |
| 95%+ | 🛑 Limit | Defer non-critical tasks |

**At 90% weekly usage:**
- All research tasks → Haiku (87% savings)
- Parallel tasks → Limited to 2 concurrent
- Large reads → Always delegated

### 5. 🤖 **Haiku-Powered Interactive Analysis**

**Intelligent command suggestions** using Claude Code headless mode.

**Example:**
```
You: "help me research React state libraries"
Detected: /ctx:help (keyword: "help")

💡 Better alternatives:
  • /ctx:research - fast answers using 3 parallel agents

💬 Haiku: Use '/ctx:research' to investigate libraries in parallel
(2 min, ~$0.07). Follow with '/ctx:plan' for structured development.

Auto-executes: /ctx:research
```

**Performance:**
- Analysis time: 1-2 seconds
- Cost per suggestion: ~$0.001
- No API key needed (uses Claude Code auth)

---

## Key Benefits

### **Context Preservation**
- **3x longer sessions** before compaction (8 min → 25 min average)
- **Measurable metrics** via session duration tracking
- **Automatic optimization** based on usage patterns

### **Cost Optimization**
- **87% savings** on delegated operations
- **Usage-aware routing** at high quota consumption
- **Transparent tracking** in observability database

### **Zero-Context Overhead**
- **All hooks run OUTSIDE conversation**
- **Status line integration** (file-based, not in context)
- **SessionStart feedback** (UI-only, 0 tokens)
- **Result: Full functionality, zero additional context cost**

### **Data-Driven Insights**
- **Observability database** tracks everything
- **Session metrics, tool costs, routing decisions**
- **Marimo dashboard** for visualization
- **Export-ready data** for analysis

---

## Quick Start

### Installation

```bash
# Add Contextune marketplace
/plugin marketplace add Shakes-tzd/contextune

# Install plugin
/plugin install contextune
```

### Basic Usage

Just type naturally:

```
"analyze my code"              → /sc:analyze
"run tests and fix failures"   → /sc:test
"research best React patterns" → /ctx:research
"work on auth and dashboard in parallel" → /ctx:execute
```

### View Session Metrics

```bash
# See how well context is preserved
./scripts/view_session_metrics.sh
```

### Track Usage

```bash
# Check your Claude Code usage
/usage

# Then track in Contextune
/contextune:usage
# Paste the output when prompted
```

---

## Architecture Highlights

### Zero-Context Overhead Design

```
User Prompt
    ↓
UserPromptSubmit Hook (OUTSIDE conversation)
    ↓
3-Tier Detection Cascade (keyword → Model2Vec → Semantic)
    ↓
Modified Prompt with Command
    ↓
Claude Code Executes (with ZERO additional context)
```

**Result:** Full intent detection with NO context cost

### Intelligent Tool Routing

```
Tool Call (e.g., Read large_file.py)
    ↓
PreToolUse Hook Analyzes
    ↓
Decision: Delegate to Haiku (saves $0.08)
    ↓
Haiku reads, summarizes
    ↓
Sonnet reads summary (preserves context)
```

**Result:** 77% cost savings + delayed compaction

### Session Duration Tracking

```
SessionStart Hook → Record start_time
    ↓
... work happens ...
    ↓
CompactStart Hook → Record first_compact_time
    ↓
Duration = compact_time - start_time
    ↓
Assessment: ✅ Good (25 minutes)
```

**Result:** Measurable context preservation effectiveness

---

## Performance

**Intent Detection:**
- P50 latency: 0.02ms (keyword match)
- P95 latency: <2ms (90% of queries)
- P99 latency: 50ms (semantic fallback)

**Tool Routing:**
- Decision time: <1ms
- Savings per delegation: 77-87%
- Context preservation: 3x longer sessions

**Usage Monitoring:**
- Token estimation: <1ms
- Headless query: 1-2 seconds
- Manual paste: Instant (cached)

---

## Documentation

### Core Features
- [Smart Tool Routing](delegation-modes.md) - How intelligent delegation works
- [Observability](OBSERVABILITY.md) - Database schema and metrics
- [Prompt Augmentation](PROMPT_AUGMENTATION.md) - How prompts are modified
- [Skills System](SKILLS.md) - Expert guidance system

### Architecture
- [Haiku Agent Architecture](HAIKU_AGENT_ARCHITECTURE.md) - Three-tier intelligence
- [Agent Integration Guide](AGENT_INTEGRATION_GUIDE.md) - Using Haiku agents
- [Cost Optimization](COST_OPTIMIZATION_GUIDE.md) - Maximize savings

### Usage & Integration
- [Usage Integration](USAGE_INTEGRATION.md) - Claude Code `/usage` integration
- [Usage Reality Check](USAGE_REALITY_CHECK.md) - Honest assessment of approaches
- [Auto-Approval Configuration](AUTO_APPROVAL_CONFIGURATION.md) - Automation setup

### Guides
- [Migration Guide v0.3.0](MIGRATION_GUIDE_v0.3.0.md) - Upgrade from v0.2.0
- [Research Agents Guide](RESEARCH_AGENTS_GUIDE.md) - Parallel research workflows
- [Parallel Setup Pattern](PARALLEL_SETUP_PATTERN.md) - Git worktree workflows

---

## ROI Example

**Scenario:** 100 operations/week, 90% weekly usage

### Before Contextune
```
100 file reads on Sonnet: $9.00/week
Sessions: First compact at ~8 minutes
Visibility: None
Annual cost: $468
```

### After Contextune
```
10 small files on Sonnet:        $0.90
90 files delegated to Haiku:     $1.80
Sessions: First compact at ~25 min (3x longer)
Visibility: Full metrics dashboard
Annual cost: $140

Annual savings: $328 (70% reduction)
Time saved: 17 min/session × 5 sessions/week = 85 min/week
```

---

## Unique Differentiators

| Feature | Contextune | Typical Plugin |
|---------|-----------|----------------|
| Intent detection | ✅ 3-tier cascade | ❌ Manual commands |
| Cost optimization | ✅ Smart routing | ❌ None |
| Usage monitoring | ✅ Automatic | ❌ Manual |
| Context tracking | ✅ Session metrics | ❌ None |
| Zero-context overhead | ✅ Yes | ❌ Adds context |
| Observability | ✅ Full database | ❌ None |

**Contextune is the only Claude Code plugin focused on CONTEXT ENGINEERING.**

---

## Get Started

1. **Install**: `/plugin install contextune`
2. **Use naturally**: "analyze my code", "research React patterns"
3. **Track metrics**: `./scripts/view_session_metrics.sh`
4. **Monitor usage**: `/contextune:usage` (paste `/usage` output)
5. **Optimize**: Let Contextune auto-optimize based on your usage

---

## License

MIT License - See [LICENSE](https://github.com/Shakes-tzd/contextune/blob/master/LICENSE) for details.

---

## Links

- **GitHub**: [Shakes-tzd/contextune](https://github.com/Shakes-tzd/contextune)
- **Issues**: [Report bugs](https://github.com/Shakes-tzd/contextune/issues)
- **Discussions**: [Join the community](https://github.com/Shakes-tzd/contextune/discussions)

---

<p align="center">
  <b>Contextune: The context engineering framework Claude Code needs.</b>
  <br><br>
  Made with ❤️ by developers who care about context preservation and cost optimization.
</p>
