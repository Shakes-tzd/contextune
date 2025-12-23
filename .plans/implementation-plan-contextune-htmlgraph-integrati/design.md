I'll create a comprehensive implementation plan for the Contextune-HtmlGraph integration based on our strategic discussion.

# Implementation Plan: Contextune-HtmlGraph Integration Layer

**Type:** Plan
**Status:** Ready
**Created:** 20251223-103000

---

## Overview

Create a tight integration layer between Contextune and HtmlGraph to provide unified observability, seamless workflow, and shared configuration while maintaining their separate architectural identities.

---

## Plan Structure

```yaml
metadata:
  name: "Contextune-HtmlGraph Integration Layer"
  created: "20251223-103000"
  status: "ready"

overview: |
  Build integration layer that bridges Contextune (Claude Code interface) and HtmlGraph 
  (tracking/persistence) into a cohesive software development workflow with unified 
  configuration, shared dashboard, and automatic feature tracking.

research:
  approach: "Layered integration with shared data models and automatic tracking"
  libraries:
    - name: "pydantic"
      reason: "Already used by both projects, enables shared models"
    - name: "pyyaml"
      reason: "Configuration management for unified config"
  patterns:
    - file: "htmlgraph/sdk.py:1-50"
      description: "SDK pattern for programmatic access"
    - file: "hooks/user_prompt_submit.py:1-100"
      description: "Hook pattern for automatic integration"
  specifications:
    - requirement: "Maintain separate repositories"
      status: "must_follow"
    - requirement: "Backward compatible with existing workflows"
      status: "must_follow"
    - requirement: "Zero-transformation architecture"
      status: "should_follow"
  dependencies:
    existing:
      - "pydantic>=2.0"
      - "pyyaml>=6.0"
      - "htmlgraph>=0.7.5"
    new:
      - "contextune-integration>=0.1.0"

features:
  - "Automatic HtmlGraph track creation from /ctx:plan"
  - "Automatic HtmlGraph feature start from /ctx:execute"
  - "Unified configuration file"
  - "Contextune metrics in HtmlGraph dashboard"
  - "Shared data models for plans/tasks"

tasks:
  - id: "task-0"
    name: "Create shared data models package"
    file: "tasks/task-0.md"
    priority: "blocker"
    dependencies: []

  - id: "task-1"
    name: "Implement auto-tracking hook"
    file: "tasks/task-1.md"
    priority: "high"
    dependencies: ["task-0"]

  - id: "task-2"
    name: "Create unified configuration"
    file: "tasks/task-2.md"
    priority: "high"
    dependencies: []

  - id: "task-3"
    name: "Add Contextune views to HtmlGraph dashboard"
    file: "tasks/task-3.md"
    priority: "medium"
    dependencies: ["task-1"]

  - id: "task-4"
    name: "Update documentation for unified workflow"
    file: "tasks/task-4.md"
    priority: "low"
    dependencies: ["task-1", "task-2", "task-3"]

shared_resources:
  files:
    - path: "pyproject.toml"
      reason: "Both projects need dependency updates"
      mitigation: "Task 0 updates Contextune first, Task 2 updates HtmlGraph"
  
  databases:
    - name: "HtmlGraph .htmlgraph/ directory"
      concern: "Multiple hooks writing to same graph"
      mitigation: "Use SDK's built-in locking mechanisms"

testing:
  unit:
    - "Each task writes unit tests for new components"
    - "Mock integration points for isolated testing"
  integration:
    - "Test Contextune → HtmlGraph data flow"
    - "Test unified config loading in both projects"
    - "Test dashboard rendering of Contextune data"
  isolation:
    - "Integration tests run in separate worktrees"
    - "Mock HtmlGraph SDK for Contextune tests"

success_criteria:
  - "Running /ctx:plan automatically creates HtmlGraph track"
  - "Running /ctx:execute automatically starts HtmlGraph features"
  - "Unified config file works for both projects"
  - "HtmlGraph dashboard shows Contextune command history"
  - "Intent detection metrics visible in dashboard"
  - "All existing workflows still function"
  - "Backward compatible with standalone usage"
  - "Documentation updated and comprehensive"

notes: |
  Key architectural decision: Keep projects separate but add integration
  package that both can depend on. This maintains flexibility while
  providing tight coupling where needed.
  
  Phase 1 (this plan): Basic integration and auto-tracking
  Phase 2 (future): Advanced dashboard features and analytics
  Phase 3 (future): Shared execution engine and parallel coordination

changelog:
  - timestamp: "20251223-103000"
    event: "Plan created based on strategic architecture discussion"
```

