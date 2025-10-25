# Contextune Configuration Command Specification

**Command:** `/contextune:configure`
**Purpose:** One-time setup for persistent Contextune visibility
**User Permission:** Required before any modifications

---

## Overview

The `/contextune:configure` command integrates Contextune into the user's Claude Code environment through three mechanisms:

1. **CLAUDE.md Integration** - Persistent context injection
2. **Status Bar Integration** - Always-visible command reminders
3. **Settings Validation** - Ensure plugin is properly enabled

---

## Command File

**Location:** `commands/contextune-configure.md`

**Frontmatter:**
```yaml
---
name: contextune:configure
description: Configure Contextune for persistent visibility in CLAUDE.md and status bar. Run once after installation.
executable: true
---
```

**Content:**
```markdown
# Contextune Configuration - One-Time Setup

This command integrates Contextune into your Claude Code environment for maximum visibility.

## What This Does

1. **CLAUDE.md Integration**
   - Adds Contextune section to `~/.claude/CLAUDE.md`
   - Provides command reference at every session start
   - ~150 token context overhead (minimal)

2. **Status Bar Integration**
   - Adds Contextune commands to your status bar
   - Always visible in Claude Code UI
   - Zero context overhead (UI-only)

3. **Settings Validation**
   - Verifies plugin is enabled
   - Checks skill directory exists
   - Reports configuration status

---

## Workflow

### Step 1: Get User Permission

**IMPORTANT:** Do NOT modify any files without explicit user confirmation!

Present this message:

```
🔧 Contextune Configuration

I can integrate Contextune into your Claude Code environment:

✅ Add Contextune section to ~/.claude/CLAUDE.md (~150 tokens context)
✅ Add Contextune commands to status bar (zero context)
✅ Validate plugin settings

Files to modify:
- ~/.claude/CLAUDE.md (add section)
- ~/.claude/statusline.sh (add commands)

Proceed with configuration? (yes/no)
```

Wait for user response.

**If user declines:** Exit gracefully, explain they can run `/contextune:configure` anytime.

**If user confirms:** Continue to Step 2.

---

### Step 2: Backup Existing Files

Before making any changes, create backups:

```bash
# Create backup directory
mkdir -p ~/.claude/backups/contextune-config-$(date +%Y%m%d-%H%M%S)

# Backup files
cp ~/.claude/CLAUDE.md ~/.claude/backups/contextune-config-$(date +%Y%m%d-%H%M%S)/CLAUDE.md.bak 2>/dev/null || true
cp ~/.claude/statusline.sh ~/.claude/backups/contextune-config-$(date +%Y%m%d-%H%M%S)/statusline.sh.bak 2>/dev/null || true
```

Report backup location to user.

---

### Step 3: Modify CLAUDE.md

Check if `~/.claude/CLAUDE.md` exists:

```bash
if [ -f ~/.claude/CLAUDE.md ]; then
    echo "Found existing CLAUDE.md"
else
    echo "CLAUDE.md not found - will create"
fi
```

**If exists:** Check for existing Contextune section

```bash
if grep -q "## Contextune Plugin" ~/.claude/CLAUDE.md; then
    echo "Contextune section already exists - skipping"
else
    # Add section
fi
```

**Content to Add:**

```markdown
## Contextune Plugin (Parallel Development)

**Quick Research**: `/contextune:research` - Fast answers using parallel agents
**Planning**: `/contextune:parallel:plan` - Create parallel development plans
**Execution**: `/contextune:parallel:execute` - Run tasks in parallel worktrees
**Monitoring**: `/contextune:parallel:status` - Check progress
**Cleanup**: `/contextune:parallel:cleanup` - Remove completed worktrees

**Natural Language:** Just say "research best React libraries" or "create parallel plan for X, Y, Z"

**Skills (Auto-Activated):**
- `parallel-development-expert` - Suggests parallelization opportunities
- `intent-recognition` - Helps discover Contextune capabilities
- `git-worktree-master` - Worktree troubleshooting

