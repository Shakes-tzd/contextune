# Integration Scripts v3: Contextune ctx-plan Integration

**Version:** 3.0
**Design:** Works with Contextune ctx-plan command (research already included)

---

## Overview

These scripts integrate copilot-delegate with Contextune's parallel execution workflows. Plans are created by the `/ctx:plan` command which includes comprehensive parallel research (5 agents).

**Key principles:**
- ✅ Plans created by `/ctx:plan` command (includes research)
- ✅ Research already embedded in plan.yaml (no separate research step)
- ✅ `.parallel/plans/` committed to git
- ✅ No GitHub issues required
- ✅ Simple workflow: plan → setup worktrees → spawn agents

---

## Quick Start

```bash
# 1. Create plan with research (via Contextune)
/ctx:plan

# 2. Setup worktrees from plan
./integration-scripts-v2/setup_worktrees_from_plan.sh

# 3. Spawn agents
# (agents read from .parallel/plans/plan.yaml and tasks/*.md)
```

**That's it!** Research is already done by ctx-plan in Step 1.

## Prerequisites

1. **Contextune plugin installed** (provides `/ctx:plan` command)
2. **copilot-delegate skill** (for GitHub operations via Copilot CLI)
3. **yq** installed (`brew install yq` on macOS)

---

## Scripts

### 1. `setup_worktrees_from_plan.sh`

**Purpose:** Create git worktrees for parallel task execution based on plan created by `/ctx:plan`

**Usage:**
```bash
./setup_worktrees_from_plan.sh [path/to/plan.yaml]
```

**Default path:** `.parallel/plans/plan.yaml` (created by `/ctx:plan`)

**Requirements:**
- Plan must exist (created by `/ctx:plan`)
- Git repository must have no uncommitted changes
- Tasks must have status != "completed"

**What it does:**
1. Reads plan from `.parallel/plans/plan.yaml`
2. Parses task list from plan index
3. For each pending task:
   - Creates worktree: `worktrees/task-{id}`
   - Creates branch: `feature/task-{id}`
   - Updates task metadata with worktree/branch info
4. Commits metadata updates

**Output:**
```
worktrees/
├── task-0/             # Worktree for task-0
├── task-1/             # Worktree for task-1
└── task-2/             # Worktree for task-2

.parallel/plans/tasks/task-*.md  # Updated with worktree/branch info
├── task-2.json         # Research results for task-2
└── summary.md          # Summary of all research
```

**Notes:**
- Research directory is gitignored (cache only)
- Delete research files to refresh
- Agents will read research if available

---

### 3. `setup_worktrees_from_plan.sh`

**Purpose:** Create git worktrees based on plan.yaml

**Usage:**
```bash
./setup_worktrees_from_plan.sh [path/to/plan.yaml]
```

**Requirements:**
- plan.yaml must exist
- Git repository must have no uncommitted changes
- Tasks must have status != "completed"

**What it does:**
1. Reads tasks from plan.yaml
2. For each pending task:
   - Creates worktree: `worktrees/task-{id}`
   - Creates branch: `feature/task-{id}`
   - Updates plan.yaml with worktree/branch info
3. Commits plan.yaml updates

**Output:**
```
worktrees/
├── task-1/             # Worktree for task-1
└── task-2/             # Worktree for task-2

.parallel/plan.yaml:    # Updated with:
  worktree: "worktrees/task-1"
  branch: "feature/task-1"
```

**Next step:** Spawn agents in each worktree

---

## Plan Format (Created by /ctx:plan)

The `/ctx:plan` command creates a modular plan structure:

```
.parallel/plans/
├── plan.yaml           # Index/TOC with research synthesis
├── tasks/
│   ├── task-0.md      # Individual task files (GitHub issue format)
│   ├── task-1.md
│   └── task-2.md
├── templates/
│   └── task-template.md
└── scripts/
    ├── status.sh
    └── update.sh
```

### plan.yaml Structure

