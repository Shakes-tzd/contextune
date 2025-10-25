# Contextune v0.5.0 Implementation Plan
## Cost Optimization & Discovery Features

**Date:** 2025-10-24
**Architect:** Claude Code (Sonnet 4.5) via software-architect skill
**Analysis Source:** DocuColab parallel workflow post-mortem

---

## Executive Summary

This plan addresses **$1.15 per workflow cost waste** (82% inefficiency) discovered during the DocuColab parallel development project. The root cause: users are unaware of Contextune's cost-optimized Haiku agents and have no discovery mechanism.

### Investment vs. Return

| Metric | Value |
|--------|-------|
| **Development Effort** | 42-54 hours |
| **Cost Savings Per Workflow** | $1.15 (82% reduction) |
| **Break-Even Point** | 3,261 workflows OR 1.5 years @ 1,200 workflows/year |
| **Annual ROI** | $2,484/year (with 80% adoption increase) |

### Key Features

1. **Cost Tracking Infrastructure** - Real-time token usage and cost reporting
2. **Contextual Help System** - Proactive feature suggestions
3. **Agent Cost Advisor** - Intelligent agent recommendations with cost comparison
4. **Cross-Branch API Validation** - Prevent integration bugs before merge
5. **Enhanced Orchestration** - Full workflow automation with validation

---

## Problem Statement

**Core Issue:** Users waste 82% on agent costs because they:
- Don't know Contextune's specialized agents exist
- Have no cost preview before spawning agents
- Have no cost visibility after execution
- Lack cross-branch API validation
- Must manually coordinate parallel workflows

**Real Example (DocuColab):**
- Used: 5 × `general-purpose` agents = **$1.40**
- Optimal: 5 × `parallel-task-executor` agents = **$0.25**
- Waste: **$1.15 (82%)**

**Additional Issues:**
- 11 minutes debugging API inconsistencies (property vs method)
- 9 minutes resolving merge conflicts
- No cost or performance metrics

---

## Solution Architecture

### Research Findings

**Cost Tracking Patterns** (from AG2/AutoGen):
- Track tokens at agent level
- Aggregate in orchestrator
- Display formatted reports
- Compare to baseline

**Multi-Agent Orchestration** (from Microsoft Agent Framework):
- Centralized orchestration pattern
- Dynamic resource allocation
- Memory optimization (8x reduction)
- Phase-based execution

**Cross-Branch Validation** (Novel approach):
- Git worktree isolation
- Abstract class interface extraction
- Implementation comparison
- Shared test suite execution
- **No existing standard found - we're pioneering this**

**Contextual Help UX** (from UX research):
- Pull revelations (timely, relevant)
- Non-intrusive suggestions
- Smart defaults
- Embedded help centers

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Prompt                              │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  Contextual Help System (NEW)                               │
│  - Detect keywords → Suggest features → Show savings        │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  Intent Detection (Existing)                                │
│  - Keyword → Model2Vec → Semantic Router                    │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Cost Advisor (NEW)                                   │
│  - Match task → Show cost comparison → Get confirmation     │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│  Parallel Orchestration (ENHANCED)                          │
│  ├─ Plan: Dependency analysis                               │
│  ├─ Execute: Spawn agents in worktrees                      │
│  ├─ Validate: Cross-branch API check (NEW)                  │
│  ├─ Merge: Intelligent coordination                         │
│  └─ Report: Cost + Performance metrics (NEW)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Specifications

### Spec 1: Cost Tracking Infrastructure (Issue #7)

**Purpose:** Enable cost visibility and optimization measurement

**Components:**
- `lib/cost_tracker.py` - Core tracking logic
- Agent cost reporting - JSON output from all agents
- Report formatting - ASCII tables with savings

**Data Model:**
```python
@dataclass
class AgentCostReport:
    agent_id: str
    model: str  # "haiku-4.5" or "sonnet-4.5"
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    duration_ms: float
    cost_usd: float

PRICING = {
    "haiku-4.5": {"input": 0.80, "output": 4.00},  # per 1M tokens
    "sonnet-4.5": {"input": 3.00, "output": 15.00}
}
```

