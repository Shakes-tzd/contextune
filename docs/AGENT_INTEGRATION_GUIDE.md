# Agent Integration Guide

**Version:** 1.0
**Last Updated:** 2025-10-21
**Target Audience:** Developers integrating Haiku agents with Contextune parallel workflows

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use Haiku vs Sonnet](#when-to-use-haiku-vs-sonnet)
3. [Agent Communication Patterns](#agent-communication-patterns)
4. [Data Exchange Between Agents](#data-exchange-between-agents)
5. [Error Handling and Reporting](#error-handling-and-reporting)
6. [Cost Tracking and Optimization](#cost-tracking-and-optimization)
7. [Agent Coordination Examples](#agent-coordination-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Agent Integration?

Agent integration in Contextune refers to the coordination between:

1. **Main Agent (Sonnet 4.5)**: Your primary Claude Code conversation
2. **Haiku Agents**: Specialized, cost-optimized execution agents
3. **Skills**: Educational, guidance-focused modules running in main context

### Architecture at a Glance

```
User Request
    ↓
Main Agent (Sonnet)
├─ Analyzes intent
├─ Plans decomposition
└─ Delegates to agents
    ↓
Haiku Agents (Parallel)
├─ Execute independently
├─ Report completion
└─ Handle errors autonomously
    ↓
Results Consolidated
    ↓
User Feedback
```

### Why This Matters

**Without proper integration:**
- Agents work in silos
- Communication overhead increases
- Error propagation is unclear
- Cost tracking is impossible
- User experience suffers

**With proper integration:**
- Seamless coordination
- Clear responsibility boundaries
- Efficient error handling
- Transparent cost tracking
- Delightful user experience

---

## When to Use Haiku vs Sonnet

### Decision Matrix

| Factor | Use Haiku | Use Sonnet |
|--------|-----------|------------|
| **Task Complexity** | Low - well-defined | High - requires reasoning |
| **Repetition** | Repetitive operations | One-off creative tasks |
| **Decision Making** | Simple if/else | Complex judgment calls |
| **Context Needed** | Minimal (task-specific) | Extensive (project-wide) |
| **Cost Sensitivity** | High (many operations) | Low (few operations) |
| **Speed Priority** | Critical (user waiting) | Not critical |
| **Error Tolerance** | Must be reliable | Can iterate and refine |

### Task Type Classification

#### Perfect for Haiku

**Execution Tasks:**
```yaml
git_operations:
  - Create worktree
  - Switch branches
  - Commit changes
  - Push to remote
  - Clean up worktrees

test_operations:
  - Run unit tests
  - Run integration tests
  - Collect coverage
  - Generate reports
  - Benchmark performance

file_operations:
  - Read files
  - Write boilerplate
  - Update configuration
  - Format code
  - Search and replace

issue_management:
  - Create issues from templates
  - Update issue status
  - Add labels
  - Link to PRs
  - Close issues
```

**Why Haiku works:**
- Operations follow clear steps
- Templates provide structure
- Minimal decision-making required
- Cost-sensitive due to high frequency
- Speed critical for user experience

#### Requires Sonnet

**Planning & Reasoning Tasks:**
```yaml
complex_decisions:
  - Architecture design choices
  - Conflict resolution strategies
  - Security vulnerability assessment
  - Performance optimization planning
  - Code refactoring approach

creative_work:
  - API design
  - User experience flows
  - Error message composition
  - Documentation writing
  - Test strategy planning

analysis_work:
  - Code review
  - Dependency analysis
  - Breaking change assessment
  - Migration path planning
  - Risk evaluation
```

**Why Sonnet required:**
- No clear template to follow
- Requires project-wide context
- Multiple trade-offs to balance
- Creative problem-solving needed
- Judgment calls at each step

### Practical Examples

#### Example 1: Feature Implementation

**Task:** "Add user logout functionality"

**Breakdown:**
```
Sonnet (Main Agent):
├─ Analyze requirements (5 mins)
├─ Design logout flow (10 mins)
├─ Identify affected files (5 mins)
└─ Create execution plan (5 mins)
    ↓
Haiku Agent (parallel-task-executor):
├─ Create GitHub issue (5s)
├─ Create worktree (5s)
├─ Implement logout button (2 mins)
├─ Add logout handler (2 mins)
├─ Write tests (3 mins)
├─ Run tests (30s)
└─ Push and report (10s)

Cost:
- Sonnet planning: ~$0.03
- Haiku execution: ~$0.04
Total: $0.07 (vs $0.30 if all Sonnet)
Savings: 77%
```

#### Example 2: Bug Fix

**Task:** "Fix authentication redirect loop"

**Breakdown:**
```
Sonnet (Main Agent):
├─ Analyze bug report (5 mins)
├─ Reproduce issue (10 mins)
├─ Identify root cause (15 mins)
├─ Design fix approach (10 mins)
└─ Create fix plan (5 mins)
    ↓
Haiku Agent (parallel-task-executor):
├─ Create GitHub issue (5s)
├─ Create worktree (5s)
├─ Apply fix (1 min)
├─ Add test for regression (2 mins)
├─ Run all tests (45s)
└─ Push and report (10s)

Cost:
- Sonnet investigation: ~$0.12
- Haiku execution: ~$0.04
Total: $0.16 (vs $0.42 if all Sonnet)
Savings: 62%
```

#### Example 3: Parallel Feature Development

**Task:** "Implement auth, dashboard, and analytics pages"

**Breakdown:**
```
Sonnet (Main Agent):
├─ Validate task independence (5 mins)
├─ Create parallel plan (10 mins)
└─ Spawn 3 Haiku agents (instant)
    ↓
Haiku Agent 1 (auth page):
├─ Create issue + worktree
├─ Implement auth page
├─ Test and push
└─ Report completion
    ↓
Haiku Agent 2 (dashboard):
├─ Create issue + worktree
├─ Implement dashboard
├─ Test and push
└─ Report completion
    ↓
Haiku Agent 3 (analytics):
├─ Create issue + worktree
├─ Implement analytics
├─ Test and push
└─ Report completion
    ↓
Sonnet (Main Agent):
└─ Review and coordinate merge

Cost:
- Sonnet planning: ~$0.03
- 3 Haiku agents: 3 × $0.04 = $0.12
- Sonnet review: ~$0.02
Total: $0.17 (vs $0.87 if all Sonnet)
Savings: 80%
```

---

## Agent Communication Patterns

### Pattern 1: Request-Response (Synchronous)

**Use case:** Main agent needs immediate result from subagent

```
Main Agent (Sonnet)
    ↓ Request with full context
Haiku Agent
    ↓ Execute task
    ↓ Return result immediately
Main Agent (Sonnet)
    ↓ Continue with result
```

**Implementation:**

```markdown
# Main Agent (Sonnet)
I need to create a GitHub issue for this task. Let me delegate to the issue-orchestrator agent.

**Agent Request:**
{
  "agent": "issue-orchestrator",
  "task": "create_issue",
  "params": {
    "title": "Implement logout button",
    "body": "Add logout button to navigation...",
    "labels": ["feature", "auth"]
  }
}

**Expected Response:**
{
  "success": true,
  "issue_number": 123,
  "issue_url": "https://github.com/..."
}
```

**Haiku Agent Response:**

```markdown
✅ Issue created successfully!

**Issue Number:** #123
**URL:** https://github.com/user/repo/issues/123
**Labels:** feature, auth
**Cost:** $0.01
```

### Pattern 2: Fire-and-Forget (Asynchronous)

**Use case:** Parallel execution where main agent doesn't wait

```
Main Agent (Sonnet)
    ↓ Spawn 3 agents with tasks
    ├─ Haiku Agent 1 (executes independently)
    ├─ Haiku Agent 2 (executes independently)
    └─ Haiku Agent 3 (executes independently)
    ↓ (doesn't wait)
Main Agent (Sonnet)
    ↓ Continues with other work

(Later...)
Agents report completion asynchronously
```

**Implementation:**

```markdown
# Main Agent (Sonnet)
I'm spawning 3 parallel agents for independent tasks:

**Agent 1 (parallel-task-executor):**
- Task: Implement auth page
- Issue: Will create #TBD
- Worktree: Will create worktrees/task-TBD

**Agent 2 (parallel-task-executor):**
- Task: Implement dashboard page
- Issue: Will create #TBD
- Worktree: Will create worktrees/task-TBD

**Agent 3 (parallel-task-executor):**
- Task: Implement analytics page
- Issue: Will create #TBD
- Worktree: Will create worktrees/task-TBD

All agents will report completion independently.
```

**Haiku Agent 1 (later):**

```markdown
✅ Task Completed Successfully!

**Task:** Implement auth page
**Issue:** #124
**Branch:** feature/task-124
**Status:** All tests passing, ready to merge
**Cost:** $0.04
```

### Pattern 3: Streaming Progress (Real-time)

**Use case:** Long-running tasks where user wants updates

```
Main Agent (Sonnet)
    ↓ Start long task
Haiku Agent
    ↓ Progress update 1 (25%)
Main Agent (Sonnet)
    ↓ Show to user
Haiku Agent
    ↓ Progress update 2 (50%)
Main Agent (Sonnet)
    ↓ Show to user
Haiku Agent
    ↓ Progress update 3 (75%)
Main Agent (Sonnet)
    ↓ Show to user
Haiku Agent
    ↓ Completion (100%)
Main Agent (Sonnet)
    ↓ Final report to user
```

**Implementation:**

```markdown
# Haiku Agent (test-runner)

Starting test suite execution...

**Progress Update (25%):**
✅ Unit tests: 45/45 passing (2.3s)
⏳ Integration tests: Running...

**Progress Update (50%):**
✅ Unit tests: 45/45 passing
✅ Integration tests: 12/12 passing (15.7s)
⏳ E2E tests: Running...

**Progress Update (75%):**
✅ Unit tests: 45/45 passing
✅ Integration tests: 12/12 passing
✅ E2E tests: 8/10 passing
❌ 2 failures detected

**Final Report (100%):**
⚠️ Test suite completed with 2 failures
- auth-flow.spec.ts: Timeout on login redirect
- dashboard.spec.ts: Element not found error

Created issues: #125, #126
**Cost:** $0.03
```

### Pattern 4: Callback Chain (Sequential)

**Use case:** Tasks with dependencies

```
Main Agent (Sonnet)
    ↓ Task 1 request
Haiku Agent A
    ↓ Complete task 1
    ↓ Return result
Main Agent (Sonnet)
    ↓ Task 2 request (uses result from 1)
Haiku Agent B
    ↓ Complete task 2
    ↓ Return result
Main Agent (Sonnet)
    ↓ Task 3 request (uses results from 1 & 2)
Haiku Agent C
    ↓ Complete task 3
    ↓ Final result
```

**Implementation:**

```markdown
# Main Agent (Sonnet)

Step 1: Create worktree
→ Agent: worktree-manager
→ Result: worktrees/task-123 created

Step 2: Run tests
→ Agent: test-runner
→ Input: worktree path from Step 1
→ Result: All tests passing

Step 3: Deploy
→ Agent: parallel-task-executor
→ Input: worktree path + test results
→ Result: Deployed successfully

Total cost: $0.03 + $0.03 + $0.04 = $0.10
```

---

## Data Exchange Between Agents

### JSON-Based Contract

**Standard message format:**

```json
{
  "version": "1.0",
  "timestamp": "2025-10-21T10:30:00Z",
  "sender": "main-agent",
  "receiver": "parallel-task-executor",
  "message_type": "task_request",
  "correlation_id": "req-12345",
  "payload": {
    "task": {
      "title": "Implement logout button",
      "description": "Add logout functionality to navigation",
      "files": ["src/components/Navigation.tsx"],
      "tests": ["src/components/Navigation.test.tsx"],
      "success_criteria": "Logout button visible and functional"
    },
    "context": {
      "project_type": "react-typescript",
      "test_command": "npm test",
      "lint_command": "npm run lint"
    }
  }
}
```

**Standard response format:**

```json
{
  "version": "1.0",
  "timestamp": "2025-10-21T10:35:00Z",
  "sender": "parallel-task-executor",
  "receiver": "main-agent",
  "message_type": "task_completion",
  "correlation_id": "req-12345",
  "status": "success",
  "payload": {
    "issue_number": 123,
    "issue_url": "https://github.com/user/repo/issues/123",
    "branch": "feature/task-123",
    "worktree": "worktrees/task-123",
    "commits": 3,
    "tests_passing": true,
    "files_changed": [
      "src/components/Navigation.tsx",
      "src/components/Navigation.test.tsx"
    ]
  },
  "metrics": {
    "duration_seconds": 180,
    "cost_usd": 0.04,
    "tokens_used": 35000
  }
}
```

### Passing Complex Data Structures

#### Example: Task Plan

```yaml
# Main Agent creates detailed plan

task_plan:
  id: "plan-001"
  tasks:
    - id: "task-1"
      title: "Implement auth page"
      type: "feature"
      priority: "high"
      dependencies: []
      files:
        - path: "src/pages/Auth.tsx"
          operation: "create"
          template: "react-page"
        - path: "src/pages/Auth.test.tsx"
          operation: "create"
          template: "react-test"
      implementation_steps:
        - "Create Auth page component"
        - "Add login form with email/password"
        - "Add form validation"
        - "Connect to auth API"
        - "Add error handling"
        - "Add loading states"
      tests:
        - "Form renders correctly"
        - "Validation works"
        - "Successful login redirects"
        - "Failed login shows error"

    - id: "task-2"
      title: "Implement dashboard"
      type: "feature"
      priority: "high"
      dependencies: ["task-1"]  # Depends on auth!
      files:
        - path: "src/pages/Dashboard.tsx"
          operation: "create"
          template: "react-page"
      implementation_steps:
        - "Create Dashboard component"
        - "Fetch user data"
        - "Display user stats"
      tests:
        - "Protected route works"
        - "Data loads correctly"

  metadata:
    created_by: "main-agent"
    created_at: "2025-10-21T10:00:00Z"
    estimated_cost: "$0.12"
    estimated_duration: "30 minutes"
```

**Haiku agent receives simplified subset:**

```yaml
# Agent gets only what it needs

assigned_task:
  id: "task-1"
  title: "Implement auth page"
  files:
    - src/pages/Auth.tsx
    - src/pages/Auth.test.tsx
  steps:
    - "Create Auth page component"
    - "Add login form with email/password"
    - "Add form validation"
    - "Connect to auth API"
    - "Add error handling"
    - "Add loading states"
  tests:
    - "Form renders correctly"
    - "Validation works"
    - "Successful login redirects"
    - "Failed login shows error"
  context:
    test_command: "npm test"
    lint_command: "npm run lint"
```

### Environment Variables

**Passing configuration:**

```bash
# Main agent sets environment for Haiku agents

export TASK_ID="task-123"
export ISSUE_NUMBER="123"
export WORKTREE_PATH="worktrees/task-123"
export BRANCH_NAME="feature/task-123"
export PROJECT_TYPE="react-typescript"
export TEST_COMMAND="npm test"
export LINT_COMMAND="npm run lint"
export MAIN_BRANCH="main"

# Haiku agent reads environment

TASK_ID="${TASK_ID}"
ISSUE_NUMBER="${ISSUE_NUMBER}"
# ... etc
```

### File-Based Communication

**For large data transfers:**

```bash
# Main agent writes plan to file

cat > /tmp/task-plan-123.json <<'EOF'
{
  "task_id": "task-123",
  "title": "Implement logout",
  "files": [...],
  "steps": [...]
}
EOF

# Pass file path to Haiku agent
export TASK_PLAN_FILE="/tmp/task-plan-123.json"

# Haiku agent reads plan
PLAN=$(cat "$TASK_PLAN_FILE")
```

**For streaming logs:**

```bash
# Haiku agent writes progress to log file

exec 1> >(tee -a /tmp/agent-123.log)
exec 2>&1

echo "Starting task execution..."
echo "Step 1: Creating worktree..."
echo "Step 2: Installing dependencies..."
# ... etc

# Main agent monitors progress

tail -f /tmp/agent-123.log
```

---

## Error Handling and Reporting

### Error Classification

```yaml
error_types:
  recoverable:
    - Network timeout (retry)
    - File lock (wait and retry)
    - Dependency installation failure (retry with cache clear)
    - Test flakiness (retry once)

  non_recoverable:
    - Syntax errors in code
    - Missing required files
    - Test failures (actual bugs)
    - Git merge conflicts

  escalation_required:
    - Architecture decisions needed
    - Ambiguous requirements
    - Security vulnerabilities
    - Breaking changes
```

### Error Handling Strategy

#### Haiku Agent Autonomy

```yaml
haiku_agent_handles:
  automatic_retry:
    - Network errors (3 attempts)
    - Temporary file locks (wait up to 30s)
    - Flaky tests (1 retry)

  graceful_degradation:
    - Optional features fail → continue
    - Non-critical tests fail → warn and continue
    - Linting warnings → report but don't block

  clear_reporting:
    - Document error in GitHub issue
    - Include full error message
    - Provide context (what was being attempted)
    - Suggest next steps
```

**Example: Network Error Handling**

```bash
# Haiku agent script

retry_count=0
max_retries=3

while [ $retry_count -lt $max_retries ]; do
  if npm install; then
    echo "✅ Dependencies installed successfully"
    break
  else
    retry_count=$((retry_count + 1))
    echo "⚠️ Attempt $retry_count failed, retrying..."
    sleep $((retry_count * 2))  # Exponential backoff
  fi
done

if [ $retry_count -eq $max_retries ]; then
  echo "❌ Failed to install dependencies after $max_retries attempts"
  gh issue comment $ISSUE_NUMBER --body "⚠️ Environment setup failed. Network error during npm install. Manual intervention required."
  exit 1
fi
```

#### Escalation to Main Agent

**When Haiku agent can't proceed:**

```markdown
# Haiku Agent Report

❌ **Task Blocked: Requires Human Decision**

**Task:** Implement logout button
**Issue:** #123
**Blocker:** Test failure in authentication flow

**Error Details:**
```
FAIL src/auth/Login.test.tsx
  ● Login flow › redirects after successful login

    Expected redirect to "/dashboard"
    Received redirect to "/login"

    at Object.<anonymous> (src/auth/Login.test.tsx:45:23)
```

**Context:**
- This test was passing before my changes
- I only modified Navigation.tsx to add logout button
- Possible regression in auth flow logic

**Options:**
1. Investigate auth flow (requires understanding of auth architecture)
2. Update test expectations (requires knowing intended behavior)
3. Revert changes (safe but doesn't solve problem)

**Recommendation:** Main agent should investigate as this requires project-wide context.

**Cost so far:** $0.02
```

### Error Reporting Format

**Standard error report:**

```json
{
  "error_report": {
    "severity": "critical|high|medium|low",
    "type": "test_failure|build_error|dependency_error|git_error",
    "task_id": "task-123",
    "agent_id": "parallel-task-executor-1",
    "timestamp": "2025-10-21T10:45:00Z",

    "error": {
      "message": "Test suite failed with 2 errors",
      "code": "TEST_FAILURE",
      "details": "...",
      "stack_trace": "..."
    },

    "context": {
      "operation": "Running test suite",
      "command": "npm test",
      "working_directory": "worktrees/task-123",
      "environment": {
        "node_version": "18.17.0",
        "npm_version": "9.8.1"
      }
    },

    "attempted_solutions": [
      "Retried tests once (still failed)",
      "Cleared npm cache (no effect)",
      "Checked for flaky tests (errors consistent)"
    ],

    "next_steps": {
      "requires_escalation": true,
      "reason": "Test failures indicate actual bugs, not transient errors",
      "suggested_action": "Main agent should review test failures and determine fix approach"
    },

    "artifacts": {
      "github_issue": "https://github.com/user/repo/issues/123",
      "log_file": "/tmp/agent-123.log",
      "test_report": "/tmp/test-report-123.html"
    }
  }
}
```

---

## Cost Tracking and Optimization

### Cost Attribution

**Track cost per agent:**

```yaml
agent_costs:
  main_agent:
    model: "sonnet-4.5"
    input_tokens: 10000
    output_tokens: 2000
    cost_usd: 0.06

  haiku_agent_1:
    model: "haiku-4.5"
    task: "Implement auth page"
    input_tokens: 30000
    output_tokens: 5000
    cost_usd: 0.044

  haiku_agent_2:
    model: "haiku-4.5"
    task: "Implement dashboard"
    input_tokens: 32000
    output_tokens: 5500
    cost_usd: 0.048

  total_cost: 0.152

  comparison:
    if_all_sonnet: 0.78
    savings_usd: 0.628
    savings_percent: 80.5
```

### Real-Time Cost Monitoring

**Show cost to user during execution:**

```markdown
# Main Agent Progress Report

🚀 **Parallel Execution in Progress**

**Tasks:**
- ✅ Auth page (Haiku) - Complete - $0.04
- ⏳ Dashboard (Haiku) - Running - $0.02 so far
- ⏳ Analytics (Haiku) - Running - $0.01 so far

**Running Cost:** $0.07
**Estimated Total:** $0.12
**Estimated Savings:** $0.66 (85%) vs all-Sonnet approach

**Time Elapsed:** 2 minutes
**Estimated Time Remaining:** 3 minutes
```

### Cost Optimization Techniques

#### 1. Prompt Compression

**Before (verbose):**
```
Your task is to implement a logout button in the navigation component.
This button should be placed in the top-right corner of the navigation bar,
next to the user profile icon. When clicked, it should call the logout
function from the auth context, which will clear the user's session and
redirect them to the login page. Please ensure that you add appropriate
tests for this functionality, including tests for the button rendering,
the click handler, and the logout function being called correctly.
```
**Tokens:** ~120

**After (compressed):**
```
Task: Add logout button to Navigation.tsx
- Position: top-right, next to profile icon
- Click handler: calls auth context logout()
- Tests: rendering, click handler, logout call
```
**Tokens:** ~35
**Savings:** 71%

#### 2. Template Reuse

**Create reusable task templates:**

```yaml
# Template: feature-implementation.yaml

task_template:
  title: "{feature_name}"
  type: "feature"
  steps:
    - "Read existing code"
    - "Implement {feature_name}"
    - "Add tests"
    - "Run test suite"
    - "Push changes"
  tests:
    - "Feature works as expected"
    - "No regressions"
  success_criteria: "All tests passing"
```

**Use template (low token cost):**

```yaml
task:
  template: "feature-implementation"
  variables:
    feature_name: "logout button"
```

**Tokens saved:** ~80% vs full task description

#### 3. Selective Context

**Don't send unnecessary context:**

```yaml
# Bad: Send entire codebase
context:
  all_files: "..." # 50K tokens!

# Good: Send only relevant files
context:
  files:
    - src/components/Navigation.tsx  # 500 tokens
    - src/auth/AuthContext.tsx       # 300 tokens
  total: 800 tokens

savings: 49.2K tokens = ~$0.15
```

#### 4. Batch Operations

**Group related tasks:**

```yaml
# Bad: 5 separate agent calls
- Create issue for task 1    # $0.01
- Create issue for task 2    # $0.01
- Create issue for task 3    # $0.01
- Create issue for task 4    # $0.01
- Create issue for task 5    # $0.01
total: $0.05

# Good: Batch issue creation
- Create 5 issues in one call  # $0.02
savings: $0.03 (60%)
```

---

## Agent Coordination Examples

### Example 1: Simple Task Delegation

**Scenario:** Main agent delegates test execution to Haiku agent

```markdown
# Main Agent (Sonnet)

I need to run the test suite. Let me delegate to the test-runner agent.

**Delegation:**
- Agent: test-runner (Haiku)
- Task: Run full test suite
- Context: All tests should be passing after recent changes
- Expected: Test report with pass/fail status

---

# Haiku Agent (test-runner)

Starting test execution...

**Test Suite Results:**
✅ Unit tests: 45/45 passing (2.3s)
✅ Integration tests: 12/12 passing (15.7s)
✅ E2E tests: 10/10 passing (42.1s)

**Coverage:**
- Statements: 87.3%
- Branches: 82.1%
- Functions: 91.2%
- Lines: 86.9%

**Total Duration:** 60.1s
**Cost:** $0.03

All tests passing! ✅

---

# Main Agent (Sonnet)

Excellent! All tests passing. I can now proceed with deployment.

**Total cost for this operation:**
- Main agent coordination: $0.01
- Haiku test execution: $0.03
- Total: $0.04 (vs $0.12 if all Sonnet)
- Savings: 67%
```

### Example 2: Parallel Task Execution

**Scenario:** Three independent features developed in parallel

```markdown
# Main Agent (Sonnet)

User requested: "Work on auth, dashboard, and analytics in parallel"

**Analysis:**
- All three tasks are independent (no shared files)
- Can be executed in parallel safely
- Each task well-defined

**Parallel Execution Plan:**

Task 1: Auth Page
- Files: src/pages/Auth.tsx, src/pages/Auth.test.tsx
- Agent: parallel-task-executor-1 (Haiku)
- Estimated: $0.04, 15 mins

Task 2: Dashboard Page
- Files: src/pages/Dashboard.tsx, src/pages/Dashboard.test.tsx
- Agent: parallel-task-executor-2 (Haiku)
- Estimated: $0.04, 12 mins

Task 3: Analytics Page
- Files: src/pages/Analytics.tsx, src/pages/Analytics.test.tsx
- Agent: parallel-task-executor-3 (Haiku)
- Estimated: $0.04, 18 mins

**Total Estimated Cost:** $0.15 (vs $0.78 if all Sonnet)
**Total Time:** 18 mins (vs 45 mins sequential)

Spawning agents...

---

# Haiku Agent 1 (auth page)

✅ Task Started: Implement auth page
- Created issue #124
- Created worktree: worktrees/task-124
- Installing dependencies...
- Implementing auth page...
- Adding tests...
- Running tests: ✅ All passing
- Pushing changes...
- ✅ Complete! Cost: $0.04

---

# Haiku Agent 2 (dashboard)

✅ Task Started: Implement dashboard page
- Created issue #125
- Created worktree: worktrees/task-125
- Installing dependencies...
- Implementing dashboard...
- Adding tests...
- Running tests: ✅ All passing
- Pushing changes...
- ✅ Complete! Cost: $0.04

---

# Haiku Agent 3 (analytics)

✅ Task Started: Implement analytics page
- Created issue #126
- Created worktree: worktrees/task-126
- Installing dependencies...
- Implementing analytics...
- Adding tests...
- Running tests: ✅ All passing
- Pushing changes...
- ✅ Complete! Cost: $0.04

---

# Main Agent (Sonnet)

All three tasks completed successfully!

**Results Summary:**
- ✅ Auth page: Issue #124, branch feature/task-124
- ✅ Dashboard: Issue #125, branch feature/task-125
- ✅ Analytics: Issue #126, branch feature/task-126

**All tests passing, ready to merge!**

**Final Costs:**
- Planning: $0.03
- 3 × Haiku agents: $0.12
- Review: $0.02
- **Total: $0.17** (vs $0.87 if all Sonnet)
- **Savings: $0.70 (80%)**

**Time:**
- Sequential: ~45 minutes
- Parallel: ~18 minutes
- **Time saved: 27 minutes (60%)**
```

### Example 3: Error Handling and Recovery

**Scenario:** Agent encounters test failure and escalates

```markdown
# Main Agent (Sonnet)

Delegating logout feature implementation to Haiku agent.

**Task:** Add logout button
**Agent:** parallel-task-executor (Haiku)
**Expected:** Complete implementation with tests

---

# Haiku Agent (parallel-task-executor)

Starting task: Add logout button

✅ Created issue #127
✅ Created worktree: worktrees/task-127
✅ Implemented logout button
✅ Added tests
⏳ Running tests...

❌ **Test Failure Detected**

```
FAIL src/components/Navigation.test.tsx
  ● Navigation › logout button › calls logout on click

    Expected: logout function called once
    Received: logout function called 0 times
```

**Analysis:**
- Test expects logout to be called
- Button click not triggering logout
- Possible issue: onClick handler not connected

**Attempted Fix:**
- Verified onClick handler is present
- Checked auth context is imported
- Confirmed logout function exists

**Still Failing After Fix Attempt**

This requires deeper investigation into auth context behavior.

**Escalating to main agent for guidance.**

**Cost so far:** $0.02

---

# Main Agent (Sonnet)

Received escalation from Haiku agent. Analyzing test failure...

**Root Cause Analysis:**
- Auth context uses a custom hook: useAuth()
- Hook must be wrapped in AuthProvider for tests
- Haiku agent's test is missing the provider wrapper

**Solution:**
Update test to wrap component in AuthProvider:

```tsx
<AuthProvider>
  <Navigation />
</AuthProvider>
```

**Sending fix guidance back to Haiku agent...**

---

# Haiku Agent (parallel-task-executor)

Received guidance from main agent. Applying fix...

✅ Updated test with AuthProvider wrapper
⏳ Running tests again...
✅ All tests passing!

Completing task...
✅ Pushed changes
✅ Updated issue #127

**Task Complete!**
**Total Cost:** $0.04 (including escalation)

---

# Main Agent (Sonnet)

Excellent! Problem solved with minimal additional cost.

**Breakdown:**
- Haiku initial attempt: $0.02
- Escalation + analysis: $0.01
- Haiku fix application: $0.01
- **Total: $0.04**

**This demonstrates:**
- Haiku handles standard execution well
- Escalates when encountering unknowns
- Main agent provides targeted guidance
- Haiku applies fix successfully
- Total cost still significantly lower than full Sonnet execution
```

---

## Best Practices

### 1. Clear Responsibility Boundaries

```yaml
main_agent_responsibilities:
  - High-level planning
  - Complex decision-making
  - Conflict resolution
  - User communication
  - Quality assurance review

haiku_agent_responsibilities:
  - Task execution
  - Test running
  - Issue creation/updates
  - Git operations
  - Progress reporting

never_overlap:
  - Each agent owns its domain
  - Clear handoff points
  - Explicit delegation
  - Unambiguous success criteria
```

### 2. Minimize Context Transfer

```yaml
good_delegation:
  task: "Add logout button to Navigation.tsx"
  files: ["src/components/Navigation.tsx"]
  steps:
    - "Add button JSX"
    - "Add onClick handler"
    - "Call logout from auth context"
  tests: ["Button renders", "onClick calls logout"]

bad_delegation:
  task: "Add logout functionality"
  context: "Here's the entire codebase..." # 50K tokens!
  instructions: "Figure out where to add it..." # Vague!
```

### 3. Validate Before Delegating

```markdown
# Main Agent Validation Checklist

Before delegating to Haiku agent:

✅ Task is well-defined
✅ Files to modify are identified
✅ Success criteria are clear
✅ Tests are specified
✅ No complex decisions required
✅ No dependencies on other tasks
✅ Environment is set up correctly

If any checkbox is unchecked:
→ Don't delegate yet
→ Resolve ambiguities first
→ Ensure Haiku has everything needed
```

### 4. Monitor and Intervene Early

```yaml
monitoring_strategy:
  checkpoints:
    - After environment setup
    - After initial implementation
    - After test execution
    - Before final push

  intervention_triggers:
    - Tests failing for >5 minutes
    - Agent stuck on same operation
    - Repeated error messages
    - Unexpected file modifications

  intervention_actions:
    - Pause agent
    - Analyze situation
    - Provide targeted guidance
    - Resume or reassign
```

### 5. Cost-Aware Delegation

```yaml
cost_optimization_rules:

  use_haiku_when:
    - Task is repetitive
    - Steps are well-defined
    - Context is minimal
    - Speed is critical
    - Operation runs frequently

  use_sonnet_when:
    - Task is one-off
    - Requires creativity
    - Context is extensive
    - Judgment needed
    - Cost is negligible

  never_sacrifice_quality:
    - Don't use Haiku for complex reasoning
    - Don't compress context beyond clarity
    - Don't skip validation to save cost
    - Quality > Cost savings
```

---

## Troubleshooting

### Issue: Haiku Agent Gets Stuck

**Symptoms:**
- No progress updates for >5 minutes
- Agent appears to be looping
- Repeated error messages

**Diagnosis:**

```bash
# Check agent logs
tail -f /tmp/agent-{task-id}.log

# Check git status in worktree
cd worktrees/task-{id}
git status

# Check running processes
ps aux | grep "task-{id}"
```

**Solutions:**

1. **Environment issue:**
   ```bash
   # Kill stuck process
   pkill -f "task-{id}"

   # Clean up worktree
   git worktree remove --force worktrees/task-{id}

   # Restart agent with fresh environment
   ```

2. **Dependency issue:**
   ```bash
   # Clear npm cache (if Node.js)
   npm cache clean --force

   # Re-sync dependencies (if Python/UV)
   uv sync --reinstall
   ```

3. **Logic issue:**
   - Main agent should review task definition
   - Simplify steps
   - Provide more explicit instructions
   - Consider doing this task with Sonnet instead

### Issue: Cost Higher Than Expected

**Diagnosis:**

```bash
# Check token usage
grep "tokens_used" /tmp/agent-*.log | awk '{sum+=$2} END {print sum}'

# Check number of retries
grep "retry" /tmp/agent-*.log | wc -l

# Check context size
grep "context_tokens" /tmp/agent-*.log
```

**Common Causes:**

1. **Too much context:**
   - Solution: Reduce context to only essential files

2. **Too many retries:**
   - Solution: Fail fast and escalate sooner

3. **Verbose output:**
   - Solution: Use structured logging, reduce chatter

4. **Wrong model selected:**
   - Solution: Ensure Haiku is being used for execution

### Issue: Tests Failing Intermittently

**Symptoms:**
- Tests pass locally, fail in agent
- Tests pass sometimes, fail other times
- Different failures each run

**Diagnosis:**

```bash
# Run tests multiple times
for i in {1..10}; do npm test; done

# Check for race conditions
npm test -- --runInBand

# Check for environment differences
diff .env .env.example
```

**Solutions:**

1. **Flaky tests:**
   - Add retries to agent script
   - Fix tests to be deterministic
   - Increase timeouts

2. **Environment differences:**
   - Ensure .env files are copied
   - Verify environment variables
   - Check dependency versions

3. **Timing issues:**
   - Add delays where needed
   - Use proper async/await
   - Increase test timeouts

### Issue: Agent Can't Create GitHub Issue

**Symptoms:**
- "gh: command not found"
- "Authentication failed"
- "API rate limit exceeded"

**Diagnosis:**

```bash
# Check gh CLI installed
which gh

# Check gh authentication
gh auth status

# Check API rate limit
gh api rate_limit
```

**Solutions:**

1. **gh not installed:**
   ```bash
   brew install gh  # macOS
   # or
   sudo apt install gh  # Linux
   ```

2. **Not authenticated:**
   ```bash
   gh auth login
   ```

3. **Rate limit exceeded:**
   - Wait for rate limit reset
   - Use authentication token
   - Reduce API calls

---

## Summary

Agent integration in Contextune is about finding the right balance:

**Key Principles:**

1. **Sonnet for thinking, Haiku for doing**
   - Planning and complex reasoning: Sonnet
   - Execution and repetitive tasks: Haiku

2. **Clear communication contracts**
   - Well-defined inputs and outputs
   - Structured data formats
   - Explicit success criteria

3. **Graceful error handling**
   - Haiku handles recoverable errors
   - Escalates when uncertain
   - Main agent provides guidance

4. **Cost optimization**
   - Minimize context transfer
   - Batch operations
   - Use templates
   - Monitor and optimize

5. **User experience first**
   - Transparent progress updates
   - Clear cost reporting
   - Fast execution
   - Reliable results

**Expected Outcomes:**

- **80% cost reduction** for parallel workflows
- **2x faster execution** with Haiku
- **Same quality** as all-Sonnet approach
- **Better UX** with clear progress updates

**Next Steps:**

1. Review examples in this guide
2. Implement cost tracking
3. Monitor agent performance
4. Optimize based on data
5. Share learnings with team

---

**Version:** 1.0
**Last Updated:** 2025-10-21
**License:** MIT
**Questions?** See [COST_OPTIMIZATION_GUIDE.md](./COST_OPTIMIZATION_GUIDE.md) for cost analysis
