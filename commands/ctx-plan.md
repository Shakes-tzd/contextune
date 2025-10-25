---
name: ctx:plan
description: Document a development plan for parallel execution (modular YAML)
keywords:
  - create plan
  - development plan
  - parallel plan
  - plan tasks
  - make plan
  - plan development
  - create development plan
executable: true
---

# Parallel Plan - Create Modular YAML Development Plan

You are executing the parallel planning workflow. Your task is to analyze the conversation history and create a **modular YAML plan** for parallel development.

**Key Innovation:** Each task is a separate YAML file. No more monolithic markdown files!

**Benefits:**
- ✅ 95% fewer tokens for updates (edit one task file vs entire plan)
- ✅ Add/remove tasks without touching existing content
- ✅ Reorder tasks with simple array edits
- ✅ Better version control (smaller, focused diffs)
- ✅ No time estimates (they go stale immediately)
- ✅ Priority + dependencies (what actually matters for execution)

This command is part of the Contextune plugin and can be triggered via natural language or explicitly with `/contextune:parallel:plan`.

---

## Step 1: Analyze Conversation and Requirements

Review the conversation history to identify:
- What features/tasks the user wants to implement
- Which tasks are independent (can run in parallel)
- Which tasks have dependencies (must run sequentially)
- Potential shared resources or conflict zones

Use the following criteria to classify tasks:

**Independent Tasks (Parallel-Safe):**
- Touch different files
- Different modules/features
- No shared state
- Can complete in any order

**Dependent Tasks (Sequential):**
- Task B needs Task A's output
- Database migrations
- Shared file modifications
- Order matters

**Conflict Risks:**
- Same file edits
- Shared configuration
- Database schema changes
- API contract changes

---

## Step 2: Parallel Research (NEW! - Grounded Research)

**IMPORTANT:** Before planning, do comprehensive research using 5 parallel agents!

**Why parallel research?**
- 5x faster (1-2 min vs 6+ min sequential)
- More comprehensive coverage
- Grounded in current reality (uses context from hook)
- Main agent context preserved (research in subagents)

### Research Phase Workflow

**Context Available (injected by hook):**
- Current date (for accurate web searches)
- Tech stack (from package.json, etc.)
- Existing specifications
- Recent plans

**Spawn 5 Research Agents in PARALLEL:**

Use the Task tool to spawn ALL 5 agents in a SINGLE message:

#### Agent 1: Web Search - Similar Solutions

```
Task tool with subagent_type="general-purpose"

Description: "Research similar solutions and best practices"

Prompt: (Use template from docs/RESEARCH_AGENTS_GUIDE.md - Agent 1)

"You are researching similar solutions for {PROBLEM}.

Use WebSearch to find:
- Best practices for {PROBLEM} in {CURRENT_YEAR} ← Use year from context!
- Common approaches and patterns
- Known pitfalls

Search queries:
- 'best practices {PROBLEM} {TECH_STACK} {CURRENT_YEAR}'
- '{PROBLEM} implementation examples latest'

Report back (<500 words):
1. Approaches found (top 3)
2. Recommended approach with reasoning
3. Implementation considerations
4. Pitfalls to avoid"
```

#### Agent 2: Web Search - Libraries/Tools

```
Task tool with subagent_type="general-purpose"

Description: "Research libraries and tools"

Prompt: (Use template from docs/RESEARCH_AGENTS_GUIDE.md - Agent 2)

"You are researching libraries for {USE_CASE} in {TECH_STACK}.

Use WebSearch to find:
- Popular libraries for {USE_CASE}
- Comparison of top solutions
- Community recommendations

Report back (<500 words):
1. Top 3 libraries (comparison table)
2. Recommended library with reasoning
3. Integration notes"
```

#### Agent 3: Codebase Pattern Search

```
Task tool with subagent_type="general-purpose"

Description: "Search codebase for existing patterns"

Prompt: (Use template from docs/RESEARCH_AGENTS_GUIDE.md - Agent 3)

"You are searching codebase for existing patterns for {PROBLEM}.

Use Grep/Glob to search:
- grep -r '{KEYWORD}' . --include='*.{ext}'
- Check for similar functionality

CRITICAL: If similar code exists, recommend REUSING it!

Report back (<400 words):
1. Existing functionality found (with file:line)
2. Patterns to follow
3. Recommendation (REUSE vs CREATE NEW)"
```

