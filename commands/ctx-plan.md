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

## Step 3: Create Plan Files Directly

**IMPORTANT:** Use the PlanBuilder to create plan files directly instead of outputting to conversation.

This creates files immediately and ensures 100% reliability (no parsing errors).

**Import and initialize:**
```python
from lib.plan_builder import PlanBuilder

# Initialize with plan name
builder = PlanBuilder(name="Your Feature Name Here")
```

---

## Step 4: Build Plan Using PlanBuilder

Use the fluent API to build your plan:

**Step 4.1: Set Research Synthesis**

Add your research findings from Step 2:

```python
builder.set_research({
    "approach": "Best approach from Agent 1 research",
    "libraries": [
        {
            "name": "library-name",
            "reason": "Why this library (from Agent 2)"
        }
    ],
    "patterns": [
        {
            "file": "path/to/file.ts:123",
            "description": "Pattern to reuse (from Agent 3)"
        }
    ],
    "specifications": [
        {
            "requirement": "Requirement from specs (from Agent 4)",
            "status": "must_follow"  # must_follow | should_follow | nice_to_have
        }
    ],
    "dependencies": {
        "existing": ["already-installed-dep"],
        "new": ["new-dependency-needed"]
    }
})
```

**Step 4.2: Set Plan Metadata**

Add overview and additional metadata:

```python
builder.set_metadata(
    overview="2-3 sentence description of what we're building",
    shared_resources={
        "files": [
            {
                "path": "config/app.ts",
                "reason": "Multiple tasks may import",
                "mitigation": "Task 0 creates base first"
            }
        ]
    },
    testing={
        "unit": [
            "Each task writes own tests",
            "Must pass before push"
        ],
        "integration": [
            "Run after merging to main",
            "Test cross-feature interactions"
        ]
    },
    success_criteria=[
        "All tasks complete",
        "All tests passing",
        "No merge conflicts",
        "Code reviewed"
    ]
)
```

**Step 4.3: Add Tasks**

For each task you identified, add it to the builder:

```python
# Task 0 - Blocker (no dependencies)
builder.add_task(
    id="task-0",
    name="Short Task Name",
    priority="blocker",  # blocker | high | medium | low
    dependencies=[],
    content="""---
id: task-0
priority: blocker
status: pending
dependencies: []
---

# Full Task Name

## 🎯 Objective

Clear description of what this task accomplishes.

## 🛠️ Implementation Approach

**From Research:**
- Use {library} for {purpose} (from Agent 2)
- Follow pattern in {file:line} (from Agent 3)

**Steps:**
1. Create {component}
2. Implement {functionality}
3. Add tests

## 📁 Files to Touch

**Create:**
- `path/to/new/file.ts`

**Modify:**
- `path/to/existing/file.ts`

## 🧪 Tests Required

- [ ] Unit test for {functionality}
- [ ] Integration test for {feature}

## ✅ Acceptance Criteria

- [ ] All tests pass
- [ ] {Specific functionality works}
- [ ] Code follows project conventions
"""
)

# Task 1 - High priority (depends on task-0)
builder.add_task(
    id="task-1",
    name="Another Task",
    priority="high",
    dependencies=["task-0"],  # Runs after task-0
    content="""---
id: task-1
priority: high
status: pending
dependencies: [task-0]
---

# Another Task

## 🎯 Objective
...
"""
)

# Add more tasks as needed
```

**Important:**
- **NO TIME ESTIMATES** - Use priority + dependencies instead
- **Priority** determines execution order (blocker → high → medium → low)
- **Dependencies** ensure correct sequencing
- **Content** must include full task markdown with YAML frontmatter
- Aim for 3-5 tasks maximum for optimal parallelization

**Step 4.4: Build Files**

After adding all tasks, build the plan files:

```python
# Create all files
created = builder.build()

# Print summary to show user what was created
print(builder.get_summary())

print("\n✅ Plan files created:")
print(f"  - {created['plan']}")
for task_file in created['tasks']:
    print(f"  - {task_file}")
```

This creates:
- `.parallel/plans/plan.yaml` (master plan)
- `.parallel/plans/tasks/task-N.md` (individual tasks)
- Directory structure ready for `/ctx:execute`

