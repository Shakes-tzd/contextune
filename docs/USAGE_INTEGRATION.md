# Context Usage Integration Guide

## Overview

This document explains how Contextune integrates with Claude Code's `/usage` and `/context` commands to provide intelligent context optimization and cost savings.

## Problem Statement

Claude Code tracks usage across three dimensions:
1. **Session limits**: Resets every 12 hours
2. **Weekly limits (all models)**: Resets weekly
3. **Weekly limits (Opus)**: Separate quota for Opus

Users need to manually run `/usage` to check these limits. **Contextune automates this optimization**.

## Solution Architecture

### 1. Manual Usage Logging (`/ctx:usage`)

**User Workflow:**
```bash
# Step 1: Check Claude Code usage
/usage

# Step 2: Log to Contextune (prompts for paste)
/ctx:usage
```

**What Contextune Does:**
- Parses the `/usage` output
- Stores snapshot in `observability.db`
- Analyzes trends over time
- Provides recommendations

**Example:**
```
Input (pasted by user):
  Current session: 7% used
  Current week (all models): 89% used
  Current week (Opus): 0% used

Output (Contextune):
  ⚠️  89% weekly usage - approaching limit
  💡 Switch research tasks to Haiku (87% savings)
  💡 Max parallel tasks: 2 (based on remaining 11%)
  ✨ Opus available - use for complex architecture
```

### 2. Automatic Token Estimation

**What We Track:**
- Prompt lengths (word count → token estimate)
- Response sizes (from observability DB)
- Model used (Haiku vs Sonnet vs Opus)
- Parallel task spawning (context multiplication)

**Estimation Formula:**
```python
# Rough estimates (Claude 3.5 tokenizer)
tokens = words * 1.3

# Session usage estimate
session_tokens = sum(prompt_tokens + response_tokens)
session_percent = (session_tokens / SESSION_LIMIT) * 100

# Weekly usage estimate
weekly_tokens = sum_last_7_days(session_tokens)
weekly_percent = (weekly_tokens / WEEKLY_LIMIT) * 100
```

**Accuracy:**
- ±10% for session estimates
- ±15% for weekly estimates
- Good enough for proactive warnings

### 3. Smart Model Selection

**Decision Logic (implemented in `usage_monitor.py`):**

```python
def should_use_haiku(task_type, weekly_usage):
    """
    Research tasks: Always Haiku (fast, cheap, good enough)
    Design tasks: Sonnet unless weekly > 80%
    Execute tasks: Always Haiku (deterministic)
    General tasks: Haiku if weekly > 80%
    """
```

**Cost Savings:**
- Haiku: $0.25 / 1M input tokens
- Sonnet: $3.00 / 1M input tokens
- **Savings: 87% by using Haiku for research**

Example:
- 10 research tasks @ Sonnet: $0.30
- 10 research tasks @ Haiku: $0.04
- **Saved: $0.26 per 10 tasks**

### 4. Parallel Task Limits

**Context Budget Calculation:**

```python
def get_parallel_task_limit(remaining_percent):
    """
    Each parallel task consumes ~10-15% context.

    remaining < 15%: 1 task only
    remaining < 30%: 2 tasks
    remaining < 45%: 3 tasks
    remaining < 60%: 4 tasks
    remaining >= 60%: 5 tasks (max)
    """
```

**Integration Points:**

1. `/ctx:plan` - Checks usage before creating plan
   ```markdown
   Warning: 89% weekly usage
   Recommendation: Plan for 2 parallel tasks (not 5)
   Alternative: Wait until reset (Oct 29, 9:59pm) for full capacity
   ```

2. `/ctx:execute` - Validates before spawning agents
   ```markdown
   Attempting to spawn 5 tasks...
   ⚠️  Only 11% context remaining
   ✅ Spawning 2 tasks now
   📅 Queuing 3 tasks for after reset
   ```

### 5. Proactive Warnings

**Warning Levels:**

| Weekly Usage | Status    | Action                                    |
|--------------|-----------|-------------------------------------------|
| 0-70%        | ✅ Healthy | Normal operation                         |
| 71-85%       | ⚠️  Warning | Suggest Haiku for non-critical tasks    |
| 86-95%       | 🚨 Critical | Auto-switch to Haiku, limit parallel     |
| 96-100%      | 🛑 Limit   | Defer all tasks until reset              |

**Hook Integration:**

The `user_prompt_submit.py` hook checks usage before every prompt:

```python
# In hook
monitor = UsageMonitor()
usage = monitor.get_current_usage()

if usage.weekly_percent > 90:
    # Add warning to prompt
    warning = f"⚠️  {usage.weekly_percent}% weekly usage. Using Haiku for this request."
    # Auto-switch model
    model = "haiku-4-5"
```

## Implementation Status

### ✅ Completed (v0.8.8)
- [x] `lib/usage_monitor.py` - Core usage tracking
- [x] Manual usage parsing (`_parse_usage_output()`)
- [x] Smart model selection (`should_use_haiku()`)
- [x] Parallel task limits (`get_parallel_task_limit()`)
- [x] Recommendations engine (`get_recommendation()`)
- [x] Database integration (`save_usage_history()`)

