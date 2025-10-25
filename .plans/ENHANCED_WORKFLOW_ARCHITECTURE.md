# Enhanced Workflow Architecture: Research-Driven Planning with Parallel Intelligence

**Created:** 2025-10-21
**Principle:** Sonnet plans EVERYTHING, Haiku executes EXACTLY

---

## 🎯 Core Architecture Principle

### The Division of Labor

```
┌─────────────────────────────────────────────────────────────┐
│ PLANNING PHASE (Sonnet - Main Agent)                       │
├─────────────────────────────────────────────────────────────┤
│ Responsibilities:                                           │
│ • ALL research (codebase, web, specifications)             │
│ • ALL architectural decisions                               │
│ • ALL pattern selection                                     │
│ • ALL task decomposition                                    │
│ • Create DETAILED execution specifications                  │
│                                                              │
│ Output: Complete, no-decisions-needed execution plan        │
└─────────────────────────────────────────────────────────────┘
              │
              │ Detailed Execution Plan
              ▼
┌─────────────────────────────────────────────────────────────┐
│ EXECUTION PHASE (Haiku - Execution Agents)                 │
├─────────────────────────────────────────────────────────────┤
│ Responsibilities:                                           │
│ • Read execution specification                              │
│ • Execute EXACTLY as specified                              │
│ • NO research                                                │
│ • NO decisions                                               │
│ • NO planning                                                │
│                                                              │
│ Output: Implemented code matching specification             │
└─────────────────────────────────────────────────────────────┘
```

**Why this works:**
- **Sonnet** = Expensive, smart → Use for ALL thinking
- **Haiku** = Cheap, fast → Use for ZERO thinking
- **Result** = Optimal cost/quality ratio

---

## 🔬 Planning Phase: Parallel Research Architecture

### Current Problem

```
Planning Agent (Sonnet):
├─ Does research sequentially
├─ Web searches consume main context
├─ Codebase searches in main conversation
└─ Slow, context-heavy process
```

### New Architecture: Parallel Research Subagents

```
Main Planning Agent (Sonnet):
│
├─ Spawn Research Subagents (PARALLEL)
│  │
│  ├─ Research Agent 1: Web Search - Similar Solutions
│  │  └─ Search: "best practices for [problem] 2024"
│  │
│  ├─ Research Agent 2: Web Search - Libraries/Tools
│  │  └─ Search: "[technology] libraries for [use-case]"
│  │
│  ├─ Research Agent 3: Codebase Pattern Search
│  │  └─ Grep/Glob: Find similar implementations
│  │
│  ├─ Research Agent 4: Specification Validation
│  │  └─ Read: docs/specs/, ARCHITECTURE.md, README.md
│  │
│  └─ Research Agent 5: Dependency Analysis
│     └─ Analyze: package.json, requirements.txt, go.mod
│
├─ [Wait for all research agents to complete]
│
├─ Synthesize Research Results
│  ├─ Compare findings
│  ├─ Identify best patterns
│  ├─ Make architecture decisions
│  └─ Document rationale
│
├─ Create Detailed Specifications
│  ├─ Exact files to create/modify
│  ├─ Exact functions with signatures
│  ├─ Exact test cases
│  ├─ Code patterns to follow
│  └─ No ambiguity, no decisions left
│
└─ Output: Execution-Ready Plan
   └─ Haiku agents can execute blindly
```

**Benefits:**
1. **5x faster research** (5 parallel agents vs sequential)
2. **Preserved main context** (research happens in subagents)
3. **Comprehensive coverage** (web + codebase + specs simultaneously)
4. **Better decisions** (more information gathered)

---

## 📋 Detailed Planning Phase Workflow

### Phase 1: Problem Understanding (Main Agent)

**Duration:** 2-5 minutes

```markdown
1. Extract core problem from conversation
2. Identify constraints (time, budget, stack)
3. Clarify success criteria
4. Ask user questions if unclear

Output: Clear problem statement
```

### Phase 2: Parallel Research (5 Subagents)

**Duration:** 1-2 minutes (parallel)

**Spawn 5 research subagents simultaneously:**

