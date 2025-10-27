# Revised Architecture: plan.yaml as Source of Truth

**Date:** 2025-10-27
**Issue Identified:** Creating GitHub issues duplicates information already in plan.yaml
**Solution:** Use plan.yaml as single source of truth, commit .parallel/ to git, make GitHub issues optional

---

## The Problem with Original Design

**Original Flow:**
```
plan.yaml (has task info)
    ↓
Create GitHub issues (DUPLICATE task info)
    ↓
Agents use issue numbers
    ↓
Issues track status
```

**Problems:**
1. ❌ Duplication: Task info in both plan.yaml and GitHub issues
2. ❌ Dependency: Requires GitHub API for basic workflow
3. ❌ Overhead: Creating issues takes 12-60 seconds
4. ❌ Complexity: Need issue number mapping
5. ❌ Not git-tracked: .parallel/ was gitignored

---

## Revised Design: plan.yaml as Source of Truth

**New Flow:**
```
.parallel/plan.yaml (complete task definitions - committed to git)
    ↓
Agents read directly from plan.yaml
    ↓
Status tracked in .parallel/status/ (committed or gitignored)
    ↓
GitHub issues OPTIONAL (only if user wants GitHub integration)
```

**Benefits:**
1. ✅ Single source of truth (plan.yaml)
2. ✅ No GitHub dependency for execution
3. ✅ Faster (no issue creation overhead)
4. ✅ Git-tracked (version controlled tasks)
5. ✅ Simpler (no mapping files needed)
6. ✅ Offline-capable

---

## Directory Structure

```
project-root/
├── .parallel/                      # Committed to git (source of truth)
│   ├── plan.yaml                   # Complete task definitions ✅ COMMITTED
│   ├── status/                     # Task execution status ✅ COMMITTED
│   │   ├── task-1.yaml
│   │   ├── task-2.yaml
│   │   └── task-3.yaml
│   ├── research/                   # Optional research results (gitignored)
│   │   ├── task-1.json
│   │   └── task-2.json
│   └── scripts/                    # Helper scripts ✅ COMMITTED
│       ├── init.sh
│       ├── status.sh
│       └── cleanup.sh
├── worktrees/                      # Git worktrees (gitignored)
│   ├── task-1/
│   ├── task-2/
│   └── task-3/
└── .gitignore
```

**What's committed:**
- `.parallel/plan.yaml` - Task definitions
- `.parallel/status/` - Task status (or optionally gitignored)
- `.parallel/scripts/` - Helper scripts

**What's gitignored:**
- `worktrees/` - Temporary work directories
- `.parallel/research/` - Optional research cache

---

## Enhanced plan.yaml Format

```yaml
project:
  name: "my-project"
  description: "Project description"
  created: "2025-10-27"

parallel_config:
  max_concurrent: 4
  auto_research: true          # Use Copilot for pre-implementation research
  github_integration: false    # Optional GitHub issue creation
  status_tracking: "file"      # "file" or "github"

tasks:
  - id: "task-1"
    title: "Implement authentication module"
    description: |
      Add OAuth authentication using Auth0.
      Support Google and GitHub providers.

    # Task details
    priority: "high"
    complexity: 7
    estimated_hours: 8

    # Implementation guidance
    files:
      - "src/auth/oauth.ts"
      - "src/auth/providers.ts"
      - "tests/auth.test.ts"

    dependencies: []             # No dependencies

    implementation_steps:
      - "Install Auth0 SDK"
      - "Create OAuth configuration"
      - "Implement login flow"
      - "Implement logout flow"
      - "Add provider buttons"
      - "Write tests"

    success_criteria:
      - "User can login with Google"
      - "User can login with GitHub"
      - "User can logout"
      - "All tests passing"
      - "No security vulnerabilities"

    research_keywords:           # For Copilot research
      - "react authentication"
      - "auth0 react"
      - "oauth best practices"

    # Execution tracking (updated by orchestrator/agents)
    status: "pending"            # pending, in_progress, completed, blocked
    assigned_to: null            # Agent identifier
    started_at: null
    completed_at: null
    worktree: null               # worktrees/task-1
    branch: null                 # feature/task-1

    # Results (updated by agents)
    commits: 0
    files_changed: []
    tests_added: 0
    tests_passing: false

  - id: "task-2"
    title: "Implement dashboard UI"
    description: "Create main dashboard with user stats"
    priority: "medium"
    complexity: 5
    estimated_hours: 6

    files:
      - "src/components/Dashboard.tsx"
      - "src/hooks/useDashboard.ts"
      - "tests/Dashboard.test.tsx"

    dependencies: ["task-1"]     # Depends on auth

    implementation_steps:
      - "Create Dashboard component"
      - "Fetch user data"
      - "Display statistics"
      - "Add loading states"
      - "Write tests"

    success_criteria:
      - "Dashboard displays user stats"
      - "Loading states work"
      - "Error handling works"
      - "Tests passing"

    research_keywords:
      - "react dashboard"
      - "data visualization"
      - "loading states"

    status: "pending"
```

