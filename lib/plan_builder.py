#!/usr/bin/env python3
"""
Plan Builder - Direct file creation for /ctx:plan

Creates plan files directly instead of relying on transcript extraction.
Provides fluent API for building plans with tasks, metadata, and research synthesis.

Usage:
    from lib.plan_builder import PlanBuilder

    builder = PlanBuilder("Feature Name")
    builder.set_research({
        "approach": "...",
        "libraries": [...]
    })
    builder.add_task(
        id="task-0",
        name="Task Name",
        priority="blocker",
        content="# Task\nContent here"
    )
    created = builder.build()
"""

from pathlib import Path
from typing import Any, Optional
from datetime import datetime
import yaml


class PlanBuilder:
    """
    Build and write plan files directly.

    Provides fluent API for creating modular plan structures with:
    - plan.yaml (master plan with metadata)
    - tasks/task-N.md (individual task files)
    - Directory structure (.parallel/plans/)

    Example:
        builder = PlanBuilder("Auth System")
        builder.set_research({"approach": "JWT"})
        builder.add_task("task-0", "Create models", "blocker", content)
        builder.add_task("task-1", "Add routes", "high", content, ["task-0"])
        files = builder.build()
    """

    def __init__(self, name: str, output_dir: str = ".parallel/plans"):
        """
        Initialize PlanBuilder.

        Args:
            name: Plan name (e.g., "User Authentication System")
            output_dir: Output directory path (default: .parallel/plans)
        """
        self.name = name
        self.output_dir = Path(output_dir)
        self.tasks: list[dict[str, Any]] = []
        self.plan_data: dict[str, Any] = {
            "metadata": {
                "name": name,
                "created": datetime.now().strftime("%Y%m%d-%H%M%S"),
                "status": "ready"
            }
        }

    def set_research(self, research: dict[str, Any]) -> 'PlanBuilder':
        """
        Set research synthesis results.

        Args:
            research: Research findings with keys:
                - approach: Recommended approach
                - libraries: List of libraries to use
                - patterns: Existing code patterns to follow
                - specifications: Requirements to follow
                - dependencies: Dependency analysis

        Returns:
            Self for chaining

        Example:
            builder.set_research({
                "approach": "Use JWT with refresh tokens",
                "libraries": [
                    {"name": "jsonwebtoken", "reason": "Industry standard"}
                ],
                "patterns": [
                    {"file": "auth/oauth.ts:45", "description": "OAuth pattern"}
                ]
            })
        """
        self.plan_data["research"] = research
        return self

    def set_metadata(self, **kwargs) -> 'PlanBuilder':
        """
        Set additional plan metadata fields.

        Args:
            **kwargs: Arbitrary metadata fields (overview, shared_resources, etc.)

        Returns:
            Self for chaining

        Example:
            builder.set_metadata(
                overview="Build auth system with JWT",
                shared_resources={"files": [...]},
                testing={"unit": [...], "integration": [...]},
                success_criteria=["All tests pass", "No security issues"]
            )
        """
        self.plan_data.update(kwargs)
        return self

    def add_task(
        self,
        id: str,
        name: str,
        priority: str,
        content: str,
        dependencies: Optional[list[str]] = None
    ) -> 'PlanBuilder':
        """
        Add a task to the plan.

        Args:
            id: Task ID (e.g., "task-0", "task-1")
            name: Task name (e.g., "Create Data Models")
            priority: Priority level (blocker, high, medium, low)
            content: Full task content (markdown with YAML frontmatter)
            dependencies: List of task IDs this depends on (default: [])

        Returns:
            Self for chaining

        Example:
            builder.add_task(
                id="task-0",
                name="Create Data Models",
                priority="blocker",
                content='''---
id: task-0
priority: blocker
status: pending
dependencies: []
---

# Create Data Models

## Objective
...
''',
                dependencies=[]
            )
        """
        if priority not in ["blocker", "high", "medium", "low"]:
            raise ValueError(f"Invalid priority: {priority}. Must be blocker, high, medium, or low")

        self.tasks.append({
            "id": id,
            "name": name,
            "file": f"tasks/{id}.md",
            "priority": priority,
            "dependencies": dependencies or [],
            "content": content
        })
        return self

    def build(self) -> dict[str, Any]:
        """
        Write all plan files and return paths.

        Creates:
        - .parallel/plans/plan.yaml (master plan)
        - .parallel/plans/tasks/task-N.md (individual tasks)
        - .parallel/plans/templates/ (helper directory)
        - .parallel/plans/scripts/ (helper directory)

        Returns:
            Dictionary mapping file types to paths:
            - "plan": Path to plan.yaml
            - "tasks": List of task file paths
            - "directories": List of created directories

        Raises:
            ValueError: If no tasks have been added

        Example:
            created = builder.build()
            print(f"Created plan: {created['plan']}")
            print(f"Created {len(created['tasks'])} tasks")
        """
        if not self.tasks:
            raise ValueError("Cannot build plan with no tasks. Add at least one task first.")

        # Create directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        tasks_dir = self.output_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)
        templates_dir = self.output_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        scripts_dir = self.output_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        created_files: dict[str, Any] = {
            "directories": [self.output_dir, tasks_dir, templates_dir, scripts_dir]
        }

        # Build task references for plan.yaml (without content)
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
        task_files: list[Path] = []
        for task in self.tasks:
            task_file = tasks_dir / f"{task['id']}.md"
            with open(task_file, 'w') as f:
                f.write(task["content"])
            task_files.append(task_file)

        created_files["tasks"] = task_files

        return created_files

    def get_summary(self) -> str:
        """
        Get a summary of the plan for display.

        Returns:
            Formatted summary string showing:
            - Plan name and status
            - Task count and breakdown by priority
            - Dependencies

        Example:
            summary = builder.get_summary()
            print(summary)
        """
        task_count = len(self.tasks)

        # Count by priority
        priority_counts = {"blocker": 0, "high": 0, "medium": 0, "low": 0}
        for task in self.tasks:
            priority_counts[task["priority"]] += 1

        # Find tasks with dependencies
        dependent_tasks = [t for t in self.tasks if t["dependencies"]]
        parallel_tasks = task_count - len(dependent_tasks)

        summary = f"""📋 Plan: {self.name}

**Status:** {self.plan_data['metadata']['status']}
**Created:** {self.plan_data['metadata']['created']}

**Tasks:**
- Total: {task_count}
- Can run in parallel: {parallel_tasks}
- Have dependencies: {len(dependent_tasks)}

**By Priority:**
- Blocker: {priority_counts['blocker']}
- High: {priority_counts['high']}
- Medium: {priority_counts['medium']}
- Low: {priority_counts['low']}

**Files to be created:**
- plan.yaml (master plan)
"""

        for task in self.tasks:
            deps = f" (depends on: {', '.join(task['dependencies'])})" if task['dependencies'] else ""
            summary += f"- tasks/{task['id']}.md - {task['name']} [{task['priority']}]{deps}\n"

        return summary


