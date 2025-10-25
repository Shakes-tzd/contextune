---
name: ctx:configure
description: Learn how to optionally customize your environment for extra Contextune visibility (manual setup guide)
keywords:
  - configure
  - setup
  - customize
  - configuration
  - setup contextune
  - configure environment
  - customization guide
executable: false
---

# Contextune Optional Customization Guide

**Note:** Contextune works automatically after installation through Skills and Hooks. This guide provides **optional** customizations for users who want extra visibility.

---

## ✅ What Works Automatically (No Setup Needed)

After installing Contextune, these features work immediately:

1. **Intent Detection** - Hook detects slash commands from natural language
2. **Skills** - Claude auto-suggests parallelization and discovers capabilities
3. **Commands** - All `/ctx:*` commands available in autocomplete

**You don't need to configure anything!** Contextune is designed to be zero-setup.

---

## 🎨 Optional Customizations (Manual Setup)

If you want **extra visibility**, you can manually add Contextune to:
1. **CLAUDE.md** - Persistent context at session start (~150 tokens)
2. **Status Bar** - Always-visible command reminders

**Trade-offs:**
- ✅ Pro: Contextune always top-of-mind for Claude
- ✅ Pro: Visual reminders in status bar
- ⚠️ Con: ~150 tokens per session (CLAUDE.md)
- ⚠️ Con: Manual setup required
- ⚠️ Con: You must manually update if plugin changes

---

## Option 1: Add to CLAUDE.md

**File:** `~/.claude/CLAUDE.md`

**Add this section:**

```markdown
## Contextune Plugin (Parallel Development)

**Quick Research**: `/ctx:research` - Fast answers using 3 parallel agents (1-2 min, $0.07)
**Planning**: `/ctx:plan` - Create parallel development plans with grounded research
**Execution**: `/ctx:execute` - Run tasks in parallel using git worktrees
**Monitoring**: `/ctx:status` - Check progress across all worktrees
**Cleanup**: `/ctx:cleanup` - Remove completed worktrees and branches

**Natural Language Examples:**
- "research best React state libraries" → Triggers `/ctx:research`
- "create parallel plan for auth, dashboard, API" → Triggers `/ctx:plan`
- "what can Contextune do?" → Activates `intent-recognition` skill

**Skills (Auto-Activated):**
- `parallel-development-expert` - Suggests parallelization when you mention multiple tasks
- `intent-recognition` - Helps discover Contextune capabilities

**Cost Optimization**: Uses Haiku agents (87% cheaper than Sonnet) for execution.

Full documentation: Type `/ctx:research what can Contextune do?`
```

**How to add:**
```bash
# 1. Open CLAUDE.md
code ~/.claude/CLAUDE.md

# 2. Add the section above anywhere in the file

# 3. Save and restart Claude Code session
```

**Cost:** ~150 tokens per session (loaded at session start)

---

## Option 2: Add to Status Bar

**File:** `~/.claude/statusline.sh`

**Add this section before the final `echo` command:**

```bash
# Section: Contextune Commands (if plugin installed)
if grep -q '"slashsense@Contextune".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}Contextune:${RESET} /ctx:research | /ctx:plan | /ctx:execute"
fi
```

**How to add:**
```bash
# 1. Open statusline.sh
code ~/.claude/statusline.sh

# 2. Find the line near the end that starts with: echo -e "$OUTPUT"

# 3. Add the section above BEFORE that echo line

# 4. Save (changes apply immediately on next status bar refresh)
```

**Cost:** Zero context (UI-only display)

---

## Option 3: Validate Plugin Status

Run this command to check Contextune installation:

```bash
# Check if plugin is enabled
grep -A 2 '"slashsense@Contextune"' ~/.claude/settings.json

# List available skills
ls -la ~/.claude/plugins/*/skills/*/SKILL.md

# List available commands
ls -la ~/.claude/plugins/*/commands/*.md | grep ss-
```

**Expected output:**
- Plugin enabled: `"slashsense@Contextune": true`
- Skills: `parallel-development-expert`, `intent-recognition`
- Commands: `ss-research`, `ss-plan`, `ss-execute`, `ss-status`, `ss-cleanup`, `ss-stats`, `ss-verify`

---

## Recommendation

**Most users: Don't customize!**
- Skills provide automatic discovery
- Hook provides intent detection
- Commands work out of the box

**Power users who want extra visibility:**
- Add Status Bar section (zero context cost)
- Skip CLAUDE.md (Skills are better for discovery)

**Only if you really want persistent context:**
- Add both CLAUDE.md and Status Bar sections
- Understand the ~150 token cost per session
- Manually update if plugin changes

---

## Troubleshooting

**Q: Contextune commands not appearing?**
```bash
/plugin list  # Verify plugin is installed and enabled
/plugin enable slashsense  # Enable if disabled
```

**Q: Skills not activating?**
```bash
# Check skills exist
ls ~/.claude/plugins/marketplaces/Contextune/skills/

# Expected: parallel-development-expert/, intent-recognition/
```

**Q: Hook not detecting intents?**
```bash
# Check hook is registered
cat ~/.claude/plugins/marketplaces/Contextune/hooks/hooks.json

# Expected: UserPromptSubmit hook with user_prompt_submit.py
```

---

## Summary

**Built-in (no setup):**
- ✅ Intent detection via hook
- ✅ Discovery via skills
- ✅ All commands available

**Optional customizations (manual):**
- 🎨 CLAUDE.md integration (~150 tokens/session)
- 🎨 Status bar display (zero tokens)

**Need help?**
- Run `/ctx:research what can Contextune do?`
- Ask Claude: "How do I use Contextune for parallel development?"
- Read README: `cat ~/.claude/plugins/marketplaces/Contextune/README.md`