**Key additions:**
- `parallel_config` section for workflow settings
- `github_integration: false` by default
- `research_keywords` for Copilot research
- Inline status tracking (no separate files needed)
- Complete implementation guidance

---

## Workflow: plan.yaml-Centric

### Phase 1: Planning (Orchestrator - Sonnet)

```bash
# 1. Create comprehensive plan.yaml
cat > .parallel/plan.yaml <<EOF
project:
  name: "my-app"

parallel_config:
  max_concurrent: 4
  auto_research: true
  github_integration: false  # No GitHub issues needed!

tasks:
  - id: "task-1"
    title: "Implement auth"
    description: "..."
    # ... complete task definition
EOF

# 2. Commit plan to git
git add .parallel/plan.yaml
git commit -m "feat: add parallel execution plan"
```

### Phase 2: Optional Research (Copilot)

```bash
# Only if parallel_config.auto_research: true

# Read plan.yaml
yq '.tasks[]' .parallel/plan.yaml | while read task; do
  TASK_ID=$(echo "$task" | yq '.id')
  KEYWORDS=$(echo "$task" | yq '.research_keywords | join(", ")')

  # Delegate research to Copilot
  ./copilot-delegate/scripts/research_task.sh general \
    "Research best practices for: $KEYWORDS"

  # Save to .parallel/research/ (gitignored cache)
  mv result.json .parallel/research/$TASK_ID.json
done
```

### Phase 3: Worktree Setup

```bash
# Read tasks from plan.yaml and create worktrees
yq '.tasks[].id' .parallel/plan.yaml | while read task_id; do
  git worktree add "worktrees/$task_id" -b "feature/$task_id"

  # Update plan.yaml with worktree info
  yq -i ".tasks[] |= select(.id == \"$task_id\") | .worktree = \"worktrees/$task_id\"" .parallel/plan.yaml
  yq -i ".tasks[] |= select(.id == \"$task_id\") | .branch = \"feature/$task_id\"" .parallel/plan.yaml
done

# Commit updated plan
git add .parallel/plan.yaml
git commit -m "chore: assign worktrees to tasks"
```

### Phase 4: Parallel Execution (Haiku Agents)

**Each agent receives:**
- Task ID (e.g., "task-1")
- Path to plan.yaml

**Agent workflow:**
```bash
#!/bin/bash
TASK_ID=$1

# Read task from plan.yaml
TASK=$(yq ".tasks[] | select(.id == \"$TASK_ID\")" .parallel/plan.yaml)

# Extract task details
TITLE=$(echo "$TASK" | yq '.title')
DESCRIPTION=$(echo "$TASK" | yq '.description')
FILES=$(echo "$TASK" | yq '.files[]')
STEPS=$(echo "$TASK" | yq '.implementation_steps[]')
WORKTREE=$(echo "$TASK" | yq '.worktree')

# Check for research
if [ -f ".parallel/research/$TASK_ID.json" ]; then
  echo "📚 Research available:"
  cat ".parallel/research/$TASK_ID.json"
fi

# Update status to in_progress
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"in_progress\"" .parallel/plan.yaml
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .started_at = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" .parallel/plan.yaml
git add .parallel/plan.yaml
git commit -m "chore: start $TASK_ID"

# Move to worktree
cd "$WORKTREE"

# Implement task following steps
# ...

# Update status to completed
cd - > /dev/null
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .status = \"completed\"" .parallel/plan.yaml
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .completed_at = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" .parallel/plan.yaml
yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .tests_passing = true" .parallel/plan.yaml

# Commit status update
git add .parallel/plan.yaml
git commit -m "chore: complete $TASK_ID"
```

### Phase 5: Optional PR Creation (Copilot)

```bash
# Read completed tasks from plan.yaml
yq '.tasks[] | select(.status == "completed")' .parallel/plan.yaml | while read task; do
  TASK_ID=$(echo "$task" | yq '.id')
  TITLE=$(echo "$task" | yq '.title')
  BRANCH=$(echo "$task" | yq '.branch')

  # Delegate PR creation to Copilot (if desired)
  ./copilot-delegate/scripts/github_operation.sh create-pr \
    "$TITLE" \
    "Implements $TASK_ID. See .parallel/plan.yaml for details." \
    main \
    "$BRANCH"
done
```

---

## Optional GitHub Integration

**If user wants GitHub issues** (set `github_integration: true` in plan.yaml):

```bash
# Optional: Create GitHub issues from plan.yaml
yq '.tasks[]' .parallel/plan.yaml | while read task; do
  TASK_ID=$(echo "$task" | yq '.id')
  TITLE=$(echo "$task" | yq '.title')
  DESCRIPTION=$(echo "$task" | yq '.description')

  # Create issue
  ISSUE_URL=$(gh issue create --title "$TITLE" --body "$DESCRIPTION")
  ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')

  # Update plan.yaml with issue number
  yq -i ".tasks[] |= select(.id == \"$TASK_ID\") | .github_issue = $ISSUE_NUM" .parallel/plan.yaml
done

# Commit issue references
git add .parallel/plan.yaml
git commit -m "chore: link GitHub issues to tasks"
```

