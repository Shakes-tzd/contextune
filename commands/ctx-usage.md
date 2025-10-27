---
name: ctx:usage
description: Track and optimize context usage with intelligent recommendations
keywords:
  - usage
  - context
  - limits
  - quota
  - optimization
---

# /ctx:usage - Context Usage Optimization

Track your Claude Code usage and get intelligent recommendations for cost optimization.

## Usage

### Quick Check (Manual Input)
```bash
# 1. Run Claude Code's built-in command:
/usage

# 2. Then run this command to log it:
/ctx:usage
```

Claude will ask you to paste the `/usage` output, then provide:
- ✅ Current usage status
- ⚠️  Warnings if approaching limits
- 💡 Recommendations (model selection, parallel tasks, timing)
- 📊 Historical trends

### Automatic Tracking
Contextune automatically estimates your token usage based on:
- Prompt lengths
- Response sizes
- Haiku vs Sonnet usage
- Parallel task spawning

## Example Output

```
📊 Context Usage Analysis

Current Status:
  Session: 7% (resets 12:59am)
  Weekly: 89% (resets Oct 29, 9:59pm)
  Opus: 0% available

⚠️  Warnings:
  • 89% weekly usage - approaching limit
  • Reset in 3 days, 9 hours

💡 Recommendations:
  • Switch research tasks to Haiku (87% cost savings)
  • Max parallel tasks: 2 (based on remaining context)
  • ✨ Opus available (0% used) - great for complex architecture
  • Defer non-critical tasks until weekly reset

📈 Estimated Savings:
  • Using Haiku for next 5 tasks: ~$0.45 saved
  • Waiting until reset: +11% weekly capacity
```

## Integration with Other Commands

### /ctx:research
Automatically uses Haiku when weekly usage > 80%

### /ctx:plan
Limits parallel tasks based on available context

### /ctx:execute
Defers execution if approaching session limits

## Manual Update

If you want to manually log usage data:

```bash
/ctx:usage --update
```

Then paste your `/usage` output when prompted.

## Dashboard

View historical trends:
```bash
marimo edit notebooks/contextune_metrics_dashboard.py
```

The dashboard shows:
- Usage trends over time
- Cost savings from optimization
- Model selection patterns
- Parallel task efficiency
