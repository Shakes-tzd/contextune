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

### BUG-002: Plan Extraction Fails with Subagent Transcripts

**Severity:** Medium
**Status:** Open
**Discovered:** 2025-12-23
**Affected Version:** 0.9.1

#### Description

The `extract-current-plan.sh` script extracts from the wrong transcript when subagent transcripts are more recent than the main session transcript, resulting in "No plan found" errors even when a valid plan exists in the conversation.

#### Error Message

```
🔍 Found transcript: /Users/shakes/.claude/projects/-Users-shakes-DevProjects-htmlgraph/agent-a35eba5.jsonl
🔍 Extracting plan...
DEBUG: Loaded 2 conversation entries
DEBUG: No plan found in transcript
❌ Error: No plan found in transcript
```

#### Root Cause

1. Extraction script uses: `ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | head -1`
2. This gets the **most recently modified** file by timestamp
3. When subagents run (via Task tool), they create `agent-*.jsonl` files
4. These subagent transcripts are often modified MORE RECENTLY than the main session
5. Script extracts from subagent transcript instead of main session
6. Subagent transcripts have minimal content (often 2-3 entries) and no plans
7. Result: "No plan found" even though plan exists in main session

#### Example File Structure

```
~/.claude/projects/-Users-shakes-DevProjects-htmlgraph/
├── 1cc2a1f2-b6c9-4b5e-a684-f82ff9cc7b3a.jsonl  # Main session (has plan)
├── agent-a35eba5.jsonl                          # Subagent (2 entries, no plan) ⬅️ Most recent!
├── agent-0f201a73.jsonl                         # Other subagent
└── ...
```

#### Impact

- Plan extraction fails when subagents have run recently
- Users must manually identify correct transcript file
- `/ctx:execute` workflow breaks
- Parallel execution cannot start automatically

#### Reproduction

1. Create a plan in main Claude Code session
2. Run a Task tool (spawns subagent with `agent-*.jsonl` transcript)
3. Run `./scripts/extract-current-plan.sh`
4. Script finds most recent file (subagent transcript)
5. Error: "No plan found in transcript"

#### Expected Behavior

- Script should extract from **main session transcript**, not subagent
- Should identify main session by largest file size or entry count
- Or exclude `agent-*.jsonl` files from consideration
- Or provide transcript file as argument to script

#### Actual Behavior

- Script blindly uses most recent file
- Gets subagent transcript with 2-3 entries
- Fails to find plan that exists in main session

#### Files Affected

- `scripts/extract-current-plan.sh:20` - Uses `ls -t` (sort by time)
- Should use smarter selection logic

#### Proposed Solutions

**Option 1: Exclude Subagent Transcripts (RECOMMENDED)**

```bash
# Find most recent NON-SUBAGENT transcript
TRANSCRIPT_FILE=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | grep -v "agent-" | head -1)
```

**Why this is best:**
- ✅ Simple one-line fix
- ✅ Subagents never contain plans (by design)
- ✅ Main session always has UUID format (not "agent-" prefix)
- ✅ No breaking changes

**Option 2: Find Largest Transcript**

```bash
# Get largest file (most conversation entries)
TRANSCRIPT_FILE=$(ls -lS "$TRANSCRIPT_DIR"/*.jsonl 2>/dev/null | tail -n +2 | head -1 | awk '{print $NF}')
```

**Pros:** Main session usually has most content
**Cons:** Doesn't work if subagent transcript is artificially large

**Option 3: Interactive Selection**

```bash
# Let user choose which transcript
echo "Available transcripts:"
ls -1t "$TRANSCRIPT_DIR"/*.jsonl | nl
read -p "Select transcript number: " selection
```

**Pros:** User has full control
**Cons:** Not automated, breaks scripting

**Option 4: Accept Transcript as Argument**

```bash
# Usage: ./extract-current-plan.sh [transcript-file]
if [ -n "$1" ]; then
    TRANSCRIPT_FILE="$1"
else
    TRANSCRIPT_FILE=$(ls -t "$TRANSCRIPT_DIR"/*.jsonl | grep -v "agent-" | head -1)
fi
```

**Pros:** Flexibility + defaults work
**Cons:** More complex API

#### Workaround

Manually specify the correct transcript:

```bash
# Find main session transcript (UUID format, largest size)
ls -lS ~/.claude/projects/-Users-shakes-DevProjects-htmlgraph/*.jsonl

# Pass to extraction script
uv run scripts/extract-plan-from-context.py /path/to/correct-transcript.jsonl
```

#### Related Issues

- Task tool spawns subagents with separate transcripts
- No way to distinguish main session from subagent programmatically (except filename pattern)
- Claude Code architecture creates multiple transcript files per project

#### Testing

After fix, verify:
1. Create plan in main session
2. Run Task tool to spawn subagent (creates `agent-*.jsonl`)
3. Run `extract-current-plan.sh`
4. Script should find main session transcript (UUID format)
5. Plan should be extracted successfully

---

## Resolved Bugs

(None yet)
