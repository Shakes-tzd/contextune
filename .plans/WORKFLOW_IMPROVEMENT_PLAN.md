# Workflow Improvement Plan: Software Architecture Integration

**Created:** 2025-10-21
**Goal:** Integrate software-architect skill and fix workflow transition gap

---

## 🎯 Problem Statement

### Issue 1: Workflow Transition Gap

**What happened:**
1. User ran `/slashsense:parallel:plan` → Created plan
2. Plan said "Spawn 5 subagents in parallel"
3. I continued working **sequentially** instead of executing the plan
4. User had to remind me to work in parallel

**Root cause:**
- `/slashsense:parallel:plan` only creates the plan (documentation)
- `/slashsense:parallel:execute` executes the plan
- No automatic transition between plan → execute
- No reminder to execute after planning

### Issue 2: Missing Software Architecture Discipline

**What's missing:**
1. **No research phase** - Don't check for existing solutions/patterns
2. **No specification validation** - Don't check if specs exist
3. **No DRY enforcement** - Might duplicate code
4. **No Skills integration** - Don't remind to use existing Skills
5. **No software engineering principles** - Separation of concerns, time complexity

### Issue 3: Haiku Agents Lack Architecture Knowledge

**Current state:**
- Haiku agents are task executors
- Don't research existing solutions
- Don't validate against specifications
- Don't apply software engineering principles

---

## 🔍 Solution Architecture

### 1. Integrate Software-Architect Skill

**Copy to SlashSense:**
```bash
cp /Users/shakes/.claude/skills/software-architect/SKILL.md \
   skills/software-architect/SKILL.md
```

**Update to include SlashSense-specific guidance:**
- Remind to check for existing implementations in codebase
- Suggest using parallel development for independent tasks
- Reference SlashSense workflows

### 2. Enhance parallel-plan Command

**Add 5-phase workflow from software-architect:**

```markdown
## Phase 0: Understand Problem
- Extract core problem
- Identify constraints
- Clarify success criteria
- Ask questions if unclear

## Phase 1: Research Solutions
- Search codebase for similar patterns (Grep/Glob)
- Check if specs exist (read docs/, specs/, ARCHITECTURE.md)
- Research existing libraries/tools (WebSearch if appropriate)
- Document findings

## Phase 2: Validate/Create Specifications
- If specs exist: Read and validate
- If specs missing: Create them (ask user questions)
- Ensure requirements are clear and testable

## Phase 3: Decompose with Software Engineering Principles
- Apply DRY (identify shared code)
- Apply separation of concerns (break into modules)
- Consider time complexity (O(n) vs O(1))
- Map dependencies explicitly
- Identify parallel vs sequential tasks

## Phase 4: Create Execution Plan
- Structure tasks by dependency (parallel phases + sequential phases)
- **NEW:** Add workflow transition reminder
```

**Critical addition at end of plan:**
```markdown
---

## ⚡ Next Step: Execute This Plan

**IMPORTANT:** This plan is ready for execution!

To start parallel development, run:
```
/slashsense:parallel:execute
```

Or say: "execute this plan in parallel"

**What happens next:**
- Main agent spawns {N} Haiku agents in parallel
- Each agent creates own issue + worktree autonomously
- All work happens concurrently (O(1) setup time)
- Cost: ${cost} (vs ${old_cost} with Sonnet)

Ready to execute? 🚀
```

### 3. Enhance parallel-execute Command

**Add automatic plan detection:**

```markdown
## Phase 1: Load or Create Plan

**Check for existing plan:**

```bash
# Find most recent plan file
LATEST_PLAN=$(ls -t .parallel/plans/PLAN-*.md 2>/dev/null | head -1)
```

**NEW: Automatic workflow transition detection**

If this command was run immediately after `/slashsense:parallel:plan`:
- Auto-load the just-created plan
- Show brief summary
- **Skip asking user** - they already confirmed by running execute
- Immediately proceed to Phase 2 (spawn agents)

**Detection logic:**
```python
# Check if plan was created in last 5 minutes
if plan_exists and plan_age_seconds < 300:
    print("✅ Found recent plan: {plan_file}")
    print("📋 Executing {N} tasks in parallel...")
    # Proceed directly to spawning agents
```

**If no recent plan:**
- Ask: "No plan found. Options:
  1. Create plan now with /slashsense:parallel:plan
  2. Provide task list directly and I'll create inline plan
  3. Cancel"
```

### 4. Add Skills Integration Reminders

**In parallel-plan command (Step 1: Analyze):**

