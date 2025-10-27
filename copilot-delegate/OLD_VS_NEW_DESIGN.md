# Old vs. New Design Comparison

**Date:** 2025-10-27
**Issue:** Original design duplicated task information and required GitHub issues
**Solution:** Use plan.yaml as single source of truth, make GitHub optional

---

## Side-by-Side Comparison

| Aspect | ❌ Old Design (v1) | ✅ New Design (v2) |
|--------|-------------------|-------------------|
| **Source of truth** | GitHub issues | `.parallel/plan.yaml` |
| **Task duplication** | Yes (plan + issues) | No (just plan) |
| **GitHub dependency** | Required | Optional |
| **Offline capable** | No | Yes |
| **Git tracked** | No (.parallel gitignored) | Yes (.parallel committed) |
| **Setup time (4 tasks)** | 60-80s (issue creation) | 0s |
| **Issue number mapping** | Yes (complex) | No (not needed) |
| **Agent startup** | Wait for issues | Immediate |
| **Status tracking** | GitHub issues | plan.yaml |
| **Version control** | Issues only | Full git history |
| **Team coordination** | Via GitHub | Via git commits |

---

## Workflow Comparison

### Old Design (v1) - GitHub Issues Required

```bash
# 1. Create plan.yaml
cat > plan.yaml <<EOF
tasks:
  - id: task-1
    title: "Implement auth"
EOF

# 2. Create GitHub issues from plan (DUPLICATION!)
./batch_create_issues.sh plan.yaml
# Takes 60-80 seconds
# Outputs: issue-mapping.json

# 3. Source issue mapping
source issue-mapping.env
export ISSUE_NUM_task_1=101  # From GitHub

# 4. Setup worktrees
./setup_worktrees.sh

# 5. Spawn agents with issue numbers
spawn_agent --task task-1 --issue 101

# 6. Agent creates issue, works, updates issue
# All GitHub operations in agent context

# 7. Manual PR creation or separate script
```

**Problems:**
- ❌ Task info exists in 2 places (plan.yaml + GitHub)
- ❌ 60-80 seconds wasted creating issues
- ❌ Issue mapping file needed
- ❌ Can't work offline
- ❌ Plan not version controlled

---

### New Design (v2) - plan.yaml Only

```bash
# 1. Initialize plan (creates .parallel/plan.yaml)
./init_plan.sh
# Outputs: .parallel/plan.yaml (COMPLETE task definitions)

# 2. Edit plan.yaml - add all task details
vim .parallel/plan.yaml

# 3. Commit plan to git (VERSION CONTROLLED!)
git add .parallel/
git commit -m "feat: add parallel execution plan"

# 4. Optional: Research (if auto_research: true)
./research_from_plan.sh
# Reads from plan.yaml, no extra config needed

# 5. Setup worktrees from plan
./setup_worktrees_from_plan.sh
# Reads from plan.yaml, updates plan with worktree info
# Commits updates automatically

# 6. Spawn agents with task ID only
spawn_agent --task task-1
# Agent reads from plan.yaml directly
# No issue numbers needed!

# 7. Agent works, updates plan.yaml status
# All updates go to plan.yaml (git tracked)

# 8. Optional: Create PRs at end
# Only if you want GitHub integration
```

**Benefits:**
- ✅ Task info in ONE place (plan.yaml)
- ✅ No setup overhead (0 seconds)
- ✅ No mapping files
- ✅ Works offline
- ✅ Full git history of task evolution
- ✅ GitHub optional, not required

---

## File Structure Comparison

### Old Design (v1)

```
project/
├── plan.yaml                    # Task definitions (not committed!)
├── issue-mapping.json           # GitHub issue numbers (generated)
├── issue-mapping.env            # Environment exports (generated)
├── worktrees/                   # Git worktrees (gitignored)
├── .parallel/                   # GITIGNORED
└── .gitignore
```

**Issues:**
- .parallel/ was gitignored (no history)
- Multiple generated mapping files
- Task info in plan.yaml not complete (just IDs)
- GitHub issues have the real task details

---

