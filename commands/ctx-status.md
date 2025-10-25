---
name: ctx:status
description: Check status of parallel worktrees and tasks
executable: true
---

# Parallel Status - Monitor Parallel Development

You are checking the status of all parallel worktrees and tasks.

**Contextune Integration:** This command can be triggered via `/contextune:parallel:status` or natural language like "check parallel progress", "show parallel status".

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

## Contextune-Specific Additions

### Natural Language Triggers

Users can trigger this command with:
- `/contextune:parallel:status` (explicit)
- "check parallel progress"
- "show parallel status"
- "how are the parallel tasks doing"
- "parallel development status"

Contextune automatically detects these intents.

### Global Availability

Works in ALL projects after installing Contextune:

```bash
/plugin install slashsense
```

### Related Commands

When suggesting next steps, mention:
- `/contextune:parallel:execute` - Execute parallel development
- `/contextune:parallel:cleanup` - Clean up completed work
- `/contextune:parallel:plan` - Create development plan

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
User: "/contextune:parallel:status"

You: [Execute status check workflow]
```

---

## Implementation Notes

- Use the exact same implementation as `/.claude/commands/parallel/status.md`
- Add Contextune branding where appropriate
- Support both explicit and natural language invocation
- This command is read-only - never modifies anything