#### Agent 4: Specification Validation

```
Task tool with subagent_type="general-purpose"

Description: "Validate against existing specifications"

Prompt: (Use template from docs/RESEARCH_AGENTS_GUIDE.md - Agent 4)

"You are checking specifications for {PROBLEM}.

Read these files (if exist):
- docs/ARCHITECTURE.md
- docs/specs/*.md
- README.md

Check for:
- Existing requirements
- Constraints we must follow
- Patterns to use

Report back (<500 words):
1. Spec status (exists/incomplete/missing)
2. Requirements from specs
3. Compliance checklist"
```

#### Agent 5: Dependency Analysis

```
Task tool with subagent_type="general-purpose"

Description: "Analyze project dependencies"

Prompt: (Use template from docs/RESEARCH_AGENTS_GUIDE.md - Agent 5)

"You are analyzing dependencies for {PROBLEM}.

Read:
- package.json (Node.js)
- pyproject.toml (Python)
- go.mod (Go)
- Cargo.toml (Rust)

Check:
- What's already installed?
- Can we reuse existing deps?
- What new deps needed?

Report back (<300 words):
1. Relevant existing dependencies
2. New dependencies needed (if any)
3. Compatibility analysis"
```

**Spawn ALL 5 in ONE message** (parallel execution!)

### Wait for Research Results

All 5 agents will complete in ~1-2 minutes (parallel).

### Synthesize Research Findings

Once all 5 agents report back:

1. **Read all research reports**
2. **Identify best approach** (from Agent 1)
3. **Select libraries** (from Agent 2)
4. **Plan code reuse** (from Agent 3)
5. **Check spec compliance** (from Agent 4)
6. **Plan dependencies** (from Agent 5)

**Create Research Synthesis:**

```markdown
## Research Synthesis

### Best Approach
{From Agent 1: Recommended approach and reasoning}

### Libraries/Tools
{From Agent 2: Which libraries to use}

### Existing Code to Reuse
{From Agent 3: Files and patterns to leverage}

### Specification Compliance
{From Agent 4: Requirements we must follow}

### Dependencies
{From Agent 5: What to install, what to reuse}

### Architectural Decisions

Based on research findings:

**Decision 1:** {Architecture decision}
- **Reasoning:** {Why, based on research}
- **Source:** {Which research agent(s)}

**Decision 2:** {Technology decision}
- **Reasoning:** {Why, based on research}
- **Source:** {Which research agent(s)}

**Decision 3:** {Pattern decision}
- **Reasoning:** {Why, based on research}
- **Source:** {Which research agent(s)}
```

This synthesis will be embedded in the plan document and used to create detailed specifications for Haiku agents.

---

## Step 3: Create Plan Directory Structure

Create the modular plan directory structure:

```bash
mkdir -p .parallel/plans/tasks
mkdir -p .parallel/plans/templates
mkdir -p .parallel/plans/scripts
```

If this fails, report the error to the user and stop.

---

## Step 4: Generate Modular YAML Plan

### 4.1 Create plan.yaml

Create the main plan file at `.parallel/plans/plan.yaml` using the Write tool.

Use the current timestamp in format: `YYYYMMDD-HHMMSS`

The `plan.yaml` MUST follow this structure:

