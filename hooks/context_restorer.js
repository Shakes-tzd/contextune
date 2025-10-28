#!/usr/bin/env node
/**
 * Context Restorer (SessionStart Hook)
 *
 * Automatically injects preserved context from scratch_pad.md into new session.
 * Complements PreCompact hook (context_preserver.py) for DRY workflow:
 *
 * Session 1: Work → /compact → PreCompact writes scratch_pad.md
 * Session 2: SessionStart injects scratch_pad.md → Claude has context (no Read needed!)
 *
 * DRY Benefit: No redundant file reading - context injected once at session start.
 *
 * Context Cost: Variable (size of scratch_pad.md content, typically 2-5K tokens)
 */

const fs = require('fs');
const path = require('path');

/**
 * Find project root by walking up from current directory
 * @returns {string|null} Project root path or null if not found
 */
function findProjectRoot() {
  let currentDir = process.cwd();
  const root = path.parse(currentDir).root;

  while (currentDir !== root) {
    // Check for common project indicators
    if (
      fs.existsSync(path.join(currentDir, '.git')) ||
      fs.existsSync(path.join(currentDir, 'pyproject.toml')) ||
      fs.existsSync(path.join(currentDir, 'package.json')) ||
      fs.existsSync(path.join(currentDir, 'Cargo.toml'))
    ) {
      return currentDir;
    }
    currentDir = path.dirname(currentDir);
  }

  return null;
}

/**
 * Read and format scratch_pad.md for injection
 * @param {string} scratchPadPath Path to scratch_pad.md
 * @returns {string|null} Formatted context or null if not found
 */
function readScratchPad(scratchPadPath) {
  if (!fs.existsSync(scratchPadPath)) {
    return null;
  }

  try {
    const content = fs.readFileSync(scratchPadPath, 'utf8');

    // Don't inject if file is empty or very small
    if (content.trim().length < 100) {
      return null;
    }

    // Format for injection
    const formatted = [
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '📋 WORKING CONTEXT RESTORED FROM PREVIOUS SESSION',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '',
      content,
      '',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      '✅ You can continue from where you left off.',
      '   Context preserved automatically by PreCompact hook.',
      '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
      ''
    ].join('\n');

    return formatted;

  } catch (err) {
    console.error(`DEBUG: Failed to read scratch_pad.md: ${err.message}`);
    return null;
  }
}

/**
 * Delete scratch_pad.md after successful injection
 * @param {string} scratchPadPath Path to scratch_pad.md
 */
function cleanupScratchPad(scratchPadPath) {
  try {
    if (fs.existsSync(scratchPadPath)) {
      fs.unlinkSync(scratchPadPath);
      console.error('DEBUG: ✅ Cleaned up scratch_pad.md (context injected)');
    }
  } catch (err) {
    console.error(`DEBUG: Failed to cleanup scratch_pad.md: ${err.message}`);
    // Non-fatal
  }
}

/**
 * Main hook execution
 */
function main() {
  try {
    // Read SessionStart event (contains source: startup|resume|clear|compact)
    const event = JSON.parse(fs.readFileSync(0, 'utf-8'));
    const source = event.source || 'unknown';

    console.error(`DEBUG: SessionStart triggered (source: ${source})`);

    // Find project root
    const projectRoot = findProjectRoot();
    if (!projectRoot) {
      console.error('DEBUG: Project root not found, skipping context restoration');
      process.exit(0);
    }

    console.error(`DEBUG: Project root: ${projectRoot}`);

    // Check for scratch_pad.md
    const scratchPadPath = path.join(projectRoot, 'scratch_pad.md');
    const scratchPadContent = readScratchPad(scratchPadPath);

    if (!scratchPadContent) {
      console.error('DEBUG: No scratch_pad.md found or content too small');
      // No context to restore, continue normally
      const output = { continue: true };
      console.log(JSON.stringify(output));
      process.exit(0);
    }

    // Calculate token estimate (rough: 4 chars per token)
    const estimatedTokens = Math.ceil(scratchPadContent.length / 4);
    console.error(`DEBUG: Restoring context (~${estimatedTokens.toLocaleString()} tokens)`);

    // Inject context via additionalContext
    const output = {
      continue: true,
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: scratchPadContent
      },
      feedback: `📋 Working context restored from previous session (~${estimatedTokens.toLocaleString()} tokens)`,
      suppressOutput: false  // Show in transcript for transparency
    };

    console.log(JSON.stringify(output));

    // Cleanup scratch_pad.md after successful injection
    // (prevents re-injection in future sessions)
    cleanupScratchPad(scratchPadPath);

    process.exit(0);

  } catch (err) {
    console.error('Context restoration error:', err.message);
    // Fail gracefully - don't block session
    const output = { continue: true };
    console.log(JSON.stringify(output));
    process.exit(0);
  }
}

main();
