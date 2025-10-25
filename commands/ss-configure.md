---
name: ss:configure
description: Learn how to optionally customize your environment for extra SlashSense visibility (manual setup guide)
executable: false
---

# SlashSense Optional Customization Guide

**Note:** SlashSense works automatically after installation through Skills and Hooks. This guide provides **optional** customizations for users who want extra visibility.

---

## ✅ What Works Automatically (No Setup Needed)

After installing SlashSense, these features work immediately:

1. **Intent Detection** - Hook detects slash commands from natural language
2. **Skills** - Claude auto-suggests parallelization and discovers capabilities
3. **Commands** - All `/ss:*` commands available in autocomplete

**You don't need to configure anything!** SlashSense is designed to be zero-setup.

---

## 🎨 Optional Customizations (Manual Setup)

If you want **extra visibility**, you can manually add SlashSense to:
1. **CLAUDE.md** - Persistent context at session start (~150 tokens)
2. **Status Bar** - Always-visible command reminders

**Trade-offs:**
- ✅ Pro: SlashSense always top-of-mind for Claude
- ✅ Pro: Visual reminders in status bar
- ⚠️ Con: ~150 tokens per session (CLAUDE.md)
- ⚠️ Con: Manual setup required
- ⚠️ Con: You must manually update if plugin changes

---

## Option 1: Add to CLAUDE.md

**File:** `~/.claude/CLAUDE.md`

**Add this section:**

```markdown
## SlashSense Plugin (Parallel Development)

**Quick Research**: `/ss:research` - Fast answers using 3 parallel agents (1-2 min, $0.07)
**Planning**: `/ss:plan` - Create parallel development plans with grounded research
**Execution**: `/ss:execute` - Run tasks in parallel using git worktrees
**Monitoring**: `/ss:status` - Check progress across all worktrees
**Cleanup**: `/ss:cleanup` - Remove completed worktrees and branches

**Natural Language Examples:**
- "research best React state libraries" → Triggers `/ss:research`
- "create parallel plan for auth, dashboard, API" → Triggers `/ss:plan`
- "what can SlashSense do?" → Activates `intent-recognition` skill

**Skills (Auto-Activated):**
- `parallel-development-expert` - Suggests parallelization when you mention multiple tasks
- `intent-recognition` - Helps discover SlashSense capabilities

**Cost Optimization**: Uses Haiku agents (87% cheaper than Sonnet) for execution.

Full documentation: Type `/ss:research what can SlashSense do?`
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
# Section: SlashSense Commands (if plugin installed)
if grep -q '"slashsense@SlashSense".*true' ~/.claude/settings.json 2>/dev/null; then
    OUTPUT="${OUTPUT} | ${YELLOW}SlashSense:${RESET} /ss:research | /ss:plan | /ss:execute"
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

Run this command to check SlashSense installation:

```bash
# Check if plugin is enabled
grep -A 2 '"slashsense@SlashSense"' ~/.claude/settings.json

# List available skills
ls -la ~/.claude/plugins/*/skills/*/SKILL.md

# List available commands
ls -la ~/.claude/plugins/*/commands/*.md | grep ss-
```

**Expected output:**
- Plugin enabled: `"slashsense@SlashSense": true`
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

**Q: SlashSense commands not appearing?**
```bash
/plugin list  # Verify plugin is installed and enabled
/plugin enable slashsense  # Enable if disabled
```

**Q: Skills not activating?**
```bash
# Check skills exist
ls ~/.claude/plugins/marketplaces/SlashSense/skills/

# Expected: parallel-development-expert/, intent-recognition/
```

**Q: Hook not detecting intents?**
```bash
# Check hook is registered
cat ~/.claude/plugins/marketplaces/SlashSense/hooks/hooks.json

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
- Run `/ss:research what can SlashSense do?`
- Ask Claude: "How do I use SlashSense for parallel development?"
- Read README: `cat ~/.claude/plugins/marketplaces/SlashSense/README.md`
