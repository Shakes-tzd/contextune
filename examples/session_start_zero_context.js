#!/usr/bin/env node

/**
 * Zero-Context SessionStart Hook Example
 *
 * Demonstrates the difference between:
 * - feedback: User-visible UI message (NO context cost)
 * - additionalContext: Added to Claude's context (HAS context cost)
 * - suppressOutput: Controls visibility in transcript (Ctrl-R)
 *
 * Use this pattern to show Contextune commands without consuming tokens.
 */

const fs = require('fs');
const path = require('path');

/**
 * Load Contextune commands from commands/ directory
 */
function getContextuneCommands() {
  const pluginRoot = process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, '..');
  const commandsDir = path.join(pluginRoot, 'commands');

  if (!fs.existsSync(commandsDir)) {
    return [];
  }

  const commands = [];
  const files = fs.readdirSync(commandsDir);

  for (const file of files) {
    if (file.endsWith('.md')) {
      try {
        const content = fs.readFileSync(path.join(commandsDir, file), 'utf8');

        // Extract frontmatter
        const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
        if (frontmatterMatch) {
          const frontmatter = frontmatterMatch[1];

          // Parse name and description
          const nameMatch = frontmatter.match(/name:\s*(.+)/);
          const descMatch = frontmatter.match(/description:\s*(.+)/);

          if (nameMatch) {
            commands.push({
              name: `/${nameMatch[1].trim()}`,
              description: descMatch ? descMatch[1].trim() : ''
            });
          }
        }
      } catch (err) {
        // Ignore file read errors
      }
    }
  }

  return commands;
}

/**
 * Format commands as user-visible message
 */
function formatCommandList(commands) {
  if (commands.length === 0) {
    return '💡 Contextune is ready! Type naturally and I\'ll detect commands.';
  }

  const lines = [];
  lines.push('💡 Contextune Commands Available:');
  lines.push('');

  for (const cmd of commands) {
    lines.push(`  ${cmd.name}`);
    if (cmd.description) {
      lines.push(`    ${cmd.description}`);
    }
  }

  lines.push('');
  lines.push('Or just type naturally - I\'ll detect your intent!');

  return lines.join('\n');
}

/**
 * Main hook execution
 */
function main() {
  try {
    // Get Contextune commands
    const commands = getContextuneCommands();
    const message = formatCommandList(commands);

    // PATTERN 1: Zero-context UI message
    // - feedback: Shown to user (NOT added to context)
    // - suppressOutput: false = visible in transcript
    // - NO additionalContext = NO token cost
    const output = {
      continue: true,
      feedback: message,
      suppressOutput: false
      // NOTE: NO hookSpecificOutput.additionalContext = zero tokens!
    };

    console.log(JSON.stringify(output));
    process.exit(0);

  } catch (err) {
    // Fail silently - don't block session start
    console.error('SessionStart hook error:', err.message);
    process.exit(0);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  getContextuneCommands,
  formatCommandList
};