**Agent updates GitHub issue:**
```bash
# If github_issue exists, update it
GITHUB_ISSUE=$(yq ".tasks[] | select(.id == \"$TASK_ID\") | .github_issue" .parallel/plan.yaml)

if [ -n "$GITHUB_ISSUE" ] && [ "$GITHUB_ISSUE" != "null" ]; then
  gh issue comment $GITHUB_ISSUE --body "✅ Task completed"
  gh issue close $GITHUB_ISSUE
fi
```

---

## Status Tracking Comparison

### Option 1: Inline in plan.yaml (Recommended)

**Benefits:**
- ✅ Single file
- ✅ Easy to query: `yq '.tasks[] | select(.status == "completed")'`
- ✅ Git history shows progress
- ✅ No additional files

**Drawbacks:**
- ⚠️ Merge conflicts if multiple agents update simultaneously
- ⚠️ File grows with status updates

**Mitigation:**
- Use git worktree (each agent in own worktree, no conflicts)
- Status updates are small (no problem)

### Option 2: Separate status files in .parallel/status/

```
.parallel/status/
├── task-1.yaml
├── task-2.yaml
└── task-3.yaml
```

**Benefits:**
- ✅ No merge conflicts
- ✅ Parallel writes OK
- ✅ Can gitignore if desired

**Drawbacks:**
- ❌ More files to manage
- ❌ Need to sync with plan.yaml

---

## Comparison: Old vs. New Design

| Aspect | Old Design | New Design |
|--------|-----------|------------|
| **Source of truth** | GitHub issues | plan.yaml |
| **Duplication** | Yes (plan + issues) | No (just plan) |
| **GitHub dependency** | Required | Optional |
| **Offline capable** | No | Yes |
| **Setup time (4 tasks)** | 60-80s (issue creation) | 0s |
| **Git tracking** | No (.parallel gitignored) | Yes (.parallel committed) |
| **Version control** | Issues only | Full history |
| **Complexity** | High (mapping files) | Low (just plan) |
| **Agent startup** | Wait for issues | Immediate |

---

## Migration from Old Design

### For existing Contextune users:

**Before (with GitHub issues):**
```bash
# Create issues
./batch_create_issues.sh plan.yaml

# Spawn agents with issue numbers
export TASK_ISSUE_NUM=101
```

**After (plan.yaml only):**
```bash
# No issue creation needed!

# Spawn agents with task ID
export TASK_ID=task-1
```

**Changes needed:**
1. Update `parallel-task-executor.md` to read from plan.yaml
2. Remove issue creation scripts (or make optional)
3. Update status tracking to use plan.yaml
4. Remove issue number mapping

---

## Implementation Checklist

### Phase 1: Core Infrastructure

- [ ] Design complete plan.yaml schema
- [ ] Create plan.yaml validator script
- [ ] Update .gitignore (remove .parallel/, add worktrees/)
- [ ] Create plan.yaml template generator
- [ ] Write plan.yaml documentation

### Phase 2: Agent Updates

- [ ] Update `parallel-task-executor.md` to read plan.yaml
- [ ] Remove GitHub issue creation dependency
- [ ] Add plan.yaml status update commands
- [ ] Test agent with plan.yaml workflow

### Phase 3: Optional GitHub Integration

- [ ] Create optional GitHub sync script
- [ ] Add `github_integration` config option
- [ ] Update docs for GitHub integration
- [ ] Test hybrid mode (plan.yaml + issues)

### Phase 4: Migration

- [ ] Document migration from old design
- [ ] Provide migration script
- [ ] Update all documentation
- [ ] Test with real project

---

## Revised Scripts Needed

### `scripts/init_plan.sh`
- Creates `.parallel/plan.yaml` from template
- Validates structure
- Commits to git

### `scripts/update_status.sh`
- Updates task status in plan.yaml
- Commits changes
- Usage: `./update_status.sh task-1 completed`

### `scripts/query_plan.sh`
- Queries plan.yaml for task info
- Usage: `./query_plan.sh task-1` → returns task JSON

### `scripts/optional_github_sync.sh`
- Syncs plan.yaml with GitHub issues (if enabled)
- Creates issues for new tasks
- Updates issue status

---

## Conclusion

**Original Design Problems:**
- ❌ Duplicated task information
- ❌ Required GitHub API
- ❌ Slower (issue creation overhead)
- ❌ Complex (mapping files)
- ❌ Not git-tracked

**New Design Benefits:**
- ✅ Single source of truth (plan.yaml)
- ✅ Git-tracked and version controlled
- ✅ No GitHub dependency
- ✅ Faster (no issue creation)
- ✅ Simpler (no mapping needed)
- ✅ Offline-capable
- ✅ GitHub integration optional

**Recommendation:** Adopt new design immediately. The old design was over-engineered.

**Next steps:**
1. Create plan.yaml schema and validator
2. Update parallel-task-executor agent
3. Write helper scripts for plan.yaml management
4. Document workflow
5. Test with real project
