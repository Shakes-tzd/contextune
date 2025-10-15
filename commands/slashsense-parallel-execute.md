---
name: slashsense:parallel:execute
description: Execute plan in parallel using git worktrees and multiple Claude sessions
---

# Parallel Execute - Automated Parallel Development

**Purpose:** Turn a plan into independent GitHub issues, create git worktrees, and **automatically spawn subagents** to work in parallel - completing multiple tasks simultaneously with zero manual coordination.

---

## 🎯 What This Does

1. **Documents your plan** to `.parallel/plans/PLAN-{timestamp}.md`
2. **Breaks plan into GitHub issues** (independent tasks only)
3. **Creates git worktrees** for each task (isolated branches)
4. **Automatically spawns subagents** to work in parallel on each worktree
5. **Monitors progress** and coordinates completion
6. **Merges completed work** back to main
7. **Cleans up worktrees** when done

**Key Feature:** I spawn multiple subagents automatically - you don't need to manage multiple terminals!

---

## ⚠️ Prerequisites Check

I will automatically validate these requirements before starting:

```bash
# 1. GitHub CLI installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI not installed: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated. Run: gh auth login"
    exit 1
fi

# 2. Git remote configured
if ! git remote get-url origin &> /dev/null && \
   ! git remote get-url $(git remote | head -1) &> /dev/null; then
    echo "❌ No git remote configured"
    exit 1
fi

# 3. Clean working tree
if ! git diff-index --quiet HEAD --; then
    echo "❌ Uncommitted changes. Commit or stash first."
    exit 1
fi

# 4. On main/master/develop branch
current_branch=$(git branch --show-current)
if [[ ! "$current_branch" =~ ^(main|master|develop)$ ]]; then
    echo "⚠️  Not on main branch (currently on: $current_branch)"
fi
```

**Automatic Setup:**
- ✅ Create GitHub labels if they don't exist
- ✅ Add `.parallel/` to `.gitignore` if not present
- ✅ Detect and use correct git remote name
- ✅ Validate all prerequisites before execution

---

## 📋 Workflow

### **Phase 0: GitHub Setup & Validation**

Before creating issues and worktrees, I perform these setup tasks:

