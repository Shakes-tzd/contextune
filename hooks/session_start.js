#!/usr/bin/env node
/**
 * Contextune SessionStart Hook
 *
 * Displays available Contextune commands at session start.
 * Uses `feedback` field for ZERO context overhead (0 tokens).
 *
 * Context Cost: 0 tokens (feedback is UI-only, not added to Claude's context)
 */

function main() {
  try {
    // Read SessionStart event from stdin (optional - we don't use it)
    // const event = JSON.parse(require('fs').readFileSync(0, 'utf-8'));

    const contextuneInfo = `
💡 Contextune Active (v0.5.4)

Quick Commands:
  /ctx:research - Fast research with 3 parallel agents (1-2 min, ~$0.07)
  /ctx:plan - Create parallel development plan
  /ctx:execute - Execute plan in parallel worktrees
  /ctx:status - Monitor parallel task progress
  /ctx:cleanup - Clean up completed worktrees
  /ctx:configure - Optional customization guide (manual)
  /ctx:stats - View usage statistics

Natural Language Examples:
  • "research best React state library" → /ctx:research
  • "create parallel plan for auth, dashboard, API" → /ctx:plan
  • "what can Contextune do?" → skill: intent-recognition

Just type naturally—I'll detect your intent automatically!

Note: This message has 0 context cost (UI-only display).
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
