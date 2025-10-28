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