```yaml
metadata:
  name: "Feature Name"
  created: "20251027-120000"
  status: "ready"

overview: |
  Brief description of what we're building

# Research synthesis from 5 parallel agents
research:
  approach: "Best approach from research"
  libraries:
    - name: "library-name"
      reason: "Why selected"
  patterns:
    - file: "src/example.ts:42"
      description: "Pattern to reuse"
  specifications:
    - requirement: "Must follow X"
      status: "must_follow"
  dependencies:
    existing: ["dep-1"]
    new: ["dep-2"]

# Task index (TOC)
tasks:
  - id: "task-0"
    name: "Task Name"
    file: "tasks/task-0.md"
    priority: "high"
    dependencies: []
```

### Task File Format (tasks/task-N.md)

Task files are in GitHub issue format (Markdown + YAML frontmatter):

```markdown
---
id: task-0
priority: high
status: pending
dependencies: []
labels:
  - parallel-execution
---

# Task Name

## 🎯 Objective
Clear description of what this accomplishes

## 🛠️ Implementation Approach
{From research synthesis}

**Libraries:**
- `library-1` - Why needed

**Pattern to follow:**
- **File:** `src/example.ts:42`
- **Description:** Pattern to reuse

## 📁 Files to Touch
**Create:** `path/to/new/file.ts`
**Modify:** `path/to/existing/file.ts`

## 🧪 Tests Required
- [ ] Test functionality
- [ ] Test edge cases

## ✅ Acceptance Criteria
- [ ] Tests pass
- [ ] Feature works
```

---

## Agent Integration

### How Agents Use ctx-plan Output

Agents read from the modular plan structure created by `/ctx:plan`:

```bash
#!/bin/bash
# Agent receives task ID only
TASK_ID=$1

# Find task file from plan index
TASK_FILE=$(yq ".tasks[] | select(.id == \"$TASK_ID\") | .file" .parallel/plans/plan.yaml)

# Read full task from markdown file
TASK_CONTENT=$(cat ".parallel/plans/$TASK_FILE")

# Parse YAML frontmatter
PRIORITY=$(echo "$TASK_CONTENT" | yq -p md '.priority')
STATUS=$(echo "$TASK_CONTENT" | yq -p md '.status')
DEPENDENCIES=$(echo "$TASK_CONTENT" | yq -p md '.dependencies[]')

# Read research synthesis from plan
RESEARCH=$(yq '.research' .parallel/plans/plan.yaml)
LIBRARIES=$(echo "$RESEARCH" | yq '.libraries[]')
PATTERNS=$(echo "$RESEARCH" | yq '.patterns[]')

# Task implementation is in markdown body
# Research findings are embedded in "🛠️ Implementation Approach" section

# Update status: in_progress
yq -i -p md ".status = \"in_progress\"" ".parallel/plans/$TASK_FILE"
git add ".parallel/plans/$TASK_FILE"
git commit -m "chore: start $TASK_ID"

# Work in worktree
WORKTREE="worktrees/$TASK_ID"
cd "$WORKTREE"
# ... implement ...

# Update status: completed
cd - > /dev/null
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"completed\"" .parallel/plan.yaml
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .tests_passing = true" .parallel/plan.yaml
git add .parallel/plan.yaml
git commit -m "chore: complete $TASK_ID"
```

**Key points:**
- No GitHub operations needed
- All status tracked in plan.yaml
- Git commits provide history
- Research read from `.parallel/research/` if available

---

## Optional GitHub Integration

**If you want GitHub issues**, set `github_integration: true` in plan.yaml and create optional sync script:

```bash
# Optional: Create GitHub issues from plan.yaml
yq '.tasks[]' .parallel/plan.yaml | while read task; do
  TASK_ID=$(echo "$task" | yq '.id')
  TITLE=$(echo "$task" | yq '.title')

  ISSUE_URL=$(gh issue create --title "$TITLE" --body "...")
  ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

  yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .github_issue = $ISSUE_NUM" .parallel/plan.yaml
done
```

**But this is OPTIONAL!** Most teams won't need it.

---

## Comparison to v1

| Feature | v1 (OLD) | v2 (NEW) |
|---------|----------|----------|
| **Setup time** | 60-80s | 0s |
| **GitHub required** | Yes | No |
| **Source of truth** | GitHub issues | plan.yaml |
| **Git tracked** | No (.parallel gitignored) | Yes (.parallel committed) |
| **Mapping files** | Yes (issue-mapping.json) | No |
| **Offline capable** | No | Yes |

