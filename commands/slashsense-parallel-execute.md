---
name: slashsense:parallel:execute
description: Execute plan in parallel using git worktrees and multiple Claude sessions
executable: true
---

# Parallel Execute - Run Parallel Development Workflow

You are executing an automated parallel development workflow with **optimized parallel setup**.

**SlashSense Integration:** This command can be triggered via `/slashsense:parallel:execute` or natural language like "work on these tasks in parallel", "parallelize this work".

---

## 🎯 Performance-Optimized Architecture

**Key Innovation:** Each subagent creates its own GitHub issue and worktree autonomously, enabling true parallel execution from the start.

**Time Savings:**
- 5 tasks: 30% faster setup (32s saved)
- 10 tasks: 48% faster setup (72s saved)
- 20 tasks: 63% faster setup (152s saved)

**Scaling:** Setup time is O(1) instead of O(n) — constant regardless of task count!

---

## Phase 0: Validate Prerequisites

**Check required tools:**

```bash
# Verify git, gh CLI, and worktree support
git --version && gh --version && git worktree list
```

**Requirements:**
- Git 2.5+ (worktree support)
- GitHub CLI (`gh`) authenticated
- Clean working directory (no uncommitted changes)

**If validation fails:**
- Report missing tools to user
- Provide installation instructions
- Stop execution

---

## Phase 1: Load or Create Plan

**Check for existing plan:**

```bash
# Find most recent plan file
ls -t .parallel/plans/PLAN-*.md 2>/dev/null | head -1
```

**If plan exists:**
- Read the plan file
- Extract independent tasks (those marked "Can Run in Parallel")
- Validate task structure (description, files, tests)

**If no plan exists:**
- Ask user: "No plan found. Would you like to create one with `/slashsense:parallel:plan`?"
- Wait for user response
- If user provides task list directly, create minimal inline plan

**Plan validation:**
- At least 1 independent task
- Each task has: description, estimated time, files touched
- No circular dependencies

**If validation fails:**
- Report issues to user
- Suggest running `/slashsense:parallel:plan` to create proper plan

---

## Phase 2: Setup GitHub Labels (One-Time)

**Create reusable GitHub issue labels:**

```bash
# Create labels if they don't exist (idempotent)
gh label create "parallel-execution" --description "Auto-created for parallel development" --color "0366d6" 2>/dev/null || true
gh label create "auto-created" --description "Created by automation" --color "d4c5f9" 2>/dev/null || true
```

**Note:** Failures are non-critical (labels may already exist).

---

## Phase 3: Spawn Autonomous Subagents (PARALLEL) ⚡

**IMPORTANT:** This is where the optimization happens! Each subagent creates its own issue and worktree.

**For each independent task in the plan:**

Spawn a subagent with complete autonomy using the Task tool. Each subagent receives:

### Subagent Instructions Template

```
You are Subagent working on: {task.description}

**Plan Reference:** {plan_file_path}
**Task Details:**
- Estimated Time: {task.estimated_time}
- Files to Touch: {task.files}
- Tests Required: {task.tests}

---

## YOUR COMPLETE WORKFLOW

### Phase 1: Setup Your Environment (Do This First!)

**Step 1: Create Your GitHub Issue**

```bash
gh issue create \
  --title "{task.title}" \
  --body "$(cat <<'EOF'
## Task Description
{task.description}

## Plan Reference
Created from: {plan_file_path}

## Files to Modify
{task.files_list}

## Tests Required
{task.tests_list}

## Success Criteria
{task.success_criteria}

**Worktree:** `worktrees/task-{task_id}`
**Branch:** `feature/{task_id}`
**Labels:** parallel-execution, auto-created

---

🤖 Auto-created via SlashSense parallel execution
EOF
)" \
  --label "parallel-execution,auto-created"
```

**Capture the issue number:**
```bash
ISSUE_URL=$(gh issue create ... above ...)
ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
echo "Created issue #$ISSUE_NUM: $ISSUE_URL"
```

**Step 2: Create Your Worktree**

```bash
git worktree add "worktrees/task-$ISSUE_NUM" -b "feature/task-$ISSUE_NUM"
cd "worktrees/task-$ISSUE_NUM"
```

**Step 3: Setup Development Environment**

```bash
# Copy environment files if they exist
cp ../../.env .env 2>/dev/null || true
cp ../../.env.local .env.local 2>/dev/null || true

# Install dependencies (adjust based on project type)
{project_setup_commands}

# Example for Node.js:
# npm install

# Example for Python:
# uv sync

# Example for Rust:
# cargo build
```

**Verify setup:**
```bash
# Run a quick test to ensure environment works
{project_verify_command}

# Example: npm run typecheck
# Example: uv run pytest --collect-only
```

---

### Phase 2: Implement the Feature

{task.detailed_implementation_steps}

**Guidelines:**
- Follow existing code patterns and conventions
- Write tests as you go (TDD approach)
- Keep commits atomic and descriptive
- Comment your code clearly
- Run linter/formatter before committing

**Commit messages should follow:**
```
{type}: {brief description}

{detailed explanation if needed}

