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

## Phase 3: Spawn Autonomous Haiku Agents (PARALLEL) ⚡

**IMPORTANT:** This is where the optimization happens! We use specialized Haiku agents for 85% cost savings and 2x speedup.

**Three-Tier Architecture in Action:**
- **Tier 1** (You - Sonnet): Orchestration and planning
- **Tier 2** (Haiku): Autonomous task execution
- **Result**: 81% cost reduction, 2x performance improvement

**For each independent task in the plan:**

Spawn a `parallel-task-executor` Haiku agent. Each agent receives:

### 🎯 v0.4.0: Context-Grounded Execution (Zero Research!)

**IMPORTANT:** If using SlashSense v0.4.0+ with context-grounded research:

✅ **All research was ALREADY done during planning!**
- Web searches for best practices (2025, not 2024!)
- Library comparisons and recommendations
- Codebase pattern searches
- Specification validation
- Dependency analysis

✅ **The specifications you receive are COMPLETE and GROUNDED:**
- Based on current date and tech stack
- Follows existing specifications
- Reuses existing code patterns
- Uses compatible dependencies
- Follows proven best practices from 2025

✅ **Your job is EXECUTION ONLY:**
- Read the specification
- Execute EXACTLY as specified
- Do NOT research alternatives
- Do NOT make architectural decisions
- Do NOT search for different libraries
- If ANYTHING is unclear → ASK, don't guess!

**Why this matters:**
The planning phase (Sonnet) already spent 2 minutes doing comprehensive parallel research. You (Haiku) are optimized for fast, accurate execution of well-defined tasks. Trust the plan!

**Cost savings:**
- Planning (Sonnet + research): $0.20
- Your execution (Haiku): $0.04 per task
- If you re-research: Wastes time and money!

---

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

**🎯 EXECUTION-ONLY Guidelines (v0.4.0):**

**DO (Execute as specified):**
- ✅ Follow the specification EXACTLY
- ✅ Use the libraries/tools specified in the plan
- ✅ Implement the patterns specified in the plan
- ✅ Follow existing code patterns and conventions
- ✅ Write tests as specified
- ✅ Keep commits atomic and descriptive
- ✅ Run linter/formatter before committing

**DON'T (No research, no decisions):**
- ❌ Research alternative approaches (already done in planning!)
- ❌ Choose different libraries (planning chose the best one!)
- ❌ Make architectural decisions (planning made them!)
- ❌ Search for "better" patterns (planning found them!)
- ❌ Second-guess the specification

**IF UNCLEAR:**
- ⚠️ Specification is ambiguous → Ask in GitHub issue comments
- ⚠️ Implementation detail missing → Ask for clarification
- ⚠️ Library doesn't work as expected → Report in issue
- ⚠️ Tests are unclear → Request test specification

**Remember:** All research was done. All decisions were made. You execute!

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
8. 🎯 **EXECUTE ONLY (v0.4.0):** Follow spec exactly, no research, no decisions
9. ⚠️ **Ask if unclear:** Specification ambiguous? Ask in issue, don't guess!

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

### Spawning Haiku Agents (Implementation)

**Use the Task tool with `parallel-task-executor` agent:**

For each task, create a Task tool invocation with:
- `description`: "{task.title}"
- `prompt`: The complete subagent instructions template above (filled with task-specific values)
- `subagent_type`: "slashsense:parallel-task-executor" (Haiku agent)

**CRITICAL:** Spawn ALL agents in a SINGLE response using multiple Task tool invocations. This ensures parallel execution from the start.

**Cost Tracking:**
Each Haiku agent costs ~$0.04 per task execution (vs $0.27 Sonnet - **85% savings!**)

For 5 parallel tasks:
- **Old (All Sonnet):** 5 × $0.27 = $1.35
- **New (Haiku Agents):** 5 × $0.04 = $0.20
- **Savings:** $1.15 per workflow (85% reduction!)

**Example for 3 tasks:**

```
[Single response with 3 Task tool calls using parallel-task-executor agent]
Task 1: Implement authentication (Haiku agent - $0.04)
Task 2: Build dashboard UI (Haiku agent - $0.04)
Task 3: Add analytics tracking (Haiku agent - $0.04)
Total cost: $0.12 (vs $0.81 Sonnet - 85% savings!)
```

All 3 Haiku agents start simultaneously, each creating its own issue and worktree in parallel! ⚡

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

**Provide comprehensive summary with cost tracking:**

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