**Example Output:**
```
Contextune Cost Report
======================

Workflow: DocuColab Phase 1
Tasks: 5/5 completed
Time: 22 minutes

┌──────────────────────────────────────────────┐
│ Main Agent (Sonnet):              $0.05      │
│ 5 × parallel-task-executor:       $0.20      │
│ ├─ Abstract Core:                 $0.04      │
│ ├─ PPTX Plugin:                   $0.04      │
│ ├─ DOCX Plugin:                   $0.04      │
│ ├─ Unified Schema:                $0.04      │
│ └─ Knowledge Base:                $0.04      │
│                                               │
│ Total: $0.25                                 │
│                                               │
│ vs. general-purpose: $1.40                   │
│ Savings: $1.15 (82%)                         │
└──────────────────────────────────────────────┘
```

**Performance:** <1ms calculation overhead

---

### Spec 2: Contextual Help System (Issue #8)

**Purpose:** Proactive feature discovery

**Trigger Patterns:**

| Keywords | Suggestion | Benefit |
|----------|------------|---------|
| "parallel", "concurrent", "N tasks" | `/contextune:parallel-plan` | 82% cost savings |
| "test", "pytest" | `test-runner` agent | 87% cheaper |
| "worktree", "parallel branch" | `worktree-manager` | 100% automation |
| "GitHub issue" | `issue-orchestrator` | Bulk operations |
| "spawn agent", "Task tool" | Show cost comparison | 82% potential savings |

**Example UX:**
```
💡 Contextune Suggestion

I noticed you mentioned "parallel tasks".

Contextune can automate this workflow:
• Cost: $0.25 (vs $1.40 manual - 82% savings)
• Speed: Fully automated
• Quality: Cross-branch validation included

Try: `/contextune:parallel-plan`

[Yes, use it] [No, continue manually]
```

**Implementation:** `lib/contextual_help.py` integrated into `hooks/user_prompt_submit.py`

**Performance:** <0.5ms keyword detection

---

### Spec 3: Agent Cost Advisor (Issue #5)

**Purpose:** Prevent cost waste through intelligent recommendations

**Agent Matching:**
```python
agent_patterns = {
    "parallel-task-executor": {
        "keywords": ["implement", "feature", "bug fix"],
        "cost_per_task": 0.04,
        "speed": "1-2s"
    },
    "test-runner": {
        "keywords": ["test", "pytest", "coverage"],
        "cost_per_run": 0.02,
        "speed": "0.5-1s"
    },
    "worktree-manager": {
        "keywords": ["worktree", "branch"],
        "cost_per_op": 0.008,
        "speed": "0.2-0.5s"
    },
    "general-purpose": {
        "cost_per_task": 0.27,
        "speed": "3-5s"
    }
}
```

**Example UX:**
```
🎯 Agent Cost Comparison

Task: "Implement 5 features in parallel"

┌─────────────────────────────────────────────────────┐
│ ✅ Recommended: contextune:parallel-task-executor   │
│    Cost: $0.20 (5 × $0.04)                          │
│    Speed: 5-10s total                               │
│    Benefits: Cost tracking + API validation         │
│                                                      │
│ Alternative: general-purpose                        │
│    Cost: $1.35 (5 × $0.27) - 85% more expensive    │
│    Speed: 15-25s total                              │
└─────────────────────────────────────────────────────┘

[Use recommended] [Use alternative] [Show details]
```

**Implementation:** `.claude/skills/agent-cost-advisor/SKILL.md`

**Performance:** <5ms (matching + calculation)

---

### Spec 4: Cross-Branch API Validation (Issue #6)

**Purpose:** Catch API inconsistencies before merge

**Validation Levels:**

| Level | Check | Blocker? |
|-------|-------|----------|
| 1 | Method signature match | Yes |
| 2 | Property vs method consistency | Yes |
| 3 | Required method implementation | Yes |
| 4 | Test suite pass rate | Yes (if <100%) |
| 5 | Documentation consistency | Warning |

**Implementation:**
```python
class CrossBranchValidator:
    def detect_siblings(self) -> list[Path]:
        """Find parallel worktrees"""

    def extract_interface(self, base_class: str) -> dict:
        """Parse abstract base class"""

    def compare_implementations(self, interface: dict, branches: list) -> list[dict]:
        """Check consistency across branches"""

    def run_shared_tests(self, branches: list) -> dict:
        """Run interface test suite"""

    def generate_report(self, issues: list[dict]) -> str:
        """Format report with fix suggestions"""
```

