# Copilot Delegate Skill

**Preserve Claude Code session limits by delegating GitHub operations and research tasks to GitHub Copilot CLI.**

## Quick Start (5 Minutes)

### 1. Prerequisites

**Required:**
- Claude Code (any plan: Pro, Max 5x, or Max 20x)
- GitHub Copilot CLI installed and configured
- Node.js 18+ (for Copilot CLI)

**Install GitHub Copilot CLI:**
```bash
npm install -g @githubnext/github-copilot-cli

# Login
copilot login

# Verify
copilot --version
```

### 2. Install the Skill

**Option A: Via Claude Code**
```
# In Claude Code
"Install the copilot-delegate skill from copilot-delegate.zip"
```

**Option B: Manual Installation**
```bash
# Copy skill to Claude skills directory
cp -r copilot-delegate ~/.claude/skills/

# Verify
ls ~/.claude/skills/copilot-delegate/
```

### 3. Test It

```
# In Claude Code
"Create a GitHub issue titled 'Test issue' with body 'This is a test'"

# Claude will automatically use the skill to delegate to Copilot
# Result: Issue created without consuming multiple Claude prompts
```

---

## Why Use This Skill?

### The Problem

Claude Code has session limits that reset every 5 hours:

| Plan | Prompts per 5h | Cost |
|------|----------------|------|
| **Pro** | 10-40 | $20/month |
| **Max 5x** | 50-200 | $100/month |
| **Max 20x** | 200-800 | $200/month |

Research and GitHub operations consume multiple prompts:
- Research a library: 5-10 prompts
- Create GitHub issues: 1-3 prompts each
- Compare 3 libraries: 10-15 prompts
- **One research task can max out a Pro plan!**

### The Solution

Delegate heavy operations to Copilot CLI (runs in subprocess):

**Without skill:**
```
Research zustand: 5 prompts
Research jotai: 5 prompts
Research recoil: 5 prompts
Compare: 3 prompts
Total: 18 prompts (Pro plan 50% consumed!)
```

**With skill:**
```
Delegate all research: 0 prompts (subprocess)
Claude reviews results: 1 prompt
Total: 1 prompt (95% savings!)
```

---

## What It Does

### Automatic Activation

The skill automatically activates when Claude detects:

**GitHub keywords:**
- "create issue"
- "list issues"
- "create PR"
- "merge"
- "repo stats"
- "commit history"

**Research keywords:**
- "research"
- "compare"
- "best practices"
- "which library"
- "evaluate"

### Core Capabilities

#### 1. GitHub Operations

```bash
# Create issue
./scripts/github_operation.sh create-issue \
  "Fix auth bug" \
  "Users can't login. Error at auth.ts:42" \
  "bug,priority-high"

# List issues
./scripts/github_operation.sh list-issues . open 20

# Create PR
./scripts/github_operation.sh create-pr \
  "Add OAuth" \
  "Implements Auth0. Fixes #123" \
  main \
  feature/oauth
```

#### 2. Research Tasks

```bash
# Compare libraries
./scripts/research_task.sh compare \
  "zustand,jotai,recoil" \
  "bundle-size,DX,performance"

# Research library
./scripts/research_task.sh library \
  "zustand" \
  "React state management"

# Best practices
./scripts/research_task.sh best-practices \
  "React optimization" \
  2025

# Documentation lookup
./scripts/research_task.sh documentation \
  "Next.js App Router" \
  "server components"
```

#### 3. General Delegation

```bash
# Any task
./scripts/delegate_copilot.sh "Your task here"

# With task file
./scripts/delegate_copilot.sh --task-file tasks/task.json
```

---

## Usage Examples

### Example 1: Create GitHub Issue

**User prompt:**
```
Create a GitHub issue:
Title: Fix login bug
Body: OAuth flow is broken. Error in auth.ts line 42.
Labels: bug, priority-high
```