# Convenience function for quick plan creation
def create_plan(
    name: str,
    tasks: list[dict[str, Any]],
    research: Optional[dict[str, Any]] = None,
    metadata: Optional[dict[str, Any]] = None,
    output_dir: str = ".parallel/plans"
) -> dict[str, Any]:
    """
    Create a plan in one function call.

    Args:
        name: Plan name
        tasks: List of task dicts with keys: id, name, priority, content, dependencies
        research: Optional research synthesis
        metadata: Optional additional metadata
        output_dir: Output directory

    Returns:
        Created file paths

    Example:
        files = create_plan(
            name="Auth System",
            tasks=[
                {
                    "id": "task-0",
                    "name": "Models",
                    "priority": "blocker",
                    "content": "# Models\n...",
                    "dependencies": []
                }
            ],
            research={"approach": "JWT"},
            metadata={"overview": "Build auth"}
        )
    """
    builder = PlanBuilder(name, output_dir)

    if research:
        builder.set_research(research)

    if metadata:
        builder.set_metadata(**metadata)

    for task in tasks:
        builder.add_task(
            id=task["id"],
            name=task["name"],
            priority=task["priority"],
            content=task["content"],
            dependencies=task.get("dependencies", [])
        )

    return builder.build()


if __name__ == "__main__":
    # Self-test
    print("Testing PlanBuilder...")

    builder = PlanBuilder("Test Plan", output_dir="/tmp/test-plan")

    builder.set_research({
        "approach": "Test-driven approach",
        "libraries": [{"name": "pytest", "reason": "Standard testing"}]
    })

    builder.set_metadata(
        overview="Test plan for validation",
        success_criteria=["All tests pass"]
    )

    builder.add_task(
        id="task-0",
        name="Write Tests",
        priority="blocker",
        content="""---
id: task-0
priority: blocker
status: pending
dependencies: []
---

# Write Tests

## Objective
Create comprehensive tests.
"""
    )

    builder.add_task(
        id="task-1",
        name="Implement Code",
        priority="high",
        content="""---
id: task-1
priority: high
status: pending
dependencies: [task-0]
---

# Implement Code

## Objective
Implement features to pass tests.
""",
        dependencies=["task-0"]
    )

    # Build
    created = builder.build()

    # Print summary
    print(builder.get_summary())

    print("\n✅ Test passed! Files created:")
    print(f"  Plan: {created['plan']}")
    print(f"  Tasks: {len(created['tasks'])} files")
