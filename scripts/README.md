# Feature Management Scripts

**Purpose:** Manage feature improvements using `features.yaml` tracking system.

---

## Quick Start

```bash
# View all features
./scripts/feature-status.sh

# View dependency graph
./scripts/feature-graph.sh

# Execute a feature
./scripts/feature-execute.sh feat-001

# Mark feature as completed
./scripts/feature-complete.sh feat-001
```

---

## Scripts

### 1. feature-status.sh

**Purpose:** Show feature status, dependencies, and execution recommendations.

**Usage:**
```bash
./scripts/feature-status.sh [OPTIONS]

Options:
  --phase N               Show only Phase N features
  --priority LEVEL        Show only PRIORITY features (critical, high, medium, low)
  --status STATUS         Show only STATUS features (planned, in_progress, completed, blocked)
```

**Examples:**
```bash
# Show all features
./scripts/feature-status.sh

# Show Phase 1 features only
./scripts/feature-status.sh --phase 1

# Show critical priority features
./scripts/feature-status.sh --priority critical

# Show planned features
./scripts/feature-status.sh --status planned
```

**Output:**
- Summary statistics
- Feature list with status, priority, phase, effort
- Dependencies
- Execution recommendations (ready vs blocked)

---

### 2. feature-execute.sh

**Purpose:** Execute feature implementation by creating worktree.

**Usage:**
```bash
./scripts/feature-execute.sh FEATURE_ID
```

**What it does:**
1. Validates feature exists
2. Checks dependencies are completed
3. Shows implementation plan
4. Creates git worktree (`worktrees/FEATURE_ID`)
5. Creates feature branch (`feature/FEATURE_ID`)
6. Updates feature status to `in_progress`
7. Commits status change

**Example:**
```bash
# Execute feat-001 (Haiku 4.5 Integration)
./scripts/feature-execute.sh feat-001

# Creates:
#   worktrees/feat-001/
#   Branch: feature/feat-001
#   Status: in_progress
```

**Dependency Checking:**
- If feature has dependencies, checks they are completed
- Blocks execution if dependencies not met
- Shows which dependencies need completion first

---

### 3. feature-graph.sh

**Purpose:** Generate dependency graph visualization.

**Usage:**
```bash
./scripts/feature-graph.sh [--format FORMAT]

Formats:
  text      ASCII art visualization (default)
  dot       Graphviz DOT format
  mermaid   Mermaid diagram format
```

**Examples:**
```bash
# Text format (terminal)
./scripts/feature-graph.sh

# Generate PNG image
./scripts/feature-graph.sh --format dot > graph.dot
dot -Tpng graph.dot -o feature-graph.png

# Generate Mermaid diagram (for GitHub)
./scripts/feature-graph.sh --format mermaid > GRAPH.md
```

**Output (text format):**
- Dependency tree
- Phase grouping
- Parallel execution groups
- Status symbols (✓ completed, → in progress, ○ planned, ✗ blocked)

---

### 4. feature-complete.sh

**Purpose:** Mark feature as completed.

**Usage:**
```bash
./scripts/feature-complete.sh FEATURE_ID
```

**What it does:**
1. Validates feature exists
2. Updates feature status to `completed`
3. Commits status change
4. Shows features now unblocked
5. Shows overall progress

**Example:**
```bash
# Mark feat-001 as completed
./scripts/feature-complete.sh feat-001

# Output:
#   ✓ Status updated to: completed
#   ✓ Committed status change
#
#   Features now unblocked:
#     ✓ feat-003: PreToolUse Input Modifications
#     ✓ feat-004: Explore Subagent Integration
#
#   Overall Progress:
#     Completed: 2 / 15 (13%)
```

---

## Workflow

### Standard Feature Implementation

