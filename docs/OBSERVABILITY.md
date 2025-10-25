# Contextune Observability Architecture

## Overview

Contextune uses a **unified SQLite database** for all observability, metrics, and state management. This provides:

- ✅ **Centralized**: Single source of truth (no scattered JSON files)
- ✅ **Fast**: SQL queries for aggregations (0.05-0.5ms)
- ✅ **Responsive**: Status line updates in real-time
- ✅ **Thread-safe**: ACID transactions built-in
- ✅ **Correlations**: JOIN detection + performance + errors
- ✅ **Time-series ready**: Timestamp-based analytics

## Database Schema

### File Location
```
.contextune/observability.db
```

### Tables

#### 1. `current_detection` (State)
Active detection shown in status line (single row, updated in-place)

```sql
CREATE TABLE current_detection (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Always 1 (single row)
    command TEXT NOT NULL,                   -- e.g., "/ctx:research"
    confidence REAL NOT NULL,                -- 0.0-1.0
    method TEXT NOT NULL,                    -- "keyword", "model2vec", "semantic"
    timestamp REAL NOT NULL,                 -- Unix timestamp
    prompt_preview TEXT                      -- First 60 chars
)
```

**Usage:**
- Written by: `hooks/user_prompt_submit.py`
- Read by: `~/.claude/statusline.sh`
- Cleared by: `hooks/session_start.js` (on new session)

#### 2. `detection_history` (Analytics)
All detections for statistics and analysis

```sql
CREATE TABLE detection_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    confidence REAL NOT NULL,
    method TEXT NOT NULL,
    timestamp REAL NOT NULL,
    session_id TEXT,
    prompt_preview TEXT,
    latency_ms REAL
)

CREATE INDEX idx_detection_timestamp ON detection_history(timestamp);
CREATE INDEX idx_detection_command ON detection_history(command);
CREATE INDEX idx_detection_method ON detection_history(method);
```

**Queries:**
```sql
-- Total detections
SELECT COUNT(*) FROM detection_history;

-- By method
SELECT method, COUNT(*) FROM detection_history GROUP BY method;

-- Recent detections
SELECT * FROM detection_history ORDER BY timestamp DESC LIMIT 10;

-- Success rate by method
SELECT method, AVG(confidence) FROM detection_history GROUP BY method;
```

#### 3. `performance_metrics` (Performance)
Component latency tracking (hook, matchers, DB operations)

```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL,        -- "hook", "keyword_matcher", "statusline"
    operation TEXT NOT NULL,        -- "detect", "write_db", "read_db"
    latency_ms REAL NOT NULL,
    timestamp REAL NOT NULL,
    session_id TEXT,
    metadata TEXT                   -- JSON for additional context
)

CREATE INDEX idx_perf_component ON performance_metrics(component);
CREATE INDEX idx_perf_timestamp ON performance_metrics(timestamp);
```

**Queries:**
```sql
-- P50/P95/P99 by component
SELECT
    component,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM performance_metrics
GROUP BY component;

-- Slow operations (> 100ms)
SELECT * FROM performance_metrics
WHERE latency_ms > 100
ORDER BY timestamp DESC;
```

#### 4. `matcher_performance` (Matcher Efficiency)
Per-tier matcher success rates and latency

```sql
CREATE TABLE matcher_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method TEXT NOT NULL,          -- "keyword", "model2vec", "semantic"
    latency_ms REAL NOT NULL,
    success BOOLEAN NOT NULL,      -- 1 = match found, 0 = no match
    timestamp REAL NOT NULL
)

CREATE INDEX idx_matcher_method ON matcher_performance(method);
```

**Queries:**
```sql
-- Average latency by tier
SELECT method, AVG(latency_ms) FROM matcher_performance GROUP BY method;

-- Success rate by tier
SELECT method, AVG(CAST(success AS FLOAT)) * 100 as success_rate
FROM matcher_performance GROUP BY method;
```

#### 5. `error_logs` (Error Tracking)
Exception tracking with stack traces