#### Research Agent 1: Web Search - Similar Solutions

```
Task tool with subagent_type="general-purpose"

Prompt:
"Research similar solutions for [problem].

Use WebSearch to find:
1. Best practices for [problem] in 2024
2. Common approaches and patterns
3. Known pitfalls and gotchas
4. Real-world implementations

Search queries:
- 'best practices [problem] [technology] 2024'
- '[problem] implementation examples'
- '[problem] common mistakes'

Report back:
- 3-5 approaches found
- Pros/cons of each
- Recommended approach with reasoning
- Links to examples

Keep report concise (< 500 words)"
```

#### Research Agent 2: Web Search - Libraries/Tools

```
Task tool with subagent_type="general-purpose"

Prompt:
"Research libraries and tools for [problem].

Use WebSearch to find:
1. Popular libraries for [use-case]
2. Comparison of top solutions
3. Community consensus/recommendations
4. Compatibility with [existing stack]

Search queries:
- 'best [technology] library for [use-case] 2024'
- '[library A] vs [library B] comparison'
- '[technology] [use-case] recommendations'

Report back:
- Top 3 libraries/tools
- Comparison table (features, maturity, community)
- Recommendation with reasoning
- Integration considerations

Keep report concise (< 500 words)"
```

#### Research Agent 3: Codebase Pattern Search

```
Task tool with subagent_type="general-purpose"

Prompt:
"Search codebase for similar patterns to [problem].

Use Grep/Glob to find:
1. Similar feature implementations
2. Code patterns we already use
3. Shared utilities we can reuse
4. Tests we can use as reference

Search patterns:
- grep -r '[related_keyword]' --include='*.{ext}'
- glob '**/*[pattern]*'

Report back:
- Files with similar functionality
- Code patterns found (with file:line references)
- Reusable utilities identified
- Recommended pattern to follow

Include code snippets (max 3 examples)"
```

#### Research Agent 4: Specification Validation

```
Task tool with subagent_type="general-purpose"

Prompt:
"Check for existing specifications related to [problem].

Read these files (if they exist):
- docs/specs/[relevant].md
- docs/ARCHITECTURE.md
- README.md
- CONTRIBUTING.md
- .github/PULL_REQUEST_TEMPLATE.md

Report back:
- Do specs exist for this feature? (yes/no)
- If yes: Summary of requirements, constraints, patterns
- If no: Gaps that need specification
- Coding standards to follow
- Testing requirements

Keep report concise (< 500 words)"
```

#### Research Agent 5: Dependency Analysis

```
Task tool with subagent_type="general-purpose"

Prompt:
"Analyze project dependencies for [problem].

Read package manager files:
- package.json / package-lock.json (Node.js)
- requirements.txt / pyproject.toml (Python)
- go.mod / go.sum (Go)
- Cargo.toml (Rust)

Check:
1. What libraries are already installed?
2. Can we use existing dependencies?
3. What versions are we locked to?
4. Any conflicts to be aware of?

Report back:
- Relevant existing dependencies
- Whether new dependencies are needed
- Version constraints
- Compatibility concerns

Keep report concise (< 300 words)"
```

**All 5 agents run in PARALLEL** → Main agent waits for all results

### Phase 3: Synthesis & Decision Making (Main Agent)

**Duration:** 3-5 minutes

```markdown
1. Read all research agent reports
2. Compare and contrast findings
3. Identify best approach based on:
   - Existing codebase patterns
   - Specifications (if exist)
   - Best practices from web research
   - Available libraries/tools
   - Project constraints

4. Make architectural decisions:
   - Which pattern to use?
   - Which libraries to use?
   - How to structure code?
   - How to handle edge cases?

5. Document decisions with rationale:
   - "Using [pattern] because [reason]"
   - "Chose [library] over [alternative] because [reason]"
   - "Following [spec] requirement for [feature]"

Output: Architecture Decision Record (ADR)
```

### Phase 4: Detailed Specification Creation (Main Agent)

**Duration:** 5-10 minutes

**Create COMPLETE execution specification with ZERO ambiguity:**

