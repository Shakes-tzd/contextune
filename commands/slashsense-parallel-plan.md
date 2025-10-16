---
name: slashsense:parallel:plan
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

## Step 2: Create Plan Directory

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