```yaml
# Plan metadata (lightweight!)
metadata:
  name: "{Feature Name}"
  created: "{YYYYMMDD-HHMMSS}"
  status: "ready"  # ready | in_progress | completed

# High-level overview
overview: |
  {2-3 sentence description of what we're building}

# Research synthesis from parallel research phase
research:
  approach: "{Best approach from Agent 1}"
  libraries:
    - name: "{Library from Agent 2}"
      reason: "{Why selected}"
  patterns:
    - file: "{file:line from Agent 3}"
      description: "{Pattern to reuse}"
  specifications:
    - requirement: "{Requirement from Agent 4}"
      status: "must_follow"  # must_follow | should_follow | nice_to_have
  dependencies:
    existing:
      - "{Dependency already installed}"
    new:
      - "{New dependency needed}"

# Feature list (just names for reference)
features:
  - "{feature-1}"
  - "{feature-2}"

# Task index (TOC with task names for quick reference)
tasks:
  - id: "task-0"
    name: "{Task Name}"  # Name here for index/TOC!
    file: "tasks/task-0.md"
    priority: "blocker"  # blocker | high | medium | low
    dependencies: []

  - id: "task-1"
    name: "{Task Name}"
    file: "tasks/task-1.md"
    priority: "high"
    dependencies: ["task-0"]  # If depends on task-0

  - id: "task-2"
    name: "{Task Name}"
    file: "tasks/task-2.md"
    priority: "high"
    dependencies: []

  # Add more task references as needed

# Shared resources and conflict zones
shared_resources:
  files:
    - path: "config/app.ts"
      reason: "Multiple tasks may import"
      mitigation: "Task 1 creates base first"

  databases:
    - name: "{database}"
      concern: "{What could conflict}"
      mitigation: "{How to avoid}"

# Testing strategy
testing:
  unit:
    - "Each task writes own tests"
    - "Must pass before push"
  integration:
    - "Run after merging to main"
    - "Test cross-feature interactions"
  isolation:
    - "Each worktree runs independently"
    - "No shared test state"

# Success criteria
success_criteria:
  - "All tasks complete"
  - "All tests passing"
  - "No merge conflicts"
  - "Code reviewed"
  - "Documentation updated"

# Notes and decisions
notes: |
  {Any additional context, decisions, or considerations}

# Changelog
changelog:
  - timestamp: "{YYYYMMDD-HHMMSS}"
    event: "Plan created"
```

**Important instructions:**
- Fill in all placeholders with actual values from the conversation
- **NO TIME ESTIMATES** - they go stale immediately and add no value
- Use priority (blocker/high/medium/low) instead - this determines execution order
- Use dependencies to define execution sequence
- **Add task names to the index** - plan.yaml acts as Table of Contents for the model
- Be specific about files that will be touched
- Break down large tasks into smaller, independent tasks when possible
- Aim for 3-5 parallel tasks maximum for optimal efficiency

**Context Optimization:**
- plan.yaml = lightweight index/TOC (model reads this first)
- Task names in index allow model to understand scope without reading full task files
- If tasks created in same session → already in context, no re-read needed!
- If new session → model reads specific task files only when spawning agents

### 4.2 Create Individual Task Files

For each task identified, create a separate Markdown file: `.parallel/plans/tasks/task-{N}.md`

**IMPORTANT:** Tasks are stored in **GitHub issue format** (Markdown + YAML frontmatter) to eliminate transformation overhead in Haiku agents!

**Task Markdown Structure:**

```markdown
---
id: task-{N}
priority: high  # blocker | high | medium | low
status: pending  # pending | in_progress | completed | blocked
dependencies:
  - task-0  # Must complete before this starts
labels:
  - parallel-execution
  - auto-created
  - priority-{priority}
---

# {Task Name}

## 🎯 Objective

{Clear, specific description of what this task accomplishes}

## 🛠️ Implementation Approach

{Implementation approach from research synthesis}

**Libraries:**
- `{library-1}` - {Why needed}
- `{library-2}` - {Why needed}

**Pattern to follow:**
- **File:** `{file:line to copy from}`
- **Description:** {What pattern to follow}

## 📁 Files to Touch

**Create:**
- `path/to/new/file.ts`

**Modify:**
- `path/to/existing/file.ts`

**Delete:**
- `path/to/deprecated/file.ts`

## 🧪 Tests Required

**Unit:**
- [ ] Test {specific functionality}
- [ ] Test {edge case}

**Integration:**
- [ ] Test {interaction with other components}

## ✅ Acceptance Criteria

- [ ] All unit tests pass
- [ ] {Specific functionality works}
- [ ] No regressions in existing features
- [ ] Code follows project conventions

## ⚠️ Potential Conflicts

**Files:**
- `shared/config.ts` - Task 2 also modifies → Coordinate with Task 2

## 📝 Notes

{Any additional context, gotchas, or decisions}

---

**Worktree:** `worktrees/task-{N}`
**Branch:** `feature/task-{N}`

🤖 Auto-created via Contextune parallel execution
```

