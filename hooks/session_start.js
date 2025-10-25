#!/usr/bin/env node
/**
 * SlashSense SessionStart Hook
 * 
 * Displays available SlashSense commands at session start.
 * Uses `feedback` field for ZERO context overhead (0 tokens).
 * 
 * Context Cost: 0 tokens (feedback is UI-only, not added to Claude's context)
 */

function main() {
  try {
    // Read SessionStart event from stdin (optional - we don't use it)
    // const event = JSON.parse(require('fs').readFileSync(0, 'utf-8'));

    const slashsenseInfo = `
💡 SlashSense Active (v0.5.2)

Quick Commands:
  /ss:research - Fast research with 3 parallel agents (1-2 min, ~$0.07)
  /ss:plan - Create parallel development plan
  /ss:execute - Execute plan in parallel worktrees
  /ss:status - Monitor parallel task progress
  /ss:cleanup - Clean up completed worktrees
  /ss:configure - Optional customization guide (manual)
  /ss:stats - View usage statistics

Natural Language Examples:
  • "research best React state library" → /ss:research
  • "create parallel plan for auth, dashboard, API" → /ss:plan
  • "what can SlashSense do?" → skill: intent-recognition

Just type naturally—I'll detect your intent automatically!

Note: This message has 0 context cost (UI-only display).
    `.trim();

    // Zero-context pattern: feedback shows to user, NOT added to Claude's context
    const output = {
      continue: true,
      feedback: slashsenseInfo,
      suppressOutput: false  // Show in transcript (Ctrl+R)
    };

    console.log(JSON.stringify(output));
    process.exit(0);
  } catch (err) {
    // Log error but don't block session
    console.error('SlashSense SessionStart hook error:', err.message);
    process.exit(0);  // Success exit to continue session
  }
}

main();