---

## Task Details

### Task 0: Create Shared Data Models Package

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

# Create Shared Data Models Package

## 🎯 Objective

Create a `contextune-integration` package with shared Pydantic models for plans, tasks, and sessions that both Contextune and HtmlGraph can use, eliminating translation layers.

## 🛠️ Implementation Approach

**Pattern to follow:**
- **File:** `htmlgraph/models.py:1-100`
- **Description:** Use Pydantic BaseModel pattern with validation

**Libraries:**
- `pydantic>=2.0` - Shared models with validation
- `pyyaml>=6.0` - YAML serialization

## 📁 Files to Touch

**Create:**
- `contextune_integration/__init__.py`
- `contextune_integration/models.py` - Shared Plan, Task, Session models
- `contextune_integration/converters.py` - Convert between formats
- `tests/test_models.py` - Model validation tests
- `pyproject.toml` - Package configuration

**Modify:**
- `contextune/pyproject.toml` - Add dependency on integration package
- `htmlgraph/pyproject.toml` - Add dependency on integration package

## 🧪 Tests Required

**Unit:**
- [ ] Test Plan model validation
- [ ] Test Task model validation
- [ ] Test Session model validation
- [ ] Test YAML serialization/deserialization
- [ ] Test converters from Contextune → Integration
- [ ] Test converters from Integration → HtmlGraph

**Integration:**
- [ ] Test end-to-end Plan creation flow
- [ ] Test model compatibility with both systems

## ✅ Acceptance Criteria

- [ ] All models use Pydantic BaseModel
- [ ] Models serialize to/from YAML correctly
- [ ] Converters handle all edge cases
- [ ] 100% test coverage on models
- [ ] Documentation for each model field
- [ ] Type hints on all functions
- [ ] Published to PyPI as `contextune-integration`

## ⚠️ Potential Conflicts

**Files:**
- None - This is a new package

## 📝 Notes

This is a blocker because all other tasks depend on shared models.
Package should be minimal and focused - only data models, no business logic.

---

**Worktree:** `worktrees/task-0`
**Branch:** `feature/task-0`

🤖 Auto-created via Contextune parallel execution

---

### Task 1: Implement Auto-Tracking Hook

---
id: task-1
priority: high
status: pending
dependencies: ["task-0"]
labels:
  - parallel-execution
  - auto-created
  - priority-high
---

# Implement Auto-Tracking Hook

## 🎯 Objective

Create hooks in Contextune that automatically create HtmlGraph tracks when running `/ctx:plan` and automatically start features when running `/ctx:execute`.

## 🛠️ Implementation Approach

**Pattern to follow:**
- **File:** `hooks/user_prompt_submit.py:1-200`
- **Description:** Hook pattern with JSON input/output

**Libraries:**
- `htmlgraph>=0.7.5` - SDK for track/feature creation
- `contextune-integration>=0.1.0` - Shared models

## 📁 Files to Touch

**Create:**
- `hooks/contextune_htmlgraph_bridge.py` - Auto-tracking hook
- `tests/test_integration_hook.py` - Hook tests

**Modify:**
- `hooks/hooks.json` - Register new PreToolUse hook
- `.claude-plugin/plugin.json` - Update dependencies

## 🧪 Tests Required

**Unit:**
- [ ] Test track creation from plan data
- [ ] Test feature start from execute command
- [ ] Test hook response format
- [ ] Test error handling when HtmlGraph unavailable

**Integration:**
- [ ] Test full /ctx:plan → HtmlGraph track flow
- [ ] Test full /ctx:execute → HtmlGraph feature flow
- [ ] Test with actual HtmlGraph installation

## ✅ Acceptance Criteria

- [ ] Running `/ctx:plan` creates HtmlGraph track automatically
- [ ] Running `/ctx:execute` starts HtmlGraph features automatically
- [ ] Hook doesn't block if HtmlGraph unavailable
- [ ] All activity logged to HtmlGraph session
- [ ] Track ID stored in plan metadata
- [ ] Feature IDs stored in task metadata
- [ ] Backward compatible (works without HtmlGraph)

