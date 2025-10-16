---
name: slashsense:parallel:execute
description: Execute plan in parallel using git worktrees and multiple Claude sessions
executable: true
---

# Parallel Execute - Run Parallel Development Workflow

You are executing an automated parallel development workflow.

**SlashSense Integration:** This command can be triggered via `/slashsense:parallel:execute` or natural language like "work on these tasks in parallel", "parallelize this work".

---

## Execution Instructions

Follow the same instructions as defined in `.claude/commands/parallel/execute.md` with these additions:

1. Execute all phases exactly as specified in the core execute command
2. When reporting to user, mention SlashSense where appropriate
3. Support natural language detection for related commands

---

## Core Workflow (Reference)

Execute the complete workflow from `/.claude/commands/parallel/execute.md`:

- **Phase 0:** Validate Prerequisites
- **Phase 1:** Setup GitHub Labels and .gitignore
- **Phase 2:** Load or Create Plan
- **Phase 3:** Create GitHub Issues
- **Phase 4:** Create Git Worktrees
- **Phase 5:** Spawn Parallel Subagents (PRIMARY METHOD)
- **Phase 6:** Monitor Progress
- **Phase 7:** Handle Subagent Completion
- **Phase 8:** Merge Completed Work
- **Phase 9:** Cleanup

---

## SlashSense-Specific Additions

### Natural Language Triggers

Users can trigger this command with:
- `/slashsense:parallel:execute` (explicit)
- "work on X, Y, Z in parallel"
- "parallelize these tasks"
- "execute parallel development"

SlashSense automatically detects these intents and routes to this command.

### Global Availability

This command works in ALL projects after installing SlashSense:

```bash
/plugin install slashsense
```

No project-specific configuration needed.

### Related Commands

When suggesting next steps, mention:
- `/slashsense:parallel:status` - Monitor progress
- `/slashsense:parallel:cleanup` - Clean up completed work
- `/slashsense:parallel:plan` - Create development plan

---

## Example User Interactions

**Natural Language:**
```
User: "work on auth, dashboard, and analytics in parallel"

You: [Execute full parallel workflow]
     Mention: "Triggered via SlashSense natural language detection"
```

**Explicit Command:**
```
User: "/slashsense:parallel:execute"

You: [Execute full parallel workflow]
```

---

## Implementation Notes

- Use the exact same implementation as `/.claude/commands/parallel/execute.md`
- Add SlashSense branding to user-facing messages
- Support both explicit and natural language invocation
- Work identically across all projects (global availability)