```bash
# 1. Check status
./scripts/feature-status.sh --phase 1

# 2. View dependencies
./scripts/feature-graph.sh

# 3. Execute independent feature
./scripts/feature-execute.sh feat-001

# 4. Work in worktree
cd worktrees/feat-001
# ... make changes ...
git add .
git commit -m "feat(feat-001): implement Haiku 4.5 integration"
git push -u origin feature/feat-001

# 5. Create PR, get reviewed, merge

# 6. Mark as completed
cd ../..
./scripts/feature-complete.sh feat-001

# 7. Check what's unblocked
./scripts/feature-status.sh
```

### Parallel Execution

```bash
# 1. Identify independent features (Phase 1)
./scripts/feature-status.sh --phase 1

# Output shows:
#   Ready to execute (no dependencies):
#     • feat-001: Haiku 4.5 Integration (Phase 1)
#     • feat-002: AskUserQuestion Integration (Phase 1)
#     • feat-006: SessionEnd Hook Analytics (Phase 1)

# 2. Execute all in parallel
./scripts/feature-execute.sh feat-001
./scripts/feature-execute.sh feat-002
./scripts/feature-execute.sh feat-006

# 3. Work on all simultaneously
#    worktrees/feat-001/
#    worktrees/feat-002/
#    worktrees/feat-006/

# 4. Complete as they finish
./scripts/feature-complete.sh feat-001
./scripts/feature-complete.sh feat-002
./scripts/feature-complete.sh feat-006
```

### Handling Dependencies

```bash
# 1. Try to execute dependent feature
./scripts/feature-execute.sh feat-003

# Output:
#   Error: Dependencies not met
#     ✗ feat-001: Haiku 4.5 Integration (status: planned)
#   Complete dependent features first, then try again

# 2. Complete dependency first
./scripts/feature-execute.sh feat-001
# ... implement ...
./scripts/feature-complete.sh feat-001

# 3. Now unblocked
./scripts/feature-execute.sh feat-003
# Success!
```

---

## Features.yaml Format

The `features.yaml` file tracks all improvements with:

**Metadata:**
- `id`: Unique feature ID (feat-001, feat-002, etc.)
- `name`: Human-readable name
- `status`: planned | in_progress | completed | blocked | deprecated | research
- `priority`: critical | high | medium | low
- `phase`: 0-4 (execution phase)
- `category`: cost-optimization, ux-improvement, reliability, etc.

**Impact:**
- `cost`: Cost impact (e.g., "-40% to -50%")
- `performance`: Performance impact
- `reliability`: Reliability impact
- `ux`: UX impact
- `score`: Numerical impact score (1-10)

**Effort:**
- `estimate_hours`: Estimated hours to implement
- `complexity`: low | medium | high
- `risk`: low | medium | high
- `score`: Numerical effort score (1-10)

**Dependencies:**
- `dependencies`: Array of feature IDs this depends on
- `blocks`: Array of feature IDs this blocks
- `benefits_from`: Features that enhance this (optional)
- `complementary_with`: Related features (optional)

**Implementation:**
- `files`: Files to create/modify
- `changes`: List of changes to make
- `lines_changed`: Estimated lines changed

**Testing:**
- Array of test scenarios

**Metadata:**
- `release_note`: Claude Code version that added this capability
- `created`: Date created
- `assigned_to`: Who's working on it
- `estimated_value`: Business value estimate

---

## Integration with Contextune Commands

### Future: /ctx:improve Command

These scripts are the foundation for a future `/ctx:improve` command that will:

1. **Analyze:** Scan release notes, issues, tech debt
2. **Catalog:** Add to features.yaml automatically
3. **Prioritize:** Score by impact vs effort
4. **Execute:** Create worktrees with one command
5. **Track:** Show progress in real-time

**Different from /ctx:plan:**
- `/ctx:plan`: Plan NEW features (forward-looking)
- `/ctx:improve`: Track EXISTING improvements (backward-looking)

**Complementary:**
```bash
# Typical workflow:
1. /ctx:improve analyze --source release-notes.md
2. /ctx:improve prioritize
3. /ctx:plan (for complex features)
4. /ctx:improve execute feat-001 (for simple features)
5. /ctx:execute (for planned features)
```