**v2 is simpler, faster, and more flexible.**

---

## Troubleshooting

### "Plan file not found"
```bash
# Run init_plan.sh first
./init_plan.sh
```

### "auto_research is disabled"
```yaml
# Edit plan.yaml
parallel_config:
  auto_research: true  # Enable research
```

### "Uncommitted changes"
```bash
# Commit or stash changes before setup
git add . && git commit -m "wip"
# or
git stash
```

### "Worktree already exists"
```bash
# Remove existing worktree
git worktree remove worktrees/task-1
# or force remove
git worktree remove --force worktrees/task-1
```

### "Research failed"
```bash
# Check copilot CLI is working
copilot --version

# Check research keywords are defined
yq '.tasks[0].research_keywords' .parallel/plan.yaml
```

---

## Dependencies

### Required
- `bash` - Shell script execution
- `git` - Version control and worktrees
- `yq` - YAML parsing (install: `brew install yq`)

### Optional
- `copilot` CLI - For research phase (install: `npm install -g @githubnext/github-copilot-cli`)
- `jq` - JSON parsing for research results (install: `brew install jq`)
- `gh` CLI - For optional GitHub integration (install: `brew install gh`)

---

## Examples

### Example 1: Simple 2-Task Workflow

```bash
# 1. Initialize
./init_plan.sh

# 2. Edit plan.yaml
cat > .parallel/plan.yaml <<EOF
project:
  name: "my-app"

parallel_config:
  auto_research: false  # Skip research for speed

tasks:
  - id: "task-1"
    title: "Add login button"
    description: "Add login button to navbar"
    files: ["src/components/Navbar.tsx"]
    implementation_steps: ["Add button JSX", "Add click handler"]
    success_criteria: ["Button visible", "Click works"]
    status: "pending"

  - id: "task-2"
    title: "Add logout button"
    description: "Add logout button to navbar"
    files: ["src/components/Navbar.tsx"]
    implementation_steps: ["Add button JSX", "Add click handler"]
    success_criteria: ["Button visible", "Click works"]
    status: "pending"
EOF

# 3. Commit
git add .parallel/ && git commit -m "feat: add parallel plan"

# 4. Setup worktrees
./setup_worktrees_from_plan.sh

# 5. Spawn agents (manual for now)
# cd worktrees/task-1 && implement...
# cd worktrees/task-2 && implement...
```

### Example 2: With Research Phase

```bash
# 1. Initialize
./init_plan.sh

# 2. Edit plan.yaml (with research keywords)
vim .parallel/plan.yaml
# Add research_keywords: ["react hooks", "state management"]

git add .parallel/ && git commit -m "feat: add parallel plan"

# 3. Research
./research_from_plan.sh

# 4. Review research
cat .parallel/research/summary.md

# 5. Setup worktrees
./setup_worktrees_from_plan.sh

# 6. Agents will read research automatically
```

---

## FAQ

### Q: Do I need GitHub?
**A:** No! GitHub integration is optional. plan.yaml is the source of truth.

### Q: Where is task status tracked?
**A:** In plan.yaml by default. Status updates are git commits.

### Q: Can I still use GitHub issues if I want?
**A:** Yes! Set `github_integration: true` and add sync script.

### Q: What if I don't have yq?
**A:** Install it: `brew install yq`. It's required for parsing plan.yaml.

### Q: Is research required?
**A:** No. Set `auto_research: false` to skip.

### Q: Can I edit plan.yaml while agents are working?
**A:** Yes, but commit your changes to avoid conflicts.

---

## See Also

- `../REVISED_ARCHITECTURE.md` - Complete architectural design
- `../OLD_VS_NEW_DESIGN.md` - Comparison to old design
- `../FINAL_RECOMMENDATION.md` - Executive summary
- `../copilot-delegate/SKILL.md` - Copilot delegation skill

---

**Version:** 2.0
**Status:** Ready to use
**Recommendation:** Use these scripts instead of v1