### New Design (v2)

```
project/
├── .parallel/                   # ✅ COMMITTED TO GIT
│   ├── plan.yaml                # ✅ Complete task definitions (source of truth)
│   ├── status/                  # ✅ Optional status files (if not inline)
│   │   ├── task-1.yaml
│   │   └── task-2.yaml
│   ├── research/                # Cache (gitignored)
│   │   ├── task-1.json
│   │   └── task-2.json
│   └── scripts/                 # ✅ Helper scripts (committed)
│       ├── status.sh
│       └── update.sh
├── worktrees/                   # Git worktrees (gitignored)
│   ├── task-1/
│   └── task-2/
└── .gitignore
```

**Benefits:**
- .parallel/plan.yaml is source of truth
- No generated mapping files
- Full git history
- Research cached (optional, gitignored)
- Helper scripts committed for team use

---

## Agent Workflow Comparison

### Old: Agent Receives Issue Number

```bash
# Agent startup (old)
TASK_ID=$1
ISSUE_NUM=$2  # From GitHub

# Agent has to:
# 1. Create GitHub issue (or receive pre-created number)
gh issue create --title "..." --body "..."

# 2. Work in worktree
cd worktrees/$TASK_ID

# 3. Implement feature

# 4. Update GitHub issue
gh issue comment $ISSUE_NUM --body "..."

# 5. Close GitHub issue
gh issue close $ISSUE_NUM

# Problem: GitHub operations in agent context!
```

---

### New: Agent Reads from plan.yaml

```bash
# Agent startup (new)
TASK_ID=$1

# Agent reads everything from plan.yaml
TASK=$(yq ".tasks[] | select(.id == \"$TASK_ID\")" .parallel/plan.yaml)

TITLE=$(echo "$TASK" | yq '.title')
DESCRIPTION=$(echo "$TASK" | yq '.description')
STEPS=$(echo "$TASK" | yq '.implementation_steps[]')
WORKTREE=$(echo "$TASK" | yq '.worktree')

# Check for research
if [ -f ".parallel/research/$TASK_ID.json" ]; then
  cat ".parallel/research/$TASK_ID.json"
fi

# Update status: in_progress
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"in_progress\"" .parallel/plan.yaml
git add .parallel/plan.yaml && git commit -m "chore: start $TASK_ID"

# Work in worktree
cd "$WORKTREE"
# Implement...

# Update status: completed
cd - > /dev/null
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"completed\"" .parallel/plan.yaml
git add .parallel/plan.yaml && git commit -m "chore: complete $TASK_ID"

# No GitHub operations needed!
# All status in plan.yaml (git tracked)
```

---

## Cost Comparison

### Old Design: Required Copilot for GitHub Issues

**4 parallel tasks:**

| Operation | Agent | Cost | Time |
|-----------|-------|------|------|
| Create 4 issues (batch) | Copilot | ~$0.01 | 12-15s |
| Research (4 tasks) | Copilot | ~$0.04 | 15-20s |
| Execution (4 agents) | Haiku | ~$0.12 | Variable |
| Update/close issues | Copilot | ~$0.01 | 10-12s |
| **Total** | | **$0.18** | **~50s overhead** |

---

### New Design: No GitHub Required

**4 parallel tasks:**

| Operation | Agent | Cost | Time |
|-----------|-------|------|------|
| Create issues | None | $0 | 0s |
| Research (4 tasks) | Copilot | ~$0.04 | 15-20s |
| Execution (4 agents) | Haiku | ~$0.12 | Variable |
| Update status | None | $0 | 0s (git commits) |
| **Total** | | **$0.16** | **~20s overhead** |

**Savings:**
- **Cost:** -$0.02 (-11%)
- **Time:** -30s (-60% overhead)

**If you want GitHub integration (optional):**
- Add $0.02 for optional issue creation/sync
- Total: $0.18 (same as old, but now optional!)

---

## Migration Guide

### From Old Design to New Design

#### Step 1: Create Enhanced plan.yaml