Full docs: `@~/.claude/plugins/marketplaces/Contextune/README.md`

---
```

**Implementation:**

Use the Edit tool if file exists, Write tool if creating new.

**Insertion Point:** After "## Advanced Features" section (if exists) or at end of file.

---

### Step 4: Modify Status Bar

Check if `~/.claude/statusline.sh` exists:

```bash
if [ -f ~/.claude/statusline.sh ]; then
    echo "Found existing statusline.sh"
else
    echo "No statusline.sh - will create basic one"
fi
```

**Content to Add** (after existing sections):

```bash
# Section 5: Contextune Commands (if plugin installed)
if grep -q '"contextune@Contextune".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}Contextune:${RESET} /research | /parallel:plan | /parallel:execute"
fi
```

**Insertion Point:** After line 113 (after Flags section) in existing statusline.sh

**If statusline.sh doesn't exist:** Create minimal version:

```bash
#!/bin/bash
set -euo pipefail

# Color codes
YELLOW="\033[1;33m"
RESET="\033[0m"

# Contextune Commands (if plugin installed)
if grep -q '"contextune@Contextune".*true' ~/.claude/settings.json 2>/dev/null; then
    echo -e "${YELLOW}Contextune:${RESET} /research | /parallel:plan | /parallel:execute"
fi
```

Make executable:

```bash
chmod +x ~/.claude/statusline.sh
```

---

### Step 5: Validate Settings

Check if Contextune is enabled in settings:

```bash
if grep -q '"contextune@Contextune".*true' ~/.claude/settings.json 2>/dev/null; then
    echo "✅ Plugin enabled in settings"
else
    echo "⚠️  Plugin not enabled - run '/plugin install contextune@Contextune'"
fi
```

Check if skills exist:

```bash
SKILLS_DIR="~/.claude/plugins/marketplaces/Contextune/skills"
if [ -d "$SKILLS_DIR" ]; then
    SKILL_COUNT=$(ls -1 "$SKILLS_DIR" | wc -l | tr -d ' ')
    echo "✅ Found $SKILL_COUNT Contextune skills"
else
    echo "⚠️  Skills directory not found"
fi
```

---

### Step 6: Report Results

Display configuration summary:

```
🎉 Contextune Configuration Complete!

✅ CLAUDE.md updated
   Location: ~/.claude/CLAUDE.md
   Added: Contextune section (~150 tokens)

✅ Status bar updated
   Location: ~/.claude/statusline.sh
   Added: Contextune commands (UI-only, zero context)

✅ Settings validated
   Plugin: Enabled
   Skills: 3 found

📦 Backups created: ~/.claude/backups/contextune-config-{timestamp}/

🔄 Next Steps:
1. Restart Claude Code to see status bar changes
2. Start new session to load CLAUDE.md changes
3. Try: "research best React libraries" or "/contextune:research"

💡 Tips:
- Status bar shows quick commands: /research | /parallel:plan | /parallel:execute
- CLAUDE.md loaded at session start (automatic context)
- Skills activate automatically when relevant

Run `/contextune:help` to see all capabilities.
```

---

### Step 7: Error Handling

**If CLAUDE.md modification fails:**
```
❌ Failed to modify CLAUDE.md
Reason: {error message}

Manual fix:
1. Open ~/.claude/CLAUDE.md
2. Add this section:

{show Contextune section content}

3. Save and restart Claude Code
```

**If statusline.sh modification fails:**
```
❌ Failed to modify statusline.sh
Reason: {error message}

Manual fix:
1. Open ~/.claude/statusline.sh (or create if missing)
2. Add this code at the end:

{show status bar code}