```markdown
## Step 1: Analyze Conversation and Requirements

**IMPORTANT: Check for existing resources first!**

Before planning, check if any Skills can help:

1. **software-architect** - For systematic problem analysis
   - Activates on: "design", "architect", "plan"
   - Provides: Research, specification, decomposition

2. **parallel-development-expert** - For parallelization guidance
   - Activates on: "parallel", "faster", "concurrent"
   - Provides: Task analysis, dependency mapping

3. **performance-optimizer** - For bottleneck identification
   - Activates on: "optimize", "slow", "bottleneck"
   - Provides: Performance analysis, Amdahl's Law

**Check for existing implementations:**

```bash
# Search for similar features
grep -r "similar_feature_name" . --include="*.{ts,js,py}"

# Check for specs
ls docs/specs/ docs/ARCHITECTURE.md README.md 2>/dev/null
```

**If similar code exists:**
- Read it to understand patterns
- Apply DRY: Extract shared functionality
- Reuse instead of duplicate

**If specs exist:**
- Read and validate against requirements
- Update specs if needed
- Don't proceed without clear specifications
```

### 5. Update Haiku Agents with Software Engineering Knowledge

**Add to ALL Haiku agents (parallel-task-executor, worktree-manager, etc.):**

```markdown
## Software Engineering Principles (MANDATORY)

Before implementing ANY code, you MUST:

### 1. Research Existing Solutions

**Check for similar code:**
```bash
# Search for related functionality
grep -r "related_keyword" . --include="*.{ext}"

# Find existing modules
ls -la {relevant_directories}
```

**If similar code exists:**
- Read it (use Read tool)
- Understand the pattern
- **Reuse, don't duplicate!**
- If you must create new code, follow the same pattern

### 2. Follow Specifications

**Check for specs:**
```bash
ls docs/specs/ docs/ARCHITECTURE.md README.md 2>/dev/null
```

**If specs exist:**
- Read them first (use Read tool)
- Validate your implementation against specs
- If spec is unclear, ask main agent for clarification
- **Never deviate from specs without approval**

**If specs don't exist:**
- Follow existing code patterns
- Ask main agent if unsure

### 3. Apply DRY (Don't Repeat Yourself)

**Before writing code:**
- Is this functionality already implemented somewhere?
- Can I extract shared logic to a utility function?
- Am I duplicating configuration or constants?

**If you find duplication:**
- Extract to shared module/function/constant
- Update both usages to reference shared code
- Document the extraction

### 4. Separation of Concerns

**Organize code by responsibility:**
- Data access → separate module
- Business logic → separate module
- UI/presentation → separate module
- Configuration → separate file

**Don't mix concerns in single function!**

### 5. Time Complexity Awareness

**Consider algorithmic efficiency:**
- O(1) - Constant time (best)
- O(log n) - Logarithmic (good)
- O(n) - Linear (acceptable)
- O(n²) - Quadratic (avoid if possible)
- O(2ⁿ) - Exponential (avoid!)

**If you write a loop inside a loop:**
- Question if there's a better way
- Document why O(n²) is necessary
- Consider using maps/sets for O(n) lookups

### 6. Code Quality Standards

**Readability:**
- Clear, descriptive names
- Functions < 50 lines
- Single responsibility per function
- Comments explain WHY, not WHAT

**Testing:**
- Write tests FIRST (TDD)
- Test happy path + edge cases
- Mock external dependencies
- Aim for >80% coverage

**Error Handling:**
- Validate inputs
- Handle errors gracefully
- Provide clear error messages
- Never swallow exceptions

---

## ❌ RULES TO PREVENT BAD CODE

**You MUST stop and ask main agent if:**

1. **Found duplicate code** - "Should I extract this to shared utility?"
2. **No spec exists** - "No specification found. Should I create one?"
3. **Time complexity > O(n)** - "This is O(n²). Is there a better approach?"
4. **Large function (>50 lines)** - "This function is large. Should I split it?"
5. **Mixing concerns** - "This mixes data access and UI. Should I separate?"

**NEVER proceed with bad practices without approval!**
```

### 6. Create Workflow Transition Detection

