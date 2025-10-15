---
name: slashsense:parallel:cleanup
description: Clean up completed worktrees and branches
---

# Parallel Cleanup - Remove Completed Worktrees

**Purpose:** Safely remove merged worktrees, delete branches, and clean up GitHub artifacts.

---

## What This Does

1. **Identifies merged branches** (already in main)
2. **Removes worktrees** for completed tasks
3. **Deletes local branches** (optional)
4. **Deletes remote branches** (optional)
5. **Closes GitHub issues** (if not auto-closed)
6. **Archives plan documents** (optional)

---

## Safety Checks

**Before cleaning:**
```bash
# Check what will be deleted
git branch --merged main | grep feature/task

# Verify each branch is merged
git log main..feature/task-123  # Should be empty if merged
```

**⚠️ Never Deletes:**
- Unmerged branches
- Branches with unpushed commits
- Worktrees with uncommitted changes
- Main/develop/master branches

---

## Cleanup Process

### **Phase 1: Identify Merged Branches** 🔍

```bash
# Find all merged feature branches
git branch --merged main | grep 'feature/task-' | while read branch; do
  echo "✅ Merged: $branch"
done

# Find unmerged branches
git branch --no-merged main | grep 'feature/task-' | while read branch; do
  echo "⚠️ Not merged: $branch"
done
```

### **Phase 2: Remove Worktrees** 📁

```bash
# For each merged branch
for dir in worktrees/task-*/; do
  task=$(basename "$dir")
  branch="feature/$task"
  
  # Check if merged
  if git branch --merged main | grep -q "$branch"; then
    echo "Removing worktree: $dir"
    git worktree remove "$dir"
  else
    echo "⚠️ Skipping $dir (not merged)"
  fi
done

# Clean up worktree metadata
git worktree prune
```

### **Phase 3: Delete Branches** 🔀

**Local branches:**
```bash
git branch --merged main | grep 'feature/task-' | while read branch; do
  git branch -d "$branch"
  echo "✅ Deleted local: $branch"
done
```

**Remote branches (optional):**
```bash
git branch -r --merged main | grep 'origin/feature/task-' | while read branch; do
  remote_branch=${branch#origin/}
  git push origin --delete "$remote_branch"
  echo "✅ Deleted remote: $remote_branch"
done
```

### **Phase 4: GitHub Cleanup** 🐙

```bash
# Close completed issues (if still open)
gh issue list --label parallel-execution --state open | while read issue; do
  issue_number=$(echo "$issue" | awk '{print $1}')
  
  # Check if branch is merged
  branch="feature/task-$issue_number"
  if git branch --merged main | grep -q "$branch"; then
    gh issue close "$issue_number" --comment "All changes merged to main"
    echo "✅ Closed issue #$issue_number"
  fi
done
```

### **Phase 5: Cleanup Directory Structure** 📂

```bash
# Remove empty worktrees directory
if [ -d "worktrees" ] && [ -z "$(ls -A worktrees)" ]; then
  rmdir worktrees
  echo "✅ Removed empty worktrees directory"
fi

# Archive completed plans (optional)
if [ -d ".parallel/plans" ]; then
  mkdir -p .parallel/archive/$(date +%Y-%m)
  mv .parallel/plans/PLAN-*.md .parallel/archive/$(date +%Y-%m)/ 2>/dev/null
  echo "📦 Archived plan documents"
fi
```

---

## Cleanup Modes

### **Safe Mode (Default)** ✅
- Only removes merged worktrees
- Keeps local branches (for history)
- Keeps remote branches (for PRs)
- Asks for confirmation

```bash
# Guided cleanup
/parallel:cleanup

# Shows what will be removed
# Asks: "Remove these worktrees? (Y/n)"
```

### **Aggressive Mode** 🚨
- Removes all merged worktrees
- Deletes local branches
- Deletes remote branches
- Closes GitHub issues
- No confirmation

```bash
# Use with caution!
/slashsense:parallel:cleanup --aggressive

# Or manually:
# Asks: "Delete branches too? (y/N)"
```

### **Dry Run Mode** 🔍
- Shows what would be deleted
- Doesn't actually delete anything
- Good for verification

```bash
/slashsense:parallel:cleanup --dry-run

# Output shows planned actions without executing
```

---

## Global Availability

This command is available in **all projects** after installing the SlashSense plugin:

```bash
/plugin install slashsense
```

You can trigger it with:
- `/slashsense:parallel:cleanup` (explicit)
- Natural language: "clean up parallel worktrees", "remove completed tasks"
- SlashSense will detect your intent automatically

---

## Related Commands