```markdown
## Task Specification for Haiku Agent

### Overview
[1-2 sentence description]

### Files to Create/Modify

**Create:**
- `src/features/auth/LoginForm.tsx`
- `src/features/auth/__tests__/LoginForm.test.tsx`

**Modify:**
- `src/App.tsx` (add LoginForm import and route)
- `src/types/User.ts` (add User type)

### Exact Implementation Steps

#### Step 1: Create User Type
File: `src/types/User.ts`

```typescript
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
```

**Why:** Specification requires User type with these exact fields.

#### Step 2: Create LoginForm Component
File: `src/features/auth/LoginForm.tsx`

```typescript
import { useState } from 'react';
import { LoginCredentials } from '@/types/User';

export const LoginForm = () => {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Call login API (already implemented in src/api/auth.ts)
    // Pattern: Following existing form pattern from src/features/signup/SignupForm.tsx
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Use existing Input component from src/components/Input.tsx */}
      {/* Follow pattern from SignupForm */}
    </form>
  );
};
```

**Pattern to follow:** `src/features/signup/SignupForm.tsx` (our existing form pattern)
**Reuse:** `src/components/Input.tsx`, `src/hooks/useAuth.ts`

#### Step 3: Create Tests
File: `src/features/auth/__tests__/LoginForm.test.tsx`

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '../LoginForm';

describe('LoginForm', () => {
  it('renders email and password fields', () => {
    // Test implementation
  });

  it('submits credentials on form submit', () => {
    // Test implementation
  });

  // Follow test patterns from src/features/signup/__tests__/SignupForm.test.tsx
});
```

**Pattern to follow:** `src/features/signup/__tests__/SignupForm.test.tsx`

### Code Patterns to Follow

**Component Structure:**
```typescript
// Pattern from existing codebase:
export const ComponentName = () => {
  // 1. Hooks first
  // 2. State
  // 3. Event handlers
  // 4. Effects
  // 5. Return JSX
};
```

**Error Handling:**
```typescript
// Pattern from src/utils/errorHandler.ts:
try {
  await apiCall();
} catch (error) {
  toast.error(getErrorMessage(error));
  logError(error);
}
```

### Reusable Code (DO NOT DUPLICATE)

**Use these existing utilities:**
- `src/hooks/useAuth.ts` - Authentication logic
- `src/components/Input.tsx` - Form inputs
- `src/utils/validation.ts` - Email/password validation
- `src/api/auth.ts` - Login API call

**DO NOT create new versions!**

### Tests Required

1. **Unit Tests:**
   - LoginForm renders correctly
   - Email validation works
   - Password validation works
   - Form submission calls API

2. **Integration Tests:**
   - Login flow end-to-end
   - Error handling (invalid credentials)
   - Success redirect to dashboard

**Coverage target:** >80% for new code

### Definition of Done

- [ ] All files created/modified as specified
- [ ] Code follows patterns from existing codebase
- [ ] No code duplication (reused existing utilities)
- [ ] All tests written and passing
- [ ] Test coverage >80%
- [ ] Linter passing
- [ ] Type checker passing
- [ ] Manual testing completed

### Success Criteria

**Functional:**
- User can enter email and password
- Form validates input
- Successful login redirects to dashboard
- Failed login shows error message

**Technical:**
- Follows existing patterns exactly
- Reuses existing components/utilities
- No new dependencies added
- Time complexity: O(1) for all operations

### If You Encounter Issues

**DO NOT make decisions yourself!**

Instead, report to main agent:
- "Specification unclear: [what's unclear]"
- "Existing pattern doesn't fit: [why]"
- "Found duplicate code: [where]"
- "Test failing: [which test, error message]"

**Wait for guidance before proceeding.**
```

**Key aspects of good specification:**
1. **ZERO ambiguity** - Exact files, exact code
2. **Patterns specified** - Which existing code to follow
3. **Reuse mandated** - Don't duplicate
4. **Tests detailed** - Exact test cases
5. **Success criteria** - How to know it's done

### Phase 5: Task Decomposition & Execution Plan (Main Agent)

**Duration:** 2-3 minutes

```markdown
1. Break specification into atomic tasks
2. Identify dependencies
3. Group into parallel phases
4. Create execution plan

