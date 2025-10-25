#!/usr/bin/env node
/**
 * Contextune SessionStart Hook
 *
 * 1. Clears old detection state from status line
 * 2. Displays available Contextune commands at session start
 *
 * Uses `feedback` field for ZERO context overhead (0 tokens).
 *
 * Context Cost: 0 tokens (feedback is UI-only, not added to Claude's context)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function main() {
  try {
    // Clear old detection state from observability database
    const dbFile = path.join('.contextune', 'observability.db');
    try {
      if (fs.existsSync(dbFile)) {
        // Fast SQLite DELETE query (0.1ms)
        execSync(`sqlite3 "${dbFile}" "DELETE FROM current_detection WHERE id = 1"`, {
          stdio: 'pipe',
          timeout: 1000
        });
        console.error('DEBUG: Cleared old detection from observability DB');
      }
    } catch (err) {
      console.error('DEBUG: Failed to clear detection from observability DB:', err.message);
      // Non-fatal, continue with session start message
    }

    // Read SessionStart event from stdin (optional - we don't use it)
    // const event = JSON.parse(require('fs').readFileSync(0, 'utf-8'));

    const contextuneInfo = `
🎯 Contextune Active (v0.5.4) - Natural Language → Slash Commands

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Try It Now (Just Type These):

  "research best React state management library"
    → Spawns 3 parallel agents (web + codebase + deps)
    → Results in 1-2 min, ~$0.07

  "work on auth, dashboard, and API in parallel"
    → Creates plan + worktrees + parallel execution
    → 30-70% faster than sequential

  "what can Contextune do?"
    → Shows full capabilities guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Most Used Commands:

  /ctx:research <query>    Fast answers (3 parallel agents)
  /ctx:status              Check parallel worktrees progress
  /ctx:help                Example-first command reference

🔧 Advanced Workflow:

  /ctx:plan                Create parallel development plan
  /ctx:execute             Run tasks in parallel worktrees
  /ctx:cleanup             Clean up completed worktrees
  /ctx:configure           Setup status bar integration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Tip: Enable status bar for real-time detection display
   Run: /ctx:configure

⚡ Zero context overhead - This message costs 0 tokens!
    `.trim();

    // Zero-context pattern: feedback shows to user, NOT added to Claude's context
    const output = {
      continue: true,
      feedback: contextuneInfo,
      suppressOutput: false  // Show in transcript (Ctrl+R)
    };

    console.log(JSON.stringify(output));
    process.exit(0);
  } catch (err) {
    // Log error but don't block session
    console.error('Contextune SessionStart hook error:', err.message);
    process.exit(0);  // Success exit to continue session
  }
}

main();
