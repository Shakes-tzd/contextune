---
name: ctx:stats
description: View Contextune detection statistics
keywords:
  - show stats
  - statistics
  - detection stats
  - performance metrics
  - stats
  - metrics
  - show statistics
executable: commands/slashsense-stats.py
---

# Contextune Statistics

Display detection performance metrics and usage statistics from the observability database.

---

## Execution

This command runs automatically via the executable script. The markdown provides documentation only.

**Script:** `commands/slashsense-stats.py`
**Execution:** Automatic when command is triggered
**Data Source:** `~/.claude/plugins/contextune/data/observability.db`

---

## What This Command Does

**Step 1: Load Statistics**

Reads detection data from the observability database:
```bash
sqlite3 ~/.claude/plugins/contextune/data/observability.db \
  "SELECT tier, COUNT(*), AVG(latency_ms), AVG(confidence)
   FROM detections GROUP BY tier"
```

**Step 2: Generate Report**

Creates formatted output using Rich library showing:

1. **Detection Performance by Tier**
   - Keyword: Detection count, average latency, accuracy
   - Model2Vec: Detection count, average latency, accuracy
   - Semantic Router: Detection count, average latency, accuracy

2. **Top Detected Commands**
   - Command name and frequency count
   - Shows top 5 most-used commands

3. **Confidence Distribution**
   - Breakdown by confidence range (50-70%, 70-85%, 85%+)
   - Visual progress bars

**Step 3: Display to User**

Outputs formatted tables and panels to terminal.

---

## Example Output

```
╭─────────────────────────── Contextune Statistics ───────────────────────────╮
│                                                                              │
│ Total Detections: 1,247                                                     │
│                                                                              │
│ Performance by Tier                                                         │
│ ┌───────────────┬────────────┬─────────────┬──────────┐                    │
│ │ Tier          │ Detections │ Avg Latency │ Accuracy │                    │
│ ├───────────────┼────────────┼─────────────┼──────────┤                    │
│ │ Keyword       │        892 │      0.05ms │     98%  │                    │
│ │ Model2Vec     │        245 │      0.18ms │     94%  │                    │
│ │ Semantic      │        110 │     47.30ms │     89%  │                    │
│ └───────────────┴────────────┴─────────────┴──────────┘                    │
│                                                                              │
│ Top Commands                                                                │
│ 1. /sc:analyze       324 detections                                         │
│ 2. /sc:implement     218 detections                                         │
│ 3. /sc:test          187 detections                                         │
│ 4. /sc:git           156 detections                                         │
│ 5. /sc:improve       134 detections                                         │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## Data Sources

**If observability.db exists:**
- Shows actual detection data
- Real latency measurements
- Actual command frequencies

**If observability.db doesn't exist:**
- Shows example/mock data (for demonstration)
- Indicates data is not from actual usage

---

## Interpreting Results

**Tier Performance:**
- **Keyword (Target: <0.1ms):** Fastest, highest accuracy, handles 60% of queries
- **Model2Vec (Target: <1ms):** Fast, good accuracy, handles 30% of queries
- **Semantic Router (Target: <100ms):** Slower, handles complex/ambiguous 10%

**Latency Analysis:**
- < 1ms: Excellent (no perceptible delay)
- 1-10ms: Good (barely noticeable)
- 10-50ms: Acceptable (slight delay)
- > 100ms: Needs optimization

**Accuracy Expectations:**
- 95%+: Excellent (trust the detection)
- 85-95%: Good (verify before auto-execute)
- 70-85%: Fair (suggest to user)
- < 70%: Skip (don't suggest)

---

## Troubleshooting

**"No data available":**
```
ℹ️  No detection data found. Using example statistics.
```
- This is normal for new installations
- Data accumulates as you use Contextune
- Mock data shows what stats will look like

**"Database error":**
- Check: `ls ~/.claude/plugins/contextune/data/observability.db`
- Permissions: Ensure readable
- Corruption: Delete and let it recreate on next detection

---

## Related Commands

- `/ctx:usage` - View token usage and cost optimization
- `/ctx:help` - View all available commands
- `/ctx:configure` - Configure Contextune settings