Implements: #{ISSUE_NUM}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

### Phase 3: Test Your Work

**Run all relevant tests:**

```bash
# Unit tests
{unit_test_command}

# Integration tests (if applicable)
{integration_test_command}

# Linting
{lint_command}

# Type checking
{typecheck_command}
```

**All tests MUST pass before pushing!**

If tests fail:
1. Fix the issues
2. Re-run tests
3. Update GitHub issue with status

---

### Phase 4: Push and Report

**Push your branch:**

```bash
git push origin "feature/task-$ISSUE_NUM"
```

**Update GitHub issue with completion status:**

```bash
gh issue comment $ISSUE_NUM --body "$(cat <<'EOF'
✅ **Task Completed**

**Branch:** feature/task-$ISSUE_NUM
**Commits:** $(git log --oneline origin/main..HEAD | wc -l)

**Tests:**
- ✅ Unit tests passing
- ✅ Integration tests passing
- ✅ Linter passing
- ✅ Type checker passing

**Files Changed:**
$(git diff --name-only origin/main..HEAD)

Ready for review and merge!

🤖 Completed via SlashSense parallel execution
EOF
)"
```

**Close the issue:**

```bash
gh issue close $ISSUE_NUM --comment "Task completed successfully!"
```

---

### Phase 5: Report Back to Main Agent

**Return to main agent with:**

```
✅ Task completed successfully!

**Issue:** #{ISSUE_NUM}
**Branch:** feature/task-$ISSUE_NUM
**Worktree:** worktrees/task-$ISSUE_NUM
**Tests:** All passing ✅
**Status:** Ready to merge

**Summary:** {brief summary of what was implemented}
```

---

## RULES FOR SUBAGENTS

1. ✅ **Autonomy:** You create your own issue and worktree
2. ✅ **Isolation:** Work only in your worktree directory
3. ✅ **Testing:** All tests must pass before reporting completion
4. ✅ **Communication:** Update GitHub issue with progress
5. ❌ **No touching main:** Never commit directly to main branch
6. ❌ **No touching other worktrees:** Stay in your assigned directory
7. ⚠️ **Report conflicts:** If you encounter merge conflicts, report in issue

---

## ERROR HANDLING

**If issue creation fails:**
- Retry once
- If still fails, report to main agent with error details
- Include GitHub API response for debugging

**If worktree creation fails:**
- Check if worktree already exists: `git worktree list`
- Try alternative name: `worktrees/task-{task_id}-retry`
- Report to main agent if unresolvable

**If tests fail:**
- Do NOT push failing code
- Document failures in GitHub issue
- Request help from main agent if blocked

**If environment setup fails:**
- Document exact error message
- Check for missing dependencies
- Report to main agent for project-specific guidance

---

End of subagent instructions.
```

### Spawning Subagents (Implementation)

**Use the Task tool to spawn each subagent:**

For each task, create a Task tool invocation with:
- `description`: "{task.title}"
- `prompt`: The complete subagent instructions template above (filled with task-specific values)
- `subagent_type`: "general-purpose"

**CRITICAL:** Spawn ALL subagents in a SINGLE response using multiple Task tool invocations. This ensures parallel execution from the start.

**Example for 3 tasks:**

```
[Single response with 3 Task tool calls]
Task 1: Implement authentication
Task 2: Build dashboard UI
Task 3: Add analytics tracking
```

All 3 subagents start simultaneously, each creating its own issue and worktree in parallel! ⚡

---

## Phase 4: Monitor Progress (Optional)

**While subagents are working:**

Users can check progress at any time with:

```bash
/slashsense:parallel:status
```

This will show:
- Active worktrees and their branches
- GitHub issue statuses
- Test results (if available)
- Estimated completion

**Main agent responsibilities during monitoring:**
- Respond to subagent questions
- Resolve conflicts if subagents report issues
- Coordinate shared resource access if needed

---

## Phase 5: Handle Subagent Completion

**As each subagent completes:**

1. **Verify completion:**
   - Check GitHub issue is closed
   - Verify branch is pushed
   - Confirm tests are passing

2. **Review changes:**
   ```bash
   # Switch to completed worktree
   cd worktrees/task-{ISSUE_NUM}

   # Review diff
   git diff origin/main..HEAD
   ```

3. **Prepare for merge:**
   - Document what was completed
   - Note any conflicts or issues
   - Track completion in main agent's todo list

---

## Phase 6: Merge Completed Work

**Merge strategy options:**

### Option A: Merge Each Branch Individually (Recommended)

```bash
# For each completed task:
git checkout main
git pull origin main
git merge feature/task-{ISSUE_NUM} --no-ff -m "Merge task {ISSUE_NUM}: {task.title}"
git push origin main
```

**Benefits:**
- Clear git history
- Easy to revert individual features
- Can merge as soon as each completes

### Option B: Create Pull Requests

```bash
# For each completed task:
gh pr create \
  --base main \
  --head feature/task-{ISSUE_NUM} \
  --title "{task.title}" \
  --body "Closes #{ISSUE_NUM}"
