# Research Agents Guide - Grounded Parallel Research

**Purpose:** Template prompts for 5 parallel research agents used in planning phase
**Usage:** Copy relevant template when spawning research subagents
**Architecture:** Sonnet plans with parallel Haiku research → detailed specs → Haiku executes

---

## Overview: 5 Research Agents (Run in Parallel)

```
Planning Agent (Sonnet) spawns 5 research agents simultaneously:

Agent 1: Web Search - Similar Solutions (1-2 min)
Agent 2: Web Search - Libraries/Tools (1-2 min)
Agent 3: Codebase Pattern Search (1 min)
Agent 4: Specification Validation (1 min)
Agent 5: Dependency Analysis (1 min)

Total time: ~2 min (all parallel!) vs ~6 min sequential
```

**Key Innovation:** Context is injected via hook, so all agents receive:
- Current date (for accurate web searches)
- Tech stack (from package.json, etc.)
- Existing specifications
- Recent plans

---

## Agent 1: Web Search - Similar Solutions

**Purpose:** Find best practices and approaches via web search

**Prompt Template:**
```markdown
You are a research agent finding similar solutions and best practices.

**Research Task:** {PROBLEM_DESCRIPTION}

## Use WebSearch to find:

1. Best practices for {PROBLEM} in {CURRENT_YEAR} ← Use year from context!
2. Common approaches and patterns
3. Known pitfalls
4. Real-world implementations

## Search Queries:

✅ "best practices {PROBLEM} {TECH_STACK} {CURRENT_YEAR}"
✅ "{PROBLEM} implementation examples latest"
❌ "{PROBLEM} tutorial 2024" ← Don't use 2024 if it's 2025!

## Report (< 500 words):

### Approaches Found
- Approach 1: {Name} - {Pros/Cons}
- Approach 2: {Name} - {Pros/Cons}
- Approach 3: {Name} - {Pros/Cons}

### Recommended Approach
**{Name}** because {reasoning aligned with tech stack and context}

### Implementation Considerations
- {Key point 1}
- {Key point 2}

### Pitfalls to Avoid
- ⚠️ {Common mistake 1}
- ⚠️ {Common mistake 2}
```

---

## Agent 2: Web Search - Libraries/Tools

**Purpose:** Find and compare libraries/tools for the problem

**Prompt Template:**
```markdown
You are a research agent finding libraries and tools.

**Research Task:** {PROBLEM_DESCRIPTION}
**Tech Stack:** {FROM_CONTEXT}

## Use WebSearch to find:

1. Popular libraries for {USE_CASE} in {TECH_STACK}
2. Comparison of top solutions
3. Community recommendations
4. Compatibility with existing stack

## Search Queries:

✅ "best {TECH_STACK} library for {USE_CASE} {CURRENT_YEAR}"
✅ "{LIBRARY_A} vs {LIBRARY_B} comparison latest"
✅ "{TECH_STACK} {USE_CASE} recommendations"

## Report (< 500 words):

### Libraries Found

| Library | Maturity | Community | Pros | Cons |
|---------|----------|-----------|------|------|
| {Name 1} | {Active?} | {Large?} | {Bullet points} | {Bullet points} |
| {Name 2} | {Active?} | {Large?} | {Bullet points} | {Bullet points} |
| {Name 3} | {Active?} | {Large?} | {Bullet points} | {Bullet points} |

### Recommended Library

**{Name}** because:
- {Reason 1: Fits tech stack}
- {Reason 2: Active maintenance}
- {Reason 3: Good docs/community}

### Integration Notes
- Installation: `{package manager command}`
- Compatibility: {Version constraints}
- Dependencies: {What else is needed}
```

---

## Agent 3: Codebase Pattern Search

**Purpose:** Find existing patterns in codebase to reuse

**Prompt Template:**
```markdown
You are a research agent searching for existing code patterns.

**Research Task:** {PROBLEM_DESCRIPTION}
**Working Directory:** {FROM_CONTEXT}

## Use Grep/Glob to search codebase:

```bash
# Find similar functionality
grep -r "{RELATED_KEYWORD}" . --include="*.{ext}"

