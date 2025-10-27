# Session Preservation Guide

**Purpose:** Preserve Claude Code session limits by delegating appropriate tasks to Copilot CLI.

---

## Claude Code Session Limits

### Pro Plan ($20/month)
- **Capacity:** ~10-40 prompts every 5 hours
- **Weekly usage:** 40-80 hours of Sonnet 4
- **Best for:** Small repos (<1,000 lines)
- **Resets:** Every 5 hours based on usage

### Max 5x Plan ($100/month)
- **Capacity:** ~50-200 prompts every 5 hours
- **Weekly usage:** 140-280 hours Sonnet 4 + 15-35 hours Opus 4
- **Opus switch:** Automatic at 20% usage threshold
- **Best for:** Medium repos

### Max 20x Plan ($200/month)
- **Capacity:** ~200-800 prompts every 5 hours
- **Weekly usage:** 240-480 hours Sonnet 4 + 24-40 hours Opus 4
- **Opus switch:** Automatic at 50% usage threshold
- **Best for:** Large repos, heavy usage

---

## When to Delegate vs. Execute Directly

### ✅ DELEGATE to Copilot (Preserves Sessions)

**GitHub Operations:**
- Creating/updating issues
- Managing pull requests
- Querying repo statistics
- Branch operations
- Commit history analysis
- Label management

**Research Tasks:**
- Library comparisons
- Best practices lookup
- API documentation search
- Technology evaluation
- Web research (Copilot has web access)
- Current trends/versions

**Bulk Operations:**
- Multiple file reads (>10 files)
- Codebase analysis (>1000 lines)
- Large refactorings
- Comprehensive testing

**Reasons:**
- These consume multiple prompts/messages
- Results can be compressed into JSON
- Copilot is faster for these (12.7s avg)
- Fresh context = better quality

### ❌ DO DIRECTLY in Claude Code (Don't Delegate)

**Critical Thinking:**
- Architecture decisions
- Security analysis requiring deep context
- Code review requiring full repo understanding
- Complex debugging with stack traces

**Quick Operations:**
- Single file edits
- Simple code generation (<100 lines)
- Quick questions about visible code
- Running tests/builds

**Context-Dependent:**
- Tasks requiring conversation history
- Multi-turn refinement
- Iterative development with feedback

**Reasons:**
- These are fast in Claude (<5 seconds)
- Benefit from existing conversation context
- Delegation overhead not worth it
- Require back-and-forth interaction

---

## Cost-Benefit Analysis

### Delegation Cost

**Time:**
- Delegation overhead: ~2-5 seconds
- Copilot execution: ~12-15 seconds
- Total: ~15-20 seconds

**Benefit:**
- Saves 1-5 Claude Code prompts (depends on task)
- Preserves conversation context
- Gets fresh context for research

### Break-Even Point

**Delegate if task would consume:**
- Pro plan: >1 prompt worth (always delegate research/GitHub ops)
- Max 5x: >2 prompts worth
- Max 20x: >3 prompts worth

**Example: GitHub Issue Creation**

Without delegation (direct in Claude):
- Prompt 1: "Create issue for bug X"
- Prompt 2: Clarify details
- Prompt 3: Execute gh command
- Total: 3 prompts consumed

With delegation:
- Prompt 1: "./scripts/github_operation.sh create-issue \"Bug X\" \"Details\""
- Copilot handles execution in subprocess
- Total: 1 prompt consumed (67% savings)

---

## Monitoring Session Usage

### Check Remaining Capacity

```bash
# In Claude Code
/status
```

Shows:
- Current usage vs. limit
- Messages/prompts remaining
- Time until reset

### Track Delegation Savings

```bash
# View delegation metadata
cat copilot-results/*.meta | jq '.tokens_estimate' | awk '{sum+=$1} END {print sum " tokens saved"}'
```

---

## Best Practices

### 1. Batch Operations

**Bad (Multiple Prompts):**
```
Create issue for bug A
Create issue for bug B
Create issue for bug C
```

**Good (Single Delegation):**
```bash
# Create batch task file
cat > batch-issues.json <<EOF
{
  "operations": [
    {"title": "Bug A", "body": "..."},
    {"title": "Bug B", "body": "..."},
    {"title": "Bug C", "body": "..."}
  ]
}
EOF

# Single delegation
./scripts/delegate_copilot.sh --task-file batch-issues.json
```

### 2. Progressive Complexity

Start with Claude, delegate when needed:

```
1. Quick question → Claude (1 prompt)
2. Needs research → Delegate to Copilot (0 extra prompts)
3. Implement solution → Claude (1 prompt)
4. Comprehensive testing → Delegate to Copilot (0 extra prompts)

Total: 2 Claude prompts vs. 4+ without delegation
```

### 3. Aggregate Results

Let Copilot do heavy lifting, Claude does synthesis:

```
Copilot: Research 5 state management libraries
Claude: Review Copilot's findings + make decision
Claude: Implement chosen solution

Savings: 10-15 prompts for research → 0 prompts (in subprocess)
```

---

## Session Preservation Strategies

### Strategy 1: Research-Heavy Workflows

**Scenario:** Need to research and implement new feature

```bash
# Day 1: Research (delegate to Copilot - 0 prompts)
./scripts/research_task.sh compare "zustand,jotai,recoil"
./scripts/research_task.sh best-practices "React state management"

# Day 2: Implement (Claude - 5-10 prompts)
# Claude reviews research results and implements

Total: 5-10 Claude prompts vs. 20-30 without delegation
```

### Strategy 2: GitHub-Heavy Workflows

**Scenario:** Managing issues and PRs for large project

```bash
# Delegate all GitHub ops (0 Claude prompts)
./scripts/github_operation.sh list-issues . open 50
./scripts/github_operation.sh create-pr "Feature X" "..."

# Claude reviews and makes decisions (2-3 prompts)
Total: 2-3 Claude prompts vs. 10-15 without delegation
```

### Strategy 3: Analysis-Heavy Workflows

**Scenario:** Analyze large codebase

```bash
# Delegate bulk analysis (0 Claude prompts)
./scripts/delegate_copilot.sh "Analyze all files in src/ and identify patterns"

# Claude reviews findings and plans refactor (5 prompts)
Total: 5 Claude prompts vs. 30-50 without delegation
```

---

## Emergency: Out of Sessions

If you hit session limit:

**Option 1: Wait for Reset**
- Sessions reset every 5 hours based on usage
- Use `/status` to check time remaining

**Option 2: Use Copilot for Everything**
```bash
# Delegate orchestration itself
./scripts/delegate_copilot.sh "Take these requirements and implement: ..."
```

**Option 3: Switch to claude.ai**
- Pro/Max plans share limits
- If maxed in Claude Code, you're maxed in claude.ai too
- Only option: wait or upgrade plan

---

## Summary

**Golden Rule:**
If a task can be compressed into JSON results and doesn't require conversation context, delegate to Copilot.

**Pro Plan:** Delegate aggressively (limited to 10-40 prompts/5h)
**Max 5x:** Delegate research and GitHub ops (50-200 prompts/5h)
**Max 20x:** Delegate anything taking >3 prompts (200-800 prompts/5h)

**Result:** 50-80% session preservation with minimal overhead