```sql
CREATE TABLE error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL,       -- "semantic_router", "model2vec", etc.
    error_type TEXT NOT NULL,      -- "ImportError", "ValueError", etc.
    message TEXT NOT NULL,
    stack_trace TEXT,
    timestamp REAL NOT NULL,
    session_id TEXT
)

CREATE INDEX idx_error_timestamp ON error_logs(timestamp);
CREATE INDEX idx_error_component ON error_logs(component);
```

**Queries:**
```sql
-- Errors in last 24h
SELECT * FROM error_logs
WHERE timestamp > (strftime('%s','now') - 86400)
ORDER BY timestamp DESC;

-- Error rate by component
SELECT component, COUNT(*) FROM error_logs GROUP BY component;
```

#### 6. `sessions` (Session Analytics)
Session-level metrics (future use)

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time REAL NOT NULL,
    end_time REAL,
    total_detections INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0
)
```

#### 7. `command_usage` (Usage Patterns)
Track when commands are actually executed (future use)

```sql
CREATE TABLE command_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    executed BOOLEAN NOT NULL,
    timestamp REAL NOT NULL,
    session_id TEXT
)

CREATE INDEX idx_usage_command ON command_usage(command);
```

#### 8. `user_patterns` (Custom Preferences)
User-defined patterns (migrate from user_patterns.json)

```sql
CREATE TABLE user_patterns (
    pattern TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    confidence_threshold REAL DEFAULT 0.7,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
)
```

## Data Flow

### Detection Flow
```
User types prompt
    ↓
hooks/user_prompt_submit.py
    ├─ Detect intent (3-tier cascade)
    ├─ Log to detection_history
    ├─ Update current_detection
    └─ Log matcher_performance
    ↓
~/.claude/statusline.sh
    ├─ Query current_detection
    └─ Display in status line
```

### Session Start Flow
```
New session starts
    ↓
hooks/session_start.js
    ├─ DELETE FROM current_detection
    └─ Show welcome message
    ↓
Status line shows clean state
```

### Dashboard Flow
```
User runs: uv run commands/ctx-dashboard.py
    ↓
lib/observability_db.py
    ├─ Query detection_history
    ├─ Query performance_metrics
    ├─ Query matcher_performance
    ├─ Query error_logs
    └─ Calculate health score
    ↓
Beautiful formatted output
```

## API Usage

### Python (Hooks)

```python
from observability_db import ObservabilityDB

db = ObservabilityDB(".contextune/observability.db")

# Log detection
db.set_detection(
    command="/ctx:research",
    confidence=0.95,
    method="keyword",
    prompt_preview="research best React libraries",
    latency_ms=0.003
)

# Log performance
db.log_performance(
    component="hook",
    operation="total_execution",
    latency_ms=2.5
)

# Log matcher performance
db.log_matcher_performance(
    method="keyword",
    latency_ms=0.003,
    success=True
)

# Log error
db.log_error(
    component="semantic_router",
    error_type="ImportError",
    message="Cohere API key not found",
    stack_trace=traceback.format_exc()
)

# Get stats
stats = db.get_stats()
print(stats["detections"]["total"])
print(stats["matchers"]["keyword"]["avg_latency_ms"])
```

### Shell (Status Line)

```bash
# Query current detection
sqlite3 .contextune/observability.db \
  "SELECT command, CAST(confidence * 100 AS INTEGER), method
   FROM current_detection WHERE id = 1"

# Output: /ctx:research|95|keyword
```

### JavaScript (Session Start)

```javascript
const { execSync } = require('child_process');