```

**Benefits:**
- Code review workflow
- CI/CD integration
- Team collaboration

**Choose based on project workflow and team preferences.**

---

## Phase 7: Verify Integration

**After merging all tasks:**

1. **Run full test suite on main:**
   ```bash
   git checkout main
   {full_test_command}
   ```

2. **Check for integration issues:**
   - Do all features work together?
   - Are there any unexpected interactions?
   - Performance regressions?

3. **Fix any integration bugs:**
   - Create new issues for bugs found
   - Fix directly on main (small fixes)
   - Or create hotfix branches (larger fixes)

---

## Phase 8: Cleanup

**Clean up completed worktrees:**

```bash
# Use the cleanup command
/slashsense:parallel:cleanup
```

Or manually:

```bash
# For each completed task:
git worktree remove worktrees/task-{ISSUE_NUM}
git branch -d feature/task-{ISSUE_NUM}

# Prune references
git worktree prune
```

**Archive the plan:**

```bash
# Move plan to archive
mkdir -p .parallel/archive
mv .parallel/plans/PLAN-{timestamp}.md .parallel/archive/
```

---

## Phase 9: Report to User

**Provide comprehensive summary:**

```
✅ Parallel execution complete!

**Tasks Completed:** {N} / {N}
**Total Time:** {actual_time} (estimated: {estimated_time})
**Time Saved:** {sequential_time - parallel_time} ({percentage}%)

**Merged Branches:**
- feature/task-123: {task 1 title}
- feature/task-124: {task 2 title}
- feature/task-125: {task 3 title}

**Test Results:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Linter passing
- ✅ Type checker passing

**GitHub Issues:**
- Closed: #{123}, #{124}, #{125}

**Next Steps:**
- [ ] Review merged code
- [ ] Deploy to staging
- [ ] Update documentation
- [ ] Announce to team

**Cleanup:**
- Worktrees removed: 3
- Branches deleted: 3
- Plan archived: .parallel/archive/PLAN-{timestamp}.md

🎉 All tasks completed successfully via SlashSense parallel execution!
```

---

## SlashSense Integration

### Natural Language Triggers

Users can trigger this command with:
- `/slashsense:parallel:execute` (explicit)
- "work on X, Y, Z in parallel"
- "parallelize these tasks"
- "execute parallel development"
- "run these in parallel"

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

## Performance Comparison

### Before Optimization (Sequential Setup)

```
Time Analysis for 5 tasks:
Planning:                        60s
Create 5 issues (sequential):    15s  ← Bottleneck
Create 5 worktrees (sequential): 25s  ← Bottleneck
Spawn 5 agents:                   5s
─────────────────────────────────────
Total Setup:                    105s
Work time:                      Parallel ✅
```

### After Optimization (Parallel Setup)

```
Time Analysis for 5 tasks:
Planning:                            60s
Spawn 5 agents:                       5s
Each agent creates issue + worktree:  8s (concurrent!) ⚡
──────────────────────────────────────────
Total Setup:                         73s
Work time:                           Parallel ✅

Time Saved: 32 seconds (30% faster)
```

**Scaling benefits:**
- 10 tasks: 72s saved (48% faster)
- 20 tasks: 152s saved (63% faster)

---

## Example User Interactions

**Natural Language:**
```
User: "work on auth, dashboard, and analytics in parallel"

You: Analyzing request... detected 3 independent tasks.

Creating parallel execution plan...
✅ Plan created: .parallel/plans/PLAN-20251021-143000.md

Spawning 3 autonomous subagents...
🚀 Agent 1: Auth implementation
🚀 Agent 2: Dashboard UI
🚀 Agent 3: Analytics tracking

⏳ All agents creating issues and worktrees in parallel...

[Agents work concurrently]

✅ All tasks completed in 2.5 hours (estimated: 6 hours sequential)
Time saved: 3.5 hours (58% faster)

Triggered via SlashSense natural language detection.
```

**Explicit Command:**
```
User: "/slashsense:parallel:execute"

You: [Load existing plan or ask for task list]
     [Execute full parallel workflow as above]
```

---

## Troubleshooting

**Issue: "Worktree already exists"**
- Run: `git worktree list` to see active worktrees
- Remove stale: `git worktree remove worktrees/task-{N}`
- Or run: `/slashsense:parallel:cleanup`

**Issue: "GitHub issue creation failed"**
- Check: `gh auth status`
- Re-authenticate: `gh auth login`
- Verify repo permissions

**Issue: "Tests failing in subagent"**
- Subagent should report in GitHub issue
- Review issue comments for error details
- Main agent provides guidance

**Issue: "Merge conflicts"**
- Expected with shared files
- Subagents should rebase before final push
- Main agent resolves during merge phase

**Issue: "Subagent not responding"**
- Check Claude Code UI for subagent status
- Review subagent's last output
- May need to restart subagent

---

## Implementation Notes

- Uses optimized parallel setup (subagents create own issues/worktrees)
- Fully autonomous subagents reduce coordination overhead
- Setup time is O(1) regardless of task count
- Works identically across all projects (global availability)
- Follows git best practices (feature branches, worktrees, atomic commits)