Output: .parallel/plans/PLAN-{timestamp}.md with detailed specs embedded
```

---

## ⚡ Execution Phase: Pure Implementation (Haiku Agents)

### Haiku Agent Responsibilities (SIMPLIFIED)

```markdown
## Your Task (Haiku Agent)

You have been given a COMPLETE specification.

**YOUR ONLY JOB:**
1. Read the specification
2. Execute EXACTLY as specified
3. Do NOT research
4. Do NOT make decisions
5. Do NOT plan
6. Ask main agent if ANYTHING is unclear

### Workflow

1. **Read specification** (provided in task description)
2. **Create GitHub issue** (copy specification into issue body)
3. **Create worktree** (git worktree add worktrees/task-{N})
4. **Execute specification:**
   - Create files EXACTLY as specified
   - Follow patterns EXACTLY as specified
   - Reuse utilities EXACTLY as specified
   - Write tests EXACTLY as specified
5. **Run tests** (must pass 100%)
6. **Push and report**

### Rules

❌ **NEVER:**
- Research anything
- Make architectural decisions
- Choose between alternatives
- Create new patterns
- Deviate from specification

✅ **ALWAYS:**
- Follow specification exactly
- Ask if unclear
- Reuse existing code
- Run all tests
- Report completion

### If Something is Unclear

**STOP and ask main agent:**

```
⚠️ SPECIFICATION UNCLEAR

Task: [task name]
Issue: [what's unclear]
Need: [what you need to proceed]
```

**Main agent will update specification, then you proceed.**

### Success = 100% Spec Compliance

Your task is successful if:
- [ ] Implemented exactly as specified
- [ ] No deviations
- [ ] No decisions made
- [ ] All tests passing
- [ ] No questions left unanswered
```

---

## 📊 Performance Comparison

### Current Approach (Without Parallel Research)

```
Planning Phase (Sonnet):
├─ Research codebase (2 min)
├─ Web search 1 (1 min)
├─ Web search 2 (1 min)
├─ Web search 3 (1 min)
├─ Read specs (1 min)
├─ Make decisions (3 min)
├─ Create plan (5 min)
└─ Total: 14 minutes

Execution Phase (Haiku):
├─ Figure out what to do (5 min) ← Waste!
├─ Research patterns (3 min) ← Waste!
├─ Make decisions (2 min) ← Waste!
├─ Implement (10 min)
└─ Total: 20 minutes per task

TOTAL: 14 + (20 × N tasks)
For 5 tasks: 14 + 100 = 114 minutes
```

### New Approach (With Parallel Research)

```
Planning Phase (Sonnet):
├─ Understand problem (3 min)
├─ Spawn 5 research agents (parallel):
│  ├─ Web search 1 (1 min) ─┐
│  ├─ Web search 2 (1 min) ─┤
│  ├─ Codebase search (1 min) ─┤ ← All parallel!
│  ├─ Spec validation (1 min) ─┤
│  └─ Dependency analysis (1 min) ─┘
├─ Synthesize (3 min)
├─ Create detailed specs (8 min)
├─ Decompose tasks (2 min)
└─ Total: 17 minutes (vs 14, but WAY more thorough)

Execution Phase (Haiku):
├─ Read specification (1 min) ← Simple!
├─ Execute exactly (10 min) ← No thinking!
├─ Test (2 min)
└─ Total: 13 minutes per task (vs 20!)

TOTAL: 17 + (13 × N tasks)
For 5 tasks: 17 + 65 = 82 minutes

IMPROVEMENT: 114 → 82 minutes (28% faster!)
QUALITY: Much higher (better research, zero execution errors)
```

---

## 🎯 Implementation in Commands

### Updated slashsense-parallel-plan Command

```markdown
## Phase 2: Parallel Research (NEW!)

**Spawn 5 research subagents simultaneously:**

