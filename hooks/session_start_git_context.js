#!/usr/bin/env node
/**
 * SessionStart Git Context Injector
 *
 * Injects differential git context at session start:
 * - Commits since last session
 * - Files changed since last session
 * - Current git status
 * - Branch information
 *
 * Token Overhead: ~1-2K tokens (differential only, not full history)
 * Blocking: No
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

/**
 * Load last session metadata
 */
function loadLastSession() {
    try {
        const cacheDir = path.join(
            process.env.HOME,
            '.claude',
            'plugins',
            'contextune',
            '.cache'
        );
        const lastSessionFile = path.join(cacheDir, 'last_session.yaml');

        if (!fs.existsSync(lastSessionFile)) {
            return null;
        }

        const content = fs.readFileSync(lastSessionFile, 'utf8');
        return yaml.parse(content);
    } catch (error) {
        console.error('DEBUG: Failed to load last session:', error.message);
        return null;
    }
}

/**
 * Get commits since last session
 */
function getCommitsSinceLastSession(lastCommit, limit = 10) {
    try {
        const cmd = `git log --oneline ${lastCommit}..HEAD -n ${limit}`;
        const output = execSync(cmd, { encoding: 'utf8', timeout: 2000 });

        const commits = output.trim().split('\n').filter(line => line);
        return commits;
    } catch (error) {
        console.error('DEBUG: Failed to get commits:', error.message);
        return [];
    }
}

/**
 * Get files changed since last session
 */
function getFilesChanged(lastCommit) {
    try {
        const cmd = `git diff --name-status ${lastCommit}..HEAD`;
        const output = execSync(cmd, { encoding: 'utf8', timeout: 2000 });

        const changes = [];
        for (const line of output.trim().split('\n')) {
            if (!line) continue;

            const parts = line.split('\t');
            if (parts.length >= 2) {
                const status = parts[0];
                const file = parts[1];

                // Decode status
                let changeType = 'modified';
                if (status === 'A') changeType = 'added';
                else if (status === 'D') changeType = 'deleted';
                else if (status === 'M') changeType = 'modified';
                else if (status.startsWith('R')) changeType = 'renamed';

                changes.push({ file, type: changeType, status });
            }
        }

        return changes;
    } catch (error) {
        console.error('DEBUG: Failed to get file changes:', error.message);
        return [];
    }
}

/**
 * Get diff statistics
 */
function getDiffStats(lastCommit) {
    try {
        const cmd = `git diff --shortstat ${lastCommit}..HEAD`;
        const output = execSync(cmd, { encoding: 'utf8', timeout: 2000 });
        return output.trim();
    } catch (error) {
        return 'Unable to calculate diff stats';
    }
}

/**
 * Get current git status
 */
function getCurrentStatus() {
    try {
        const cmd = 'git status --short';
        const output = execSync(cmd, { encoding: 'utf8', timeout: 1000 });

        const lines = output.trim().split('\n').filter(line => line);

        if (lines.length === 0) {
            return { clean: true, uncommitted: 0 };
        }

        return { clean: false, uncommitted: lines.length, files: lines.slice(0, 5) };
    } catch (error) {
        return { clean: true, uncommitted: 0 };
    }
}

/**
 * Calculate time since last session
 */
