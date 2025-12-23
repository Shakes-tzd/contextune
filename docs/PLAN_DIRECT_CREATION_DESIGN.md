# Design: Direct Plan File Creation for `/ctx:plan`

**Feature:** feat-3e7e6183
**Created:** 2025-12-23
**Status:** Design

---

## Problem Statement

The current `/ctx:plan` workflow is error-prone:

1. `/ctx:plan` outputs plan in markdown (conversation only)
2. User runs `/ctx:execute`
3. `extract-current-plan.sh` finds transcript
4. `extract-plan-from-context.py` parses transcript using regex
5. **Problem:** Parsing often fails due to format mismatches

**Failure Mode Example:**
```
⚠️  Warning: No YAML frontmatter for task-0
⚠️  Warning: No YAML frontmatter for task-1
❌ Error: No tasks found in content
```

---

## Proposed Solution: Hybrid Approach

**Have `/ctx:plan` do BOTH:**
1. **Create files directly** using Write tool (reliability)
2. **Output summary** to conversation (visibility)

### Benefits

✅ **Reliable:** No parsing, no regex, no extraction failures
✅ **Visible:** User still sees plan summary in conversation
✅ **Iterable:** User can request changes, we update files directly
✅ **Immediate:** Files ready for `/ctx:execute` instantly
✅ **DRY:** Single source of truth (the files), summary derived from files

### Trade-offs

❌ **More tokens:** Write tool calls add ~500 tokens per file
✅ **But:** Saves 5-10K tokens from failed extraction attempts
✅ **Net:** Token savings overall due to fewer retries

---

## New Workflow

### Phase 1: Research (Unchanged)
- Spawn 5 parallel research agents
- Synthesize findings

### Phase 2: Plan Creation (NEW!)

**2.1: Create Plan Structure**

```python
# Create .parallel/plans/ directory structure
plan_dir = Path(".parallel/plans")
plan_dir.mkdir(parents=True, exist_ok=True)
(plan_dir / "tasks").mkdir(exist_ok=True)
(plan_dir / "templates").mkdir(exist_ok=True)
(plan_dir / "scripts").mkdir(exist_ok=True)
```

**2.2: Write plan.yaml**

```python
plan_data = {
    "metadata": {
        "name": "Feature Name",
        "created": "20251223-105000",
        "status": "ready"
    },
    "overview": "...",
    "research": {...},  # From research phase
    "tasks": [
        {
            "id": "task-0",
            "name": "Task Name",
            "file": "tasks/task-0.md",
            "priority": "blocker",
            "dependencies": []
        },
        # ...
    ],
    "shared_resources": {...},
    "testing": {...},
    "success_criteria": [...]
}

# Write plan.yaml
Write(
    file_path=".parallel/plans/plan.yaml",
    content=yaml.dump(plan_data)
)
```

**2.3: Write task-N.md files**

For each task:

```python
task_content = f"""---
id: task-{N}
priority: high
status: pending
dependencies: []
---

# {Task Name}

## 🎯 Objective
{...}

## 🛠️ Implementation
{...}

## 📁 Files
{...}

## ✅ Acceptance Criteria
{...}
"""

Write(
    file_path=f".parallel/plans/tasks/task-{N}.md",
    content=task_content
)
```

**2.4: Output Summary to Conversation**

After creating all files, output:

```
📋 Plan created and saved to `.parallel/plans/`

**Files Created:**
- plan.yaml (master plan with 5 tasks)
- tasks/task-0.md - Shared Data Models (blocker)
- tasks/task-1.md - Auto-tracking Hooks (high)
- tasks/task-2.md - Unified Config (high)
- tasks/task-3.md - Dashboard Views (medium)
- tasks/task-4.md - Documentation (low)

**Plan Summary:**
- 5 total tasks
- 3 can run in parallel
- 2 have dependencies
- Estimated: 75,000 tokens (~$0.089 with Haiku)

**Next Steps:**
- Review files: `cat .parallel/plans/plan.yaml`
- Request changes: "Change task 2 to use Redis"
- Execute: `/ctx:execute` (files already ready!)

Ready to execute? Run `/ctx:execute` to start parallel development.
```

---

## Implementation Plan

### 1. Create Plan Builder Module

**File:** `lib/plan_builder.py`

