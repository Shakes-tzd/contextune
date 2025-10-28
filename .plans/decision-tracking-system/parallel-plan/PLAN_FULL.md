# Development Plan: Unified Decision Tracking System

**Created:** 20251028-011700
**Status:** ready

---

## 📋 Overview

Complete unified decision tracking system that solves changelog bloat via
bounded selective context loading. Auto-populates from 1,236 historical
conversations, integrates features.yaml, links to observability_db.py.
Replaces manual CHANGELOG with queryable decisions.yaml (10K vs 150K tokens).
# Research synthesis
research:
approach: "Extend extraction-optimized system with decisions.yaml layer"
libraries:
  - name: "pyyaml"

---

---
id: task-0
priority: blocker
status: pending
dependencies: []
labels:
  - parallel-execution
  - auto-created
  - priority-blocker
---

# Create decisions.yaml Schema with Features Integration

## 🎯 Objective

Create the decisions.yaml schema that integrates features.yaml, provides conversation linking, and enables selective context loading. This is the foundation file that replaces manual CHANGELOG with bounded, queryable decision tracking.

## 🛠️ Implementation Approach

Based on scratch_pad.md design:

**Schema structure:**
```yaml
metadata:
  project: "contextune"
  last_scan: "timestamp"
  auto_population_enabled: true

conversations:
  scanned_count: 1236
  sessions_with_decisions: 15

research:
  - id: "res-001"
    topic: "..."
    findings: [...]
    conversation_link: {session_id, timestamp, history_line}
    expires_at: "6 months from creation"

plans:
  - id: "plan-001"
    title: "..."
    design_file: ".plans/[topic]/design.md"
    conversation_link: {...}
    archived_at: "90 days after completion"

decisions:
  - id: "dec-001"
    title: "..."
    context: "..."
    alternatives: [...]
    rationale: "..."
    conversation_link: {...}
    permanent: true

features:
  - id: "feat-001" (from features.yaml)
    based_on_decision: ["dec-001"]
    conversation_link: {...}
    status: "planned|in_progress|completed"
```

**Pattern to follow:**
- **File:** `scripts/feature-status.py:1-270`
- **Description:** YAML structure with Rich output formatting

## 📁 Files to Touch

**Create:**
- `decisions.yaml` (root of project)

## 🧪 Tests Required

**Unit:**
- [ ] Test YAML schema validation
- [ ] Test all sections parse correctly
- [ ] Test conversation_link structure

**Integration:**
- [ ] Test features.yaml import
- [ ] Test .plans/ reference linking

## ✅ Acceptance Criteria

- [ ] decisions.yaml created with all 5 sections
- [ ] Valid YAML syntax
- [ ] Features.yaml entries importable
- [ ] Conversation link structure defined
- [ ] Lifecycle fields present (expires_at, archived_at)

## ⚠️ Potential Conflicts

None - creates new file

## 📝 Notes

This file is the foundation. Tasks 1-4 will populate and query it.
Must include Context, Alternatives, Rationale sections to preserve fidelity.

---

**Worktree:** `worktrees/task-0`
**Branch:** `feature/task-0-decisions-schema`

🤖 Auto-created via Contextune parallel execution

---

---
id: task-1
priority: blocker
status: pending
dependencies:
  - task-0
labels:
  - parallel-execution
  - auto-created
  - priority-blocker
---

# Implement decision-sync.py for History Auto-Population

## 🎯 Objective

Create decision-sync.py script that scans ~/.claude/history.jsonl (1,236 conversations) and auto-populates decisions.yaml with research, plans, and decisions found in past conversations.

## 🛠️ Implementation Approach

**Keywords to detect:**
- Research: "research", "/ctx:research", "investigate", "explore", "compare"
- Plans: "/ctx:plan", "create plan", "break down", "design", "architecture"
- Decisions: "decided to", "why did we choose", "alternatives considered"

**Pattern to follow:**
- **File:** `hooks/session_end_extractor.py:113-170`
- **Description:** Pattern-based extraction from transcripts

**Libraries:**
- `pyyaml` - YAML reading/writing
- `json` - history.jsonl parsing

## 📁 Files to Touch

**Create:**
- `scripts/decision-sync.py`