**Why Markdown instead of YAML?**
- ✅ **Zero transformation**: Haiku agents pipe directly to `gh issue create --body-file`
- ✅ **~500 tokens saved per task** (no parsing, no reformatting)
- ✅ **GitHub-native format**: Emoji, checkboxes, formatting work natively
- ✅ **Human-readable**: Preview in any markdown viewer

Create one task file for each task (task-0.md, task-1.md, etc.).

### 4.3 Create Task Template

Create `.parallel/plans/templates/task-template.md` for users to copy when adding tasks:

```markdown
---
id: task-NEW
priority: medium  # blocker | high | medium | low
status: pending   # pending | in_progress | completed | blocked
dependencies: []
labels:
  - parallel-execution
  - auto-created
  - priority-medium
---

# Task Name

## 🎯 Objective

Clear description of what this task accomplishes.

## 🛠️ Implementation Approach

Describe the approach here.

**Libraries:**
- `library-name` - Why needed

**Pattern to follow:**
- **File:** `path/to/file.ts:line`
- **Description:** What pattern to follow

## 📁 Files to Touch

**Create:**
- `path/to/new/file.ts`

**Modify:**
- `path/to/existing/file.ts`

**Delete:**
- (if any)

## 🧪 Tests Required

**Unit:**
- [ ] Test specific functionality
- [ ] Test edge cases

**Integration:**
- [ ] Test integration with other components

## ✅ Acceptance Criteria

- [ ] All unit tests pass
- [ ] Functionality works as specified
- [ ] Code follows project conventions

## ⚠️ Potential Conflicts

**Files:**
- (if any conflicts, list here)

## 📝 Notes

Additional context, gotchas, or decisions.

---

**Worktree:** `worktrees/task-NEW`
**Branch:** `feature/task-NEW`

🤖 Auto-created via Contextune parallel execution
```

### 4.4 Create Helper Scripts

**Script 1: add_task.sh** - Add new task to plan

Create `.parallel/plans/scripts/add_task.sh`:

```bash
#!/bin/bash
# Helper: Add new task to plan

TASK_NUM=$1
TASK_NAME=$2

if [ -z "$TASK_NUM" ] || [ -z "$TASK_NAME" ]; then
  echo "Usage: ./add_task.sh <task-num> <task-name>"
  echo ""
  echo "Example: ./add_task.sh 5 'Implement user authentication'"
  exit 1
fi

# Copy template
cp templates/task-template.md tasks/task-$TASK_NUM.md

# Update task ID and name in file
sed -i '' "s/task-NEW/task-$TASK_NUM/g" tasks/task-$TASK_NUM.md
sed -i '' "s/Task Name/$TASK_NAME/g" tasks/task-$TASK_NUM.md

echo "✅ Created tasks/task-$TASK_NUM.md"
echo ""
echo "📝 Now add reference to plan.yaml:"
echo ""
echo "  - id: \"task-$TASK_NUM\""
echo "    file: \"tasks/task-$TASK_NUM.md\""
echo "    priority: \"medium\"  # Change as needed"
echo ""
echo "Then edit tasks/task-$TASK_NUM.md to fill in details."
echo ""
echo "Finally, run: ./scripts/generate_full.sh"
```

**Script 2: generate_full.sh** - Regenerate PLAN_FULL.md from task files

Create `.parallel/plans/scripts/generate_full.sh`:

