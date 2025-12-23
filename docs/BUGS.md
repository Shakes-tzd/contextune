# Known Bugs

## Active Bugs

### BUG-001: Missing Node.js Dependencies in Cached Plugin

**Severity:** High
**Status:** Open
**Discovered:** 2025-12-23
**Affected Version:** 0.9.1

#### Description

The `session_start_git_context.js` hook fails at session start because Node.js dependencies are not installed in the cached plugin directory.

#### Error Message

```
Error: Cannot find module 'yaml'
Require stack:
- /Users/shakes/.claude/plugins/cache/Contextune/contextune/0.9.1/hooks/session_start_git_context.js
    at Function._resolveFilename (node:internal/modules/cjs/loader:1383:15)
    ...
    at Object.<anonymous> (/Users/shakes/.claude/plugins/cache/Contextune/contextune/0.9.1/hooks/session_start_git_context.js:18:14)
```

#### Root Cause

1. `package.json` declares `yaml: ^2.3.4` as dependency
2. `session_start_git_context.js:18` requires the `yaml` package
3. When plugin is installed to cache directory (`~/.claude/plugins/cache/Contextune/contextune/0.9.1/`), `npm install` is not run
4. No `node_modules` directory exists in cached plugin
5. Node.js module resolution fails when hook tries to load `yaml`

#### Impact

- SessionStart hook (`session_start_git_context.js`) fails on every session
- Users see error message at session start
- Git context injection feature is non-functional
- Breaks session continuity feature

#### Reproduction

1. Install Contextune plugin
2. Start new Claude Code session
3. SessionStart hook triggers
4. Error: Cannot find module 'yaml'

#### Expected Behavior

- Plugin installation should run `npm install` in cache directory
- Hook should successfully load `yaml` module
- Git context should be injected at session start

#### Actual Behavior

- `node_modules` directory missing from cache
- Hook fails immediately on `require('yaml')`
- SessionStart hook execution fails

#### Files Affected

- `/Users/shakes/.claude/plugins/cache/Contextune/contextune/0.9.1/package.json` - Has dependency
- `/Users/shakes/.claude/plugins/cache/Contextune/contextune/0.9.1/hooks/session_start_git_context.js:18` - Requires yaml
- Missing: `/Users/shakes/.claude/plugins/cache/Contextune/contextune/0.9.1/node_modules/`

#### Proposed Solutions

**Option 1: Use Python Hook Instead (RECOMMENDED)**

Rewrite `session_start_git_context.js` as Python script using UV (like other hooks):

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
```

**Why this is best:**
- ✅ Consistent with other Contextune hooks (all use UV + Python)
- ✅ UV handles dependencies automatically via inline metadata
- ✅ No bundling or installation issues
- ✅ Aligned with project's Python focus
- ✅ Claude Code already supports UV scripts

**Option 2: Bundle Dependencies**

Use webpack/rollup to bundle `yaml` module into single JS file.

**Option 3: Remove Dependency**

Rewrite hook to use Node.js built-in modules only (no external deps).
Parse YAML manually or use JSON instead.

**Option 4: Add Installation Instructions**

Document manual `npm install` step in plugin README.

#### Workaround

Manually install dependencies in cache directory:

```bash
cd ~/.claude/plugins/cache/Contextune/contextune/0.9.1/
npm install
```

#### Related Issues

- Plugin installation/deployment process needs review
- Consider UV-based hooks for consistency
- Node.js hooks may need bundling strategy

#### Testing

After fix, verify:
1. Fresh plugin installation
2. `node_modules` exists in cache directory
3. SessionStart hook executes successfully
4. No "Cannot find module" errors

---

## Resolved Bugs

(None yet)