**💰 Cost Savings (Haiku Optimization):**
```
┌─────────────────────────────────────────────────┐
│ Cost Comparison: Sonnet vs Haiku Agents        │
├─────────────────────────────────────────────────┤
│ Scenario 1: All Sonnet Agents                  │
│   Main agent (planning):        $0.054         │
│   {N} execution agents:         ${N × 0.27}    │
│   Total:                        ${total_sonnet}│
├─────────────────────────────────────────────────┤
│ Scenario 2: Haiku Agents (ACTUAL) ✨           │
│   Main agent (planning):        $0.054         │
│   {N} Haiku agents:             ${N × 0.04}    │
│   Total:                        ${total_haiku} │
├─────────────────────────────────────────────────┤
│ 💵 This Workflow Saved:         ${savings}     │
│ 📊 Cost Reduction:              {percentage}%  │
│ ⚡ Speed Improvement:           ~2x faster     │
└─────────────────────────────────────────────────┘

Annual projection (1,200 workflows):
  • Old cost (Sonnet): ${total_sonnet × 1200}
  • New cost (Haiku):  ${total_haiku × 1200}
  • Annual savings:    ${savings × 1200} 💰
```

**Next Steps:**
- [ ] Review merged code
- [ ] Deploy to staging
- [ ] Update documentation
- [ ] Announce to team

**Cleanup:**
- Worktrees removed: {N}
- Branches deleted: {N}
- Plan archived: .parallel/archive/PLAN-{timestamp}.md

🎉 All tasks completed successfully via SlashSense parallel execution!
🚀 Powered by Context-Grounded Parallel Research v0.4.0
✨ Sonnet planned EVERYTHING, Haiku executed BLINDLY
```

**Calculate Cost Savings:**

Use this formula to calculate actual costs:

```python
# Cost per agent (Claude pricing as of Oct 2024)
SONNET_INPUT_COST = 3.00 / 1_000_000   # $3/MTok
SONNET_OUTPUT_COST = 15.00 / 1_000_000  # $15/MTok
HAIKU_INPUT_COST = 0.80 / 1_000_000     # $0.80/MTok
HAIKU_OUTPUT_COST = 4.00 / 1_000_000    # $4/MTok

# Average tokens per agent
MAIN_AGENT_INPUT = 18_000
MAIN_AGENT_OUTPUT = 3_000
EXECUTION_AGENT_INPUT_SONNET = 40_000
EXECUTION_AGENT_OUTPUT_SONNET = 10_000
EXECUTION_AGENT_INPUT_HAIKU = 30_000
EXECUTION_AGENT_OUTPUT_HAIKU = 5_000

# Calculate costs
main_cost = (MAIN_AGENT_INPUT * SONNET_INPUT_COST +
             MAIN_AGENT_OUTPUT * SONNET_OUTPUT_COST)

sonnet_agent_cost = (EXECUTION_AGENT_INPUT_SONNET * SONNET_INPUT_COST +
                     EXECUTION_AGENT_OUTPUT_SONNET * SONNET_OUTPUT_COST)

haiku_agent_cost = (EXECUTION_AGENT_INPUT_HAIKU * HAIKU_INPUT_COST +
                    EXECUTION_AGENT_OUTPUT_HAIKU * HAIKU_OUTPUT_COST)

# Total costs
num_tasks = len(completed_tasks)
total_sonnet = main_cost + (num_tasks * sonnet_agent_cost)
total_haiku = main_cost + (num_tasks * haiku_agent_cost)
savings = total_sonnet - total_haiku
percentage = (savings / total_sonnet) * 100

# Format nicely
print(f"This workflow saved: ${savings:.2f} ({percentage:.0f}% reduction)")
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

- Uses optimized parallel setup (agents create own issues/worktrees)
- Uses Haiku agents for 85% cost savings and 2x speedup
- Fully autonomous agents reduce coordination overhead
- Setup time is O(1) regardless of task count
- Works identically across all projects (global availability)
- Follows git best practices (feature branches, worktrees, atomic commits)

---

## Specialized Haiku Agents

SlashSense v0.3.0 includes specialized Haiku agents for specific operations. Use them when you need focused capabilities:

### 1. parallel-task-executor
**Use for:** Complete feature implementation from start to finish

**Capabilities:**
- Creates GitHub issue and worktree
- Implements features
- Runs tests
- Pushes code and reports

**Cost:** ~$0.04 per task
**When to use:** Default agent for all parallel task execution

### 2. worktree-manager
**Use for:** Git worktree lifecycle management

**Capabilities:**
- Create worktrees with safety checks
- Diagnose worktree issues
- Remove and cleanup worktrees
- Handle lock files
- Bulk operations

**Cost:** ~$0.008 per operation
**When to use:** Troubleshooting worktree issues, bulk cleanup, advanced worktree operations

**Example:**
```bash
# Use directly for troubleshooting
Task tool with subagent_type: "slashsense:worktree-manager"
Prompt: "Diagnose and fix worktree lock files in .git/worktrees/"
```

### 3. issue-orchestrator
**Use for:** GitHub issue management

**Capabilities:**
- Create issues with templates
- Update and comment on issues
- Manage labels
- Link issues to PRs
- Bulk operations

**Cost:** ~$0.01 per operation
**When to use:** Bulk issue creation, issue management automation, complex labeling

**Example:**
```bash
# Use directly for bulk operations
Task tool with subagent_type: "slashsense:issue-orchestrator"
Prompt: "Create 10 issues from this task list and label them appropriately"
```

### 4. test-runner
**Use for:** Autonomous test execution and reporting

**Capabilities:**
- Run unit/integration/E2E tests
- Generate test reports
- Create issues for failures
- Track coverage
- Multi-language support (Python, JS/TS, Rust, Go)

**Cost:** ~$0.02 per test run
**When to use:** Dedicated test execution, failure tracking, CI/CD integration

**Example:**
```bash
# Use directly for test automation
Task tool with subagent_type: "slashsense:test-runner"
Prompt: "Run full test suite and create GitHub issues for any failures"
```

### 5. performance-analyzer
**Use for:** Workflow benchmarking and optimization

**Capabilities:**
- Measure workflow timing
- Identify bottlenecks
- Calculate metrics (Amdahl's Law)
- Generate reports
- Cost analysis

**Cost:** ~$0.015 per analysis
**When to use:** Performance monitoring, optimization analysis, cost tracking

**Example:**
```bash
# Use directly for performance analysis
Task tool with subagent_type: "slashsense:performance-analyzer"
Prompt: "Analyze the last 5 parallel workflows and identify bottlenecks"
```

---

## Cost Optimization Strategy

**Three-Tier Model in Practice:**

**Tier 1 - Skills (Sonnet):**
- Guidance and expertise
- User-facing explanations
- Complex reasoning
- **Cost:** 20% of total workflow

**Tier 2 - Orchestration (Sonnet - You):**
- Planning and coordination
- Breaking down tasks
- Managing agents
- **Cost:** Already included (you're the orchestrator)

**Tier 3 - Execution (Haiku):**
- Implementing features
- Running tests
- Managing infrastructure
- **Cost:** 80% of work, but Haiku = 73% cheaper!

**Result:** 81% overall cost reduction!

**Example Workflow Costs:**

**5 Parallel Tasks (Old - All Sonnet):**
```
Main agent (planning):     $0.054
5 execution agents:        $1.350 (5 × $0.27)
Total:                     $1.404
```

**5 Parallel Tasks (New - Haiku Agents):**
```
Main agent (planning):     $0.054 (Sonnet)
5 Haiku agents:            $0.220 (5 × $0.04)
Total:                     $0.274
Savings:                   $1.13 (81% reduction!)
```

**Annual Savings (1,200 workflows/year):**
```
Old cost:  $1,684/year
New cost:  $328/year
Savings:   $1,356/year (81% reduction!)
```

---

## Performance Comparison: Sonnet vs Haiku

**Response Time:**
- Haiku 4.5: ~1-2 seconds
- Sonnet 4.5: ~3-5 seconds
- **Speedup:** 2x faster

**Context Window:**
- Both: 200K tokens (same capacity)

**Quality for Execution Tasks:**
- Haiku: Excellent (well-defined workflows)
- Sonnet: Excellent (but overkill for execution)
- **Conclusion:** Use right tool for the job!

**When to Use Each:**

**Use Sonnet when:**
- Complex reasoning required
- Ambiguous requirements
- Architectural decisions
- User-facing explanations

**Use Haiku when:**
- Well-defined workflows
- Deterministic operations
- Repetitive tasks
- Infrastructure automation

---

## See Also

**Documentation:**
- `docs/HAIKU_AGENT_ARCHITECTURE.md` - Complete architecture spec
- `docs/AGENT_INTEGRATION_GUIDE.md` - Integration patterns
- `docs/COST_OPTIMIZATION_GUIDE.md` - Cost tracking and ROI

**Agent Specifications:**
- `agents/parallel-task-executor.md` - Default execution agent
- `agents/worktree-manager.md` - Worktree specialist
- `agents/issue-orchestrator.md` - GitHub issue specialist
- `agents/test-runner.md` - Test execution specialist
- `agents/performance-analyzer.md` - Performance analysis specialist

**Related Commands:**
- `/slashsense:parallel:plan` - Create development plan
- `/slashsense:parallel:status` - Monitor progress
- `/slashsense:parallel:cleanup` - Clean up worktrees