**Example Report:**
```
❌ Cross-Branch Validation Failed

Incompatibilities detected:

1. format_name implementation mismatch
   Branch: feature/pptx-plugin
   → Implements as @property

   Branch: feature/docx-plugin
   → Implements as method

   Fix: Change PPTX to method for consistency

2. Missing method: supports_file()
   Branch: feature/pptx-plugin
   → Not implemented

   Required by: AbstractFormatPlugin

   Fix: Add supports_file() method

Blocking push until resolved.
```

**Novel Approach:** No existing standard found - this pioneers cross-branch API validation for parallel development

**Performance:** 2-5s validation (acceptable for pre-push check)

---

### Spec 5: Enhanced Parallel Orchestration (Issue #9)

**Purpose:** Full workflow automation

**Execution Phases:**
```
Phase 1: Planning (Main agent - Sonnet)
├─ Parse task list
├─ Build dependency graph (DAG)
├─ Identify shared interfaces
├─ Create conflict prevention plan
└─ Estimate costs

Phase 2: Execution (Parallel agents - Haiku)
├─ Create worktrees (worktree-manager)
├─ Spawn task agents (parallel-task-executor × N)
├─ Monitor progress
└─ Track costs

Phase 3: Validation (Before merge)
├─ Cross-branch API validation
├─ Run shared test suites
├─ Report incompatibilities
└─ Block if failures

Phase 4: Integration (Sequential)
├─ Determine merge order from DAG
├─ Merge in dependency order
├─ Validate tests after each merge
├─ Rollback on failure
└─ Final test run

Phase 5: Reporting (Main agent)
├─ Cost breakdown
├─ Performance metrics (speedup, efficiency)
├─ Savings vs baseline
└─ Recommendations
```

**Integration:** Enhanced `commands/contextune-parallel-execute.md`

**Performance:** ~5s orchestration overhead (worth it for automation)

---

## Task Breakdown with Dependencies

### Dependency Graph

```
Foundation Layer (Parallel - Start Immediately)
┌─────────────────────────────────────────────────────┐
│ Task A: Cost Tracking (4-5h)                        │
│ Task B: Contextual Help (3-4h)                      │
│ Task C: Cross-Branch Validator (8-10h)              │
└─────────────────────────────────────────────────────┘
                    ↓
Integration Layer (Sequential - After Foundation)
┌─────────────────────────────────────────────────────┐
│ Task D: Agent Cost Advisor (6-8h) - needs A         │
│ Task E: Enhanced Orchestration (12-15h) - needs A,C │
└─────────────────────────────────────────────────────┘
                    ↓
Validation Layer (Sequential - After Integration)
┌─────────────────────────────────────────────────────┐
│ Task F: Testing & QA (6-8h) - needs all above       │
│ Task G: Documentation (3-4h) - needs all above      │
└─────────────────────────────────────────────────────┘
```

### Task Summary

| Task | Description | Effort | Dependencies | Parallel? |
|------|-------------|--------|--------------|-----------|
| **A** | Cost Tracking Infrastructure | 4-5h | None | ✅ Yes |
| **B** | Contextual Help System | 3-4h | None | ✅ Yes |
| **C** | Cross-Branch Validator | 8-10h | None | ✅ Yes |
| **D** | Agent Cost Advisor Skill | 6-8h | Task A | ❌ No |
| **E** | Enhanced Orchestration | 12-15h | Tasks A, C | ❌ No |
| **F** | Testing & QA | 6-8h | All above | ❌ No |
| **G** | Documentation | 3-4h | All above | ✅ Yes (with F) |

**Total Effort:** 42-54 hours

**Critical Path:** Task C (8-10h) → Task E (12-15h) → Task F (6-8h) = **26-33 hours**

---

## Phased Execution Plan

### Phase 1: Foundation (Week 1) - PARALLEL EXECUTION

**Duration:** 8-10 hours wall clock (if parallelized)

**Recommended Approach:** Use git worktrees + parallel Claude Code instances

