---
name: ctx:status
description: Check status of parallel worktrees and tasks
keywords:
  - check status
  - parallel status
  - show progress
  - task status
  - worktree status
  - show parallel progress
  - check parallel
executable: true
---

# Parallel Status - Monitor Parallel Development

You are checking the status of all parallel worktrees and tasks.

**Contextune Integration:** This command can be triggered via `/contextune:parallel:status` or natural language like "check parallel progress", "show parallel status".

---

## Execution Workflow

### Step 1: Check for Active Worktrees

**Run this command:**
```bash
git worktree list
```

**Expected output:**
```
/Users/you/project              abc1234 [main]
/Users/you/project/worktrees/task-0  def5678 [feature/task-0]
/Users/you/project/worktrees/task-1  ghi9012 [feature/task-1]
```

**Parse the output:**
- Line 1: Main worktree (skip)
- Lines 2+: Parallel worktrees (check each)
- Extract: worktree path, commit hash, branch name

**If no worktrees found:**
```
No parallel tasks active.
```
Stop here - nothing to report.

---

### Step 2: Check Task Files for Status

**For each worktree found, read its task file:**

```bash
# Get task ID from worktree path
task_id=$(basename /path/to/worktrees/task-0)

# Read task status from YAML frontmatter
grep "^status:" .parallel/plans/tasks/${task_id}.md
```

**Status values:**
- `pending`: Not started yet
- `in_progress`: Currently working
- `completed`: Done and pushed
- `blocked`: Encountered error

---

### Step 3: Check Git Status Per Worktree

**For each worktree, check uncommitted changes:**

```bash
cd worktrees/task-0
git status --short
cd ../..
```

**Interpret output:**
- Empty: Clean working tree (good!)
- `M file.ts`: Modified files (work in progress)
- `??` file: Untracked files (needs git add)

---

### Step 4: Check Branch Status (Ahead/Behind)

**For each worktree, check if branch is pushed:**

```bash
cd worktrees/task-0
git status --branch --porcelain | head -1
cd ../..
```

**Example outputs:**
- `## feature/task-0...origin/feature/task-0`: Branch is up to date ✅
- `## feature/task-0...origin/feature/task-0 [ahead 2]`: 2 commits not pushed ⚠️
- `## feature/task-0`: No remote branch yet ⚠️

---

### Step 5: Check Test Status (if available)

**Look for test result files:**

```bash
ls worktrees/task-0/test-results.xml 2>/dev/null || echo "No test results"
ls worktrees/task-0/.pytest_cache 2>/dev/null || echo "No pytest cache"
```

**Or check recent git log for test-related commits:**

```bash
cd worktrees/task-0
git log --oneline -5 | grep -i "test"
cd ../..
```

---

### Step 6: Format Status Report

**Create comprehensive status report:**

```
📊 Parallel Development Status

**Active Tasks:** 3
**Completed:** 1
**In Progress:** 2
**Blocked:** 0

─────────────────────────────────────────────────

Task 0: Fix ctx-stats.md
├─ Status: completed ✅
├─ Branch: feature/task-0
├─ Commits: 3 commits ahead
├─ Tests: All passing ✅
└─ Ready: Yes - can merge

Task 1: Fix ctx-status.md
├─ Status: in_progress ⏳
├─ Branch: feature/task-1
├─ Commits: 1 commit ahead (not pushed)
├─ Tests: Not run yet
└─ Ready: No - work in progress

Task 2: Fix ctx-cleanup.md
├─ Status: pending 📋
├─ Branch: feature/task-2
├─ Commits: None (clean)
└─ Ready: No - not started

─────────────────────────────────────────────────

**Next Actions:**
• task-0: Ready to merge/create PR
• task-1: Push changes and run tests
• task-2: Start implementation
```

---

### Step 7: Provide Recommendations

**Based on task statuses, suggest next actions:**

**If any tasks are completed:**
```
✅ Tasks ready for review: task-0

Suggested action:
./scripts/create_prs.sh
```

**If any tasks are blocked:**
```
⚠️ Blocked tasks need attention: task-N

Check error logs:
cd worktrees/task-N && git log -1
```

**If all tasks are complete:**
```
🎉 All tasks completed!

Next steps:
1. Create PRs: ./scripts/create_prs.sh
2. Or merge directly: /ctx:cleanup
```

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