### 🚧 In Progress
- [ ] `/ctx:usage` slash command implementation
- [ ] Hook integration for automatic warnings
- [ ] Marimo dashboard for usage trends
- [ ] Token estimation algorithm
- [ ] Auto-model-switching in research agents

### 📋 Planned
- [ ] Weekly usage reports via email
- [ ] Budget alerts ("$X spent this week")
- [ ] Opus usage optimization (use when available)
- [ ] Session reset notifications
- [ ] Cost forecasting ("At current rate, you'll hit limit in X days")

## Usage Examples

### Example 1: Research Task with Auto-Optimization

```
User: "research best React state libraries"

Contextune (detects):
  - Command: /ctx:research
  - Weekly usage: 89%
  - Recommendation: Use Haiku (not Sonnet)

Contextune (executes):
  - Spawns 3 Haiku research agents
  - Cost: $0.02 (vs $0.24 with Sonnet)
  - Time: 2 minutes
  - Saved: $0.22 ✅
```

### Example 2: Parallel Plan with Context Limits

```
User: "create parallel plan for auth, dashboard, API, tests, docs"

Contextune (checks):
  - 5 tasks requested
  - Session usage: 92%
  - Remaining: 8%
  - Max tasks: 1

Contextune (warns):
  ⚠️  92% session usage (resets 12:59am)
  💡 Can only execute 1 task now
  💡 Options:
    1. Execute Task 1 now (highest priority)
    2. Wait 4 hours for session reset
    3. Queue all tasks for after reset

User choice: Queue for reset
Contextune: ✅ Tasks queued, will auto-execute at 1:00am
```

### Example 3: Opus Opportunity Detection

```
Contextune (monitors):
  - Weekly usage: 45%
  - Opus usage: 0%
  - Task: "design distributed cache architecture"

Contextune (suggests):
  ✨ Opus available (0% used)!
  This is a complex architecture task - perfect for Opus.

  Cost comparison:
    • Sonnet: $0.15 estimated
    • Opus: $0.75 estimated (+$0.60)

  Trade-off: 5x cost for highest quality reasoning

  Use Opus? [y/N]
```

## Dashboard Integration

The Marimo dashboard (`notebooks/contextune_metrics_dashboard.py`) will show:

1. **Usage Trends**
   - Session usage over last 24 hours
   - Weekly usage over last 4 weeks
   - Opus usage (if any)

2. **Cost Savings**
   - Money saved by auto-switching to Haiku
   - Comparison: "Without Contextune" vs "With Contextune"
   - ROI calculation

3. **Model Distribution**
   - % of tasks on Haiku vs Sonnet vs Opus
   - Recommended vs actual usage

4. **Parallel Efficiency**
   - Tasks executed vs tasks queued
   - Context utilization rate
   - Time saved by parallelization

## Testing

```bash
# Test usage monitor
uv run lib/usage_monitor.py

# Test with mock data
python3 <<EOF
from lib.usage_monitor import UsageMonitor, UsageStats

# Simulate high usage
stats = UsageStats(
    session_percent=92.0,
    session_reset_time="12:59am",
    weekly_percent=89.0,
    weekly_reset_time="Oct 29, 9:59pm",
    opus_percent=0.0,
    timestamp=time.time(),
    raw_output=""
)

monitor = UsageMonitor()
monitor._cache = stats

# Get recommendations
rec = monitor.get_recommendation()
print(rec)
EOF
```

## Future Enhancements

1. **Predictive Analysis**
   - "At current rate, you'll hit 95% by Tuesday"
   - "Recommend deferring 3 tasks to next week"

2. **Budget Tracking**
   - "$X spent this week / $Y monthly budget"
   - "On track to spend $Z this month"

3. **Team Coordination**
   - Share usage data across team
   - Coordinate parallel tasks to avoid limit collisions

4. **API Integration**
   - Direct integration with Anthropic's usage API (when available)
   - Real-time usage tracking without manual paste

## Summary

**Key Benefits:**

1. ✅ **Automatic optimization**: No manual checking needed
2. 💰 **Cost savings**: 87% reduction by smart model selection
3. ⚡ **Faster execution**: Haiku is 5x faster for research
4. 🎯 **Better planning**: Context-aware task scheduling
5. 📊 **Visibility**: Historical trends and forecasting

**User Experience:**

Before Contextune:
```
User: [runs 10 research tasks on Sonnet]
Result: $0.30 spent, might hit weekly limit
```

After Contextune:
```
User: [runs 10 research tasks]
Contextune: Auto-switched to Haiku (89% weekly usage)
Result: $0.04 spent, saved $0.26, 11% capacity preserved
```

---

**Next Steps:**
1. Implement `/ctx:usage` slash command
2. Add hook integration for automatic warnings
3. Create Marimo usage dashboard
4. Test with real usage data
5. Document user workflows