// Clear detection
execSync(
  `sqlite3 .contextune/observability.db "DELETE FROM current_detection WHERE id = 1"`,
  { stdio: 'pipe', timeout: 1000 }
);
```

## Performance Characteristics

### Write Performance
- **Detection write**: ~0.3ms
- **Performance metric**: ~0.2ms
- **Error log**: ~0.2ms

### Read Performance
- **Current detection**: ~0.1ms
- **Stats query**: ~5-10ms (with aggregations)
- **Recent detections**: ~1-2ms

### Database Size
- **1,000 detections**: ~200KB
- **10,000 detections**: ~2MB
- **100,000 detections**: ~20MB

**Rotation strategy**: Archive old data quarterly

## Monitoring & Alerts

### Health Checks

```python
# Check database health
db = ObservabilityDB()
stats = db.get_stats()

# Alert if error rate > 10%
error_rate = stats["errors"]["total"] / stats["detections"]["total"]
if error_rate > 0.1:
    alert("High error rate!")

# Alert if P95 > 100ms
if stats["performance"]["hook"]["p95"] > 100:
    alert("Hook latency degraded!")
```

### Dashboard
Run `uv run commands/ctx-dashboard.py` for comprehensive health view.

## Migration from JSON

### Before (v0.5.x)
```
.contextune/
├── last_detection (JSON file)
└── (detection_stats.json in ~/.claude/plugins/...)
```

### After (v0.7.0+)
```
.contextune/
└── observability.db (SQLite)
```

**Migration steps:**
1. Automatic - no user action needed
2. Old JSON files ignored
3. New database created on first detection
4. Zero breaking changes

## Future Enhancements

### Planned
- [ ] Session correlation (group detections by session)
- [ ] Command execution tracking (detect → execute flow)
- [ ] ML-powered insights (anomaly detection)
- [ ] Export to Prometheus/Grafana
- [ ] Real-time alerts (webhook integrations)
- [ ] A/B testing framework (matcher comparison)

### Queries for ML
```sql
-- Feature: User patterns
SELECT
    strftime('%H', timestamp, 'unixepoch') as hour,
    command,
    COUNT(*) as frequency
FROM detection_history
GROUP BY hour, command;

-- Feature: Matcher fallback rate
SELECT
    SUM(CASE WHEN method = 'semantic' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
FROM detection_history;

-- Feature: Confidence distribution
SELECT
    CASE
        WHEN confidence >= 0.9 THEN 'high'
        WHEN confidence >= 0.7 THEN 'medium'
        ELSE 'low'
    END as confidence_bucket,
    COUNT(*)
FROM detection_history
GROUP BY confidence_bucket;
```

## Best Practices

### 1. Use Transactions
```python
with sqlite3.connect(db_path) as conn:
    conn.execute("INSERT ...")
    conn.execute("UPDATE ...")
    conn.commit()  # Atomic
```

### 2. Index Frequently Queried Columns
```sql
CREATE INDEX idx_detection_timestamp ON detection_history(timestamp);
```

### 3. Archive Old Data
```sql
-- Keep last 90 days
DELETE FROM detection_history
WHERE timestamp < (strftime('%s','now') - 7776000);
```

### 4. Monitor Database Size
```bash
du -h .contextune/observability.db
```

### 5. Vacuum Periodically
```sql
VACUUM;  -- Reclaim space after DELETE
```

## Troubleshooting

### Database Locked
**Cause**: WAL mode prevents locks, but check for zombie processes

```bash
ps aux | grep sqlite3
kill <pid>
```

### Slow Queries
**Solution**: Add indexes

```sql
EXPLAIN QUERY PLAN SELECT ...;  -- Check query plan
CREATE INDEX IF NOT EXISTS idx_... ON ...;
```

### Corruption
**Recovery**:
```bash
sqlite3 .contextune/observability.db "PRAGMA integrity_check;"
sqlite3 .contextune/observability.db ".recover" | sqlite3 new.db
```

## Conclusion

The unified observability database provides:
- **Single source of truth** for all metrics
- **Fast, responsive** status line updates
- **Comprehensive analytics** via SQL
- **Foundation for ML** insights
- **Production-grade** instrumentation

**Key insight**: SQLite's architectural benefits (thread safety, ACID, no file churn) outweigh the small raw I/O speed difference vs JSON files (0.3ms vs 0.1ms).
