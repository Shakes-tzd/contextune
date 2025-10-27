#!/usr/bin/env node
/**
 * Contextune Version Checker
 *
 * Checks for plugin updates by comparing local version with remote version.
 * Runs on SessionStart hook to notify users of available updates.
 *
 * Features:
 * - Fetches latest version from GitHub
 * - Caches check (once per day)
 * - Non-blocking (never fails session start)
 * - Friendly upgrade notifications
 * - Tracks check history in observability DB
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const { execSync } = require('child_process');

// Configuration
const GITHUB_OWNER = 'Shakes-tzd';
const GITHUB_REPO = 'contextune';
const PLUGIN_JSON_URL = `https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/master/.claude-plugin/plugin.json`;
const CHECK_INTERVAL_HOURS = 24; // Check once per day
const CACHE_FILE = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'plugins', 'contextune', 'data', 'version_cache.json');

/**
 * Get current installed version
 */
function getCurrentVersion() {
  try {
    const pluginRoot = process.env.CLAUDE_PLUGIN_ROOT;
    if (!pluginRoot) {
      return null;
    }

    const pluginJsonPath = path.join(pluginRoot, '.claude-plugin', 'plugin.json');
    const pluginJson = JSON.parse(fs.readFileSync(pluginJsonPath, 'utf-8'));
    return pluginJson.version;
  } catch (error) {
    console.error(`Version check error (local): ${error.message}`);
    return null;
  }
}

/**
 * Fetch latest version from GitHub
 */
function fetchLatestVersion() {
  return new Promise((resolve, reject) => {
    const request = https.get(PLUGIN_JSON_URL, { timeout: 3000 }, (response) => {
      let data = '';

      response.on('data', (chunk) => {
        data += chunk;
      });

      response.on('end', () => {
        try {
          if (response.statusCode === 200) {
            const pluginJson = JSON.parse(data);
            resolve(pluginJson.version);
          } else {
            reject(new Error(`HTTP ${response.statusCode}`));
          }
        } catch (error) {
          reject(error);
        }
      });
    });

    request.on('error', reject);
    request.on('timeout', () => {
      request.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

/**
 * Compare version strings (semver-like)
 */
function compareVersions(current, latest) {
  const currentParts = current.split('.').map(Number);
  const latestParts = latest.split('.').map(Number);

  for (let i = 0; i < Math.max(currentParts.length, latestParts.length); i++) {
    const currentPart = currentParts[i] || 0;
    const latestPart = latestParts[i] || 0;

    if (latestPart > currentPart) return 1;  // Update available
    if (latestPart < currentPart) return -1; // Current is newer (dev version)
  }

  return 0; // Versions are equal
}

/**
 * Get cached version check result
 */
function getCachedCheck() {
  try {
    if (!fs.existsSync(CACHE_FILE)) {
      return null;
    }

    const cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
    const cacheAge = Date.now() - cache.timestamp;
    const cacheValid = cacheAge < CHECK_INTERVAL_HOURS * 60 * 60 * 1000;

    return cacheValid ? cache : null;
  } catch (error) {
    return null;
  }
}

/**
 * Save version check result to cache
 */
function saveCachedCheck(currentVersion, latestVersion, updateAvailable) {
  try {
    const cacheDir = path.dirname(CACHE_FILE);
    if (!fs.existsSync(cacheDir)) {
      fs.mkdirSync(cacheDir, { recursive: true });
    }

    const cache = {
      timestamp: Date.now(),
      currentVersion,
      latestVersion,
      updateAvailable,
      lastCheck: new Date().toISOString()
    };

    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
  } catch (error) {
    // Silent fail - caching is not critical
  }
}

/**
 * Record version check in observability database
 */
function recordVersionCheck(currentVersion, latestVersion, updateAvailable) {
  try {
    const dbFile = path.join(process.env.CLAUDE_PLUGIN_ROOT || '', '.contextune', 'observability.db');

    if (!fs.existsSync(dbFile)) {
      return; // DB doesn't exist yet
    }

    const query = `
      INSERT INTO version_checks (check_time, current_version, latest_version, update_available)
      VALUES (${Date.now() / 1000}, '${currentVersion}', '${latestVersion}', ${updateAvailable ? 1 : 0})
    `;

    execSync(`sqlite3 "${dbFile}" "${query}"`, {
      stdio: 'pipe',
      timeout: 1000
    });
  } catch (error) {
    // Silent fail - observability is not critical
  }
}

/**
 * Generate update notification message
 */
function generateUpdateMessage(currentVersion, latestVersion) {
  return `
╭─────────────────────────────────────────────────╮
│  🎉 Contextune Update Available!                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Current: v${currentVersion.padEnd(10)} →  Latest: v${latestVersion}       │
│                                                  │
│  📦 What's New:                                  │
│     • Performance improvements                   │
│     • Bug fixes and enhancements                │
│     • See full changelog on GitHub              │
│                                                  │
│  🔄 To Update:                                   │
│     /plugin update contextune                    │
│                                                  │
│  📚 Release Notes:                               │
│     github.com/${GITHUB_OWNER}/${GITHUB_REPO}/releases   │
│                                                  │
╰─────────────────────────────────────────────────╯

💡 Tip: Keep Contextune updated for the latest features and fixes!
`;
}

/**
 * Main version check logic
 */
async function checkVersion() {
  try {
    // Get current version
    const currentVersion = getCurrentVersion();
    if (!currentVersion) {
      console.error('Could not determine current version');
      return;
    }

    // Check cache first
    const cached = getCachedCheck();
    if (cached) {
      if (cached.updateAvailable) {
        console.log(generateUpdateMessage(cached.currentVersion, cached.latestVersion));
      }
      return;
    }

    // Fetch latest version from GitHub
    const latestVersion = await fetchLatestVersion();

    // Compare versions
    const comparison = compareVersions(currentVersion, latestVersion);
    const updateAvailable = comparison > 0;

    // Save to cache
    saveCachedCheck(currentVersion, latestVersion, updateAvailable);

    // Record in observability DB
    recordVersionCheck(currentVersion, latestVersion, updateAvailable);

    // Show notification if update available
    if (updateAvailable) {
      console.log(generateUpdateMessage(currentVersion, latestVersion));
    } else {
      console.error(`Contextune v${currentVersion} (latest)`);
    }

  } catch (error) {
    // Silent fail - version check should never block session start
    console.error(`Version check skipped: ${error.message}`);
  }
}

/**
 * Initialize version checks table in observability DB
 */
function initializeDatabase() {
  try {
    const dbFile = path.join(process.env.CLAUDE_PLUGIN_ROOT || '', '.contextune', 'observability.db');

    if (!fs.existsSync(dbFile)) {
      return; // DB doesn't exist yet, will be created by other hooks
    }

    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS version_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_time REAL NOT NULL,
        current_version TEXT NOT NULL,
        latest_version TEXT NOT NULL,
        update_available INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `;

    execSync(`sqlite3 "${dbFile}" "${createTableQuery}"`, {
      stdio: 'pipe',
      timeout: 2000
    });
  } catch (error) {
    // Silent fail
  }
}

// Run version check
if (require.main === module) {
  initializeDatabase();
  checkVersion().catch(err => {
    console.error(`Version check failed: ${err.message}`);
  });
}

module.exports = { checkVersion, compareVersions };
