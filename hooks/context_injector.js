#!/usr/bin/env node

/**
 * Context Injection Hook for Grounded Research
 *
 * Injects current context into research prompts:
 * - Current date (for accurate web searches)
 * - Tech stack (from package.json, etc.)
 * - Existing specifications
 * - Recent plans
 *
 * This hook runs BEFORE intent detection to ensure research is grounded.
 *
 * Requirements: Node.js (comes with Claude Code - no additional install needed!)
 */

const fs = require('fs');
const path = require('path');

/**
 * Get current context from environment and codebase
 */
function getCurrentContext() {
  // Get current date
  const currentDate = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

  // Get working directory
  const workingDir = process.cwd();
  const projectName = path.basename(workingDir);

  // Detect tech stack
  const techStack = detectTechStack(workingDir);

  // Find specifications
  const specs = findSpecifications(workingDir);

  // Find recent plans
  const recentPlans = findRecentPlans(workingDir);

  return {
    date: currentDate,
    project: projectName,
    workingDir,
    techStack,
    specifications: specs,
    recentPlans
  };
}

/**
 * Detect tech stack from project files
 */
function detectTechStack(workingDir) {
  const stack = {};

  // Check for package.json (Node.js/TypeScript)
  const packageJsonPath = path.join(workingDir, 'package.json');
  if (fs.existsSync(packageJsonPath)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

      stack.language = 'TypeScript/JavaScript';
      stack.runtime = 'Node.js';

      // Detect framework
      const deps = pkg.dependencies || {};
      if (deps.react) {
        stack.framework = 'React';
      } else if (deps.vue) {
        stack.framework = 'Vue';
      } else if (deps.svelte) {
        stack.framework = 'Svelte';
      } else if (deps.next) {
        stack.framework = 'Next.js';
      }

      // Top dependencies
      stack.dependencies = Object.keys(deps).slice(0, 10);
    } catch (err) {
      // Ignore parsing errors
    }
  }

  // Check for pyproject.toml (Python)
  const pyprojectPath = path.join(workingDir, 'pyproject.toml');
  if (fs.existsSync(pyprojectPath)) {
    stack.language = 'Python';
    stack.packageManager = 'UV/pip';
  }

  // Check for go.mod (Go)
  const goModPath = path.join(workingDir, 'go.mod');
  if (fs.existsSync(goModPath)) {
    stack.language = 'Go';
  }

  // Check for Cargo.toml (Rust)
  const cargoPath = path.join(workingDir, 'Cargo.toml');
  if (fs.existsSync(cargoPath)) {
    stack.language = 'Rust';
  }

  return stack;
}

/**
 * Find existing specification documents
 */
function findSpecifications(workingDir) {
  const specs = [];

  const specLocations = [
    'docs/specs',
    'docs/ARCHITECTURE.md',
    'ARCHITECTURE.md',
    'README.md',
    'CONTRIBUTING.md',
    'docs/DESIGN.md'
  ];

  for (const location of specLocations) {
    const fullPath = path.join(workingDir, location);

    if (fs.existsSync(fullPath)) {
      const stat = fs.statSync(fullPath);

      if (stat.isFile()) {
        specs.push(location);
      } else if (stat.isDirectory()) {
        // Add all markdown files in specs directory
        try {
          const files = fs.readdirSync(fullPath);
          for (const file of files) {
            if (file.endsWith('.md')) {
              specs.push(path.join(location, file));
            }
          }
        } catch (err) {
          // Ignore read errors
        }
      }
    }
  }

  return specs;
}

/**
 * Find recent development plans
 */
function findRecentPlans(workingDir) {
  const plansDir = path.join(workingDir, '.parallel', 'plans');

  if (!fs.existsSync(plansDir)) {
    return [];
  }

  const now = new Date();
  const recentPlans = [];

  try {
    const files = fs.readdirSync(plansDir);

    for (const file of files) {
      if (file.startsWith('PLAN-') && file.endsWith('.md')) {
        try {
          // Extract timestamp (PLAN-YYYYMMDD-HHMMSS.md)
          const timestampStr = file.replace('PLAN-', '').replace('.md', '');
          const dateStr = timestampStr.split('-')[0]; // YYYYMMDD

          // Parse date
          const year = parseInt(dateStr.substr(0, 4));
          const month = parseInt(dateStr.substr(4, 2)) - 1;
          const day = parseInt(dateStr.substr(6, 2));
          const planDate = new Date(year, month, day);

          // Calculate age in days
          const ageDays = Math.floor((now - planDate) / (1000 * 60 * 60 * 24));

          // Only include plans from last 30 days
          if (ageDays <= 30) {
            recentPlans.push({
              file: path.join('.parallel', 'plans', file),
              date: planDate.toISOString().split('T')[0],
              ageDays
            });
          }
        } catch (err) {
          // Ignore parsing errors
        }
      }
    }
  } catch (err) {
    // Ignore read errors
  }

  // Sort by age (newest first)
  recentPlans.sort((a, b) => a.ageDays - b.ageDays);

  return recentPlans.slice(0, 5); // Return 5 most recent
}