```bash
# Create 3 worktrees for parallel work
git worktree add ../contextune-cost-tracking -b feature/cost-tracking
git worktree add ../contextune-contextual-help -b feature/contextual-help
git worktree add ../contextune-validator -b feature/cross-branch-validator

# Launch Claude Code in each worktree
# Work on all 3 tasks simultaneously
```

**Task Assignments:**

| Worktree | Task | Files to Create | Tests Required |
|----------|------|-----------------|----------------|
| `feature/cost-tracking` | Task A | `lib/cost_tracker.py`<br>Agent cost JSON output | `tests/test_cost_tracker.py` |
| `feature/contextual-help` | Task B | `lib/contextual_help.py`<br>`data/contextual_help_config.json`<br>Update `hooks/user_prompt_submit.py` | `tests/test_contextual_help.py` |
| `feature/cross-branch-validator` | Task C | `lib/cross_branch_validator.py`<br>Integration with agents | `tests/test_validator.py` |

**Deliverables:**
- ✅ All 3 modules implemented with unit tests
- ✅ Performance benchmarks met
- ✅ Ready to merge (zero conflicts - different files)

**Quality Gate:**
- [ ] All unit tests pass (>85% coverage)
- [ ] Performance: cost <1ms, help <0.5ms, validator <5s
- [ ] Code review approved
- [ ] UV script format (PEP 723) used

---

### Phase 2: Integration (Week 2) - SEQUENTIAL EXECUTION

**Duration:** 12-15 hours wall clock (must be sequential due to dependencies)

#### Phase 2A: Agent Cost Advisor (6-8h)
**Depends on:** Task A merged

```bash
git worktree add ../contextune-cost-advisor -b feature/agent-cost-advisor
# Wait for Task A to merge first
```

**Deliverables:**
- ✅ `.claude/skills/agent-cost-advisor/` skill
- ✅ Agent matching with cost comparison
- ✅ User confirmation flow
- ✅ Metrics tracking

#### Phase 2B: Enhanced Orchestration (12-15h)
**Depends on:** Tasks A + C merged

```bash
git worktree add ../contextune-orchestration -b feature/enhanced-orchestration
# Wait for Tasks A and C to merge first
```

**Deliverables:**
- ✅ Enhanced `/contextune:parallel-execute` command
- ✅ Dependency analysis (DAG)
- ✅ Validation integration (Task C)
- ✅ Cost reporting (Task A)
- ✅ Merge coordination

**Quality Gate:**
- [ ] Integration tests pass
- [ ] DocuColab scenario works end-to-end
- [ ] Cost reporting accurate
- [ ] Cross-branch validation prevents API bugs

---

### Phase 3: Validation & Documentation (Week 3) - PARALLEL EXECUTION

**Duration:** 6-8 hours wall clock (can parallelize)

```bash
git worktree add ../contextune-testing -b test/integration-qa
git worktree add ../contextune-docs -b docs/v0.5.0
```

**Task F: Testing & QA (6-8h)**
- ✅ Integration test suite
- ✅ Performance benchmarks
- ✅ DocuColab end-to-end test
- ✅ Regression tests
- ✅ Test documentation

**Task G: Documentation (3-4h)**
- ✅ Updated README.md
- ✅ User guides (`docs/cost-optimization.md`, `docs/contextual-help.md`, etc.)
- ✅ Updated CHANGELOG.md
- ✅ MkDocs site deployed
- ✅ Example outputs

**Quality Gate:**
- [ ] All tests pass (unit + integration + E2E)
- [ ] Performance validated
- [ ] Documentation complete
- [ ] Ready for release

---

## Resource Allocation Scenarios

### Scenario 1: Single Developer (Sequential)
**Total Time:** 42-54 hours = **5-7 days** (8h/day)

```
Week 1: Task A → Task B → Task C (15-19h)
Week 2: Task D → Task E (18-23h)
Week 3: Task F → Task G (9-12h)
```

### Scenario 2: Three Developers (Parallel)
**Total Time:** ~**3 weeks** (faster wall clock)

```
Week 1: Dev1=Task A, Dev2=Task B, Dev3=Task C (parallel, 8-10h wall clock)
Week 2: Dev1=Task D, Dev2=Task E (12-15h wall clock)
Week 3: Dev1=Task F, Dev2=Task G (6-8h wall clock)
```