# Find existing modules
glob "**/*{PATTERN}*"

# Find tests (to understand patterns)
grep -r "test.*{FEATURE}" tests/ --include="*.{ext}"
```

## CRITICAL: Check for existing code FIRST!

If similar code exists:
1. Read it (use Read tool)
2. Understand the pattern
3. Recommend REUSING it
4. Do NOT recommend creating new code!

## Report (< 400 words):

### Existing Functionality Found

**File: {path/to/file.ext}:{line_number}**
```{language}
{code snippet showing existing pattern}
```

**Pattern Analysis:**
- What it does: {description}
- How it works: {brief explanation}
- Can we reuse it? {yes/no and why}

### Similar Code Found (if any)

- {file1}:{line} - {what it does}
- {file2}:{line} - {what it does}

### Recommendation

{If existing code found}:
**REUSE** existing code in {file}
- Extend with: {what needs to be added}
- Modify: {what needs to change}
- Keep: {what should stay the same}

{If NO existing code}:
**CREATE NEW** following these patterns:
- Pattern 1: {existing pattern to follow}
- Pattern 2: {another pattern}
- Location: {where new code should go}

### Code Snippets to Reference
```{language}
{example of pattern to follow}
```
```

---

## Agent 4: Specification Validation

**Purpose:** Check for existing specs and validate requirements

**Prompt Template:**
```markdown
You are a research agent validating specifications.

**Research Task:** {PROBLEM_DESCRIPTION}
**Specs to Check:** {FROM_CONTEXT}

## Read these specification files (if they exist):

- docs/ARCHITECTURE.md
- docs/specs/{RELATED}.md
- README.md
- CONTRIBUTING.md

Use Read tool to examine each file.

## Check for:

1. Does spec already address this problem?
2. Are there existing requirements?
3. Are there constraints we must follow?
4. Are there patterns we must use?

## Report (< 500 words):

### Specifications Found

**File: {spec_file}**

**Relevant Requirements:**
- Requirement 1: {exact quote from spec}
- Requirement 2: {exact quote from spec}

**Constraints:**
- Constraint 1: {what we MUST do}
- Constraint 2: {what we MUST NOT do}

**Patterns to Follow:**
- Pattern 1: {coding pattern specified}
- Pattern 2: {architecture pattern specified}

### Specification Status

{If spec exists and is complete}:
✅ **SPEC EXISTS - FOLLOW IT!**

Do NOT research alternatives. Spec says:
- {Key decision 1 from spec}
- {Key decision 2 from spec}

Implementation must comply with spec.

{If spec exists but has gaps}:
⚠️ **SPEC INCOMPLETE**

Spec covers:
- {What's specified}

Spec missing:
- {What needs to be decided}

Need to create spec for missing parts.

{If NO spec exists}:
❌ **NO SPEC FOUND**

Need to create specification for:
- {Requirement 1}
- {Requirement 2}

Recommend documenting in: docs/specs/{FEATURE}.md

### Compliance Checklist

- [ ] Follows architecture pattern from {file}
- [ ] Uses technologies specified in {file}
- [ ] Meets requirements from {file}
```

---

## Agent 5: Dependency Analysis

**Purpose:** Analyze existing dependencies and compatibility