**Read:**
- `~/.claude/history.jsonl`
- `lib/observability_db.py` (for session linking)

**Modify:**
- `decisions.yaml` (append entries)

## 🧪 Tests Required

**Unit:**
- [ ] Test history.jsonl parsing
- [ ] Test keyword detection
- [ ] Test YAML appending (doesn't corrupt file)

**Integration:**
- [ ] Test with real history.jsonl (1,236 entries)
- [ ] Test duplicate detection (don't re-add same entry)
- [ ] Test decisions.yaml grows correctly

## ✅ Acceptance Criteria

- [ ] Scans all 1,236 history.jsonl entries
- [ ] Detects research/plans/decisions via keywords
- [ ] Appends to decisions.yaml without corruption
- [ ] Links to conversation via timestamp
- [ ] Handles missing/corrupted history entries gracefully
- [ ] Progress output (Rich library)

## ⚠️ Potential Conflicts

**Files:**
- `decisions.yaml` - Task-3 also writes → Use atomic operations

## 📝 Notes

This is retroactive population - scans past conversations.
Task-3 handles ongoing population (new sessions).

Together they cover: historical + future.

---

**Worktree:** `worktrees/task-1`
**Branch:** `feature/task-1-decision-sync`

🤖 Auto-created via Contextune parallel execution

---

---
id: task-2
priority: high
status: pending
dependencies:
  - task-1
labels:
  - parallel-execution
  - auto-created
  - priority-high
---

# Implement decision-link.py for Observability DB Linking

## 🎯 Objective

Create decision-link.py script that links decisions.yaml entries to observability_db.py sessions, enabling full context chain: conversation → session → detections → performance metrics.

## 🛠️ Implementation Approach

**Cross-reference strategy:**
- Match timestamps between decisions.yaml and observability DB
- Link session_id from conversation to sessions table
- Add detection_id links for intent detection events

**Pattern to follow:**
- **File:** `lib/observability_db.py:68-189`
- **Description:** Database query patterns, session tracking

**Libraries:**
- `sqlite3` - Query observability.db
- `pyyaml` - Update decisions.yaml with links

## 📁 Files to Touch

**Create:**
- `scripts/decision-link.py`

**Read:**
- `lib/observability_db.py` (session schema)
- `~/.claude/plugins/contextune/data/observability.db`

**Modify:**
- `decisions.yaml` (add observability_link fields)

## 🧪 Tests Required

**Unit:**
- [ ] Test timestamp matching logic
- [ ] Test session_id lookup
- [ ] Test YAML link field writing

**Integration:**
- [ ] Test with real observability.db
- [ ] Test link accuracy (timestamps match)
- [ ] Test missing session handling

## ✅ Acceptance Criteria

- [ ] Links decisions to observability sessions
- [ ] Timestamp matching works reliably
- [ ] Handles missing sessions gracefully
- [ ] Updates decisions.yaml without corruption
- [ ] Progress reporting with Rich

## ⚠️ Potential Conflicts

**Files:**
- `decisions.yaml` - Task-1, Task-3 also modify → Run sequentially after task-1

## 📝 Notes

Read-only access to observability.db (no conflicts).
Enhances decisions.yaml entries with observability links for full traceability.

---

**Worktree:** `worktrees/task-2`
**Branch:** `feature/task-2-decision-link`

🤖 Auto-created via Contextune parallel execution

---

---
id: task-3
priority: high
status: pending
dependencies:
  - task-0
labels:
  - parallel-execution
  - auto-created
  - priority-high
---

# Enhance SessionEnd to Populate decisions.yaml

## 🎯 Objective

Enhance hooks/session_end_extractor.py to not only extract designs to .plans/ but also extract decisions to decisions.yaml. This enables ongoing automatic population as work happens.

## 🛠️ Implementation Approach

**Extend existing SessionEnd hook:**
- Keep design extraction to .plans/ (existing)
- Add decision extraction to decisions.yaml (new)
- Detect decision patterns in transcripts
- Append to decisions.yaml with conversation links

**Pattern to follow:**
- **File:** `hooks/session_end_extractor.py:205-253`
- **Description:** extract_decisions() function (already has skeleton)

**Libraries:**
- `pyyaml` - YAML appending
- `json` - Transcript parsing

## 📁 Files to Touch

**Modify:**
- `hooks/session_end_extractor.py` (enhance append_decisions function)

**Write to:**
- `decisions.yaml` (append decision entries)

## 🧪 Tests Required

**Unit:**
- [ ] Test decision pattern detection
- [ ] Test YAML appending doesn't corrupt
- [ ] Test conversation link creation

**Integration:**
- [ ] Test with extraction-optimized format transcripts
- [ ] Test decisions.yaml grows correctly
- [ ] Test .plans/ extraction still works

## ✅ Acceptance Criteria

- [ ] Detects decisions in transcripts (## Decision: patterns)
- [ ] Extracts context, alternatives, rationale
- [ ] Appends to decisions.yaml atomically
- [ ] Links to conversation (session_id, timestamp)
- [ ] Doesn't break existing .plans/ extraction

## ⚠️ Potential Conflicts

**Files:**
- `hooks/session_end_extractor.py` - Only this task modifies → No conflict
- `decisions.yaml` - Task-1, Task-2 also write → Sequential execution safe

## 📝 Notes

This is ongoing population (new sessions).
Task-1 is retroactive (historical conversations).

Together: complete coverage of all conversations.

---

**Worktree:** `worktrees/task-3`
**Branch:** `feature/task-3-sessionend-enhancement`

🤖 Auto-created via Contextune parallel execution

---

---
id: task-4
priority: medium
status: pending
dependencies:
  - task-0
  - task-1
labels:
  - parallel-execution
  - auto-created
  - priority-medium
---

# Implement Selective Context Loading

## 🎯 Objective

Create system for selective context loading from decisions.yaml. Instead of importing entire file (10K tokens), query for specific topics/decisions (2-5K tokens). This is what makes it superior to traditional CHANGELOG.

## 🛠️ Implementation Approach

**Query interface:**
```python
# Load decisions about specific topic
load_decisions(topic="authentication")  # Returns 2-5K tokens

# vs loading entire decisions.yaml
load_all_decisions()  # Returns 10K tokens

# vs loading CHANGELOG.md
load_changelog()  # Returns 15K-150K tokens (bloat!)
```

**Implementation:**
- CLI script: `scripts/decision-query.py`
- SessionStart hook integration (optional)
- Tag-based filtering
- Timestamp-based filtering
- Lifecycle-aware (skip expired research)

**Pattern to follow:**
- **File:** `scripts/feature-status.py:163-203`
- **Description:** Filtering and Rich output formatting

**Libraries:**
- `pyyaml` - YAML querying
- `rich` - Beautiful CLI output

## 📁 Files to Touch

**Create:**
- `scripts/decision-query.py`
- `hooks/selective_context_loader.js` (optional SessionStart enhancement)

**Read:**
- `decisions.yaml`

## 🧪 Tests Required

**Unit:**
- [ ] Test topic filtering
- [ ] Test tag filtering
- [ ] Test lifecycle expiration logic
- [ ] Test token count estimation

**Integration:**
- [ ] Test selective load vs full load (measure tokens)
- [ ] Test with real decisions.yaml
- [ ] Test expired entry filtering

## ✅ Acceptance Criteria

- [ ] Can query decisions by topic
- [ ] Can query decisions by tags
- [ ] Respects lifecycle (filters expired research)
- [ ] Returns 2-5K tokens (vs 10K full file)
- [ ] Rich CLI output
- [ ] Optional SessionStart integration

## ⚠️ Potential Conflicts

None - read-only queries

## 📝 Notes

This is the KEY differentiator vs CHANGELOG:
- CHANGELOG: All or nothing (15K-150K tokens)
- decisions.yaml: Selective query (2-5K tokens)
- Savings: 83-97% context reduction

Example use:
```bash
# Load auth decisions only
./scripts/decision-query.py --topic authentication

# Load recent decisions (last 30 days)
./scripts/decision-query.py --since 30d

# Load high-impact decisions
./scripts/decision-query.py --impact high
```

---

**Worktree:** `worktrees/task-4`
**Branch:** `feature/task-4-selective-loading`

🤖 Auto-created via Contextune parallel execution

---