```python
from pathlib import Path
from typing import Any
import yaml
from datetime import datetime

class PlanBuilder:
    """Build and write plan files directly."""

    def __init__(self, name: str, output_dir: str = ".parallel/plans"):
        self.name = name
        self.output_dir = Path(output_dir)
        self.tasks = []
        self.research = {}
        self.plan_data = {
            "metadata": {
                "name": name,
                "created": datetime.now().strftime("%Y%m%d-%H%M%S"),
                "status": "ready"
            }
        }

    def set_research(self, research: dict) -> 'PlanBuilder':
        """Set research synthesis results."""
        self.plan_data["research"] = research
        return self

    def add_task(
        self,
        id: str,
        name: str,
        priority: str,
        content: str,
        dependencies: list[str] = None
    ) -> 'PlanBuilder':
        """Add a task to the plan."""
        self.tasks.append({
            "id": id,
            "name": name,
            "file": f"tasks/{id}.md",
            "priority": priority,
            "dependencies": dependencies or [],
            "content": content
        })
        return self

    def set_metadata(self, **kwargs) -> 'PlanBuilder':
        """Set plan metadata fields."""
        self.plan_data.update(kwargs)
        return self

    def build(self) -> dict[str, Path]:
        """
        Write all plan files and return paths.

        Returns:
            dict mapping file types to paths created
        """
        # Create directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        tasks_dir = self.output_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)
        (self.output_dir / "templates").mkdir(exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)

        created_files = {}

        # Build task references for plan.yaml
        self.plan_data["tasks"] = [
            {
                "id": t["id"],
                "name": t["name"],
                "file": t["file"],
                "priority": t["priority"],
                "dependencies": t["dependencies"]
            }
            for t in self.tasks
        ]

        # Write plan.yaml
        plan_file = self.output_dir / "plan.yaml"
        with open(plan_file, 'w') as f:
            yaml.dump(self.plan_data, f, default_flow_style=False, sort_keys=False)
        created_files["plan"] = plan_file

        # Write task files
        task_files = []
        for task in self.tasks:
            task_file = tasks_dir / f"{task['id']}.md"
            with open(task_file, 'w') as f:
                f.write(task["content"])
            task_files.append(task_file)

        created_files["tasks"] = task_files

        return created_files
```

### 2. Update `/ctx:plan` Command

**File:** `commands/ctx-plan.md`

**Changes:**

```diff
## Step 3: Output Extraction-Optimized Plan Format

-**IMPORTANT:** Do NOT use the Write tool. Output the plan in structured format in the conversation.
+**IMPORTANT:** Create plan files directly using the PlanBuilder.

-The `/ctx:execute` command will extract this automatically to modular files when the user runs it.
+Files are created immediately and ready for `/ctx:execute`.
```

**Add new section:**

```markdown
## Step 3: Create Plan Files Directly

Use the PlanBuilder to create plan files:

```python
from lib.plan_builder import PlanBuilder

# Initialize builder
builder = PlanBuilder(name="Feature Name")

# Add research synthesis
builder.set_research({
    "approach": "...",
    "libraries": [...],
    # ...from research phase
})

# Add metadata
builder.set_metadata(
    overview="What we're building",
    shared_resources={...},
    testing={...},
    success_criteria=[...]
)

# Add tasks
builder.add_task(
    id="task-0",
    name="Shared Data Models",
    priority="blocker",
    dependencies=[],
    content="""---
id: task-0
priority: blocker
status: pending
dependencies: []
---

# Shared Data Models

## 🎯 Objective
...
"""
)

builder.add_task(
    id="task-1",
    name="Auto-tracking Hooks",
    priority="high",
    dependencies=["task-0"],
    content="""..."""
)

# Build files
created = builder.build()

# Output summary to conversation
print(f"✅ Created plan files:")
for file_type, paths in created.items():
    if isinstance(paths, list):
        for path in paths:
            print(f"  - {path}")
    else:
        print(f"  - {paths}")
```
```

### 3. Update `/ctx:execute` Command

**File:** `commands/ctx-execute.md`

**Changes:**

```diff
## Phase 1: Extract and Load Plan

-**Primary:** Always try extraction from transcript first
-**Fallback:** Direct file read if extraction fails
+**Primary:** Direct file read (plan files already exist)
+**Fallback:** Extraction from transcript (deprecated, for old plans only)

## Step 1: Load Plan Files

```python
import yaml
from pathlib import Path

