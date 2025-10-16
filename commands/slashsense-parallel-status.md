---
name: slashsense:parallel:status
description: Check status of parallel worktrees and tasks
executable: true
---

# Parallel Status - Monitor Parallel Development

You are checking the status of all parallel worktrees and tasks.

**SlashSense Integration:** This command can be triggered via `/slashsense:parallel:status` or natural language like "check parallel progress", "show parallel status".

---

## Execution Instructions

Follow the same instructions as defined in `.claude/commands/parallel/status.md`:

1. **Step 1:** Check for Active Worktrees
2. **Step 2:** Check Git Branch Status
3. **Step 3:** Check GitHub Issues
4. **Step 4:** Analyze Each Worktree
5. **Step 5:** Check Test Status (Optional)
6. **Step 6:** Assess Merge Readiness
7. **Step 7:** Format and Display Report
8. **Step 8:** Provide Next Actions

---

## SlashSense-Specific Additions

### Natural Language Triggers

Users can trigger this command with:
- `/slashsense:parallel:status` (explicit)
- "check parallel progress"
- "show parallel status"
- "how are the parallel tasks doing"
- "parallel development status"

SlashSense automatically detects these intents.

### Global Availability

Works in ALL projects after installing SlashSense:

```bash
/plugin install slashsense
```

### Related Commands

When suggesting next steps, mention:
- `/slashsense:parallel:execute` - Execute parallel development
- `/slashsense:parallel:cleanup` - Clean up completed work
- `/slashsense:parallel:plan` - Create development plan

---

## Example User Interactions

**Natural Language:**
```
User: "how are the parallel tasks going?"

You: [Execute status check workflow]
     Display formatted status report
     Provide recommendations
```

**Explicit Command:**
```
User: "/slashsense:parallel:status"

You: [Execute status check workflow]
```

---

## Implementation Notes

- Use the exact same implementation as `/.claude/commands/parallel/status.md`
- Add SlashSense branding where appropriate
- Support both explicit and natural language invocation
- This command is read-only - never modifies anything
