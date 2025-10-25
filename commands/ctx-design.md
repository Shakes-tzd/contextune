---
name: ctx:design
description: Design system architecture, APIs, and component interfaces with structured workflow
keywords:
  - design
  - architect
  - architecture
  - system design
  - api design
  - design pattern
  - structure
executable: true
---

# Design Architecture - Structured Design Workflow

Systematic architecture design following: Understand → Research → Specify → Decompose → Plan

This command provides a structured approach to system design, API design, and architectural planning.

## When to Use

Use `/ctx:design` when you need to:
- Design a new system or feature
- Plan API architecture
- Structure component interfaces
- Make build vs buy decisions
- Break down complex architectural problems
- Create implementation plans with dependencies

## Workflow

### 1. Understand the Problem

Extract essentials:
- Core problem (what's the real need?)
- Constraints (time, budget, skills, existing systems)
- Success criteria (what does "done" look like?)
- Assumptions (make implicit explicit)

If unclear, ask:
- "What problem does this solve?"
- "What systems must it integrate with?"
- "Expected scale/volume?"
- "Must-haves vs. nice-to-haves?"

### 2. Research Existing Solutions

Use WebSearch to find:
- Existing tools/libraries: `"best [tech] for [problem] 2025"`
- Implementation patterns: `"[problem] implementation examples"`
- Known challenges: `"[problem] pitfalls"`
- Comparisons: `"[tool A] vs [tool B]"`

Evaluate each solution:
- Maturity (active? community?)
- Fit (solves 80%+?)
- Integration (works with stack?)
- Cost (license, hosting)
- Risk (lock-in, learning curve)

Output: Comparison table with pros/cons

### 3. Develop Specifications

Structure:
```
## Problem Statement
[1-2 sentences]

## Requirements
- [ ] Functional (High/Med/Low priority)
- [ ] Performance (metrics, scale)
- [ ] Security (requirements)

## Constraints
- Technical: [stack, systems]
- Resources: [time, budget, team]

## Success Criteria
- [Measurable outcomes]
```

### 4. Decompose into Tasks

Process:
1. Identify major components
2. Break into 1-3 day tasks
3. Classify: Independent | Sequential | Parallel-ready
4. Map dependencies

For each task:
- Prerequisites (what must exist first?)
- Outputs (what does it produce?)
- Downstream (what depends on it?)
- Parallelizable? (can run with others?)

### 5. Create Execution Plan

Phase structure:
```
## Phase 1: Foundation (Parallel)
- [ ] Task A - Infrastructure
- [ ] Task B - Data models
- [ ] Task C - CI/CD

## Phase 2: Core (Sequential after Phase 1)
- [ ] Task D - Auth (needs A,B)
- [ ] Task E - API (needs B)

## Phase 3: Features (Mixed)
- [ ] Task F - Feature 1 (needs D,E)
- [ ] Task G - Feature 2 (needs D,E) ← Parallel with F
```

## Build vs. Buy Decision

| Factor | Build | Buy |
|--------|-------|-----|
| Uniqueness | Core differentiator | Common problem |
| Fit | Tools don't match | 80%+ match |
| Control | Need full control | Standard OK |
| Timeline | Have time | Need speed |
| Expertise | Team has skills | Steep curve |
| Maintenance | Can maintain | Want support |

## Integration with ctx:architect Skill

This command is enhanced by the `ctx:architect` skill, which provides:
- Proactive detection of design opportunities
- Structured workflow guidance
- Research recommendations
- Specification templates

The skill automatically activates when Contextune detects design-related prompts.

## Examples

**API Design:**
```
/ctx:design Design REST API for user management with auth
```

**System Architecture:**
```
/ctx:design Design microservices architecture for e-commerce platform
```

**Component Planning:**
```
/ctx:design Plan authentication system with OAuth2 and JWT
```

## See Also

- `/ctx:research` - Research libraries and best practices
- `/ctx:plan` - Create parallel development plan
- `ctx:architect` skill - Automated design workflow guidance