**What happens:**
1. Claude detects "create issue" keyword
2. Skill activates
3. Claude executes: `./scripts/github_operation.sh create-issue "..." "..." "..."`
4. Script delegates to Copilot CLI (subprocess)
5. Copilot uses `gh` CLI to create issue
6. Returns JSON: `{"issue_number": 123, "issue_url": "..."}`
7. Claude reviews result (1 prompt vs. 3 without skill)

**Result:**
```
Issue created: #123
URL: https://github.com/user/repo/issues/123
Session impact: 1 prompt (saved 2 prompts)
```

### Example 2: Research Libraries

**User prompt:**
```
Research and compare React state management libraries:
zustand, jotai, recoil
Focus on: bundle size, DX, performance
```

**What happens:**
1. Claude detects "research" + "compare" keywords
2. Skill activates
3. Claude executes: `./scripts/research_task.sh compare "..." "..."`
4. Script delegates to Copilot CLI (subprocess)
5. Copilot researches with web access (has current 2025 data)
6. Returns comprehensive JSON comparison
7. Claude reviews findings (1 prompt vs. 15+ without skill)

**Result:**
```
Comparison complete:
- zustand: 1.2KB, excellent DX, best performance
- jotai: 2.9KB, good DX, good performance
- recoil: 16.7KB, moderate DX, moderate performance

Recommendation: zustand for this use case
Session impact: 1 prompt (saved 14 prompts!)
```

### Example 3: Bulk GitHub Operations

**User prompt:**
```
List all open issues labeled "bug" in the current repo
```

**What happens:**
1. Claude detects "list" + "issues" keywords
2. Skill activates
3. Executes: `./scripts/github_operation.sh list-issues . open 50`
4. Copilot queries via `gh issue list --label bug`
5. Returns JSON array of issues
6. Claude formats for user

**Result:**
```
Found 12 open bug issues:
#143 - Login fails with OAuth
#142 - Crash on empty input
#138 - Memory leak in dashboard
...

Session impact: 1 prompt (saved 1-2 prompts)
```

---

## Session Preservation Strategy

### When to Delegate

| Task | Prompts Without Skill | With Skill | Savings |
|------|----------------------|------------|---------|
| Research 1 library | 5-10 | 1 | 80-90% |
| Compare 3 options | 10-15 | 1 | 93% |
| Create GitHub issue | 1-3 | 1 | 0-67% |
| List 20 issues | 1-2 | 1 | 0-50% |
| Best practices lookup | 5-10 | 1 | 80-90% |
| Bulk operations | 10-50 | 1-2 | 80-95% |

### Example Workflow

**Scenario:** Research and implement state management

**Without Skill (38 prompts):**
- Research zustand: 5 prompts
- Research jotai: 5 prompts
- Research recoil: 5 prompts
- Compare: 3 prompts
- Best practices: 5 prompts
- Implement: 10 prompts
- Test: 5 prompts

**With Skill (12 prompts - 68% savings):**
- Delegate research (all 3): 0 prompts (subprocess)
- Delegate comparison: 0 prompts (subprocess)
- Delegate best practices: 0 prompts (subprocess)
- Review findings: 1 prompt
- Implement: 10 prompts
- Delegate testing: 0 prompts (subprocess)
- Review results: 1 prompt

**Impact:**
- Pro plan: One task instead of hitting limit
- Max 5x: 12 prompts instead of 38 (26 saved)
- Max 20x: 12 prompts instead of 38 (26 saved)

---

## Performance

### Speed

- **Copilot execution:** 7-25 seconds (varies by task)
- **Script overhead:** 2-3 seconds
- **Total:** 10-30 seconds per delegation
- **Comparison:** Faster than sequential Claude prompts

### Quality

**GitHub Operations:** ⭐⭐⭐⭐⭐
- Native `gh` CLI integration
- Perfect for issues, PRs, queries

**Research Tasks:** ⭐⭐⭐⭐
- Web access (current 2025 data)
- Good comparisons and recommendations
- Less detailed than Claude, but sufficient

**Code Analysis:** ⭐⭐⭐
- Practical bug identification
- Concise improvements
- Use Claude for deep analysis

### Cost

- **Copilot:** Subscription model (GitHub Copilot subscription)
- **Claude Code:** Preserved for critical tasks
- **Net benefit:** More tasks per 5-hour window