## ⚠️ Potential Conflicts

**Files:**
- `hooks/hooks.json` - Task 2 also modifies → Use different hook points

## 📝 Notes

Hook should be non-blocking - if HtmlGraph SDK fails, just log warning
and continue. This maintains Contextune's standalone usability.

---

**Worktree:** `worktrees/task-1`
**Branch:** `feature/task-1`

🤖 Auto-created via Contextune parallel execution

---

### Task 2: Create Unified Configuration

---
id: task-2
priority: high
status: pending
dependencies: []
labels:
  - parallel-execution
  - auto-created
  - priority-high
---

# Create Unified Configuration

## 🎯 Objective

Create a unified configuration system that both Contextune and HtmlGraph can read from a single `.contextune-config.yaml` file.

## 🛠️ Implementation Approach

**Libraries:**
- `pyyaml>=6.0` - Configuration parsing
- `pydantic>=2.0` - Config validation

## 📁 Files to Touch

**Create:**
- `contextune_integration/config.py` - Unified config loader
- `.contextune-config.yaml.example` - Example config file
- `docs/UNIFIED_CONFIG.md` - Configuration documentation

**Modify:**
- `hooks/session_start.py` - Load unified config
- `htmlgraph/config.py` - Use unified config loader

## 🧪 Tests Required

**Unit:**
- [ ] Test config loading from YAML
- [ ] Test config validation with Pydantic
- [ ] Test fallback to defaults
- [ ] Test environment variable overrides

**Integration:**
- [ ] Test Contextune reads config correctly
- [ ] Test HtmlGraph reads config correctly
- [ ] Test config changes reflected in both systems

## ✅ Acceptance Criteria

- [ ] Single `.contextune-config.yaml` works for both projects
- [ ] Config validates with Pydantic schema
- [ ] Environment variables override file values
- [ ] Backward compatible with existing configs
- [ ] Clear error messages for invalid config
- [ ] Documentation with examples
- [ ] Default config doesn't require file

## ⚠️ Potential Conflicts

**Files:**
- None - Config files are read-only

## 📝 Notes

Config should support hierarchical loading:
1. Default values (in code)
2. Global config (~/.contextune-config.yaml)
3. Project config (./.contextune-config.yaml)
4. Environment variables

---

**Worktree:** `worktrees/task-2`
**Branch:** `feature/task-2`

🤖 Auto-created via Contextune parallel execution

---

### Task 3: Add Contextune Views to HtmlGraph Dashboard

---
id: task-3
priority: medium
status: pending
dependencies: ["task-1"]
labels:
  - parallel-execution
  - auto-created
  - priority-medium
---

# Add Contextune Views to HtmlGraph Dashboard

## 🎯 Objective

Extend HtmlGraph dashboard to display Contextune-specific data including command history, intent detection stats, and parallel execution status.

## 🛠️ Implementation Approach

**Pattern to follow:**
- **File:** `htmlgraph/dashboard.py:1-200`
- **Description:** justhtml rendering pattern

**Libraries:**
- `justhtml` - HTML generation
- `htmlgraph>=0.7.5` - Access to session/event data

## 📁 Files to Touch

**Create:**
- `htmlgraph/views/contextune_dashboard.py` - Contextune views
- `htmlgraph/analytics/contextune_metrics.py` - Metrics calculation
- `tests/test_contextune_views.py` - View tests

**Modify:**
- `htmlgraph/dashboard.py` - Add Contextune tab
- `htmlgraph/static/styles.css` - Contextune-specific styles

## 🧪 Tests Required

**Unit:**
- [ ] Test command history rendering
- [ ] Test intent detection stats calculation
- [ ] Test parallel execution status display
- [ ] Test empty state handling

**Integration:**
- [ ] Test dashboard loads with Contextune data
- [ ] Test real-time updates (if applicable)
- [ ] Test dashboard works without Contextune data

## ✅ Acceptance Criteria

- [ ] Dashboard has "Contextune" tab
- [ ] Shows command history with timestamps
- [ ] Displays intent detection accuracy metrics
- [ ] Shows parallel execution status
- [ ] Visualizes token savings from optimizations
- [ ] Works with `htmlgraph serve` command
- [ ] Gracefully handles missing Contextune data

## ⚠️ Potential Conflicts

**Files:**
- `htmlgraph/dashboard.py` - Only adds new tab, minimal conflict risk

