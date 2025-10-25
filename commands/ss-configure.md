---
name: ss:configure
description: Configure SlashSense for persistent visibility in CLAUDE.md and status bar. Run once after installation.
executable: true
---

# SlashSense Configuration - One-Time Setup

This command integrates SlashSense into your Claude Code environment for maximum visibility through three mechanisms:

1. **CLAUDE.md Integration** - Persistent context at session start (~150 tokens)
2. **Status Bar Integration** - Always-visible command reminders (zero context)
3. **Settings Validation** - Verify plugin is properly enabled

---

## Step 1: Get User Permission

**IMPORTANT:** Present this message and wait for user confirmation:

```
🔧 SlashSense Configuration

I can integrate SlashSense into your Claude Code environment for better discoverability:

✅ Add SlashSense section to ~/.claude/CLAUDE.md (~150 tokens context)
   - Loaded at every session start
   - Provides command reference
   - Helps Claude remember SlashSense capabilities

✅ Add SlashSense commands to status bar (zero context overhead)
   - Always visible in Claude Code UI
   - Quick reference: /research | /parallel:plan | /parallel:execute

✅ Validate plugin settings
   - Check plugin is enabled
   - Verify skills exist
   - Report configuration status

Files to modify:
- ~/.claude/CLAUDE.md (add SlashSense section)
- ~/.claude/statusline.sh (add command display)

Backups will be created before any changes.

Proceed with configuration? (yes/no)
```

**If user says no:**

```
No problem! You can run `/slashsense:configure` anytime to set this up.

You can still use SlashSense commands directly:
- /slashsense:research
- /slashsense:parallel:plan
- /slashsense:parallel:execute

Or use natural language (intent detection will still work).
```

Then exit.

**If user says yes:** Continue to Step 2.

---

## Step 2: Create Backups

Before making any changes, create backups using Bash:

```bash
# Create timestamped backup directory
BACKUP_DIR=~/.claude/backups/slashsense-config-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup CLAUDE.md if exists
if [ -f ~/.claude/CLAUDE.md ]; then
    cp ~/.claude/CLAUDE.md "$BACKUP_DIR/CLAUDE.md.bak"
    echo "✅ Backed up CLAUDE.md"
fi

# Backup statusline.sh if exists
if [ -f ~/.claude/statusline.sh ]; then
    cp ~/.claude/statusline.sh "$BACKUP_DIR/statusline.sh.bak"
    echo "✅ Backed up statusline.sh"
fi

echo "📦 Backups created in: $BACKUP_DIR"
```

Report backup location to user.

---

## Step 3: Modify CLAUDE.md

### Check if CLAUDE.md exists

Use Read tool to check `~/.claude/CLAUDE.md`:

**If file exists:**
1. Check if SlashSense section already exists:
   - Search for "## SlashSense Plugin"
   - If found: Skip modification, report "Already configured"
   - If not found: Proceed to add section

**If file doesn't exist:**
1. Create new file with basic structure

### Add SlashSense Section

**Content to add:**

```markdown
## SlashSense Plugin (Parallel Development)

**Quick Research**: `/slashsense:research` - Fast answers using parallel agents (1-2 min)
**Planning**: `/slashsense:parallel:plan` - Create parallel development plans with grounded research
**Execution**: `/slashsense:parallel:execute` - Run tasks in parallel using git worktrees
**Monitoring**: `/slashsense:parallel:status` - Check progress across all worktrees
**Cleanup**: `/slashsense:parallel:cleanup` - Remove completed worktrees and branches

**Natural Language Examples:**
- "research best React state libraries" → Triggers research agents
- "create parallel plan for auth, dashboard, API" → Creates structured plan
- "what can SlashSense do?" → Activates intent-recognition skill

**Skills (Auto-Activated):**
- `parallel-development-expert` - Suggests parallelization when you mention multiple tasks
- `intent-recognition` - Helps discover SlashSense capabilities
- `git-worktree-master` - Troubleshoots worktree issues

**Cost Optimization**: SlashSense uses Haiku agents (87% cheaper than Sonnet) for execution.

Full documentation: `@~/.claude/plugins/marketplaces/SlashSense/README.md`

---

```

**Implementation:**

- **If CLAUDE.md exists:** Use Edit tool to add section after "## Advanced Features" or at end
- **If CLAUDE.md doesn't exist:** Use Write tool to create file with minimal structure + SlashSense section

```markdown
# Claude Code Configuration

{User's existing CLAUDE.md content or minimal template}

## SlashSense Plugin (Parallel Development)
{SlashSense section from above}
```

**Report:**
```
✅ CLAUDE.md updated
   Location: ~/.claude/CLAUDE.md
   Added: SlashSense section (~150 tokens)
   Effect: Loaded at every session start
```

