The extraction failed because the script is looking for a specific section name `## Plan Structure` with a YAML block. Let me create a plan in the exact format the extractor expects:

---

# Implementation Plan: HtmlGraph Session Analytics Dashboard

**Type:** Plan
**Status:** Complete
**Estimated Tokens:** 45,000

---

## Overview

Create an interactive analytics dashboard for HtmlGraph sessions that visualizes work patterns, productivity metrics, and session comparisons.

---

## Plan Structure

```yaml
metadata:
  title: "HtmlGraph Session Analytics Dashboard"
  version: "1.0"
  created: "2025-12-23"
  estimated_total_tokens: 45000
  estimated_cost_haiku: "$0.054"
  execution_mode: "sequential"

overview: |
  Build analytics dashboard for HtmlGraph sessions with interactive visualizations
  showing work patterns, productivity metrics, and session comparisons.

phases:
  phase_1:
    name: "Core Analytics"
    duration: "4 hours"
    tasks: ["task-1", "task-2"]
    parallelizable: false
    dependencies: []
    estimated_tokens: 15000

  phase_2:
    name: "Dashboard UI"
    duration: "5 hours"
    tasks: ["task-3", "task-4"]
    parallelizable: false
    dependencies: ["phase_1"]
    estimated_tokens: 20000

  phase_3:
    name: "Advanced Features"
    duration: "3 hours"
    tasks: ["task-5"]
    parallelizable: false
    dependencies: ["phase_2"]
    estimated_tokens: 10000

tasks:
  - file: "tasks/task-1.md"
    id: "task-1"
    title: "Implement SessionAnalytics engine"
    type: "implement"
    complexity: "medium"
    estimated_tokens: 8000
    priority: "high"
    dependencies: []

  - file: "tasks/task-2.md"
    id: "task-2"
    title: "Add metrics calculation methods"
    type: "implement"
    complexity: "medium"
    estimated_tokens: 7000
    priority: "high"
    dependencies: ["task-1"]

  - file: "tasks/task-3.md"
    id: "task-3"
    title: "Create dashboard HTML renderer"
    type: "implement"
    complexity: "medium"
    estimated_tokens: 10000
    priority: "medium"
    dependencies: ["task-2"]

  - file: "tasks/task-4.md"
    id: "task-4"
    title: "Add interactive charts"
    type: "implement"
    complexity: "simple"
    estimated_tokens: 10000
    priority: "medium"
    dependencies: ["task-3"]

  - file: "tasks/task-5.md"
    id: "task-5"
    title: "Implement session comparison"
    type: "implement"
    complexity: "complex"
    estimated_tokens: 10000
    priority: "low"
    dependencies: ["task-4"]

success_criteria:
  - "SessionAnalytics parses session events correctly"
  - "Dashboard renders in htmlgraph serve"
  - "Charts display accurate data"
  - "All tests pass"

rollback_plan:
  - "Revert analytics module changes"
  - "Remove dashboard files"
```

---

## Task Details

### Task 1: Implement SessionAnalytics engine

```yaml
id: task-1
title: "Implement SessionAnalytics engine"
type: implement
complexity: medium
estimated_tokens: 8000
dependencies: []
files_created:
  - path: "htmlgraph/analytics/session_analytics.py"
    purpose: "Core analytics engine"
validation:
  - "Parses session events from JSONL"
  - "Calculates work type distribution"
  - "Computes session duration"
```

**Implementation:**
- Create SessionAnalytics class with event parsing
- Add work type distribution calculation
- Implement session metric aggregation

---

### Task 2: Add metrics calculation methods

```yaml
id: task-2
title: "Add metrics calculation methods"
type: implement
complexity: medium
estimated_tokens: 7000
dependencies: [task-1]
files_modified:
  - path: "htmlgraph/analytics/session_analytics.py"
    changes: "Add productivity scoring"
validation:
  - "Context efficiency ratio calculated"
  - "Tool usage patterns scored"
```

**Implementation:**
- Add productivity scoring algorithm
- Implement efficiency metrics
- Calculate tool usage patterns

---

### Task 3: Create dashboard HTML renderer

```yaml
id: task-3
title: "Create dashboard HTML renderer"
type: implement
complexity: medium
estimated_tokens: 10000
dependencies: [task-2]
files_created:
  - path: "htmlgraph/analytics/dashboard_renderer.py"
    purpose: "justhtml dashboard generation"
validation:
  - "Renders session overview"
  - "Displays work breakdown"
```

**Implementation:**
- Create DashboardRenderer with justhtml
- Add session overview rendering
- Implement work type breakdown display

---

### Task 4: Add interactive charts

```yaml
id: task-4
title: "Add interactive charts with Chart.js"
type: implement
complexity: simple
estimated_tokens: 10000
dependencies: [task-3]
files_modified:
  - path: "htmlgraph/analytics/dashboard_renderer.py"
    changes: "Integrate Chart.js"
validation:
  - "Pie chart for work types"
  - "Bar chart for tools"
  - "Line chart for trends"
```

**Implementation:**
- Integrate Chart.js library
- Create pie chart for work distribution
- Add timeline visualization

---

### Task 5: Implement session comparison

```yaml
id: task-5
title: "Implement session comparison features"
type: implement
complexity: complex
estimated_tokens: 10000
dependencies: [task-4]
files_modified:
  - path: "htmlgraph/analytics/session_analytics.py"
    changes: "Add comparison logic"
  - path: "htmlgraph/analytics/dashboard_renderer.py"
    changes: "Add comparison view"
validation:
  - "Compares 2+ sessions"
  - "Highlights differences"
```

**Implementation:**
- Add multi-session comparison logic
- Create comparison view renderer
- Implement difference highlighting

---

Now let's test the extraction again: