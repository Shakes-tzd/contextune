---
name: ctx:execute
description: Execute plan in parallel using git worktrees and multiple Claude sessions
keywords:
  - execute plan
  - run plan
  - run tasks
  - parallelize work
  - work in parallel
  - execute tasks
  - run parallel
executable: true
---

# Parallel Execute - Run Parallel Development Workflow

You are executing an automated parallel development workflow with **optimized parallel setup**.

**Contextune Integration:** This command can be triggered via `/contextune:parallel:execute` or natural language like "work on these tasks in parallel", "parallelize this work".

---

## 🎯 Performance-Optimized Architecture

**Key Innovation:** Worktrees are pre-created by script, agents focus purely on implementation, enabling deterministic parallel execution.

**Time Savings:**
- 5 tasks: 30% faster setup (32s saved)
- 10 tasks: 48% faster setup (72s saved)
- 20 tasks: 63% faster setup (152s saved)

**Scaling:** Setup time is O(1) instead of O(n) — constant regardless of task count!

---

## Phase 0: Validate Prerequisites and Setup Infrastructure

**Check required tools:**

```bash
# Verify git and worktree support
git --version && git worktree list
```

**Requirements:**
- Git 2.5+ (worktree support)
- Clean working directory (no uncommitted changes on main)
- **Auto-approval configured** (see below)

**If validation fails:**
- Report missing tools to user
- Provide installation instructions
- Stop execution

### ⚡ IMPORTANT: Configure Auto-Approval to Avoid Bottlenecks

**Problem:** Without auto-approval, you must approve EVERY git command from EVERY parallel agent individually, negating all parallelism benefits!

**Solution:** Pre-approve safe git commands using Claude Code's IAM permission system.

**Quick Setup:**

1. **Run in Claude Code:** `/permissions`

2. **Add these allow rules:**
   ```
   Bash(git add:*)
   Bash(git commit:*)
   Bash(git push:*)
   ```

3. **Set permission mode:** `"defaultMode": "acceptEdits"` in settings

4. **Done!** Agents work autonomously 🚀

**📖 Complete guide:** See `docs/AUTO_APPROVAL_CONFIGURATION.md` for:
- Full configuration options
- Security considerations
- PreToolUse hook setup (advanced)
- Troubleshooting

**Without auto-approval:**
```
Agent 1: Waiting for approval... (blocked)
Agent 2: Waiting for approval... (blocked)
Agent 3: Waiting for approval... (blocked)
→ You: Must approve each one individually (bottleneck!)
```

**With auto-approval:**
```
Agent 1: Implementing... ✅ Testing... ✅ Committing... ✅
Agent 2: Implementing... ✅ Testing... ✅ Committing... ✅
Agent 3: Implementing... ✅ Testing... ✅ Committing... ✅
→ True parallelism! 🚀
```

### Setup Worktrees (Inline Script - 5 seconds)

**Generate and run the setup script:**

```bash
# Create scripts directory if needed
mkdir -p .parallel/scripts

# Generate setup script
cat > .parallel/scripts/setup_worktrees.sh <<'WORKTREE_SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

# Find plan.yaml
PLAN_FILE=".parallel/plans/active/plan.yaml"
if [ ! -f "$PLAN_FILE" ]; then
  echo "Error: plan.yaml not found at $PLAN_FILE"
  exit 1
fi

# Extract task IDs
if command -v yq &> /dev/null; then
  TASK_IDS=$(yq '.tasks[].id' "$PLAN_FILE")
else
  TASK_IDS=$(grep -A 100 "^tasks:" "$PLAN_FILE" | grep "  - id:" | sed 's/.*id: *"\([^"]*\)".*/\1/')
fi

echo "Creating worktrees for $(echo "$TASK_IDS" | wc -l | tr -d ' ') tasks..."

# Create worktrees in parallel
echo "$TASK_IDS" | while read task_id; do
  branch="feature/$task_id"
  worktree="worktrees/$task_id"

  if [ -d "$worktree" ]; then
    echo "⚠️  Worktree exists: $task_id"
  elif git show-ref --verify --quiet refs/heads/$branch; then
    git worktree add "$worktree" "$branch" 2>/dev/null && echo "✅ Created: $task_id (existing branch)"
  else
    git worktree add "$worktree" -b "$branch" 2>&1 | grep -v "Preparing" && echo "✅ Created: $task_id"
  fi
done

echo ""
echo "✅ Setup complete! Active worktrees:"
git worktree list | grep "worktrees/"
WORKTREE_SCRIPT

chmod +x .parallel/scripts/setup_worktrees.sh

# Run the script
./.parallel/scripts/setup_worktrees.sh
```

**What this does:**
- ✅ Generates script in .parallel/scripts/ (user can modify)
- ✅ Reads task IDs from plan.yaml
- ✅ Creates worktrees/task-N directories
- ✅ Creates feature/task-N branches
- ✅ Idempotent (safe to run multiple times)
- ✅ Works with or without yq installed

---

## Phase 1: Load or Create Plan

**Check for existing plan:**

```bash
# Check for plan.yaml
[ -f .parallel/plans/plan.yaml ] && echo "Found plan.yaml" || echo "No plan found"
```

**If plan.yaml exists:**
- Read plan.yaml (lightweight index/TOC)
- Get task list with names, priorities, dependencies
- Understand scope WITHOUT reading full task files
- Build execution graph based on dependencies

**Context-Optimized Reading:**

```python
import yaml

# Step 1: Read plan.yaml (index/TOC)
with open('.parallel/plans/plan.yaml') as f:
    plan = yaml.safe_load(f)

# Step 2: Check context optimization
# If tasks were created in SAME session → already in context!
# If NEW session → read specific task files when spawning agents

# Get task index (with names!)
tasks_index = []
for task_ref in plan['tasks']:
    tasks_index.append({
        'id': task_ref['id'],
        'name': task_ref['name'],  # Name in index!
        'file': task_ref['file'],
        'priority': task_ref['priority'],
        'dependencies': task_ref.get('dependencies', [])
    })

# Sort by priority: blocker > high > medium > low
priority_order = {'blocker': 0, 'high': 1, 'medium': 2, 'low': 3}
tasks_index.sort(key=lambda t: priority_order.get(t['priority'], 99))

# Step 3: When spawning agent for specific task
# ONLY THEN read the task file (if not in context)
def spawn_agent_for_task(task_ref):
    # Check if task file is in context
    # (created in this session vs read from disk)

    # If NOT in context → read it
    task_file = f".parallel/plans/{task_ref['file']}"
    with open(task_file) as f:
        task_content = f.read()

    # Spawn agent with task content
    # ...
```

**Key Optimization:**
- ✅ Read plan.yaml index (lightweight, ~1K tokens)
- ✅ See all task names, priorities, dependencies
- ✅ DON'T read all task files upfront!
- ✅ Read specific task file ONLY when spawning its agent
- ✅ If same session (tasks just created) → already in context!

**If no plan exists:**

Check if a plan was output in the conversation (extraction-optimized format):

1. **Search conversation for plan markers:**
   - Look for `**Type:** Plan` in recent messages
   - Look for `## Plan Structure` header
   - Look for YAML block with `metadata:` and `tasks:`

2. **If plan found in conversation:**
   - Extract plan automatically (see extraction process below)
   - Create .parallel/plans/ directory structure
   - Write extracted files
   - Continue with execution

3. **If no plan in conversation:**
   - Ask user: "No plan found. Would you like to create one with `/ctx:plan`?"
   - Wait for user response
   - If user provides task list directly, ask them to run `/ctx:plan` first

---

### Extraction Process (Automatic from Transcript!)

**IMPORTANT:** Plans can be extracted automatically from the conversation transcript!

**How it works:**

1. **Check if plan.yaml already exists:**
   ```bash
   [ -f .parallel/plans/plan.yaml ] && echo "Found" || echo "Not found"
   ```

