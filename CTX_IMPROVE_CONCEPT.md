# /ctx:improve - Feature Improvement Command (Concept)

**Status:** Proposal / Concept
**Purpose:** Systematic feature improvement management
**Different from:** /ctx:plan (new features) vs /ctx:improve (existing improvements)

---

## Executive Summary

**/ctx:improve** is a proposed Contextune command for managing continuous improvement opportunities. It differs from `/ctx:plan` by focusing on **existing** improvement opportunities (from release notes, tech debt, bugs) rather than new feature development.

**Value Proposition:**
- Track improvements systematically (not ad-hoc)
- Prioritize by impact vs effort
- Execute efficiently (parallel when possible)
- Measure value delivered

---

## Problem Statement

**Current State:**
- Improvement opportunities identified ad-hoc
- No systematic tracking
- No prioritization framework
- Dependencies unclear
- Value not measured

**Example Pain Points:**
1. Release notes have new features → "We should use that!"
2. Months later: "Did we ever implement X?"
3. Start implementing → blocked by dependency we didn't know about
4. Can't measure ROI of improvements

**Gap:** Need systematic improvement management, not just feature planning.

---

## Solution: /ctx:improve Command

### Core Workflow

```
1. ANALYZE    → Scan sources (release notes, issues, tech debt)
2. CATALOG    → Add to features.yaml with metadata
3. PRIORITIZE → Score by (impact / effort) * risk
4. EXECUTE    → Create worktrees, track status
5. MEASURE    → Track value delivered
```

### Comparison to /ctx:plan

| Aspect | /ctx:plan | /ctx:improve |
|--------|-----------|--------------|
| **Purpose** | Plan NEW features | Track EXISTING improvements |
| **Source** | User request | External changes (releases, bugs, debt) |
| **Timeline** | Immediate (sprint) | Backlog (prioritized queue) |
| **Research** | Always (5 agents) | Sometimes (depends) |
| **Format** | Modular YAML + tasks | Feature catalog (features.yaml) |
| **Execution** | Parallel worktrees | Parallel + sequential (dependencies) |
| **Lifecycle** | Plan → Execute → Complete | Identify → Prioritize → Track → Execute |

**Key Insight:** Complementary, not overlapping!

---

## Command Specification

### /ctx:improve analyze

**Purpose:** Analyze sources for improvement opportunities.

**Usage:**
```bash
/ctx:improve analyze --source FILE [--category CATEGORY]

Examples:
  /ctx:improve analyze --source release-notes.md
  /ctx:improve analyze --source github-issues.json --category bugs
  /ctx:improve analyze --source tech-debt.md
```

**What it does:**
1. Reads source document
2. Uses Haiku to identify improvements
3. Extracts:
   - What changed
   - Why it's valuable
   - How to implement
   - Dependencies
4. Adds to features.yaml
5. Assigns priority based on impact

**Output:**
```
✅ Analyzed release-notes.md

Found 8 new improvement opportunities:
  🔥 feat-016: Haiku 4.5 Integration (critical)
  ⭐ feat-017: AskUserQuestion tool (high)
  ○ feat-018: PreToolUse modifications (medium)
  ...

Added to features.yaml
Run: /ctx:improve list to see all features
```

---

### /ctx:improve list

**Purpose:** Show improvement opportunities.

**Usage:**
```bash
/ctx:improve list [OPTIONS]

Options:
  --phase N              Show Phase N
  --priority LEVEL       Show priority level
  --status STATUS        Show status
  --independent          Show independent features only

Examples:
  /ctx:improve list
  /ctx:improve list --phase 1
  /ctx:improve list --priority critical
  /ctx:improve list --independent
```

**Output:**
```
Contextune Feature Improvements

Summary:
  Total: 15 features
  Planned: 13 | In Progress: 0 | Completed: 1

Ready to Execute (independent):
  🔥 feat-001: Haiku 4.5 Integration (4h, Phase 1)
  ⭐ feat-002: AskUserQuestion Integration (16h, Phase 1)
  ⭐ feat-006: SessionEnd Analytics (8h, Phase 1)

Blocked (dependencies):
  ○ feat-003: PreToolUse Modifications (needs: feat-001)
  ○ feat-004: Explore Integration (needs: feat-001)

Commands:
  /ctx:improve execute feat-001
  /ctx:improve graph
```

---

### /ctx:improve graph

**Purpose:** Show dependency graph.