```yaml
# Old plan.yaml (minimal)
tasks:
  - id: task-1
    title: "Implement auth"

# New plan.yaml (complete)
project:
  name: "my-project"

parallel_config:
  auto_research: true
  github_integration: false  # NEW: optional!

tasks:
  - id: task-1
    title: "Implement auth"
    description: "Full detailed description..."
    files: ["src/auth.ts", "tests/auth.test.ts"]
    implementation_steps:
      - "Step 1"
      - "Step 2"
    success_criteria:
      - "Tests pass"
    research_keywords:
      - "oauth"
      - "authentication"
    # Inline status tracking
    status: "pending"
    worktree: null
    branch: null
```

#### Step 2: Update Scripts

**Old:**
```bash
./batch_create_issues.sh plan.yaml  # Creates GitHub issues
source issue-mapping.env            # Export issue numbers
./setup_worktrees.sh                # Setup worktrees
```

**New:**
```bash
./research_from_plan.sh             # Optional research
./setup_worktrees_from_plan.sh      # Setup from plan.yaml
# No issue creation needed!
```

#### Step 3: Update Agents

**Old agent code:**
```bash
# Expects ISSUE_NUM environment variable
if [ -z "$ISSUE_NUM" ]; then
  echo "ERROR: ISSUE_NUM not set!"
  exit 1
fi

gh issue create ...
```

**New agent code:**
```bash
# Reads from plan.yaml
TASK=$(yq ".tasks[] | select(.id == \"$TASK_ID\")" .parallel/plan.yaml)

# All info is in plan.yaml, no GitHub needed!
```

---

## Benefits Summary

### New Design Wins

1. ✅ **Simpler:** One source of truth (plan.yaml)
2. ✅ **Faster:** No issue creation overhead (0s vs 60s)
3. ✅ **Cheaper:** $0.16 vs $0.18 (-11%)
4. ✅ **Git-tracked:** Full version history
5. ✅ **Offline:** No GitHub dependency
6. ✅ **Flexible:** GitHub integration optional
7. ✅ **Team-friendly:** Commit plan.yaml, team sees tasks
8. ✅ **No duplication:** Task info in one place only

### When to Use GitHub Integration

**Use `github_integration: true` when:**
- Team uses GitHub Projects for tracking
- Want issues for discussion/review
- Need issue references in PRs
- Using GitHub automation (Actions, etc.)

**Skip GitHub integration when:**
- Working solo or small team
- Git commits are enough for tracking
- Want to work offline
- Don't need GitHub overhead

---

## Recommendation

**Use new design (v2) by default.**

GitHub integration should be **opt-in**, not required:

```yaml
parallel_config:
  github_integration: false  # Default: no GitHub needed
```

Change to `true` only if you specifically want GitHub issues.

---

## Files Overview

### Old Design (integration-scripts/)
```
integration-scripts/
├── batch_create_issues.sh       # ❌ Creates GitHub issues (60-80s)
├── research_tasks.sh             # ⚠️  Needs issue mapping
└── batch_update_issues.sh        # ❌ Updates GitHub issues
```

### New Design (integration-scripts-v2/)
```
integration-scripts-v2/
├── init_plan.sh                  # ✅ Initialize .parallel/plan.yaml
├── research_from_plan.sh         # ✅ Research from plan.yaml
└── setup_worktrees_from_plan.sh  # ✅ Setup from plan.yaml
```

**Simpler, faster, no GitHub dependency!**

---

## Conclusion

**Original design was over-engineered.**

Creating GitHub issues was unnecessary duplication. The new design:

1. Uses plan.yaml as single source of truth
2. Commits .parallel/ to git (version controlled)
3. Makes GitHub integration optional
4. Faster (no issue creation)
5. Simpler (no mapping files)
6. Cheaper (saves $0.02 per workflow)

**Adopt new design immediately.** Old design should be deprecated.

**For new users:** Start with `integration-scripts-v2/`

**For existing users:** Migrate to new design (simple conversion)

---

**Version:** 2.0 (plan.yaml-centric)
**Status:** Recommended approach
**Old version:** Deprecated (use v2 instead)
