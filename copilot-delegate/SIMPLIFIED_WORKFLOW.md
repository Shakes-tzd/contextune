# Simplified Workflow: v3 Integration with ctx-plan

**Date:** 2025-10-27
**Version:** 3.0
**Status:** Current Recommendation

---

## Summary of Changes

After user feedback, we've dramatically simplified the copilot-delegate integration with Contextune's parallel execution workflow.

### What Changed?

**v1 (GitHub-centric) → v2 (plan.yaml-centric) → v3 (ctx-plan integration)**

#### Version History

**v1:** GitHub Issues Required
- Created GitHub issues from plan.yaml (60-80s overhead)
- Issues were source of truth
- Complex mapping files needed
- .parallel/ gitignored
- **Problem:** Duplicated information (plan.yaml + GitHub issues)

**v2:** plan.yaml as Source of Truth
- Eliminated GitHub issues requirement
- plan.yaml became source of truth
- .parallel/ committed to git
- 0s setup overhead
- **Problem:** Still had separate research phase

**v3:** ctx-plan Integration (CURRENT)
- Uses Contextune's `/ctx:plan` command
- Research already included (5 parallel agents)
- No separate research step needed
- Works with `.parallel/plans/` directory structure
- **Result:** Maximum simplification

---

## Why v3 is Better

### User Insight #1: Don't Duplicate Task Info

**User feedback:**
> "why are we still creating issues in addition to the task files instead of just making the task yaml files complete"

**Solution (v2):**
- Made plan.yaml the single source of truth
- Made GitHub integration optional
- Committed .parallel/ to git for version control

### User Insight #2: Don't Duplicate Research

**User feedback:**
> "why do we have to do more research per task if @commands/ctx-plan.md is supposed to ensure that all tasks are backed by research?"

**Solution (v3):**
- Recognized that `/ctx:plan` already does comprehensive research
- Removed redundant `research_from_plan.sh` script
- Updated workflow to assume research is pre-done
- Simplified to 2 steps: plan → setup worktrees

---

## The Simplified Workflow

### Step 1: Create Plan with Research

```bash
/ctx:plan
```

**What happens:**
1. User describes what they want to build
2. ctx-plan spawns 5 research agents IN PARALLEL:
   - Agent 1: Web Search - Similar Solutions
   - Agent 2: Web Search - Libraries/Tools
   - Agent 3: Codebase Pattern Search
   - Agent 4: Specification Validation
   - Agent 5: Dependency Analysis
3. Research synthesized into plan
4. Creates `.parallel/plans/` structure:
   - `plan.yaml` - Index/TOC with research synthesis
   - `tasks/*.md` - Individual task files with implementation approach
   - `scripts/` - Helper scripts

**Output:** `.parallel/plans/plan.yaml` with embedded research

### Step 2: Setup Worktrees

```bash
./integration-scripts-v2/setup_worktrees_from_plan.sh
```

**What happens:**
1. Reads task list from `.parallel/plans/plan.yaml`
2. Creates worktree for each task: `worktrees/task-{id}`
3. Creates branch for each task: `feature/task-{id}`
4. Updates task markdown files with worktree/branch info
5. Commits updates

**Output:** Worktrees ready for parallel execution

### Step 3: Execute (via Contextune)

```bash
/ctx:execute
```

**What happens:**
- Contextune spawns Haiku agents in each worktree
- Agents read task details and research from markdown files
- Agents implement features in parallel
- Results tracked in task files

**That's it!** No GitHub issues, no separate research phase.

---

## Directory Structure

### Before (v1 & v2)

```
project/
├── .parallel/                 # Gitignored (v1) or committed (v2)
│   ├── plan.yaml              # Complete task definitions (v2)
│   ├── research/              # Separate research step (v2)
│   │   ├── task-1.json
│   │   └── task-2.json
│   └── scripts/
└── worktrees/                 # Gitignored
    ├── task-1/
    └── task-2/
```

**Problems:**
- v1: Duplicated info in GitHub issues
- v2: Separate research step (redundant with ctx-plan)

### After (v3 - Current)

```
project/
├── .parallel/plans/           # Created by /ctx:plan (committed to git)
│   ├── plan.yaml              # Index/TOC with research synthesis
│   ├── tasks/
│   │   ├── task-0.md          # Task details + implementation approach
│   │   ├── task-1.md          # Research embedded in markdown
│   │   └── task-2.md
│   ├── templates/
│   │   └── task-template.md
│   └── scripts/
│       ├── status.sh
│       └── update.sh
└── worktrees/                 # Created by setup script (gitignored)
    ├── task-0/
    ├── task-1/
    └── task-2/
```

**Benefits:**
- Research embedded in plan.yaml and task files
- No duplication
- Git-tracked for team coordination
- Works seamlessly with Contextune commands

---

## Comparison Table