---

## Project Structure

```
copilot-delegate/
├── SKILL.md                          # Main skill documentation
├── README.md                         # This file
├── scripts/
│   ├── delegate_copilot.sh          # Universal delegation
│   ├── github_operation.sh          # GitHub operations
│   └── research_task.sh             # Research tasks
├── references/
│   ├── copilot-capabilities.md      # Copilot strengths/limits
│   └── session-preservation.md      # When to delegate
└── assets/
    └── task-templates/              # JSON templates
        ├── github-issue.json
        ├── github-pr.json
        └── research.json
```

---

## Troubleshooting

### "Command not found: copilot"

**Solution:**
```bash
npm install -g @githubnext/github-copilot-cli
copilot login
```

### "Authentication required"

**Solution:**
```bash
copilot login
```

### "Timeout" (macOS)

**Optional:** Install GNU coreutils for timeout support:
```bash
brew install coreutils
# Provides gtimeout command
```

Without it, scripts run without timeout (usually fine).

### "Invalid JSON output"

Scripts automatically handle Copilot's markdown-wrapped JSON. If you see issues, check:
```bash
cat copilot-results/<latest>.json
cat copilot-results/<latest>.meta
```

---

## Advanced Usage

### Custom Task Files

```bash
# Create custom task
cat > tasks/my-task.json <<EOF
{
  "prompt": "Your detailed task description here",
  "type": "custom"
}
EOF

# Execute
./scripts/delegate_copilot.sh --task-file tasks/my-task.json
```

### Batch Operations

```bash
# Create batch task
cat > tasks/batch-issues.json <<EOF
{
  "prompt": "Create 3 GitHub issues:
    1. Bug: Login fails
    2. Feature: Add dark mode
    3. Docs: Update README
  Use gh CLI and return JSON array of issue URLs."
}
EOF

./scripts/delegate_copilot.sh --task-file tasks/batch-issues.json
```

### Environment Variables

```bash
# Increase timeout (default 60s)
export COPILOT_TIMEOUT=120

# Change results directory
export COPILOT_RESULTS_DIR=./my-results
```

---

## Tips

1. **Monitor your sessions:** Use `/status` in Claude Code to check usage
2. **Delegate early:** Save sessions for implementation and debugging
3. **Batch operations:** Combine multiple GitHub ops in one delegation
4. **Review results:** Always check Copilot's output before using
5. **Be specific:** Detailed prompts get better results

---

## Comparison

### vs. Direct Claude Code Usage

| Aspect | Direct Claude | With Copilot Delegate |
|--------|---------------|----------------------|
| **GitHub ops** | 1-3 prompts each | 1 prompt total |
| **Research** | 5-15 prompts | 1 prompt total |
| **Speed** | 30-60s sequential | 10-30s parallel |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ (good enough) |
| **Session cost** | High | Low |
| **Web access** | Limited | Full (via Copilot) |

### vs. Zen MCP (30k token overhead)

| Aspect | Zen MCP | Copilot Delegate |
|--------|---------|------------------|
| **Token overhead** | 30,000 | 0 (subprocess) |
| **Context pollution** | High | None |
| **Setup** | Complex | Simple |
| **Flexibility** | Limited | High |
| **Performance** | MCP overhead | Native CLI |

---

## Support

**Issues:** Check `copilot-results/*.meta` for error details

**Questions:** See `references/` for detailed guides:
- `copilot-capabilities.md` - What Copilot is good at
- `session-preservation.md` - When/how to delegate

**Examples:** See `assets/task-templates/` for JSON templates

---

## Summary

**Use this skill to:**
✅ Save 50-80% of Claude Code sessions
✅ Delegate GitHub operations (native gh CLI)
✅ Offload research to Copilot (web access)
✅ Get faster results (parallel subprocess)
✅ Focus Claude on high-value tasks

**Don't use for:**
❌ Critical architecture decisions
❌ Security audits
❌ Context-dependent debugging
❌ Iterative refinement

**Result:** More productive development within session limits!
