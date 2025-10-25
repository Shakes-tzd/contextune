#!/usr/bin/env node

/**
 * Context-Injecting SessionStart Hook Example
 *
 * Demonstrates when to use additionalContext (with token cost):
 * - Loading project context Claude needs to "know"
 * - Injecting configuration Claude should remember
 * - Adding persistent state across the session
 *
 * This DOES consume context tokens - use sparingly!
 */

const fs = require('fs');
const path = require('path');

/**
 * Load Contextune configuration
 */
function getContextuneConfig() {
  const pluginRoot = process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, '..');
  const configPath = path.join(pluginRoot, 'data', 'user_patterns.json');

  if (!fs.existsSync(configPath)) {
    return null;
  }

  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    return config;
  } catch (err) {
    return null;
  }
}

/**
 * Format config for Claude's context
 */
function formatConfigContext(config) {
  if (!config) {
    return null;
  }

  const lines = [];
  lines.push('[Contextune Configuration]');
  lines.push('');

  if (config.customPatterns && Object.keys(config.customPatterns).length > 0) {
    lines.push('Custom command patterns defined:');
    for (const [command, patterns] of Object.entries(config.customPatterns)) {
      lines.push(`  ${command}: ${patterns.slice(0, 3).join(', ')}`);
    }
    lines.push('');
  }

  if (config.detectionSettings) {
    lines.push('Detection settings:');
    lines.push(`  Min confidence: ${config.detectionSettings.minConfidence || 0.7}`);
    lines.push(`  Enabled tiers: ${(config.detectionSettings.enabledTiers || ['keyword', 'model2vec', 'semantic']).join(', ')}`);
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Main hook execution
 */
function main() {
  try {
    // Get Contextune config
    const config = getContextuneConfig();
    const contextBlock = formatConfigContext(config);

    // PATTERN 2: Context injection (HAS token cost)
    // - additionalContext: Added to Claude's context (COSTS TOKENS!)
    // - feedback: User-visible message (optional, no cost)
    // - suppressOutput: typically true for context injection
    const output = {
      continue: true,
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: contextBlock || '[Contextune loaded with default configuration]'
      },
      feedback: '💡 Contextune loaded with your custom patterns',
      suppressOutput: true
    };

    console.log(JSON.stringify(output));
    process.exit(0);

  } catch (err) {
    // Fail silently
    console.error('SessionStart hook error:', err.message);
    process.exit(0);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  getContextuneConfig,
  formatConfigContext
};
