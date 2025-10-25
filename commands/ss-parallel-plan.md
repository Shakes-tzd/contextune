---
name: ss:plan
description: Document a development plan for parallel execution
executable: true
---

# Parallel Plan - Create Structured Development Plan

You are executing the parallel planning workflow. Your task is to analyze the conversation history and create a structured plan document for parallel development.

This command is part of the SlashSense plugin and can be triggered via natural language or explicitly with `/slashsense:parallel:plan`.

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

## Step 3: Create Plan Directory

Create the `.parallel/plans/` directory if it doesn't exist:

```bash
mkdir -p .parallel/plans
```

If this fails, report the error to the user and stop.

---

## Step 3: Generate Plan Document

Create a new plan file at `.parallel/plans/PLAN-{timestamp}.md` using the Write tool.

Use the current timestamp in format: `YYYYMMDD-HHMMSS`

Example: `PLAN-20251016-143000.md`

The plan document MUST follow this structure:

```markdown
# Development Plan: {Feature Name}

**Created:** {timestamp}
**Estimated Total Time:** {X hours sequential / Y hours parallel}

---

## 🎯 Overview

{High-level description of what we're building - 2-3 sentences}

---

## ✅ Independent Tasks (Can Run in Parallel)

### Task 1: {Name}
- **Description:** {What needs to be done}
- **Estimated Time:** {X hours}
- **Files Touched:**
  - `path/to/file1.ts`
  - `path/to/file2.ts`
- **Dependencies:** None (independent)
- **Tests Required:** {Test descriptions}

### Task 2: {Name}
- **Description:** {What needs to be done}
- **Estimated Time:** {Y hours}
- **Files Touched:**
  - `path/to/file3.ts`
- **Dependencies:** None (independent)
- **Tests Required:** {Test descriptions}

{Add more tasks as needed}

---

## 🔗 Dependent Tasks (Must Be Sequential)

{Only include this section if there are dependencies}

### Phase 1: {Task Name}
**Must complete before:** Phase 2
**Reason:** {Why dependency exists}

### Phase 2: {Task Name}
**Depends on:** Phase 1
**Reason:** {Why dependency exists}

---

## ⚠️ Shared Resources & Potential Conflicts

### Shared Files
- `config/app.ts` - Multiple tasks may need to import
- `types/index.ts` - Shared type definitions

**Mitigation Strategy:**
- Task 1 creates base types first
- Other tasks rebase before merging

{Include database concerns, API contracts, etc. if relevant}

---

## 🧪 Testing Strategy

**Unit Tests:**
- Each task writes own unit tests
- Must pass before pushing branch

**Integration Tests:**
- Run after merging to main
- Test cross-feature interactions

**Test Isolation:**
- Each worktree runs tests independently
- No shared test state

---

## 📊 Success Criteria

- [ ] All independent tasks complete
- [ ] All tests passing (unit + integration)
- [ ] No merge conflicts
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Performance benchmarks met

---

## 🚀 Execution Order

**Parallel Phase (Estimated {Y hours}):**
1. Spawn subagents for Tasks 1, 2, 3 simultaneously
2. Each agent works in its own git worktree
3. Monitor progress and coordinate completion
4. Merge branches as each completes

**Sequential Phase (if any):**
1. Complete Phase 1
2. Then Phase 2
3. Final integration tests

---

## 📝 Notes

{Any additional context, decisions, or considerations}

---

## 🔄 Changelog

- **{timestamp}:** Plan created
```

**Important instructions:**
- Fill in all placeholders with actual values from the conversation
- Estimate times based on task complexity (simple: 1h, medium: 2-3h, complex: 4-6h)
- Be specific about files that will be touched
- Break down large tasks into smaller, independent tasks when possible
- Aim for 3-5 parallel tasks maximum for optimal efficiency

---

## Step 4: Add .parallel/ to .gitignore

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

## Step 5: Validate the Plan

Before reporting to the user, verify:

1. Plan file was created successfully (use Read tool to confirm)
2. All required sections are present
3. At least 1 independent task is defined
4. Time estimates are reasonable

If validation fails, report the error to the user and ask for guidance.

---

## Step 6: Report to User

Tell the user:

```
📋 Created development plan: .parallel/plans/PLAN-{timestamp}.md

**Summary:**
- {N} tasks can run in parallel
- {M} tasks must run sequentially (if any)
- Estimated time: {X hours sequential / Y hours parallel} ({Z%} faster)
- Conflict risk: {Low/Medium/High}

**Independent Tasks:**
1. {Task 1 name} (~{X}h)
2. {Task 2 name} (~{Y}h)
3. {Task 3 name} (~{Z}h)

Ready to execute? Run `/slashsense:parallel:execute` to start parallel development.
```

Include a warning if:
- Conflict risk is Medium or High
- More than 5 parallel tasks (may be hard to coordinate)
- Sequential dependencies exist

---

## Error Handling

**If directory creation fails:**
- Check permissions
- Report error to user
- Suggest manual creation: `mkdir -p .parallel/plans`

**If Write tool fails:**
- Check if file already exists (read it first)
- Report error to user
- Suggest manual file creation

**If git commit fails:**
- Check if there are uncommitted changes
- Report to user but continue (not critical)

**If conversation context is insufficient:**
- Ask user for clarification:
  - What features do they want to implement?
  - Which tasks can run independently?
  - Are there any dependencies?

---

## SlashSense Integration

This command is available globally through the SlashSense plugin. Users can trigger it with:

- **Explicit command:** `/slashsense:parallel:plan`
- **Natural language:** "plan parallel development", "create parallel plan"
- **Auto-detection:** SlashSense will detect planning intent automatically

When users say things like "plan parallel development for X, Y, Z", SlashSense routes to this command automatically.

---

## Notes

- Always create a plan even if the user's request is brief
- Break down vague requests into specific, actionable tasks
- Ask clarifying questions if the scope is unclear
- Prioritize task independence to maximize parallelization
- Document assumptions in the Notes section
- Keep the plan focused and concise