---

## Step 4: Modify Status Bar

### Check if statusline.sh exists

Use Read tool to check `~/.claude/statusline.sh`:

**If file exists:**
1. Check if SlashSense section already exists
2. If not, add after existing sections

**If file doesn't exist:**
1. Create minimal statusline.sh with SlashSense section

### Add SlashSense Section

**Content to add** (after existing sections, typically after line 113):

```bash

# Section 5: SlashSense Commands (if plugin installed)
if grep -q '"slashsense@SlashSense".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}SlashSense:${RESET} /research | /parallel:plan | /parallel:execute"
fi
```

**If statusline.sh doesn't exist, create this minimal version:**

```bash
#!/bin/bash
# SlashSense Status Bar Integration
set -euo pipefail

# Color codes
YELLOW="\033[1;33m"
GREEN="\033[1;32m"
RESET="\033[0m"

OUTPUT=""

# Project context
CURRENT_DIR=$(basename "$PWD")
OUTPUT="${GREEN}${CURRENT_DIR}${RESET}"

# SlashSense Commands (if plugin installed)
if grep -q '"slashsense@SlashSense".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}SlashSense:${RESET} /research | /parallel:plan | /parallel:execute"
fi

echo -e "$OUTPUT"
```

**Make executable:**

```bash
chmod +x ~/.claude/statusline.sh
```

**Report:**
```
✅ Status bar updated
   Location: ~/.claude/statusline.sh
   Added: SlashSense command display
   Effect: Visible on every prompt (zero context overhead)
```

---

## Step 5: Validate Settings

Check if plugin is enabled using Bash:

```bash
# Check if SlashSense is enabled
if grep -q '"slashsense@SlashSense".*true' ~/.claude/settings.json 2>/dev/null; then
    echo "✅ Plugin enabled in settings"
else
    echo "⚠️  Plugin not enabled in settings"
    echo "   Run: /plugin install slashsense@SlashSense"
fi
```

Check if skills exist:

```bash
# Check for skills directory
SKILLS_DIR=~/.claude/plugins/marketplaces/SlashSense/skills
if [ -d "$SKILLS_DIR" ]; then
    SKILL_COUNT=$(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$SKILL_COUNT" -gt 0 ]; then
        echo "✅ Found $SKILL_COUNT SlashSense skill(s)"
        ls -1 "$SKILLS_DIR"
    else
        echo "⚠️  Skills directory empty"
    fi
else
    echo "⚠️  Skills directory not found"
    echo "   Expected: $SKILLS_DIR"
fi
```

Check if commands exist:

```bash
# Check for commands
COMMANDS_DIR=~/.claude/plugins/marketplaces/SlashSense/commands
if [ -d "$COMMANDS_DIR" ]; then
    COMMAND_COUNT=$(ls -1 "$COMMANDS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo "✅ Found $COMMAND_COUNT SlashSense command(s)"
else
    echo "⚠️  Commands directory not found"
fi
```

---

## Step 6: Report Results

Display comprehensive configuration summary:

```
🎉 SlashSense Configuration Complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ CLAUDE.md Integration
   Location: ~/.claude/CLAUDE.md
   Added: SlashSense section (~150 tokens)
   Effect: Loaded at every session start

   Claude will now remember:
   - Available commands (/research, /parallel:plan, etc.)
   - Natural language examples
   - Auto-activated skills

✅ Status Bar Integration
   Location: ~/.claude/statusline.sh
   Added: SlashSense command display
   Effect: Always visible (zero context overhead)

   You'll see: SlashSense: /research | /parallel:plan | /parallel:execute

✅ Settings Validated
   Plugin: {Enabled/Not Enabled}
   Skills: {Count} found
   Commands: {Count} found

📦 Backups Created
   Location: {backup directory path}
   Files: CLAUDE.md.bak, statusline.sh.bak

   To rollback: cp {backup_dir}/*.bak ~/.claude/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Next Steps

1. **Restart Claude Code** to see status bar changes
   - Status bar updates on next prompt
   - No restart needed for CLAUDE.md (loads at session start)

2. **Start new session** to load CLAUDE.md changes
   - Exit this session
   - Start fresh
   - Claude will have SlashSense context

3. **Try it out:**
   - Say: "research best React state libraries"
   - Or: "/slashsense:research"
   - Or: "create parallel plan for 3 features"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 How Discovery Works Now

**Layer 1: Session Start (CLAUDE.md)**
→ Claude reads SlashSense section
→ Knows commands exist from session start

**Layer 2: Always Visible (Status Bar)**
→ See commands on every prompt
→ Quick reference without typing /help

**Layer 3: Proactive (Skills)**
→ When you mention multiple tasks
→ Skill suggests: "I can parallelize these!"

**Layer 4: Reactive (Hook)**
→ Type natural language
→ Intent detection suggests commands

All layers work together for maximum discoverability!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Learn More

- `/slashsense:help` - Full documentation
- `/slashsense:stats` - Usage statistics
- `/slashsense:config` - View/edit settings

Questions? Check README.md in plugin directory.
```