**Usage:**
```bash
/ctx:improve graph [--format FORMAT]

Formats:
  text (default) - ASCII visualization
  mermaid        - Mermaid diagram
  summary        - Just show phases
```

**Output (text):**
```
Feature Dependency Graph

✓ = Completed | → = In Progress | ○ = Planned | ✗ = Blocked

○ feat-001: Haiku 4.5 Integration [Phase 1]
   └─ blocks: feat-003, feat-004

○ feat-002: AskUserQuestion Integration [Phase 1]
   └─ independent (can execute in parallel)

○ feat-003: PreToolUse Modifications [Phase 2]
   ├─ depends on: feat-001 [○]
   └─ blocks: none

Phase Execution:
  Phase 1 (parallel): feat-001, feat-002, feat-006
  Phase 2 (sequential): feat-003, feat-004, feat-005
  Phase 3 (parallel): feat-007, feat-009, feat-011
```

---

### /ctx:improve execute

**Purpose:** Execute feature implementation.

**Usage:**
```bash
/ctx:improve execute FEATURE_ID [--batch]

Examples:
  /ctx:improve execute feat-001
  /ctx:improve execute-batch --phase 1  # Execute all Phase 1 in parallel
```

**What it does:**
1. Validates feature exists
2. Checks dependencies completed
3. Creates worktree (worktrees/FEATURE_ID)
4. Creates branch (feature/FEATURE_ID)
5. Updates status to in_progress
6. Shows implementation guide

**Output:**
```
✅ Ready to implement feat-001

Feature: Haiku 4.5 Integration
Phase: 1 | Priority: critical | Effort: 4h

Files to modify:
  ✓ hooks/user_prompt_submit.py

Changes required:
  • Update model string to claude-haiku-4-5-20250929
  • Test performance benchmarks
  • Verify cost reduction

Testing required:
  • Benchmark latency (target <200ms P95)
  • Verify cost reduction (target 87%)
  • Test accuracy (maintain ≥85%)

Created worktree: worktrees/feat-001
Branch: feature/feat-001

Next steps:
  1. cd worktrees/feat-001
  2. Make changes
  3. Run tests
  4. Push: git push -u origin feature/feat-001
  5. Create PR
  6. Complete: /ctx:improve complete feat-001
```

---

### /ctx:improve execute-batch

**Purpose:** Execute multiple independent features in parallel.

**Usage:**
```bash
/ctx:improve execute-batch --phase 1
/ctx:improve execute-batch --independent
```

**What it does:**
1. Identifies independent features (no dependencies)
2. Creates worktrees for all
3. Creates branches for all
4. Updates statuses
5. Shows parallel execution plan

**Output:**
```
✅ Executing 3 features in parallel

Created worktrees:
  • feat-001 → worktrees/feat-001 (branch: feature/feat-001)
  • feat-002 → worktrees/feat-002 (branch: feature/feat-002)
  • feat-006 → worktrees/feat-006 (branch: feature/feat-006)

Parallel execution plan:
  Terminal 1: cd worktrees/feat-001 && <implement>
  Terminal 2: cd worktrees/feat-002 && <implement>
  Terminal 3: cd worktrees/feat-006 && <implement>

After implementation:
  /ctx:improve complete feat-001
  /ctx:improve complete feat-002
  /ctx:improve complete feat-006

Estimated total time: 28h
Estimated parallel time: 16h (if 3 devs)
Time savings: 43%
```

---

### /ctx:improve complete

**Purpose:** Mark feature as completed.

**Usage:**
```bash
/ctx:improve complete FEATURE_ID
```

**What it does:**
1. Updates status to completed
2. Shows features now unblocked
3. Shows overall progress
4. Suggests next steps

**Output:**
```
✅ feat-001 marked as completed

Features now unblocked:
  ⭐ feat-003: PreToolUse Modifications
  ⭐ feat-004: Explore Integration

Overall Progress:
  Completed: 2 / 15 (13%)
  Phase 1: 1 / 3 (33%)

Value delivered:
  Cost savings: $200/month
  Performance: 2-3x faster analysis

Next steps:
  /ctx:improve execute feat-003
  /ctx:improve execute feat-004
```

---

### /ctx:improve stats

**Purpose:** Show improvement statistics.

**Usage:**
```bash
/ctx:improve stats [--period PERIOD]
```