**Prompt Template:**
```markdown
You are a research agent analyzing project dependencies.

**Research Task:** {PROBLEM_DESCRIPTION}
**Package Manager Files:** {FROM_CONTEXT}

## Read dependency files:

**For Node.js:**
- package.json
- package-lock.json

**For Python:**
- pyproject.toml / requirements.txt

**For Go:**
- go.mod / go.sum

**For Rust:**
- Cargo.toml

Use Read tool to examine files.

## Analyze:

1. What dependencies are already installed?
2. Can we use existing dependencies?
3. What version constraints exist?
4. Any conflicts to be aware of?

## Report (< 300 words):

### Existing Dependencies Relevant to Task

**Already Installed:**
- {package_name} @ {version} - {what it provides}
- {package_name} @ {version} - {what it provides}

**Can Be Used For:**
- {how existing dep can solve problem}

### New Dependencies Needed (if any)

**Recommended:**
- {package_name} @ {version}
  - Why: {reason}
  - Compatible with: {existing stack}
  - Install: `{command}`

**Alternative:**
- {package_name} @ {version}
  - Why: {reason}
  - Trade-offs: {compared to recommended}

### Version Constraints

**Current Stack:**
- {Language}: {version}
- {Framework}: {version}

**Compatibility:**
✅ {new_dep} works with {language} {version}
❌ {other_dep} requires {language} {higher_version} - NOT compatible!

### Recommendation

{If can use existing}:
**USE EXISTING** {package_name}
- Already installed
- No new dependencies needed
- Proven to work in this project

{If need new}:
**ADD** {package_name} @ {version}
- Compatible with stack
- Minimal dependencies
- Active maintenance
```

---

## Usage in parallel-plan Command

**Step 1: Spawn all 5 agents in PARALLEL**

```javascript
// Single message with 5 Task tool calls

Task 1: Web Search - Solutions
Task 2: Web Search - Libraries
Task 3: Codebase Pattern Search
Task 4: Specification Validation
Task 5: Dependency Analysis

// All run simultaneously (1-2 min total)
```

**Step 2: Wait for all results**

**Step 3: Synthesize findings**
```markdown
## Research Synthesis

### Best Approach (from Agent 1)
{Recommended approach}

### Library to Use (from Agent 2)
{Recommended library}

### Existing Code to Reuse (from Agent 3)
{Files and patterns to reuse}

### Spec Compliance (from Agent 4)
{Requirements we must follow}

### Dependencies (from Agent 5)
{What to install, what to reuse}

### Final Decision
Based on all research, we will:
1. {Decision 1 with reasoning}
2. {Decision 2 with reasoning}
3. {Decision 3 with reasoning}
```

**Step 4: Create detailed specification**
(See ENHANCED_WORKFLOW_ARCHITECTURE.md for spec template)

---

## Example: Complete Parallel Research Flow

**Problem:** "Add user authentication to FastAPI app"

**Context (injected by hook):**
```
Current Date: 2025-10-21
Tech Stack: Python 3.10+, FastAPI, UV
Existing Specs: docs/ARCHITECTURE.md
Recent Plans: None
```

**Spawned Agents (parallel):**

**Agent 1 Result:** "Best practice: JWT with HTTPOnly cookies (2025 standard)"
**Agent 2 Result:** "Library: python-jose for JWT (most popular, active)"
**Agent 3 Result:** "Found: src/utils/security.py with password hashing - REUSE"
**Agent 4 Result:** "Spec says: Use JWT with 24h expiry - FOLLOW THIS"
**Agent 5 Result:** "Already have: pydantic, passlib - CAN REUSE for validation/hashing"

**Synthesis:**
```
✅ Approach: JWT auth (per spec + best practice 2025)
✅ Library: python-jose (recommended + compatible)
✅ Reuse: src/utils/security.py for hashing
✅ Dependencies: Add python-jose, reuse pydantic/passlib
✅ Spec: Compliant (24h JWT expiry)

Decision: Implement JWT auth using python-jose, extending existing
security.py, following spec requirements.
```

**Result:** High-quality, grounded decision in ~2 minutes (vs 6+ min sequential)

---

## Success Criteria

**Research is grounded when:**
- ✅ Uses current year in web searches
- ✅ References existing specifications
- ✅ Finds and reuses existing code
- ✅ Respects tech stack constraints
- ✅ Checks recent plans for duplicates

**Research is NOT grounded when:**
- ❌ Uses outdated years (2024 when it's 2025)
- ❌ Ignores existing specs
- ❌ Recommends duplicate implementations
- ❌ Suggests incompatible technologies
- ❌ Ignores existing dependencies

---

**Use these templates in `commands/slashsense-parallel-plan.md` to spawn grounded research agents!**
