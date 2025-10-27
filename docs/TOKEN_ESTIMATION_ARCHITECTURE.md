# Token Estimation System Architecture

**Version:** 1.0
**Date:** 2025-10-27
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

This document specifies a comprehensive token estimation system for Contextune that predicts computational cost (in tokens) for AI tasks before execution, tracks actual usage during execution, and learns from differences to improve accuracy over time.

**Key Goals:**
- ✅ Estimation accuracy: ±15-20% within 1 month, ±10-15% within 3 months
- ✅ Integration: Seamlessly works with features.yaml and /ctx:plan
- ✅ Validation: Automatic comparison of estimated vs actual tokens
- ✅ Learning: System improves via calibration over time

**Implementation Effort:**
- Total tokens: ~95K (35K context + 21K reasoning + 44K output)
- Cost: $0.112 (Haiku execution)
- Timeline: 1.5-2 days (parallel) or 3-4 days (sequential)

---

## Table of Contents

1. [Research Findings](#research-findings)
2. [Problem Statement](#problem-statement)
3. [System Architecture](#system-architecture)
4. [Token Estimation Formulas](#token-estimation-formulas)
5. [Database Schema](#database-schema)
6. [Implementation Plan](#implementation-plan)
7. [Build vs Buy Decisions](#build-vs-buy-decisions)
8. [Success Criteria](#success-criteria)

---

## Research Findings

### Existing Libraries & Tools

**1. Anthropic Token Counting API** (Beta, Nov 2024)
- **Endpoint:** `/v1/messages/count_tokens`
- **Accuracy:** Estimated counts; actual may differ slightly
- **Rate Limits:** 100-8,000 RPM (tier-based)
- **Cost:** Free
- **Use Case:** Pre-execution counting for Claude models
- **URL:** https://docs.claude.com/en/docs/build-with-claude/token-counting

**2. Tiktoken** (OpenAI)
- **Performance:** 3-6x faster than comparable tokenizers
- **Accuracy:** Exact for input tokens
- **Models:** o200k_base (GPT-4o), cl100k_base (GPT-4/3.5)
- **Installation:** `pip install tiktoken`
- **Use Case:** Client-side token counting
- **URL:** https://github.com/openai/tiktoken

**3. TokenCost** (AgentOps-AI)
- **Coverage:** 400+ LLMs (OpenAI, Anthropic, Azure, Mistral, etc.)
- **Features:** Token counting + USD cost calculation
- **Technology:** Tiktoken + Anthropic beta API
- **Installation:** `pip install tokencost`
- **Use Case:** Multi-provider token counting + cost estimation
- **URL:** https://github.com/AgentOps-AI/tokencost

**4. PreflightLLMCost** (ML-Based)
- **Uniqueness:** Predicts completion tokens via 3-tier ML cascade
- **Accuracy:** 15-25% MAPE with 95% confidence intervals
- **Complexity:** High (requires training, hidden state analysis)
- **URL:** https://github.com/aatakansalar/PreflightLLMCost

### Existing Contextune Infrastructure

**Current Token Tracking** (`lib/observability_db.py:209-247`):
```sql
CREATE TABLE model_corrections (
    prompt_tokens INTEGER,           -- Already tracked
    completion_tokens INTEGER,       -- Already tracked
    total_cost_usd REAL,            -- Already calculated
    -- ... other fields
)
```

**Current Cost Calculation** (`observability_db.py:413-417`):
```python
# Haiku 4.5 pricing
input_cost = (prompt_tokens * 0.25) / 1_000_000   # $0.25/M
output_cost = (completion_tokens * 1.25) / 1_000_000  # $1.25/M
total_cost_usd = input_cost + output_cost
```

**Current Estimation Heuristics** (`tool_cost_tracker.py:99-127`):
```python
# Tool-specific formulas:
Read: 2 tokens per line
Bash: 0.5 tokens per character
Grep: 1 token per match
Generic: 4 characters per token
```

**Gaps Identified:**
- ❌ No table for storing estimated tokens before execution
- ❌ No validation system (estimated vs actual comparison)
- ❌ No calibration/learning loop
- ❌ Pricing constants duplicated across files

### Token Estimation Methodologies

**Context Token Estimation:**
- **Precise:** Use tiktoken BPE tokenization (`len(encoding.encode(text))`)
- **Fast Heuristic:** 4 characters per token, or 2 tokens per line for code
- **Language-Specific:**
  - JavaScript: ~7 tokens/line
  - SQL: ~11.5 tokens/line
  - Python: ~10 tokens/line

**Reasoning Token Estimation:**
Research shows complexity-based multipliers work well:

| Complexity | Multiplier | Description |
|------------|------------|-------------|
| Simple | 0.15× context | Template-based, minimal thinking |
| Medium | 0.30× context | Standard feature, moderate planning |
| Complex | 0.75× context | Architecture, debugging, deep analysis |

**Output Token Estimation:**
Task-type-based ratios from real-world data:

| Task Type | Ratio | Example |
|-----------|-------|---------|
| Planning | 0.225× context | Design docs, specs |
| Implementation | 0.16× context | Code generation |
| Analysis | 0.40× context | Code review, debugging |
| Testing | 0.20× context | Test generation |

### Real-World Validation Data

**From Contextune's Actual Usage:**
```yaml
Execution Tasks:
  Input: 30,000-40,000 tokens
  Output: 4,800-8,500 tokens
  Ratio: ~6:1 (input:output)

Planning Tasks:
  Input: 8,000 tokens
  Output: 1,800 tokens
  Ratio: ~4.4:1 (input:output)
```

**Industry Best Practices:**
- Initial estimation error: ±25-30% acceptable
- Month 1 target: ±15-20% error
- Month 3 target: ±10-15% error
- Calibration: 30-day rolling average adjustments

---

## Problem Statement

### Core Need

Contextune needs a **repeatable, accurate token estimation system** that enables cost-aware decision making throughout the development workflow: from planning (features.yaml) to execution (parallel agents) to retrospective analysis.

### Requirements

**Functional:**
1. Estimate tokens BEFORE execution (context + reasoning + output)
2. Calculate costs for both Haiku and Sonnet models
3. Store estimates in observability DB
4. Track actual token usage from API responses
5. Compare estimated vs actual for validation
6. Auto-calibrate formulas based on historical accuracy
7. Integrate with features.yaml and /ctx:plan workflows

**Non-Functional:**
- Estimation latency: <100ms single task, <500ms for 15 tasks
- Accuracy: ±15-20% within 1 month
- No external API calls for basic estimation (optional tiktoken)
- Backward compatible with existing observability_db.py

### Success Criteria

✅ CLI tool estimates all features.yaml entries in <500ms
✅ Phase 1 task estimation error is ±20% after 2 weeks
✅ Observability DB tracks both estimated and actual tokens
✅ Accuracy report shows error trends over time
✅ Calibration improves accuracy by ≥5% within 30 days

---

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERFACES                        │
├─────────────────────────────────────────────────────────┤
│  CLI Tools          │  Features.yaml Scripts │ /ctx:plan│
│  - estimate-tokens  │  - feature-status.py   │ Command  │
│  - accuracy-report  │  - feature-execute.py  │          │
└──────────────┬──────────────────┬─────────────┬─────────┘
               │                  │             │
               ▼                  ▼             ▼
┌─────────────────────────────────────────────────────────┐
│              TOKEN ESTIMATION ENGINE                     │
├─────────────────────────────────────────────────────────┤
│  TokenEstimator Class                                    │
│  - estimate_task()                                       │
│  - estimate_from_features_yaml()                         │
│  - estimate_batch()                                      │
│                                                          │
│  Uses:                                                   │
│  - Pricing Config (centralized)                          │
│  - Tiktoken (optional precision)                         │
│  - Heuristics (fast estimation)                          │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│              STORAGE & TRACKING LAYER                    │
├─────────────────────────────────────────────────────────┤
│  observability_db.py (Extended)                          │
│                                                          │
│  Tables:                                                 │
│  - task_estimates (NEW)      - Estimated tokens         │
│  - model_corrections         - Actual tokens (existing) │
│  - calibration_history (NEW) - Formula adjustments      │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│           VALIDATION & LEARNING LAYER                    │
├─────────────────────────────────────────────────────────┤
│  EstimationValidator                                     │
│  - compare_estimated_vs_actual()                         │
│  - calculate_error_metrics()                             │
│  - generate_accuracy_reports()                           │
│                                                          │
│  CalibrationEngine                                       │
│  - analyze_historical_errors()                           │
│  - adjust_multipliers()                                  │
│  - log_calibration_changes()                             │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

**Estimation Flow (Pre-Execution):**
```
1. User requests estimation
   ↓
2. TokenEstimator.estimate_task(description, files, complexity, type)
   ↓
3. Calculate: context_tokens = sum(file_tokens) + description_tokens
   ↓
4. Calculate: reasoning_tokens = context × complexity_multiplier
   ↓
5. Calculate: output_tokens = context × output_ratio
   ↓
6. Calculate: costs = tokens × pricing[model]
   ↓
7. Store in task_estimates table
   ↓
8. Return TokenEstimate object
```

**Validation Flow (Post-Execution):**
```
1. Task executes, actual tokens logged to model_corrections
   ↓
2. EstimationValidator links estimate_id → execution_id
   ↓
3. Calculate error: (actual - estimated) / actual
   ↓
4. Store error metrics by task_type + complexity
   ↓
5. Generate accuracy report
```

**Calibration Flow (Monthly):**
```
1. CalibrationEngine analyzes last 30 days
   ↓
2. Calculate average error per task_type + complexity
   ↓
3. If error > 20%: adjust multiplier by ±10%
   ↓
4. Log adjustment to calibration_history
   ↓
5. Update TokenEstimator formulas
```

---

## Token Estimation Formulas

### Core Formula

```python
total_tokens = context_tokens + reasoning_tokens + output_tokens

Where:
  context_tokens = sum(file_tokens) + description_tokens
  reasoning_tokens = context_tokens × complexity_multiplier
  output_tokens = context_tokens × output_ratio
```

### Complexity Multipliers

| Complexity | Multiplier | Use When |
|------------|------------|----------|
| **Simple** | 0.15 | Template-based changes, config updates, simple fixes |
| **Medium** | 0.30 | Standard features, API integrations, moderate refactoring |
| **Complex** | 0.75 | Architecture changes, debugging, algorithm design |

### Task Type Output Ratios

| Task Type | Ratio | Use When |
|-----------|-------|----------|
| **Read/Analyze** | 0.05 | Code review, documentation reading |
| **Plan** | 0.225 | Design docs, specifications, architecture |
| **Implement** | 0.16 | Feature implementation, code generation |
| **Test** | 0.20 | Test generation, QA automation |
| **Analyze** | 0.40 | Debugging, performance analysis, deep code review |

### Context Token Calculation

**Option 1: Precise (Tiktoken)**
```python
import tiktoken

def count_tokens_precise(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

**Option 2: Fast Heuristic**
```python
def count_tokens_heuristic(text: str) -> int:
    # Generic: 4 characters per token
    return len(text) // 4

def count_tokens_code(code: str, language: str) -> int:
    lines = code.count("\n")
    tokens_per_line = {
        "python": 10,
        "javascript": 7,
        "sql": 11.5,
        "generic": 2
    }
    return int(lines * tokens_per_line.get(language, 2))
```

### Cost Calculation

```python
def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> dict:
    pricing = {
        "haiku": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
        "sonnet": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000}
    }

    input_cost = input_tokens * pricing[model]["input"]
    output_cost = output_tokens * pricing[model]["output"]

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost
    }
```

### Example Calculation

**Task:** Implement Haiku 4.5 upgrade (feat-001)
- **Files to read:** `hooks/user_prompt_submit.py` (~500 lines)
- **Description:** 50 words
- **Complexity:** Simple (0.15)
- **Type:** Implement (0.16)

**Calculation:**
```python
# Context
file_tokens = 500 lines × 2 tokens/line = 1,000
description_tokens = 50 words × 1.3 tokens/word = 65
context_tokens = 1,000 + 65 = 1,065

# Reasoning
reasoning_tokens = 1,065 × 0.15 = 160

# Output
output_tokens = 1,065 × 0.16 = 170

# Total
input_tokens = 1,065 + 160 = 1,225
output_tokens = 170
total_tokens = 1,395

# Cost (Haiku)
input_cost = 1,225 × $0.00000025 = $0.00031
output_cost = 170 × $0.00000125 = $0.00021
total_cost = $0.00052
```

**Note:** Actual feat-001 estimate is 10,000 tokens because it includes:
- Reading existing code
- Understanding architecture
- Testing/validation
- Documentation updates

---

## Database Schema

### New Table: task_estimates

```sql
CREATE TABLE task_estimates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Task identification
    task_id TEXT NOT NULL,              -- Feature ID (e.g., "feat-001") or task name
    task_type TEXT NOT NULL,            -- plan | implement | analyze | test
    complexity TEXT NOT NULL,           -- simple | medium | complex

    -- Estimated tokens (breakdown)
    estimated_context_tokens INTEGER NOT NULL,
    estimated_reasoning_tokens INTEGER NOT NULL,
    estimated_output_tokens INTEGER NOT NULL,
    estimated_total_tokens INTEGER NOT NULL,

    -- Estimated costs
    estimated_cost_haiku_usd REAL NOT NULL,
    estimated_cost_sonnet_usd REAL NOT NULL,

    -- Estimation metadata
    estimation_method TEXT DEFAULT 'heuristic',  -- heuristic | tiktoken | hybrid
    formula_version TEXT DEFAULT '1.0',          -- Track formula changes

    -- Timing & linking
    timestamp REAL NOT NULL,
    session_id TEXT,
    actual_execution_id INTEGER,                 -- Link to model_corrections

    -- Validation results (populated post-execution)
    actual_total_tokens INTEGER,
    estimation_error_pct REAL,                   -- (actual - estimated) / actual * 100

    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (actual_execution_id) REFERENCES model_corrections(id)
);

-- Indexes for common queries
CREATE INDEX idx_task_estimates_task_id ON task_estimates(task_id);
CREATE INDEX idx_task_estimates_session_id ON task_estimates(session_id);
CREATE INDEX idx_task_estimates_timestamp ON task_estimates(timestamp);
CREATE INDEX idx_task_estimates_type_complexity ON task_estimates(task_type, complexity);
```

### New Table: calibration_history

```sql
CREATE TABLE calibration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- What changed
    parameter_name TEXT NOT NULL,      -- E.g., "complexity_multiplier_medium"
    old_value REAL NOT NULL,
    new_value REAL NOT NULL,
    change_pct REAL NOT NULL,          -- (new - old) / old * 100

    -- Why it changed
    reason TEXT NOT NULL,              -- E.g., "30-day avg error: -18%"
    task_type TEXT,                    -- If specific to task type
    complexity TEXT,                   -- If specific to complexity

    -- Supporting data
    sample_size INTEGER NOT NULL,      -- How many tasks analyzed
    avg_error_before_pct REAL,         -- Average error before adjustment

    -- Timing
    timestamp REAL NOT NULL,
    applied_by TEXT DEFAULT 'auto'     -- auto | manual | admin
);

-- Index for audit trail
CREATE INDEX idx_calibration_history_timestamp ON calibration_history(timestamp DESC);
CREATE INDEX idx_calibration_history_parameter ON calibration_history(parameter_name);
```

### Modified Table: model_corrections (no changes needed)

Existing schema already has:
```sql
prompt_tokens INTEGER,           -- Actual input tokens
completion_tokens INTEGER,       -- Actual output tokens
total_cost_usd REAL,            -- Actual cost
```

Link via `task_estimates.actual_execution_id → model_corrections.id`

---

## Implementation Plan

### Phase 1: Foundation (2-4 hours, parallel)

**Task 1: Design Token Estimation Formulas** (2h)
- Document mathematical formulas
- Define complexity multipliers and output ratios
- Create example calculations
- **Deliverable:** Formula specification document

**Task 2: Create Centralized Pricing Config Module** (2h)
- Extract pricing from `tool_cost_tracker.py` and `tool_router.py`
- Create `lib/pricing_config.py`
- Update all files to use centralized module
- **Deliverable:** `lib/pricing_config.py`, no duplicate constants

**Task 3: Research tiktoken vs Heuristic Tradeoffs** (1h)
- Benchmark accuracy vs speed
- Create decision matrix
- **Deliverable:** Recommendation document

### Phase 2: Core Implementation (6-8 hours, sequential)

**Task 4: Extend observability_db.py Schema** (2h, needs Task 2)
- Add `task_estimates` table
- Add `calibration_history` table
- Create migration script
- **Deliverable:** Schema updated, backward compatible

**Task 5: Implement TokenEstimator Class** (3h, needs Task 1, 2)
- Create `lib/token_estimator.py`
- Implement core estimation methods
- Unit tests for formula accuracy
- **Deliverable:** Working TokenEstimator class

**Task 6: Add Estimation Storage Methods** (2h, needs Task 4, 5)
- Extend observability_db.py with CRUD methods
- Add foreign key linking logic
- **Deliverable:** Database integration complete

### Phase 3: Integration & Tools (5-7 hours, parallel)

**Task 7: Create estimate-tokens CLI Tool** (2h, needs Task 5)
- Create `scripts/estimate-tokens.py` (PEP 723)
- Rich terminal output
- **Deliverable:** Standalone CLI tool

**Task 8: Update features.yaml Scripts** (2h, needs Task 5)
- Update `feature-status.py` to show tokens
- Update `feature-execute.py` with token breakdown
- **Deliverable:** Enhanced scripts

**Task 9: Integrate with ctx-plan Command** (3h, needs Task 5, 6)
- Auto-estimate tokens during task creation
- Store estimates in DB
- Add to task YAML frontmatter
- **Deliverable:** /ctx:plan integration

### Phase 4: Validation & Learning (5-7 hours, sequential)

**Task 10: Build Validation System** (3h, needs Task 6, 8)
- Create `lib/estimation_validator.py`
- Implement error calculation (MAPE, bias)
- Query paired estimate + actual from DB
- **Deliverable:** Validation system

**Task 11: Create Accuracy Reporting CLI** (2h, needs Task 10)
- Create `scripts/estimation-accuracy.py`
- Rich tables showing error metrics
- **Deliverable:** Accuracy report CLI

**Task 12: Implement Calibration System** (3h, needs Task 10)
- Create `lib/calibration_engine.py`
- Auto-adjust multipliers monthly
- Log changes to calibration_history
- **Deliverable:** Calibration system

### Phase 5: Testing & Documentation (4-6 hours, sequential)

**Task 13: Comprehensive Testing** (3h)
- Unit tests (formulas, DB operations)
- Integration tests (end-to-end)
- Accuracy tests (historical data)
- **Deliverable:** 90% code coverage

**Task 14: Documentation & Examples** (2h)
- Create `docs/TOKEN_ESTIMATION.md` (user guide)
- Create `docs/ESTIMATION_ARCHITECTURE.md` (this doc)
- Create `docs/CALIBRATION_GUIDE.md`
- Add examples to README
- **Deliverable:** Complete documentation

### Dependency Graph

```
Phase 1 (Parallel):
  Task 1 ──┐
  Task 2 ──┼──> Phase 2
  Task 3 ──┘

Phase 2 (Sequential):
  Task 4 (needs Task 2) ──┐
  Task 5 (needs Task 1,2) ┼──> Phase 3
  Task 6 (needs Task 4,5) ┘

Phase 3 (Parallel):
  Task 7 (needs Task 5) ──┐
  Task 8 (needs Task 5) ──┼──> Phase 4
  Task 9 (needs Task 5,6) ┘

Phase 4 (Sequential):
  Task 10 (needs Task 6,8) ──┐
  Task 11 (needs Task 10) ───┼──> Phase 5
  Task 12 (needs Task 10) ───┘

Phase 5 (Sequential):
  Task 13 (needs all) ──┐
  Task 14 (needs all) ──┘
```

---

## Build vs Buy Decisions

| Component | Decision | Library/Approach | Rationale |
|-----------|----------|------------------|-----------|
| **Token Counting (Input)** | **BUY** | tiktoken | Exact, fast, free, standard |
| **Multi-Model Support** | **BUY** | TokenCost | 400+ models, pricing DB, free |
| **Output Prediction** | **BUILD** | Heuristic multipliers | Simple, good enough, PreflightLLMCost too complex |
| **Database Integration** | **BUILD** | Extend observability_db.py | Already exists, just extend schema |
| **Calibration System** | **BUILD** | Rolling average adjustments | Custom to workflow, no ML needed |
| **CLI Tools** | **BUILD** | Rich + UV scripts | Integrate with existing scripts |

**Dependencies to Add:**
```toml
# pyproject.toml
dependencies = [
    "tiktoken>=0.5.0",      # Exact token counting
    "tokencost>=0.1.0",     # Multi-model pricing
    # ... existing deps
]
```

---

## Success Criteria

### Functional Success

✅ **Estimation Accuracy**
- Initial: ±25-30% error (baseline)
- Month 1: ±15-20% error
- Month 3: ±10-15% error

✅ **Performance**
- Single task estimation: <100ms
- Batch (15 tasks): <500ms
- CLI tools responsive (<1s total)

✅ **Integration**
- features.yaml scripts show tokens correctly
- /ctx:plan auto-estimates new tasks
- Observability DB tracks estimates + actuals

✅ **Validation**
- Accuracy reports show error by task type
- Trends visible over time
- Systematic bias identified and corrected

✅ **Calibration**
- Auto-adjusts formulas monthly
- Improves accuracy by ≥5% within 30 days
- Logs all changes for audit trail

### User Acceptance

✅ Users can estimate token cost before starting work
✅ Cost-aware decisions enabled (Haiku vs Sonnet, parallelization)
✅ Historical accuracy data builds confidence in estimates
✅ System learns and improves without manual intervention

---

## Next Steps

1. **Review & Approve:** Team reviews this architecture
2. **Phase 1 Kickoff:** Start foundation tasks (all parallel)
3. **Implement Phase 2-3:** Core engine + integration
4. **Collect Data:** Start storing estimates from day 1
5. **Validate & Calibrate:** Phase 4-5 after 2 weeks of data

---

## Appendix A: Token Estimation Formula Reference Card

```python
# Quick Reference

# 1. Context Tokens
context = sum(file_tokens) + description_tokens
# Heuristic: file_chars/4 or lines*2

# 2. Reasoning Tokens
reasoning = context * {
    "simple": 0.15,
    "medium": 0.30,
    "complex": 0.75
}[complexity]

# 3. Output Tokens
output = context * {
    "read": 0.05,
    "plan": 0.225,
    "implement": 0.16,
    "test": 0.20,
    "analyze": 0.40
}[task_type]

# 4. Total
input_tokens = context + reasoning
output_tokens = output
total_tokens = input_tokens + output_tokens

# 5. Cost
cost_haiku = (input * 0.25 + output * 1.25) / 1_000_000
cost_sonnet = (input * 3.00 + output * 15.00) / 1_000_000
```

---

## Appendix B: Research Sources

- Anthropic Token Counting API: https://docs.claude.com/en/docs/build-with-claude/token-counting
- Tiktoken: https://github.com/openai/tiktoken
- TokenCost: https://github.com/AgentOps-AI/tokencost
- PreflightLLMCost: https://github.com/aatakansalar/PreflightLLMCost
- TALE Framework (Token Budget Awareness): Research paper, Dec 2024
- LangChain Token Tracking: https://python.langchain.com/docs/guides/productionization/callbacks/

---

**End of Architecture Document**