- `/slashsense:parallel:plan` - Create development plan
- `/slashsense:parallel:execute` - Execute parallel development
- `/slashsense:parallel:status` - Monitor progress

---

## Interactive Cleanup

```
You: "/slashsense:parallel:cleanup"

Or naturally: "clean up parallel worktrees"

Claude: "🧹 Analyzing worktrees for cleanup...

**Found:**
- 3 worktrees total
- 2 fully merged
- 1 not merged yet

**Merged and ready to clean:**
✅ worktrees/task-123 (feature/task-123)
✅ worktrees/task-125 (feature/task-125)

**Not merged (will keep):**
⚠️ worktrees/task-124 (feature/task-124)
   - 2 commits not in main
   - 1 failing test

**Cleanup plan:**
1. Remove worktrees/task-123
2. Remove worktrees/task-125  
3. Keep worktrees/task-124

Proceed with cleanup? (Y/n)"

You: "y"

Me: "🔄 Cleaning up...

✅ Removed: worktrees/task-123
✅ Deleted local branch: feature/task-123
✅ Closed issue #123

✅ Removed: worktrees/task-125
✅ Deleted local branch: feature/task-125
✅ Closed issue #125

📊 Summary:
- 2 worktrees removed
- 2 branches deleted
- 2 issues closed
- 1 worktree remaining (task-124)

Delete remote branches too? (y/N)"

You: "n"

Me: "✅ Cleanup complete!

**Current state:**
- 1 active worktree (task-124)
- Remote branches preserved
- All merged work cleaned up

Run `/slashsense:parallel:status` to see remaining tasks."
```

---

## Cleanup Checklist

Before running cleanup:

- [ ] All intended merges completed
- [ ] Integration tests passing
- [ ] No pending work in worktrees
- [ ] Team notified (if applicable)
- [ ] Backup/tag created (if major milestone)

---

## Selective Cleanup

**Clean specific task:**
```bash
# Just remove task-123
git worktree remove worktrees/task-123
git branch -d feature/task-123
gh issue close 123
```

**Clean all except one:**
```bash
# Keep task-124, clean others
for dir in worktrees/task-*/; do
  if [[ "$dir" != "worktrees/task-124/" ]]; then
    git worktree remove "$dir"
  fi
done
```

---

## Post-Cleanup Verification

```bash
# Verify worktrees removed
git worktree list

# Verify branches deleted
git branch | grep feature/task

# Verify issues closed
gh issue list --label parallel-execution

# Verify main is clean
git status
```

---

## Cleanup Frequency

**When to cleanup:**
- ✅ After each task merge (individual)
- ✅ End of sprint (batch)
- ✅ Before starting new parallel work
- ✅ When disk space is low

**Don't cleanup:**
- ❌ While tasks in progress
- ❌ Before code review
- ❌ With uncommitted changes
- ❌ Before integration tests

---

## Recovery from Accidental Cleanup

**If worktree deleted but branch exists:**
```bash
# Recreate worktree
git worktree add worktrees/task-123 feature/task-123
```

**If branch deleted but not merged:**
```bash
# Find commit in reflog
git reflog | grep task-123

# Recreate branch
git branch feature/task-123 <commit-hash>
```

**If unsure:**
```bash
# Check reflog for last 30 days
git reflog --since="30 days ago" | grep task
```

---

## Disk Space Management

**Before cleanup:**
```bash
# Check worktrees size
du -sh worktrees/

# Check total repo size
du -sh .git/
```

**After cleanup:**
```bash
# Prune unreachable objects
git gc --prune=now

# Aggressive cleanup
git gc --aggressive
```

**Expected savings:**
- Each worktree: ~project size
- 3 worktrees: ~3x project size freed

---

## Best Practices

1. **Cleanup regularly** - Don't let worktrees accumulate
2. **Verify merges** - Always confirm branches merged before deleting
3. **Keep documentation** - Archive plan documents
4. **Coordinate with team** - Ensure everyone done with branches
5. **Test after cleanup** - Run tests to ensure nothing broke

---

## Troubleshooting

**"Worktree is locked"**
```bash
rm -f .git/worktrees/task-123/locked
git worktree remove worktrees/task-123
```

**"Branch is not fully merged"**
```bash
# Force delete (use with caution!)
git branch -D feature/task-123
```

**"Can't delete remote branch"**
```bash
# Check if protected branch
gh repo view --json branchProtectionRules

# Force delete
git push origin --delete feature/task-123 --force
```

**"Worktree directory still exists"**
```bash
# Manual cleanup
rm -rf worktrees/task-123
git worktree prune
```