**Output:**
```
Improvement Statistics

Overall:
  Total features: 15
  Completed: 2 (13%)
  In progress: 3 (20%)
  Planned: 10 (67%)

Value Delivered (completed):
  Cost savings: $250/month
  Performance: +250% (average)
  Reliability: +25%
  UX: +20%

In Progress (estimated):
  Cost savings: +$100/month
  Performance: +15%
  Reliability: +40%
  UX: +30%

Top Priorities (not started):
  🔥 feat-007: MCP Server (high value, medium effort)
  ⭐ feat-011: Dynamic Model Selection (medium value, low effort)

Recommendations:
  • Execute feat-007 next (high ROI)
  • Complete in-progress features first
  • Phase 1 is 33% complete
```

---

## Implementation Architecture

### File Structure

```
.claude/plugins/marketplaces/Contextune/
├── commands/
│   └── ctx-improve.md          # Command documentation
├── skills/
│   └── improvement-manager/    # Skill for improvement workflow
│       └── SKILL.md
├── agents/
│   └── improvement-analyzer.md # Agent for analyzing sources
└── lib/
    └── improvement_parser.py   # Parse release notes, issues
```

### Skills Integration

**Skill:** `improvement-manager`

**Triggers:**
- "analyze improvements"
- "track feature improvements"
- "prioritize improvements"
- "show improvement roadmap"

**Actions:**
- Loads features.yaml
- Uses scripts/feature-*.sh
- Provides recommendations

---

## Integration Points

### With /ctx:plan

```bash
# Workflow: Improvement → Plan → Execute

# 1. Identify improvement
/ctx:improve analyze --source release-notes.md
# Adds: feat-020 (complex feature)

# 2. See it's complex
/ctx:improve list
# Shows: feat-020 (complexity: high, risk: medium)

# 3. Use ctx:plan for detailed planning
/ctx:plan
# "Implement feat-020: [detailed requirements]"
# Creates: .parallel/plans/ with research

# 4. Execute via ctx:execute
/ctx:execute
# Uses plan from /ctx:plan

# 5. Mark improvement complete
/ctx:improve complete feat-020
```

**Complementary:**
- **/ctx:improve:** Identify & prioritize
- **/ctx:plan:** Detailed planning for complex features
- **/ctx:execute:** Parallel execution

### With /ctx:research

```bash
# Some improvements need research first

# 1. Identify improvement
/ctx:improve analyze --source issues.json
# Adds: feat-021 (research needed)

# 2. Research first
/ctx:research --topic "Best practices for X"
# Returns: Research findings

# 3. Update improvement with findings
/ctx:improve update feat-021 --research "..."

# 4. Execute
/ctx:improve execute feat-021
```

### With Existing Scripts

```bash
# Behind the scenes, /ctx:improve uses:

/ctx:improve list
  → ./scripts/feature-status.sh

/ctx:improve graph
  → ./scripts/feature-graph.sh

/ctx:improve execute feat-001
  → ./scripts/feature-execute.sh feat-001

/ctx:improve complete feat-001
  → ./scripts/feature-complete.sh feat-001
```

---

## Use Cases

### Use Case 1: Release Notes Analysis

**Scenario:** Claude Code releases v2.1.0 with 10 new features.

**Workflow:**
```bash
# 1. Download release notes
curl -o release-notes-v2.1.0.md https://...

# 2. Analyze
/ctx:improve analyze --source release-notes-v2.1.0.md

# Output:
#   Found 6 improvement opportunities:
#     feat-025: New feature X (critical)
#     feat-026: Enhanced feature Y (high)
#     ...

# 3. Review and prioritize
/ctx:improve list --priority critical

# 4. Execute high-value improvements
/ctx:improve execute-batch --priority critical
```

---

### Use Case 2: Technical Debt Management

**Scenario:** Accumulated technical debt across codebase.

**Workflow:**
```bash
# 1. Document tech debt
cat > tech-debt.md <<EOF
# Technical Debt

1. Old API still using callbacks (should use promises)
2. Duplicate code in 3 files (should extract)
3. Missing tests for edge cases
EOF

# 2. Analyze
/ctx:improve analyze --source tech-debt.md --category tech-debt

# 3. Prioritize by effort
/ctx:improve list --sort-by effort_to_value

# 4. Execute quick wins first
/ctx:improve execute feat-030  # Low effort, high value
```

---

### Use Case 3: Bug Backlog

**Scenario:** 50 bugs in GitHub issues.