---

## Tips

### Finding Work

```bash
# Show what's ready to work on
./scripts/feature-status.sh | grep "Ready to execute"

# Show highest value features
./scripts/feature-status.sh --priority critical
```

### Parallel Execution

```bash
# Phase 1 features can usually run in parallel
./scripts/feature-status.sh --phase 1

# Check graph to confirm independence
./scripts/feature-graph.sh
```

### Tracking Progress

```bash
# See overall progress
./scripts/feature-status.sh | head -20

# See completion percentage
./scripts/feature-complete.sh feat-001
# Shows: Completed: 2 / 15 (13%)
```

### Visualizations

```bash
# Generate pretty graph for GitHub
./scripts/feature-graph.sh --format mermaid > docs/FEATURE_GRAPH.md

# Generate image for presentations
./scripts/feature-graph.sh --format dot > graph.dot
dot -Tpng graph.dot -o docs/feature-graph.png
```

---

## Requirements

- **yq:** YAML processor
  ```bash
  brew install yq
  ```

- **Git:** For worktree management
  ```bash
  # Already installed with Claude Code
  ```

- **Optional: Graphviz** (for dot format)
  ```bash
  brew install graphviz
  ```

---

## Troubleshooting

### "yq: command not found"

Install yq:
```bash
brew install yq
```

### "Worktree already exists"

Remove manually:
```bash
git worktree remove worktrees/feat-001 --force
```

### "Dependencies not met"

Complete dependent features first:
```bash
./scripts/feature-graph.sh
# See what needs to be done first
```

### "Feature not found"

Check feature ID:
```bash
./scripts/feature-status.sh | grep feat-
```

---

## Examples

### Example 1: Implement High-Priority Feature

```bash
# 1. Find high-priority feature
./scripts/feature-status.sh --priority critical

# Output shows: feat-001 (Haiku 4.5 Integration)

# 2. Execute
./scripts/feature-execute.sh feat-001

# 3. Implement in worktree
cd worktrees/feat-001
# ... edit hooks/user_prompt_submit.py ...
# ... update model string to claude-haiku-4-5-20250929 ...
git commit -am "feat(feat-001): upgrade to Haiku 4.5"

# 4. Test
# ... run tests ...

# 5. Push and create PR
git push -u origin feature/feat-001

# 6. After merge, mark complete
cd ../..
./scripts/feature-complete.sh feat-001
```

### Example 2: Parallel Execution (Phase 1)

```bash
# Execute 3 independent features in parallel
./scripts/feature-execute.sh feat-001 &
./scripts/feature-execute.sh feat-002 &
./scripts/feature-execute.sh feat-006 &
wait

# Work on all simultaneously
# Terminal 1: cd worktrees/feat-001 && vim ...
# Terminal 2: cd worktrees/feat-002 && vim ...
# Terminal 3: cd worktrees/feat-006 && vim ...

# Complete as they finish
./scripts/feature-complete.sh feat-001
./scripts/feature-complete.sh feat-002
./scripts/feature-complete.sh feat-006
```

### Example 3: Check What's Unblocked

```bash
# After completing feat-001
./scripts/feature-complete.sh feat-001

# Output shows:
#   Features now unblocked:
#     ✓ feat-003: PreToolUse Input Modifications
#     ✓ feat-004: Explore Subagent Integration
#
#   You can now execute:
#     ./scripts/feature-execute.sh feat-003
#     ./scripts/feature-execute.sh feat-004
```

---

## Contributing

When adding new features to `features.yaml`:

1. Use next sequential ID (feat-016, feat-017, etc.)
2. Fill in all required fields
3. Add dependencies if applicable
4. Set reasonable effort estimates
5. Update summary statistics
6. Run validation:
   ```bash
   yq . features.yaml > /dev/null
   # Should produce no errors
   ```

---

**Version:** 1.0
**Created:** 2025-10-27
**Maintained by:** Contextune team