---

## Error Handling

### If CLAUDE.md modification fails

```
❌ Failed to modify ~/.claude/CLAUDE.md
Reason: {error message}

Manual fix:
1. Open ~/.claude/CLAUDE.md (create if doesn't exist)
2. Add this section:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## SlashSense Plugin (Parallel Development)

**Quick Research**: `/slashsense:research` - Fast answers using parallel agents
**Planning**: `/slashsense:parallel:plan` - Create parallel development plans
**Execution**: `/slashsense:parallel:execute` - Run tasks in parallel worktrees

**Natural Language:** Just say "research best React libraries"

Full docs: `@~/.claude/plugins/marketplaces/SlashSense/README.md`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. Save and restart Claude Code
```

### If statusline.sh modification fails

```
❌ Failed to modify ~/.claude/statusline.sh
Reason: {error message}

Manual fix:
1. Create or edit ~/.claude/statusline.sh
2. Add this code:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SlashSense Commands
if grep -q '"slashsense@SlashSense".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}SlashSense:${RESET} /research | /parallel:plan | /parallel:execute"
fi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. Make executable: chmod +x ~/.claude/statusline.sh
4. Restart Claude Code
```

### If backup creation fails

```
⚠️  Warning: Could not create backups
Reason: {error message}

Continuing with configuration anyway.

If you want to rollback later, you'll need to manually restore files.
```

Continue with configuration but warn user.

### If settings validation fails

```
⚠️  Plugin may not be properly installed

Issues found:
- {list issues}

Recommendation:
1. Run: /plugin install slashsense@SlashSense
2. Restart Claude Code
3. Run: /slashsense:configure again

Configuration completed anyway (CLAUDE.md and status bar updated).
```

---

## Rollback Instructions

If user wants to undo configuration:

```
To rollback SlashSense configuration:

1. Restore from backups:

   BACKUP_DIR={most recent backup directory}
   cp "$BACKUP_DIR/CLAUDE.md.bak" ~/.claude/CLAUDE.md
   cp "$BACKUP_DIR/statusline.sh.bak" ~/.claude/statusline.sh

2. Or manually remove:

   - Open ~/.claude/CLAUDE.md
   - Remove "## SlashSense Plugin" section

   - Open ~/.claude/statusline.sh
   - Remove "Section 5: SlashSense" code

3. Restart Claude Code

Or create and run: /slashsense:unconfigure (future enhancement)
```

---

## Implementation Notes

**Execution Order:**
1. Get permission (AskUserQuestion if available, or read user response)
2. Create backups (Bash)
3. Modify CLAUDE.md (Read + Edit/Write)
4. Modify statusline.sh (Read + Edit/Write)
5. Validate settings (Bash)
6. Report results (formatted output)

**Tools Used:**
- Bash: Backups, validation, file checks
- Read: Check existing files
- Edit: Modify existing files
- Write: Create new files
- AskUserQuestion: Get permission (optional, can also read text response)

**Safety:**
- Always create backups
- Never overwrite without permission
- Check for existing sections (idempotent)
- Report all changes clearly
- Provide rollback instructions

**Testing:**
- Test with existing CLAUDE.md
- Test with no CLAUDE.md
- Test with existing statusline.sh
- Test with no statusline.sh
- Test with plugin enabled/disabled
- Test rollback procedure

---

## Context Impact

**Before Configuration:**
- Skills: ~200 tokens
- Commands: ~240 tokens
- Total: ~440 tokens

**After Configuration:**
- Skills: ~200 tokens
- Commands: ~240 tokens
- CLAUDE.md section: ~150 tokens (NEW)
- Status bar: 0 tokens (UI-only)
- Total: ~590 tokens

**Trade-off:**
- Cost: +150 tokens (~$0.00045/session)
- Benefit: Persistent visibility at session start
- ROI: High (users discover and use features)

---

## Success Criteria

- [ ] User gives permission
- [ ] Backups created successfully
- [ ] CLAUDE.md updated (or created)
- [ ] statusline.sh updated (or created)
- [ ] Settings validated
- [ ] Results reported clearly
- [ ] Rollback instructions provided
- [ ] User can see status bar changes
- [ ] User can verify CLAUDE.md in new session

---

**Ready to configure SlashSense for persistent visibility!**