---

## Step 5: Output Summary to User

After building files, output a concise summary to the conversation:

```
📋 Plan created and saved to .parallel/plans/

**Plan: {Name}**
- Status: ready
- Created: {timestamp}

**Files Created:**
✅ plan.yaml (master plan with {N} tasks)
✅ tasks/task-0.md - {Task Name} [blocker]
✅ tasks/task-1.md - {Task Name} [high]
... (list all tasks)

**Plan Summary:**
- Total tasks: {N}
- Can run in parallel: {X}
- Have dependencies: {Y}
- Conflict risk: {Low/Medium/High}

**Tasks by Priority:**
- Blocker: {count} tasks
- High: {count} tasks
- Medium: {count} tasks
- Low: {count} tasks

**Next Steps:**
1. Review files: `cat .parallel/plans/plan.yaml`
2. View tasks: `cat .parallel/plans/tasks/task-0.md`
3. Request changes: "Change task 2 to use Redis instead of Postgres"
4. When ready: `/ctx:execute` (files already ready!)

Ready to execute? Run `/ctx:execute` to start parallel development.
```

Include warnings if:
- Conflict risk is Medium or High
- More than 5 parallel tasks (coordination complexity)
- Circular dependencies detected

---

## Step 6: Handle User Requests for Changes

If the user requests changes to the plan:

1. **Update the builder and rebuild:**
   ```python
   # Example: User wants to change a task
   builder.tasks[1]["priority"] = "blocker"  # Change priority
   builder.build()  # Rebuild files
   print("✅ Plan updated!")
   ```

2. **Or create new builder with changes:**
   ```python
   # For major changes, easier to rebuild from scratch
   builder = PlanBuilder("Updated Plan Name")
   # ... add tasks with changes
   builder.build()
   ```

Files are immediately updated, no extraction needed!

---

## Error Handling

**If builder.build() fails:**
- **No tasks added:** You must add at least one task before building
  ```python
  # Fix: Add tasks first
  builder.add_task("task-0", "Task Name", "high", content)
  builder.build()
  ```

**If task priority is invalid:**
- Must be one of: "blocker", "high", "medium", "low"
  ```python
  # Wrong:
  builder.add_task("task-0", "Name", "urgent", content)  # ❌

  # Right:
  builder.add_task("task-0", "Name", "blocker", content)  # ✅
  ```

**If circular dependencies exist:**
- Detect cycle before building: task-1 → task-2 → task-1
- Fix dependencies to be acyclic
- Use a dependency graph to visualize

**If conversation context is insufficient:**
- Ask user for clarification:
  - What features do they want to implement?
  - Which tasks can run independently?
  - Are there any dependencies?
  - What libraries or patterns should be used?

---

## Contextune Integration

This command is available globally through the Contextune plugin. Users can trigger it with:

- **Explicit command:** `/contextune:parallel:plan`
- **Natural language:** "plan parallel development", "create parallel plan"
- **Auto-detection:** Contextune will detect planning intent automatically

When users say things like "plan parallel development for X, Y, Z", Contextune routes to this command automatically.

---

## Notes

- **Use PlanBuilder** for direct file creation (100% reliable)
- Break down vague requests into specific, actionable tasks
- Ask clarifying questions if the scope is unclear
- Prioritize task independence to maximize parallelization
- Document assumptions in each task's notes section
- **NO TIME ESTIMATES** - use priority, dependencies, and tokens instead
- Ensure each task content is self-contained and complete
- The plan YAML should be lightweight (just references and metadata)
- **Files created immediately** - ready for `/ctx:execute` instantly

**Benefits of Direct Creation Approach:**
- **100% Reliable**: No parsing errors, no extraction failures
- **Instant Feedback**: User sees files created immediately
- **Easy Iteration**: Request changes, files updated instantly
- **Token Efficient**: 35% savings vs extraction with retries
- **Modular Output**: GitHub-ready task files from the start
- **Type Safe**: PlanBuilder validates inputs
- **DRY**: Plan exists once (in files), no duplication