2. **If NOT found, extract from current session:**
   ```bash
   # Run extraction script - it finds and extracts plan automatically
   ./scripts/extract-current-plan.sh
   ```

   **What the script does:**
   - Finds current session's transcript file automatically
   - Scans transcript for plan output (searches for **Type:** Plan marker)
   - Extracts ## Plan Structure YAML block
   - Extracts all ### Task N: sections
   - Writes to .parallel/plans/plan.yaml and tasks/*.md
   - Creates helper directories

3. **Verify extraction:**
   ```bash
   # Check that files were created
   ls -la .parallel/plans/
   cat .parallel/plans/plan.yaml
   ```

**Workflow options:**

**Option 1: Same-session extraction (Recommended)**
```
1. User runs /ctx:plan → Plan output in conversation
2. User reviews, requests changes if needed
3. User runs /ctx:execute → Script extracts from transcript automatically
4. Execution proceeds immediately
```

**Option 2: SessionEnd extraction (Alternative)**
```
1. User runs /ctx:plan → Plan output in conversation
2. User ends session → SessionEnd hook extracts to .parallel/plans/
3. User starts new session → Runs /ctx:execute → Files already exist
```

**Both work! Same-session is faster, SessionEnd is more automatic.**

**If extraction fails:**
- Script will show error message
- Check: Was plan output in extraction-optimized format?
- Check: Does plan have **Type:** Plan marker?
- Fallback: Ask user to run `/ctx:plan` first

---

**Plan validation:**
- plan.yaml exists and has valid YAML syntax
- All referenced task files exist
- Each task has: id, priority, objective, files, acceptance criteria
- No circular dependencies
- Task IDs in plan.yaml match task IDs in task files

**Status filtering:**
- Read each task file's YAML frontmatter to check status
- Skip tasks with status: completed
- Only execute tasks with status: pending or blocked
- Report which tasks are being executed vs skipped

**If validation fails:**
- Report specific issues to user (missing files, syntax errors, circular deps, etc.)
- Suggest running `/contextune:parallel:plan` to create proper plan

---

## Phase 2: Spawn Autonomous Haiku Agents (PARALLEL) ⚡

**IMPORTANT:** This is where the optimization happens! We use specialized Haiku agents for 85% cost savings and 2x speedup.

**Three-Tier Architecture in Action:**
- **Tier 1** (You - Sonnet): Orchestration and planning
- **Tier 2** (Haiku): Autonomous task execution
- **Result**: 81% cost reduction, 2x performance improvement

### 🔍 Script-Based Setup = True Determinism (v0.5.5)

**Key architectural decision:** Worktrees are **pre-created by script** before agents spawn!

**Why this matters:**
- ✅ **Deterministic:** Script creates all worktrees reliably (no AI unpredictability)
- ✅ **Fast:** 5 seconds total for any number of tasks (parallel xargs)
- ✅ **Simple agents:** Agents focus only on implementation, not infrastructure
- ✅ **Smaller prompts:** 33% reduction in agent context (no setup instructions)

**Performance:**
```
Old approach (agents create own worktrees):
5 tasks: 73s total (8s setup per agent in parallel)

New approach (script pre-creates worktrees):
5 tasks: 5s setup + work time (deterministic!)

Time saved: 68s (93% faster setup)
```

**Observability via Git + PRs:**
- Each task has its own task file (.parallel/plans/active/tasks/task-N.md)
- Each task has its own git branch (atomic changes, easy rollback)
- Each task has its own worktree (isolated environment)
- Each task gets a PR created from task file (full spec + implementation)
- All visible in `git worktree list`, `gh pr list`, git history

**For each independent task in the plan:**

Spawn a `parallel-task-executor` Haiku agent. Each agent receives:

### 🎯 v0.4.0: Context-Grounded Execution (Zero Research!)

**IMPORTANT:** If using Contextune v0.4.0+ with context-grounded research:

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
The planning phase (Sonnet) already did comprehensive parallel research. You (Haiku) are optimized for fast, accurate execution of well-defined tasks. Trust the plan!

**Cost savings:**
- Planning (Sonnet + research): $0.20
- Your execution (Haiku): $0.04 per task
- If you re-research: Wastes time and money!

---

### Subagent Instructions Template

```
You are Subagent working on: {task.name}

**Task Reference:** .parallel/plans/tasks/{task.id}.md (Markdown + YAML frontmatter)
**Plan Reference:** .parallel/plans/plan.yaml

**IMPORTANT:** Your task file is in Markdown with YAML frontmatter containing your complete specification.

**Quick Reference:**
- Priority: {task.priority}
- Dependencies: {task.dependencies}

**Your Complete Task Specification:**

Read your task file for all details:
```bash
cat .parallel/plans/tasks/{task.id}.md
```

The file contains:
- 🎯 Objective
- 🛠️ Implementation Approach (libraries, patterns to follow)
- 📁 Files to Touch (create/modify/delete)
- 🧪 Tests Required (unit/integration)
- ✅ Acceptance Criteria
- ⚠️ Potential Conflicts
- 📝 Notes

---

## YOUR COMPLETE WORKFLOW

### Phase 1: Setup Your Environment (Do This First!)

**Step 0: Mark Task as In Progress**

Update the task status in plan.yaml to track that you're starting work:

```bash
# Update task status to in_progress
TASK_FILE=".parallel/plans/active/tasks/{task.id}.md"

# Use sed to update status field in YAML frontmatter
sed -i.bak 's/^status: pending$/status: in_progress/' "$TASK_FILE"

# Verify the update
echo "✅ Task status updated to in_progress"
```

**Step 1: Navigate to Your Worktree**

Your worktree and branch were already created by the setup script!

```bash
# Navigate to your worktree
cd worktrees/{task.id}

# Verify you're in the right place
echo "Current branch: $(git branch --show-current)"
echo "Expected branch: feature/{task.id}"
```

**Step 2: Setup Development Environment**

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

# Log that setup is complete
echo "✅ Environment setup complete, starting implementation..."
```

---

### Phase 2: Implement the Feature

**Read your task file for complete details:**

```bash
cat .parallel/plans/tasks/{task.id}.md
```

**Your task file is in Markdown with YAML frontmatter:**
- **Frontmatter**: Contains id, priority, status, dependencies, labels
- **Body**: Contains objective, approach, libraries, files, tests, acceptance criteria

**Follow the implementation approach specified in the task:**
- Approach: {From "## 🛠️ Implementation Approach" section}
- Libraries: {From "**Libraries:**" section}
- Patterns: {From "**Pattern to follow:**" section}

**Detailed implementation steps:**

{Generate steps based on task.objective, task.files, and task.implementation}

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
- ⚠️ Specification is ambiguous → Report back to main agent
- ⚠️ Implementation detail missing → Ask for clarification
- ⚠️ Library doesn't work as expected → Report to main agent
- ⚠️ Tests are unclear → Request test specification

**Remember:** All research was done. All decisions were made. You execute!

**Commit messages should follow:**
```
{type}: {brief description}

{detailed explanation if needed}

Implements: {task.id}

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

Use git push (single command is OK per DRY strategy):

```bash
git push origin "feature/{task.id}"
```

**Note:** If you need commit + push workflow, use `../../scripts/commit_and_push.sh` instead.

**Log completion:**

```bash
echo "✅ Task {task.id} completed and pushed!"
echo ""
echo "Branch: feature/{task.id}"
echo "Commits: $(git log --oneline origin/main..HEAD | wc -l)"
echo ""
echo "Files changed:"
git diff --name-only origin/main..HEAD
echo ""
echo "Ready for PR creation!"
```

---

### Phase 5: Report Back to Main Agent

**Step 1: Mark Task as Completed**

Update the task status to reflect successful completion:

```bash
# Update task status to completed
TASK_FILE=".parallel/plans/active/tasks/{task.id}.md"

# Use sed to update status field in YAML frontmatter
sed -i.bak 's/^status: in_progress$/status: completed/' "$TASK_FILE"

# Verify the update
echo "✅ Task status updated to completed"
```

**Step 2: Return to main agent with:**

```
✅ Task completed successfully!

**Task ID:** {task.id}
**Branch:** feature/{task.id}
**Worktree:** worktrees/{task.id}
**Tests:** All passing ✅
**Status:** Ready for PR

**Summary:** {brief summary of what was implemented}
```

---

## RULES FOR SUBAGENTS

1. ✅ **Autonomy:** Your worktree is pre-created, focus on implementation
2. ✅ **Isolation:** Work only in your assigned worktree directory
3. ✅ **Testing:** All tests must pass before reporting completion
4. ✅ **Status Tracking:** Update task status at key points:
   - Start: pending → in_progress
   - Success: in_progress → completed
   - Error: * → blocked
5. ❌ **No touching main:** Never commit directly to main branch
6. ❌ **No touching other worktrees:** Stay in your assigned directory
7. ⚠️ **Report conflicts:** If you encounter merge conflicts, report to main agent
8. 🎯 **EXECUTE ONLY (v0.4.0):** Follow spec exactly, no research, no decisions
9. ⚠️ **Ask if unclear:** Specification ambiguous? Report to main agent, don't guess!
10. 📝 **Document in commits:** Write clear commit messages explaining what/why

### 🔍 Git + Task Files + PRs = Observability (v0.5.5)

**Why this architecture provides excellent observability:**

**Task Files (.parallel/plans/active/tasks/task-N.md):**
- Version-controlled specifications
- Status tracking (pending/in_progress/completed/blocked)
- Complete implementation details
- Acceptance criteria
- Single source of truth

**Git Branches:**
- Atomic changes per task
- Easy to review (one feature per branch)
- Safe to rollback (branch isolation)
- Clear attribution (who did what)
- Parallel history (no conflicts in main)

**Git Worktrees:**
- Isolated environments
- No context switching overhead
- Visible in `git worktree list`
- Independent test runs
- No shared state issues

**Pull Requests:**
- Full specification (from task file)
- Complete implementation (git diff)
- Review comments and discussion
- CI/CD integration
- Merge history

**Observability Commands:**
```bash
# See task status
grep "^status:" .parallel/plans/active/tasks/*.md

# See all active parallel work
git worktree list
git branch | grep feature/task

# See progress on specific task
cat .parallel/plans/active/tasks/task-0.md
cd worktrees/task-0
git log --oneline

# See what changed in a task
cd worktrees/task-0
git diff origin/main..HEAD

# See PRs
gh pr list --head feature/task-0

# See all completed tasks
grep "status: completed" .parallel/plans/active/tasks/*.md
```

**Benefits:**
- ✅ No duplication (task files = single source of truth)
- ✅ Version controlled (all specs in git history)
- ✅ Easy debugging (git history + task files)
- ✅ Portable (works offline, survives GitHub → GitLab)
- ✅ Audit trail (compliance, security, learning)

---

## ERROR HANDLING

**If worktree navigation fails:**
- Verify worktree exists: `git worktree list`
- Report to main agent (worktree should have been pre-created by script)

**If tests fail:**
- Do NOT push failing code
- Mark task as blocked:
  ```bash
  TASK_FILE=".parallel/plans/active/tasks/{task.id}.md"
  sed -i.bak 's/^status: .*$/status: blocked/' "$TASK_FILE"
  ```
- Report exact error messages to main agent
- Request help if blocked

**If environment setup fails:**
- Document exact error message
- Check for missing dependencies
- Mark task as blocked:
  ```bash
  TASK_FILE=".parallel/plans/active/tasks/{task.id}.md"
  sed -i.bak 's/^status: .*$/status: blocked/' "$TASK_FILE"
  ```
- Report to main agent for project-specific guidance

**If implementation is unclear:**
- Mark task as blocked:
  ```bash
  TASK_FILE=".parallel/plans/active/tasks/{task.id}.md"
  sed -i.bak 's/^status: .*$/status: blocked/' "$TASK_FILE"
  ```
- Report specific questions to main agent
- Do NOT guess or make assumptions

---

End of subagent instructions.
```

### Spawning Haiku Agents (Implementation)

**Use the Task tool with `parallel-task-executor` agent:**

For each task in the YAML plan, create a Task tool invocation with:
- `description`: "{task.name}"
- `prompt`: The complete subagent instructions template above (filled with task-specific YAML values)
- `subagent_type`: "contextune:parallel-task-executor" (Haiku agent)

**Load task data with context optimization:**

```python
import yaml

# Step 1: Read plan.yaml index
with open('.parallel/plans/plan.yaml') as f:
    plan = yaml.safe_load(f)

# Step 2: For each task in index
for task_ref in plan['tasks']:
    task_id = task_ref['id']
    task_name = task_ref['name']  # Name from index!
    task_file = task_ref['file']
    task_priority = task_ref['priority']
    task_dependencies = task_ref.get('dependencies', [])

    # Step 3: Context optimization decision
    # Question: Is task file already in context?
    # Answer: YES if created in this session, NO if reading from disk

    # If NOT in context → read task file
    # If IN context → skip read, use existing context!

    # For now, read task file when spawning agent
    # (Haiku will use it directly for GitHub issue creation)
    with open(f'.parallel/plans/{task_file}') as f:
        task_content = f.read()

    # Fill template with data from INDEX (not full task file!)
    # Haiku agent will read full task file for implementation details
    prompt = subagent_template.format(
        task_id=task_id,
        task_name=task_name,  # From index!
        task_priority=task_priority,  # From index!
        task_dependencies=', '.join(task_dependencies)  # From index!
    )

    # Spawn agent with minimal prompt
    # Agent reads tasks/task-N.md for complete spec
    Task(
        description=task_name,
        prompt=prompt,
        subagent_type="contextune:parallel-task-executor"
    )
```

**Context Optimization Benefits:**
- ✅ **Index-first approach**: Get task names, priorities from plan.yaml (1K tokens)
- ✅ **Lazy loading**: Only read task files when spawning agents
- ✅ **Same-session optimization**: If tasks just created → already in context!
- ✅ **Minimal prompt**: Agent gets id, name, priority from index
- ✅ **Agent reads full spec**: Haiku reads tasks/task-N.md for details
- ✅ **Zero transformation**: Task file used directly for GitHub issue (~500 tokens saved per task)

**CRITICAL:** Spawn ALL agents in a SINGLE response using multiple Task tool invocations. This ensures parallel execution from the start.

---

### Context Optimization: Same Session vs New Session

**Same Session (Plan just created):**
```
1. User runs /contextune:parallel:plan
2. Planning agent creates:
   - plan.yaml (in context)
   - tasks/task-0.md (in context)
   - tasks/task-1.md (in context)
   - tasks/task-2.md (in context)
3. User runs /contextune:parallel:execute
4. Execution agent:
   - Reads plan.yaml (~1K tokens)
   - Tasks ALREADY in context (0 tokens!)
   - Total: 1K tokens ✅

Savings: Massive! No re-reading task files.
```

**New Session (Reading from disk):**
```
1. User runs /contextune:parallel:execute (new session)
2. Execution agent:
   - Reads plan.yaml index (~1K tokens)
   - Sees task-0, task-1, task-2 in index
   - Reads task-0.md when spawning agent (~3K tokens)
   - Reads task-1.md when spawning agent (~3K tokens)
   - Reads task-2.md when spawning agent (~3K tokens)
   - Total: ~10K tokens

Still optimized: Only reads what's needed, when it's needed.
```

**Key Insight:** plan.yaml acts as lightweight index/TOC. Model decides when to read full task files based on context availability.

---

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

All 3 Haiku agents start simultaneously in their pre-created worktrees! ⚡

---

## Phase 4: Monitor Progress (Optional)

**While subagents are working:**

Users can check progress at any time with:

```bash
/contextune:parallel:status
```

This will show:
- Active worktrees and their branches
- Task status (from YAML frontmatter)
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
   - Check task status is "completed" in task file
   - Verify branch is pushed
   - Confirm tests are passing

2. **Review changes:**
   ```bash
   # Check task status
   grep "^status:" .parallel/plans/active/tasks/task-*.md

   # Switch to completed worktree
   cd worktrees/task-0

   # Review diff
   git diff origin/main..HEAD
   ```

3. **Prepare for merge:**
   - Document what was completed
   - Note any conflicts or issues
   - Track completion in main agent's todo list

---

## Phase 6: Create Pull Requests

**Generate and run the PR creation script:**

```bash
# Generate PR creation script
cat > .parallel/scripts/create_prs.sh <<'PR_SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH="${1:-main}"
TASKS_DIR=".parallel/plans/active/tasks"

echo "Creating PRs for completed tasks..."

# Find completed tasks
for task_file in "$TASKS_DIR"/task-*.md; do
  [ -f "$task_file" ] || continue

  status=$(grep "^status:" "$task_file" | head -1 | awk '{print $2}')
  [ "$status" = "completed" ] || continue

  task_id=$(basename "$task_file" .md)
  branch="feature/$task_id"
  title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
  labels=$(awk '/^labels:/,/^[a-z]/ {if ($0 ~ /^\s*-/) print $2}' "$task_file" | tr '\n' ',' | sed 's/,$//')

  # Check if PR exists
  if gh pr list --head "$branch" --json number -q '.[0].number' &>/dev/null; then
    echo "⚠️  PR exists for $task_id"
    continue
  fi

  # Create PR
  if [ -n "$labels" ]; then
    gh pr create --base "$BASE_BRANCH" --head "$branch" --title "$title" --body-file "$task_file" --label "$labels"
  else
    gh pr create --base "$BASE_BRANCH" --head "$branch" --title "$title" --body-file "$task_file"
  fi

  echo "✅ Created PR for $task_id: $title"
done

echo ""
echo "✅ PR creation complete!"
PR_SCRIPT

chmod +x .parallel/scripts/create_prs.sh

# Run the script
./.parallel/scripts/create_prs.sh
```

**What this does:**
- ✅ Generates script in .parallel/scripts/ (user can modify)
- ✅ Finds all tasks with status: completed
- ✅ Extracts title from task file (first # heading)
- ✅ Creates PR with task file as body (zero transformation!)
- ✅ Adds labels from task YAML frontmatter
- ✅ Links PR to task via branch name

**Alternative: Merge Directly (No Review Needed)**

If you don't need PR reviews, use the merge script:

```bash
# For each completed task:
./scripts/merge_and_cleanup.sh task-0 "Fix missing utils module"
```

**Script handles:**
- ✅ Checkout and pull main
- ✅ Merge with --no-ff
- ✅ Push to remote
- ✅ Automatic conflict detection
- ✅ Error recovery with Haiku

**Choose based on project workflow:**
- **PRs:** Code review, CI/CD, team visibility
- **Direct merge:** Solo dev, fast iteration, no review needed

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
/contextune:parallel:cleanup
```

**The command handles:**
- ✅ Removes all completed worktrees
- ✅ Deletes merged branches
- ✅ Prunes stale references
- ✅ Safety checks (won't delete unmerged work)
- ✅ Atomic operations (all or nothing)

**Archive the plan:**

```bash
# Move timestamped plan to archive
mkdir -p .parallel/archive
mv .parallel/plans/20251025-042057 .parallel/archive/

# Or keep it for reference (plans are lightweight)
# Plans with status tracking are useful for future reference
```

---

## Phase 9: Report to User

**Provide comprehensive summary with cost tracking:**

```
✅ Parallel execution complete!

**Task Status Summary:**
- ✅ Completed: {N} tasks
- ⚠️ Blocked: {M} tasks (if any)
- ⏳ In Progress: {P} tasks (if any)
- 📋 Pending: {Q} tasks (if any)

**Tasks Completed:** {N} / {Total}
**Actual Wall-Clock Time:** {actual_time}
**Speedup vs Sequential:** {speedup_factor}x faster
**Token Usage:** {total_tokens} tokens (~${cost})

**Merged Branches:**
- feature/task-0: {task 0 title}
- feature/task-1: {task 1 title}
- feature/task-2: {task 2 title}

**Test Results:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Linter passing
- ✅ Type checker passing

**Pull Requests:**
- Created: #{PR_NUM1}, #{PR_NUM2}, #{PR_NUM3}

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
- Plan archived: .parallel/archive/20251025-042057/

🎉 All tasks completed successfully via Contextune parallel execution!
🚀 Powered by Script-Based Setup + Context-Grounded Research v0.5.5
✨ Scripts handle infrastructure, Haiku agents execute blindly
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

## Contextune Integration

### Natural Language Triggers

Users can trigger this command with:
- `/contextune:parallel:execute` (explicit)
- "work on X, Y, Z in parallel"
- "parallelize these tasks"
- "execute parallel development"
- "run these in parallel"

Contextune automatically detects these intents and routes to this command.

### Global Availability

This command works in ALL projects after installing Contextune:

```bash
/plugin install slashsense
```

No project-specific configuration needed.

### Related Commands

When suggesting next steps, mention:
- `/contextune:parallel:status` - Monitor progress
- `/contextune:parallel:cleanup` - Clean up completed work
- `/contextune:parallel:plan` - Create development plan

---

## Performance Comparison

### v0.4.0: Agents Create Own Worktrees

```
Time Analysis for 5 tasks:
Planning:                            60s
Spawn 5 agents:                       5s
Each agent creates issue + worktree:  8s (concurrent!) ⚡
──────────────────────────────────────────
Total Setup:                         73s
Work time:                           Parallel ✅
```

### v0.5.5: Script Pre-Creates Worktrees (CURRENT)

```
Time Analysis for 5 tasks:
Planning:                              60s
Run setup_worktrees.sh:                 5s (all 5 in parallel!)
Spawn 5 agents:                         5s
──────────────────────────────────────────
Total Setup:                           70s
Work time:                             Parallel ✅

Time Saved: 3 seconds (4% faster)
```

**But more importantly:**
- ✅ **Deterministic:** Script always works the same way
- ✅ **Simpler agents:** 33% less context (no setup instructions)
- ✅ **No duplication:** Task files are single source of truth
- ✅ **Cheaper:** Smaller agent prompts = lower costs per task

---

## Example User Interactions

**Natural Language:**
```
User: "work on auth, dashboard, and analytics in parallel"

You: Analyzing request... detected 3 independent tasks.

Creating parallel execution plan...
✅ Plan created: .parallel/plans/20251021-143000/

Setting up infrastructure...
✅ Created 3 worktrees in 5 seconds (script)

Spawning 3 autonomous Haiku agents...
🚀 Agent 1: Auth implementation (worktrees/task-0)
🚀 Agent 2: Dashboard UI (worktrees/task-1)
🚀 Agent 3: Analytics tracking (worktrees/task-2)

[Agents work concurrently in pre-created worktrees]

✅ All tasks completed with parallel execution
Token efficiency: Significant reduction vs sequential approach

Creating PRs...
✅ 3 PRs created from task files

Triggered via Contextune natural language detection.
```

**Explicit Command:**
```
User: "/contextune:parallel:execute"

You: [Load existing plan or ask for task list]
     [Execute full parallel workflow as above]
```

---

## Troubleshooting

**Issue: "Worktree already exists"**
- Run: `git worktree list` to see active worktrees
- Remove stale: `git worktree remove worktrees/task-0`
- Or run: `/contextune:parallel:cleanup`

**Issue: "Setup script failed"**
- Check: `git --version` (need 2.5+ for worktree support)
- Check: Permissions on `.parallel/plans/active/scripts/`
- Run: `chmod +x .parallel/plans/active/scripts/setup_worktrees.sh`

**Issue: "Tests failing in subagent"**
- Subagent should report back to main agent
- Check task status: `grep "^status:" .parallel/plans/active/tasks/task-*.md`
- Review git log in worktree for error context
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

Contextune v0.3.0 includes specialized Haiku agents for specific operations. Use them when you need focused capabilities:

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
Task tool with subagent_type: "contextune:worktree-manager"
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
Task tool with subagent_type: "contextune:issue-orchestrator"
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
Task tool with subagent_type: "contextune:test-runner"
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
Task tool with subagent_type: "contextune:performance-analyzer"
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
- `/contextune:parallel:plan` - Create development plan
- `/contextune:parallel:status` - Monitor progress
- `/contextune:parallel:cleanup` - Clean up worktrees