```bash
# All in ONE message with 5 Task tool calls
Task 1: Web search - similar solutions
Task 2: Web search - libraries/tools
Task 3: Codebase pattern search
Task 4: Specification validation
Task 5: Dependency analysis
```

**Wait for all results, then synthesize.**

## Phase 3: Synthesis & Specification

**Use research results to create detailed, zero-ambiguity specifications:**

For each task, specify:
- Exact files to create/modify (with full paths)
- Exact code to write (with pattern references)
- Exact utilities to reuse (no duplication!)
- Exact tests to write (with examples)
- Success criteria (measurable)

**Rule:** If a Haiku agent needs to make a decision, the spec is incomplete!

## Phase 4: Create Execution Plan

Embed detailed specifications into plan file.

## Phase 5: Transition to Execute

Save workflow state:
```bash
uv run lib/workflow_transitions.py save "parallel:plan" "$PLAN_FILE"
```

Remind user:
```
✅ Plan complete with detailed specifications!

Next: /slashsense:parallel:execute

The plan includes:
- 5 parallel research results synthesized
- Complete specifications (zero decisions needed)
- Haiku agents will execute blindly
- Estimated cost: $X (vs $Y with Sonnet)
```
```

### Updated slashsense-parallel-execute Command

```markdown
## Phase 3: Spawn Haiku Execution Agents

**For each task, pass COMPLETE specification:**

```
Task tool with subagent_type="slashsense:parallel-task-executor"

Prompt:
"Execute this task EXACTLY as specified.

## COMPLETE SPECIFICATION
{detailed_specification_from_plan}

## YOUR ONLY JOB
1. Read spec above
2. Execute exactly
3. Ask if unclear
4. Do NOT research
5. Do NOT make decisions

If anything is unclear, STOP and ask main agent."
```

**Critical:** Specification should be so detailed that Haiku needs ZERO thinking.
```

---

## ✅ Success Criteria

**Planning Phase:**
- [ ] 5 research subagents spawn in parallel
- [ ] All research completes in <2 min (parallel)
- [ ] Synthesis produces clear architectural decisions
- [ ] Specifications are 100% complete (zero ambiguity)
- [ ] Haiku agents don't need to make ANY decisions

**Execution Phase:**
- [ ] Haiku agents read spec and execute
- [ ] No research by Haiku agents
- [ ] No decisions by Haiku agents
- [ ] 100% spec compliance
- [ ] All tests pass

**Performance:**
- [ ] Planning faster (parallel research)
- [ ] Execution faster (no thinking overhead)
- [ ] Higher quality (better research, zero execution errors)
- [ ] Lower cost (Haiku doesn't waste tokens on thinking)

---

## 📝 Implementation Plan

**Phase 1: Create Research Agent Templates**
1. Create 5 research agent prompt templates
2. Test each independently
3. Validate output format

**Phase 2: Update parallel-plan Command**
4. Add parallel research spawning
5. Add synthesis logic
6. Enhance specification creation
7. Test complete planning flow

**Phase 3: Update parallel-task-executor Agent**
8. Simplify to pure execution (remove decision-making)
9. Add "ask if unclear" safeguards
10. Test with detailed specifications

**Phase 4: Integration Testing**
11. Test plan → execute transition
12. Test with 5 parallel tasks
13. Validate Haiku agents don't research/decide
14. Measure time savings

**Phase 5: Documentation**
15. Update README with new architecture
16. Create "Writing Good Specifications" guide
17. Update migration guide

---

## 💡 Key Insights

**Division of Labor:**
```
Sonnet (Expensive): Use for ALL thinking
├─ Research (parallel subagents)
├─ Architecture
├─ Decisions
└─ Detailed specifications

Haiku (Cheap): Use for ZERO thinking
├─ Read specification
├─ Execute exactly
└─ Report completion
```

**Result:**
- **Better quality** (more research, better decisions)
- **Lower cost** (Haiku doesn't waste tokens thinking)
- **Faster** (parallel research, no execution overhead)
- **Fewer errors** (Haiku can't make wrong decisions)

---

This architecture ensures **Sonnet does ALL the brain work** and **Haiku does ALL the hand work**. Perfect division of labor!
