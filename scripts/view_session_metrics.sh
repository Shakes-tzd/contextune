#!/bin/bash
# View session duration and context preservation metrics

DB_FILE=".contextune/observability.db"

echo "📊 Session Context Preservation Metrics"
echo "========================================"
echo ""

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Observability database not found at $DB_FILE"
    exit 1
fi

# Get session metrics
echo "🕐 Recent Sessions (Time to First Compact):"
echo "--------------------------------------------"
sqlite3 "$DB_FILE" <<EOF
.headers on
.mode column
SELECT
    session_id,
    datetime(start_time, 'unixepoch', 'localtime') as session_start,
    ROUND(duration_to_compact / 60.0, 1) as minutes_to_compact,
    CASE
        WHEN duration_to_compact IS NULL THEN 'No compact yet'
        WHEN duration_to_compact < 600 THEN '⚠️  Short (<10 min)'
        WHEN duration_to_compact < 1800 THEN '✅ Good (10-30 min)'
        WHEN duration_to_compact >= 1800 THEN '🎯 Excellent (30+ min)'
    END as context_preservation
FROM sessions
WHERE start_time > strftime('%s', 'now', '-7 days')
ORDER BY start_time DESC
LIMIT 10;
EOF

echo ""
echo "📈 Context Preservation Statistics (Last 7 Days):"
echo "---------------------------------------------------"
sqlite3 "$DB_FILE" <<EOF
.headers on
.mode column
SELECT
    COUNT(*) as total_sessions,
    COUNT(first_compact_time) as sessions_with_compact,
    ROUND(AVG(duration_to_compact / 60.0), 1) as avg_minutes_to_compact,
    ROUND(MAX(duration_to_compact / 60.0), 1) as max_minutes_to_compact,
    ROUND(MIN(duration_to_compact / 60.0), 1) as min_minutes_to_compact
FROM sessions
WHERE start_time > strftime('%s', 'now', '-7 days')
  AND duration_to_compact IS NOT NULL;
EOF

echo ""
echo "🎯 Context Preservation Goals:"
echo "--------------------------------"
echo "  ⚠️  Short (<10 min)    - Context fills quickly, consider optimization"
echo "  ✅ Good (10-30 min)    - Healthy context usage"
echo "  🎯 Excellent (30+ min) - Excellent context preservation"
echo ""
echo "💡 Tips to Improve Context Preservation:"
echo "  1. Use Task tool for exploratory searches (offload to subagents)"
echo "  2. Leverage smart tool routing (large files → Haiku delegation)"
echo "  3. Enable parallel workflows (/ctx:execute) to distribute context"
echo "  4. Use /ctx:research for quick answers (preserves main agent context)"
echo ""