**New file: `lib/workflow_transitions.py`**

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""
Detect workflow transitions and suggest next steps.
"""

import os
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkflowState:
    """Current workflow state."""
    last_command: str
    timestamp: float
    plan_file: Optional[str]

class WorkflowDetector:
    """Detect workflow transitions."""

    def __init__(self):
        self.state_file = Path(".parallel/.workflow_state")

    def save_state(self, command: str, plan_file: Optional[str] = None):
        """Save workflow state."""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            f.write(f"{command}\n{time.time()}\n{plan_file or ''}\n")

    def load_state(self) -> Optional[WorkflowState]:
        """Load workflow state."""
        if not self.state_file.exists():
            return None

        with open(self.state_file, 'r') as f:
            lines = f.read().strip().split('\n')
            if len(lines) < 2:
                return None

            return WorkflowState(
                last_command=lines[0],
                timestamp=float(lines[1]),
                plan_file=lines[2] if len(lines) > 2 and lines[2] else None
            )

    def should_auto_execute(self) -> tuple[bool, str]:
        """
        Determine if we should auto-execute based on workflow state.

        Returns:
            (should_execute, reason)
        """
        state = self.load_state()
        if not state:
            return False, "No previous workflow state"

        # Check if last command was plan
        if state.last_command != "parallel:plan":
            return False, f"Last command was {state.last_command}, not plan"

        # Check if plan was recent (< 5 minutes)
        age_seconds = time.time() - state.timestamp
        if age_seconds > 300:  # 5 minutes
            return False, f"Plan is {age_seconds:.0f}s old (> 5 min)"

        # Check if plan file exists
        if state.plan_file and Path(state.plan_file).exists():
            return True, f"Recent plan found: {state.plan_file}"

        return False, "Plan file not found"

# CLI usage
if __name__ == "__main__":
    import sys

    detector = WorkflowDetector()

    if len(sys.argv) < 2:
        print("Usage: workflow_transitions.py <save|check> [command] [plan_file]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "save":
        command = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        plan_file = sys.argv[3] if len(sys.argv) > 3 else None
        detector.save_state(command, plan_file)
        print(f"✅ Saved state: {command}")

    elif action == "check":
        should_execute, reason = detector.should_auto_execute()
        if should_execute:
            print(f"✅ AUTO-EXECUTE: {reason}")
            sys.exit(0)
        else:
            print(f"❌ NO AUTO-EXECUTE: {reason}")
            sys.exit(1)
```

**Usage in parallel-plan:**

```bash
# At end of plan creation
uv run lib/workflow_transitions.py save "parallel:plan" "$PLAN_FILE"
```

**Usage in parallel-execute:**

```bash
# At start of execute
if uv run lib/workflow_transitions.py check; then
    echo "✅ Auto-executing recent plan..."
    # Skip user confirmation, proceed directly
else
    echo "No recent plan, asking user..."
    # Show plan selection UI
fi
```

---

## 📊 Expected Improvements

### Before (Current)

```
User: /slashsense:parallel:plan
→ Plan created

[User has to manually run]
User: /slashsense:parallel:execute
→ Execution starts

Issues:
- Manual workflow transition
- No research phase
- No spec validation
- No Skills integration
- Haiku agents don't apply principles
```

### After (Improved)

```
User: /slashsense:parallel:plan
→ Research existing code ✅
→ Check for specs ✅
→ Validate requirements ✅
→ Apply DRY/SoC ✅
→ Create plan ✅
→ Remind to execute ✅

User: /slashsense:parallel:execute
→ Detect recent plan ✅
→ Auto-load and execute ✅
→ Haiku agents apply principles ✅

Benefits:
- Automatic workflow transition
- Research-driven planning
- Specification validation
- Skills integration
- Better code quality
```

---

## 🚀 Implementation Plan

**Phase 1: Foundation (can parallelize these)**
1. Copy software-architect skill → `skills/software-architect/`
2. Create `lib/workflow_transitions.py`
3. Create test files for validation

**Phase 2: Update Commands (sequential - depends on Phase 1)**
4. Update `commands/slashsense-parallel-plan.md` with 5-phase workflow
5. Update `commands/slashsense-parallel-execute.md` with auto-transition
6. Add workflow state tracking to both commands

**Phase 3: Update Agents (can parallelize these)**
7. Update `agents/parallel-task-executor.md` with SE principles
8. Update `agents/worktree-manager.md` with SE principles
9. Update `agents/issue-orchestrator.md` with SE principles
10. Update `agents/test-runner.md` with SE principles
11. Update `agents/performance-analyzer.md` with SE principles

**Phase 4: Testing**
12. Create test plan
13. Test plan → execute transition
14. Test research phase
15. Test spec validation
16. Test Haiku agent SE compliance

**Phase 5: Documentation**
17. Update README with new workflow
18. Create WORKFLOW.md guide
19. Update migration guide

---

## ✅ Success Criteria

- [ ] software-architect skill integrated
- [ ] parallel-plan includes research phase
- [ ] parallel-plan validates/creates specs
- [ ] parallel-execute auto-detects recent plans
- [ ] All Haiku agents enforce SE principles
- [ ] Workflow transitions automatically
- [ ] No duplicate code created
- [ ] All code follows DRY/SoC
- [ ] Documentation complete

---

## 📝 Notes

**This addresses the core issue:** The system will now AUTOMATICALLY transition from planning to execution, and SYSTEMATICALLY apply software engineering principles throughout.

**User experience improvement:**
```
Before: User creates plan → User manually executes plan
After:  User creates plan → System reminds → User executes → System auto-detects
```

**Code quality improvement:**
```
Before: Haiku agents just execute tasks
After:  Haiku agents research, validate, apply principles, ask when unclear
```