# Load plan.yaml directly
plan_path = Path(".parallel/plans/plan.yaml")
if not plan_path.exists():
+    # Fallback: Try extraction (deprecated)
+    print("⚠️ No plan.yaml found, trying extraction...")
+    run_extraction()

with open(plan_path) as f:
    plan = yaml.safe_load(f)

# Tasks already exist as individual files
tasks = plan["tasks"]
```
```

### 4. Deprecate Extraction Scripts

**File:** `scripts/extract-current-plan.sh`

Add deprecation notice:

```bash
echo "⚠️  DEPRECATED: This script is no longer needed." >&2
echo "   /ctx:plan now creates files directly." >&2
echo "   This script remains for backward compatibility with old transcripts." >&2
```

---

## Migration Strategy

### Phase 1: Add PlanBuilder (This PR)
- Create `lib/plan_builder.py`
- Add tests for PlanBuilder
- No breaking changes yet

### Phase 2: Update `/ctx:plan` (Next PR)
- Update command to use PlanBuilder
- Keep extraction as fallback
- Update documentation

### Phase 3: Update `/ctx:execute` (Next PR)
- Prefer direct file read
- Extraction becomes fallback
- Update documentation

### Phase 4: Deprecate Extraction (Future)
- Add deprecation warnings
- Remove from default workflow
- Keep for old plan compatibility

---

## Testing Strategy

### Unit Tests

```python
def test_plan_builder_creates_files():
    """Test that PlanBuilder creates all expected files."""
    builder = PlanBuilder("Test Plan", output_dir="/tmp/test-plans")

    builder.add_task(
        id="task-0",
        name="Test Task",
        priority="high",
        content="# Test\nContent here"
    )

    created = builder.build()

    assert (Path("/tmp/test-plans/plan.yaml")).exists()
    assert (Path("/tmp/test-plans/tasks/task-0.md")).exists()

def test_plan_builder_yaml_valid():
    """Test that generated YAML is valid."""
    builder = PlanBuilder("Test")
    builder.add_task("task-0", "Test", "high", "content")
    builder.build()

    with open(".parallel/plans/plan.yaml") as f:
        data = yaml.safe_load(f)

    assert data["metadata"]["name"] == "Test"
    assert len(data["tasks"]) == 1
```

### Integration Tests

```python
def test_ctx_plan_creates_files(tmp_path):
    """Test that /ctx:plan creates all files."""
    # Run /ctx:plan command
    # ...

    # Verify files exist
    assert (tmp_path / ".parallel/plans/plan.yaml").exists()
    assert (tmp_path / ".parallel/plans/tasks/task-0.md").exists()

def test_ctx_execute_loads_direct_files(tmp_path):
    """Test that /ctx:execute loads plan from files."""
    # Create plan files
    # Run /ctx:execute
    # Verify it loaded from files, not extraction
```

---

## Success Criteria

- [ ] PlanBuilder creates valid plan.yaml
- [ ] PlanBuilder creates task-N.md files with correct format
- [ ] `/ctx:plan` uses PlanBuilder successfully
- [ ] `/ctx:execute` loads files directly (no extraction)
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Zero extraction failures in testing

---

## Rollback Plan

If direct file creation causes issues:

1. Revert `/ctx:plan` to output-only mode
2. Re-enable extraction as primary path
3. PlanBuilder remains available for manual use

No data loss - extraction scripts still work for old plans.

---

## Token Cost Analysis

**Current (Extraction):**
- Plan output: 3,000 tokens
- Extraction attempt 1: 2,000 tokens (fail)
- Retry with corrections: 2,000 tokens (fail)
- Manual file creation: 3,000 tokens
- **Total: ~10,000 tokens** (with failures)

**New (Direct):**
- Plan creation: 3,000 tokens
- Write tool calls: 500 tokens × 6 files = 3,000 tokens
- Summary output: 500 tokens
- **Total: ~6,500 tokens** (reliable)

**Savings: 35% reduction + zero failures**

---

## Next Steps

1. ✅ Design document (this file)
2. ⏳ Implement PlanBuilder class
3. ⏳ Add unit tests
4. ⏳ Update `/ctx:plan` command
5. ⏳ Update `/ctx:execute` command
6. ⏳ Integration testing
7. ⏳ Documentation updates
8. ⏳ Deprecation notices

---

**Decision: Approved for implementation**
**Estimated effort: 20,000 tokens (medium complexity)**
