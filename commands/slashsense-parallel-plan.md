---
name: slashsense:parallel:plan
description: Document a development plan for parallel execution
---

# Parallel Plan - Document Development Plan

**Purpose:** Analyze our discussion and create a structured plan document for parallel development.

---

## What This Does

Analyzes our conversation and creates `.parallel/plans/PLAN-{timestamp}.md` with:

1. **Overview** - What we're building
2. **Independent Tasks** - Can run in parallel
3. **Dependent Tasks** - Must run sequentially  
4. **Shared Resources** - Potential conflict zones
5. **Success Criteria** - How to know we're done

---

## Task Analysis Criteria

**✅ Independent Tasks (Parallel-Safe):**
- Touch different files
- Different modules/features
- No shared state
- Can complete in any order

**⚠️ Dependent Tasks (Sequential):**
- Task B needs Task A's output
- Database migrations
- Shared file modifications
- Order matters

**🔴 Conflict Risks:**
- Same file edits
- Shared configuration
- Database schema changes
- API contract changes

---

## Plan Document Structure

```markdown
# Development Plan: {Feature Name}

**Created:** {timestamp}
**Estimated Total Time:** {X hours sequential / Y hours parallel}

---

## 🎯 Overview

{High-level description of what we're building}

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

### Task 3: {Name}
- **Description:** {What needs to be done}
- **Estimated Time:** {Z hours}
- **Files Touched:**
  - `path/to/file4.ts`
- **Dependencies:** None (independent)
- **Tests Required:** {Test descriptions}

---

## 🔗 Dependent Tasks (Must Be Sequential)

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

### Database Concerns
- No schema changes in parallel tasks
- Each task uses separate migrations

### API Contracts
- Define interfaces upfront
- No breaking changes during parallel work

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
1. I automatically spawn subagents for Tasks 1, 2, 3 simultaneously
2. Each agent works in its own git worktree
3. I monitor progress and coordinate completion
4. Merge branches as each completes

**Sequential Phase (if any):**
1. Complete Phase 1
2. Then Phase 2
3. Final integration tests

**Note:** When you run `/parallel:execute`, I spawn all subagents automatically - no manual terminal management required!

---

## 📝 Notes

{Any additional context, decisions, or considerations}

---

## 🔄 Changelog

- **{timestamp}:** Plan created
- **{timestamp}:** Task 2 modified (reason)
- **{timestamp}:** All tasks completed
```

---

## Example Usage

```
You: "Plan parallel development for user auth, dashboard, and analytics"

Me: "📋 Creating development plan...

**Analyzing your requirements...**

✅ Identified 3 independent tasks:
- Authentication system (user login/logout/session)
- Dashboard UI (charts, widgets, layout)
- Analytics tracking (events, metrics)

**Checking for dependencies...**
- All tasks are independent ✅
- No shared file conflicts ✅
- Can run in true parallel ✅

**Creating plan document...**

Created: .parallel/plans/PLAN-20251014-153045.md

**Summary:**
- 3 tasks in parallel
- Estimated: 4.5h sequential → 2h parallel (57% faster)
- 0 blocking dependencies
- Low conflict risk

Ready to execute? Use `/slashsense:parallel:execute`"
```

---

## Global Availability

This command is available in **all projects** after installing the SlashSense plugin:

```bash
/plugin install slashsense
```

You can trigger it with:
- `/slashsense:parallel:plan` (explicit)
- Natural language: "plan parallel development"
- SlashSense will detect your intent automatically

---

## When to Use This

**Before `/slashsense:parallel:execute`:**
- Review plan for feasibility
- Share with team for input
- Adjust task boundaries
- Document decisions

**Standalone:**
- Architecture planning
- Feasibility analysis
- Team coordination
- Sprint planning

---

## Output Location

Plans saved to: `.parallel/plans/PLAN-{timestamp}.md`

**Git Tracking:**
```bash
# Add to git for team visibility
git add .parallel/plans/
git commit -m "docs: add parallel development plan"
```

**Reference in Issues:**
```markdown
**Plan:** `.parallel/plans/PLAN-20251014-153045.md`
```