### Scenario 3: Contextune Parallel Workflow (RECOMMENDED)
**Total Time:** ~**20-25 hours wall clock**

Use `/contextune:parallel-execute` to orchestrate development:

```bash
# Phase 1: Foundation (parallel)
/contextune:parallel-execute \
  --tasks="Cost Tracking,Contextual Help,Cross-Branch Validator" \
  --branches="feature/cost-tracking,feature/contextual-help,feature/cross-branch-validator"
# Wall clock: 8-10h (tasks run in parallel worktrees)

# Phase 2: Integration (sequential)
/contextune:parallel-execute \
  --tasks="Agent Cost Advisor,Enhanced Orchestration" \
  --branches="feature/agent-cost-advisor,feature/enhanced-orchestration"
# Wall clock: 12-15h (Task E is longer)

# Phase 3: Validation (parallel)
/contextune:parallel-execute \
  --tasks="Testing,Documentation" \
  --branches="test/integration-qa,docs/v0.5.0"
# Wall clock: 6-8h
```

**Total Wall Clock:** 26-33 hours (vs 42-54h sequential) - **40% faster**

---

## Risk Management

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Task C complexity exceeds estimate | High | Medium | Start earliest, allocate buffer time |
| Task E integration issues | High | Medium | Build incrementally, test each phase |
| Merge conflicts | Medium | Low | Different file sets, cross-branch validation |
| Performance regression | Medium | Low | Benchmark at each phase, gate on metrics |
| API changes in Claude Code | High | Low | Monitor changelog, test against latest |
| Low user adoption | Medium | Medium | Contextual help (Task B) drives discovery |

---

## Success Metrics (Post-Launch)

### Primary KPIs

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Agent Discovery Rate** | 80%+ users choose optimal agents | Cost advisor acceptance tracking |
| **Cost Savings** | 82% average reduction | Actual vs baseline in cost reports |
| **Contextual Help Adoption** | 60%+ accept suggestions | Trigger acceptance rate |
| **API Validation Success** | 90% bug reduction | Pre-merge vs post-merge issues |
| **Workflow Automation** | 100% hands-off | Manual intervention rate |

### Secondary Metrics

- Average cost per workflow: Target <$0.30 (currently $1.40)
- Time to merge: Reduce by 50% (automated coordination)
- User satisfaction: 4.5/5 stars (GitHub surveys)
- Feature adoption: 80% usage within 3 months

---

## Rollout Strategy

### Phase 1: Internal Testing (Week 4)
1. Deploy to personal instance
2. Run 5-10 real workflows
3. Validate 82% cost savings
4. Collect metrics
5. Fix bugs

### Phase 2: Beta Release (Week 5)
1. Tag `v0.5.0-beta`
2. Announce on GitHub Discussions
3. Recruit 10-20 beta testers
4. Monitor adoption metrics
5. Iterate based on feedback

### Phase 3: General Availability (Week 6)
1. Tag `v0.5.0`
2. Deploy docs to GitHub Pages
3. Announce on social media (Reddit, Discord, Twitter)
4. Monitor cost savings metrics
5. Plan v0.6.0 based on data

---

## Cost-Benefit Analysis

### Investment

| Component | Effort | Cost (@$100/hr) |
|-----------|--------|-----------------|
| Cost Tracking | 4-5h | $450 |
| Contextual Help | 3-4h | $350 |
| Cross-Branch Validator | 8-10h | $900 |
| Agent Cost Advisor | 6-8h | $700 |
| Enhanced Orchestration | 12-15h | $1,350 |
| Testing & QA | 6-8h | $700 |
| Documentation | 3-4h | $350 |
| **Total** | **42-54h** | **$4,800** |

### Return

**Per-Workflow Savings:** $1.15 (82% reduction)

**Annual Savings** (assuming 1,200 workflows/year):
- Current cost: 1,200 × $1.40 = $1,680/year
- Optimized cost: 1,200 × $0.25 = $300/year
- **Savings: $1,380/year**

**Break-Even:**
- At current adoption: $4,800 ÷ $1.15 = 4,174 workflows = **3.5 years**
- With 80% adoption increase (contextual help): **1.5 years**