function getTimeSince(timestamp) {
    try {
        const lastTime = new Date(timestamp);
        const now = new Date();
        const diffMs = now - lastTime;

        const minutes = Math.floor(diffMs / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'just now';
    } catch (error) {
        return 'recently';
    }
}

/**
 * Generate context summary
 */
function generateContextSummary(lastSession) {
    const commits = getCommitsSinceLastSession(lastSession.last_commit);
    const filesChanged = getFilesChanged(lastSession.last_commit);
    const diffStats = getDiffStats(lastSession.last_commit);
    const currentStatus = getCurrentStatus();
    const timeSince = getTimeSince(lastSession.ended_at);

    // Build summary
    let summary = `📋 Git Context Since Last Session (${timeSince})\n\n`;

    // Commit activity
    if (commits.length > 0) {
        summary += `**Git Activity:**\n`;
        summary += `- ${commits.length} new commit${commits.length > 1 ? 's' : ''}\n`;
        summary += `- ${diffStats}\n`;
        summary += `- Branch: ${lastSession.branch}\n\n`;

        summary += `**Recent Commits:**\n`;
        commits.slice(0, 5).forEach(commit => {
            summary += `  ${commit}\n`;
        });

        if (commits.length > 5) {
            summary += `  ... and ${commits.length - 5} more\n`;
        }
        summary += '\n';
    } else {
        summary += `**Git Activity:** No commits since last session\n\n`;
    }

    // File changes
    if (filesChanged.length > 0) {
        summary += `**Files Changed (${filesChanged.length} total):**\n`;

        const byType = { added: [], modified: [], deleted: [], renamed: [] };
        filesChanged.forEach(change => {
            const list = byType[change.type] || byType.modified;
            list.push(change.file);
        });

        if (byType.added.length > 0) {
            summary += `  Added (${byType.added.length}):\n`;
            byType.added.slice(0, 3).forEach(f => summary += `    - ${f}\n`);
            if (byType.added.length > 3) summary += `    ... and ${byType.added.length - 3} more\n`;
        }

        if (byType.modified.length > 0) {
            summary += `  Modified (${byType.modified.length}):\n`;
            byType.modified.slice(0, 3).forEach(f => summary += `    - ${f}\n`);
            if (byType.modified.length > 3) summary += `    ... and ${byType.modified.length - 3} more\n`;
        }

        if (byType.deleted.length > 0) {
            summary += `  Deleted (${byType.deleted.length}):\n`;
            byType.deleted.slice(0, 3).forEach(f => summary += `    - ${f}\n`);
        }

        summary += '\n';
    }

    // Current working directory status
    if (!currentStatus.clean) {
        summary += `**Current Status:**\n`;
        summary += `- ${currentStatus.uncommitted} uncommitted change${currentStatus.uncommitted > 1 ? 's' : ''}\n`;

        if (currentStatus.files && currentStatus.files.length > 0) {
            summary += `\n**Uncommitted:**\n`;
            currentStatus.files.forEach(file => {
                summary += `  ${file}\n`;
            });
        }
        summary += '\n';
    } else {
        summary += `**Current Status:** Working directory clean ✅\n\n`;
    }

    // Last session context
    if (lastSession.files_worked_on && lastSession.files_worked_on.length > 0) {
        summary += `**Last Session Work:**\n`;
        summary += `- Worked on ${lastSession.file_count} file${lastSession.file_count > 1 ? 's' : ''}\n`;

        if (lastSession.files_worked_on.length <= 5) {
            lastSession.files_worked_on.forEach(f => {
                summary += `  - ${f}\n`;
            });
        } else {
            lastSession.files_worked_on.slice(0, 3).forEach(f => {
                summary += `  - ${f}\n`;
            });
            summary += `  ... and ${lastSession.files_worked_on.length - 3} more\n`;
        }
        summary += '\n';
    }

    summary += `---\n\n`;
    summary += `**Ready to continue!** Git is synced and tracking all changes.\n`;

    return summary;
}

/**
 * Main hook entry point
 */
function main() {
    try {
        // Read stdin
        const chunks = [];
        process.stdin.on('data', chunk => chunks.push(chunk));

        process.stdin.on('end', () => {
            try {
                const hookData = JSON.parse(Buffer.concat(chunks).toString());

                console.error('DEBUG: SessionStart git context injector triggered');

                // Load last session
                const lastSession = loadLastSession();

                if (!lastSession) {
                    console.error('DEBUG: No previous session found, skipping git context');
                    // First session or cache cleared
                    const response = { continue: true };
                    console.log(JSON.stringify(response));
                    return;
                }

                console.error(`DEBUG: Last session: ${lastSession.session_id}`);
                console.error(`DEBUG: Last commit: ${lastSession.last_commit}`);

                // Generate context summary
                const summary = generateContextSummary(lastSession);

                console.error(`DEBUG: Generated context summary (${summary.length} chars)`);

                // Inject context
                const response = {
                    continue: true,
                    additionalContext: summary,
                    suppressOutput: false
                };

                console.log(JSON.stringify(response));

            } catch (error) {
                console.error('DEBUG: SessionStart error:', error.message);
                // Never block - always continue
                const response = { continue: true };
                console.log(JSON.stringify(response));
            }
        });

    } catch (error) {
        console.error('DEBUG: SessionStart fatal error:', error.message);
        // Never block
        const response = { continue: true };
        console.log(JSON.stringify(response));
    }
}

// Handle stdin
if (require.main === module) {
    main();
}