| Aspect | v1 (GitHub) | v2 (plan.yaml) | v3 (ctx-plan) |
|--------|-------------|----------------|---------------|
| **Setup time** | 60-80s | 0s | 0s |
| **Research time** | 15-20s | 15-20s | Included in plan |
| **Total overhead** | ~80s | ~20s | **0s** |
| **GitHub required** | Yes | No | No |
| **Separate research** | Yes | Yes | **No** |
| **Source of truth** | GitHub issues | plan.yaml | plan.yaml + tasks/*.md |
| **Directory** | .parallel/ | .parallel/ | .parallel/plans/ |
| **Git tracked** | No | Yes | Yes |
| **Steps** | 5 | 4 | **2** |

---

## What's Removed in v3

### Deprecated Scripts

**`research_from_plan.sh`** - REMOVED
- Reason: ctx-plan already does research
- Research embedded in plan.yaml and task markdown files
- No separate research step needed

**`init_plan.sh`** - NOT NEEDED
- Reason: /ctx:plan creates the plan
- Users don't manually initialize plans anymore

**`batch_create_issues.sh`** (v1) - DEPRECATED
- Reason: GitHub integration is optional
- Only create issues if team specifically wants them

### What Remains

**`setup_worktrees_from_plan.sh`** - UPDATED FOR v3
- Now reads from `.parallel/plans/plan.yaml`
- Reads task details from markdown files
- Updates task files (not plan.yaml) with worktree info

---

## Research in ctx-plan

### How Research is Embedded

**In plan.yaml:**

```yaml
research:
  approach: "Best approach from Agent 1"
  libraries:
    - name: "library-name"
      version: "1.2.3"
      reason: "Why selected"
  patterns:
    - file: "src/example.ts:42"
      description: "Pattern to reuse"
  specifications:
    - requirement: "Must follow X"
      status: "must_follow"
  dependencies:
    existing: ["existing-dep"]
    new: ["new-dep-needed"]
```

**In task files (tasks/task-N.md):**

```markdown
## 🛠️ Implementation Approach

{Approach from research synthesis}

**Libraries:**
- `library-1` - {Why needed}
- `library-2` - {Why needed}

**Pattern to follow:**
- **File:** `src/example.ts:42`
- **Description:** {Pattern to reuse}
```

### Why This Works

1. **Research done once** - During plan creation (5 parallel agents, ~2 min)
2. **Embedded in plan** - No separate files to track
3. **Available to agents** - Agents read from task markdown files
4. **Git tracked** - Full research history in version control
5. **No duplication** - Research findings in one place per task

---

## Cost Analysis

### v1: GitHub-centric (DEPRECATED)

```
Issue creation (4 tasks):   $0.01  (12-15s)
Research (4 tasks):          $0.04  (15-20s)
Execution (4 Haiku agents):  $0.12  (variable)
Issue updates:               $0.01  (10-12s)
Total:                       $0.18  (~50s overhead)
```

### v2: plan.yaml-centric (SUPERSEDED)

```
Issue creation:              $0.00  (0s - not needed)
Research (4 tasks):          $0.04  (15-20s)
Execution (4 Haiku agents):  $0.12  (variable)
Issue updates:               $0.00  (0s - git commits)
Total:                       $0.16  (~20s overhead)
```

### v3: ctx-plan integration (CURRENT)

```
Plan + Research (/ctx:plan): $0.04  (~2 min, 5 parallel agents)
Setup worktrees:             $0.00  (0s - bash script)
Execution (4 Haiku agents):  $0.12  (variable)
Updates:                     $0.00  (0s - git commits)
Total:                       $0.16  (0s overhead!)
```

**Key difference:** Research happens during planning (not separate step)

**Savings vs v1:**
- Time: -50s overhead (-100%)
- Cost: -$0.02 (-11%)
- Complexity: Much simpler (2 steps vs 5)

---

## Migration Guide

### From v1 (GitHub-centric)

If you were using `integration-scripts/`:

1. **Stop using** `batch_create_issues.sh`
2. **Stop using** `research_tasks.sh`
3. **Stop using** `batch_update_issues.sh`
4. **Start using** `/ctx:plan` command
5. **Use** updated `setup_worktrees_from_plan.sh` (from v3)

### From v2 (plan.yaml-centric)

If you were using `integration-scripts-v2/`:

1. **Stop using** `init_plan.sh` (use `/ctx:plan` instead)
2. **Stop using** `research_from_plan.sh` (deprecated - research in /ctx:plan)
3. **Update** to new `setup_worktrees_from_plan.sh` (reads from .parallel/plans/)
4. **Change** workflow to: `/ctx:plan` → setup_worktrees → execute

### Agent Updates

**Old agents expected:**
```bash
TASK_ID=$1
ISSUE_NUM=$2  # No longer needed!
```

**New agents expect:**
```bash
TASK_ID=$1
# Read from .parallel/plans/plan.yaml and tasks/*.md
```

---

## Benefits of v3

### 1. Maximum Simplicity

**2 steps instead of 5:**
1. `/ctx:plan` (creates plan with research)
2. `setup_worktrees_from_plan.sh` (creates worktrees)

**vs v1 (5 steps):**
1. Create plan.yaml
2. Create GitHub issues
3. Research tasks
4. Setup worktrees
5. Spawn agents

### 2. No Duplication

**Single source of truth:**
- Task info: `.parallel/plans/tasks/*.md`
- Research: Embedded in plan.yaml and task markdown
- No GitHub issues (unless you want them)
- No separate research files

### 3. Research Included

**5 parallel research agents built into `/ctx:plan`:**
- Agent 1: Web Search - Similar Solutions
- Agent 2: Web Search - Libraries/Tools
- Agent 3: Codebase Pattern Search
- Agent 4: Specification Validation
- Agent 5: Dependency Analysis

**Results synthesized into:**
- `plan.yaml` (research: section)
- Task markdown files (Implementation Approach sections)

### 4. Git Tracked

**Full version control:**
- Plan creation: committed
- Research findings: embedded in plan
- Task updates: committed
- Worktree assignments: committed
- Full history of decisions and progress

### 5. Offline Capable

**No network dependencies:**
- GitHub optional (not required)
- All information in local files
- Git operations only (no API calls)

---

## FAQ

### Q: Why remove the research script?

**A:** The `/ctx:plan` command already does comprehensive research using 5 parallel agents. Having a separate research step would duplicate this work.

**Evidence:**
- ctx-plan Step 2: "Parallel Research" with 5 agents
- Research findings embedded in plan.yaml
- Task files include "Implementation Approach" from research

### Q: What if I need more research?

**A:** Re-run `/ctx:plan` with more context:
- Mention specific concerns in your prompt
- Ask for deeper analysis on specific aspects
- The 5 research agents will investigate thoroughly

### Q: Can I still use GitHub issues?

**A:** Yes! GitHub integration is optional:
- Set `github_integration: true` in your setup
- Manually create issues from task markdown files
- Use GitHub for team coordination if desired
- But it's not required for the workflow

### Q: What happened to init_plan.sh?

**A:** Not needed. The `/ctx:plan` command creates the entire plan structure automatically, including:
- .parallel/plans/ directory
- plan.yaml with research synthesis
- tasks/*.md files with implementation details
- Helper scripts

### Q: How do I update from v2 to v3?

**A:**
1. Use `/ctx:plan` instead of `init_plan.sh` + manual editing
2. Remove calls to `research_from_plan.sh` (deprecated)
3. Update `setup_worktrees_from_plan.sh` (new version reads from .parallel/plans/)
4. Update agent scripts to read from task markdown files

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────┐
│  User describes what to build                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  /ctx:plan                                       │
│  ├─ Spawns 5 research agents in parallel        │
│  ├─ Synthesizes findings into plan.yaml         │
│  ├─ Creates task markdown files                 │
│  └─ Embeds research in Implementation Approach  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  .parallel/plans/                                │
│  ├── plan.yaml (with research: section)         │
│  ├── tasks/                                      │
│  │   ├── task-0.md (with 🛠️ approach)          │
│  │   ├── task-1.md                              │
│  │   └── task-2.md                              │
│  └── scripts/                                    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  setup_worktrees_from_plan.sh                   │
│  ├─ Reads plan.yaml index                       │
│  ├─ Creates worktree per task                   │
│  ├─ Creates branch per task                     │
│  └─ Updates task files with worktree info       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  worktrees/                                      │
│  ├── task-0/ → feature/task-0                   │
│  ├── task-1/ → feature/task-1                   │
│  └── task-2/ → feature/task-2                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  /ctx:execute (or manual agent spawn)           │
│  ├─ Spawns Haiku agent per worktree             │
│  ├─ Agents read task markdown files             │
│  ├─ Agents use research from Implementation     │
│  └─ Agents work in parallel                     │
└─────────────────────────────────────────────────┘
```

**Total steps: 2** (/ctx:plan + setup_worktrees)

---

## Conclusion

**Version 3 represents the final simplification** of the copilot-delegate integration with Contextune.

**Key achievements:**
- ✅ No duplication (single source of truth)
- ✅ No separate research step (embedded in /ctx:plan)
- ✅ No GitHub dependency (optional)
- ✅ 2 steps total (down from 5)
- ✅ 0s overhead (down from 80s)
- ✅ Git tracked (full version control)
- ✅ Research included (5 parallel agents)

**User insights led to these improvements:**
1. "Don't duplicate task info in GitHub issues" → v2
2. "Don't duplicate research if ctx-plan does it" → v3

**Status:** ✅ Ready to use

**Recommendation:** Use v3 integration exclusively. v1 and v2 are deprecated.

---

**Version:** 3.0
**Date:** 2025-10-27
**Files:**
- `integration-scripts-v2/setup_worktrees_from_plan.sh` - Updated for v3
- `integration-scripts-v2/research_from_plan.sh.deprecated` - Deprecated with explanation
- `integration-scripts-v2/README.md` - Updated for v3
- This document - Complete explanation of v3 simplification

