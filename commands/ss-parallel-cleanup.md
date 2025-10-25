---
name: ss:cleanup
description: Clean up completed worktrees and branches
executable: true
---

# Parallel Cleanup - Remove Completed Worktrees

You are performing cleanup of completed parallel development work.

**SlashSense Integration:** This command can be triggered via `/slashsense:parallel:cleanup` or natural language like "clean up parallel worktrees", "remove completed tasks".

---

## Execution Instructions

Follow the same instructions as defined in `.claude/commands/parallel/cleanup.md`:

1. **Step 1:** Identify Merged Branches
2. **Step 2:** Show Cleanup Plan
3. **Step 3:** Remove Worktrees
4. **Step 4:** Delete Local Branches
5. **Step 5:** Delete Remote Branches (Optional)
6. **Step 6:** Close GitHub Issues (Optional)
7. **Step 7:** Clean Up Directory Structure
8. **Step 8:** Verify Cleanup
9. **Step 9:** Final Recommendations

Also support:
- **Selective Cleanup Mode** - Clean specific tasks only
- **Dry Run Mode** - Show what would be deleted without actually deleting
- **Recovery Instructions** - Help users recover from accidental deletions

---

## SlashSense-Specific Additions

### Natural Language Triggers

Users can trigger this command with:
- `/slashsense:parallel:cleanup` (explicit)
- "clean up parallel worktrees"
- "remove completed tasks"
- "clean up parallel work"
- "delete merged branches"

SlashSense automatically detects these intents.

### Global Availability

Works in ALL projects after installing SlashSense:

```bash
/plugin install slashsense
```

### Related Commands

When suggesting next steps, mention:
- `/slashsense:parallel:status` - Check what's left
- `/slashsense:parallel:execute` - Start new parallel work
- `/slashsense:parallel:plan` - Plan next iteration

---

## Example User Interactions

**Natural Language:**
```
User: "clean up the parallel worktrees"

You: [Execute cleanup workflow]
     1. Identify merged branches
     2. Ask for confirmation
     3. Clean up safely
     4. Report results
```

**Explicit Command:**
```
User: "/slashsense:parallel:cleanup"

You: [Execute cleanup workflow]
```

**With Options:**
```
User: "/slashsense:parallel:cleanup --dry-run"

You: [Show what WOULD be deleted]
     Don't actually delete anything
     Provide option to run for real
```

---

## Safety First

Always:
- Verify branches are merged before deleting
- Ask for user confirmation
- Provide recovery instructions if something goes wrong
- Support dry-run mode for safety
- Never delete unmerged work automatically

---

## Implementation Notes

- Use the exact same implementation as `/.claude/commands/parallel/cleanup.md`
- Add SlashSense branding where appropriate
- Support both explicit and natural language invocation
- Be conservative - when in doubt, keep rather than delete
