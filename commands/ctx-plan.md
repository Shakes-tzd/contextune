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
- ✅ No time/duration estimates (use tokens and priority instead)
- ✅ Priority + dependencies (what actually matters for execution)

**DRY Strategy Note:**
- Plans use **extraction-optimized output format** (visibility + iteration)
- NO Write tool during planning (user sees full plan in conversation)
- `/ctx:execute` extracts plan automatically when needed
- SessionEnd hook as backup (extracts at session end)
- Result: Modular files created automatically, zero manual work

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
- 5x faster (parallel vs sequential execution)
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

All 5 agents will complete quickly when executed in parallel.

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

## Step 3: Output Extraction-Optimized Plan Format

**IMPORTANT:** Do NOT use the Write tool. Output the plan in structured format in the conversation.

The `/ctx:execute` command will extract this automatically to modular files when the user runs it.

Your output will be automatically extracted to:
```
.parallel/plans/
├── plan.yaml           ← From your Plan Structure YAML
├── tasks/
│   ├── task-0.md      ← From your Task 0 section
│   ├── task-1.md      ← From your Task 1 section
│   └── ...
├── templates/
│   └── task-template.md
└── scripts/
    ├── add_task.sh
    └── generate_full.sh
```

---

## Step 4: Output Plan in Extraction-Optimized Format

Output your plan in this structured markdown format. The extraction process will parse this into modular files automatically.

**Format Template:**

```markdown
# Implementation Plan: {Feature Name}

**Type:** Plan
**Status:** Ready
**Created:** {YYYYMMDD-HHMMSS}

---

## Overview

{2-3 sentence description of what this plan accomplishes}

---

## Plan Structure

\`\`\`yaml
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

\`\`\`

---

## Task Details

For each task in your plan, output a task section using this format:

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

**Important:** Output one task section for EACH task in your plan. Repeat the structure above for task-0, task-1, task-2, etc.

**End the plan output with:**

```markdown
---

## References

- [Related documentation]
- [Related code]
```

This completes the extraction-optimized plan format.

---

## Step 5: Validate Your Plan Output

Before finishing, verify your conversation output includes:

1. ✅ **Detection markers:** `**Type:** Plan` header
2. ✅ **Plan Structure section:** With valid YAML block containing:
   - `metadata:` with name, created, status
   - `tasks:` array with id, name, file, priority, dependencies
   - `shared_resources:`, `testing:`, `success_criteria:`
3. ✅ **Task Details sections:** One `### Task N:` section per task
4. ✅ **Task YAML frontmatter:** Each task has valid YAML between \`\`\`yaml blocks
5. ✅ **At least 1 task defined**
6. ✅ **Valid dependencies:** No circular deps, all referenced tasks exist
7. ✅ **Priorities set:** Each task has blocker/high/medium/low
8. ✅ **NO time estimates:** Only tokens, complexity, priority

**Extraction will happen automatically when user runs `/ctx:execute` or at session end.**

If you notice issues in your output, fix them before reporting to user.

---

## Step 6: Report to User

Tell the user:

```
📋 Plan created in extraction-optimized format!

**Plan Summary:**
- {N} total tasks
- {X} can run in parallel
- {Y} have dependencies (sequential)
- Conflict risk: {Low/Medium/High}

**Tasks by Priority:**
- Blocker: {list task IDs}
- High: {list task IDs}
- Medium: {list task IDs}
- Low: {list task IDs}

**What Happens Next:**

The plan above will be automatically extracted to modular files when you:
1. Run `/ctx:execute` - Extracts and executes immediately
2. End this session - SessionEnd hook extracts automatically

**Extraction Output:**
```
.parallel/plans/
├── plan.yaml           (main plan with metadata)
├── tasks/
│   ├── task-0.md      (GitHub-ready task files)
│   ├── task-1.md
│   └── ...
├── templates/
│   └── task-template.md
└── scripts/
    ├── add_task.sh
    └── generate_full.sh
```

**Key Benefits:**
✅ **Full visibility**: You see complete plan in conversation
✅ **Easy iteration**: Ask for changes before extraction
✅ **Zero manual work**: Extraction happens automatically
✅ **Modular files**: Edit individual tasks after extraction
✅ **Perfect DRY**: Plan exists once (conversation), extracted once (files)

**Next Steps:**
1. Review the plan above (scroll up if needed)
2. Request changes: "Change task 2 to use React instead of Vue"
3. When satisfied, run: `/ctx:execute`

Ready to execute? Run `/ctx:execute` to extract and start parallel development.
```

Include a warning if:
- Conflict risk is Medium or High
- More than 5 parallel tasks (may be hard to coordinate)
- Sequential dependencies exist
- Tasks have circular dependencies (validation should catch this!)

---

## Error Handling

**If YAML syntax is invalid in your output:**
- Check your YAML blocks for syntax errors
- Validate with a YAML parser before outputting
- Common issues: Improper indentation, missing quotes, unclosed brackets

**If task dependencies are circular:**
- Detect the cycle (e.g., task-1 → task-2 → task-1)
- Fix the dependencies in your output
- Ensure each task can complete before its dependents start

**If conversation context is insufficient:**
- Ask user for clarification:
  - What features do they want to implement?
  - Which tasks can run independently?
  - Are there any dependencies?
  - What libraries or patterns should be used?

**If extraction fails (reported by `/ctx:execute`):**
- The user will see error messages from the extraction process
- Common fixes:
  - Ensure `**Type:** Plan` header is present
  - Verify YAML blocks are properly formatted
  - Check that task IDs match between plan and task sections

---

## Contextune Integration

This command is available globally through the Contextune plugin. Users can trigger it with:

- **Explicit command:** `/contextune:parallel:plan`
- **Natural language:** "plan parallel development", "create parallel plan"
- **Auto-detection:** Contextune will detect planning intent automatically

When users say things like "plan parallel development for X, Y, Z", Contextune routes to this command automatically.

---

## Notes

- Output plans in extraction-optimized format (NO Write tool)
- Break down vague requests into specific, actionable tasks
- Ask clarifying questions if the scope is unclear
- Prioritize task independence to maximize parallelization
- Document assumptions in each task's notes section
- **NO TIME ESTIMATES** - use priority, dependencies, and tokens instead
- Ensure each task section is self-contained and complete
- The plan YAML should be lightweight (just references and metadata)
- **Extraction happens automatically** when user runs `/ctx:execute` or ends session

**Benefits of Extraction-Based Approach:**
- **Full visibility**: User sees complete plan in conversation
- **Easy iteration**: User can request changes before extraction
- **Perfect DRY**: Plan exists once (conversation), extracted once (files)
- **Zero manual work**: No Write tool calls, extraction is automatic
- **Modular output**: Extracted files are modular and editable
- **GitHub-native**: Tasks in GitHub issue format (zero transformation!)
- **Token efficient**: ~500 tokens saved per task (no parsing overhead)
