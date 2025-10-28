---
id: task-1
title: "Create decisions.yaml Schema"
type: implement
complexity: simple
estimated_tokens: 12000
dependencies: []
priority: blocker
copy_from: features.yaml
---

# Task 1: Create decisions.yaml Schema

## Description

Create `decisions.yaml` at project root following the same pattern as `features.yaml`.
This will be the main database for tracking research, plans, and architectural decisions.

## Prerequisites

Read these files to understand the pattern:
- `features.yaml` (lines 1-100) - Structure and format
- `scripts/feature-status.py` - How it's read and queried

## Implementation Steps

### Step 1: Create decisions.yaml with Template

```bash
cat > decisions.yaml <<'EOF'
# Contextune Decision Tracking Database
# Version: 1.0
# Created: 2025-10-27
# Purpose: Preserve context across sessions without bloating conversations

metadata:
  project: "contextune"
  version: "1.0"
  created: "2025-10-27"
  last_updated: "2025-10-27"
  retention_policy: "90_days_active"
  archive_path: "docs/archive/decisions/"
  rag_enabled: false  # Future: enable when >100 entries

# Quick index (what Claude sees first)
index:
  total_research: 0
  total_plans: 0
  total_decisions: 0
  active_research: 0
  active_plans: 0
  active_decisions: 0
  last_research: null
  last_plan: null
  last_decision: null

# ============================================================
# RESEARCH SESSIONS
# Purpose: Avoid redundant research, reference existing findings
# Lifecycle: Expires after 6 months (technology changes)
# ============================================================

research:
  # Example entry (reference, then delete):
  - id: "res-001"
    topic: "Token estimation libraries and methodologies"
    date: "2025-10-27"

    # Research metadata
    agents_used: ["web-research", "codebase-analysis", "methodology"]
    cost_usd: 0.07
    duration_min: 2

    # Key findings (Markdown supported)
    key_findings: |
      - **No industry standards yet** (emerging practice in 2025)
      - **Libraries available:** Anthropic Token Counting API, tiktoken, TokenCost
      - **Methodologies:** Complexity multipliers (0.15×, 0.30×, 0.75×)
      - **Output ratios:** plan (0.225×), implement (0.16×), analyze (0.40×)

    # Recommendations from research
    recommendations:
      - "Use tiktoken for precise input counting"
      - "Use heuristics for output prediction (good enough)"
      - "Implement calibration loop after 30 days"

    # References to full details
    references:
      architecture: "docs/TOKEN_ESTIMATION_ARCHITECTURE.md"
      implementation: "features.yaml"
      changelog: "CHANGELOG.md [Unreleased] 2025-10-27"

    # Categorization
    tags: ["estimation", "tokens", "research", "cost-optimization"]

    # Lifecycle management
    status: "active"  # active | expired | superseded | archived
    expires: "2026-04-27"  # 6 months from creation
    superseded_by: null
    archived_to: null

# ============================================================
# PLANS CREATED
# Purpose: Reference expensive planning work, don't recreate
# Lifecycle: Archives 90 days after completion
# ============================================================

plans:
  # Example entry (reference, then delete):
  - id: "plan-001"
    title: "Token Estimation System Implementation"
    date: "2025-10-27"

    # Plan metadata
    phases: 5
    tasks: 14
    estimated_tokens: 95000
    estimated_cost_haiku: "$0.112"
    estimated_cost_sonnet: "$0.598"

    # Plan summary (Markdown supported)
    summary: |
      5-phase implementation plan for token estimation system:

      **Phase 1:** Foundation (formulas, pricing config)
      **Phase 2:** Core (DB schema, TokenEstimator class)
      **Phase 3:** Integration (CLI tools, features.yaml scripts)
      **Phase 4:** Validation (accuracy tracking, calibration)
      **Phase 5:** Testing (comprehensive test suite)

      **Key decisions:**
      - BUY: tiktoken, TokenCost (free libraries)
      - BUILD: Output prediction, DB integration, calibration

    # Implementation details reference
    references:
      architecture: "docs/TOKEN_ESTIMATION_ARCHITECTURE.md"
      task_breakdown: null
      related_research: ["res-001"]

    # Categorization
    tags: ["estimation", "implementation", "plan", "architecture"]

    # Lifecycle management
    status: "designed"  # designed | in_progress | completed | cancelled | archived
    completed_date: null
    archives_after: null  # Set to date + 90 days when completed
    archived_to: null

# ============================================================
# DECISIONS MADE
# Purpose: Document WHY we made choices, permanent record
# Lifecycle: Never auto-archives (unless superseded)
# ============================================================

decisions:
  # Example entry (reference, then delete):
  - id: "dec-001"
    title: "Token-Based Effort Estimation"
    date: "2025-10-27"
    status: "accepted"  # proposed | accepted | rejected | deprecated | superseded
    deciders: ["team"]

    # Links to supporting work
    based_on_research: ["res-001"]
    based_on_plans: ["plan-001"]

    # Context (WHY we faced this decision)
    context: |
      Time-based estimates (hours/days) are poor metrics in AI-assisted
      parallel development where agents execute simultaneously. Tokens
      directly represent computational cost and enable cost-aware decisions.

    # Problem statement
    problem: |
      Need repeatable way to estimate effort that:
      - Reflects true computational cost
      - Works with parallel agent execution
      - Enables model selection (Haiku vs Sonnet)
      - Provides accurate cost forecasting

    # Alternatives considered
    alternatives_considered:
      - option: "Keep time-based estimates (hours/days)"
        pros:
          - "Familiar to team"
          - "Industry standard for software"
          - "Easy to explain to stakeholders"
        cons:
          - "Inaccurate for parallel work (agents run simultaneously)"
          - "No cost visibility (hours don't map to $)"
          - "Doesn't reflect AI-assisted development reality"
        rejected_because: "Fundamentally incompatible with parallel AI agents"

      - option: "Token-based estimates"
        pros:
          - "Direct cost mapping (tokens → $)"
          - "Parallel-aware (sum of agent tokens)"
          - "Model-aware (Haiku vs Sonnet)"
          - "Enables real-time cost tracking"
        cons:
          - "No industry standards yet (emerging practice)"
          - "Initial estimation accuracy ~25-30%"
          - "Team learning curve on token thinking"
        selected_because: "Represents true computational cost in AI development"

    # The decision (WHAT we're doing)
    decision: |
      Use token-based estimation throughout the project:

      **Formula:** `total = context + reasoning + output`

      **Complexity multipliers:**
      - Simple: 0.15× (template-based, minimal thinking)
      - Medium: 0.30× (standard features, moderate planning)
      - Complex: 0.75× (architecture, debugging, analysis)

      **Output ratios by task type:**
      - Read/Analyze: 0.05× (mostly input)
      - Plan: 0.225× (some output)
      - Implement: 0.16× (code generation)
      - Test: 0.20× (test generation)
      - Analyze: 0.40× (analysis heavy)

      **Replace all time-based estimates** in features.yaml, CLAUDE.md,
      scripts, and documentation.

    # Consequences (positive and negative)
    consequences:
      positive:
        - "Better cost visibility: $0.012 vs '4 hours'"
        - "Accurate parallel execution planning (sum agent tokens)"
        - "Model selection guidance (Haiku for <20K, Sonnet for complex)"
        - "Foundation for real-time cost tracking and budgets"
        - "Enables 82% cost savings via strategic model selection"

      negative:
        - "No industry standards (emerging practice, may evolve)"
        - "Initial estimation accuracy ±25-30% (improves to ±10-15% after 3 months)"
        - "Team learning curve (weeks to think in tokens vs hours)"
        - "Calibration required (need 30 days of data to refine formulas)"

    # Implementation impact
    implementation:
      files_modified:
        - path: "CLAUDE.md"
          changes: "Added Token-Based Effort Estimation section with formulas"
          lines_changed: 100

        - path: "features.yaml"
          changes: "Converted all 15 features from hours to tokens with breakdown"
          lines_changed: 200

        - path: "scripts/feature-status.py"
          changes: "Display tokens with thousands separators and Haiku cost"
          lines_changed: 10

        - path: "scripts/feature-execute.py"
          changes: "Show token breakdown table (context/reasoning/output)"
          lines_changed: 30

      estimated_effort:
        tokens: 95000
        cost_haiku: "$0.112"
        cost_sonnet: "$0.598"

    # Impact assessment
    impact:
      scope: "project-wide"
      affected_systems: ["estimation", "planning", "execution", "reporting", "budgeting"]
      metrics:
        - metric: "Total project effort"
          value: "315K tokens = $0.366 (Haiku) vs $2.028 (Sonnet)"
        - metric: "Cost savings potential"
          value: "82% via Haiku vs Sonnet selection"
        - metric: "Estimation accuracy target"
          value: "±15-20% (Month 1), ±10-15% (Month 3)"

    # How we'll know if this worked
    validation:
      success_criteria:
        - "Estimation accuracy reaches ±15-20% within 1 month"
        - "Estimation accuracy reaches ±10-15% within 3 months"
        - "CLI tools estimate features in <500ms"
        - "Cost forecasts within ±20% of actual spend"

      failure_criteria:
        - "Estimation accuracy stuck above ±30% after 3 months"
        - "Team cannot internalize token thinking after 2 months"
        - "Industry standardizes on different approach"

    # References to full details
    references:
      architecture: "docs/TOKEN_ESTIMATION_ARCHITECTURE.md"
      implementation: "CHANGELOG.md [Unreleased] 2025-10-27"
      research: ["res-001"]
      related_plans: ["plan-001"]
      related_decisions: []

    # Categorization
    tags: ["estimation", "tokens", "cost-optimization", "architecture"]

    # Lifecycle management
    superseded_by: null
    supersedes: null
    archived_to: null

    # Review and updates
    last_reviewed: "2025-10-27"
    review_notes: null

# ============================================================
# SUMMARY STATISTICS (auto-updated by scripts)
# ============================================================

summary:
  total_entries: 3
  by_type:
    research: 1
    plans: 1
    decisions: 1

  by_status:
    research:
      active: 1
      expired: 0
      superseded: 0
      archived: 0
    plans:
      designed: 1
      in_progress: 0
      completed: 0
      archived: 0
    decisions:
      accepted: 1
      proposed: 0
      rejected: 0
      superseded: 0

  by_tag:
    estimation: 3
    tokens: 2
    research: 1
    cost-optimization: 2
    implementation: 1
    architecture: 2

  lifecycle:
    expiring_soon: []  # Research expiring in next 30 days
    ready_to_archive: []  # Completed plans >90 days old
    superseded: []  # Superseded decisions

  last_updated: "2025-10-27"
EOF
```