**Workflow:**
```bash
# 1. Export bugs
gh issue list --label bug --json title,body > bugs.json

# 2. Analyze
/ctx:improve analyze --source bugs.json --category bugs

# 3. Prioritize by severity
/ctx:improve list --category bugs --sort-by priority

# 4. Execute in parallel
/ctx:improve execute-batch --category bugs --priority critical
```

---

## Benefits

### For Solo Developers

**Before:**
- Improvement ideas forgotten
- No prioritization
- Work on whatever comes to mind
- No measurement

**After:**
- All improvements tracked
- Prioritized by value
- Work on highest ROI
- Measure impact

### For Teams

**Before:**
- Everyone tracks differently
- No visibility into backlog
- Dependencies unclear
- Duplicate work

**After:**
- Shared improvement backlog
- Full team visibility
- Dependencies tracked
- Parallel execution coordinated

---

## Success Metrics

### Quantitative

- **Improvements identified:** Target 20+ per quarter
- **Improvements completed:** Target 50% completion rate
- **Value delivered:** Track cost savings, performance, etc.
- **Time to execution:** Days from identification to start
- **Parallel efficiency:** % time saved via parallel execution

### Qualitative

- **Visibility:** Team knows what's coming
- **Prioritization:** Work on highest value
- **Dependencies:** No surprise blockers
- **Measurement:** ROI tracking

---

## Implementation Plan

### Phase 1: Foundation (Completed ✅)

- ✅ features.yaml format
- ✅ Execution scripts
- ✅ Dependency tracking
- ✅ Documentation

### Phase 2: Command Implementation (Next)

1. Create `commands/ctx-improve.md`
2. Create `skills/improvement-manager/SKILL.md`
3. Create `agents/improvement-analyzer.md`
4. Create `lib/improvement_parser.py`
5. Test with real release notes

**Estimated effort:** 40 hours

### Phase 3: Integration (Future)

1. Integrate with /ctx:plan
2. Integrate with /ctx:research
3. Add auto-analysis (watch release notes)
4. Add value tracking
5. Add team collaboration features

**Estimated effort:** 60 hours

---

## Competitive Analysis

### vs. GitHub Projects

**GitHub Projects:**
- General purpose
- No prioritization framework
- No dependency tracking
- No parallel execution optimization

**/ctx:improve:**
- Purpose-built for improvements
- Impact/effort scoring
- Automatic dependency tracking
- Parallel execution planning

### vs. JIRA

**JIRA:**
- Heavy, enterprise focus
- Requires setup and configuration
- No AI integration
- No code-level execution

**/ctx:improve:**
- Lightweight, developer-focused
- Zero setup (works with Claude Code)
- AI-powered analysis
- Direct worktree creation

---

## FAQ

### Q: How is this different from /ctx:plan?

**A:** /ctx:plan is for planning NEW features from scratch. /ctx:improve is for tracking EXISTING improvement opportunities. They complement each other:

- `/ctx:improve` identifies what should be improved
- `/ctx:plan` plans how to build complex features
- `/ctx:execute` executes the plans

### Q: Can I use this for new features too?

**A:** Yes, but /ctx:plan is better for new features because it includes comprehensive research (5 parallel agents). Use /ctx:improve for improvements where requirements are clear.

### Q: How does dependency tracking work?

**A:** Features declare dependencies in features.yaml. The system prevents execution of features until dependencies are completed. This prevents wasted work.

### Q: Can I customize the prioritization formula?

**A:** Yes! Edit features.yaml to adjust impact/effort scores. The priority_score is calculated as: `(impact_score / effort_score) * risk_multiplier`

### Q: Does this work offline?

**A:** Yes! All tracking is in features.yaml (local file). Analysis phase needs network (uses Haiku), but execution/tracking works offline.

---

## Conclusion

**/ctx:improve** fills a gap between feature planning (/ctx:plan) and execution (/ctx:execute) by providing systematic improvement management.

**Key Value:**
1. **Track improvements** systematically (not ad-hoc)
2. **Prioritize** by impact vs effort
3. **Execute efficiently** (parallel when possible)
4. **Measure value** delivered

**Status:** Foundation complete (scripts + features.yaml). Command implementation next.

**Ready to build:** Yes!

---

**Version:** 1.0 (Concept)
**Created:** 2025-10-27
**Next Steps:**
1. Gather user feedback on concept
2. Validate with real release notes
3. Implement Phase 2 (command)
4. Beta test with users
5. Iterate based on feedback