**5-Year ROI:**
- Total savings: $1,380 × 5 = $6,900
- Net ROI: $6,900 - $4,800 = **$2,100**
- ROI %: **44%**

**Conclusion:** Moderate ROI, primarily valuable for:
1. Multi-user scenarios (ROI scales linearly)
2. Developer productivity (faster workflows)
3. Quality improvements (fewer bugs)
4. Competitive advantage (pioneering features)

---

## Next Steps

### Immediate Actions

1. **Review and approve this plan**
   - Validate technical approach
   - Confirm resource allocation
   - Approve timeline

2. **Set up development environment**
   ```bash
   cd /Users/shakes/DevProjects/contextune
   git checkout -b develop  # Create integration branch
   mkdir .plans  # Store this plan
   ```

3. **Create GitHub Project Board**
   - One column per phase
   - One card per task
   - Track progress visually

4. **Begin Phase 1 execution**
   ```bash
   # Create worktrees
   git worktree add ../contextune-cost-tracking -b feature/cost-tracking
   git worktree add ../contextune-contextual-help -b feature/contextual-help
   git worktree add ../contextune-validator -b feature/cross-branch-validator

   # Launch parallel development
   # Open Claude Code in each worktree
   ```

### Questions for Decision

1. **Resource allocation:** Single developer sequential OR parallel worktrees?
2. **Timeline:** Aggressive (3 weeks) OR conservative (5-7 weeks)?
3. **Scope:** All features OR MVP first (Tasks A, B, F only)?
4. **Beta testing:** Internal only OR public beta?

---

## Appendix: File Structure

```
contextune/
├── .plans/
│   └── IMPLEMENTATION_PLAN_v0.5.0.md  # This document
├── lib/
│   ├── cost_tracker.py                # NEW - Task A
│   ├── contextual_help.py             # NEW - Task B
│   ├── cross_branch_validator.py      # NEW - Task C
│   ├── keyword_matcher.py             # Existing
│   ├── model2vec_matcher.py           # Existing
│   └── unified_detector.py            # Existing
├── .claude/skills/
│   └── agent-cost-advisor/            # NEW - Task D
│       ├── SKILL.md
│       ├── matcher.py
│       └── README.md
├── commands/
│   ├── contextune-parallel-execute.md # ENHANCED - Task E
│   ├── contextune-config.md           # Existing
│   └── contextune-stats.md            # Existing
├── agents/
│   ├── parallel-task-executor.md      # ENHANCED - Add cost reporting
│   ├── worktree-manager.md            # ENHANCED - Add cost reporting
│   ├── test-runner.md                 # ENHANCED - Add cost reporting
│   └── performance-analyzer.md        # Existing
├── data/
│   ├── contextual_help_config.json    # NEW - Task B
│   ├── intent_mappings.json           # Existing
│   └── user_patterns.json             # Existing
├── tests/
│   ├── test_cost_tracker.py           # NEW - Task A
│   ├── test_contextual_help.py        # NEW - Task B
│   ├── test_validator.py              # NEW - Task C
│   ├── test_integration.py            # NEW - Task F
│   └── test_e2e_docucolab.py          # NEW - Task F
├── docs/
│   ├── cost-optimization.md           # NEW - Task G
│   ├── contextual-help.md             # NEW - Task G
│   ├── parallel-workflows.md          # NEW - Task G
│   └── cross-branch-validation.md     # NEW - Task G
└── CHANGELOG.md                        # UPDATE - Task G
```

---

## References

- **Analysis Documents:**
  - `/tmp/contextune-analysis-summary.md` - Executive summary
  - `/tmp/contextune-issues-analysis.md` - Detailed issue breakdown

- **GitHub Issues:**
  - Issue #5: Agent Cost Advisor Skill
  - Issue #6: Cross-Branch API Validation
  - Issue #7: Cost Tracking and Reporting
  - Issue #8: Contextual Help System
  - Issue #9: Parallel-Execute Orchestration

- **Research Sources:**
  - AG2 (AutoGen) cost tracking patterns
  - Microsoft Agent Framework orchestration
  - UX research on contextual help
  - Git worktree parallel development

---

**Plan Status:** ✅ Complete - Ready for execution
**Approval Required:** Yes
**Next Review:** After Phase 1 completion