## 📝 Notes

Dashboard should show:
- Recent Contextune commands (/ctx:plan, /ctx:execute, etc.)
- Intent detection: queries → commands mapping
- Token savings metrics
- Parallel execution timeline
- Hook execution times

---

**Worktree:** `worktrees/task-3`
**Branch:** `feature/task-3`

🤖 Auto-created via Contextune parallel execution

---

### Task 4: Update Documentation for Unified Workflow

---
id: task-4
priority: low
status: pending
dependencies: ["task-1", "task-2", "task-3"]
labels:
  - parallel-execution
  - auto-created
  - priority-low
---

# Update Documentation for Unified Workflow

## 🎯 Objective

Create comprehensive documentation explaining the Contextune-HtmlGraph integration, unified workflow, and migration guide for existing users.

## 🛠️ Implementation Approach

**Libraries:**
- None - Documentation only

## 📁 Files to Touch

**Create:**
- `docs/INTEGRATION_GUIDE.md` - Complete integration guide
- `docs/UNIFIED_WORKFLOW.md` - Workflow documentation
- `docs/MIGRATION.md` - Migration from standalone to integrated
- `docs/ARCHITECTURE_DECISION.md` - Why layered integration

**Modify:**
- `README.md` - Add integration section
- `docs/QUICKSTART.md` - Update for unified workflow

## 🧪 Tests Required

**Unit:**
- [ ] Verify all code examples work
- [ ] Check all links resolve
- [ ] Validate YAML examples

**Integration:**
- [ ] Test quick start guide end-to-end
- [ ] Verify migration steps work

## ✅ Acceptance Criteria

- [ ] Integration guide covers all features
- [ ] Workflow documentation with examples
- [ ] Migration guide for existing users
- [ ] Architecture decision documented
- [ ] All code examples tested
- [ ] Screenshots of dashboard views
- [ ] FAQ section addresses common questions
- [ ] Links to both project docs

## ⚠️ Potential Conflicts

**Files:**
- None - Documentation only

## 📝 Notes

Documentation should emphasize:
- Unified mental model (Contextune = interface, HtmlGraph = persistence)
- Automatic integration (zero manual work)
- Backward compatibility (works standalone)
- Benefits of integration (observability, continuity, analytics)

Include examples:
- Installing integrated setup
- Using /ctx:plan with auto-tracking
- Viewing results in HtmlGraph dashboard
- Migrating from standalone

---

**Worktree:** `worktrees/task-4`
**Branch:** `feature/task-4`

🤖 Auto-created via Contextune parallel execution

---

## References

- Strategic architecture discussion (this conversation)
- HtmlGraph SDK documentation
- Contextune hooks architecture
- Pydantic models documentation

---

📋 Plan created in extraction-optimized format!

**Plan Summary:**
- 5 total tasks
- 3 can run in parallel (task-0, task-2, and task-4 after dependencies)
- 2 have dependencies (task-1 depends on task-0, task-3 depends on task-1)
- Conflict risk: Low

**Tasks by Priority:**
- Blocker: task-0 (shared models)
- High: task-1 (auto-tracking), task-2 (unified config)
- Medium: task-3 (dashboard views)
- Low: task-4 (documentation)

**What Happens Next:**

The plan above will be automatically extracted to modular files when you:
1. Run `/ctx:execute` - Extracts and executes immediately
2. End this session - SessionEnd hook extracts automatically

**Extraction Output:**
```
.parallel/plans/
├── plan.yaml           (main plan with metadata)
├── tasks/
│   ├── task-0.md      (GitHub-ready task files)
│   ├── task-1.md
│   ├── task-2.md
│   ├── task-3.md
│   └── task-4.md
├── templates/
│   └── task-template.md
└── scripts/
    ├── add_task.sh
    └── generate_full.sh
```

**Key Benefits:**
✅ **Full visibility**: You see complete plan in conversation
✅ **Easy iteration**: Ask for changes before extraction
✅ **Zero manual work**: Extraction happens automatically
✅ **Modular files**: Edit individual tasks after extraction
✅ **Perfect DRY**: Plan exists once (conversation), extracted once (files)

**Next Steps:**
1. Review the plan above (scroll up if needed)
2. Request changes if needed
3. When satisfied, run: `/ctx:execute`

Ready to execute? Run `/ctx:execute` to extract and start parallel development.