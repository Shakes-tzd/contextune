---
name: contextune:usage
description: Track and optimize Claude Code usage with intelligent recommendations
---

# Usage Tracking & Optimization

Contextune integrates with Claude Code's `/usage` command to provide intelligent context optimization, cost savings, and proactive warnings.

## Quick Start

### Option 1: Manual Paste (Most Accurate - Recommended)

1. Run Claude Code's usage command:
   ```
   /usage
   ```

2. Copy the entire output

3. Run this command and paste when prompted:
   ```
   /contextune:usage
   ```

### Option 2: Automatic Estimation

Contextune automatically estimates usage based on tracked operations (~85% accurate for Contextune tasks only).

View current estimates:
```
/contextune:stats
```

## What You Get

### Intelligent Recommendations

Based on your current usage, Contextune provides:

- **Model Selection**: Auto-switch to Haiku when approaching limits (87% cost savings)
- **Parallel Task Limits**: Recommended max concurrent tasks based on remaining quota
- **Proactive Warnings**: Alerts when approaching session or weekly limits
- **Opus Opportunities**: Suggestions to use Opus when quota is available for complex tasks

### Example Output

```
📊 Current Usage Analysis
═══════════════════════════════════════

📈 Usage Metrics:
  Session:  19% (resets 1:00am America/New_York)
  Weekly:   90% (resets Oct 29, 10:00pm America/New_York)  ⚠️  CRITICAL
  Opus:     0%

🎯 Status: CRITICAL

⚠️  Warnings:
  • CRITICAL: 90% weekly usage (resets Oct 29, 10:00pm)
  • You have ~10% capacity until Oct 29, 10:00pm

💡 Recommendations:
  • Switch research tasks to Haiku (87% cost savings)
  • Recommended max parallel tasks: 2
  • Consider deferring non-critical tasks until weekly reset
  • ✨ Opus available (0% used) - great for complex architecture tasks

📊 Historical Trends:
  • Average daily usage: 12.9% (7-day trend)
  • Projected time to limit: ~18 hours
  • Cost savings from Haiku: $0.42 this week
```

## Usage Thresholds

| Weekly Usage | Status | Automatic Actions |
|-------------|--------|-------------------|
| 0-70% | ✅ Healthy | Normal operation, all models available |
| 71-85% | ⚠️ Warning | Suggest Haiku for research tasks |
| 86-95% | 🚨 Critical | Auto-switch to Haiku, limit parallel tasks |
| 96-100% | 🛑 Limit | Defer all tasks until reset |

## Integration Points

### Automatic Optimization

Once you've logged your usage, Contextune automatically:

1. **Research Tasks** (`/ctx:research`):
   - Uses Haiku if weekly > 80% (saves $0.12 per task)
   - Adjusts number of parallel agents based on quota

2. **Planning** (`/ctx:plan`):
   - Warns if approaching limits
   - Suggests task deferral if critical
   - Recommends queue for after reset

3. **Execution** (`/ctx:execute`):
   - Limits parallel tasks based on remaining quota
   - Queues excess tasks for after reset
   - Provides time estimates

## Manual Paste Format

Contextune can parse Claude Code's `/usage` output in this format:

```
Current session
[progress bar] 19% used
Resets 1:00am (America/New_York)

Current week (all models)
[progress bar] 90% used
Resets Oct 29, 10:00pm (America/New_York)

Current week (Opus)
[progress bar] 0% used
```

Just paste the entire block when prompted.

## Cost Savings Examples

### Research Task (3 parallel agents)

**Without optimization:**
- Model: Sonnet 3.5
- Cost: ~$0.24 per research task
- Weekly (10 tasks): $2.40

**With Contextune (90% usage):**
- Model: Haiku 4.5 (auto-switched)
- Cost: ~$0.02 per research task
- Weekly (10 tasks): $0.20
- **Saved: $2.20/week** ✅

### Parallel Execution (5 tasks)

**Without optimization:**
- Spawn all 5 tasks
- Risk hitting 100% limit mid-execution
- Failed tasks, wasted quota

**With Contextune (90% usage):**
- Execute 2 tasks now (within quota)
- Queue 3 tasks for after reset
- **Avoided: quota exhaustion** ✅

## Technical Details

### Data Storage

Usage snapshots are stored in `.contextune/observability.db`:

```sql
CREATE TABLE usage_history (
    timestamp REAL PRIMARY KEY,
    session_percent REAL,
    weekly_percent REAL,
    opus_percent REAL,
    session_reset TEXT,
    weekly_reset TEXT
);
```

### Token Estimation

When manual data isn't available, Contextune estimates usage from tracked operations:

```python
# Rough estimates (Claude 3.5 limits)
SESSION_LIMIT = 200,000 tokens  # ~12 hours
WEEKLY_LIMIT = 1,000,000 tokens  # ~7 days

# Calculation
session_percent = (tracked_tokens / SESSION_LIMIT) * 100
```

**Accuracy**: ~85% for Contextune operations only (doesn't track other Claude Code sessions)

### Three-Tier Fallback

Contextune tries multiple approaches:

1. **Headless query** (experimental, may not be reliable)
2. **Token estimation** (85% accurate, automatic)
3. **Manual paste** (100% accurate, user-triggered)

## Troubleshooting

### "Unable to fetch usage data"

**Cause**: All automatic methods failed
**Solution**: Use manual paste workflow:
```
/usage
# Copy output
/contextune:usage
# Paste when prompted
```

### "Usage seems low compared to /usage"

**Cause**: Token estimation only tracks Contextune operations
**Solution**: Use manual paste for accurate data including all Claude Code sessions

### "Headless query taking too long"

**Cause**: Experimental feature timing out
**Solution**: Press Ctrl+C to cancel, use manual paste instead

## Privacy & Security

- Usage data stored locally in `.contextune/observability.db`
- No data sent to external servers
- Reset times preserved from Claude Code output
- Historical data helps optimize future tasks

## Related Commands

- `/usage` - Claude Code's native usage command
- `/context` - Claude Code's context management
- `/contextune:stats` - View Contextune detection statistics
- `/contextune:config` - Configure Contextune settings

## Future Enhancements

Planned for v1.0:

- **Predictive Analysis**: "At current rate, you'll hit 95% by Tuesday"
- **Budget Tracking**: "$X spent this week / $Y monthly budget"
- **Email Reports**: Weekly usage summaries
- **Team Coordination**: Share usage data across team
- **Official MCP Integration**: Direct API access (when available from Anthropic)

---

**Pro Tip**: Run `/contextune:usage` at the start of your session to enable intelligent optimization for all subsequent tasks.
