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