```bash
#!/bin/bash
# Helper: Regenerate PLAN_FULL.md from modular task files

PLAN_FILE="plan.yaml"
OUTPUT_FILE="PLAN_FULL.md"

if [ ! -f "$PLAN_FILE" ]; then
  echo "❌ Error: plan.yaml not found"
  exit 1
fi

echo "📝 Generating $OUTPUT_FILE from modular task files..."

# Extract metadata from plan.yaml
PLAN_NAME=$(grep "name:" $PLAN_FILE | head -1 | sed 's/.*name: *"\(.*\)".*/\1/')
CREATED=$(grep "created:" $PLAN_FILE | head -1 | sed 's/.*created: *"\(.*\)".*/\1/')
STATUS=$(grep "status:" $PLAN_FILE | head -1 | sed 's/.*status: *"\(.*\)".*/\1/')

# Start output file
cat > $OUTPUT_FILE <<EOF
# Development Plan: $PLAN_NAME

**Created:** $CREATED
**Status:** $STATUS

---

EOF

# Extract overview
echo "## 📋 Overview" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
grep -A 10 "overview:" $PLAN_FILE | tail -n +2 | sed '/^$/d' | sed 's/^  //' >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "---" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Append each task file
TASK_COUNT=0
for TASK_REF in $(grep "file:" $PLAN_FILE | sed 's/.*file: *"\(.*\)".*/\1/'); do
  TASK_FILE="$TASK_REF"
  if [ -f "$TASK_FILE" ]; then
    echo "  ✅ Adding $TASK_FILE"
    cat "$TASK_FILE" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    echo "---" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    ((TASK_COUNT++))
  else
    echo "  ⚠️  Warning: $TASK_FILE not found"
  fi
done

echo ""
echo "✅ Generated $OUTPUT_FILE with $TASK_COUNT tasks"
echo ""
echo "📖 Read entire plan: cat PLAN_FULL.md"
echo "🔍 Read single task: cat tasks/task-N.md"
```

Make both executable:
```bash
chmod +x .parallel/plans/scripts/add_task.sh
chmod +x .parallel/plans/scripts/generate_full.sh
```

---

## Step 5: Add .parallel/ to .gitignore

Check if `.gitignore` exists and contains `.parallel/`:

```bash
grep -q "^\.parallel/" .gitignore 2>/dev/null
```

If the grep command exits with non-zero status, add `.parallel/` to `.gitignore`:

Use the Edit tool to add to `.gitignore`:
```
.parallel/
```

If `.gitignore` doesn't exist, create it using the Write tool.

Commit the change:
```bash
git add .gitignore
git commit -m "chore: add .parallel/ to gitignore"
```

If the commit fails (e.g., already exists), continue anyway.

---

## Step 5: Generate PLAN_FULL.md (Human Review Only)

After creating all task files, generate the consolidated plan for human review:

```bash
cd .parallel/plans
./scripts/generate_full.sh
```

**IMPORTANT:** `PLAN_FULL.md` is for **human review only**!
- ✅ User runs `cat PLAN_FULL.md` to review the full plan
- ❌ Model NEVER reads this file
- ❌ Model uses `plan.yaml` as index/TOC instead

