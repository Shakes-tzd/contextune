#!/usr/bin/env node
/**
 * Contextune CompactStart Hook
 *
 * Tracks when Claude Code compacts the conversation context.
 * This reveals how well we preserve context for the main agent.
 *
 * Metrics:
 * - Time from session start to first compact
 * - Total compacts per session
 * - Average time between compacts
 *
 * Context Cost: 0 tokens (hook runs outside conversation)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function main() {
  try {
    const dbFile = path.join('.contextune', 'observability.db');

    if (!fs.existsSync(dbFile)) {
      console.error('DEBUG: Observability DB not found, skipping compact tracking');
      process.exit(0);
    }

    const compactTime = Date.now() / 1000; // Unix timestamp

    try {
      // Get most recent session
      const getSessionQuery = `
        SELECT session_id, start_time, first_compact_time
        FROM sessions
        ORDER BY start_time DESC
        LIMIT 1
      `;

      const sessionData = execSync(`sqlite3 "${dbFile}" "${getSessionQuery}"`, {
        encoding: 'utf-8',
        timeout: 1000
      }).trim();

      if (!sessionData) {
        console.error('DEBUG: No active session found');
        process.exit(0);
      }

      const [sessionId, startTime, firstCompactTime] = sessionData.split('|');

      // Calculate duration if this is the first compact
      if (!firstCompactTime || firstCompactTime === '') {
        const duration = compactTime - parseFloat(startTime);

        const updateQuery = `
          UPDATE sessions
          SET first_compact_time = ${compactTime},
              duration_to_compact = ${duration}
          WHERE session_id = '${sessionId}'
        `;

        execSync(`sqlite3 "${dbFile}" "${updateQuery}"`, {
          stdio: 'pipe',
          timeout: 1000
        });

        const minutes = (duration / 60).toFixed(1);
        console.error(`DEBUG: First compact at ${new Date(compactTime * 1000).toISOString()}`);
        console.error(`DEBUG: Context preserved for ${minutes} minutes`);
        console.error(`DEBUG: 🎯 Contextune effectiveness: ${minutes} min of full context`);
      } else {
        // Not first compact - just log
        const timeSinceFirst = compactTime - parseFloat(firstCompactTime);
        console.error(`DEBUG: Subsequent compact at +${(timeSinceFirst / 60).toFixed(1)} min from first`);
      }

      // Log compact event to performance metrics
      const logQuery = `
        INSERT INTO performance_metrics (component, operation, latency_ms, timestamp, metadata)
        VALUES ('session_tracking', 'compact_event', 0, ${compactTime}, '{"compact_time": ${compactTime}}')
      `;

      execSync(`sqlite3 "${dbFile}" "${logQuery}"`, {
        stdio: 'pipe',
        timeout: 1000
      });

    } catch (err) {
      console.error('DEBUG: Failed to track compact event:', err.message);
    }

    // Always continue (don't block compaction)
    const output = {
      continue: true
    };

    console.log(JSON.stringify(output));
    process.exit(0);

  } catch (err) {
    console.error('Contextune CompactStart hook error:', err.message);
    // Always continue (don't block compaction)
    console.log(JSON.stringify({ continue: true }));
    process.exit(0);
  }
}

main();
