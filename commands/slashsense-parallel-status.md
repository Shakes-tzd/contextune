---
name: slashsense:parallel:status
description: Check status of parallel worktrees and tasks
---

# Parallel Status - Monitor Parallel Development

**Purpose:** Get real-time status of all parallel worktrees, branches, and GitHub issues.

---

## What This Checks

1. **Git Worktrees** - Active worktrees and branches
2. **GitHub Issues** - Progress on parallel tasks
3. **Branch Status** - Commits, pushes, conflicts
4. **Test Results** - Pass/fail status in each worktree
5. **Merge Readiness** - Which tasks are ready to merge

---

## Status Report Format

```bash
# Run diagnostic commands
git worktree list
git branch -vv
gh issue list --label parallel-execution --state open
```

**Output Dashboard:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PARALLEL DEVELOPMENT STATUS                       │
└─────────────────────────────────────────────────────────────────────┘

📁 WORKTREES
┌─────────┬──────────────────────────────┬─────────────────┬──────────┐
│ Task    │ Path                         │ Branch          │ Status   │
├─────────┼──────────────────────────────┼─────────────────┼──────────┤
│ #123    │ worktrees/task-123           │ feature/task-123│ Active   │
│ #124    │ worktrees/task-124           │ feature/task-124│ Active   │
│ #125    │ worktrees/task-125           │ feature/task-125│ Complete │
└─────────┴──────────────────────────────┴─────────────────┴──────────┘

🔀 BRANCH STATUS
┌─────────┬─────────────────┬──────────┬──────────┬────────────┐
│ Issue   │ Branch          │ Commits  │ Pushed   │ Behind/Ahead│
├─────────┼─────────────────┼──────────┼──────────┼────────────┤
│ #123    │ feature/task-123│ 5        │ ✅ Yes   │ 0/5        │
│ #124    │ feature/task-124│ 3        │ ✅ Yes   │ 0/3        │
│ #125    │ feature/task-125│ 4        │ ✅ Yes   │ 0/4        │
└─────────┴─────────────────┴──────────┴──────────┴────────────┘

📋 GITHUB ISSUES
┌─────────┬─────────────────────┬──────────┬─────────────────┐
│ Issue   │ Title               │ Status   │ Last Update     │
├─────────┼─────────────────────┼──────────┼─────────────────┤
│ #123    │ Authentication      │ In Prog  │ 15 min ago      │
│ #124    │ Dashboard UI        │ In Prog  │ 30 min ago      │
│ #125    │ Analytics           │ Complete │ 1 hour ago      │
└─────────┴─────────────────────┴──────────┴─────────────────┘

🧪 TEST STATUS (if available)
┌─────────┬──────────┬─────────┬─────────┐
│ Task    │ Tests    │ Passed  │ Failed  │
├─────────┼──────────┼─────────┼─────────┤
│ #123    │ 12       │ 12      │ 0       │
│ #124    │ 8        │ 7       │ 1       │
│ #125    │ 15       │ 15      │ 0       │
└─────────┴──────────┴─────────┴─────────┘

✅ MERGE READINESS
┌─────────┬─────────────────────┬───────────┬────────┐
│ Issue   │ Criteria            │ Status    │ Ready  │
├─────────┼─────────────────────┼───────────┼────────┤
│ #123    │ Tests passing       │ ✅        │        │
│         │ Branch pushed       │ ✅        │        │
│         │ Issue updated       │ ❌        │ No     │
│         │ No conflicts        │ ✅        │        │
├─────────┼─────────────────────┼───────────┼────────┤
│ #124    │ Tests passing       │ ❌        │        │
│         │ Branch pushed       │ ✅        │        │
│         │ Issue updated       │ ✅        │ No     │
│         │ No conflicts        │ ✅        │        │
├─────────┼─────────────────────┼───────────┼────────┤
│ #125    │ Tests passing       │ ✅        │        │
│         │ Branch pushed       │ ✅        │        │
│         │ Issue updated       │ ✅        │ ✅ Yes │
│         │ No conflicts        │ ✅        │        │
└─────────┴─────────────────────┴───────────┴────────┘

💡 RECOMMENDATIONS
→ Task #125 is ready to merge
→ Task #124 has 1 failing test - needs attention
→ Task #123 needs issue comment with status update
```

---

## Detailed Task Inspection

For each worktree, I'll check:

```bash
cd worktrees/task-123

# Recent commits
git log --oneline -5

# Files changed
git status

# Tests (if test command exists)
npm test 2>/dev/null || pytest 2>/dev/null || cargo test 2>/dev/null

# Check for conflicts with main
git fetch origin
git merge-base --is-ancestor main HEAD && echo "Up to date" || echo "Needs rebase"
```

---

## Quick Status Checks

**Fast Overview:**
```bash
# Just worktrees
git worktree list

# Just branches
git branch -vv | grep feature/task

# Just issues
gh issue list --label parallel-execution
```

**Specific Task:**
```bash
# Check task #123 only
cd worktrees/task-123 && git status && npm test
```

---

## Alerts & Warnings

**🚨 Critical Issues:**
- Failing tests
- Merge conflicts detected
- Uncommitted changes
- Branch not pushed
- Behind main by many commits

**⚠️ Warnings:**
- No commits in last hour
- Issue not updated recently
- Large number of file changes
- Potential shared file conflicts

**✅ Ready to Merge:**
- All tests passing
- Branch pushed
- Issue marked complete
- No conflicts with main
- Code reviewed (if applicable)

---

## Example Usage

```
You: "/slashsense:parallel:status"

Or naturally: "show parallel status"

Claude: "📊 Checking parallel development status...

**Worktrees Active:** 3
**Tasks Complete:** 1 (#125)
**Tasks In Progress:** 2 (#123, #124)

**Quick Summary:**
✅ Task #125: Ready to merge!
⚠️ Task #124: 1 failing test
🔄 Task #123: Working (last commit 15m ago)

**Recommendations:**
1. Merge #125 now
2. Fix failing test in #124
3. #123 is progressing well

Show detailed report? (Y/n)"
```

---

## Status Frequency

**Check status:**
- Every 30-60 minutes during active development
- Before merging any branch
- When context switching between tasks
- If you notice slowdowns

**Auto-monitoring:**
```bash
# Watch status every 5 minutes
watch -n 300 '/parallel:status'
```

---

## Integration with Workflow

**Phase 4 (Spawning):** Initial status baseline
**Phase 5 (Monitoring):** Regular status checks
**Phase 6 (Merging):** Pre-merge verification
**Phase 7 (Cleanup):** Final status confirmation

---

## Troubleshooting Status Issues

**"Can't access worktree"**
→ Worktree may have been manually deleted
→ Run: `git worktree prune`

**"Branch shows conflicts"**
→ Need to rebase on main
→ In worktree: `git fetch && git rebase origin/main`

**"Tests failing"**
→ Check test output in worktree
→ May need dependency update

**"Issue not found"**
→ Issue may have been closed
→ Check: `gh issue view <number>`

---

## Global Availability

This command is available in **all projects** after installing the SlashSense plugin:

```bash
/plugin install slashsense
```

You can trigger it with:
- `/slashsense:parallel:status` (explicit)
- Natural language: "check parallel progress", "show parallel status"
- SlashSense will detect your intent automatically

---

## Related Commands

- `/slashsense:parallel:plan` - Create development plan
- `/slashsense:parallel:execute` - Execute parallel development
- `/slashsense:parallel:cleanup` - Clean up completed work