### Step 2: Validate YAML Syntax

```bash
python -c "import yaml; yaml.safe_load(open('decisions.yaml'))" && echo "✅ Valid YAML"
```

### Step 3: Test Python Can Read It

```python
import yaml

with open("decisions.yaml") as f:
    data = yaml.safe_load(f)

# Verify structure
assert "metadata" in data
assert "index" in data
assert "research" in data
assert "plans" in data
assert "decisions" in data
assert "summary" in data

# Verify can query
research = data["research"]
print(f"Found {len(research)} research entries")

decisions = data["decisions"]
print(f"Found {len(decisions)} decisions")

print("✅ All sections present and queryable")
```

### Step 4: Remove Example Entries

After verifying the structure works, empty the example entries:

```bash
# Edit decisions.yaml:
# Change: research: [example entry]
# To:     research: []
# Change: plans: [example entry]
# To:     plans: []
# Change: decisions: [example entry]
# To:     decisions: []
```

Or start with empty arrays:

```yaml
research: []
plans: []
decisions: []
```

## Files Created

- `decisions.yaml` (500 lines, template with examples)

## Validation Checklist

- [ ] File exists at `/Users/shakes/DevProjects/contextune/decisions.yaml`
- [ ] YAML syntax is valid (no parse errors)
- [ ] Python can load with `yaml.safe_load()`
- [ ] All required sections present (metadata, index, research, plans, decisions, summary)
- [ ] Can query sections with `data["research"]`
- [ ] Example entries demonstrate proper structure

## Expected Output

```
✅ Valid YAML
Found 1 research entries
Found 1 decisions
✅ All sections present and queryable
```

## Estimated Effort

- Tokens: 12K (context: 3K, reasoning: 2K, output: 7K)
- Time: 15 minutes (mostly copy/paste from template)
- Complexity: Simple (just copy template, validate syntax)

## Success Criteria

File exists, is valid YAML, has all required sections, and can be queried programmatically.

## Rollback Plan

Delete `decisions.yaml` if validation fails. No dependencies on this file yet.