**Why this matters:**
- If tasks were created in same session → already in model context (don't re-read!)
- If new session → model reads `plan.yaml` index, then specific task files as needed
- PLAN_FULL.md would waste context by re-loading everything unnecessarily

---

## Step 6: Validate the Plan

Before reporting to the user, verify:

1. **plan.yaml exists** (use Read tool to confirm)
2. **All task files exist** (check each tasks/task-N.md)
3. **Valid YAML syntax in plan.yaml** (no parse errors)
4. **Valid YAML frontmatter in each task** (no parse errors)
5. **At least 1 task defined** in plan.yaml
6. **Task references match files** (plan.yaml IDs = actual task file IDs)
7. **Dependencies are valid** (no circular deps, referenced tasks exist)
8. **Priorities are set** (blocker/high/medium/low)
9. **PLAN_FULL.md generated** (should exist)

**Quick validation:**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.parallel/plans/plan.yaml'))"

# Check all task files exist
for task in $(grep "file:" .parallel/plans/plan.yaml | cut -d'"' -f2); do
  [ -f ".parallel/plans/$task" ] || echo "Missing: $task"
done

# Check PLAN_FULL.md exists
[ -f ".parallel/plans/PLAN_FULL.md" ] || echo "Warning: PLAN_FULL.md not generated"
```

If validation fails, report the error to the user and ask for guidance.

---

## Step 7: Report to User

Tell the user:

```
📋 Created modular plan: .parallel/plans/

**Structure:**
- plan.yaml (main plan with metadata)
- tasks/*.md ({N} GitHub-ready task files)
- PLAN_FULL.md (consolidated single-file view)
- templates/task-template.md (for adding tasks)
- scripts/add_task.sh (helper: add tasks)
- scripts/generate_full.sh (helper: regenerate PLAN_FULL.md)

**Task Summary:**
- {N} total tasks
- {X} can run in parallel
- {Y} have dependencies (sequential)
- Conflict risk: {Low/Medium/High}

**Tasks by Priority:**
- Blocker: {list task IDs}
- High: {list task IDs}
- Medium: {list task IDs}
- Low: {list task IDs}

**Key Benefits:**
✅ **Zero transformation**: Tasks in GitHub issue format → Haiku agents pipe directly
✅ **~500 tokens saved per task** (no parsing, no reformatting)
✅ **Single-read option**: PLAN_FULL.md for full overview (no N+1 reads)
✅ **Modular editing**: Add/remove/update tasks without touching others
✅ **95% fewer tokens** for updates (edit one task vs entire plan)
✅ **GitHub-native**: Emoji, checkboxes, formatting work natively

**Next Steps:**
1. Review full plan: `cat .parallel/plans/PLAN_FULL.md`
2. Review individual tasks: `ls .parallel/plans/tasks/`
3. Execute: `/contextune:parallel:execute`

**How to Add Tasks Later:**
```bash
cd .parallel/plans
./scripts/add_task.sh 10 "New Task Name"
# Edit tasks/task-10.md to fill in details
# Add reference to plan.yaml
./scripts/generate_full.sh  # Regenerate PLAN_FULL.md
```

Ready to execute? Run `/contextune:parallel:execute` to start parallel development.
```

Include a warning if:
- Conflict risk is Medium or High
- More than 5 parallel tasks (may be hard to coordinate)
- Sequential dependencies exist
- Tasks have circular dependencies (validation should catch this!)

---

## Error Handling

**If directory creation fails:**
- Check permissions
- Report error to user
- Suggest manual creation: `mkdir -p .parallel/plans/{tasks,templates,scripts}`

**If Write tool fails:**
- Check if file already exists (read it first)
- Report error to user
- Suggest manual file creation

**If YAML syntax is invalid:**
- Report YAML parse error to user
- Show which file has syntax error
- Suggest fixing with YAML validator

**If task dependencies are circular:**
- Report circular dependency chain (e.g., task-1 → task-2 → task-1)
- Suggest breaking the cycle
- Block execution until fixed

**If git commit fails:**
- Check if there are uncommitted changes
- Report to user but continue (not critical)

**If conversation context is insufficient:**
- Ask user for clarification:
  - What features do they want to implement?
  - Which tasks can run independently?
  - Are there any dependencies?

---

## Contextune Integration

This command is available globally through the Contextune plugin. Users can trigger it with:

- **Explicit command:** `/contextune:parallel:plan`
- **Natural language:** "plan parallel development", "create parallel plan"
- **Auto-detection:** Contextune will detect planning intent automatically

When users say things like "plan parallel development for X, Y, Z", Contextune routes to this command automatically.

---

## Notes

- Always create a modular plan even if the user's request is brief
- Break down vague requests into specific, actionable tasks
- Ask clarifying questions if the scope is unclear
- Prioritize task independence to maximize parallelization
- Document assumptions in each task's notes section
- Keep individual task files focused and concise (50-100 lines)
- **NO TIME ESTIMATES** - use priority and dependencies instead
- Each task file should be self-contained and readable on its own
- The plan.yaml should be lightweight (just references and metadata)
- **Always run generate_full.sh after creating/modifying tasks**

**Benefits of Hybrid Markdown Architecture:**
- **Zero transformation**: Tasks already in GitHub issue format (~500 tokens saved per task!)
- **Single-read option**: PLAN_FULL.md for full overview (no N+1 reads)
- **Modular editing**: 95% fewer tokens for updates (edit one task vs entire plan)
- **Better git diffs**: One task file changed vs entire plan
- **GitHub-native**: Emoji, checkboxes, formatting work natively
- **Parallel editing**: Multiple people can edit different tasks
- **Clearer structure**: One file = one concern