/**
 * Format context for injection into prompt
 */
function formatContextForInjection(context) {
  const lines = [];

  lines.push('📋 RESEARCH CONTEXT (Use this information in your research!)');
  lines.push('');

  // Current date (CRITICAL for web searches)
  lines.push(`**Current Date:** ${context.date}`);
  lines.push('⚠️ IMPORTANT: When searching the web, use THIS date, not 2024!');

  const year = context.date.split('-')[0];
  lines.push(`   Search for '${year}' or 'latest', not '2024'`);
  lines.push('');

  // Project info
  lines.push(`**Project:** ${context.project}`);
  lines.push(`**Directory:** ${context.workingDir}`);
  lines.push('');

  // Tech stack
  if (Object.keys(context.techStack).length > 0) {
    lines.push('**Tech Stack:**');
    for (const [key, value] of Object.entries(context.techStack)) {
      if (Array.isArray(value)) {
        lines.push(`  • ${key}: ${value.slice(0, 5).join(', ')}`);
      } else {
        lines.push(`  • ${key}: ${value}`);
      }
    }
    lines.push('');
  }

  // Existing specifications
  if (context.specifications.length > 0) {
    lines.push('**Existing Specifications (READ THESE FIRST!):**');
    for (const spec of context.specifications) {
      lines.push(`  • ${spec}`);
    }
    lines.push('');
    lines.push('⚠️ Do NOT research what\'s already specified!');
    lines.push('   Read these docs to understand existing decisions.');
    lines.push('');
  }

  // Recent plans
  if (context.recentPlans.length > 0) {
    lines.push('**Recent Development Plans:**');
    for (const plan of context.recentPlans) {
      lines.push(`  • ${plan.file} (${plan.ageDays} days ago)`);
    }
    lines.push('');
    lines.push('⚠️ Check if similar work was already planned!');
    lines.push('');
  }

  lines.push('---');
  lines.push('');

  return lines.join('\n');
}

/**
 * Check if prompt should receive context injection
 */
function shouldInjectContext(prompt) {
  const keywords = [
    'research',
    'plan',
    'parallel',
    'execute',
    'analyze',
    'design',
    'architect',
    'implement'
  ];

  const lowerPrompt = prompt.toLowerCase();
  return keywords.some(keyword => lowerPrompt.includes(keyword));
}

/**
 * Main hook execution
 */
function main() {
  // Read stdin for hook input
  let inputData = '';

  process.stdin.on('data', chunk => {
    inputData += chunk;
  });

  process.stdin.on('end', () => {
    try {
      // Parse input
      const hookInput = JSON.parse(inputData);
      const prompt = hookInput.prompt || '';

      // Only inject context if prompt mentions research/plan/execute keywords
      if (!shouldInjectContext(prompt)) {
        // Don't inject, continue normally
        process.exit(0);
        return;
      }

      // Get current context
      const context = getCurrentContext();

      // Format context for injection
      const contextBlock = formatContextForInjection(context);

      // Inject at start of prompt
      const modifiedPrompt = `${contextBlock}\n${prompt}`;

      // Build feedback message to show user what was injected
      const feedbackParts = [`ℹ️ Context injected: ${context.date}`];

      if (context.techStack && Object.keys(context.techStack).length > 0) {
        if (context.techStack.language) {
          feedbackParts.push(context.techStack.language);
        }
        if (context.techStack.framework) {
          feedbackParts.push(context.techStack.framework);
        }
      }

      if (context.specifications && context.specifications.length > 0) {
        feedbackParts.push(`${context.specifications.length} spec(s)`);
      }

      const feedback = feedbackParts.join(', ');

      // Output modified prompt with user feedback
      const output = {
        continue: true,
        modifiedPrompt: modifiedPrompt,
        feedback: feedback,
        suppressOutput: false
      };

      console.log(JSON.stringify(output));
      process.exit(0);

    } catch (err) {
      // Fail silently on errors
      // Log to stderr for debugging (won't affect hook output)
      console.error('Context injection error:', err.message);
      process.exit(0);
    }
  });
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  getCurrentContext,
  detectTechStack,
  findSpecifications,
  findRecentPlans,
  formatContextForInjection
};
