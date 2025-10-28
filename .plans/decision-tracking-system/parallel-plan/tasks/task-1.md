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