**1. Create Standard Labels** (if they don't exist)

```bash
# Check and create labels for parallel execution
create_label_if_missing() {
    local name=$1
    local color=$2
    local desc=$3

    if ! gh label list | grep -q "^$name"; then
        gh label create "$name" --color "$color" --description "$desc" 2>/dev/null || {
            echo "⚠️  Could not create label '$name' (may lack permissions)"
        }
    fi
}

# Standard labels
create_label_if_missing "parallel-execution" "0366d6" "Task from parallel execution workflow"
create_label_if_missing "auto-created" "ededed" "Automatically generated issue"
create_label_if_missing "worktree" "fbca04" "Associated with git worktree"
```

**2. Setup .gitignore**

```bash
# Add .parallel/ to .gitignore if not present
if ! grep -q "^\.parallel/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Parallel execution workspace" >> .gitignore
    echo ".parallel/" >> .gitignore
    git add .gitignore
    git commit -m "chore: add .parallel/ to gitignore" 2>/dev/null || true
    echo "✅ Added .parallel/ to .gitignore"
fi
```

**3. Detect Git Remote**

```bash
# Auto-detect remote name (origin, upstream, or first available)
REMOTE_NAME=$(git remote | grep -E '^(origin|upstream)$' | head -1)
if [[ -z "$REMOTE_NAME" ]]; then
    REMOTE_NAME=$(git remote | head -1)
fi
echo "Using git remote: $REMOTE_NAME"
```

---

### **Phase 1: Planning & Documentation**

1. **Analyze the plan** I created in our conversation
2. **Identify independent tasks** that can run in parallel
3. **Document everything** to `.parallel/plans/PLAN-{timestamp}.md`

**Plan Structure:**
```markdown
# Plan: [Feature Name]

## Overview
[High-level description]

## Independent Tasks (Can Run Parallel)
- Task 1: [Description] (~X hours)
- Task 2: [Description] (~Y hours)
- Task 3: [Description] (~Z hours)

## Dependencies
- Task A must complete before Task B

## Shared Files/Resources
- [List any files multiple tasks might touch]

## Success Criteria
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Documentation updated
```

---

### **Phase 2: GitHub Issues Creation**

For each independent task, I create issues with safe label handling:

```bash
# Create issue and capture number
create_parallel_issue() {
    local title=$1
    local body=$2

    # Create issue without labels first (always works)
    local issue_url=$(gh issue create \
        --title "$title" \
        --body "$body" 2>&1)

    # Extract issue number
    local issue_num=$(echo "$issue_url" | grep -oE '[0-9]+$')

    # Try to add labels (fail gracefully if labels don't exist)
    for label in "parallel-execution" "auto-created"; do
        gh issue edit "$issue_num" --add-label "$label" 2>/dev/null || {
            echo "⚠️  Skipping label '$label' (doesn't exist)"
        }
    done

    echo "$issue_num"
}
```

**Issue Template Includes:**
- Link to plan document
- Implementation steps
- Success criteria
- Worktree path and branch name
- Task isolation boundaries
- Testing requirements

**Example Output:**
```
✅ Created Issue #123: Implement authentication
✅ Created Issue #124: Build dashboard UI
✅ Created Issue #125: Add analytics tracking
```

**Error Handling:**
- Labels added only if they exist (no failures)
- Graceful fallback if label creation was skipped
- Clear error messages with next steps

---

### **Phase 3: Git Worktree Creation**

```bash
# Create worktrees directory
mkdir -p worktrees

# For each GitHub issue, create worktree
git worktree add worktrees/task-123 -b feature/task-123
git worktree add worktrees/task-124 -b feature/task-124
git worktree add worktrees/task-125 -b feature/task-125

# Setup each environment
cd worktrees/task-123
cp ../../.env .env 2>/dev/null || true
npm install  # or: uv sync, cargo build, go mod download
cd ../..

# Verify worktrees created
git worktree list
```

**Directory Structure:**
```
project/
├── .git/                    # Shared git database
├── main-code/              # Your main workspace (this terminal)
└── worktrees/
    ├── task-123/           # Separate working directory
    │   ├── .git            # Link to shared .git
    │   └── [files]         # Branch: feature/task-123
    ├── task-124/
    └── task-125/
```

---

### **Phase 4: Spawning Parallel Agents** 🚀

**⚡ PRIMARY METHOD: Automated Subagent Spawning**

I will **automatically spawn subagents** to work on each worktree in parallel using the Task tool. This is the DEFAULT and RECOMMENDED approach.

**What Happens:**

1. **I spawn multiple subagents** - One for each independent task
2. **Each subagent works in its own worktree** - Isolated working directory
3. **All agents run in TRUE PARALLEL** - Simultaneously, not sequentially
4. **I monitor their progress** - Track completion and coordinate merges
5. **Agents report back when done** - With test results and status

**Example Execution:**

```
Me: "Spawning 4 parallel subagents for tasks..."

🚀 Agent 1: Working on Issue #1 (worktrees/mkdocs-config)
🚀 Agent 2: Working on Issue #2 (worktrees/plugin-config)
🚀 Agent 3: Working on Issue #3 (worktrees/license)
🚀 Agent 4: Working on Issue #4 (worktrees/commands)

⏳ All agents working in parallel...

✅ Agent 3 completed (3 minutes)
✅ Agent 2 completed (5 minutes)
✅ Agent 1 completed (10 minutes)
✅ Agent 4 completed (15 minutes)

All tasks complete! Ready to merge.
```

**What Each Subagent Does:**

Each subagent receives detailed instructions and works autonomously:

```
You are working on GitHub Issue #{issue-number}.

**Your Task:** {task description from issue}

**Working Directory:** worktrees/task-{issue-number}
**Branch:** feature/task-{issue-number}

**Your Job:**
1. Change to your worktree directory
2. Read the GitHub issue for full context
3. Implement the feature following the plan
4. Write tests and ensure they pass
5. Commit frequently with clear messages
6. When done, push branch and comment on GitHub issue

**Rules:**
- Stay in your worktree directory
- Don't modify files in other worktrees
- Flag any shared code concerns in GitHub issue
- Commit every logical change
- Test before pushing

**Success Criteria:**
{criteria from GitHub issue}

**When Complete:**
1. Run full test suite
2. Ensure all pass
3. Push: `git push origin feature/task-{issue-number}`
4. Comment on issue: "Implementation complete and tested"
```

---

### **Alternative: Manual Terminal Spawning** (Advanced)

If you prefer to spawn agents manually in separate terminals:

**Terminal 1 (Main - You're here):**
```bash
# Stay in main project directory
# Monitor progress and coordinate
```

**Terminal 2 (Task #123):**
```bash
cd worktrees/task-123
claude --continue

# Give instructions from agent instructions file
```

**Terminal 3 (Task #124):**
```bash
cd worktrees/task-124
claude --continue
```

**Note:** Manual spawning gives you more control but requires managing multiple terminal windows. The automated subagent approach is simpler and recommended for most cases.

---

### **Phase 5: Monitoring Progress** 👀

**In Main Terminal:**

```bash
# Check worktree status
git worktree list

# Check branch commits
git log --oneline --graph --all --decorate

# Check GitHub issues
gh issue list --label parallel-execution

# Watch specific worktree
cd worktrees/task-123 && git log --oneline
```

**Status Dashboard:**
```
┌─────────┬────────────────┬──────────┬─────────────┐
│ Issue   │ Task           │ Status   │ Progress    │
├─────────┼────────────────┼──────────┼─────────────┤
│ #123    │ Authentication │ Working  │ 3/5 steps   │
│ #124    │ Dashboard      │ Complete │ ✅ Pushed   │
│ #125    │ Analytics      │ Working  │ 2/3 steps   │
└─────────┴────────────────┴──────────┴─────────────┘
```

---

### **Phase 6: Merging Completed Work** ✅

When an agent completes their task:

**Pre-Merge Checklist:**
```bash
cd worktrees/task-124

# 1. All tests pass?
npm test  # or pytest, cargo test, etc.

# 2. Branch pushed?
git push origin feature/task-124

# 3. Issue updated?
gh issue view 124
```

**Merge Process:**
```bash
# Return to main project
cd ../../

# Switch to main branch
git checkout main

# Update from remote
git pull origin main

# Merge feature branch
git merge feature/task-124 --no-ff -m "feat: implement dashboard UI

Closes #124"

# Run integration tests
npm test

# Push to main
git push origin main

# Close GitHub issue
gh issue close 124 --comment "Merged in $(git rev-parse --short HEAD)"
```

**If Conflicts Occur:**
```bash
# View conflicts
git status

# Resolve manually or get my help
# Then:
git add .
git commit -m "resolve: merge conflicts from task-124"
git push origin main
```

---

### **Phase 7: Cleanup** 🧹

After successful merge, I automatically clean up:

**Per-Branch Cleanup:**
```bash
cleanup_after_merge() {
    local branch=$1
    local worktree_path=$2
    local remote_name=$3

    # 1. Remove worktree (force if needed)
    if [[ -d "$worktree_path" ]]; then
        git worktree remove "$worktree_path" --force 2>/dev/null
        echo "✅ Removed worktree: $worktree_path"
    fi

    # 2. Delete local branch
    git branch -d "$branch" 2>/dev/null || git branch -D "$branch"
    echo "✅ Deleted local branch: $branch"

    # 3. Delete remote branch (fail gracefully)
    git push "$remote_name" --delete "$branch" 2>/dev/null && \
        echo "✅ Deleted remote branch: $branch" || \
        echo "⚠️  Remote branch already deleted or not found"

    # 4. Prune worktrees
    git worktree prune
}
```

**Complete Cleanup (all tasks):**
```bash
cleanup_all_parallel_work() {
    local base_branch=${1:-master}
    local remote_name=${2:-origin}

    # Clean up all merged branches
    git branch --merged "$base_branch" | \
        grep -v "^\*" | \
        grep -v "^  $base_branch$" | \
        while read -r branch; do
            cleanup_after_merge "$branch" "worktrees/$branch" "$remote_name"
        done

    # Remove .parallel/ workspace (keep plans for reference)
    rm -rf .parallel/agent-instructions/
    rm -rf .parallel/logs/
    # Keep: .parallel/plans/ for future reference

    # Remove empty directories
    rmdir worktrees 2>/dev/null || true

    echo "✅ Cleanup complete"
}
```

**What Gets Cleaned:**
- ✅ All git worktrees
- ✅ All local branches (merged)
- ✅ All remote branches (merged)
- ✅ Agent instruction files
- ✅ Execution logs
- 📁 Plans kept for reference (in `.parallel/plans/`)

---

## 🎓 Best Practices

### **1. Task Independence**
- ✅ Different files/modules
- ✅ Separate features
- ⚠️ Shared code = coordinate in issues
- ❌ Same file edits = don't parallelize

### **2. Communication**
- Use GitHub issue comments
- Flag potential conflicts early
- Document decisions
- Ping main terminal if stuck

### **3. Commit Frequently**
```bash
# Good commits in worktrees:
git add src/auth/login.ts
git commit -m "feat(auth): add login validation"

git add src/auth/logout.ts  
git commit -m "feat(auth): add logout handler"

# Not this:
git add .
git commit -m "stuff"
```

### **4. Testing**
- Each agent tests in their worktree
- Main agent runs integration tests after merge
- Never merge failing tests

### **5. Resource Management**
- Limit to 3-5 parallel tasks
- Monitor disk space (each worktree = full copy)
- Clean up completed worktrees promptly

---

## 🔧 Project-Specific Setup

**Node.js/JavaScript:**
```bash
cd worktrees/task-123
npm install
cp ../../.env .env
npm run build
```

**Python:**
```bash
cd worktrees/task-123
uv sync
cp ../../.env .env
uv run pytest --collect-only
```

**Go:**
```bash
cd worktrees/task-123
go mod download
cp ../../.env .env
```

**Rust:**
```bash
cd worktrees/task-123
cargo build
cp ../../.env .env
```

---

## 🚨 Troubleshooting

### Common Errors and Solutions

**Error: "could not add label: 'parallel-execution' not found"**
```bash
# SOLUTION 1: Labels are created automatically in Phase 0
# If this still fails, you may lack repository permissions

# SOLUTION 2: Create labels manually
gh label create "parallel-execution" --color "0366d6" \
    --description "Task from parallel execution workflow"

gh label create "auto-created" --color "ededed" \
    --description "Automatically generated issue"

# SOLUTION 3: Skip labels (issues will still be created)
# The workflow continues even if labels fail
```

**Error: "fatal: 'origin' does not appear to be a git repository"**
```bash
# CAUSE: Remote is not named 'origin'

# SOLUTION 1: Check actual remote name
git remote -v

# SOLUTION 2: Use detected remote name
# I automatically detect the correct remote in Phase 0

# SOLUTION 3: Add origin remote if missing
git remote add origin <your-repo-url>
```

**Error: "nothing added to commit but untracked files present (.parallel/)"**
```bash
# CAUSE: .parallel/ directory not in .gitignore

# SOLUTION: Automatically handled in Phase 0
# I add .parallel/ to .gitignore before starting

# MANUAL FIX (if needed):
echo "" >> .gitignore
echo "# Parallel execution workspace" >> .gitignore
echo ".parallel/" >> .gitignore
git add .gitignore
git commit -m "chore: add .parallel/ to gitignore"
```

**Error: "Can't create worktree"**
```bash
# CAUSE: Uncommitted changes or worktree already exists

# SOLUTION 1: Commit changes first
git add .
git commit -m "wip: checkpoint before parallel work"

# SOLUTION 2: Remove existing worktree
git worktree remove worktrees/task-123 --force
git worktree prune

# SOLUTION 3: Stash changes
git stash push -m "temp: before parallel execution"
```

**Error: "GitHub CLI not authenticated"**
```bash
# SOLUTION: Authenticate with GitHub
gh auth login

# Follow the prompts to:
# 1. Select GitHub.com
# 2. Choose authentication method (browser or token)
# 3. Grant permissions

# Verify authentication
gh auth status
```

**Error: "Merge conflicts"**
```bash
# SOLUTION 1: Merge main into feature first (in worktree)
cd worktrees/task-123
git fetch origin
git merge origin/main
# Resolve conflicts
git add .
git commit -m "resolve: merge conflicts from main"
git push origin feature/task-123

# SOLUTION 2: Then merge feature into main
cd ../..
git checkout main
git pull origin main
git merge feature/task-123
# Should be clean now
```

**Error: "Worktree won't remove"**
```bash
# SOLUTION 1: Force remove
git worktree remove --force worktrees/task-123

# SOLUTION 2: Manual cleanup
rm -rf worktrees/task-123
git worktree prune

# SOLUTION 3: Unlock if locked
git worktree unlock worktrees/task-123
git worktree remove worktrees/task-123
```

**Error: "permission denied" when creating labels**
```bash
# CAUSE: Insufficient repository permissions

# SOLUTION: Issues will still be created without labels
# Only repository admins can create labels

# WORKAROUND: Ask repository admin to create labels:
# - parallel-execution (#0366d6)
# - auto-created (#ededed)
# - worktree (#fbca04)
```

### Debug Mode

If you encounter issues, enable verbose output:

```bash
# Enable bash debug mode
set -x

# Run commands and see exactly what's happening
git worktree add worktrees/test -b test-branch

# Disable debug mode
set +x
```

---

## 📊 Expected Workflow

**Example: 3 Features (4.5 hours sequential)**

**Sequential Development:**
- Auth: 2 hours
- Dashboard: 1.5 hours  
- Analytics: 1 hour
- **Total: 4.5 hours**

**Parallel Development:**
- All 3 start simultaneously
- All 3 complete in ~2 hours (longest task)
- **Total: 2 hours** (57% faster)

---

## 🎯 When to Use This

**✅ Good Use Cases:**
- Multiple independent features
- Frontend + Backend simultaneously
- Different modules/packages
- Experimental approaches (try 3 designs)

**❌ Don't Use For:**
- Dependent tasks (A needs B first)
- Same file modifications
- Database schema changes (use migrations)
- Small quick tasks (< 30 min)

---

## Global Availability

This command is available in **all projects** after installing the SlashSense plugin:

```bash
/plugin install slashsense
```

You can trigger it with:
- `/slashsense:parallel:execute` (explicit)
- Natural language: "work on these tasks in parallel", "parallelize this work"
- SlashSense will detect your intent automatically

---

## Related Commands

- `/slashsense:parallel:plan` - Create development plan
- `/slashsense:parallel:status` - Monitor progress
- `/slashsense:parallel:cleanup` - Clean up completed work

---

## 🚀 Ready to Execute?

Just run `/slashsense:parallel:execute` and Claude will:

1. **Analyze the plan** we discussed (or create one if needed)
2. **Create GitHub issues** for each independent task
3. **Set up git worktrees** for isolated development
4. **Spawn subagents automatically** to work in parallel
5. **Monitor progress** and coordinate completion
6. **Merge all branches** when done
7. **Clean up worktrees** and branches

**You don't need to:**
- Open multiple terminals
- Manually spawn agents
- Track which agent is working on what
- Coordinate merges manually

I handle everything automatically! Just provide the plan or let me create one based on our conversation.

---

## Example Command Flow

```
You: "/slashsense:parallel:execute - implement auth, dashboard, and analytics"

Or naturally: "work on auth, dashboard, and analytics in parallel"

Claude:
"📋 Analyzing plan...

**Found 3 independent tasks:**
1. Authentication system (2h)
2. Dashboard UI (1.5h)
3. Analytics tracking (1h)

**Step 1:** Creating plan document...
✅ Created: .parallel/plans/PLAN-20251014-153000.md

**Step 2:** Creating GitHub issues...
✅ Issue #123: Implement authentication
✅ Issue #124: Build dashboard UI
✅ Issue #125: Add analytics tracking

**Step 3:** Creating worktrees...
✅ worktrees/task-123 (feature/task-123)
✅ worktrees/task-124 (feature/task-124)
✅ worktrees/task-125 (feature/task-125)

**Step 4:** Spawning 3 parallel subagents...
🚀 Agent 1: Working on Issue #123 (authentication)
🚀 Agent 2: Working on Issue #124 (dashboard)
🚀 Agent 3: Working on Issue #125 (analytics)

⏳ All agents working in parallel...

✅ Agent 2 completed (1.5h) - Dashboard UI ready
✅ Agent 3 completed (1.8h) - Analytics tracking ready
✅ Agent 1 completed (2h) - Authentication ready

**All tasks complete in 2 hours (vs 4.5h sequential - 56% faster!)**

Ready to merge all branches?"
```