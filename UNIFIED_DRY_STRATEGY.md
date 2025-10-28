# Unified DRY Strategy - Contextune Architectural Standard

**Version:** 1.0
**Created:** 2025-10-28
**Status:** Active Standard

---

## Core Principle

**Don't Repeat Yourself** - Content should exist in exactly ONE place, loaded exactly ONCE per session.

---

## Decision Tree: When to Use What

### 1. For Content Creation

```yaml
ask: "Will this content be frequently updated or reordered?"

if YES (active, mutable):
  use: "Modular YAML files"
  tools: "Write tool (justified for updateability)"
  examples:
    - "/ctx:plan task files (add/remove/reorder tasks)"
    - "features.yaml (update statuses, add features)"
    - "Active project plans with evolving requirements"

  trade_off: "Accept write+read cost for 95% update efficiency"

  benefit:
    - "Edit one task file (500 tokens) vs entire plan (25K tokens)"
    - "Reorder tasks: Edit array vs rewrite file"
    - "Better git diffs: One file changed vs monolithic"

if NO (static, immutable):
  ask: "Is it documentation/design/decision?"

  if YES:
    use: "Extraction-optimized output format"
    tools: "NO Write tool"
    hooks: "SessionEnd/PreCompact extract automatically"
    examples:
      - "Architecture documentation"
      - "Design proposals"
      - "Decision records"
      - "Research findings"

    benefit:
      - "Perfect DRY (content in conversation, extracted once)"
      - "No write+read redundancy"
      - "99% extraction reliability"
      - "Zero manual file management"

  if NO:
    use: "Conversational output only"
    tools: "No files"
    examples:
      - "Answering questions"
      - "Explaining concepts"
      - "Quick responses"
```

---

## 2. For Git Operations

```yaml
ask: "Is the operation deterministic?"

if YES (same inputs → same outputs):
  ask: "Single command or workflow?"

  if SINGLE:
    use: "Direct Bash command"
    example: "git status"
    cost: "$0.002 (745 tokens)"

  if WORKFLOW:
    use: "Deterministic script"
    examples:
      - "./scripts/commit_and_push.sh"
      - "./scripts/create_pr.sh"
      - "./scripts/merge_and_cleanup.sh"
    cost: "$0.002 (545 tokens)"
    wrapper: "./scripts/smart_execute.sh (for AI error recovery)"

    never_use: "Multi-tool git via Bash (8K-25K tokens)"

if NO (requires judgment/research):
  ask: "Requires conversation context?"

  if YES:
    use: "Claude multi-tool approach"
    example: "What should commit message be?"
    cost: "$0.037-0.086"
    justification: "Needs architecture understanding"

  if NO:
    use: "copilot-delegate skill"
    example: "Research state management libraries"
    cost: "$0.113"
    benefit: "Preserves Claude session capacity"
```

---

## 3. For Effort Estimation

```yaml
never_use:
  - "hours"
  - "days"
  - "minutes"
  - "weeks"
  - "months"
  - "duration: X hours"
  - "estimate: 2 days"

always_use:
  - "estimated_tokens: 15000"
  - "complexity: simple|medium|complex"
  - "priority: blocker|high|medium|low"
  - "dependencies: [task-1, task-2]"

reason: "Time is poor metric in parallel AI-assisted development"

conversion:
  if_existing_time_estimate:
    - "Small (4-6h) → 5K-15K tokens"
    - "Medium (8-16h) → 15K-40K tokens"
    - "Large (16-24h) → 40K-80K tokens"
    - "Complex (24h+) → 80K+ tokens"

  then_remove_time: "Delete time reference, keep token estimate"
```

---

## Applied Across Components

### Commands

```yaml
commands:
  ctx_plan:
    status: "✅ Fixed"
    changes:
      - "Added DRY strategy note (extraction vs modular)"
      - "Removed time estimates (1-2 min → 'quickly')"
      - "Justified modular files for updateability"

  ctx_execute:
    review_needed: "Check for git multi-tool, time refs"
    expected_fix: "Use ./scripts/*.sh references"

  ctx_research:
    review_needed: "Check for time references"
    expected_fix: "Remove duration estimates"

  all_others:
    scan: "grep -iE 'hours|days|Write tool' commands/*.md"
    fix: "Apply decision tree above"
```

### Skills

```yaml
skills:
  copilot_delegate:
    status: "Correct (research-focused)"
    no_changes_needed: true

  git_workflow_automator:
    status: "Not yet created"
    when_created: "Follow script-first approach"

  parallel_development_expert:
    review_needed: "Check for time/git violations"
    expected_fix: "Token estimates, script references"
```

### Agents

```yaml
agents:
  worktree_manager:
    status: "✅ Fixed"
    change: "Line 535: git add && git commit → ../scripts/commit_and_push.sh"

  parallel_task_executor:
    review_needed: "Check for git multi-tool examples"
    expected_fix: "Show script usage in examples"

  test_runner:
    review_needed: "Check for time/git violations"
    expected_fix: "Scripts for git, tokens for estimation"
```

### Documentation

```yaml
documentation:
  readme:
    add: "DRY Strategy section"
    content: "Link to UNIFIED_DRY_STRATEGY.md"

  claude_md:
    verify: "Token-based estimation (already updated)"
    check: "No time references remain"

  docs:
    review: "All markdown files in docs/"
    fix: "Apply decision tree"
```

---

## Violation Patterns & Fixes

### Pattern 1: Write Tool for Documentation

**Violation:**
```markdown
Create design.md using the Write tool with the architecture...
```

**Fix:**
```markdown
Output the design using extraction-optimized format:

# Design Title

**Type:** Design
**Status:** Complete

## Architecture
```yaml
...
```

SessionEnd hook will extract this automatically to .plans/
NO Write tool needed.
```

---

### Pattern 2: Git Multi-Tool

**Violation:**
```bash
git add . && git commit -m "message" && git push origin master
```

**Fix:**
```bash
# Use deterministic script
./scripts/commit_and_push.sh "." "message" "master"

# With error recovery
./scripts/smart_execute.sh commit_and_push.sh "." "message" "master"
```

---

### Pattern 3: Time-Based Estimates

**Violation:**
```yaml
estimated_duration: "4-6 hours"
completion_time: "2 days"
```

**Fix:**
```yaml
estimated_tokens: 10000  # 4-6h equivalent
complexity: medium
priority: high
dependencies: []
```

---

## Success Criteria

- [ ] /ctx:plan has DRY strategy note
- [ ] All time references removed (hours/days/minutes)
- [ ] All git operations use scripts
- [ ] Modular vs extraction trade-offs documented
- [ ] agents/worktree-manager uses scripts
- [ ] Unified strategy documented
- [ ] All components follow decision tree

---

## References

- This Document: `UNIFIED_DRY_STRATEGY.md`
- DRY Architecture: `.plans/decision-tracking-system/DRY_CONTEXT_ARCHITECTURE.md`
- Tool Cost Analysis: `.plans/decision-tracking-system/TOOL_CALL_TOKEN_ANALYSIS.md`
- Scripts: `scripts/commit_and_push.sh`, `scripts/smart_execute.sh`
- Extraction Format: `output-styles/extraction-optimized.md`
