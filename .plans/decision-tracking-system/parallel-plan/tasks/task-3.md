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
