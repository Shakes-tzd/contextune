#!/usr/bin/env python3
"""Shared Pydantic models for Contextune-HtmlGraph integration."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .types import (
    DetectionMethod,
    ExecutionMode,
    Priority,
    TaskStatus,
    TrackingEvent,
    WorkType,
)


class ContextuneSession(BaseModel):
    """Session metadata and metrics from Contextune."""

    session_id: str = Field(..., description="Unique session identifier")
    agent: str = Field(default="claude", description="Agent name")
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Metrics
    total_prompts: int = Field(default=0, ge=0)
    detections: int = Field(default=0, ge=0)
    parallel_executions: int = Field(default=0, ge=0)

    # Links
    htmlgraph_session_id: Optional[str] = Field(
        None,
        description="Linked HtmlGraph session ID"
    )
    primary_feature_id: Optional[str] = Field(
        None,
        description="Primary HtmlGraph feature being worked on"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-20251223-120000",
                "agent": "claude",
                "total_prompts": 15,
                "detections": 3,
                "parallel_executions": 1,
                "htmlgraph_session_id": "sess-abc123",
                "primary_feature_id": "feat-xyz789"
            }
        }


class IntentDetection(BaseModel):
    """Detection results and confidence from Contextune."""

    prompt: str = Field(..., description="Original user prompt")
    detected_command: Optional[str] = Field(
        None,
        description="Detected slash command"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Detection confidence (0-1)"
    )
    method: DetectionMethod = Field(
        ...,
        description="Detection method used"
    )
    latency_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Detection latency in milliseconds"
    )
    timestamp: datetime = Field(default_factory=datetime.now)

    # Alternative suggestions
    alternatives: list[tuple[str, float]] = Field(
        default_factory=list,
        description="Alternative commands with confidence scores"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "can you help me plan this feature",
                "detected_command": "/ctx:plan",
                "confidence": 0.95,
                "method": "keyword",
                "latency_ms": 0.3,
                "alternatives": [("/ctx:research", 0.75), ("/ctx:help", 0.60)]
            }
        }


class ParallelTask(BaseModel):
    """Individual task in a parallel execution plan."""

    task_id: str = Field(..., description="Task identifier (e.g., task-0)")
    title: str = Field(..., description="Task title")
    priority: Priority = Field(..., description="Task priority")
    status: TaskStatus = Field(default="pending")
    dependencies: list[str] = Field(default_factory=list)

    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_tokens: int = Field(default=0, ge=0)
    actual_tokens: int = Field(default=0, ge=0)

    # HtmlGraph linkage
    feature_id: Optional[str] = Field(
        None,
        description="Linked HtmlGraph feature ID"
    )

    @field_validator('task_id')
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate task ID format."""
        if not v.startswith('task-'):
            raise ValueError("Task ID must start with 'task-'")
        return v


class ParallelExecution(BaseModel):
    """Execution plan and task status from /ctx:execute."""

    plan_name: str = Field(..., description="Plan name/title")
    execution_mode: ExecutionMode = Field(
        default="parallel",
        description="Execution mode"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Plan metadata
    plan_path: Path = Field(..., description="Path to plan.yaml")
    tasks: list[ParallelTask] = Field(
        default_factory=list,
        description="Tasks in execution plan"
    )

    # Cost tracking
    estimated_total_tokens: int = Field(default=0, ge=0)
    actual_total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)
    actual_cost_usd: float = Field(default=0.0, ge=0.0)

    # HtmlGraph linkage
    track_id: Optional[str] = Field(
        None,
        description="Linked HtmlGraph track ID"
    )

    @property
    def total_tasks(self) -> int:
        """Total number of tasks."""
        return len(self.tasks)

    @property
    def completed_tasks(self) -> int:
        """Number of completed tasks."""
        return sum(1 for task in self.tasks if task.status == "done")

    @property
    def progress_percentage(self) -> float:
        """Completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    class Config:
        json_schema_extra = {
            "example": {
                "plan_name": "User Authentication System",
                "execution_mode": "parallel",
                "plan_path": ".parallel/plans/plan.yaml",
                "tasks": [
                    {
                        "task_id": "task-0",
                        "title": "Create shared models",
                        "priority": "blocker",
                        "status": "done",
                        "estimated_tokens": 15000,
                        "feature_id": "feat-abc123"
                    }
                ],
                "track_id": "track-20251223-120000"
            }
        }


class WorkAttribution(BaseModel):
    """Link between Contextune work and HtmlGraph features."""

    # Contextune side
    session_id: str = Field(..., description="Contextune session ID")
    detection_count: int = Field(default=0, ge=0)
    execution_plan: Optional[str] = Field(None, description="Plan name if applicable")

    # HtmlGraph side
    feature_ids: list[str] = Field(
        default_factory=list,
        description="Linked feature IDs"
    )
    track_id: Optional[str] = Field(None, description="Linked track ID")

    # Attribution metadata
    work_type: WorkType = Field(..., description="Type of work")
    created_at: datetime = Field(default_factory=datetime.now)

    # Metrics
    total_tool_calls: int = Field(default=0, ge=0)
    files_modified: list[str] = Field(default_factory=list)
    commits: list[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-20251223-120000",
                "detection_count": 3,
                "execution_plan": "User Authentication System",
                "feature_ids": ["feat-abc123", "feat-def456"],
                "track_id": "track-20251223-120000",
                "work_type": "feature-implementation",
                "total_tool_calls": 45,
                "files_modified": ["lib/auth.py", "tests/test_auth.py"],
                "commits": ["abc123", "def456"]
            }
        }


class TrackMetadata(BaseModel):
    """Metadata stored in plan.yaml for HtmlGraph track linkage."""

    track_id: str = Field(..., description="HtmlGraph track ID")
    created_at: datetime = Field(default_factory=datetime.now)
    auto_created: bool = Field(
        default=True,
        description="Whether track was auto-created by hook"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "track_id": "track-20251223-120000",
                "auto_created": True
            }
        }


class IntegrationHealth(BaseModel):
    """Health status of Contextune-HtmlGraph integration."""

    contextune_available: bool = Field(default=False)
    htmlgraph_available: bool = Field(default=False)
    integration_enabled: bool = Field(default=False)

    last_sync: Optional[datetime] = None
    errors: list[str] = Field(default_factory=list)

    @property
    def healthy(self) -> bool:
        """Whether integration is fully healthy."""
        return (
            self.contextune_available
            and self.htmlgraph_available
            and self.integration_enabled
            and len(self.errors) == 0
        )

    class Config:
        json_schema_extra = {
            "example": {
                "contextune_available": True,
                "htmlgraph_available": True,
                "integration_enabled": True,
                "last_sync": "2025-12-23T12:00:00",
                "errors": []
            }
        }
