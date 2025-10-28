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
