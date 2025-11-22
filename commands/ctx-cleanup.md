---
name: ctx:cleanup
description: Clean up completed worktrees and branches
keywords:
  - clean up
  - cleanup worktrees
  - remove worktrees
  - cleanup tasks
  - cleanup parallel
  - remove completed
  - clean worktrees
executable: true
---

# Parallel Cleanup - Remove Completed Worktrees

You are performing cleanup of completed parallel development work.

**Contextune Integration:** This command can be triggered via `/contextune:parallel:cleanup` or natural language like "clean up parallel worktrees", "remove completed tasks".

---

## Execution Workflow

### Step 1: Identify Merged Branches

**Check which parallel branches have been merged to main:**

```bash
# List all feature branches that are fully merged
git branch --merged main | grep "feature/task-"
```

**Expected output:**
```
  feature/task-0
  feature/task-2
```

**Interpret:**
- Listed branches: Safe to delete (already in main) ✅
- Not listed: Still has unmerged commits ⚠️

---

### Step 2: Show Cleanup Plan (Ask User)

**Before deleting anything, show what will be removed:**

```
🧹 Cleanup Plan

**Will remove:**
✅ Worktree: worktrees/task-0 (merged to main)
✅ Local branch: feature/task-0 (merged)
✅ Remote branch: origin/feature/task-0 (if exists)

✅ Worktree: worktrees/task-2 (merged to main)
✅ Local branch: feature/task-2 (merged)
✅ Remote branch: origin/feature/task-2 (if exists)

**Will keep:**
⏳ Worktree: worktrees/task-1 (not merged - has uncommitted work)

Proceed with cleanup? (yes/no)
```

**Ask user for confirmation before proceeding.**

---

### Step 3: Remove Merged Worktrees

**For each merged branch, remove its worktree:**

```bash
# Remove worktree for task-0
git worktree remove worktrees/task-0

# Remove worktree for task-2
git worktree remove worktrees/task-2
```

**Expected output per removal:**
```
✅ Removed worktree 'worktrees/task-0'
```

**If removal fails:**
```
Error: worktree has uncommitted changes
```
→ Skip this worktree, warn user

---

### Step 4: Delete Local Merged Branches

**Delete the local branches that were merged:**

```bash
# Delete local branch
git branch -d feature/task-0

# Delete local branch
git branch -d feature/task-2
```

**Expected output:**
```
Deleted branch feature/task-0 (was abc1234).
```

**If deletion fails:**
```
error: The branch 'feature/task-0' is not fully merged.
```
→ Use `-D` to force (ask user first!) or skip

---

### Step 5: Delete Remote Branches (Optional)

**Ask user:** "Also delete remote branches?"

**If yes:**
```bash
# Delete remote branch
git push origin --delete feature/task-0

# Delete remote branch
git push origin --delete feature/task-2
```

**Expected output:**
```
To github.com:user/repo.git
 - [deleted]         feature/task-0
```

**If no:** Skip this step

---

### Step 6: Archive Completed Tasks (Optional)

**Move completed task files to archive:**

```bash
# Create archive directory
mkdir -p .parallel/archive/completed-$(date +%Y%m%d)

# Move completed task files
mv .parallel/plans/tasks/task-0.md .parallel/archive/completed-$(date +%Y%m%d)/
mv .parallel/plans/tasks/task-2.md .parallel/archive/completed-$(date +%Y%m%d)/
```

**Or keep them for reference** (task files are lightweight)

---

### Step 7: Prune Stale References

**Clean up git's internal references:**

```bash
git worktree prune
git remote prune origin
```

**Expected output:**
```
✅ Pruned worktree references
✅ Pruned remote references
```

---

### Step 8: Verify Cleanup

**Confirm everything was cleaned up:**

```bash
# Check remaining worktrees
git worktree list

# Check remaining feature branches
git branch | grep "feature/task-"

# Check remote branches
git branch -r | grep "feature/task-"
```

**Expected:** Only unmerged tasks should remain

---

### Step 9: Report Results

```
✅ Cleanup complete!

**Removed:**
• 2 worktrees (task-0, task-2)
• 2 local branches
• 2 remote branches

**Kept:**
• 1 worktree (task-1 - unmerged)

**Remaining parallel work:**
- task-1: In progress (3 commits ahead)

**Next actions:**
• Continue work on task-1
• Or run /ctx:status for detailed progress
```

---

## Contextune-Specific Additions

### Natural Language Triggers

Users can trigger this command with:
- `/contextune:parallel:cleanup` (explicit)
- "clean up parallel worktrees"
- "remove completed tasks"
- "clean up parallel work"
- "delete merged branches"

Contextune automatically detects these intents.

### Global Availability

Works in ALL projects after installing Contextune:

```bash
/plugin install slashsense
```

### Related Commands

When suggesting next steps, mention:
- `/contextune:parallel:status` - Check what's left
- `/contextune:parallel:execute` - Start new parallel work
- `/contextune:parallel:plan` - Plan next iteration

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
User: "/contextune:parallel:cleanup"

You: [Execute cleanup workflow]
```

**With Options:**
```
User: "/contextune:parallel:cleanup --dry-run"

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
- Add Contextune branding where appropriate
- Support both explicit and natural language invocation
- Be conservative - when in doubt, keep rather than delete