3. Make executable: chmod +x ~/.claude/statusline.sh
4. Restart Claude Code
```

**If backups fail:**
Continue anyway, but warn user that backups weren't created.

---

## Verification Steps

After configuration, verify:

1. **CLAUDE.md Section Exists:**
   ```bash
   grep -A 10 "## Contextune Plugin" ~/.claude/CLAUDE.md
   ```

2. **Status Bar Code Exists:**
   ```bash
   grep -A 3 "Section 5: Contextune" ~/.claude/statusline.sh
   ```

3. **Files are valid:**
   ```bash
   # CLAUDE.md should be markdown
   file ~/.claude/CLAUDE.md

   # statusline.sh should be executable
   ls -l ~/.claude/statusline.sh | grep -q 'x'
   ```

---

## Rollback Procedure

If user wants to undo configuration:

```bash
# Restore from backups
BACKUP_DIR=$(ls -dt ~/.claude/backups/contextune-config-* | head -1)

cp "$BACKUP_DIR/CLAUDE.md.bak" ~/.claude/CLAUDE.md
cp "$BACKUP_DIR/statusline.sh.bak" ~/.claude/statusline.sh

echo "✅ Rolled back to pre-configuration state"
```

Or create `/contextune:unconfigure` command for automatic rollback.

---

## Testing Plan

### Manual Testing

1. Run `/contextune:configure`
2. Confirm permission prompt shows
3. Confirm backups created
4. Confirm CLAUDE.md updated
5. Confirm statusline.sh updated
6. Restart Claude Code
7. Verify status bar shows Contextune commands
8. Start new session
9. Verify CLAUDE.md context loaded (ask "what Contextune commands exist?")

### Edge Cases

1. **CLAUDE.md doesn't exist** - Create new file
2. **statusline.sh doesn't exist** - Create minimal version
3. **Section already exists** - Skip modification
4. **Permission denied** - Report error, suggest manual fix
5. **Plugin not installed** - Warn but continue (for pre-install setup)

---

## Context Overhead Analysis

### Before Configuration

```
Passive context:
- Skills metadata: ~200 tokens (2 skills)
- Commands metadata: ~240 tokens (8 commands)
Total: ~440 tokens

Discovery: Reactive (skills activate when keywords match)
```

### After Configuration

```
Passive context:
- Skills metadata: ~200 tokens (same)
- Commands metadata: ~240 tokens (same)
- CLAUDE.md section: ~150 tokens (NEW)
- Status bar: 0 tokens (UI-only)
Total: ~590 tokens

Discovery: Proactive (CLAUDE.md reminds Claude at session start)
```

**Trade-off:**
- Cost: +150 tokens passive (~$0.00045 per session)
- Benefit: Persistent visibility, higher discovery rate
- ROI: High (users actually use features they know exist)

---

## Integration with v0.5.1 Plan

This command complements the discovery skills:

**Discovery Layers:**

1. **Session Start** (CLAUDE.md) → Claude reads Contextune section
2. **Passive** (Skills) → Metadata always in context
3. **Active** (Skills) → Activate when keywords match
4. **Always Visible** (Status Bar) → UI reminder
5. **On-Demand** (Hook) → Intent detection when user types

**Synergy:** All layers work together for maximum discoverability!

---

## Implementation Priority

**Phase:** Can be implemented independently or with v0.5.1

**Effort:** 2-3 hours

**Deliverables:**
- `/contextune:configure` command (2h)
- Testing and validation (1h)
- Optional: `/contextune:unconfigure` for rollback (30min)

**Impact:** High (persistent visibility without requiring user knowledge)

---

## Success Metrics

**Target:** 95%+ users configure Contextune after installation

**Measurement:**
```python
{
  "configuration_stats": {
    "total_installs": 100,
    "configured": 95,
    "configuration_rate": "95%",
    "time_to_configure": "2 min average"
  }
}
```

---

## Next Steps

1. Create `commands/contextune-configure.md` with this specification
2. Test on clean Claude Code installation
3. Verify all three mechanisms work (CLAUDE.md, status bar, settings)
4. Add to v0.5.1 plan as optional Phase 4
5. Document in README.md

---

**Status:** Ready for implementation
**Dependencies:** None (can run independently)
**Risk:** Low (backups created, rollback available)
